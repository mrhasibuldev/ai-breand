/**
 * Brain Bridge Types
 *
 * Type definitions for TypeScript → Python ML service communication
 */

export interface InferenceRequest {
  message: string;
  conversation_id?: string;
  max_tokens?: number;
  temperature?: number;
}

export interface InferenceResponse {
  response: string;
  model: string;
  latency_ms: number;
  conversation_id?: string;
}

export interface OrchestratorRequest {
  message: string;
  conversation_id?: string;
  conversation_history?: Array<{role: string; content: string}>;
  request_id?: string;
}

export interface OrchestratorResponse {
  response: string;
  latency_ms: number;
  intent?: string;
  response_source?: string;
  language?: string;
  diagnostics?: Array<{name: string; status: string; duration_ms?: number; skipReason?: string}>;
}

export interface ModelStatus {
  model_loaded: boolean;
  model_name?: string;
  model_version?: string;
  parameter_count?: number;
  checkpoint?: string;
  device: string;
  vocabulary_size?: number;
  sequence_length?: number;
}

export interface HealthResponse {
  status: string;
  service: string;
  model_loaded: boolean;
}

export interface ServiceError {
  detail: string;
}
