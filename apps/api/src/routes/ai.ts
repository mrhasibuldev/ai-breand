/**
 * AI Orchestration Routes
 *
 * Handles AI inference requests using the IntelligenceEngine
 * Requires authentication for user conversations, allows guest mode
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { authMiddleware, optionalAuthMiddleware } from '../middleware/auth.js';
import { intelligenceEngine } from '../intelligence-engine.js';

// Define SafetyMode locally for Phase 1
type SafetyMode = 'NORMAL' | 'WELLNESS_REDIRECT' | 'SAFETY_ESCALATION' | 'BLOCKED';

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
   * Routes through IntelligenceEngine for full orchestration
   */
  app.post('/api/v1/ai/chat', { preHandler: optionalAuthMiddleware }, async (request: FastifyRequest, reply: FastifyReply) => {
    const accountId = request.accountId || 'guest';
    const body = request.body as ChatRequest;
    const { message, conversationId, context } = body;

    if (!message) {
      return reply.status(400).send({ error: 'Message is required' });
    }

    try {
      // Build context for IntelligenceEngine
      const requestContext = [
        {
          message,
          conversation_id: conversationId || crypto.randomUUID(),
          user_id: accountId,
          history: context || [], // Pass conversation history for context awareness
          ...(context || {}),
        },
      ];

      // Determine safety mode (NORMAL for guest, configurable for authenticated)
      const safetyMode: SafetyMode = accountId !== 'guest' ? 'NORMAL' : 'NORMAL';

      // Create ModelRequest for IntelligenceEngine
      const modelRequest = {
        operation: 'chat' as const,
        accountId,
        safetyMode,
        context: requestContext,
      };

      // Call IntelligenceEngine
      const startTime = Date.now();
      const response = await intelligenceEngine.respond(modelRequest);
      const latencyMs = Date.now() - startTime;

      console.log(`[AI] Response generated in ${latencyMs}ms via IntelligenceEngine`);

      return reply.send({
        response: response.text,
        conversationId: conversationId || requestContext[0]?.conversation_id || crypto.randomUUID(),
        messageId: crypto.randomUUID(),
        latencyMs,
        provider: response.providerAlias,
        contextInfo: response.contextInfo,
      });
    } catch (error) {
      console.error('[AI] IntelligenceEngine error:', error);
      
      if (error instanceof Error) {
        // Handle specific error types
        if (error.message.includes('unavailable') || error.message.includes('timeout')) {
          return reply.status(503).send({ error: 'AI service unavailable' });
        }
        if (error.message.includes('empty')) {
          return reply.status(502).send({ error: 'AI generated empty response' });
        }
      }
      
      return reply.status(500).send({ error: 'AI processing failed' });
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
