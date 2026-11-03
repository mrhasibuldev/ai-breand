/**
 * Knowledge Retrieval API Routes
 * Search and retrieve knowledge from database
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';

export function knowledgeRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);

  // GET /api/v1/knowledge/search - Search knowledge
  app.get('/api/v1/knowledge/search', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const query = (request.query as any).q as string;
    const limit = parseInt((request.query as any).limit as string) || 10;

    if (!query || query.trim().length === 0) {
      return reply.status(400).send({ error: 'Query parameter "q" is required', code: 'invalid_query' });
    }

    try {
      await db.connect();
      // Search document chunks by keyword
      const result = await db.query(
        `SELECT
           dc.id as chunk_id,
           dc.document_id,
           dc.chunk_index,
           dc.content,
           dc.section_title,
           d.title as document_title,
           d.language,
           d.trust_level,
           d.created_at as document_created_at
         FROM nexus.document_chunks dc
         JOIN nexus.documents d ON dc.document_id = d.id
         WHERE d.status = 'active'
           AND dc.content ILIKE $1
         ORDER BY dc.chunk_index
         LIMIT $2`,
        [`%${query}%`, limit]
      );

      return {
        query,
        results: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Knowledge] Failed to search:', error);
      return reply.status(500).send({ error: 'Failed to search knowledge', code: 'internal_error' });
    }
  });

  // GET /api/v1/knowledge/documents - List documents
  app.get('/api/v1/knowledge/documents', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const limit = parseInt((request.query as any).limit as string) || 50;
    const offset = parseInt((request.query as any).offset as string) || 0;

    try {
      await db.connect();
      const result = await db.query(
        `SELECT
           d.id,
           d.source_id,
           d.content_hash,
           d.title,
           d.language,
           d.trust_level,
           d.quality_score,
           d.information_lifetime,
           d.word_count,
           d.char_count,
           d.status,
           d.created_at,
           d.updated_at,
           COUNT(dc.id) as chunk_count
         FROM nexus.documents d
         LEFT JOIN nexus.document_chunks dc ON d.id = dc.document_id
         WHERE d.status = 'active'
         GROUP BY d.id
         ORDER BY d.created_at DESC
         LIMIT $1 OFFSET $2`,
        [limit, offset]
      );

      return {
        documents: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Knowledge] Failed to retrieve documents:', error);
      return reply.status(500).send({ error: 'Failed to retrieve documents', code: 'internal_error' });
    }
  });

  // GET /api/v1/knowledge/documents/:id - Get specific document
  app.get('/api/v1/knowledge/documents/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      await db.connect();
      const result = await db.query(
        `SELECT
           d.id,
           d.source_id,
           d.content_hash,
           d.title,
           d.content,
           d.language,
           d.trust_level,
           d.quality_score,
           d.information_lifetime,
           d.word_count,
           d.char_count,
           d.author,
           d.publish_date,
           d.status,
           d.created_at,
           d.updated_at
         FROM nexus.documents d
         WHERE d.id = $1 AND d.status = 'active'`,
        [id]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Document not found', code: 'not_found' });
      }

      // Get chunks for this document
      const chunksResult = await db.query(
        `SELECT
           id,
           chunk_index,
           content,
           content_hash,
           token_count,
           char_count,
           section_title,
           section_hierarchy,
           position_in_document
         FROM nexus.document_chunks
         WHERE document_id = $1
         ORDER BY chunk_index`,
        [id]
      );

      return {
        document: result.rows[0],
        chunks: chunksResult.rows,
        chunk_count: chunksResult.rows.length
      };
    } catch (error) {
      console.error('[Knowledge] Failed to retrieve document:', error);
      return reply.status(500).send({ error: 'Failed to retrieve document', code: 'internal_error' });
    }
  });

  // GET /api/v1/knowledge/sources - List knowledge sources
  app.get('/api/v1/knowledge/sources', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    try {
      await db.connect();
      const result = await db.query(
        `SELECT
           id,
           source_type,
           source_url,
           source_name,
           license,
           copyright_notice,
           status,
           created_at,
           updated_at
         FROM nexus.knowledge_sources
         WHERE status = 'active'
         ORDER BY created_at DESC`
      );

      return {
        sources: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Knowledge] Failed to retrieve sources:', error);
      return reply.status(500).send({ error: 'Failed to retrieve sources', code: 'internal_error' });
    }
  });

  // GET /api/v1/knowledge/context - Get context for AI inference
  app.get('/api/v1/knowledge/context', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const query = (request.query as any).q as string;
    const topK = parseInt((request.query as any).top_k as string) || 3;

    if (!query || query.trim().length === 0) {
      return reply.status(400).send({ error: 'Query parameter "q" is required', code: 'invalid_query' });
    }

    try {
      await db.connect();
      // Search for relevant chunks
      const result = await db.query(
        `SELECT
           dc.content,
           d.title as document_title,
           d.trust_level
         FROM nexus.document_chunks dc
         JOIN nexus.documents d ON dc.document_id = d.id
         WHERE d.status = 'active'
           AND d.trust_level IN ('TIER_1', 'TIER_2')
           AND dc.content ILIKE $1
         ORDER BY dc.chunk_index
         LIMIT $2`,
        [`%${query}%`, topK]
      );

      // Format context
      const contextParts = result.rows.map((row: any, index: number) => {
        return `[${index + 1}] ${row.document_title || 'Unknown'} (Trust: ${row.trust_level}):\n${row.content}`;
      });

      return {
        query,
        context: contextParts.join('\n\n'),
        source_count: result.rows.length
      };
    } catch (error) {
      console.error('[Knowledge] Failed to retrieve context:', error);
      return reply.status(500).send({ error: 'Failed to retrieve context', code: 'internal_error' });
    }
  });
}
