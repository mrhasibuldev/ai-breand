import { describe, expect, it } from 'vitest';
import { isSafetyMode } from '../packages/policy/src/index.js';
import { API_PREFIX, INTERNAL_PREFIX } from '../packages/contracts/src/index.js';
import { assertOwnership } from '../packages/domain/src/index.js';
import {
  ConsentRequiredMemoryService,
  type MemoryRecord,
  type MemoryRepository,
} from '../packages/memory-core/src/index.js';
import {
  JobExecutor,
  type JobIdempotencyStore,
  type JobTelemetry,
} from '../packages/worker-core/src/index.js';
import { redactForTelemetry } from '../packages/observability/src/index.js';
import { readRuntimeConfig } from '../packages/config/src/index.js';
import { evaluateWellnessFreeText } from '../packages/safety-core/src/index.js';
import { buildApp } from '../apps/api/src/app.js';

describe('implementation foundation boundaries', () => {
  it('preserves approved safety modes', () => {
    expect(isSafetyMode('NORMAL')).toBe(true);
    expect(isSafetyMode('DIAGNOSIS')).toBe(false);
  });

  it('keeps the bounded wellness text policy non-clinical', () => {
    expect(evaluateWellnessFreeText('Use calm, practical encouragement')).toMatchObject({
      allowed: true,
      policyVersion: 'wellness-input-v1',
    });
    expect(evaluateWellnessFreeText('Diagnose my condition')).toMatchObject({
      allowed: false,
      reason: 'prohibited_clinical_content',
    });
  });

  it('preserves approved API prefixes', () => {
    expect(API_PREFIX).toBe('/api/v1');
    expect(INTERNAL_PREFIX).toBe('/internal/v1');
  });

  it('enforces ownership and fails closed for revoked memory consent', async () => {
    expect(() => assertOwnership({ accountId: 'a' as never }, 'b')).toThrow();
    const record: MemoryRecord = {
      id: 'm1',
      accountId: 'a',
      purpose: 'wellness',
      value: 'x',
      status: 'candidate',
    };
    const store: MemoryRepository = {
      save: async () => {},
      find: async () => record,
      listApproved: async () => [],
      changeStatus: async () => {},
      clear: async () => {},
    };
    const service = new ConsentRequiredMemoryService({ isMemoryEnabled: async () => false }, store);
    await expect(service.propose(record)).rejects.toThrow('consent');
    await expect(service.retrieve('a', 'wellness')).resolves.toEqual([]);
  });

  it('supports idempotent retry execution and redacts sensitive telemetry', async () => {
    const completed = new Set<string>();
    const events: string[] = [];
    const idempotency: JobIdempotencyStore = {
      hasCompleted: async (key) => completed.has(key),
      markCompleted: async (key) => void completed.add(key),
    };
    const telemetry: JobTelemetry = { record: (event) => events.push(event.outcome) };
    const executor = new JobExecutor(idempotency, telemetry);
    let attempts = 0;
    const job = {
      id: 'j1',
      kind: 'ai_processing' as const,
      idempotencyKey: 'k1',
      correlationId: 'c1',
      payload: {},
      attempt: 1,
    };
    await executor.run(
      job,
      {
        execute: async () => {
          attempts += 1;
          if (attempts === 1) throw new Error('retry');
        },
      },
      { maxAttempts: 2, timeoutMs: 100 },
    );
    await executor.run(
      job,
      {
        execute: async () => {
          attempts += 1;
        },
      },
      { maxAttempts: 2, timeoutMs: 100 },
    );
    expect(attempts).toBe(2);
    expect(events).toEqual(['failure', 'success', 'duplicate']);
    expect(redactForTelemetry({ password: 'x', chat: 'private', ok: 'yes' })).toEqual({
      password: '[REDACTED]',
      chat: '[REDACTED]',
      ok: 'yes',
    });
  });

  it('validates production configuration without inventing provider requirements', () => {
    expect(() => readRuntimeConfig({ NODE_ENV: 'production' })).toThrow('DATABASE_URL');
    expect(readRuntimeConfig({ NODE_ENV: 'test' }).ready).toBe(true);
    const configuredButUnavailable = {
      NODE_ENV: 'production',
      DATABASE_URL: 'postgresql://configured-but-not-connected.invalid/nexusai',
    };
    expect(readRuntimeConfig(configuredButUnavailable).ready).toBe(false);
    expect(() => buildApp({ env: configuredButUnavailable })).toThrow(
      'Production persistent storage is unavailable',
    );
  });
});
