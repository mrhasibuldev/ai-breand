import { describe, expect, it } from 'vitest';
import { buildApp } from '../apps/api/src/app.js';
import { InMemoryAuthRateLimit } from '../apps/api/src/rate-limit.js';

describe('reported development-foundation findings', () => {
  it('limits authentication by IP and normalized email and returns a retry interval', async () => {
    const app = buildApp({ env: { NODE_ENV: 'test' } });
    try {
      for (let attempt = 0; attempt < 5; attempt += 1) {
        await app.inject({
          method: 'POST',
          url: '/api/v1/auth/register',
          headers: { 'idempotency-key': `limited-${attempt}` },
          payload: { email: 'throttle@example.com' },
        });
      }
      const limited = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/register',
        headers: { 'idempotency-key': 'limited-final' },
        payload: { email: 'THROTTLE@example.com' },
      });
      expect(limited.statusCode).toBe(429);
      expect(limited.headers['retry-after']).toBe('60');
      expect(limited.json().error).toMatchObject({ code: 'rate_limited' });
      expect(limited.body).not.toContain('throttle@example.com');
    } finally {
      await app.close();
    }
  });

  it('fails closed when the development auth limiter is unavailable', async () => {
    const app = buildApp({
      env: { NODE_ENV: 'test' },
      rateLimit: { check: async () => Promise.reject(new Error('private limiter detail')) },
    });
    try {
      const response = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/register',
        headers: { 'idempotency-key': 'limiter-outage' },
        payload: { email: 'limiter-outage@example.com' },
      });
      expect(response.statusCode).toBe(503);
      expect(response.json().error.code).toBe('auth_dependency_unavailable');
      expect(response.body).not.toContain('private limiter detail');
    } finally {
      await app.close();
    }
  });

  it('expires fixed-window auth buckets and uses a bounded process-local store', async () => {
    let now = 1_000;
    const limiter = new InMemoryAuthRateLimit(2, 10, 2, () => now);
    await expect(limiter.check('one')).resolves.toEqual({ allowed: true });
    await expect(limiter.check('one')).resolves.toEqual({ allowed: true });
    await expect(limiter.check('one')).resolves.toMatchObject({ allowed: false });
    await expect(limiter.check('two')).resolves.toEqual({ allowed: true });
    await expect(limiter.check('three')).rejects.toThrow('capacity reached');
    now += 10_000;
    await expect(limiter.check('three')).resolves.toEqual({ allowed: true });
  });

  it('rejects unsupported logout payload fields and accepts the normalized empty request', async () => {
    const app = buildApp({ env: { NODE_ENV: 'test' } });
    try {
      const registration = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/register',
        headers: { 'idempotency-key': 'logout-shape-register' },
        payload: { email: 'logout-shape@example.com' },
      });
      const cookie = String(registration.headers['set-cookie']);
      const unsupported = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/logout',
        headers: { cookie, 'idempotency-key': 'logout-shape-invalid' },
        payload: { account_id: registration.json().data.account_id },
      });
      expect(unsupported.statusCode).toBe(422);

      const valid = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/logout',
        headers: { cookie, 'idempotency-key': 'logout-shape-valid' },
        payload: {},
      });
      expect(valid.statusCode).toBe(204);
      const replay = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/logout',
        headers: { cookie, 'idempotency-key': 'logout-shape-valid' },
      });
      expect(replay.statusCode).toBe(204);
    } finally {
      await app.close();
    }
  });
});
