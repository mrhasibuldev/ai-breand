import { createHash } from 'node:crypto';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { Principal, SessionIdentityAdapter } from '../packages/auth-core/src/index.js';
import { SliceStore } from '../packages/app-core/src/index.js';
import { evaluateWellnessFreeText } from '../packages/safety-core/src/index.js';
import { buildApp } from '../apps/api/src/app.js';

afterEach(() => vi.unstubAllEnvs());

const prohibited = [
  'Diagnose my fatigue',
  'My diagnosis is depression',
  'You have diabetes',
  'I have asthma',
  'Do I have cancer?',
  'I have bipolar disorder',
  'Prescribe something for sleep',
  'Take 20 mg every night',
  'Take two tablets daily',
  'Take one aspirin every morning',
  'Start insulin at five units nightly',
  'Take 2 g of amoxicillin twice daily',
  'Take naproxen every morning',
  'Take an antibiotic after dinner',
  'Administer five units nightly',
  'Start two grams every evening',
  'Take 0.5 g twice daily',
  'Take one ASPIRIN every morning',
  'Take one as\u200Bpirin every morning',
  'Take metformin at bedtime',
  'Take one cetirizine daily',
  'Take warfarin with dinner',
  'Use five units nightly',
  'Use 2 g of flucloxacillin daily',
  'Start metformin every evening',
  'Increase cetirizine to two each night',
  'Decrease warfarin to one every evening',
  'Use warfarin every evening',
  'Start prednisone each morning',
  'Five units nightly',
  'Use 2 g each morning',
  'Use twenty units nightly',
  'Start sertraline every evening',
  'Start sertraline every other morning',
  'Decrease loratadine to two each morning',
  'Take 5 mg of an unknown substance with water daily',
  'Take water daily and use five units nightly',
  'Use five units nightly then drink water',
  'Take water; start sertraline every evening',
  'Take water and loratadine daily',
  'Drink 20 ml of loratadine with water daily',
  'Eat 2 g of amoxicillin daily',
  'Drink five units nightly',
  'Drink 5 mg of an unknown substance every evening',
  'Take 2 g of an unknown substance after exercise',
  'Inject 10 units nightly',
  'Increase the dosage',
  'I take medication for sleep',
  'Tell me which disease I have',
  'Perform medical triage',
  'Guarantee a cure',
  'Replace my doctor',
  'Act as my therapist',
  'Monitor my emergency',
  'Ｄｉａｇｎｏｓｅ my condition',
  'Pre\u200Bscribe a drug',
  'Change my\nmedication dosage',
];

