/**
 * Intent Classifier
 *
 * Deterministic intent classification for NexusAI Brain
 */

import { IntentType, IntentResult } from './intent-types.js';

export class IntentClassifier {
  /**
   * Classify user intent
   */
  classify(message: string): IntentResult {
    const lowerMessage = message.toLowerCase().trim();

    // Greeting patterns
    if (this.isGreeting(lowerMessage)) {
      return {
        intent: 'GREETING',
        confidence: 0.95,
      };
    }

    // Farewell patterns
    if (this.isFarewell(lowerMessage)) {
      return {
        intent: 'FAREWELL',
        confidence: 0.95,
      };
    }

    // Identity question about NexusAI
    if (this.isIdentityQuestion(lowerMessage)) {
      return {
        intent: 'IDENTITY_QUESTION',
        confidence: 0.9,
      };
    }

    // Personal fact statement (e.g., "My name is...")
    if (this.isPersonalFactStatement(lowerMessage)) {
      const extractedData = this.extractPersonalFact(lowerMessage);
      return {
        intent: 'PERSONAL_FACT_STATEMENT',
        confidence: 0.85,
        extractedData,
      };
    }

    // Personal fact question (e.g., "What is my name?")
    if (this.isPersonalFactQuestion(lowerMessage)) {
      return {
        intent: 'PERSONAL_FACT_QUESTION',
        confidence: 0.85,
        extractedData: { factType: this.identifyFactType(lowerMessage) },
      };
    }

    // Default to unknown
    return {
      intent: 'UNKNOWN',
      confidence: 0.5,
    };
  }

  private isGreeting(message: string): boolean {
    const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'];
    return greetings.some(g => message === g || message.startsWith(g + ' '));
  }

  private isFarewell(message: string): boolean {
    const farewells = ['bye', 'goodbye', 'see you', 'farewell', 'take care'];
    return farewells.some(f => message === f || message.startsWith(f + ' '));
  }

  private isIdentityQuestion(message: string): boolean {
    const patterns = [
      'what is your name',
      'who are you',
      'what are you',
      'what can you do',
      'how can you help',
    ];
    return patterns.some(p => message.includes(p));
  }

  private isPersonalFactStatement(message: string): boolean {
    const patterns = [
      'my name is',
      'i am',
      "i'm",
      'call me',
    ];
    return patterns.some(p => message.includes(p));
  }

  private isPersonalFactQuestion(message: string): boolean {
    const patterns = [
      'what is my name',
      'what is my',
      'who am i',
      'do you remember',
      'remember my',
    ];
    return patterns.some(p => message.includes(p));
  }

  private extractPersonalFact(message: string): Record<string, string> {
    const lowerMessage = message.toLowerCase();

    // Extract name
    if (lowerMessage.includes('my name is')) {
      const name = message.substring(lowerMessage.indexOf('my name is') + 10).trim();
      if (name) {
        return { name, factType: 'name' };
      }
    }

    if (lowerMessage.includes('i am') || lowerMessage.includes("i'm")) {
      const parts = message.split(/\s+/);
      const index = lowerMessage.includes('i am') ? parts.indexOf('am') : parts.indexOf("i'm");
      if (index >= 0 && index + 1 < parts.length && parts[index + 1]) {
        const extractedName = parts[index + 1];
        if (extractedName) {
          return { name: extractedName, factType: 'name' };
        }
      }
    }

    return {};
  }

  private identifyFactType(message: string): string {
    if (message.includes('name')) return 'name';
    if (message.includes('location')) return 'location';
    if (message.includes('preference')) return 'preference';
    return 'unknown';
  }
}

export const intentClassifier = new IntentClassifier();
