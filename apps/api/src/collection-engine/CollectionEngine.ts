/**
 * Collection Engine
 * Manages collection jobs and coordinates source adapters
 */

import { SourceAdapter, SourceConfig, CollectionOptions, CollectionResult } from './SourceAdapter.js';
import { HttpSourceAdapter } from './HttpSourceAdapter.js';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';

export interface CollectionJobConfig {
  sourceId: string;
  jobType: 'full' | 'incremental' | 'manual';
  dryRun?: boolean | undefined;
  maxDocuments?: number | undefined;
  maxDocumentSize?: number | undefined;
  maxRetries?: number | undefined;
  timeout?: number | undefined;
}

export class CollectionEngine {
  private db: any;
  private adapters = new Map<string, SourceAdapter>();

  constructor() {
    const config = readDatabaseConfig();
    this.db = createDatabaseClient(config);

    // Register default adapters
    this.registerAdapter('http', new HttpSourceAdapter());
    this.registerAdapter('api', new HttpSourceAdapter()); // API uses HTTP adapter
  }

  registerAdapter(type: string, adapter: SourceAdapter) {
    this.adapters.set(type, adapter);
  }

  async initialize() {
    await this.db.connect();
  }

  async createJob(config: CollectionJobConfig): Promise<string> {
    const result = await this.db.query(
      `INSERT INTO nexus.collection_jobs
       (source_id, job_type, status, created_at)
       VALUES ($1, $2, 'pending', NOW())
       RETURNING id`,
      [config.sourceId, config.jobType]
    );

    return result.rows[0].id;
  }

  async startJob(jobId: string): Promise<void> {
    await this.db.query(
      `UPDATE nexus.collection_jobs
       SET status = 'running', started_at = NOW()
       WHERE id = $1`,
      [jobId]
    );
  }

  async completeJob(jobId: string, result: CollectionResult): Promise<void> {
    await this.db.query(
      `UPDATE nexus.collection_jobs
       SET status = 'completed',
           completed_at = NOW(),
           documents_collected = $1,
           documents_failed = $2,
           documents_skipped = $3,
           bytes_downloaded = $4,
           error_message = $5,
           metadata = $6
       WHERE id = $7`,
      [
        result.itemsCollected,
        result.itemsFailed,
        result.itemsSkipped,
        result.bytesDownloaded,
        result.errors.length > 0 ? JSON.stringify(result.errors) : null,
        JSON.stringify(result.metadata || {}),
        jobId
      ]
    );
  }

  async failJob(jobId: string, error: string): Promise<void> {
    await this.db.query(
      `UPDATE nexus.collection_jobs
       SET status = 'failed',
           completed_at = NOW(),
           error_message = $1
       WHERE id = $2`,
      [error, jobId]
    );
  }

  async cancelJob(jobId: string): Promise<void> {
    await this.db.query(
      `UPDATE nexus.collection_jobs
       SET status = 'cancelled',
           completed_at = NOW()
       WHERE id = $1 AND status = 'pending'`,
      [jobId]
    );
  }

  async executeJob(jobId: string, config: CollectionJobConfig): Promise<CollectionResult> {
    try {
      // Update job status to running
      await this.startJob(jobId);

      // Fetch source configuration
      const sourceResult = await this.db.query(
        `SELECT * FROM nexus.knowledge_sources WHERE id = $1`,
        [config.sourceId]
      );

      if (sourceResult.rows.length === 0) {
        throw new Error('Source not found');
      }

      const source = sourceResult.rows[0];
      const adapter = this.adapters.get(source.collection_method);

      if (!adapter) {
        throw new Error(`No adapter found for collection method: ${source.collection_method}`);
      }

      // Build source config
      const sourceConfig: SourceConfig = {
        sourceId: source.id,
        sourceType: source.source_type,
        sourceUrl: source.source_url,
        sourceName: source.source_name,
        collectionMethod: source.collection_method,
        apiConfigRef: source.api_config_ref,
        robotsTxtPolicy: source.robots_txt_policy,
        tosStatus: source.tos_status,
        language: source.language,
        trustLevel: source.trust_level,
        metadata: source.metadata
      };

      // Build collection options
      const options: CollectionOptions = {
        dryRun: config.dryRun ?? undefined,
        maxDocuments: config.maxDocuments ?? undefined,
        maxDocumentSize: config.maxDocumentSize ?? undefined,
        maxRetries: config.maxRetries ?? undefined,
        timeout: config.timeout ?? undefined
      };

      // Validate source
      const validation = await adapter.validate(sourceConfig);
      if (!validation.valid) {
        throw new Error(`Source validation failed: ${validation.errors.join(', ')}`);
      }

      // Execute collection
      const result = await adapter.collect(sourceConfig, options);

      // Update job status to completed
      await this.completeJob(jobId, result);

      // Update source last_successful_collection
      await this.db.query(
        `UPDATE nexus.knowledge_sources
         SET last_successful_collection = NOW()
         WHERE id = $1`,
        [config.sourceId]
      );

      return result;

    } catch (error) {
      // Update job status to failed
      await this.failJob(jobId, String(error));
      throw error;
    }
  }

  async getJobStatus(jobId: string): Promise<any> {
    const result = await this.db.query(
      `SELECT * FROM nexus.collection_jobs WHERE id = $1`,
      [jobId]
    );

    if (result.rows.length === 0) {
      throw new Error('Job not found');
    }

    return result.rows[0];
  }

  async listJobs(limit: number = 50): Promise<any[]> {
    const result = await this.db.query(
      `SELECT * FROM nexus.collection_jobs
       ORDER BY created_at DESC
       LIMIT $1`,
      [limit]
    );

    return result.rows;
  }
}
