/**
 * NexusAI Model Registry
 *
 * Central registry for all AI models
 * Manages model metadata, versions, and availability
 */

import {
  ModelMetadata,
  ModelStatus,
  ModelVersioning,
  HardwareRequirement,
} from '../core/types';

/**
 * Model Registry Implementation
 */
export class ModelRegistry implements ModelVersioning {
  private models: Map<string, ModelMetadata[]> = new Map();

  /**
   * Register a model version
   */
  registerVersion(metadata: ModelMetadata): void {
    const key = metadata.id;
    if (!this.models.has(key)) {
      this.models.set(key, []);
    }
    const versions = this.models.get(key)!;
    versions.push(metadata);
    // Sort by version (descending)
    versions.sort((a, b) => b.version.localeCompare(a.version));
  }

  /**
   * Get latest version of a model
   */
  getLatestVersion(modelId: string): ModelMetadata | undefined {
    const versions = this.models.get(modelId);
    if (!versions || versions.length === 0) {
      return undefined;
    }
    return versions[0]; // First is latest (sorted descending)
  }

  /**
   * Get specific version of a model
   */
  getVersion(modelId: string, version: string): ModelMetadata | undefined {
    const versions = this.models.get(modelId);
    if (!versions) {
      return undefined;
    }
    return versions.find((m) => m.version === version);
  }

  /**
   * List all versions of a model
   */
  listVersions(modelId: string): ModelMetadata[] {
    return this.models.get(modelId) || [];
  }

  /**
   * Get all available models (latest versions only)
   */
  getAvailableModels(): ModelMetadata[] {
    const available: ModelMetadata[] = [];
    for (const versions of this.models.values()) {
      if (versions.length > 0) {
        const latest = versions[0];
        if (latest.status === 'production' || latest.status === 'testing') {
          available.push(latest);
        }
      }
    }
    return available;
  }

  /**
   * Rollback to a specific version
   */
  rollback(modelId: string, version: string): void {
    const versions = this.models.get(modelId);
    if (!versions) {
      throw new Error(`Model ${modelId} not found`);
    }
    const target = versions.find((m) => m.version === version);
    if (!target) {
      throw new Error(`Version ${version} not found for model ${modelId}`);
    }
    // Update status to production
    target.status = 'production';
    // Mark other versions as deprecated
    versions.forEach((m) => {
      if (m.version !== version) {
        m.status = 'deprecated';
      }
    });
  }

  /**
   * Get all registered model IDs
   */
  getModelIds(): string[] {
    return Array.from(this.models.keys());
  }

  /**
   * Unregister a model
   */
  unregisterModel(modelId: string): void {
    this.models.delete(modelId);
  }

  /**
   * Clear all models
   */
  clear(): void {
    this.models.clear();
  }
}

/**
 * Singleton instance
 */
export const modelRegistry = new ModelRegistry();
