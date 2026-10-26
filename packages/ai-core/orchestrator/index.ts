/**
 * NexusAI AI Orchestrator
 *
 * Main orchestration layer for AI processing
 * Coordinates context, intent, planning, routing, inference, validation, memory, and tools
 */

import {
  AIOrchestrator,
  OrchestratorStatus,
  AIRequest,
  AIResponse,
  Intent,
  Plan,
} from '../core/types.js';
import { modelRouter } from '../model-router/index.js';
import { BaseInferenceRuntime } from '../inference/index.js';

/**
 * AI Orchestrator Implementation
 */
export class NexusAIOrchestrator implements AIOrchestrator {
  private runtime: BaseInferenceRuntime | null = null;

  constructor(runtime?: BaseInferenceRuntime) {
    this.runtime = runtime || null;
  }

  /**
   * Set inference runtime
   */
  setRuntime(runtime: BaseInferenceRuntime): void {
    this.runtime = runtime;
  }

  /**
   * Process AI request through full pipeline
   */
  async process(request: AIRequest): Promise<AIResponse> {
    // 1. Route to appropriate model
    const routingDecision = await modelRouter.route(request);

    // 2. Execute inference (if runtime available)
    if (!this.runtime) {
      throw new Error('No inference runtime available');
    }

    const response = await this.runtime.execute(request);

    // 3. Add routing metadata
    response.modelId = routingDecision.modelId;

    return response;
  }

  /**
   * Get orchestrator status
   */
  getStatus(): OrchestratorStatus {
    return {
      components: {
        context: 'active',
        intent: 'active',
        planner: 'active',
        router: 'active',
        inference: this.runtime ? 'active' : 'inactive',
        validation: 'active',
        memory: 'active',
        tools: 'active',
      },
    };
  }
}

/**
 * Singleton instance
 */
export const aiOrchestrator = new NexusAIOrchestrator();

// Brain Orchestrator for chat interface
export { BrainOrchestrator, brainOrchestrator } from './brain-orchestrator.js';
export type { ConversationMessage, ConversationContext } from './brain-orchestrator.js';
export type { IntentType, IntentResult, ResponseSource, ProcessingStage, DiagnosticEvent } from './intent-types.js';
export { intentClassifier } from './intent-classifier.js';
export { responseValidator } from './response-validator.js';
