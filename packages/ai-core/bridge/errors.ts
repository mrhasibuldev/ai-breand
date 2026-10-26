/**
 * Brain Bridge Errors
 */

export class BrainServiceError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: any
  ) {
    super(message);
    this.name = 'BrainServiceError';
  }
}

export class ServiceUnavailableError extends BrainServiceError {
  constructor(message?: string) {
    super(message || 'Brain service is unavailable', 'SERVICE_UNAVAILABLE');
  }
}

export class ModelNotLoadedError extends BrainServiceError {
  constructor(message?: string) {
    super(message || 'Model is not loaded', 'MODEL_NOT_LOADED');
  }
}

export class InferenceError extends BrainServiceError {
  constructor(message: string, details?: any) {
    super(message, 'INFERENCE_ERROR', details);
  }
}

export class TimeoutError extends BrainServiceError {
  constructor(message?: string) {
    super(message || 'Request timed out', 'TIMEOUT');
  }
}

export class ValidationError extends BrainServiceError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR');
  }
}
