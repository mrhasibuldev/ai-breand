export type JobKind =
  | 'ai_processing'
  | 'notification_delivery'
  | 'memory_lifecycle'
  | 'data_deletion'
  | 'data_export'
  | 'usage_processing';

export type Job<Payload = unknown> = {
  readonly id: string;
  readonly kind: JobKind;
  readonly idempotencyKey: string;
  readonly correlationId: string;
  readonly payload: Payload;
  readonly attempt: number;
};

export type JobPolicy = {
  readonly maxAttempts: number;
  readonly timeoutMs: number;
};

export interface JobHandler<Payload = unknown> {
  execute(job: Job<Payload>): Promise<void>;
}

export interface JobIdempotencyStore {
  hasCompleted(key: string): Promise<boolean>;
  markCompleted(key: string): Promise<void>;
}

export interface JobTelemetry {
  record(event: {
    readonly jobId: string;
    readonly kind: JobKind;
    readonly correlationId: string;
    readonly outcome: 'success' | 'failure' | 'duplicate';
    readonly attempt: number;
  }): void;
}

export class JobExecutor {
  constructor(
    private readonly idempotency: JobIdempotencyStore,
    private readonly telemetry: JobTelemetry,
  ) {}

  async run<Payload>(
    job: Job<Payload>,
    handler: JobHandler<Payload>,
    policy: JobPolicy,
  ): Promise<void> {
    if (await this.idempotency.hasCompleted(job.idempotencyKey)) {
      this.telemetry.record({
        jobId: job.id,
        kind: job.kind,
        correlationId: job.correlationId,
        attempt: job.attempt,
        outcome: 'duplicate',
      });
      return;
    }

    let lastError: unknown;
    for (let attempt = Math.max(1, job.attempt); attempt <= policy.maxAttempts; attempt += 1) {
      try {
        await withTimeout(handler.execute({ ...job, attempt }), policy.timeoutMs);
        await this.idempotency.markCompleted(job.idempotencyKey);
        this.telemetry.record({
          jobId: job.id,
          kind: job.kind,
          correlationId: job.correlationId,
          attempt,
          outcome: 'success',
        });
        return;
      } catch (error) {
        lastError = error;
        this.telemetry.record({
          jobId: job.id,
          kind: job.kind,
          correlationId: job.correlationId,
          attempt,
          outcome: 'failure',
        });
      }
    }
    throw lastError;
  }
}

async function withTimeout<Result>(promise: Promise<Result>, timeoutMs: number): Promise<Result> {
  if (!Number.isInteger(timeoutMs) || timeoutMs <= 0) throw new Error('Invalid job timeout');
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      promise,
      new Promise<never>((_resolve, reject) => {
        timer = setTimeout(() => reject(new Error('Job timed out')), timeoutMs);
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}
