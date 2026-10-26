/**
 * NexusAI Observability
 *
 * Logs AI execution events and provides metrics
 */

import {
  AIObservability,
  AIExecutionEvent,
  AIMetrics,
  MetricsFilter,
  LogFilter,
} from '../core/types';

/**
 * AI Observability Implementation
 */
export class NexusAIObservability implements AIObservability {
  private events: AIExecutionEvent[] = [];

  /**
   * Log AI execution
   */
  logExecution(event: AIExecutionEvent): void {
    this.events.push(event);
    // In production, this would be sent to a logging system
    console.log('[Observability]', event);
  }

  /**
   * Get metrics
   */
  async getMetrics(filter?: MetricsFilter): Promise<AIMetrics> {
    let filteredEvents = this.events;

    if (filter) {
      filteredEvents = this.events.filter((event) => {
        if (filter.modelId && event.modelId !== filter.modelId) return false;
        if (filter.operation && event.operation !== filter.operation) return false;
        if (filter.startTime && event.timestamp < filter.startTime) return false;
        if (filter.endTime && event.timestamp > filter.endTime) return false;
        return true;
      });
    }

    const totalRequests = filteredEvents.length;
    const totalTokens = filteredEvents.reduce((sum, e) => sum + e.inputTokens + e.outputTokens, 0);
    const averageLatency = totalRequests > 0
      ? filteredEvents.reduce((sum, e) => sum + e.latencyMs, 0) / totalRequests
      : 0;
    const successCount = filteredEvents.filter((e) => !e.error).length;
    const successRate = totalRequests > 0 ? successCount / totalRequests : 0;
    const errorRate = 1 - successRate;

    // Per-model metrics
    const byModel: Record<string, Partial<AIMetrics>> = {};
    for (const event of filteredEvents) {
      if (!byModel[event.modelId]) {
        byModel[event.modelId] = {
          totalRequests: 0,
          averageLatencyMs: 0,
          totalTokens: 0,
          successRate: 0,
          errorRate: 0,
        };
      }
      byModel[event.modelId].totalRequests = (byModel[event.modelId].totalRequests || 0) + 1;
    }

    return {
      totalRequests,
      averageLatencyMs,
      totalTokens,
      successRate,
      errorRate,
      byModel,
    };
  }

  /**
   * Get logs
   */
  async getLogs(filter?: LogFilter): Promise<AIExecutionEvent[]> {
    let filteredEvents = this.events;

    if (filter) {
      filteredEvents = this.events.filter((event) => {
        if (filter.modelId && event.modelId !== filter.modelId) return false;
        if (filter.operation && event.operation !== filter.operation) return false;
        if (filter.startTime && event.timestamp < filter.startTime) return false;
        if (filter.endTime && event.timestamp > filter.endTime) return false;
        if (filter.errorsOnly && !event.error) return false;
        return true;
      });

      if (filter.limit) {
        filteredEvents = filteredEvents.slice(-filter.limit);
      }
    }

    return filteredEvents;
  }

  /**
   * Clear all events
   */
  clear(): void {
    this.events = [];
  }
}

/**
 * Singleton instance
 */
export const aiObservability = new NexusAIObservability();