describe('HIGH #4 bounded wellness storage policy', () => {
  it.each(prohibited)(
    'rejects clinical input case %# atomically without echoing it',
    async (text) => {
      const app = buildApp();
      try {
        const registration = await app.inject({
          method: 'POST',
          url: '/api/v1/auth/register',
          headers: { 'idempotency-key': 'safety-registration' },
          payload: { email: 'synthetic-safety@example.com' },
        });
        const headers = { cookie: String(registration.headers['set-cookie']) };
        const initial = await app.inject({
          method: 'PATCH',
          url: '/api/v1/me/wellness-profile',
          headers,
          payload: { wellness_areas: ['sleep'], coaching_style: 'Gentle encouragement' },
        });
        expect(initial.statusCode).toBe(200);
        const rejected = await app.inject({
          method: 'PATCH',
          url: '/api/v1/me/wellness-profile',
          headers,
          payload: { wellness_areas: ['movement'], coaching_style: text },
        });
        expect(rejected.statusCode).toBe(422);
        expect(rejected.headers['cache-control']).toBe('no-store');
        expect(rejected.json()).toEqual({
          error: {
            code: 'unsafe_input',
            message: 'Clinical content cannot be stored in a wellness profile',
            details: [{ field: 'coaching_style', issue: 'prohibited_clinical_content' }],
            request_id: rejected.headers['x-request-id'],
            retryable: false,
          },
        });
        expect(rejected.body).not.toContain(text);
        const stored = await app.inject({
          method: 'GET',
          url: '/api/v1/me/wellness-profile',
          headers,
        });
        expect(stored.json().data).toEqual(initial.json().data);
      } finally {
        await app.close();
      }
    },
  );

  it.each([
    'Gentle encouragement for consistent sleep',
    'Practical movement and hydration reminders',
    'Help me reflect on stress without judgment',
    'Small steps for mindfulness and balanced meals',
    'I want to sleep better.',
    'I want to exercise more.',
    'I want healthier eating habits.',
    'I feel stressed and want relaxation techniques.',
    'Take a walk every morning',
    'Take two breaths every morning',
    'Take a break after lunch',
    'Start with five minutes of gentle stretching nightly',
    'Drink 200 ml of water after exercise',
    'Take 200 ml of water after exercise',
    'Increase fruit to 200 g daily',
    'Eat 200 g of fruit daily',
    'Drink water throughout the day',
    'Improve sleep consistency',
    'Exercise three times per week',
    'Eat more vegetables',
    'Reduce sugary drinks',
    'Practice relaxation before sleep',
    'Track daily hydration',
    'Decrease fruit to 100 g every evening',
    'Use 5 kg weights daily',
    'Track five units of hydration daily',
    'Take 200 ml of water and increase fruit to 200 g daily',
    'I prefer 100 g of oats for breakfast',
    'Take breakfast every morning',
    'Use relaxation every evening',
    'Increase daily hydration',
    'Start a consistent sleep schedule every night',
    'Take a healthy snack each evening',
    'Use water bottles daily',
    'Increase physical activity daily',
    'Start a daily walking routine',
    'Take a banana every morning',
    'Take water and fruit daily',
    'Use a treadmill every morning',
    'Start cycling every evening',
    'Take 200 g of avocado daily',
    'Use 200 ml of olive oil for cooking',
    'Take a morning walk daily',
    'Decrease screen time every evening',
    'Increase water intake to 250 ml daily',
    'Take 200 ml of water daily and 200 g of fruit each evening',
    'Take care of each other',
    'Use each opportunity for relaxation',
    'Take a brisk walk every morning',
    'Drink 200 ml of orange juice daily',
    'Eat 200 g of quinoa daily',
    'Eat 250 g of broccoli daily',
    'Drink 200 ml of a herbal infusion every morning',
    'Take 200 ml of warm water daily',
    'Use gentle encouragement every day',
    'Use an upbeat tone daily',
    'ml',
    'g',
    'kg',
    'units',
    'daily',
    'weekly',
    'morning',
    'evening',
    'increase',
    'decrease',
    'take',
  ])('accepts wellness content case %# through the API and reads it back', async (text) => {
    expect(evaluateWellnessFreeText(text).allowed).toBe(true);
    const app = buildApp();
    try {
      const registration = await app.inject({
        method: 'POST',
        url: '/api/v1/auth/register',
        headers: { 'idempotency-key': 'wellness-registration' },
        payload: { email: 'wellness@example.com' },
      });
      const headers = { cookie: String(registration.headers['set-cookie']) };
      const saved = await app.inject({
        method: 'PATCH',
        url: '/api/v1/me/wellness-profile',
        headers,
        payload: { wellness_areas: ['routine'], coaching_style: text },
      });
      expect(saved.statusCode).toBe(200);
      expect(saved.headers['cache-control']).toBe('private, no-store');
      expect(saved.json().meta.request_id).toBe(saved.headers['x-request-id']);
      const stored = await app.inject({
        method: 'GET',
        url: '/api/v1/me/wellness-profile',
        headers,
      });
      expect(stored.statusCode).toBe(200);
      expect(stored.json().data.coaching_style).toBe(text);
    } finally {
      await app.close();
    }
  });

  it('also enforces the policy on direct repository writes', () => {
    const store = new SliceStore('test');
    expect(() =>
      store.updateWellness('synthetic-account', { coachingStyle: prohibited[0]! }),
    ).toThrow('Clinical content cannot be stored');
    expect(store.wellnessProfile('synthetic-account').coachingStyle).toBeUndefined();
  });
});

