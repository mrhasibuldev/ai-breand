import type { SafetyMode } from '@nexusai/policy';
export type SafetyInput = {
  readonly accountId?: string;
  readonly content: string;
  readonly stage: 'input' | 'output';
};
export type SafetyDecision = {
  readonly mode: SafetyMode;
  readonly policyVersion: string;
  readonly allowModel: boolean;
  readonly allowAction: boolean;
};
export interface SafetyPolicyBoundary {
  evaluate(input: SafetyInput): Promise<SafetyDecision>;
}

export type ModelRequest = {
  readonly operation: 'chat' | 'plan' | 'safety' | 'memory_candidate';
  readonly accountId: string;
  readonly safetyMode: SafetyMode;
  readonly context: readonly unknown[];
};

export type ModelResponse = {
  readonly text: string;
  readonly safetyMode: SafetyMode;
  readonly providerAlias: string;
};

export interface ModelGateway {
  generate(request: ModelRequest): Promise<ModelResponse>;
}

export interface IntelligenceEngine {
  respond(request: ModelRequest): Promise<ModelResponse>;
}

export type MemoryCandidate = {
  readonly category: string;
  readonly purpose: string;
  readonly source: 'user_message' | 'check_in' | 'profile';
  readonly proposedValue: unknown;
};

export type UserInput = { readonly accountId: string; readonly content: string };
export type Intent = { readonly name: string; readonly confidence: number };
export type Plan = { readonly steps: readonly string[] };

export interface ContextBuilder {
  build(input: UserInput): Promise<readonly unknown[]>;
}
export interface IntentClassifier {
  classify(input: UserInput, context: readonly unknown[]): Promise<Intent>;
}
export interface Planner {
  plan(intent: Intent, context: readonly unknown[]): Promise<Plan>;
}
export interface OutputValidator {
  validate(response: ModelResponse): Promise<ModelResponse>;
}
export interface MemoryCandidateBuilder {
  build(input: UserInput, response: ModelResponse): Promise<MemoryCandidate | null>;
}
export interface ActionDispatcher {
  dispatch(plan: Plan, response: ModelResponse): Promise<void>;
}

export type IntelligencePipeline = {
  readonly context: ContextBuilder;
  readonly safety: SafetyPolicyBoundary;
  readonly intent: IntentClassifier;
  readonly planner: Planner;
  readonly gateway: ModelGateway;
  readonly output: OutputValidator;
  readonly memory: MemoryCandidateBuilder;
  readonly action: ActionDispatcher;
};

export async function runIntelligencePipeline(
  input: UserInput,
  pipeline: IntelligencePipeline,
): Promise<{ readonly response: ModelResponse; readonly memoryCandidate: MemoryCandidate | null }> {
  const context = await pipeline.context.build(input);
  const inputSafety: SafetyInput = {
    accountId: input.accountId,
    content: input.content,
    stage: 'input',
  };
  const before: SafetyDecision = await pipeline.safety.evaluate(inputSafety);
  if (!before.allowModel) throw new Error(`Model blocked by safety mode: ${before.mode}`);
  const intent = await pipeline.intent.classify(input, context);
  const plan = await pipeline.planner.plan(intent, context);
  const response = await pipeline.gateway.generate({
    operation: 'chat',
    accountId: input.accountId,
    safetyMode: before.mode,
    context,
  });
  const validated = await pipeline.output.validate(response);
  const after = await pipeline.safety.evaluate({
    accountId: input.accountId,
    content: validated.text,
    stage: 'output',
  });
  if (!after.allowAction) throw new Error(`Output blocked by safety mode: ${after.mode}`);
  await pipeline.action.dispatch(plan, validated);
  return { response: validated, memoryCandidate: await pipeline.memory.build(input, validated) };
}
