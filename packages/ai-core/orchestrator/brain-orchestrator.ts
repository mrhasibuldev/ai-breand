/**
 * Brain Orchestrator
 *
 * Manages the conversation flow between user message and AI response
 * Integrates context, intent classification, memory, inference, and validation
 */

import {
  InferenceRequest,
  InferenceResponse,
  brainServiceClient,
  InferenceError,
  ServiceUnavailableError,
} from '../bridge/index.js';
import { IntentType, IntentResult, ResponseSource, ProcessingStage, DiagnosticEvent } from './intent-types.js';
import { intentClassifier } from './intent-classifier.js';
import { responseValidator, ValidationResult } from './response-validator.js';

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ConversationContext {
  conversation_id: string;
  messages: ConversationMessage[];
  max_history: number;
  facts: Map<string, string>; // Personal facts like name
}

export interface OrchestratorConfig {
  maxHistoryLength?: number;
  defaultMaxTokens?: number;
  defaultTemperature?: number;
}

export interface ProcessMessageResult {
  response: string;
  latencyMs: number;
  intent: IntentResult;
  responseSource: ResponseSource;
  diagnostics: ProcessingStage[];
}

/**
 * Brain Orchestrator
 * 
 * Coordinates the flow from user message to AI response:
 * 1. Receive user message
 * 2. Classify intent
 * 3. Extract/store personal facts
 * 4. Update conversation context
 * 5. Select processing path (deterministic or neural)
 * 6. Execute selected path
 * 7. Validate response
 * 8. Update conversation context
 * 9. Return response with diagnostics
 */
export class BrainOrchestrator {
  private conversations: Map<string, ConversationContext>;
  private config: Required<OrchestratorConfig>;

  constructor(config?: OrchestratorConfig) {
    this.conversations = new Map();
    this.config = {
      maxHistoryLength: config?.maxHistoryLength || 10,
      defaultMaxTokens: config?.defaultMaxTokens || 50,
      defaultTemperature: config?.defaultTemperature || 0.8,
    };
  }

  /**
   * Process user message and generate response
   */
  async processMessage(
    conversationId: string,
    userMessage: string
  ): Promise<ProcessMessageResult> {
    const requestId = crypto.randomUUID();
    const diagnostics: ProcessingStage[] = [];

    try {
      // Stage 1: Input validation
      diagnostics.push({
        name: 'Input Validation',
        status: 'running',
      });
      
      if (!userMessage || userMessage.trim().length === 0) {
        throw new InferenceError('Message cannot be empty');
      }
      
      diagnostics[diagnostics.length - 1]!.status = 'success';

      // Stage 2: Intent classification
      diagnostics.push({
        name: 'Intent Classification',
        status: 'running',
      });
      
      const intent = intentClassifier.classify(userMessage);
      
      diagnostics[diagnostics.length - 1]!.status = 'success';
      diagnostics[diagnostics.length - 1]!.durationMs = 1;

      // Stage 3: Context loading
      diagnostics.push({
        name: 'Context Loading',
        status: 'running',
      });
      
      const context = this.getOrCreateContext(conversationId);
      
      diagnostics[diagnostics.length - 1]!.status = 'success';

      // Stage 4: Memory operation
      diagnostics.push({
        name: 'Memory Operation',
        status: 'running',
      });
      
      this.handleMemory(context, intent, userMessage);
      
      diagnostics[diagnostics.length - 1]!.status = 'success';

      // Stage 5: Routing decision
      diagnostics.push({
        name: 'Routing Decision',
        status: 'running',
      });
      
      const routingDecision = this.makeRoutingDecision(intent, context);
      
      diagnostics[diagnostics.length - 1]!.status = 'success';
      diagnostics[diagnostics.length - 1]!.durationMs = 1;

      // Stage 6: Execute selected path
      let response: string;
      let responseSource: ResponseSource;

      if (routingDecision.useDeterministic) {
        // Use deterministic handler
        diagnostics.push({
          name: 'Deterministic Handler',
          status: 'running',
        });
        
        response = this.handleDeterministicIntent(intent, context);
        responseSource = 'DETERMINISTIC_HANDLER';
        
        diagnostics[diagnostics.length - 1]!.status = 'success';
        diagnostics[diagnostics.length - 1]!.durationMs = 1;
        
        // Skip neural model stage
        diagnostics.push({
          name: 'Neural Model Inference',
          status: 'skipped',
          skipReason: 'Deterministic handler selected',
        });
      } else {
        // Use neural model
        diagnostics.push({
          name: 'Neural Model Inference',
          status: 'running',
        });
        
        // Add user message to context
        context.messages.push({
          role: 'user',
          content: userMessage,
          timestamp: new Date(),
        });

        // Trim history if needed
        this.trimHistory(context);

        // Prepare inference request
        const request: InferenceRequest = {
          message: userMessage,
          conversation_id: conversationId,
          max_tokens: this.config.defaultMaxTokens,
          temperature: this.config.defaultTemperature,
        };

        // Call ML service
        const startTime = Date.now();
        const inferenceResponse = await brainServiceClient.inference(request);
        const latencyMs = Date.now() - startTime;

        response = inferenceResponse.response;
        responseSource = 'NEURAL_MODEL';
        
        diagnostics[diagnostics.length - 1]!.status = 'success';
        diagnostics[diagnostics.length - 1]!.durationMs = latencyMs;

        // Stage 7: Response validation
        diagnostics.push({
          name: 'Response Validation',
          status: 'running',
        });
        
        const validationResult = responseValidator.validate(response, userMessage);
        
        if (!validationResult.isValid) {
          // Use fallback
          response = responseValidator.generateFallback(validationResult.reason || 'unknown', intent.intent);
          responseSource = validationResult.source;
        } else {
          responseSource = validationResult.source;
        }
        
        diagnostics[diagnostics.length - 1]!.status = 'success';
        diagnostics[diagnostics.length - 1]!.durationMs = 1;
      }

      // Stage 8: Update context with assistant response
      context.messages.push({
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      });

      // Trim history if needed
      this.trimHistory(context);

      // Stage 9: Final response delivered
      diagnostics.push({
        name: 'Final Response Delivered',
        status: 'success',
      });

      return {
        response,
        latencyMs: diagnostics.reduce((sum, stage) => sum + (stage.durationMs || 0), 0),
        intent,
        responseSource,
        diagnostics,
      };
    } catch (error) {
      // Mark failed stage
      if (diagnostics.length > 0) {
        const lastStage = diagnostics[diagnostics.length - 1];
        if (lastStage) {
          lastStage.status = 'failed';
          lastStage.error = error instanceof Error ? error.message : 'Unknown error';
        }
      }

      if (error instanceof InferenceError || error instanceof ServiceUnavailableError) {
        throw error;
      }
      throw new InferenceError(`Orchestrator failed: ${error}`);
    }
  }

