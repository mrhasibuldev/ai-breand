/**
 * NexusAI Core Types
 *
 * Core type definitions for AI Brain architecture
 * All types are provider-neutral and model-agnostic
 */

/**
 * AI Model Metadata
 */
export interface ModelMetadata {
  /** Unique model identifier */
  id: string;
  /** Model name (e.g., "phi-3-mini-4k") */
  name: string;
  /** Model version */
  version: string;
  /** Model type */
  type: ModelType;
  /** Model capabilities */
  capabilities: ModelCapability[];
  /** Maximum context length */
  contextLength: number;
  /** Supported quantization levels */
  quantization: QuantizationLevel[];
  /** Hardware requirements */
  hardware: HardwareRequirement;
  /** Training dataset version (if applicable) */
  trainingDatasetVersion?: string;
  /** Evaluation score (0-1) */
  evaluationScore?: number;
  /** Model status */
  status: ModelStatus;
  /** File path to model weights */
  path?: string;
  /** Model size in bytes */
  sizeBytes?: number;
}

/** Model type */
export type ModelType =
  | 'language'
  | 'reasoning'
  | 'classification'
  | 'embedding'
  | 'vision'
  | 'image-generation';

/** Model capability */
export type ModelCapability =
  | 'text-generation'
  | 'reasoning'
  | 'planning'
  | 'classification'
  | 'embedding'
  | 'vision'
  | 'image-generation'
  | 'tool-calling';

/** Quantization level */
export type QuantizationLevel = 'fp32' | 'fp16' | 'bf16' | 'int8' | 'int4';

/** Hardware requirement */
export interface HardwareRequirement {
  /** Minimum RAM in GB */
  minRamGB: number;
  /** GPU required */
  requiresGPU: boolean;
  /** Minimum GPU VRAM in GB (if GPU required) */
  minGpuVRAMGB?: number;
  /** Supported hardware types */
  supportedHardware: 'cpu' | 'gpu' | 'both';
}

/** Model status */
export type ModelStatus =
  | 'planned'
  | 'downloading'
  | 'downloaded'
  | 'testing'
  | 'production'
  | 'deprecated';

/**
 * AI Request
 */
export interface AIRequest {
  /** Request ID for correlation */
  requestId: string;
  /** Account ID */
  accountId?: string;
  /** Operation type */
  operation: AIOperation;
  /** Input text/prompt */
  input: string;
  /** Context information */
  context: ContextItem[];
  /** Maximum tokens to generate */
  maxTokens?: number;
  /** Temperature (0-1) */
  temperature?: number;
  /** Top-p sampling */
  topP?: number;
  /** Top-k sampling */
  topK?: number;
  /** Output schema (if structured output required) */
  outputSchema?: any;
  /** Allowed tools */
  allowedTools?: string[];
  /** Safety mode */
  safetyMode: SafetyMode;
  /** Timeout in milliseconds */
  timeout?: number;
}

/** AI operation type */
export type AIOperation =
  | 'chat'
  | 'plan'
  | 'reason'
  | 'classify'
  | 'embed'
  | 'vision'
  | 'image-generate'
  | 'tool-call';

/** Context item */
export interface ContextItem {
  /** Context type */
  type: 'conversation' | 'goal' | 'plan' | 'check-in' | 'memory' | 'profile';
  /** Context ID */
  id: string;
  /** Content */
  content: any;
  /** Sensitivity level */
  sensitivity: 'public' | 'private' | 'sensitive';
  /** Whether user consented */
  consented: boolean;
  /** Purpose of this context */
  purpose: string;
}

/** Safety mode */
export type SafetyMode = 'strict' | 'standard' | 'permissive';

/**
 * AI Response
 */
