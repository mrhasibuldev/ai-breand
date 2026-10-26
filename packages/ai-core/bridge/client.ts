/**
 * Brain Bridge Client
 *
 * TypeScript client for communicating with Python ML service
 */

import {
  InferenceRequest,
  InferenceResponse,
  ModelStatus,
  HealthResponse,
  OrchestratorRequest,
  OrchestratorResponse,
} from './types.js';
import {
  BRAIN_SERVICE_CONFIG,
  ENDPOINTS,
} from './config.js';
import {
  BrainServiceError,
  ServiceUnavailableError,
  InferenceError,
  TimeoutError,
  ValidationError,
} from './errors.js';

/**
 * Brain Service Client
 */
export class BrainServiceClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config?: Partial<typeof BRAIN_SERVICE_CONFIG>) {
    this.baseUrl = config?.baseUrl || BRAIN_SERVICE_CONFIG.baseUrl;
    this.timeout = config?.timeout || BRAIN_SERVICE_CONFIG.timeout;
  }

  /**
   * Check service health
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${ENDPOINTS.health}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!response.ok) {
        throw new ServiceUnavailableError(`Health check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof BrainServiceError) throw error;
      throw new ServiceUnavailableError(`Health check failed: ${error}`);
    }
  }

  /**
   * Get model status
   */
  async getModelStatus(): Promise<ModelStatus> {
    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${ENDPOINTS.modelStatus}`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (!response.ok) {
        throw new Error(`Model status check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      throw new ServiceUnavailableError(`Model status check failed: ${error}`);
    }
  }

  /**
   * Run inference
   */
  async inference(request: InferenceRequest): Promise<InferenceResponse> {
    // Validate input
    this.validateInferenceRequest(request);

    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${ENDPOINTS.inference}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new InferenceError(
          errorData.detail || `Inference failed: ${response.status}`,
          errorData
        );
      }

      const data = await response.json();
      
      // Validate response
      if (!data.response || data.response.trim() === '') {
        throw new InferenceError('Model generated empty response');
      }

      return data;
    } catch (error) {
      if (error instanceof BrainServiceError) throw error;
      throw new InferenceError(`Inference failed: ${error}`);
    }
  }

  /**
   * Run orchestration (enhanced inference with language detection and intent classification)
   */
  async orchestrate(request: OrchestratorRequest): Promise<OrchestratorResponse> {
    // Validate input
    if (!request.message || typeof request.message !== 'string') {
      throw new ValidationError('Message is required and must be a string');
    }

    if (request.message.length < BRAIN_SERVICE_CONFIG.minMessageLength) {
      throw new ValidationError('Message cannot be empty');
    }

    if (request.message.length > BRAIN_SERVICE_CONFIG.maxMessageLength) {
      throw new ValidationError(
        `Message too long (max ${BRAIN_SERVICE_CONFIG.maxMessageLength} characters)`
      );
    }

    try {
      const response = await this.fetchWithTimeout(
        `${this.baseUrl}${ENDPOINTS.orchestrate}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new InferenceError(
          errorData.detail || `Orchestration failed: ${response.status}`,
          errorData
        );
      }

      const data = await response.json();
      
      // Validate response
      if (!data.response || data.response.trim() === '') {
        throw new InferenceError('Model generated empty response');
      }

      return data;
    } catch (error) {
      if (error instanceof BrainServiceError) throw error;
      throw new InferenceError(`Orchestration failed: ${error}`);
    }
  }

  /**
   * Validate inference request
   */
  private validateInferenceRequest(request: InferenceRequest): void {
    if (!request.message || typeof request.message !== 'string') {
      throw new ValidationError('Message is required and must be a string');
    }

    if (request.message.length < BRAIN_SERVICE_CONFIG.minMessageLength) {
      throw new ValidationError('Message cannot be empty');
    }

    if (request.message.length > BRAIN_SERVICE_CONFIG.maxMessageLength) {
      throw new ValidationError(
        `Message too long (max ${BRAIN_SERVICE_CONFIG.maxMessageLength} characters)`
      );
    }

    if (request.max_tokens && request.max_tokens < 1) {
      throw new ValidationError('max_tokens must be at least 1');
    }

    if (request.temperature && (request.temperature < 0 || request.temperature > 2)) {
      throw new ValidationError('temperature must be between 0 and 2');
    }
  }

  /**
   * Fetch with timeout
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new TimeoutError();
      }
      throw error;
    }
  }
}

/**
 * Singleton instance
 */
export const brainServiceClient = new BrainServiceClient();