  /**
   * Handle memory operations
   */
  private handleMemory(context: ConversationContext, intent: IntentResult, message: string): void {
    if (intent.intent === 'PERSONAL_FACT_STATEMENT' && intent.extractedData) {
      // Store personal facts
      if (intent.extractedData.name) {
        context.facts.set('name', intent.extractedData.name);
      }
    }
  }

  /**
   * Make routing decision
   */
  private makeRoutingDecision(intent: IntentResult, context: ConversationContext): {
    useDeterministic: boolean;
    reason: string;
  } {
    // Use deterministic handlers for specific intents
    if (intent.intent === 'GREETING') {
      return { useDeterministic: true, reason: 'Greeting intent' };
    }

    if (intent.intent === 'FAREWELL') {
      return { useDeterministic: true, reason: 'Farewell intent' };
    }

    if (intent.intent === 'IDENTITY_QUESTION') {
      return { useDeterministic: true, reason: 'Identity question' };
    }

    if (intent.intent === 'PERSONAL_FACT_QUESTION') {
      // Check if we have the fact in memory
      const factType = intent.extractedData?.factType || 'name';
      if (context.facts.has(factType)) {
        return { useDeterministic: true, reason: 'Fact available in memory' };
      }
    }

    // Use neural model for other cases
    return { useDeterministic: false, reason: 'Neural model selected' };
  }

  /**
   * Handle deterministic intents
   */
  private handleDeterministicIntent(intent: IntentResult, context: ConversationContext): string {
    if (intent.intent === 'GREETING') {
      return "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?";
    }

    if (intent.intent === 'FAREWELL') {
      return "Goodbye! Feel free to come back anytime you need assistance.";
    }

    if (intent.intent === 'IDENTITY_QUESTION') {
      return "I'm NexusAI, a custom AI assistant designed to help you with various tasks.";
    }

    if (intent.intent === 'PERSONAL_FACT_QUESTION') {
      const factType = intent.extractedData?.factType || 'name';
      const fact = context.facts.get(factType);
      if (fact) {
        if (factType === 'name') {
          return `Your name is ${fact}.`;
        }
        return `I remember: ${factType} is ${fact}.`;
      }
      return "I don't have that information in our conversation memory.";
    }

    return "I'm not sure how to help with that right now.";
  }

  /**
   * Get conversation context
   */
  getConversationContext(conversationId: string): ConversationContext | null {
    return this.conversations.get(conversationId) || null;
  }

  /**
   * Clear conversation context
   */
  clearConversation(conversationId: string): void {
    this.conversations.delete(conversationId);
  }

  /**
   * Get or create conversation context
   */
  private getOrCreateContext(conversationId: string): ConversationContext {
    if (!this.conversations.has(conversationId)) {
      this.conversations.set(conversationId, {
        conversation_id: conversationId,
        messages: [],
        max_history: this.config.maxHistoryLength,
        facts: new Map(),
      });
    }
    return this.conversations.get(conversationId)!;
  }

  /**
   * Trim conversation history
   */
  private trimHistory(context: ConversationContext): void {
    if (context.messages.length > context.max_history * 2) {
      // Keep last max_history * 2 messages (user + assistant pairs)
      context.messages = context.messages.slice(-context.max_history * 2);
    }
  }
}

/**
 * Singleton instance
 */
export const brainOrchestrator = new BrainOrchestrator();
