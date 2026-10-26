/**
 * API Routes - Conversations
 *
 * Conversation management endpoints using database repository
 * Requires authentication via HTTP-only session cookie
 */

import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { ConversationRepository, MessageRepository } from '@nexusai/repositories';
import { authMiddleware } from '../middleware/auth.js';
import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';

export async function conversationRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);
  await db.connect();

  const conversationRepo = new ConversationRepository(db);
  const messageRepo = new MessageRepository(db);

  // GET /api/v1/conversations - List user's conversations
  app.get('/api/v1/conversations', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const conversations = await conversationRepo.listByAccountId(accountId);
    return reply.send(conversations);
  });

  // GET /api/v1/conversations/:id - Get specific conversation with messages
  app.get('/api/v1/conversations/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;
    const { id } = request.params as { id: string };

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const conversation = await conversationRepo.findById(accountId, id);

    if (!conversation) {
      return reply.status(404).send({ error: 'Conversation not found' });
    }

    const messages = await messageRepo.listByConversationId(id);

    return reply.send({
      conversation,
      messages,
    });
  });

  // POST /api/v1/conversations - Create new conversation
  app.post('/api/v1/conversations', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const body = request.body as any;
    const conversation = await conversationRepo.create({
      accountId,
      title: body.title,
    });

    return reply.status(201).send(conversation);
  });

  // POST /api/v1/conversations/:id/messages - Add message to conversation
  app.post('/api/v1/conversations/:id/messages', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;
    const { id } = request.params as { id: string };

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    // Verify conversation ownership
    const conversation = await conversationRepo.findById(accountId, id);
    if (!conversation) {
      return reply.status(404).send({ error: 'Conversation not found' });
    }

    const body = request.body as any;
    const message = await messageRepo.create({
      conversationId: id,
      senderRole: body.senderRole,
      content: body.content,
    });

    return reply.status(201).send(message);
  });

  // DELETE /api/v1/conversations/:id - Delete conversation
  app.delete('/api/v1/conversations/:id', { preHandler: authMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;
    const { id } = request.params as { id: string };

    if (!accountId) {
      return reply.status(401).send({ error: 'Unauthorized' });
    }

    const deleted = await conversationRepo.delete(accountId, id);

    if (!deleted) {
      return reply.status(404).send({ error: 'Conversation not found' });
    }

    return reply.status(204).send();
  });
}
