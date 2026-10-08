import { createHash } from 'node:crypto';
import type { RateLimitBoundary } from './foundation.js';

type WindowRecord = { count: number; expiresAt: number };

/** Process-local auth throttle for development and tests only. */
export class InMemoryAuthRateLimit implements RateLimitBoundary {
  private readonly windows = new Map<string, WindowRecord>();

  constructor(
    private readonly maximumAttempts = 5,
    private readonly windowSeconds = 60,
    private readonly maximumKeys = 10_000,
    private readonly now: () => number = Date.now,
  ) {
    if (!Number.isSafeInteger(maximumAttempts) || maximumAttempts < 1)
      throw new RangeError('maximumAttempts must be a positive integer');
    if (!Number.isSafeInteger(windowSeconds) || windowSeconds < 1)
      throw new RangeError('windowSeconds must be a positive integer');
  }

  async check(
    key: string,
    policy: { readonly maximumAttempts: number; readonly windowSeconds: number } = {
      maximumAttempts: this.maximumAttempts,
      windowSeconds: this.windowSeconds,
    },
  ): Promise<{ readonly allowed: boolean; readonly retryAfterSeconds?: number }> {
    if (!Number.isSafeInteger(policy.maximumAttempts) || policy.maximumAttempts < 1)
      throw new RangeError('maximumAttempts must be a positive integer');
    if (!Number.isSafeInteger(policy.windowSeconds) || policy.windowSeconds < 1)
      throw new RangeError('windowSeconds must be a positive integer');
    const timestamp = this.now();
    for (const [existingKey, record] of this.windows)
      if (record.expiresAt <= timestamp) this.windows.delete(existingKey);

    const record = this.windows.get(key);
    if (record && record.count >= policy.maximumAttempts)
      return {
        allowed: false,
        retryAfterSeconds: Math.max(1, Math.ceil((record.expiresAt - timestamp) / 1000)),
      };
    if (!record && this.windows.size >= this.maximumKeys)
      throw new Error('Development auth rate-limit capacity reached');

    this.windows.set(key, {
      count: (record?.count ?? 0) + 1,
      expiresAt: record?.expiresAt ?? timestamp + policy.windowSeconds * 1000,
    });
    return { allowed: true };
  }
}

export function authEmailRateKey(operation: 'register' | 'login', email: string): string {
  const digest = createHash('sha256').update(email.trim().toLowerCase()).digest('hex');
  return `auth:${operation}:email:${digest}`;
}
