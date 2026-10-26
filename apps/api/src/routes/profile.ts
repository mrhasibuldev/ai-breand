/**
 * API Routes - Profile
 *
 * Profile management endpoints using database repository
 * Requires authentication via HTTP-only session cookie
 */

import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { ProfileRepository } from '@nexusai/repositories';
import { authMiddleware } from '../middleware/auth.js';
import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';

export async function profileRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);
  await db.connect();

  const profileRepo = new ProfileRepository(db);

  // GET /api/v1/profile - Get current user's profile
  app.get('/api/v1/profile', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const profile = await profileRepo.findByAccountId(accountId);

    if (!profile) {
      return reply.status(404).send({ error: 'Profile not found' });
    }

    return reply.send(profile);
  });

  // POST /api/v1/profile - Create profile
  app.post('/api/v1/profile', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const body = request.body as any;
    const profile = await profileRepo.create({
      accountId,
      displayName: body.displayName,
      ageBand: body.ageBand,
      locale: body.locale,
      timezone: body.timezone,
    });

    return reply.status(201).send(profile);
  });

  // PUT /api/v1/profile - Update profile
  app.put('/api/v1/profile', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const body = request.body as any;
    const profile = await profileRepo.update(accountId, {
      displayName: body.displayName,
      ageBand: body.ageBand,
      locale: body.locale,
      timezone: body.timezone,
    });

    if (!profile) {
      return reply.status(404).send({ error: 'Profile not found' });
    }

    return reply.send(profile);
  });
}