describe('HIGH #5 development data boundary', () => {
  it.each(['production', 'staging', ''])('rejects store environment %s', (environment) => {
    expect(() => new SliceStore(environment)).toThrow('development/test-only');
  });

  it('cannot override a production process with development options', () => {
    vi.stubEnv('NODE_ENV', 'production');
    expect(() => new SliceStore()).toThrow('development/test-only');
    expect(() => new SliceStore('development')).toThrow('development/test-only');
    expect(() => buildApp({ env: { NODE_ENV: 'development' } })).toThrow('development/test-only');
  });

  it('refuses reads and writes from an existing store when the process becomes production', () => {
    const store = new SliceStore('test');
    const account = store.createAccount('synthetic@example.com');
    vi.stubEnv('NODE_ENV', 'production');
    for (const operation of [
      () => store.createAccount('another@example.com'),
      () => store.findAccountByEmail('synthetic@example.com'),
      () => store.account(account.id),
      () => store.profile(account.id),
      () => store.updateProfile(account.id, { displayName: 'Test' }),
      () => store.wellnessProfile(account.id),
      () => store.updateWellness(account.id, { wellnessAreas: ['sleep'] }),
      () => store.consentsFor(account.id),
      () =>
        store.addConsent(account.id, {
          consentType: 'memory',
          policyVersion: 'memory-foundation-v1',
          decision: 'denied',
          captureSource: 'onboarding',
        }),
      () => store.onboarding(account.id),
    ])
      expect(operation).toThrow('development/test-only');
  });

  it.each([undefined, 'postgresql://unavailable.invalid/nexusai'])(
    'fails production startup with URL case %# even with an external identity',
    (url) => {
      const identity = providerAdapter();
      expect(() =>
        buildApp({
          identity,
          env: {
            NODE_ENV: 'production',
            ...(url ? { DATABASE_URL: url } : {}),
          },
        }),
      ).toThrow();
      expect(identity.resolvePrincipal).not.toHaveBeenCalled();
    },
  );

  it.each(['development', 'test'])('preserves %s readiness', async (environment) => {
    const app = buildApp({ env: { NODE_ENV: environment } });
    try {
      expect((await app.inject('/health/ready')).statusCode).toBe(200);
    } finally {
      await app.close();
    }
  });
});

function providerAdapter() {
  const revoked = new Set<string>();
  const credential = (request: unknown) =>
    (request as { headers: Record<string, string | undefined> }).headers['x-test-session'];
  return {
    logoutReplayScope: async (request: unknown) => {
      const token = credential(request);
      return token ? createHash('sha256').update(token).digest('hex') : null;
    },
    resolvePrincipal: vi.fn(async (request: unknown): Promise<Principal | null> => {
      const token = credential(request);
      return token && ['one', 'two'].includes(token) && !revoked.has(token)
        ? {
            accountId: `account-${token}`,
            sessionId: token,
            actorType: 'user',
            assuranceLevel: 'authenticated',
          }
        : null;
    }),
    logout: vi.fn(async (principal: Principal) => {
      revoked.add(principal.sessionId!);
    }),
  } satisfies SessionIdentityAdapter;
}

