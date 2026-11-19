/**
 * NexusAI Intelligence Engine - Standalone Implementation
 *
 * Simplified IntelligenceEngine for Phase 1-3 integration
 * This module provides the runtime IntelligenceEngine contract
 * without depending on complex experimental code
 */

import { contextBuilder, type ConversationContext } from './context-builder.js';
import { memoryService, type MemoryContext } from './memory-service.js';

// Define types locally for Phase 1-2
export type SafetyMode = 'NORMAL' | 'WELLNESS_REDIRECT' | 'SAFETY_ESCALATION' | 'BLOCKED';

export type ModelRequest = {
  readonly operation: 'chat' | 'plan' | 'safety' | 'memory_candidate';
  readonly accountId: string;
  readonly safetyMode: SafetyMode;
  readonly context: readonly unknown[];
};

export type ModelResponse = {
  readonly text: string;
  readonly safetyMode: SafetyMode;
  readonly providerAlias: string;
  readonly responseSource?: string | null;
  readonly rejectionReason?: string | null;
  readonly intent?: string | null;
  readonly modelUsed?: string | null;
  readonly neuralRan?: boolean | null;
  readonly contextInfo?: {
    conversationId: string;
    messageCount: number;
    tokenCount: number;
    memoryCount: number;
  };
};

export interface IntelligenceEngine {
  respond(request: ModelRequest): Promise<ModelResponse>;
}

/**
 * Intelligence Engine Implementation
 *
 * For Phase 2, this loads conversation context before calling Python ML service
 * In later phases, this will use the full BrainOrchestrator
 */
export class NexusAIIntelligenceEngine implements IntelligenceEngine {
  async respond(request: ModelRequest): Promise<ModelResponse> {
    // Extract message and conversation ID from context
    const message = this.extractMessage(request);
    const conversationId = this.extractConversationId(request);
    const accountId = request.accountId;

    // Build conversation context (Phase 2)
    let conversationContext: ConversationContext;
    
    if (accountId === 'guest') {
      // For guest mode, use in-memory context from request
      const historyMessages = this.extractHistoryFromContext(request.context);
      conversationContext = contextBuilder.buildGuestContext(conversationId, historyMessages);
    } else {
      // For authenticated users, load from database
      try {
        conversationContext = await contextBuilder.buildContext(conversationId, accountId);
      } catch (error) {
        console.error('[IntelligenceEngine] Failed to load context:', error);
        // Fallback to empty context
        conversationContext = {
          conversationId,
          accountId,
          messages: [],
          maxHistory: 10,
        };
      }
    }

    // Retrieve memory for context (Phase 3)
    let memoryContext: MemoryContext;
    try {
      memoryContext = await memoryService.retrieveMemories(accountId);
    } catch (error) {
      console.error('[IntelligenceEngine] Failed to load memory:', error);
      // Fallback to empty memory
      memoryContext = {
        accountId,
        memories: [],
      };
    }

    // Call Python ML service with conversation history and memory
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';

    try {
      const controller = new AbortController();
      // Configurable timeout: cold neural loads can exceed 10s on low-RAM
      // hosts. AI_SERVICE_TIMEOUT_MS overrides; default unchanged.
      const timeoutMs = Number(process.env.AI_SERVICE_TIMEOUT_MS) || 10000;
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      const requestBody = JSON.stringify({
        message,
        conversation_id: conversationId,
        context: request.context,
        history: conversationContext.messages, // Add conversation history
        memory: memoryContext.memories, // Add memory (Phase 3)
        user_id: accountId,
      });

      const response = await fetch(`${aiServiceUrl}/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        signal: controller.signal,
        body: requestBody,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`AI service error: ${response.status}`);
      }

      const data = await response.json();
      const mlTrace = Array.isArray(data?.diagnostics) && data.diagnostics.length > 0
        ? data.diagnostics[0]
        : undefined;

      // Neural-only contract: an empty response or explicit error source
      // must surface as an error — never as a fake conversational answer.
      const src = data.response_source || '';
      const neuralFailSources = ['MODEL_GENERATION_FAILED','MODEL_UNAVAILABLE',
        'MODEL_LOAD_FAILED','INVALID_MODEL_OUTPUT','GENERATION_TIMEOUT',
        'SAFETY_BLOCKED'];
      if (!data.response || neuralFailSources.includes(src)) {
        const code = data.rejection_reason || src || 'MODEL_GENERATION_FAILED';
        throw new Error(`NEURAL_${code}`);
      }

      return {
        text: data.response || data.message || data.text || 'No response from AI',
        safetyMode: request.safetyMode,
        providerAlias: 'nexusai-python-ml',
        responseSource: data.response_source ?? null,
        rejectionReason: data.rejection_reason ?? null,
        intent: mlTrace?.intent ?? null,
        modelUsed: mlTrace?.model_used ?? null,
        neuralRan: mlTrace?.neural_ran ?? null,
        contextInfo: {
          conversationId,
          messageCount: conversationContext.messages.length,
          tokenCount: this.estimateTokens(conversationContext.messages),
          memoryCount: memoryContext.memories.length,
        },
      };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('AI service timeout');
      }
      // Preserve explicit neural-failure codes — do not mask them as generic outages.
      if (error instanceof Error && error.message.startsWith('NEURAL_')) {
        throw error;
      }
      throw new Error(`AI service unavailable: ${error}`);
    }
  }

  private extractMessage(request: ModelRequest): string {
    for (const item of request.context) {
      if (typeof item === 'object' && item !== null && 'message' in item) {
        return String((item as any).message);
      }
    }
    throw new Error('No message found in request context');
  }

  private extractConversationId(request: ModelRequest): string {
    for (const item of request.context) {
      if (typeof item === 'object' && item !== null && 'conversation_id' in item) {
        return String((item as any).conversation_id);
      }
    }
    return crypto.randomUUID();
  }

  private extractHistoryFromContext(context: readonly unknown[]): Array<{ role: 'user' | 'assistant'; content: string }> {
    // Extract history from context for guest mode
    const history: Array<{ role: 'user' | 'assistant'; content: string }> = [];
    
    for (const item of context) {
      if (typeof item === 'object' && item !== null && 'history' in item) {
        const historyData = (item as any).history;
        if (Array.isArray(historyData)) {
          for (const msg of historyData) {
            if (typeof msg === 'object' && msg !== null && 'role' in msg && 'content' in msg) {
              history.push({
                role: msg.role,
                content: msg.content,
              });
            }
          }
        }
      }
    }
    
    return history;
  }

  private estimateTokens(messages: Array<{ role: 'user' | 'assistant'; content: string }>): number {
    // Rough estimate: ~4 characters per token
    const totalChars = messages.reduce((sum, msg) => sum + msg.content.length, 0);
    return Math.ceil(totalChars / 4);
  }
}

/**
 * Singleton instance
 */
export const intelligenceEngine = new NexusAIIntelligenceEngine();
