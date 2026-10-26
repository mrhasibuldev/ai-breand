/**
 * NexusAI Model Versioning
 *
 * Manages model versions and rollback capability
 */

import {
  ModelVersioning,
  ModelMetadata,
} from '../core/types';
import { modelRegistry } from '../model-registry';

/**
 * Model Versioning Implementation
 */
export class NexusModelVersioning implements ModelVersioning {
  /**
   * Register model version
   */
  registerVersion(metadata: ModelMetadata): void {
    modelRegistry.registerVersion(metadata);
  }

  /**
   * Get latest version
   */
  getLatestVersion(modelId: string): ModelMetadata | undefined {
    return modelRegistry.getLatestVersion(modelId);
  }

  /**
   * Get specific version
   */
  getVersion(modelId: string, version: string): ModelMetadata | undefined {
    return modelRegistry.getVersion(modelId, version);
  }

  /**
   * List all versions
   */
  listVersions(modelId: string): ModelMetadata[] {
    return modelRegistry.listVersions(modelId);
  }

  /**
   * Rollback to version
   */
  rollback(modelId: string, version: string): void {
    modelRegistry.rollback(modelId, version);
  }
}

/**
 * Singleton instance
 */
export const modelVersioning = new NexusModelVersioning();
