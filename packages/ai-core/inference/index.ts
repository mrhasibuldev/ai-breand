/**
 * NexusAI Inference Runtime
 *
 * Base class for inference runtimes (CPU, GPU, Hybrid)
 */

import {
  InferenceRuntime,
  RuntimeConfig,
  RuntimeStatus,
  RuntimeType,
  AIRequest,
  AIResponse,
  ModelLoadConfig,
} from '../core/types';

/**
 * Base Inference Runtime (Abstract)
 */
export abstract class BaseInferenceRuntime implements InferenceRuntime {
  protected initialized: boolean = false;
  protected loadedModels: Set<string> = new Set();
  protected config: RuntimeConfig;
  protected runtimeId: string;
  protected runtimeType: RuntimeType;

  constructor(runtimeId: string, runtimeType: RuntimeType) {
    this.runtimeId = runtimeId;
    this.runtimeType = runtimeType;
    this.config = {
      device: 'cpu',
      numThreads: 4,
      batchSize: 1,
    };
  }

  /**
   * Get runtime ID
   */
  get id(): string {
    return this.runtimeId;
  }

  /**
   * Get runtime type
   */
  get type(): RuntimeType {
    return this.runtimeType;
  }

  /**
   * Initialize runtime (to be implemented)
   */
  abstract initialize(config: RuntimeConfig): Promise<void>;

  /**
   * Load model (to be implemented)
   */
  abstract loadModel(modelId: string, config: ModelLoadConfig): Promise<void>;

  /**
   * Unload model (to be implemented)
   */
  abstract unloadModel(modelId: string): Promise<void>;

  /**
   * Execute inference (to be implemented)
   */
  abstract execute(request: AIRequest): Promise<AIResponse>;

  /**
   * Get runtime status
   */
  getStatus(): RuntimeStatus {
    return {
      initialized: this.initialized,
      loadedModels: Array.from(this.loadedModels),
      availableMemoryGB: this.config.maxMemoryGB || 8,
      usedMemoryGB: this.estimateUsedMemory(),
      device: this.config.device || 'cpu',
    };
  }

  /**
   * Shutdown runtime (to be implemented)
   */
  abstract shutdown(): Promise<void>;

  /**
   * Estimate used memory (heuristic)
   */
  protected estimateUsedMemory(): number {
    // Simple heuristic: 2GB per loaded model
    return this.loadedModels.size * 2;
  }
}

/**
 * Status: NOT IMPLEMENTED
 *
 * Concrete runtimes (CPUInferenceRuntime, GPUInferenceRuntime) will extend this.
 * Next Step: Implement CPUInferenceRuntime for CPU-only inference
 */
