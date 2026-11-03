/**
 * Storage API Routes
 *
 * Backend-controlled storage operations for Neon Object Storage.
 * Provides authenticated upload, download, and deletion endpoints.
 */

import { FastifyInstance } from 'fastify';
import { createS3ProviderFromEnv, DatasetStorageService } from '@nexusai/storage-core';
import { authMiddleware } from '../middleware/auth.js';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import crypto from 'node:crypto';

// Maximum file sizes (in bytes)
const MAX_AVATAR_SIZE = 5 * 1024 * 1024; // 5MB
const MAX_DATASET_SIZE = 100 * 1024 * 1024; // 100MB

// Allowed file types
const ALLOWED_AVATAR_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const ALLOWED_DATASET_TYPES = ['application/json', 'application/jsonl', 'text/csv', 'application/parquet', 'text/plain'];

/**
 * Register storage routes
 */
export async function storageRoutes(fastify: FastifyInstance) {
  // Initialize storage service
  let storageService: DatasetStorageService | null = null;

  try {
    const s3Provider = createS3ProviderFromEnv();
    storageService = new DatasetStorageService(s3Provider);
    console.log('[API] Storage service initialized successfully');
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error('[API] Failed to initialize storage service:', errorMessage);
    // Routes will return 503 if storage service is not available
  }

  // Initialize database client for dataset registration
  let db: any = null;
  try {
    const config = readDatabaseConfig();
    db = createDatabaseClient(config);
    await db.connect();
    console.log('[API] Database client initialized for dataset registration');
  } catch (error) {
    console.error('[API] Failed to initialize database client:', error);
  }

  /**
   * Health check for storage service
   */
  fastify.get('/api/storage/health', async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }
    return { status: 'ok', provider: 'neon-s3' };
  });

  /**
   * Upload avatar
   * POST /api/storage/avatar
   * Requires authentication
   */
  fastify.post('/api/storage/avatar', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const userId = request.accountId;

    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    try {
      const data = await request.file();

      if (!data) {
        return reply.status(400).send({ error: 'No file uploaded' });
      }

      // Validate file type
      if (!ALLOWED_AVATAR_TYPES.includes(data.mimetype)) {
        return reply.status(400).send({ error: 'Invalid file type. Allowed: JPEG, PNG, WebP, GIF' });
      }

      // Validate file size
      const buffer = await data.toBuffer();
      if (buffer.length > MAX_AVATAR_SIZE) {
        return reply.status(400).send({ error: 'File size exceeds 5MB limit' });
      }

      // Extract file extension
      const fileName = data.filename || 'avatar';
      const fileExtension = fileName.split('.').pop() || 'jpg';

      // Validate file extension
      if (!DatasetStorageService.validateAvatarFileFormat(fileExtension)) {
        return reply.status(400).send({ error: 'Invalid file extension' });
      }

      // Upload to storage
      const timestamp = Date.now();
      const result = await storageService.uploadAvatar(userId, buffer, data.mimetype, fileExtension);

      return {
        success: true,
        key: result.key,
        url: result.url,
        metadata: {
          ...result.metadata,
          timestamp: timestamp.toString(),
          ext: fileExtension,
        },
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Avatar upload failed:', errorMessage);
      return reply.status(500).send({ error: 'Avatar upload failed' });
    }
  });

  /**
   * Get avatar
   * GET /api/storage/avatar/:userId/:timestamp
   * Requires authentication (private avatar access)
   */
  fastify.get('/api/storage/avatar/:userId/:timestamp', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const requestUserId = request.accountId;
    const { userId, timestamp } = request.params as { userId: string; timestamp: string };

    if (!requestUserId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    // Users can retrieve their own avatars
    if (requestUserId !== userId) {
      return reply.status(403).send({ error: 'Forbidden' });
    }

    try {
      // Determine file extension from query or default to jpg
      const ext = (request.query as { ext?: string }).ext || 'jpg';

      const buffer = await storageService.downloadAvatar(userId, parseInt(timestamp), ext);

      reply.type('image/jpeg');
      return reply.send(buffer);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Avatar download failed:', errorMessage);
      return reply.status(404).send({ error: 'Avatar not found' });
    }
  });

  /**
   * Delete avatar
   * DELETE /api/storage/avatar/:userId/:timestamp
   * Requires authentication
   */
  fastify.delete('/api/storage/avatar/:userId/:timestamp', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const requestUserId = request.accountId;
    const { userId, timestamp } = request.params as { userId: string; timestamp: string };

    if (!requestUserId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    // User can only delete their own avatars
    if (requestUserId !== userId) {
      return reply.status(403).send({ error: 'Forbidden' });
    }

    try {
      const ext = (request.query as { ext?: string }).ext || 'jpg';
      await storageService.deleteAvatar(userId, parseInt(timestamp), ext);

      return { success: true };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Avatar deletion failed:', errorMessage);
      return reply.status(500).send({ error: 'Avatar deletion failed' });
    }
  });

  /**
   * Upload dataset
   * POST /api/storage/dataset
   * Requires authentication
   */
  fastify.post('/api/storage/dataset', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const userId = request.accountId;

    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    try {
      const data = await request.file();

      if (!data) {
        return reply.status(400).send({ error: 'No file uploaded' });
      }

      // Get metadata from query parameters (simpler than multipart fields)
      const query = request.query as Record<string, string>;
      const datasetId = query.datasetId;
      const version = query.version;
      const fileFormat = query.fileFormat || 'json';
      const datasetType = query.datasetType;
      const language = query.language;
      const domain = query.domain;
      const taskType = query.taskType;

      if (!datasetId || !version) {
        return reply.status(400).send({ error: 'Missing required query parameters: datasetId, version' });
      }

      // Validate file format
      if (!DatasetStorageService.validateDatasetFileFormat(fileFormat)) {
        return reply.status(400).send({ error: 'Invalid file format. Allowed: json, jsonl, csv, parquet, txt' });
      }

      // Validate file type
      if (!ALLOWED_DATASET_TYPES.includes(data.mimetype)) {
        return reply.status(400).send({ error: 'Invalid file type' });
      }

      // Validate file size
      const buffer = await data.toBuffer();
      if (buffer.length > MAX_DATASET_SIZE) {
        return reply.status(400).send({ error: 'File size exceeds 100MB limit' });
      }

      // Upload to storage
      const result = await storageService.uploadDataset(buffer, data.mimetype, {
        userId,
        datasetId,
        version,
        fileFormat,
        metadata: {
          name: query.name || datasetId,
          description: query.description || '',
          datasetType: datasetType || 'unknown',
          language: language || 'en',
          domain: domain || 'general',
          taskType: taskType || 'conversation',
        },
      });

      // Calculate SHA-256 checksum
      const hash = crypto.createHash('sha256');
      hash.update(buffer);
      const sha256Checksum = hash.digest('hex');

      // Register dataset in database
      if (db) {
        try {
          await db.query(
            `INSERT INTO nexus.dataset_registry
             (account_id, dataset_name, description, category, storage_key, file_size_bytes, sha256_checksum, mime_type, version, source, provenance, license, privacy_status, validation_status, approval_status, training_eligible)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
             ON CONFLICT (account_id, dataset_name, version)
             DO UPDATE SET
               storage_key = nexus.dataset_registry.storage_key,
               file_size_bytes = nexus.dataset_registry.file_size_bytes,
               sha256_checksum = nexus.dataset_registry.sha256_checksum,
               updated_at = NOW()`,
            [
              userId,
              query.name || datasetId,
              query.description || '',
              datasetType || 'unknown',
              result.key,
              buffer.length,
              sha256Checksum,
              data.mimetype,
              version,
              'user_upload',
              'user_uploaded',
              'unknown',
              'private',
              'valid',
              'pending_review',
              false
            ]
          );
          console.log('[Storage] Dataset registered in database:', datasetId);
        } catch (dbError) {
          console.error('[Storage] Failed to register dataset in database:', dbError);
          // Continue even if database registration fails (storage succeeded)
        }
      }

      return {
        success: true,
        key: result.key,
        metadata: result.metadata,
        checksum: sha256Checksum,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Dataset upload failed:', errorMessage);
      return reply.status(500).send({ error: 'Dataset upload failed' });
    }
  });

  /**
   * Download dataset
   * GET /api/storage/dataset/:datasetId/:version
   */
  fastify.get('/api/storage/dataset/:datasetId/:version', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const { datasetId, version } = request.params as { datasetId: string; version: string };
    const fileFormat = (request.query as { format?: string }).format || 'json';

    try {
      const buffer = await storageService.downloadDataset(userId, datasetId, version, fileFormat);

      reply.type('application/json');
      return reply.send(buffer);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Dataset download failed:', errorMessage);
      return reply.status(404).send({ error: 'Dataset not found' });
    }
  });

  /**
   * Get dataset metadata
   * GET /api/storage/dataset/:datasetId/:version/metadata
   */
  fastify.get('/api/storage/dataset/:datasetId/:version/metadata', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const userId = request.accountId;
    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const { datasetId, version } = request.params as { datasetId: string; version: string };
    const fileFormat = (request.query as { format?: string }).format || 'json';

    try {
      const metadata = await storageService.getDatasetMetadata(userId, datasetId, version, fileFormat);
      return metadata;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Dataset metadata retrieval failed:', errorMessage);
      return reply.status(404).send({ error: 'Dataset not found' });
    }
  });

  /**
   * Delete dataset
   * DELETE /api/storage/dataset/:datasetId/:version
   * Requires authentication
   */
  fastify.delete('/api/storage/dataset/:datasetId/:version', { preHandler: authMiddleware }, async (request, reply) => {
    if (!storageService) {
      return reply.status(503).send({ error: 'Storage service not available' });
    }

    const userId = request.accountId;

    if (!userId) {
      return reply.status(401).send({ error: 'Authentication required' });
    }

    const { datasetId, version } = request.params as { datasetId: string; version: string };
    const fileFormat = (request.query as { format?: string }).format || 'json';

    try {
      await storageService.deleteDataset(userId, datasetId, version, fileFormat);
      return { success: true };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Dataset deletion failed:', errorMessage);
      return reply.status(500).send({ error: 'Dataset deletion failed' });
    }
  });
}
