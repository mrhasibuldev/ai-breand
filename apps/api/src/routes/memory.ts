/**
 * Memory API Routes
 * Persistent memory operations for user data
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';

const VALID_CATEGORIES = ['name', 'age_band', 'wellness_goal', 'preference', 'daily_habit', 'plan_preference', 'custom'];
const VALID_STATUSES = ['candidate', 'approved', 'rejected', 'revoked', 'deleted'];

export function memoryRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);

  // GET /api/v1/me/memories - List user memories
  app.get('/api/v1/me/memories', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    try {
      await db.connect();
      const result = await db.query(
        `SELECT id, category, purpose, value, status, created_at, updated_at, deleted_at
         FROM nexus.memory_records
         WHERE account_id = $1 AND status != 'deleted'
         ORDER BY created_at DESC`,
        [principal]
      );

      return {
        memories: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Memory] Failed to retrieve memories:', error);
      return reply.status(500).send({ error: 'Failed to retrieve memories', code: 'internal_error' });
    }
  });

  // GET /api/v1/me/memories/:id - Get specific memory
  app.get('/api/v1/me/memories/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      await db.connect();
      const result = await db.query(
        `SELECT id, category, purpose, value, status, created_at, updated_at, deleted_at
         FROM nexus.memory_records
         WHERE account_id = $1 AND id = $2 AND status != 'deleted'`,
        [principal, id]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Memory not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Memory] Failed to retrieve memory:', error);
      return reply.status(500).send({ error: 'Failed to retrieve memory', code: 'internal_error' });
    }
  });

  // POST /api/v1/me/memories - Create memory
  app.post('/api/v1/me/memories', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const body = request.body as {
      category?: string;
      purpose?: string;
      value?: string;
      status?: string;
    };

    // Validate category
    if (!body.category || !VALID_CATEGORIES.includes(body.category)) {
      return reply.status(400).send({ error: 'Invalid category', code: 'invalid_category' });
    }

    // Validate purpose
    if (!body.purpose || body.purpose.trim().length === 0) {
      return reply.status(400).send({ error: 'Purpose is required', code: 'invalid_purpose' });
    }

    // Validate value
    if (!body.value || body.value.trim().length === 0) {
      return reply.status(400).send({ error: 'Value is required', code: 'invalid_value' });
    }

    // Validate status
    const status = body.status || 'candidate';
    if (!VALID_STATUSES.includes(status)) {
      return reply.status(400).send({ error: 'Invalid status', code: 'invalid_status' });
    }

    try {
      await db.connect();
      const result = await db.query(
        `INSERT INTO nexus.memory_records
         (account_id, category, purpose, value, status)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id, category, purpose, value, status, created_at, updated_at`,
        [principal, body.category, body.purpose, body.value, status]
      );

      return reply.status(201).send(result.rows[0]);
    } catch (error: any) {
      console.error('[Memory] Failed to create memory:', error);
      return reply.status(500).send({ error: 'Failed to create memory', code: 'internal_error', detail: error.message });
    }
  });

  // PATCH /api/v1/me/memories/:id - Update memory
  app.patch('/api/v1/me/memories/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };
    const body = request.body as {
      category?: string;
      purpose?: string;
      value?: string;
      status?: string;
    };

    // Build update query dynamically
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (body.category !== undefined) {
      if (!VALID_CATEGORIES.includes(body.category)) {
        return reply.status(400).send({ error: 'Invalid category', code: 'invalid_category' });
      }
      updates.push(`category = $${paramIndex++}`);
      values.push(body.category);
    }

    if (body.purpose !== undefined) {
      if (body.purpose.trim().length === 0) {
        return reply.status(400).send({ error: 'Purpose cannot be empty', code: 'invalid_purpose' });
      }
      updates.push(`purpose = $${paramIndex++}`);
      values.push(body.purpose);
    }

    if (body.value !== undefined) {
      if (body.value.trim().length === 0) {
        return reply.status(400).send({ error: 'Value cannot be empty', code: 'invalid_value' });
      }
      updates.push(`value = $${paramIndex++}`);
      values.push(body.value);
    }

    if (body.status !== undefined) {
      if (!VALID_STATUSES.includes(body.status)) {
        return reply.status(400).send({ error: 'Invalid status', code: 'invalid_status' });
      }
      updates.push(`status = $${paramIndex++}`);
      values.push(body.status);
    }

    if (updates.length === 0) {
      return reply.status(400).send({ error: 'No updates provided', code: 'no_updates' });
    }

    values.push(principal);
    values.push(id);

    try {
      await db.connect();
      const result = await db.query(
        `UPDATE nexus.memory_records
         SET ${updates.join(', ')}, updated_at = NOW()
         WHERE account_id = $${paramIndex++} AND id = $${paramIndex++} AND status != 'deleted'
         RETURNING id, category, purpose, value, status, created_at, updated_at`,
        values
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Memory not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Memory] Failed to update memory:', error);
      return reply.status(500).send({ error: 'Failed to update memory', code: 'internal_error' });
    }
  });

  // DELETE /api/v1/me/memories/:id - Soft delete memory
  app.delete('/api/v1/me/memories/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      await db.connect();
      const result = await db.query(
        `UPDATE nexus.memory_records
         SET status = 'deleted', deleted_at = NOW(), updated_at = NOW()
         WHERE account_id = $1 AND id = $2 AND status != 'deleted'
         RETURNING id`,
        [principal, id]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Memory not found', code: 'not_found' });
      }

      return reply.status(204).send();
    } catch (error) {
      console.error('[Memory] Failed to delete memory:', error);
      return reply.status(500).send({ error: 'Failed to delete memory', code: 'internal_error' });
    }
  });

  // GET /api/v1/me/memories/category/:category - Get memories by category
  app.get('/api/v1/me/memories/category/:category', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { category } = request.params as { category: string };

    if (!VALID_CATEGORIES.includes(category)) {
      return reply.status(400).send({ error: 'Invalid category', code: 'invalid_category' });
    }

    try {
      await db.connect();
      const result = await db.query(
        `SELECT id, category, purpose, value, status, created_at, updated_at
         FROM nexus.memory_records
         WHERE account_id = $1 AND category = $2 AND status != 'deleted'
         ORDER BY created_at DESC`,
        [principal, category]
      );

      return {
        memories: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Memory] Failed to retrieve memories by category:', error);
      return reply.status(500).send({ error: 'Failed to retrieve memories', code: 'internal_error' });
    }
  });
}
