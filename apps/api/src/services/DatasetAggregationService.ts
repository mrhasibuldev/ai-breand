/**
 * Dataset Aggregation Service
 *
 * Aggregates processed documents into datasets for training.
 * This bridges the gap between document processing and training preparation.
 */

import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { createS3ProviderFromEnv, DatasetStorageService } from '@nexusai/storage-core';
import crypto from 'node:crypto';

interface ProcessedDocument {
  id: string;
  collection_job_id: string;
  source_id: string;
  final_url: string;
  title: string;
  content: string;
  content_type: string;
  language: string;
  checksum: string;
  processing_status: 'accepted' | 'rejected' | 'duplicate' | 'failed';
  quality_score: number;
  quality_reasons: string[];
  created_at: string;
}

interface DatasetAggregationOptions {
  name: string;
  description?: string;
  category?: string;
  source: string;
  provenance: string;
  license?: string;
  privacy_status?: 'public' | 'private' | 'restricted';
  account_id: string;
  collection_job_id?: string;
  source_id?: string;
  min_quality_score?: number;
}

interface DatasetAggregationResult {
  dataset_id: string;
  storage_key: string;
  file_size_bytes: number;
  sha256_checksum: string;
  document_count: number;
  version: string;
}

export class DatasetAggregationService {
  private db: any;
  private storageService: DatasetStorageService;

  constructor() {
    const config = readDatabaseConfig();
    this.db = createDatabaseClient(config);
    this.db.connect();

    const s3Provider = createS3ProviderFromEnv();
    this.storageService = new DatasetStorageService(s3Provider);
  }

  /**
   * Aggregate processed documents into a dataset
   */
  async aggregateFromDocuments(options: DatasetAggregationOptions): Promise<DatasetAggregationResult> {
    const {
      name,
      description = '',
      category = 'aggregated',
      source,
      provenance,
      license = 'unknown',
      privacy_status = 'private',
      account_id,
      collection_job_id,
      source_id,
      min_quality_score = 0.5
    } = options;

    try {
      // Query processed documents from nexus.documents table
      let query = `
        SELECT id, source_id as source_id, title, content,
               language, content_hash as checksum, quality_score as quality_score,
               created_at
        FROM nexus.documents
        WHERE status = 'active'
          AND quality_score >= $1
      `;
      const params: any[] = [min_quality_score];

      if (collection_job_id) {
        query += ` AND source_id IN (SELECT source_id FROM nexus.collection_jobs WHERE id = $${params.length + 1})`;
        params.push(collection_job_id);
      }

      if (source_id) {
        query += ` AND source_id = $${params.length + 1}`;
        params.push(source_id);
      }

      query += ` ORDER BY created_at ASC`;

      const result = await this.db.query(query, params);
      const documents = result.rows.map((row: any) => ({
        id: row.id,
        collection_job_id: collection_job_id || null,
        source_id: row.source_id,
        final_url: null,
        title: row.title,
        content: row.content,
        content_type: 'text/html',
        language: row.language,
        checksum: row.checksum,
        processing_status: 'accepted' as const,
        quality_score: row.quality_score,
        quality_reasons: [],
        created_at: row.created_at
      })) as ProcessedDocument[];

      if (documents.length === 0) {
        throw new Error('No documents match the aggregation criteria');
      }

      // Prepare dataset as JSONL
      const datasetContent = this.prepareDatasetJsonl(documents);
      const buffer = Buffer.from(datasetContent, 'utf-8');

      // Calculate checksum
      const hash = crypto.createHash('sha256');
      hash.update(buffer);
      const sha256Checksum = hash.digest('hex');

      // Generate version
      const version = 'v1.0';

      // Upload to storage
      const storageResult = await this.storageService.uploadDataset(buffer, 'application/jsonl', {
        userId: account_id,
        datasetId: name,
        version,
        fileFormat: 'jsonl',
        metadata: {
          name,
          description,
          datasetType: category,
          language: 'mixed',
          domain: 'general',
          taskType: 'training',
        },
      });

      // Register in dataset_registry
      const insertResult = await this.db.query(
        `INSERT INTO nexus.dataset_registry
         (account_id, dataset_name, description, category, storage_key, file_size_bytes,
          sha256_checksum, mime_type, version, source, provenance, license, privacy_status,
          validation_status, approval_status, training_eligible)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
         RETURNING id`,
        [
          account_id,
          name,
          description,
          category,
          storageResult.key,
          buffer.length,
          sha256Checksum,
          'application/jsonl',
          version,
          source,
          provenance,
          license,
          privacy_status,
          'valid',
          'pending_review',
          false
        ]
      );

      const datasetId = insertResult.rows[0].id;

      // Create version record
      await this.db.query(
        `INSERT INTO nexus.dataset_versions
         (dataset_id, version, storage_key, file_size_bytes, sha256_checksum, is_active)
         VALUES ($1, $2, $3, $4, $5, true)`,
        [datasetId, version, storageResult.key, buffer.length, sha256Checksum]
      );

      return {
        dataset_id: datasetId,
        storage_key: storageResult.key,
        file_size_bytes: buffer.length,
        sha256_checksum: sha256Checksum,
        document_count: documents.length,
        version
      };
    } catch (error) {
      console.error('[Dataset Aggregation] Failed to aggregate documents:', error);
      throw error;
    }
  }

  /**
   * Prepare dataset as JSONL format
   */
  private prepareDatasetJsonl(documents: ProcessedDocument[]): string {
    return documents.map(doc => {
      const datasetItem = {
        id: doc.id,
        text: doc.content,
        metadata: {
          title: doc.title,
          url: doc.final_url,
          source_id: doc.source_id,
          collection_job_id: doc.collection_job_id,
          content_type: doc.content_type,
          language: doc.language,
          checksum: doc.checksum,
          quality_score: doc.quality_score,
          quality_reasons: doc.quality_reasons,
          created_at: doc.created_at
        }
      };
      return JSON.stringify(datasetItem);
    }).join('\n');
  }

  /**
   * Get statistics for potential dataset aggregation
   */
  async getAggregationStats(options: {
    collection_job_id?: string;
    source_id?: string;
    min_quality_score?: number;
  }): Promise<{
    total_documents: number;
    accepted_documents: number;
    average_quality_score: number;
    estimated_size_bytes: number;
  }> {
    const {
      collection_job_id,
      source_id,
      min_quality_score = 0.5
    } = options;

    try {
      let query = `
        SELECT
          COUNT(*) as total_documents,
          COUNT(*) FILTER (WHERE status = 'active') as accepted_documents,
          AVG(quality_score) as avg_quality_score,
          SUM(LENGTH(content)) as estimated_size_bytes
        FROM nexus.documents
        WHERE quality_score >= $1
      `;
      const params: any[] = [min_quality_score];

      if (collection_job_id) {
        query += ` AND source_id IN (SELECT source_id FROM nexus.collection_jobs WHERE id = $${params.length + 1})`;
        params.push(collection_job_id);
      }

      if (source_id) {
        query += ` AND source_id = $${params.length + 1}`;
        params.push(source_id);
      }

      const result = await this.db.query(query, params);
      const row = result.rows[0];

      return {
        total_documents: parseInt(row.total_documents || 0),
        accepted_documents: parseInt(row.accepted_documents || 0),
        average_quality_score: parseFloat(row.avg_quality_score || 0),
        estimated_size_bytes: parseInt(row.estimated_size_bytes || 0)
      };
    } catch (error) {
      console.error('[Dataset Aggregation] Failed to get stats:', error);
      throw error;
    }
  }
}
