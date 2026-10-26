/**
 * Response Validator
 *
 * Validates model output and determines if fallback is needed
 */

import { ResponseSource } from './intent-types.js';

export interface ValidationResult {
  isValid: boolean;
  reason?: string;
  source: ResponseSource;
}

export class ResponseValidator {
  /**
   * Validate model response
   */
  validate(response: string, originalInput: string): ValidationResult {
    // Check for empty response
    if (!response || response.trim().length === 0) {
      return {
        isValid: false,
        reason: 'Empty response',
        source: 'FALLBACK',
      };
    }

    // Check for pure repetition of input
    if (response.toLowerCase() === originalInput.toLowerCase()) {
      return {
        isValid: false,
        reason: 'Repeated input',
        source: 'FALLBACK',
      };
    }

    // Check for obviously truncated response (much shorter than input)
    if (response.length < originalInput.length * 0.3 && originalInput.length > 10) {
      return {
        isValid: false,
        reason: 'Truncated response',
        source: 'FALLBACK',
      };
    }

    // Check for only special tokens or gibberish
    const wordCount = response.trim().split(/\s+/).length;
    if (wordCount === 0) {
      return {
        isValid: false,
        reason: 'No words generated',
        source: 'FALLBACK',
      };
    }

    // Response appears valid
    return {
      isValid: true,
      source: 'VALIDATED_MODEL',
    };
  }

  /**
   * Generate fallback response
   */
  generateFallback(reason: string, intent?: string): string {
    if (intent === 'GREETING') {
      return "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?";
    }

    if (intent === 'IDENTITY_QUESTION') {
      return "I'm NexusAI, a custom AI assistant designed to help you with various tasks.";
    }

    if (intent === 'FAREWELL') {
      return "Goodbye! Feel free to come back anytime you need assistance.";
    }

    // Generic fallback
    return `I apologize, but I had trouble generating a response (${reason}). My current model is still learning. Could you try rephrasing your question?`;
  }
}

export const responseValidator = new ResponseValidator();
