/**
 * Knowledge Ingestion API Routes
 * Hybrid: Python processing + TypeScript persistence
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { authMiddleware } from '../middleware/auth.js';

const VALID_RUN_TYPES = ['file', 'url', 'batch', 'migration'];
const VALID_STATUSES = ['running', 'completed', 'failed'];

// Python ML service URL (default to localhost)
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://127.0.0.1:8000';

export function ingestionRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);

  // POST /api/v1/ingestion/start - Start ingestion job
  app.post('/api/v1/ingestion/start', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const body = request.body as {
      source?: string;
      run_type?: string;
      documents?: Array<{
        title?: string;
        content: string;
        language?: string;
        trust_level?: string;
        metadata?: any;
      }>;
    };

    if (!body.run_type || !VALID_RUN_TYPES.includes(body.run_type)) {
      return reply.status(400).send({ error: 'Invalid run_type', code: 'invalid_run_type' });
    }

    if (!body.documents || !Array.isArray(body.documents) || body.documents.length === 0) {
      return reply.status(400).send({ error: 'Documents array is required', code: 'invalid_documents' });
    }

    try {
      await db.connect();
      // Create ingestion run
      const runResult = await db.query(
        `INSERT INTO nexus.ingestion_runs
         (run_type, source, status)
         VALUES ($1, $2, 'running')
         RETURNING id`,
        [body.run_type, body.source || 'api']
      );

      const runId = (runResult.rows[0] as any).id;

      let documentsInserted = 0;
      let documentsSkipped = 0;
      let documentsFailed = 0;
      let chunksCreated = 0;

      // Process each document using Python service
      for (const doc of body.documents as any[]) {
        if (!doc.content || doc.content.trim().length === 0) {
          documentsFailed++;
          continue;
        }

        try {
          // Calculate content hash for duplicate detection
          const crypto = await import('crypto');
          const contentHash = crypto.createHash('sha256').update(doc.content).digest('hex');

          // Check for duplicate by content hash
          const existingDoc = await db.query(
            `SELECT id FROM nexus.documents WHERE content_hash = $1 AND status = 'active'`,
            [contentHash]
          );

          if (existingDoc.rows.length > 0) {
            documentsSkipped++;
            continue;
          }

          // Call Python service for processing
          const pythonResponse = await fetch(`${PYTHON_SERVICE_URL}/ingestion/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: doc.content,
              source: body.source || 'api_ingestion',
              source_type: 'user_uploaded',
              metadata: {
                title: doc.title,
                language: doc.language,
                trust_level: doc.trust_level,
                ...doc.metadata
              }
            })
          });

          if (!pythonResponse.ok) {
            console.error('[Ingestion] Python service returned error:', pythonResponse.status);
            documentsFailed++;
            continue;
          }

          const pythonResult = await pythonResponse.json();

          if (!pythonResult.success) {
            console.error('[Ingestion] Python processing failed:', pythonResult);
            documentsFailed++;
            continue;
          }

          // Create knowledge source if needed
          let sourceId: string;
          const sourceResult = await db.query(
            `INSERT INTO nexus.knowledge_sources
             (source_type, source_name, source_url, status)
             VALUES ($1, $2, $3, 'active')
             ON CONFLICT DO NOTHING
             RETURNING id`,
            ['user_uploaded', body.source || 'api_ingestion', null]
          );

          if (sourceResult.rows.length > 0 && (sourceResult.rows[0] as any).id) {
            sourceId = (sourceResult.rows[0] as any).id;
          } else {
            const existingSource = await db.query(
              `SELECT id FROM nexus.knowledge_sources WHERE source_name = $1 LIMIT 1`,
              [body.source || 'api_ingestion']
            );
            sourceId = (existingSource.rows[0] as any).id;
          }

          // Insert document using Python-processed data
          const cleanedDoc = pythonResult.cleaned_document;
          const docResult = await db.query(
            `INSERT INTO nexus.documents
             (source_id, content_hash, title, content, language, trust_level, quality_score, information_lifetime, status)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'active')
             RETURNING id`,
            [
              sourceId,
              contentHash,
              doc.title || cleanedDoc.text.substring(0, 100),
              cleanedDoc.text,
              cleanedDoc.language || doc.language || 'en',
              cleanedDoc.trust_level || doc.trust_level || 'TIER_2',
              cleanedDoc.quality_score || 0.8,
              'SLOW_CHANGING'
            ]
          );

          const documentId = (docResult.rows[0] as any).id;

          // Insert chunks using Python-processed chunks
          for (const chunk of pythonResult.chunks) {
            const chunkHash = crypto.createHash('sha256').update(chunk.text).digest('hex');

            await db.query(
              `INSERT INTO nexus.document_chunks
               (document_id, chunk_index, content, content_hash, char_count, position_in_document)
               VALUES ($1, $2, $3, $4, $5, $6)`,
              [
                documentId,
                chunk.chunk_index,
                chunk.text,
                chunkHash,
                chunk.text.length,
                chunk.position_in_document || 0
              ]
            );

            chunksCreated++;
          }

          documentsInserted++;
        } catch (error) {
          console.error('[Ingestion] Failed to process document:', error);
          documentsFailed++;
        }
      }

      // Update ingestion run
      await db.query(
        `UPDATE nexus.ingestion_runs
         SET documents_inserted = $1, documents_skipped = $2, documents_failed = $3, chunks_created = $4,
             completed_at = NOW(), status = 'completed'
         WHERE id = $5`,
        [documentsInserted, documentsSkipped, documentsFailed, chunksCreated, runId]
      );

      return reply.status(201).send({
        run_id: runId,
        status: 'completed',
        documents_inserted: documentsInserted,
        documents_skipped: documentsSkipped,
        documents_failed: documentsFailed,
        chunks_created: chunksCreated
      });
    } catch (error) {
      console.error('[Ingestion] Failed to start ingestion:', error);
      return reply.status(500).send({ error: 'Failed to start ingestion', code: 'internal_error' });
    }
  });

  // GET /api/v1/ingestion/jobs - List ingestion jobs
  app.get('/api/v1/ingestion/jobs', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const limit = parseInt((request.query as any).limit as string) || 50;

    try {
      await db.connect();
      const result = await db.query(
        `SELECT id, run_type, source, documents_inserted, documents_skipped, documents_updated,
                documents_failed, chunks_created, started_at, completed_at, status, error_message
         FROM nexus.ingestion_runs
         ORDER BY started_at DESC
         LIMIT $1`,
        [limit]
      );

      return {
        jobs: result.rows,
        count: result.rows.length
      };
    } catch (error) {
      console.error('[Ingestion] Failed to retrieve jobs:', error);
      return reply.status(500).send({ error: 'Failed to retrieve jobs', code: 'internal_error' });
    }
  });

  // GET /api/v1/ingestion/jobs/:id - Get specific ingestion job
  app.get('/api/v1/ingestion/jobs/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const principal = request.accountId;

    if (!principal) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
    }

    const { id } = request.params as { id: string };

    try {
      await db.connect();
      const result = await db.query(
        `SELECT id, run_type, source, documents_inserted, documents_skipped, documents_updated,
                documents_failed, chunks_created, started_at, completed_at, status, error_message, metadata
         FROM nexus.ingestion_runs
         WHERE id = $1`,
        [id]
      );

      if (result.rows.length === 0) {
        return reply.status(404).send({ error: 'Ingestion job not found', code: 'not_found' });
      }

      return result.rows[0];
    } catch (error) {
      console.error('[Ingestion] Failed to retrieve job:', error);
      return reply.status(500).send({ error: 'Failed to retrieve job', code: 'internal_error' });
    }
  });
}
