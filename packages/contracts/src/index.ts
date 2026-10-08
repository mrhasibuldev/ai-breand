export const API_PREFIX = '/api/v1' as const;
export const INTERNAL_PREFIX = '/internal/v1' as const;

export type ApiErrorEnvelope = {
  readonly error: {
    readonly code: string;
    readonly message: string;
    readonly details?: readonly { readonly field: string; readonly issue: string }[];
    readonly request_id: string;
    readonly retryable: boolean;
    readonly retry_after_seconds?: number;
  };
};

export type ApiSuccessEnvelope<T> = {
  readonly data: T;
  readonly meta: {
    readonly request_id: string;
    readonly next_cursor?: string | null;
  };
  readonly warnings: readonly string[];
};

export type PaginationCursor = string;

export function apiError(
  code: string,
  message: string,
  requestId: string,
  options: {
    readonly details?: readonly { readonly field: string; readonly issue: string }[];
    readonly retryable?: boolean;
    readonly retryAfterSeconds?: number;
  } = {},
): ApiErrorEnvelope {
  return {
    error: {
      code,
      message,
      ...(options.details ? { details: options.details } : {}),
      request_id: requestId,
      retryable: options.retryable ?? false,
      ...(options.retryAfterSeconds !== undefined
        ? { retry_after_seconds: options.retryAfterSeconds }
        : {}),
    },
  };
}

export function apiSuccess<T>(
  data: T,
  requestId: string,
  options: { readonly nextCursor?: string | null; readonly warnings?: readonly string[] } = {},
): ApiSuccessEnvelope<T> {
  return {
    data,
    meta: {
      request_id: requestId,
      ...(options.nextCursor !== undefined ? { next_cursor: options.nextCursor } : {}),
    },
    warnings: options.warnings ?? [],
  };
}
