import { describe, expect, it } from 'vitest';
import { buildApp } from '../apps/api/src/app.js';

describe('Final HIGH #2 public API regressions', () => {
  it.each(['/api/v1/not-an-operation', '/api/v1/me/not-an-operation'])(
    'returns the normative not-found error for %s',
    async (url) => {
      const app = buildApp();
      try {
        const response = await app.inject({
          method: 'GET',
          url,
          headers: { 'x-request-id': 'untrusted-client-id' },
        });
        expect(response.statusCode).toBe(404);
        expect(response.headers['cache-control']).toBe('no-store');
        expect(response.headers['x-request-id']).toEqual(expect.any(String));
        expect(response.headers['x-request-id']).not.toBe('untrusted-client-id');
        expect(response.json()).toEqual({
          error: {
            code: 'not_found',
            message: 'Resource not found',
            request_id: response.headers['x-request-id'],
            retryable: false,
          },
        });
      } finally {
        await app.close();
      }
    },
  );

  it('accepts only the approved consent fields and replays across onboarding completion', async () => {
    const app = buildApp();
    try {
      const registration = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/register',
        headers: { 'idempotency-key': 'final-contract-register' },
        payload: { email: 'final-contract@example.com' },
      });
      const headers = { cookie: String(registration.headers['set-cookie']) };
      for (const [url, payload] of [
        ['/api/v1/me/profile', { display_name: 'Tester', locale: 'en-US', timezone: 'UTC' }],
        ['/api/v1/me/wellness-profile', { wellness_areas: ['sleep'] }],
      ] as const) {
        expect((await app.inject({ method: 'PATCH', url, headers, payload })).statusCode).toBe(200);
      }
      const payload = {
        consent_type: 'memory',
        policy_version: 'memory-foundation-v1',
        decision: 'denied',
      };
      const request = {
        method: 'POST' as const,
        url: '/api/v1/me/consents',
        headers: { ...headers, 'idempotency-key': 'final-consent' },
        payload,
      };
      const first = await app.inject(request);
      expect(first.statusCode).toBe(201);
      expect(first.headers['cache-control']).toBe('private, no-store');
      expect(first.json()).toEqual({
        data: {
          ...payload,
          id: expect.any(String),
          account_id: registration.json().data.account_id,
          capture_source: 'onboarding',
          captured_at: expect.any(String),
        },
        meta: { request_id: first.headers['x-request-id'] },
        warnings: [],
      });
      const account = await app.inject({ method: 'GET', url: '/api/v1/me', headers });
      expect(account.json().data.onboarding.complete).toBe(true);
      const replay = await app.inject(request);
      expect(replay.statusCode).toBe(201);
      expect(replay.json().data).toEqual(first.json().data);
      expect(replay.json().meta.request_id).toBe(replay.headers['x-request-id']);
      const changed = await app.inject({
        ...request,
        payload: { ...payload, decision: 'granted' },
      });
      expect(changed.statusCode).toBe(409);
      expect(changed.json().error.code).toBe('idempotency_key_reused');
      const history = await app.inject({ method: 'GET', url: '/api/v1/me/consents', headers });
      expect(history.json().data.items).toEqual([first.json().data]);
      const settings = await app.inject({
        ...request,
        headers: { ...headers, 'idempotency-key': 'settings-consent' },
        payload: { ...payload, decision: 'granted' },
      });
      expect(settings.statusCode).toBe(201);
      expect(settings.json().data.capture_source).toBe('settings');
      const spoofed = await app.inject({
        ...request,
        headers: { ...headers, 'idempotency-key': 'spoofed-source' },
        payload: { ...payload, capture_source: 'onboarding' },
      });
      expect(spoofed.statusCode).toBe(422);
    } finally {
      await app.close();
    }
  });

  it.each([
    'I want to sleep better.',
    'I want to exercise more.',
    'I want healthier eating habits.',
    'I feel stressed and want relaxation techniques.',
  ])('stores legitimate wellness text through the API, case %#', async (text) => {
    const app = buildApp();
    try {
      const registration = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/register',
        headers: { 'idempotency-key': 'wellness-register' },
        payload: { email: 'wellness-contract@example.com' },
      });
      const headers = { cookie: String(registration.headers['set-cookie']) };
      const saved = await app.inject({
        method: 'PATCH',
        url: '/api/v1/me/wellness-profile',
        headers,
        payload: { wellness_areas: ['sleep'], coaching_style: text },
      });
      expect(saved.statusCode).toBe(200);
      expect(saved.headers['cache-control']).toBe('private, no-store');
      expect(saved.json().meta.request_id).toBe(saved.headers['x-request-id']);
      const stored = await app.inject({
        method: 'GET',
        url: '/api/v1/me/wellness-profile',
        headers,
      });
      expect(stored.json().data.coaching_style).toBe(text);
    } finally {
      await app.close();
    }
  });
});
