import { createHash } from 'node:crypto';

export type IdempotentResult = {
  readonly statusCode: number;
  readonly data?: unknown;
  readonly headers?: Readonly<Record<string, string>>;
};

type Entry = {
  readonly requestDigest: string;
  readonly result: Promise<IdempotentResult>;
};

export class IdempotencyKeyReusedError extends Error {}

/** Process-local development store. Entries intentionally reset with the API process. */
export class InMemoryIdempotencyStore {
  private readonly entries = new Map<string, Entry>();

  async execute(input: {
    readonly scope: string;
    readonly operation: string;
    readonly key: string;
    readonly normalizedRequest: unknown;
    readonly run: () => Promise<IdempotentResult>;
  }): Promise<IdempotentResult> {
    const storageKey = `${input.scope}\u0000${input.operation}\u0000${input.key}`;
    const requestDigest = digest(input.normalizedRequest);
    const existing = this.entries.get(storageKey);

    if (existing) {
      if (existing.requestDigest !== requestDigest) throw new IdempotencyKeyReusedError();
      return existing.result;
    }

    const result = input.run();
    const entry = { requestDigest, result };
    this.entries.set(storageKey, entry);

    try {
      return await result;
    } catch (error) {
      if (this.entries.get(storageKey) === entry) this.entries.delete(storageKey);
      throw error;
    }
  }
}

function digest(value: unknown): string {
  return createHash('sha256')
    .update(JSON.stringify(canonicalize(value)) ?? 'null')
    .digest('hex');
}

function canonicalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, item]) => [key, canonicalize(item)]),
    );
  }
  return value;
}
