import { describe, expect, it } from 'vitest';
import type { FastifyInstance } from 'fastify';
import { buildApp } from '../apps/api/src/app.js';
import type { Principal, SessionIdentityAdapter } from '../packages/auth-core/src/index.js';

type InjectedResponse = Awaited<ReturnType<FastifyInstance['inject']>>;

function responseData<T>(response: InjectedResponse): T {
  return response.json().data as T;
}

async function register(app: FastifyInstance, email: string, key: string) {
  return app.inject({
    method: 'POST',
    url: '/api/v1/auth/register',
    headers: { 'idempotency-key': key },
    payload: { email },
  });
}

const deniedConsent = {
  consent_type: 'memory',
  policy_version: 'memory-foundation-v1',
  decision: 'denied',
};

describe('Phase 13 Part 1 API slice', () => {
  it('uses the Phase 07 envelope, snake_case, server request ID and no-store contract', async () => {
    const app = buildApp();
    const denied = await app.inject({
      method: 'GET',
      url: '/api/v1/me/profile',
      headers: { 'x-request-id': 'client-controlled-id' },
    });
    const deniedBody = denied.json();

    expect(denied.statusCode).toBe(401);
    expect(denied.headers['cache-control']).toBe('no-store');
    expect(deniedBody).toEqual({
      error: {
        code: 'unauthenticated',
        message: 'Authentication is required',
        request_id: denied.headers['x-request-id'],
        retryable: false,
      },
    });
    expect(deniedBody.error.request_id).not.toBe('client-controlled-id');

    const registered = await register(app, 'contract@example.com', 'contract-register');
    const registeredBody = registered.json();
    expect(registered.statusCode).toBe(201);
    expect(registered.headers['cache-control']).toBe('private, no-store');
    expect(registeredBody).toMatchObject({
      data: { authenticated: true },
      meta: { request_id: registered.headers['x-request-id'] },
      warnings: [],
    });
    expect(registeredBody.data.account_id).toEqual(expect.any(String));
    expect(registeredBody.data).not.toHaveProperty('accountId');

    const profile = await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/profile',
      headers: { cookie: String(registered.headers['set-cookie']) },
      payload: { display_name: 'Ava', locale: 'en-US', timezone: 'UTC' },
    });
    expect(profile.statusCode).toBe(200);
    expect(profile.headers['cache-control']).toBe('private, no-store');
    expect(profile.json()).toMatchObject({
      data: { display_name: 'Ava', locale: 'en-US' },
      meta: { request_id: profile.headers['x-request-id'] },
      warnings: [],
    });
    expect(profile.json().data).not.toHaveProperty('displayName');
  });

  it('rejects non-contract request field names with structured validation details', async () => {
    const app = buildApp();
    const registered = await register(app, 'validation@example.com', 'validation-register');
    const response = await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/profile',
      headers: { cookie: String(registered.headers['set-cookie']) },
      payload: { displayName: 'Not snake case' },
    });

    expect(response.statusCode).toBe(422);
    expect(response.json()).toMatchObject({
      error: {
        code: 'validation_failed',
        details: [{ field: 'display_name', issue: 'invalid_value' }],
        request_id: response.headers['x-request-id'],
        retryable: false,
      },
    });
  });

  it('records an explicit memory choice before onboarding completes', async () => {
    const app = buildApp();
    const registered = await register(app, 'choice@example.com', 'register-choice');
    const headers = { cookie: String(registered.headers['set-cookie']) };
    await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/profile',
      headers,
      payload: { display_name: 'Choice', locale: 'en-US', timezone: 'UTC' },
    });
    await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/wellness-profile',
      headers,
      payload: { wellness_areas: ['sleep'] },
    });
    expect(
      responseData<{ onboarding: { complete: boolean } }>(
        await app.inject({ method: 'GET', url: '/api/v1/me', headers }),
      ).onboarding.complete,
    ).toBe(false);
    await app.inject({
      method: 'POST',
      url: '/api/v1/me/consents',
      headers: { ...headers, 'idempotency-key': 'choice-1' },
      payload: deniedConsent,
    });
    expect(
      responseData<{
        onboarding: { complete: boolean; consent_choices_recorded: boolean };
      }>(await app.inject({ method: 'GET', url: '/api/v1/me', headers })).onboarding,
    ).toMatchObject({ complete: true, consent_choices_recorded: true });
  });

  it('rejects invalid wellness data and prevents account ownership overrides', async () => {
    const app = buildApp();
    const a = await register(app, 'a@example.com', 'register-a');
    const b = await register(app, 'b@example.com', 'register-b');
    const aData = responseData<{ account_id: string }>(a);
    const bData = responseData<{ account_id: string }>(b);
    const invalid = await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/wellness-profile',
      headers: { cookie: String(a.headers['set-cookie']) },
      payload: { wellness_areas: ['diagnosis'] },
    });
    expect(invalid.statusCode).toBe(422);
    const attemptedOwnershipOverride = await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/profile',
      headers: { cookie: String(a.headers['set-cookie']) },
      payload: { display_name: 'A', account_id: bData.account_id },
    });
    expect(attemptedOwnershipOverride.statusCode).toBe(422);
    await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/profile',
      headers: { cookie: String(a.headers['set-cookie']) },
      payload: { display_name: 'A', locale: 'en-US', timezone: 'UTC' },
    });
    await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/profile',
      headers: { cookie: String(b.headers['set-cookie']) },
      payload: { display_name: 'Bee', locale: 'en-US', timezone: 'UTC' },
    });
    const aMe = responseData<{ account: { id: string; email: string } }>(
      await app.inject({
        method: 'GET',
        url: '/api/v1/me',
        headers: { cookie: String(a.headers['set-cookie']) },
      }),
    );
    expect(aMe.account.id).toBe(aData.account_id);
    expect(aMe.account.email).toBe('a@example.com');
    expect(aMe.account.email).not.toBe('b@example.com');
  });

  it('rejects prohibited clinical free text without persisting it', async () => {
    const app = buildApp();
    const registered = await register(app, 'safety@example.com', 'safety-register');
    const headers = { cookie: String(registered.headers['set-cookie']) };
    const legitimateStyle = 'Use gentle, practical encouragement for everyday routines';
    const legitimate = await app.inject({
      method: 'PATCH',
      url: '/api/v1/me/wellness-profile',
      headers,
      payload: { wellness_areas: ['sleep'], coaching_style: legitimateStyle },
    });
    expect(legitimate.statusCode).toBe(200);
    expect(responseData<{ coaching_style: string }>(legitimate).coaching_style).toBe(
      legitimateStyle,
    );

    const prohibited = [
      'Diagnose whether my fatigue is anemia',
      'Prescribe a treatment for my condition',
      'Change my medication dosage to 20 mg',
      'Perform clinical triage for these symptoms',
      'Call an ambulance for me',
    ];
    for (const coachingStyle of prohibited) {
      const blocked = await app.inject({
        method: 'PATCH',
        url: '/api/v1/me/wellness-profile',
        headers,
        payload: { coaching_style: coachingStyle },
      });
      expect(blocked.statusCode).toBe(422);
      expect(blocked.json()).toMatchObject({
        error: {
          code: 'unsafe_input',
          details: [{ field: 'coaching_style', issue: 'prohibited_clinical_content' }],
          retryable: false,
        },
      });
      expect(JSON.stringify(blocked.json())).not.toContain(coachingStyle);
    }

    const stored = await app.inject({
      method: 'GET',
      url: '/api/v1/me/wellness-profile',
      headers,
    });
    expect(responseData<{ coaching_style: string }>(stored).coaching_style).toBe(legitimateStyle);
  });

  it('logs out through a provider-neutral session identity adapter', async () => {
    const principal: Principal = {
      accountId: 'provider-account',
      actorType: 'user',
      sessionId: 'provider-session',
      assuranceLevel: 'authenticated',
    };
    let revoked = false;
    const identity: SessionIdentityAdapter = {
      logoutReplayScope: async (request) => {
        const headers = (request as { headers?: Record<string, unknown> }).headers ?? {};
        return typeof headers['x-provider-session'] === 'string'
          ? `test-scope:${headers['x-provider-session']}`
          : null;
      },
      resolvePrincipal: async (request) => {
        const headers = (request as { headers?: Record<string, unknown> }).headers ?? {};
        return headers['x-provider-session'] === 'valid' && !revoked ? principal : null;
      },
      logout: async (resolved) => {
        if (resolved.sessionId === principal.sessionId) revoked = true;
      },
    };
    const app = buildApp({ identity });
    const missing = await app.inject({
      method: 'POST',
      url: '/api/v1/auth/logout',
      headers: { 'idempotency-key': 'provider-missing-session' },
    });
    expect(missing.statusCode).toBe(401);
    expect(missing.json()).toMatchObject({
      error: { code: 'unauthenticated', retryable: false },
    });

    const loggedOut = await app.inject({
      method: 'POST',
      url: '/api/v1/auth/logout',
      headers: {
        'x-provider-session': 'valid',
        'idempotency-key': 'provider-logout',
      },
    });
    expect(loggedOut.statusCode).toBe(204);
    expect(revoked).toBe(true);

    const revokedSession = await app.inject({
      method: 'GET',
      url: '/api/v1/me/profile',
      headers: { 'x-provider-session': 'valid' },
    });
    expect(revokedSession.statusCode).toBe(401);
  });

  it('executes the first request for a valid idempotency key normally', async () => {
    const app = buildApp();
    const response = await register(app, 'first@example.com', 'first-request-key');
    expect(response.statusCode).toBe(201);
    expect(responseData<{ account_id: string }>(response).account_id).toEqual(expect.any(String));
  });

  it('replays the original registration result for an exact retry', async () => {
    const app = buildApp();
    const first = await register(app, 'replay@example.com', 'registration-replay');
    const replay = await register(app, 'replay@example.com', 'registration-replay');

    expect(replay.statusCode).toBe(201);
    expect(responseData(replay)).toEqual(responseData(first));
    expect(replay.headers['set-cookie']).toBe(first.headers['set-cookie']);
    expect(replay.headers['x-request-id']).not.toBe(first.headers['x-request-id']);
  });

  it('prevents duplicate side effects when identical requests arrive together', async () => {
    const app = buildApp();
    const [first, duplicate] = await Promise.all([
      register(app, 'concurrent@example.com', 'concurrent-registration'),
      register(app, 'concurrent@example.com', 'concurrent-registration'),
    ]);

    expect(first.statusCode).toBe(201);
    expect(duplicate.statusCode).toBe(201);
    expect(responseData(duplicate)).toEqual(responseData(first));
  });

  it('rejects the same key when the normalized payload changes', async () => {
    const app = buildApp();
    const first = await register(app, 'one@example.com', 'reused-key');
    const conflicting = await register(app, 'two@example.com', 'reused-key');

    expect(first.statusCode).toBe(201);
    expect(conflicting.statusCode).toBe(409);
    expect(conflicting.json()).toMatchObject({
      error: { code: 'idempotency_key_reused', retryable: false },
    });
  });

  it('scopes equivalent idempotency keys independently for different users', async () => {
    const app = buildApp();
    const a = await register(app, 'scope-a@example.com', 'scope-register-a');
    const b = await register(app, 'scope-b@example.com', 'scope-register-b');
    const sharedKey = 'equivalent-consent-key';
    const aConsent = await app.inject({
      method: 'POST',
      url: '/api/v1/me/consents',
      headers: {
        cookie: String(a.headers['set-cookie']),
        'idempotency-key': sharedKey,
      },
      payload: deniedConsent,
    });
    const bConsent = await app.inject({
      method: 'POST',
      url: '/api/v1/me/consents',
      headers: {
        cookie: String(b.headers['set-cookie']),
        'idempotency-key': sharedKey,
      },
      payload: deniedConsent,
    });

    expect(aConsent.statusCode).toBe(201);
    expect(bConsent.statusCode).toBe(201);
    expect(responseData<{ id: string }>(aConsent).id).not.toBe(
      responseData<{ id: string }>(bConsent).id,
    );
  });

  it('replays consent and does not append a duplicate record', async () => {
    const app = buildApp();
    const registered = await register(app, 'consent@example.com', 'consent-register');
    const headers = {
      cookie: String(registered.headers['set-cookie']),
      'idempotency-key': 'consent-replay',
    };
    const first = await app.inject({
      method: 'POST',
      url: '/api/v1/me/consents',
      headers,
      payload: deniedConsent,
    });
    const replay = await app.inject({
      method: 'POST',
      url: '/api/v1/me/consents',
      headers,
      payload: deniedConsent,
    });
    const list = await app.inject({
      method: 'GET',
      url: '/api/v1/me/consents',
      headers: { cookie: String(registered.headers['set-cookie']) },
    });

    expect(first.statusCode).toBe(201);
    expect(replay.statusCode).toBe(201);
    expect(responseData(replay)).toEqual(responseData(first));
    expect(responseData<{ items: unknown[] }>(list).items).toHaveLength(1);
  });

  it('replays the original login result without issuing another session', async () => {
    const app = buildApp();
    await register(app, 'login@example.com', 'login-register');
    const request = {
      method: 'POST' as const,
      url: '/api/v1/auth/login',
      headers: { 'idempotency-key': 'login-replay' },
      payload: { email: 'login@example.com' },
    };
    const first = await app.inject(request);
    const replay = await app.inject(request);

    expect(first.statusCode).toBe(200);
    expect(replay.statusCode).toBe(200);
    expect(responseData(replay)).toEqual(responseData(first));
    expect(replay.headers['set-cookie']).toBe(first.headers['set-cookie']);
  });

  it('replays an already completed logout safely', async () => {
    const app = buildApp();
    const registered = await register(app, 'logout@example.com', 'logout-register');
    const headers = {
      cookie: String(registered.headers['set-cookie']),
      'idempotency-key': 'logout-replay',
    };
    const first = await app.inject({
      method: 'POST',
      url: '/api/v1/auth/logout',
      headers,
    });
    const replay = await app.inject({
      method: 'POST',
      url: '/api/v1/auth/logout',
      headers,
    });

    expect(first.statusCode).toBe(204);
    expect(replay.statusCode).toBe(204);
  });
});
