/**
 * Knowledge Source Registry API Routes
 * Multi-source knowledge acquisition management
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';

const VALID_SOURCE_TYPES = ['web', 'book', 'article', 'documentation', 'dataset', 'user_uploaded'];
const VALID_COLLECTION_METHODS = ['api', 'crawl', 'rss', 'download', 'manual_upload'];
const VALID_TOS_STATUSES = ['unknown', 'compliant', 'restricted', 'blocked'];
const VALID_TRUST_LEVELS = ['TIER_1', 'TIER_2', 'TIER_3', 'TIER_4'];
const VALID_FREQUENCIES = ['once', 'daily', 'weekly', 'monthly', 'on_demand'];
const VALID_STATUSES = ['active', 'inactive', 'blocked'];

export function knowledgeSourceRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);

  // POST /api/v1/knowledge-sources - Register a knowledge source
  app.post('/api/v1/knowledge-sources', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const body = request.body as {
      source_type?: string;
      source_url?: string;
      source_name?: string;
      source_category?: string;
      description?: string;
      collection_method?: string;
      api_config_ref?: string;
      license?: string;
      copyright_notice?: string;
      robots_txt_policy?: string;
      tos_status?: string;
      language?: string;
      trust_level?: string;
      collection_frequency?: string;
      metadata?: any;
    };

    // Validate source_type
    if (!body.source_type || !VALID_SOURCE_TYPES.includes(body.source_type)) {
      return reply.status(400).send({ error: 'Invalid source_type', code: 'invalid_source_type' });
    }

    // Validate collection_method
    if (body.collection_method && !VALID_COLLECTION_METHODS.includes(body.collection_method)) {
      return reply.status(400).send({ error: 'Invalid collection_method', code: 'invalid_collection_method' });
    }

    // Validate trust_level
    if (body.trust_level && !VALID_TRUST_LEVELS.includes(body.trust_level)) {
      return reply.status(400).send({ error: 'Invalid trust_level', code: 'invalid_trust_level' });
    }

    // Validate collection_frequency
    if (body.collection_frequency && !VALID_FREQUENCIES.includes(body.collection_frequency)) {
      return reply.status(400).send({ error: 'Invalid collection_frequency', code: 'invalid_frequency' });
    }

    try {
      await db.connect();
      const result = await db.query(
        `INSERT INTO nexus.knowledge_sources
         (source_type, source_url, source_name, source_category, description, collection_method,
          api_config_ref, license, copyright_notice, robots_txt_policy, tos_status, language,
          trust_level, collection_frequency, metadata, status)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, 'active')
         RETURNING id, source_type, source_url, source_name, source_category, description,
                  collection_method, trust_level, collection_frequency, status, created_at`,
        [
          body.source_type,
          body.source_url || null,
          body.source_name || null,
          body.source_category || null,
          body.description || null,
          body.collection_method || null,
          body.api_config_ref || null,
          body.license || null,
          body.copyright_notice || null,
          body.robots_txt_policy || null,
          body.tos_status || 'unknown',
          body.language || null,
          body.trust_level || 'TIER_4',
          body.collection_frequency || 'on_demand',
          body.metadata || {}
        ]
      );

      return reply.status(201).send(result.rows[0]);
    } catch (error) {
      console.error('[Knowledge Sources] Failed to register source:', error);
      return reply.status(500).send({ error: 'Failed to register source', code: 'internal_error' });
    }
  });

  // GET /api/v1/knowledge-sources - List knowledge sources
  app.get('/api/v1/knowledge-sources', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const limit = parseInt((request.query as any).limit as string) || 50;
    const offset = parseInt((request.query as any).offset as string) || 0;

    try {
      await db.connect();
      const result = await db.query(
        `SELECT id, source_type, source_url, source_name, source_category, description,
                collection_method, trust_level, collection_frequency, tos_status, language,
                last_successful_collection, next_scheduled_collection, status, created_at, updated_at
         FROM nexus.knowledge_sources
         WHERE status != 'blocked'
         ORDER BY created_at DESC
         LIMIT $1 OFFSET $2`,
        [limit, offset]
      );

      return {
        sources: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Knowledge Sources] Failed to list sources:', error);
      return reply.status(500).send({ error: 'Failed to list sources', code: 'internal_error' });
    }
  });

  // GET /api/v1/knowledge-sources/:id - Get specific source
  app.get('/api/v1/knowledge-sources/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      await db.connect();
      const result = await db.query(
        `SELECT * FROM nexus.knowledge_sources WHERE id = $1`,
        [id]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Source not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Knowledge Sources] Failed to get source:', error);
      return reply.status(500).send({ error: 'Failed to get source', code: 'internal_error' });
    }
  });

  // PATCH /api/v1/knowledge-sources/:id - Update source
  app.patch('/api/v1/knowledge-sources/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };
    const body = request.body as {
      status?: string;
      trust_level?: string;
      collection_frequency?: string;
      next_scheduled_collection?: string;
      last_successful_collection?: string;
    };

    // Build update query dynamically
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (body.status !== undefined) {
      if (!VALID_STATUSES.includes(body.status)) {
        return reply.status(400).send({ error: 'Invalid status', code: 'invalid_status' });
      }
      updates.push(`status = $${paramIndex++}`);
      values.push(body.status);
    }

    if (body.trust_level !== undefined) {
      if (!VALID_TRUST_LEVELS.includes(body.trust_level)) {
        return reply.status(400).send({ error: 'Invalid trust_level', code: 'invalid_trust_level' });
      }
      updates.push(`trust_level = $${paramIndex++}`);
      values.push(body.trust_level);
    }

    if (body.collection_frequency !== undefined) {
      if (!VALID_FREQUENCIES.includes(body.collection_frequency)) {
        return reply.status(400).send({ error: 'Invalid collection_frequency', code: 'invalid_frequency' });
      }
      updates.push(`collection_frequency = $${paramIndex++}`);
      values.push(body.collection_frequency);
    }

    if (body.next_scheduled_collection !== undefined) {
      updates.push(`next_scheduled_collection = $${paramIndex++}`);
      values.push(body.next_scheduled_collection);
    }

    if (body.last_successful_collection !== undefined) {
      updates.push(`last_successful_collection = $${paramIndex++}`);
      values.push(body.last_successful_collection);
    }

    if (updates.length === 0) {
      return reply.status(400).send({ error: 'No updates provided', code: 'no_updates' });
    }

    values.push(id);

    try {
      await db.connect();
      const result = await db.query(
        `UPDATE nexus.knowledge_sources
         SET ${updates.join(', ')}, updated_at = NOW()
         WHERE id = $${paramIndex}
         RETURNING id, source_name, status, trust_level, collection_frequency, updated_at`,
        values
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Source not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Knowledge Sources] Failed to update source:', error);
      return reply.status(500).send({ error: 'Failed to update source', code: 'internal_error' });
    }
  });

  console.log('[API] Knowledge source registry routes registered');
}
