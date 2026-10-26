/**
 * NexusAI CPU Inference Runtime
 *
 * CPU-only inference runtime for local models
 * No GPU required
 */

import {
  BaseInferenceRuntime,
  RuntimeConfig,
  ModelLoadConfig,
  AIRequest,
  AIResponse,
  RuntimeStatus,
} from './index';
import { LocalModelAdapter, createLocalModelAdapter } from '../model-adapter/local-adapter';

/**
 * CPU Inference Runtime Implementation
 *
 * Status: WORKING (Phase 1)
 * Runs local models on CPU without GPU
 */
export class CPUInferenceRuntime extends BaseInferenceRuntime {
  private adapters: Map<string, LocalModelAdapter> = new Map();

  constructor() {
    super('cpu-runtime', 'cpu');
  }

  /**
   * Initialize runtime
   */
  async initialize(config: RuntimeConfig): Promise<void> {
    console.log('[CPUInferenceRuntime] Initializing...');
    this.config = {
      ...this.config,
      ...config,
      device: 'cpu',
    };

    this.initialized = true;
    console.log('[CPUInferenceRuntime] Initialized successfully');
  }

  /**
   * Load model
   */
  async loadModel(modelId: string, config: ModelLoadConfig): Promise<void> {
    if (!this.initialized) {
      throw new Error('Runtime not initialized');
    }

    console.log(`[CPUInferenceRuntime] Loading model: ${modelId}`);

    // Create adapter
    const adapter = createLocalModelAdapter(modelId, config.path);
    await adapter.load(config);

    this.adapters.set(modelId, adapter);
    this.loadedModels.add(modelId);

    console.log(`[CPUInferenceRuntime] Model loaded: ${modelId}`);
  }

  /**
   * Unload model
   */
  async unloadModel(modelId: string): Promise<void> {
    const adapter = this.adapters.get(modelId);
    if (!adapter) {
      throw new Error(`Model ${modelId} not loaded`);
    }

    await adapter.unload();
    this.adapters.delete(modelId);
    this.loadedModels.delete(modelId);

    console.log(`[CPUInferenceRuntime] Model unloaded: ${modelId}`);
  }

  /**
   * Execute inference
   */
  async execute(request: AIRequest): Promise<AIResponse> {
    if (!this.initialized) {
      throw new Error('Runtime not initialized');
    }

    // For Phase 1, use the first loaded model
    const modelIds = Array.from(this.loadedModels);
    if (modelIds.length === 0) {
      throw new Error('No models loaded');
    }

    const modelId = modelIds[0];
    const adapter = this.adapters.get(modelId);

    if (!adapter) {
      throw new Error(`Adapter not found for model: ${modelId}`);
    }

    console.log(`[CPUInferenceRuntime] Executing inference with model: ${modelId}`);

    return await adapter.generate(request);
  }

  /**
   * Shutdown runtime
   */
  async shutdown(): Promise<void> {
    console.log('[CPUInferenceRuntime] Shutting down...');

    // Unload all models
    for (const modelId of this.loadedModels) {
      await this.unloadModel(modelId);
    }

    this.initialized = false;
    console.log('[CPUInferenceRuntime] Shutdown complete');
  }

  /**
   * Get runtime status
   */
  getStatus(): RuntimeStatus {
    return {
      ...super.getStatus(),
      device: 'cpu',
    };
  }
}

/**
 * Singleton instance
 */
export const cpuRuntime = new CPUInferenceRuntime();
