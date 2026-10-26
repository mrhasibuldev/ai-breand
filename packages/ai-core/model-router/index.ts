/**
 * NexusAI Model Router
 *
 * Routes AI requests to appropriate models based on operation type and capabilities
 */

import {
  ModelRouter,
  ModelRoutingDecision,
  ModelMetadata,
  AIRequest,
  AIOperation,
  ModelCapability,
} from '../core/types.js';
import { modelRegistry } from '../model-registry/index.js';

/**
 * Model Router Implementation
 */
export class NexusModelRouter implements ModelRouter {
  /**
   * Route request to appropriate model
   */
  async route(request: AIRequest): Promise<ModelRoutingDecision> {
    const availableModels = modelRegistry.getAvailableModels();

    if (availableModels.length === 0) {
      throw new Error('No models available');
    }

    // Simple routing logic based on operation type
    // This will be enhanced with more sophisticated routing
    const selectedModel = this.selectModelForOperation(request.operation, availableModels);

    return {
      modelId: selectedModel.id,
      reason: `Selected based on operation type: ${request.operation}`,
      confidence: 0.9,
      fallbackModels: availableModels.slice(0, 2).map((m: ModelMetadata) => m.id),
    };
  }

  /**
   * Select model for operation
   */
  private selectModelForOperation(operation: AIOperation, models: ModelMetadata[]): ModelMetadata {
    // Simple heuristic: pick first model that supports the operation
    // In a real implementation, this would be more sophisticated
    for (const model of models) {
      if (this.modelSupportsOperation(model, operation)) {
        return model;
      }
    }

    // Fallback to first model
    if (models.length === 0) {
      throw new Error('No models available for routing');
    }
    return models[0]!;
  }

  /**
   * Check if model supports operation
   */
  private modelSupportsOperation(model: ModelMetadata, operation: AIOperation): boolean {
    const capabilityMap: Record<AIOperation, ModelCapability> = {
      chat: 'text-generation',
      plan: 'reasoning',
      reason: 'reasoning',
      classify: 'classification',
      embed: 'embedding',
      vision: 'vision',
      'image-generate': 'image-generation',
      'tool-call': 'tool-calling',
    };

    const requiredCapability = capabilityMap[operation];
    return model.capabilities.includes(requiredCapability);
  }

  /**
   * Get all available models
   */
  getAvailableModels(): ModelMetadata[] {
    return modelRegistry.getAvailableModels();
  }

  /**
   * Register model
   */
  registerModel(metadata: ModelMetadata): void {
    modelRegistry.registerVersion(metadata);
  }

  /**
   * Unregister model
   */
  unregisterModel(modelId: string): void {
    modelRegistry.unregisterModel(modelId);
  }
}

/**
 * Singleton instance
 */
export const modelRouter = new NexusModelRouter();
