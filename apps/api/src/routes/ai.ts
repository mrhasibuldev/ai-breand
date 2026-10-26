/**
 * AI Orchestration Routes
 *
 * Handles AI inference requests by calling the Python ML service
 * Requires authentication for user conversations, allows guest mode
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { authMiddleware, optionalAuthMiddleware } from '../middleware/auth.js';

interface ChatRequest {
  message: string;
  conversationId?: string;
  context?: any[];
}

interface ChatResponse {
  response: string;
  conversationId?: string;
  messageId?: string;
}

export async function aiRoutes(app: FastifyInstance) {
  /**
   * POST /api/v1/ai/chat
   * Send a message to the AI and get a response
   * Uses optional auth - works for both guest and authenticated users
   */
  app.post('/api/v1/ai/chat', { preHandler: optionalAuthMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId;
    const body = request.body as ChatRequest;
    const { message, conversationId, context } = body;

    if (!message) {
      return reply.status(400).send({ error: 'Message is required' });
    }

    try {
      // Call Python AI service
      const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';
      
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch(`${aiServiceUrl}/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          context: context || [],
          user_id: accountId, // Pass account ID if authenticated
        }),
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[AI] Service error:', response.status, errorText);
        return reply.status(502).send({ error: 'AI service unavailable' });
      }

      const aiResponse = await response.json();

      return reply.send({
        response: aiResponse.response || aiResponse.message || aiResponse.text || 'No response from AI',
        conversationId: aiResponse.conversation_id || conversationId,
        messageId: aiResponse.message_id,
      });
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('[AI] Request timeout');
        return reply.status(504).send({ error: 'AI service timeout' });
      }
      console.error('[AI] Request error:', error);
      return reply.status(502).send({ error: 'AI service unavailable' });
    }
  });

  /**
   * GET /api/v1/ai/health
   * Check if AI service is available
   */
  app.get('/api/v1/ai/health', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';
      const response = await fetch(`${aiServiceUrl}/health`, {
        method: 'GET',
      });

      const isHealthy = response.ok;
      return reply.send({
        status: isHealthy ? 'healthy' : 'unhealthy',
        service: aiServiceUrl,
      });
    } catch (error) {
      console.error('[AI] Health check error:', error);
      return reply.status(503).send({
        status: 'unhealthy',
        error: 'AI service unreachable',
      });
    }
  });
}
