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
      const timeoutId = setTimeout(() => controller.abort(), 10000);

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
      
      return {
        text: data.response || data.message || data.text || 'No response from AI',
        safetyMode: request.safetyMode,
        providerAlias: 'nexusai-python-ml',
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
            if (typeof msg === 'object' && msg !== null && 'role' in item && 'content' in item) {
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