export interface AIResponse {
  /** Request ID */
  requestId: string;
  /** Generated text/content */
  content: string;
  /** Model used */
  modelId: string;
  /** Model version */
  modelVersion: string;
  /** Provider alias (internal) */
  providerAlias: string;
  /** Operation type */
  operation: AIOperation;
  /** Tokens used */
  tokensUsed: number;
  /** Time taken in milliseconds */
  latencyMs: number;
  /** Finish reason */
  finishReason: FinishReason;
  /** Safety decision */
  safetyDecision: SafetyDecision;
  /** Confidence score (0-1) */
  confidence?: number;
  /** Structured data (if applicable) */
  structuredData?: any;
  /** Tool calls (if applicable) */
  toolCalls?: ToolCall[];
  /** Memory candidates */
  memoryCandidates?: MemoryCandidate[];
}

/** Finish reason */
export type FinishReason =
  | 'completed'
  | 'length-limited'
  | 'blocked'
  | 'timeout'
  | 'error';

/** Safety decision */
export interface SafetyDecision {
  /** Mode used */
  mode: SafetyMode;
  /** Policy version */
  policyVersion: string;
  /** Whether to allow model output */
  allowModel: boolean;
  /** Whether to allow action execution */
  allowAction: boolean;
  /** Reason for decision */
  reason?: string;
}

/** Tool call */
export interface ToolCall {
  /** Tool name */
  name: string;
  /** Tool arguments */
  arguments: Record<string, any>;
  /** Tool ID */
  id: string;
}

/** Memory candidate */
export interface MemoryCandidate {
  /** Category */
  category: string;
  /** Purpose */
  purpose: string;
  /** Source */
  source: 'user-message' | 'check-in' | 'profile' | 'ai-inference';
  /** Proposed value */
  proposedValue: any;
  /** Confidence */
  confidence: number;
}

/**
 * Intent
 */
export interface Intent {
  /** Intent name */
  name: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Detected parameters */
  parameters?: Record<string, any>;
}

/**
 * Plan
 */
export interface Plan {
  /** Plan ID */
  id: string;
  /** Plan steps */
  steps: PlanStep[];
  /** Estimated completion time */
  estimatedTime?: number;
  /** Required tools */
  requiredTools?: string[];
}

/** Plan step */
export interface PlanStep {
  /** Step ID */
  id: string;
  /** Step description */
  description: string;
  /** Step type */
  type: 'think' | 'tool' | 'api' | 'memory' | 'output';
  /** Required tools */
  tools?: string[];
  /** Dependencies */
  dependencies?: string[];
}

/**
 * Model Adapter Interface
 */
export interface ModelAdapter {
  /** Adapter ID */
  id: string;
  /** Supported model ID */
  modelId: string;
  /** Load model */
  load(config: ModelLoadConfig): Promise<void>;
  /** Generate response */
  generate(request: AIRequest): Promise<AIResponse>;
  /** Unload model */
  unload(): Promise<void>;
  /** Get model metadata */
  getMetadata(): ModelMetadata;
  /** Check if model is loaded */
  isLoaded(): boolean;
}

/** Model load configuration */
export interface ModelLoadConfig {
  /** Model path */
  path: string;
  /** Quantization level */
  quantization?: QuantizationLevel;
  /** Device (cpu, cuda, etc.) */
  device?: string;
  /** Max memory in GB */
  maxMemoryGB?: number;
}

/**
 * Inference Runtime
 */
export interface InferenceRuntime {
  /** Runtime ID */
  id: string;
  /** Runtime type */
  type: RuntimeType;
  /** Initialize runtime */
  initialize(config: RuntimeConfig): Promise<void>;
  /** Load model */
  loadModel(modelId: string, config: ModelLoadConfig): Promise<void>;
  /** Unload model */
  unloadModel(modelId: string): Promise<void>;
  /** Execute inference */
  execute(request: AIRequest): Promise<AIResponse>;
  /** Get runtime status */
  getStatus(): RuntimeStatus;
  /** Shutdown runtime */
  shutdown(): Promise<void>;
}

/** Runtime type */
export type RuntimeType = 'cpu' | 'gpu' | 'hybrid';

/** Runtime configuration */
export interface RuntimeConfig {
  /** Device preference */
  device?: 'cpu' | 'cuda' | 'auto';
  /** Max memory in GB */
  maxMemoryGB?: number;
  /** Number of threads */
  numThreads?: number;
  /** Batch size */
  batchSize?: number;
}

