/**
 * NexusAI AI Safety Layer
 *
 * Validates AI inputs and outputs for safety
 */

import {
  AISafetyLayer,
  SafetyDecision,
  SafetyMode,
} from '../core/types';

/**
 * AI Safety Layer Implementation
 */
export class NexusAISafetyLayer implements AISafetyLayer {
  /**
   * Validate input
   */
  async validateInput(input: string, safetyMode: SafetyMode): Promise<SafetyDecision> {
    // Simple lexical checks
    const harmfulPatterns = [
      'hack',
      'exploit',
      'inject',
      'bypass',
      'jailbreak',
    ];

    const lowerInput = input.toLowerCase();
    const hasHarmful = harmfulPatterns.some((pattern) => lowerInput.includes(pattern));

    if (hasHarmful && safetyMode === 'strict') {
      return {
        mode: safetyMode,
        policyVersion: '1.0',
        allowModel: false,
        allowAction: false,
        reason: 'Harmful pattern detected',
      };
    }

    return {
      mode: safetyMode,
      policyVersion: '1.0',
      allowModel: true,
      allowAction: true,
    };
  }

  /**
   * Validate output
   */
  async validateOutput(output: string, safetyMode: SafetyMode): Promise<SafetyDecision> {
    // Simple lexical checks
    const harmfulPatterns = [
      'suicide',
      'self-harm',
      'violence',
      'illegal',
    ];

    const lowerOutput = output.toLowerCase();
    const hasHarmful = harmfulPatterns.some((pattern) => lowerOutput.includes(pattern));

    if (hasHarmful && safetyMode === 'strict') {
      return {
        mode: safetyMode,
        policyVersion: '1.0',
        allowModel: false,
        allowAction: false,
        reason: 'Harmful content detected',
      };
    }

    return {
      mode: safetyMode,
      policyVersion: '1.0',
      allowModel: true,
      allowAction: true,
    };
  }

  /**
   * Check for prompt injection
   */
  checkPromptInjection(input: string): boolean {
    const injectionPatterns = [
      'ignore previous instructions',
      'system prompt',
      'developer mode',
      'admin override',
    ];

    const lowerInput = input.toLowerCase();
    return injectionPatterns.some((pattern) => lowerInput.includes(pattern));
  }

  /**
   * Check for harmful content
   */
  checkHarmfulContent(content: string): boolean {
    const harmfulPatterns = [
      'suicide',
      'self-harm',
      'violence',
      'illegal activity',
      'hate speech',
    ];

    const lowerContent = content.toLowerCase();
    return harmfulPatterns.some((pattern) => lowerContent.includes(pattern));
  }
}

/**
 * Singleton instance
 */
export const aiSafetyLayer = new NexusAISafetyLayer();
