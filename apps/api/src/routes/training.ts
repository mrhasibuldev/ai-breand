/**
 * Training Pipeline API Routes
 * Integrate training with database metadata
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';

const VALID_STATUSES = ['pending', 'running', 'completed', 'failed', 'cancelled'];

export function trainingRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);

  // POST /api/v1/training/start - Start training run
  app.post('/api/v1/training/start', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const body = request.body as {
      dataset_id?: string;
      dataset_version?: string;
      model_config?: any;
      training_config?: any;
    };

    if (!body.dataset_id) {
      return reply.status(400).send({ error: 'dataset_id is required', code: 'invalid_dataset' });
    }

    try {
      await db.connect();
      // Verify dataset exists and is training-eligible
      const datasetResult = await db.query(
        `SELECT id, dataset_name, version, training_eligible, approval_status, storage_key
         FROM nexus.dataset_registry
         WHERE id = $1 AND training_eligible = true AND approval_status = 'approved'`,
        [body.dataset_id]
      );

      if (datasetResult.rows.length === 0) {
        return reply.status(400).send({ error: 'Dataset not found or not training-eligible', code: 'invalid_dataset' });
      }

      const dataset = datasetResult.rows[0] as any;

      // Create training run
      const runResult = await db.query(
        `INSERT INTO nexus.training_runs
         (dataset_id, dataset_version, model_config, training_config, status, started_at)
         VALUES ($1, $2, $3, $4, 'pending', NOW())
         RETURNING id`,
        [
          body.dataset_id,
          body.dataset_version || dataset.version,
          JSON.stringify(body.model_config || {}),
          JSON.stringify(body.training_config || {})
        ]
      );

      const runId = (runResult.rows[0] as any).id;

      return reply.status(201).send({
        run_id: runId,
        status: 'pending',
        dataset_id: body.dataset_id,
        dataset_version: body.dataset_version || (dataset as any).version,
        message: 'Training run created. Execute training pipeline manually with this run_id.'
      });
    } catch (error) {
      console.error('[Training] Failed to start training:', error);
      return reply.status(500).send({ error: 'Failed to start training', code: 'internal_error' });
    }
  });

  // POST /api/v1/training/:id/update - Update training run status
  app.post('/api/v1/training/:id/update', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };
    const body = request.body as {
      status?: string;
      metrics?: any;
      checkpoint_path?: string;
      error_message?: string;
    };

    if (!body.status || !VALID_STATUSES.includes(body.status)) {
      return reply.status(400).send({ error: 'Invalid status', code: 'invalid_status' });
    }

    try {
      await db.connect();
      const updates: string[] = ['status = $1'];
      const values: any[] = [body.status];
      let paramIndex = 2;

      if (body.metrics !== undefined) {
        updates.push(`metrics = $${paramIndex++}`);
        values.push(JSON.stringify(body.metrics));
      }

      if (body.checkpoint_path !== undefined) {
        updates.push(`checkpoint_path = $${paramIndex++}`);
        values.push(body.checkpoint_path);
      }

      if (body.error_message !== undefined) {
        updates.push(`error_message = $${paramIndex++}`);
        values.push(body.error_message);
      }

      if (body.status === 'completed' || body.status === 'failed' || body.status === 'cancelled') {
        updates.push(`completed_at = NOW()`);
      } else if (body.status === 'running') {
        updates.push(`started_at = NOW()`);
      }

      values.push(id);

      const result = await db.query(
        `UPDATE nexus.training_runs
         SET ${updates.join(', ')}
         WHERE id = $${paramIndex}
         RETURNING id, status, dataset_id, started_at, completed_at`,
        values
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Training run not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Training] Failed to update training run:', error);
      return reply.status(500).send({ error: 'Failed to update training run', code: 'internal_error' });
    }
  });

  // GET /api/v1/training/runs - List training runs
  app.get('/api/v1/training/runs', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const limit = parseInt((request.query as any).limit as string) || 50;

    try {
      await db.connect();
      const result = await db.query(
        `SELECT
           tr.id,
           tr.dataset_id,
           tr.dataset_version,
           tr.model_config,
           tr.training_config,
           tr.metrics,
           tr.checkpoint_path,
           tr.status,
           tr.started_at,
           tr.completed_at,
           tr.error_message,
           tr.created_at,
           dr.dataset_name
         FROM nexus.training_runs tr
         JOIN nexus.dataset_registry dr ON tr.dataset_id = dr.id
         ORDER BY tr.created_at DESC
         LIMIT $1`,
        [limit]
      );

      return {
        runs: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Training] Failed to retrieve training runs:', error);
      return reply.status(500).send({ error: 'Failed to retrieve training runs', code: 'internal_error' });
    }
  });

  // GET /api/v1/training/runs/:id - Get specific training run
  app.get('/api/v1/training/runs/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      await db.connect();
      const result = await db.query(
        `SELECT
           tr.id,
           tr.dataset_id,
           tr.dataset_version,
           tr.model_config,
           tr.training_config,
           tr.metrics,
           tr.checkpoint_path,
           tr.status,
           tr.started_at,
           tr.completed_at,
           tr.error_message,
           tr.created_at,
           dr.dataset_name,
           dr.storage_key,
           dr.sha256_checksum
         FROM nexus.training_runs tr
         JOIN nexus.dataset_registry dr ON tr.dataset_id = dr.id
         WHERE tr.id = $1`,
        [id]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Training run not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Training] Failed to retrieve training run:', error);
      return reply.status(500).send({ error: 'Failed to retrieve training run', code: 'internal_error' });
    }
  });

  // GET /api/v1/training/eligible-datasets - Get training-eligible datasets
  app.get('/api/v1/training/eligible-datasets', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    try {
      await db.connect();
      const result = await db.query(
        `SELECT
           id,
           dataset_name,
           description,
           category,
           version,
           storage_key,
           file_size_bytes,
           sha256_checksum,
           approval_status,
           training_eligible,
           created_at
         FROM nexus.dataset_registry
         WHERE training_eligible = true AND approval_status = 'approved'
         ORDER BY created_at DESC`
      );

      return {
        datasets: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Training] Failed to retrieve eligible datasets:', error);
      return reply.status(500).send({ error: 'Failed to retrieve eligible datasets', code: 'internal_error' });
    }
  });
}
