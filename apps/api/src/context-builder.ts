/**
 * NexusAI Context Builder
 *
 * Loads conversation history and builds context for AI inference
 * Ensures conversation continuity and context awareness
 */

import { ConversationRepository, MessageRepository } from '@nexusai/repositories';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';

export interface ConversationContext {
  conversationId: string;
  accountId: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  maxHistory: number;
}

export interface ContextBuilderConfig {
  maxHistoryLength?: number;
  maxTokenLimit?: number;
}

/**
 * Context Builder Implementation
 *
 * Loads conversation history from database and builds context for AI
 */
export class NexusAIContextBuilder {
  private conversationRepo: ConversationRepository;
  private messageRepo: MessageRepository;
  private db: ReturnType<typeof createDatabaseClient>;
  private dbConnectPromise: Promise<void> | null = null;
  private config: Required<ContextBuilderConfig>;

  constructor(config?: ContextBuilderConfig) {
    // Initialize database connection
    const dbConfig = readDatabaseConfig();
    const db = createDatabaseClient(dbConfig);
    this.db = db;

    this.conversationRepo = new ConversationRepository(db);
    this.messageRepo = new MessageRepository(db);
    
    this.config = {
      maxHistoryLength: config?.maxHistoryLength || 10,
      maxTokenLimit: config?.maxTokenLimit || 2000,
    };
  }

  /**
   * Build context for a given conversation
   */
  private async ensureDbConnected(): Promise<void> {
    if (!this.dbConnectPromise) {
      this.dbConnectPromise = this.db.connect().catch((err) => {
        this.dbConnectPromise = null;
        throw err;
      });
    }
    await this.dbConnectPromise;
  }

  async buildContext(conversationId: string, accountId: string): Promise<ConversationContext> {
    await this.ensureDbConnected();
    // Verify conversation ownership
    const conversation = await this.conversationRepo.findById(accountId, conversationId);
    
    if (!conversation) {
      // If conversation doesn't exist, return empty context
      // This can happen for new conversations or guest mode
      return {
        conversationId,
        accountId,
        messages: [],
        maxHistory: this.config.maxHistoryLength,
      };
    }

    // Load conversation messages
    const messages = await this.messageRepo.listByConversationId(conversationId);
    
    // Convert to context format
    const contextMessages = messages.map(msg => ({
      role: msg.senderRole,
      content: msg.content,
      timestamp: msg.createdAt,
    }));

    // Apply context limits
    const limitedMessages = this.applyContextLimits(contextMessages);

    return {
      conversationId,
      accountId,
      messages: limitedMessages,
      maxHistory: this.config.maxHistoryLength,
    };
  }

  /**
   * Apply context limits (history length and token limit)
   */
  private applyContextLimits(messages: Array<{ role: 'user' | 'assistant'; content: string; timestamp: string }>): Array<{ role: 'user' | 'assistant'; content: string; timestamp: string }> {
    // Take last N messages (most recent)
    const limitedByHistory = messages.slice(-this.config.maxHistoryLength);

    // Estimate token count (rough estimate: ~4 characters per token)
    let totalTokens = 0;
    const limitedByTokens: Array<{ role: 'user' | 'assistant'; content: string; timestamp: string }> = [];

    // Add messages from most recent to oldest until token limit
    for (let i = limitedByHistory.length - 1; i >= 0; i--) {
      const msg = limitedByHistory[i];
      if (!msg) continue;
      
      const msgTokens = Math.ceil(msg.content.length / 4);
      
      if (totalTokens + msgTokens > this.config.maxTokenLimit) {
        break;
      }
      
      totalTokens += msgTokens;
      limitedByTokens.unshift(msg);
    }

    return limitedByTokens;
  }

  /**
   * Build context for guest mode (in-memory only)
   */
  buildGuestContext(conversationId: string, messages: Array<{ role: 'user' | 'assistant'; content: string }>): ConversationContext {
    const limitedMessages = this.applyContextLimits(
      messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: new Date().toISOString(),
      }))
    );

    return {
      conversationId,
      accountId: 'guest',
      messages: limitedMessages,
      maxHistory: this.config.maxHistoryLength,
    };
  }
}

/**
 * Singleton instance
 */
export const contextBuilder = new NexusAIContextBuilder();
