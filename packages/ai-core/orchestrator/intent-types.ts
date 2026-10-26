/**
 * Intent Types
 *
 * Intent classification and routing types for NexusAI Brain
 */

export type IntentType =
  | 'GREETING'
  | 'FAREWELL'
  | 'IDENTITY_QUESTION'
  | 'PERSONAL_FACT_STATEMENT'
  | 'PERSONAL_FACT_QUESTION'
  | 'GENERAL_QUESTION'
  | 'UNKNOWN';

export interface IntentResult {
  intent: IntentType;
  confidence: number;
  extractedData?: Record<string, string>;
}

export type ResponseSource =
  | 'DETERMINISTIC_HANDLER'
  | 'NEURAL_MODEL'
  | 'VALIDATED_MODEL'
  | 'FALLBACK'
  | 'ERROR';

export interface ProcessingStage {
  name: string;
  status: 'pending' | 'running' | 'success' | 'skipped' | 'failed';
  durationMs?: number;
  error?: string;
  skipReason?: string;
}

export interface DiagnosticEvent {
  requestId: string;
  timestamp: number;
  stage: ProcessingStage;
  intent?: IntentResult;
  responseSource?: ResponseSource;
  processingPath?: string;
}