/** Runtime status */
export interface RuntimeStatus {
  /** Whether runtime is initialized */
  initialized: boolean;
  /** Loaded models */
  loadedModels: string[];
  /** Available memory in GB */
  availableMemoryGB: number;
  /** Used memory in GB */
  usedMemoryGB: number;
  /** Device type */
  device: string;
}

/**
 * Model Router
 */
export interface ModelRouter {
  /** Route request to appropriate model */
  route(request: AIRequest): Promise<ModelRoutingDecision>;
  /** Get all available models */
  getAvailableModels(): ModelMetadata[];
  /** Register model */
  registerModel(metadata: ModelMetadata): void;
  /** Unregister model */
  unregisterModel(modelId: string): void;
}

/** Model routing decision */
export interface ModelRoutingDecision {
  /** Selected model ID */
  modelId: string;
  /** Reason for selection */
  reason: string;
  /** Confidence in decision */
  confidence: number;
  /** Fallback models */
  fallbackModels?: string[];
}

/**
 * AI Orchestrator
 */
export interface AIOrchestrator {
  /** Process AI request through full pipeline */
  process(request: AIRequest): Promise<AIResponse>;
  /** Get orchestrator status */
  getStatus(): OrchestratorStatus;
}

/** Orchestrator status */
export interface OrchestratorStatus {
  /** Pipeline components status */
  components: {
    context: 'active' | 'inactive' | 'error';
    intent: 'active' | 'inactive' | 'error';
    planner: 'active' | 'inactive' | 'error';
    router: 'active' | 'inactive' | 'error';
    inference: 'active' | 'inactive' | 'error';
    validation: 'active' | 'inactive' | 'error';
    memory: 'active' | 'inactive' | 'error';
    tools: 'active' | 'inactive' | 'error';
  };
}

/**
 * Context Manager
 */
export interface ContextManager {
  /** Build context for request */
  buildContext(request: AIRequest): Promise<ContextItem[]>;
  /** Add context item */
  addContext(item: ContextItem): void;
  /** Remove context item */
  removeContext(itemId: string): void;
  /** Clear context */
  clearContext(): void;
}

/**
 * Memory Interface
 */
export interface MemoryInterface {
  /** Store memory */
  store(memory: MemoryCandidate): Promise<void>;
  /** Retrieve memories */
  retrieve(query: string, limit?: number): Promise<MemoryCandidate[]>;
  /** Delete memory */
  delete(memoryId: string): Promise<void>;
  /** Update memory */
  update(memoryId: string, updates: Partial<MemoryCandidate>): Promise<void>;
}

/**
 * Tool Registry
 */
export interface ToolRegistry {
  /** Register tool */
  register(tool: ToolDefinition): void;
  /** Unregister tool */
  unregister(toolId: string): void;
  /** Get tool */
  get(toolId: string): ToolDefinition | undefined;
  /** List all tools */
  list(): ToolDefinition[];
  /** Execute tool */
  execute(toolId: string, args: Record<string, any>): Promise<any>;
}

/** Tool definition */
export interface ToolDefinition {
  /** Tool ID */
  id: string;
  /** Tool name */
  name: string;
  /** Tool description */
  description: string;
  /** Input schema */
  inputSchema: any;
  /** Output schema */
  outputSchema: any;
  /** Permission level */
  permission: PermissionLevel;
  /** Risk level */
  riskLevel: RiskLevel;
  /** Timeout in milliseconds */
  timeout: number;
  /** Execute function */
  execute: (args: any) => Promise<any>;
}

/** Permission level */
export type PermissionLevel = 'auto' | 'controlled' | 'manual';

/** Risk level */
export type RiskLevel = 'low' | 'medium' | 'high';

/**
 * Tool Permission System
 */
export interface ToolPermissionSystem {
  /** Check if tool execution is allowed */
  checkPermission(toolId: string, accountId?: string): Promise<PermissionDecision>;
  /** Request user confirmation */
  requestConfirmation(toolId: string, args: any): Promise<boolean>;
}

