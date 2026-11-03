/**
 * Processing Service
 * Integrates data processing with collection engine and database persistence
 */

import { DataProcessingPipeline, ProcessedDocument, ProcessingResult, RawCollectionItem } from './DataProcessingPipeline.js';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';

export class ProcessingService {
  private db: any;
  private pipeline: DataProcessingPipeline;

  constructor() {
    const config = readDatabaseConfig();
    this.db = createDatabaseClient(config);
    this.pipeline = new DataProcessingPipeline();
  }

  async initialize() {
    await this.db.connect();
  }

  /**
   * Process collection job results
   */
  async processCollectionJob(jobId: string, items: RawCollectionItem[]): Promise<ProcessingResult> {
    try {
      // Process items through pipeline
      const result = await this.pipeline.processCollection(items);

      // Persist accepted documents to database
      for (const doc of result.documents) {
        await this.persistDocument(doc, jobId);
      }

      return result;
    } catch (error) {
      throw new Error(`Processing failed: ${error}`);
    }
  }

  /**
   * Persist processed document to database
   */
  private async persistDocument(doc: ProcessedDocument, jobId: string): Promise<void> {
    try {
      await this.db.query(
        `INSERT INTO nexus.documents
         (id, source_id, content_hash, title, content, language, trust_level,
          quality_score, information_lifetime, word_count, char_count, author, publish_date, status,
          created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
         ON CONFLICT (content_hash) DO NOTHING`,
        [
          doc.id,
          doc.sourceId,
          doc.contentHash,
          doc.title || null,
          doc.normalizedContent,
          doc.language,
          'TIER_2', // Default trust level for collected content
          doc.qualityScore,
          'SLOW_CHANGING', // Default information lifetime
          doc.wordCount,
          doc.charCount,
          doc.author || null,
          doc.publicationDate ? new Date(doc.publicationDate) : null,
          'active'
        ]
      );
    } catch (error) {
      console.error(`Failed to persist document ${doc.id}:`, error);
      throw error;
    }
  }

  /**
   * Get processing statistics for a job
   */
  async getJobProcessingStats(jobId: string): Promise<any> {
    const result = await this.db.query(
      `SELECT
         COUNT(*) as total_documents,
         COUNT(CASE WHEN status = 'active' THEN 1 END) as active_documents,
         AVG(quality_score) as avg_quality_score,
         SUM(word_count) as total_words,
         SUM(char_count) as total_chars
       FROM nexus.documents
       WHERE source_id IN (
         SELECT source_id FROM nexus.collection_jobs WHERE id = $1
       )`,
      [jobId]
    );

    return result.rows[0];
  }

  /**
   * Reset pipeline cache
   */
  resetCache(): void {
    this.pipeline.resetCache();
  }
}