describe('HIGH #6 provider-neutral logout', () => {
  it('isolates sessions sharing a key, replays revocation, and denies missing/invalid sessions', async () => {
    const identity = providerAdapter();
    const app = buildApp({ identity });
    const logout = (token?: string, key = 'shared-key') =>
      app.inject({
        method: 'POST',
        url: '/api/v1/auth/logout',
        headers: { 'idempotency-key': key, ...(token ? { 'x-test-session': token } : {}) },
      });
    try {
      const [first, concurrent] = await Promise.all([logout('one'), logout('one')]);
      expect(first.statusCode).toBe(204);
      expect(concurrent.statusCode).toBe(204);
      expect((await logout('two')).statusCode).toBe(204);
      expect((await logout('one')).statusCode).toBe(204);
      expect(identity.logout).toHaveBeenCalledTimes(2);
      expect(first.body).toBe('');
      expect(first.headers['set-cookie']).toBeUndefined();
      expect(first.headers['cache-control']).toBe('private, no-store');
      expect(first.headers['x-request-id']).toBeTruthy();
      for (const response of [
        await logout(),
        await logout('invalid'),
        await logout('one', 'new-key'),
      ]) {
        expect(response.statusCode).toBe(401);
        expect(response.json().error).toMatchObject({
          code: 'unauthenticated',
          request_id: response.headers['x-request-id'],
        });
        expect(response.headers['cache-control']).toBe('no-store');
      }
    } finally {
      await app.close();
    }
  });

  it.each([
    { accountId: 'a', actorType: 'user', assuranceLevel: 'authenticated' },
    { accountId: 'a', sessionId: 's', actorType: 'guest', assuranceLevel: 'anonymous' },
    { accountId: 'a', sessionId: 's', actorType: 'user', assuranceLevel: 'anonymous' },
  ] as Principal[])(
    'rejects an incomplete or unauthenticated principal case %#',
    async (principal) => {
      const identity = providerAdapter();
      identity.resolvePrincipal.mockResolvedValue(principal);
      const app = buildApp({ identity });
      try {
        const result = await app.inject({
          method: 'POST',
          url: '/api/v1/auth/logout',
          headers: { 'x-test-session': 'one', 'idempotency-key': 'invalid-principal' },
        });
        expect(result.statusCode).toBe(401);
        expect(identity.logout).not.toHaveBeenCalled();
      } finally {
        await app.close();
      }
    },
  );

  it('does not cache a failed revocation or expose provider error contents', async () => {
    const identity = providerAdapter();
    identity.logout.mockRejectedValueOnce(new Error('private provider failure'));
    const app = buildApp({ identity });
    const request = {
      method: 'POST' as const,
      url: '/api/v1/auth/logout',
      headers: { 'x-test-session': 'one', 'idempotency-key': 'failure-retry' },
    };
    try {
      const result = await app.inject(request);
      expect(result.statusCode).toBe(503);
      expect(result.json().error.code).toBe('auth_dependency_unavailable');
      expect(result.body).not.toContain('private provider failure');
      expect(result.headers['set-cookie']).toBeUndefined();
      expect((await app.inject(request)).statusCode).toBe(204);
      expect(identity.logout).toHaveBeenCalledTimes(2);
    } finally {
      await app.close();
    }
  });

  it('passes the adapter-owned cookie clearance through the response and exact replay', async () => {
    const base = providerAdapter();
    const identity: SessionIdentityAdapter = {
      ...base,
      logout: async (principal) => {
        await base.logout(principal);
        return { clearSessionCookie: 'external_session=; Path=/; HttpOnly; Max-Age=0' };
      },
    };
    const app = buildApp({ identity });
    const request = {
      method: 'POST' as const,
      url: '/api/v1/auth/logout',
      headers: { 'x-test-session': 'one', 'idempotency-key': 'clear-cookie' },
    };
    try {
      const first = await app.inject(request);
      const replay = await app.inject(request);
      expect(first.statusCode).toBe(204);
      expect(replay.statusCode).toBe(204);
      expect(first.headers['set-cookie']).toBe('external_session=; Path=/; HttpOnly; Max-Age=0');
      expect(replay.headers['set-cookie']).toBe(first.headers['set-cookie']);
      expect(base.logout).toHaveBeenCalledTimes(1);
    } finally {
      await app.close();
    }
  });
});
