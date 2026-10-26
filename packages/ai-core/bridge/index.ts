/**
 * Brain Bridge Module
 *
 * Exports for TypeScript → Python ML service communication
 */

export { BrainServiceClient, brainServiceClient } from './client.js';
export type {
  InferenceRequest,
  InferenceResponse,
  ModelStatus,
  HealthResponse,
  OrchestratorRequest,
  OrchestratorResponse,
} from './types.js';
export {
  BRAIN_SERVICE_CONFIG,
  ENDPOINTS,
} from './config.js';
export {
  BrainServiceError,
  ServiceUnavailableError,
  ModelNotLoadedError,
  InferenceError,
  TimeoutError,
  ValidationError,
} from './errors.js';