/** Permission decision */
export interface PermissionDecision {
  /** Whether execution is allowed */
  allowed: boolean;
  /** Reason */
  reason: string;
  /** Requires confirmation */
  requiresConfirmation: boolean;
}

/**
 * AI Evaluation Interface
 */
export interface AIEvaluation {
  /** Evaluate model response */
  evaluate(response: AIResponse, expected?: any): Promise<EvaluationResult>;
  /** Run benchmark */
  runBenchmark(modelId: string, dataset: string): Promise<BenchmarkResult>;
}

/** Evaluation result */
export interface EvaluationResult {
  /** Evaluation score (0-1) */
  score: number;
  /** Accuracy */
  accuracy?: number;
  /** Relevance */
  relevance?: number;
  /** Safety score */
  safety?: number;
  /** Quality score */
  quality?: number;
  /** Metrics */
  metrics: Record<string, number>;
}

/** Benchmark result */
export interface BenchmarkResult {
  /** Model ID */
  modelId: string;
  /** Dataset */
  dataset: string;
  /** Average score */
  averageScore: number;
  /** Per-metric scores */
  scores: Record<string, number>;
  /** Time taken */
  timeMs: number;
}

/**
 * AI Safety Layer
 */
export interface AISafetyLayer {
  /** Validate input */
  validateInput(input: string, safetyMode: SafetyMode): Promise<SafetyDecision>;
  /** Validate output */
  validateOutput(output: string, safetyMode: SafetyMode): Promise<SafetyDecision>;
  /** Check for prompt injection */
  checkPromptInjection(input: string): boolean;
  /** Check for harmful content */
  checkHarmfulContent(content: string): boolean;
}

/**
 * Model Versioning
 */
export interface ModelVersioning {
  /** Register model version */
  registerVersion(metadata: ModelMetadata): void;
  /** Get latest version */
  getLatestVersion(modelId: string): ModelMetadata | undefined;
  /** Get specific version */
  getVersion(modelId: string, version: string): ModelMetadata | undefined;
  /** List all versions */
  listVersions(modelId: string): ModelMetadata[];
  /** Rollback to version */
  rollback(modelId: string, version: string): void;
}

/**
 * Observability
 */
export interface AIObservability {
  /** Log AI execution */
  logExecution(event: AIExecutionEvent): void;
  /** Get metrics */
  getMetrics(filter?: MetricsFilter): Promise<AIMetrics>;
  /** Get logs */
  getLogs(filter?: LogFilter): Promise<AIExecutionEvent[]>;
}

/** AI execution event */
export interface AIExecutionEvent {
  /** Event ID */
  eventId: string;
  /** Request ID */
  requestId: string;
  /** Timestamp */
  timestamp: Date;
  /** Operation */
  operation: AIOperation;
  /** Model ID */
  modelId: string;
  /** Model version */
  modelVersion: string;
  /** Input tokens */
  inputTokens: number;
  /** Output tokens */
  outputTokens: number;
  /** Latency in milliseconds */
  latencyMs: number;
  /** Finish reason */
  finishReason: FinishReason;
  /** Error message (if any) */
  error?: string;
  /** Confidence score */
  confidence?: number;
}

/** Metrics filter */
export interface MetricsFilter {
  /** Model ID */
  modelId?: string;
  /** Operation */
  operation?: AIOperation;
  /** Start time */
  startTime?: Date;
  /** End time */
  endTime?: Date;
}

/** AI metrics */
export interface AIMetrics {
  /** Total requests */
  totalRequests: number;
  /** Average latency */
  averageLatencyMs: number;
  /** Total tokens */
  totalTokens: number;
  /** Success rate */
  successRate: number;
  /** Error rate */
  errorRate: number;
  /** Per-model metrics */
  byModel: Record<string, Partial<AIMetrics>>;
}

/** Log filter */
export interface LogFilter extends MetricsFilter {
  /** Include errors only */
  errorsOnly?: boolean;
  /** Limit */
  limit?: number;
}

// Re-export LogFilter for backward compatibility
export type { LogFilter as LogFilterType };
