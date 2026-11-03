/**
 * Dataset Registry API Routes
 *
 * Handles dataset registration, listing, approval workflow, and training eligibility
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';
import { createS3ProviderFromEnv, DatasetStorageService } from '@nexusai/storage-core';
import { DatasetAggregationService } from '../services/DatasetAggregationService.js';
import { TrainingDataGenerationService } from '../services/TrainingDataGenerationService.js';
import crypto from 'node:crypto';

interface DatasetRegistryBody {
  dataset_name: string;
  description?: string;
  category?: string;
  version?: string;
  source?: string;
  provenance?: string;
  license?: string;
  privacy_status?: 'public' | 'private' | 'restricted';
}

interface DatasetApprovalBody {
  approval_status: 'approved' | 'rejected' | 'archived';
  reason?: string;
}

interface DatasetAggregationBody {
  name: string;
  description?: string;
  category?: string;
  source: string;
  provenance: string;
  license?: string;
  privacy_status?: 'public' | 'private' | 'restricted';
  collection_job_id?: string;
  source_id?: string;
  min_quality_score?: number;
}

interface TrainingDataGenerationBody {
  dataset_id: string;
  dataset_version: string;
  train_split?: number;
  max_len?: number;
  shuffle?: boolean;
}

export async function datasetRegistryRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);
  await db.connect();

  // Initialize storage service for checksum verification
  let storageService: DatasetStorageService | null = null;
  try {
    const s3Provider = createS3ProviderFromEnv();
    storageService = new DatasetStorageService(s3Provider);
  } catch (error) {
    console.error('[Dataset Registry] Failed to initialize storage service:', error);
  }

  /**
   * POST /api/datasets/register
   * Register a new dataset (requires upload to have completed first)
   */
  app.post('/api/datasets/register', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const body = request.body as DatasetRegistryBody;
    const { dataset_name, description, category, version, source, provenance, license, privacy_status } = body;

    if (!dataset_name) {
      return reply.status(400).send({ error: 'dataset_name is required' });
    }

    try {
      // For now, this is a placeholder. In a complete implementation, this would:
      // 1. Accept a storage_key from a completed upload
      // 2. Verify the file exists in storage
      // 3. Calculate SHA-256 checksum
      // 4. Insert into dataset_registry

      return reply.status(501).send({
        error: 'Dataset registration requires storage_key from completed upload',
        note: 'This endpoint will be completed after storage integration is finalized'
      });
    } catch (error) {
      console.error('[Dataset Registry] Registration error:', error);
      return reply.status(500).send({ error: 'Registration failed' });
    }
  });

  /**
   * POST /api/datasets/aggregate
   * Aggregate processed documents into a dataset
   */
  app.post('/api/datasets/aggregate', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const body = request.body as DatasetAggregationBody;
    const { name, description, category, source, provenance, license, privacy_status, collection_job_id, source_id, min_quality_score } = body;

    if (!name || !source || !provenance) {
      return reply.status(400).send({ error: 'name, source, and provenance are required' });
    }

    try {
      const aggregationService = new DatasetAggregationService();
      const aggregationOptions: any = {
        name,
        source,
        provenance,
        account_id: userId,
        min_quality_score
      };

      if (description !== undefined) aggregationOptions.description = description;
      if (category !== undefined) aggregationOptions.category = category;
      if (license !== undefined) aggregationOptions.license = license;
      if (privacy_status !== undefined) aggregationOptions.privacy_status = privacy_status;
      if (collection_job_id !== undefined) aggregationOptions.collection_job_id = collection_job_id;
      if (source_id !== undefined) aggregationOptions.source_id = source_id;

      const result = await aggregationService.aggregateFromDocuments(aggregationOptions);

      return { success: true, dataset: result };
    } catch (error) {
      console.error('[Dataset Registry] Aggregation error:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      return reply.status(500).send({ error: 'Aggregation failed', details: errorMessage });
    }
  });

  /**
   * GET /api/datasets/aggregate/stats
   * Get statistics for potential dataset aggregation
   */
  app.get('/api/datasets/aggregate/stats', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const query = request.query as {
      collection_job_id?: string;
      source_id?: string;
      min_quality_score?: string;
    };

    try {
      const aggregationService = new DatasetAggregationService();
      const statsOptions: any = {
        min_quality_score: query.min_quality_score ? parseFloat(query.min_quality_score) : 0.5
      };

      if (query.collection_job_id !== undefined) statsOptions.collection_job_id = query.collection_job_id;
      if (query.source_id !== undefined) statsOptions.source_id = query.source_id;

      const stats = await aggregationService.getAggregationStats(statsOptions);

      return { stats };
    } catch (error) {
      console.error('[Dataset Registry] Aggregation stats error:', error);
      return reply.status(500).send({ error: 'Failed to get aggregation stats' });
    }
  });

  /**
   * GET /api/datasets
   * Health check for dataset registry
   */
  app.get('/api/datasets', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    try {
      const result = await db.query(
        `SELECT id, dataset_name, description, category, version, 
                storage_key, file_size_bytes, sha256_checksum, mime_type,
                source, license, privacy_status, validation_status, 
                approval_status, training_eligible, created_at, updated_at
         FROM nexus.dataset_registry
         WHERE account_id = $1 AND deleted_at IS NULL
         ORDER BY created_at DESC`,
        [userId]
      );

      return { datasets: result.rows };
    } catch (error) {
      console.error('[Dataset Registry] List error:', error);
      return reply.status(500).send({ error: 'Failed to list datasets' });
    }
  });

  /**
   * GET /api/datasets/:id
   * Get a specific dataset
   */
  app.get('/api/datasets/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const { id } = request.params as { id: string };

    try {
      const result = await db.query(
        `SELECT id, dataset_name, description, category, version,
                storage_key, file_size_bytes, sha256_checksum, mime_type,
                source, provenance, license, privacy_status, validation_status,
                approval_status, training_eligible, created_at, updated_at
         FROM nexus.dataset_registry
         WHERE id = $1 AND account_id = $2 AND deleted_at IS NULL`,
        [id, userId]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Dataset not found' });
      }

      return { dataset: result.rows[0] };
    } catch (error) {
      console.error('[Dataset Registry] Get error:', error);
      return reply.status(500).send({ error: 'Failed to get dataset' });
    }
  });

  /**
   * POST /api/datasets/:id/approve
   * Approve or reject a dataset (admin/owner only)
   */
  app.post('/api/datasets/:id/approve', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const { id } = request.params as { id: string };
    const body = request.body as DatasetApprovalBody;
    const { approval_status, reason } = body;

    if (!approval_status || !['approved', 'rejected', 'archived'].includes(approval_status)) {
      return reply.status(400).send({ error: 'Invalid approval_status' });
    }

    try {
      // Get current dataset
      const currentResult = await db.query(
        `SELECT approval_status, account_id FROM nexus.dataset_registry
         WHERE id = $1 AND deleted_at IS NULL`,
        [id]
      );

      if (currentResult.rows.length === 0) {
        return reply.status(404).send({ error: 'Dataset not found' });
      }

      const current = currentResult.rows[0] as { approval_status: string; account_id: string };

      // Only owner can approve their own datasets
      // (In production, add admin role check)
      if (current.account_id !== userId) {
        return reply.status(403).send({ error: 'Forbidden' });
      }

      // Update approval status
      await db.query(
        `UPDATE nexus.dataset_registry
         SET approval_status = $1, updated_at = NOW()
         WHERE id = $2`,
        [approval_status, id]
      );

      // Record approval history
      await db.query(
        `INSERT INTO nexus.dataset_approval_history (dataset_id, reviewer_id, previous_status, new_status, reason)
         VALUES ($1, $2, $3, $4, $5)`,
        [id, userId, current.approval_status, approval_status, reason || null]
      );

      // If approved, mark as training eligible (for now - add more checks in production)
      if (approval_status === 'approved') {
        await db.query(
          `UPDATE nexus.dataset_registry
           SET training_eligible = true, validation_status = 'valid'
           WHERE id = $1`,
          [id]
        );
      }

      return { success: true, approval_status };
    } catch (error) {
      console.error('[Dataset Registry] Approval error:', error);
      return reply.status(500).send({ error: 'Approval failed' });
    }
  });

  /**
   * GET /api/datasets/training-eligible
   * List training-eligible datasets
   */
  app.get('/api/datasets/training-eligible', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    try {
      const result = await db.query(
        `SELECT id, dataset_name, version, storage_key, sha256_checksum,
                training_eligible, approval_status, created_at
         FROM nexus.dataset_registry
         WHERE account_id = $1
           AND training_eligible = true
           AND approval_status = 'approved'
           AND deleted_at IS NULL
         ORDER BY created_at DESC`,
        [userId]
      );

      return { datasets: result.rows };
    } catch (error) {
      console.error('[Dataset Registry] Training-eligible list error:', error);
      return reply.status(500).send({ error: 'Failed to list training-eligible datasets' });
    }
  });

  /**
   * POST /api/datasets/:id/training-data
   * Generate training data from an approved dataset
   */
  app.post('/api/datasets/:id/training-data', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const { id: dataset_id } = request.params as { id: string };
    const body = request.body as TrainingDataGenerationBody;
    const { dataset_version, train_split, max_len, shuffle } = body;

    if (!dataset_version) {
      return reply.status(400).send({ error: 'dataset_version is required' });
    }

    try {
      const trainingDataService = new TrainingDataGenerationService();
      const options: any = {
        dataset_id,
        dataset_version,
        account_id: userId
      };

      if (train_split !== undefined) options.train_split = train_split;
      if (max_len !== undefined) options.max_len = max_len;
      if (shuffle !== undefined) options.shuffle = shuffle;

      const result = await trainingDataService.generateTrainingData(options);

      return { success: true, training_data: result };
    } catch (error) {
      console.error('[Dataset Registry] Training data generation error:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      return reply.status(500).send({ error: 'Training data generation failed', details: errorMessage });
    }
  });

  console.log('[API] Dataset registry routes registered');
}
