/**
 * Collection Job API Routes
 * Manages collection jobs and triggers source collection
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';
import { CollectionEngine, CollectionJobConfig } from '../collection-engine/CollectionEngine.js';
import { ProcessingService } from '../processing/ProcessingService.js';

const VALID_JOB_TYPES = ['full', 'incremental', 'manual'];
const VALID_STATUSES = ['pending', 'running', 'completed', 'failed', 'cancelled'];

// Singleton collection engine instance
let collectionEngine: CollectionEngine | null = null;
let processingService: ProcessingService | null = null;

function getCollectionEngine(): CollectionEngine {
  if (!collectionEngine) {
    collectionEngine = new CollectionEngine();
    collectionEngine.initialize();
  }
  return collectionEngine;
}

function getProcessingService(): ProcessingService {
  if (!processingService) {
    processingService = new ProcessingService();
    processingService.initialize();
  }
  return processingService;
}

export function collectionRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);

  // POST /api/v1/collection/jobs - Create collection job
  app.post('/api/v1/collection/jobs', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const body = request.body as {
      source_id?: string;
      job_type?: string;
      dry_run?: boolean;
      max_documents?: number;
      max_document_size?: number;
      max_retries?: number;
      timeout?: number;
    };

    if (!body.source_id) {
      return reply.status(400).send({ error: 'source_id is required', code: 'invalid_source' });
    }

    if (!body.job_type || !VALID_JOB_TYPES.includes(body.job_type)) {
      return reply.status(400).send({ error: 'Invalid job_type', code: 'invalid_job_type' });
    }

    try {
      await db.connect();

      // Verify source exists and is active
      const sourceResult = await db.query(
        `SELECT id FROM nexus.knowledge_sources WHERE id = $1 AND status = 'active'`,
        [body.source_id]
      );

      if (sourceResult.rows.length === 0) {
        return reply.status(404).send({ error: 'Source not found or not active', code: 'not_found' });
      }

      // Create job
      const config: CollectionJobConfig = {
        sourceId: body.source_id,
        jobType: body.job_type as 'full' | 'incremental' | 'manual',
        dryRun: body.dry_run ?? undefined,
        maxDocuments: body.max_documents ?? undefined,
        maxDocumentSize: body.max_document_size ?? undefined,
        maxRetries: body.max_retries ?? undefined,
        timeout: body.timeout ?? undefined
      };

      const engine = getCollectionEngine();
      const jobId = await engine.createJob(config);

      // Execute job asynchronously (in production, use a proper job queue)
      // For now, execute synchronously for testing
      const result = await engine.executeJob(jobId, config);

      // If not dry-run and successful, process the collected items
      if (!config.dryRun && result.status === 'success' && result.items.length > 0) {
        try {
          const processor = getProcessingService();
          await processor.initialize();
          // Convert CollectionItem to RawCollectionItem
          const rawItems = result.items.map(item => ({
            sourceId: item.sourceId,
            originalUrl: item.originalUrl,
            ...(item.finalUrl ? { finalUrl: item.finalUrl } : {}),
            ...(item.title ? { title: item.title } : {}),
            ...(item.content ? { content: item.content } : {}),
            ...(item.contentType ? { contentType: item.contentType } : {}),
            ...(item.language ? { language: item.language } : {}),
            ...(item.publicationDate ? { publicationDate: item.publicationDate } : {}),
            ...(item.author ? { author: item.author } : {}),
            collectionTimestamp: item.collectionTimestamp,
            ...(item.license ? { license: item.license } : {}),
            ...(item.licenseMetadata ? { licenseMetadata: item.licenseMetadata } : {}),
            ...(item.httpStatus ? { httpStatus: item.httpStatus } : {}),
            ...(item.checksum ? { checksum: item.checksum } : {}),
            ...(item.sizeBytes ? { sizeBytes: item.sizeBytes } : {}),
            ...(item.error ? { error: item.error } : {})
          }));

          const processingResult = await processor.processCollectionJob(jobId, rawItems);

          return reply.status(201).send({
            job_id: jobId,
            status: result.status,
            items_collected: result.itemsCollected,
            items_failed: result.itemsFailed,
            items_skipped: result.itemsSkipped,
            bytes_downloaded: result.bytesDownloaded,
            duration_ms: result.durationMs,
            errors: result.errors,
            processing: {
              total_processed: processingResult.totalProcessed,
              accepted: processingResult.accepted,
              rejected: processingResult.rejected,
              duplicate: processingResult.duplicate,
              failed: processingResult.failed
            }
          });
        } catch (processError) {
          const errorMessage = processError instanceof Error ? processError.message : String(processError);
          console.error('[Collection] Processing failed:', processError);
          // Return collection result even if processing failed
          return reply.status(201).send({
            job_id: jobId,
            status: result.status,
            items_collected: result.itemsCollected,
            items_failed: result.itemsFailed,
            items_skipped: result.itemsSkipped,
            bytes_downloaded: result.bytesDownloaded,
            duration_ms: result.durationMs,
            errors: result.errors,
            processing_error: `Processing failed: ${errorMessage}`
          });
        }
      }

      return reply.status(201).send({
        job_id: jobId,
        status: result.status,
        items_collected: result.itemsCollected,
        items_failed: result.itemsFailed,
        items_skipped: result.itemsSkipped,
        bytes_downloaded: result.bytesDownloaded,
        duration_ms: result.durationMs,
        errors: result.errors
      });

    } catch (error) {
      console.error('[Collection] Failed to create job:', error);
      return reply.status(500).send({ error: 'Failed to create job', code: 'internal_error' });
    }
  });

  // GET /api/v1/collection/jobs - List collection jobs
  app.get('/api/v1/collection/jobs', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const limit = parseInt((request.query as any).limit as string) || 50;

    try {
      const engine = getCollectionEngine();
      const jobs = await engine.listJobs(limit);

      return {
        jobs,
        count: jobs.length
      };
    } catch (error) {
      console.error('[Collection] Failed to list jobs:', error);
      return reply.status(500).send({ error: 'Failed to list jobs', code: 'internal_error' });
    }
  });

  // GET /api/v1/collection/jobs/:id - Get specific job
  app.get('/api/v1/collection/jobs/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      const engine = getCollectionEngine();
      const job = await engine.getJobStatus(id);

      return job;
    } catch (error) {
      console.error('[Collection] Failed to get job:', error);
      return reply.status(500).send({ error: 'Failed to get job', code: 'internal_error' });
    }
  });

  // POST /api/v1/collection/jobs/:id/cancel - Cancel job
  app.post('/api/v1/collection/jobs/:id/cancel', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      const engine = getCollectionEngine();
      await engine.cancelJob(id);

      return { success: true, message: 'Job cancelled' };
    } catch (error) {
      console.error('[Collection] Failed to cancel job:', error);
      return reply.status(500).send({ error: 'Failed to cancel job', code: 'internal_error' });
    }
  });

  // GET /api/v1/collection/jobs/:id/processing - Get processing statistics
  app.get('/api/v1/collection/jobs/:id/processing', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      const processor = getProcessingService();
      const stats = await processor.getJobProcessingStats(id);

      return stats;
    } catch (error) {
      console.error('[Collection] Failed to get processing stats:', error);
      return reply.status(500).send({ error: 'Failed to get processing stats', code: 'internal_error' });
    }
  });

  console.log('[API] Collection job routes registered');
}
