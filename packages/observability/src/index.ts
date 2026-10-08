export type CorrelationContext = {
  readonly correlationId: string;
  readonly policyVersion?: string;
};

export type SafeEvent = {
  readonly eventType: string;
  readonly outcome: 'success' | 'failure' | 'denied';
  readonly context: CorrelationContext;
};

export interface RedactedTelemetry {
  emit(event: SafeEvent): void;
}

const SENSITIVE_KEY =
  /(password|secret|token|credential|prompt|completion|payload|health|memory|chat)/i;

export function redactForTelemetry(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(redactForTelemetry);
  if (!value || typeof value !== 'object') return value;
  return Object.fromEntries(
    Object.entries(value).map(([key, item]) => [
      key,
      SENSITIVE_KEY.test(key) ? '[REDACTED]' : redactForTelemetry(item),
    ]),
  );
}
