/**
 * NexusAI Context Manager
 *
 * Manages context building for AI requests
 */

import {
  ContextManager,
  ContextItem,
  AIRequest,
} from '../core/types';

/**
 * Context Manager Implementation
 */
export class NexusContextManager implements ContextManager {
  private contextItems: Map<string, ContextItem> = new Map();

  /**
   * Build context for request
   */
  async buildContext(request: AIRequest): Promise<ContextItem[]> {
    // Filter context based on consent and purpose
    const relevant: ContextItem[] = [];
    for (const item of this.contextItems.values()) {
      if (item.consented && item.sensitivity !== 'sensitive') {
        relevant.push(item);
      }
    }
    return relevant;
  }

  /**
   * Add context item
   */
  addContext(item: ContextItem): void {
    this.contextItems.set(item.id, item);
  }

  /**
   * Remove context item
   */
  removeContext(itemId: string): void {
    this.contextItems.delete(itemId);
  }

  /**
   * Clear context
   */
  clearContext(): void {
    this.contextItems.clear();
  }
}

/**
 * Singleton instance
 */
export const contextManager = new NexusContextManager();
