/**
 * NexusAI Model Adapter Interface
 *
 * Abstract interface for model adapters
 * All model adapters must implement this interface
 */

import {
  ModelAdapter,
  ModelLoadConfig,
  AIRequest,
  AIResponse,
  ModelMetadata,
} from '../core/types';

/**
 * Base Model Adapter (Abstract)
 *
 * All concrete model adapters should extend this class
 */
export abstract class BaseModelAdapter implements ModelAdapter {
  protected loaded: boolean = false;
  protected metadata: ModelMetadata;

  constructor(metadata: ModelMetadata) {
    this.metadata = metadata;
  }

  /**
   * Get adapter ID
   */
  get id(): string {
    return `${this.metadata.id}-adapter`;
  }

  /**
   * Get supported model ID
   */
  get modelId(): string {
    return this.metadata.id;
  }

  /**
   * Get model metadata
   */
  getMetadata(): ModelMetadata {
    return this.metadata;
  }

  /**
   * Check if model is loaded
   */
  isLoaded(): boolean {
    return this.loaded;
  }

  /**
   * Load model (to be implemented by concrete adapter)
   */
  abstract load(config: ModelLoadConfig): Promise<void>;

  /**
   * Generate response (to be implemented by concrete adapter)
   */
  abstract generate(request: AIRequest): Promise<AIResponse>;

  /**
   * Unload model (to be implemented by concrete adapter)
   */
  abstract unload(): Promise<void>;
}

/**
 * Status: NOT IMPLEMENTED
 *
 * This is the base adapter interface.
 * Concrete adapters (e.g., ONNXAdapter, PyTorchAdapter) will extend this.
 *
 * Next Step: Implement ONNXAdapter for local ONNX models
 */
