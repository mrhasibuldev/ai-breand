/**
 * Brain Bridge Configuration
 */

export const BRAIN_SERVICE_CONFIG = {
  // Default to localhost for development
  baseUrl: 'http://127.0.0.1:8000',
  
  // Request timeout in milliseconds
  timeout: 30000,
  
  // Retry configuration
  maxRetries: 2,
  retryDelay: 1000,
  
  // Request validation
  maxMessageLength: 1000,
  minMessageLength: 1,
};

export const ENDPOINTS = {
  health: '/health',
  modelStatus: '/model/status',
  inference: '/inference',
  orchestrate: '/orchestrate',
} as const;
