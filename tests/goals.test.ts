import { describe, expect, it } from 'vitest';
import { SliceStore } from '../packages/app-core/src/index.js';
import { buildApp } from '../apps/api/src/app.js';

const validGoal = {
  wellness_area: 'sleep',
  title: 'Improve my sleep routine',
  description: 'Build a consistent bedtime routine',
  start_date: '2026-10-01',
  end_date: '2026-11-01',
};

async function register(app: ReturnType<typeof buildApp>, email: string, key: string) {
  const response = await app.inject({
    method: 'POST',
    url: '/api/v1/auth/register',
    headers: { 'idempotency-key': key },
    payload: { email },
  });
  expect(response.statusCode).toBe(201);
  return {
    cookie: String(response.headers['set-cookie']),
    accountId: response.json().data.account_id as string,
  };
}

function data<T>(response: { json(): { data: T } }): T {
  return response.json().data;
}

describe('goal domain validation and development storage', () => {
  it('creates and reads an owned wellness goal with bounded lifecycle fields', () => {
    const store = new SliceStore('test');
    const goal = store.createGoal('account-a', {
      wellnessArea: 'movement',
      title: 'Walk regularly',
      startDate: '2026-10-01',
    });
    expect(goal).toMatchObject({
      accountId: 'account-a',
      wellnessArea: 'movement',
      title: 'Walk regularly',
      status: 'active',
    });
    expect(store.goal('account-a', goal.id)).toEqual(goal);
    expect(store.goal('account-b', goal.id)).toBeNull();
  });

  it.each([
    [{ wellnessArea: 'diagnosis', title: 'Sleep better', startDate: '2026-10-01' }, 'wellnessArea'],
    [{ wellnessArea: 'sleep', startDate: '2026-10-01' }, 'title'],
    [{ wellnessArea: 'sleep', title: '   ', startDate: '2026-10-01' }, 'title'],
    [{ wellnessArea: 'sleep', title: 'x'.repeat(161), startDate: '2026-10-01' }, 'title'],
    [
      {
        wellnessArea: 'sleep',
        title: 'Sleep better',
        description: 'x'.repeat(2001),
        startDate: '2026-10-01',
      },
      'description',
    ],
    [{ wellnessArea: 'sleep', title: 'Sleep better', startDate: '2026-02-30' }, 'startDate'],
    [
      {
        wellnessArea: 'sleep',
        title: 'Sleep better',
        startDate: '2026-10-02',
        endDate: '2026-10-01',
      },
      'endDate',
    ],
    [
      {
        wellnessArea: 'sleep',
        title: 'Sleep better',
        startDate: '2026-10-01',
        status: 'unknown',
      },
      'status',
    ],
    [
      {
        wellnessArea: 'sleep',
        title: 'Sleep better',
        startDate: '2026-10-01',
        status: 'deleted',
      },
      'status',
    ],
  ] as const)('rejects invalid goal fields before storage', (input, field) => {
    const store = new SliceStore('test');
    let error: unknown;
    try {
      store.createGoal('account-a', input);
    } catch (caught) {
      error = caught;
    }
    expect(error).toMatchObject({ field });
    expect(store.listGoals('account-a')).toEqual([]);
  });

  it.each([
    'Start insulin at 5 units nightly',
    'Increase my medication dosage',
    'Stop taking prescribed medicine',
    'Treat my diabetes with this plan',
    'Diagnose my symptoms through this goal',
  ])('rejects prohibited clinical goal text atomically: %s', (title) => {
    const store = new SliceStore('test');
    const safe = store.createGoal('account-a', {
      wellnessArea: 'sleep',
      title: 'Improve my sleep routine',
      startDate: '2026-10-01',
    });
    expect(() => store.updateGoal('account-a', safe.id, { title })).toThrow();
    expect(store.goal('account-a', safe.id)?.title).toBe('Improve my sleep routine');
  });

  it.each([
    'Drink more water',
    'Walk regularly',
    'Eat more vegetables',
    'Practice relaxation',
    'Build a consistent breakfast routine',
  ])('accepts ordinary wellness goal text: %s', (title) => {
    const store = new SliceStore('test');
    expect(
      store.createGoal('account-a', {
        wellnessArea: 'routine',
        title,
        startDate: '2026-10-01',
      }).title,
    ).toBe(title);
  });
});

describe('goal API contract, ownership, idempotency, and lifecycle', () => {
  it('denies unauthenticated access and returns private success envelopes with correlated request IDs', async () => {
    const app = buildApp();
    try {
      const denied = await app.inject({ method: 'GET', url: '/api/v1/me/goals' });
      expect(denied.statusCode).toBe(401);
      expect(denied.headers['cache-control']).toBe('no-store');
      expect(denied.json().error.request_id).toBe(denied.headers['x-request-id']);

      const user = await register(app, 'goal-contract@example.com', 'goal-contract-register');
      const listed = await app.inject({
        method: 'GET',
        url: '/api/v1/me/goals',
        headers: { cookie: user.cookie },
      });
      expect(listed.statusCode).toBe(200);
      expect(listed.headers['cache-control']).toBe('private, no-store');
      expect(listed.json()).toMatchObject({
        data: { items: [] },
        meta: { request_id: listed.headers['x-request-id'], next_cursor: null },
        warnings: [],
      });
    } finally {
      await app.close();
    }
  });

  it('creates, lists, reads, edits, archives, and soft-deletes goals using snake_case projections', async () => {
    const app = buildApp();
    try {
      const user = await register(app, 'goal-crud@example.com', 'goal-crud-register');
      const headers = { cookie: user.cookie, 'idempotency-key': 'goal-create-1' };
      const created = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers,
        payload: validGoal,
      });
      expect(created.statusCode).toBe(201);
      expect(created.headers['cache-control']).toBe('private, no-store');
      expect(created.json().meta.request_id).toBe(created.headers['x-request-id']);
      const goal = data<{ goal_id: string; title: string; status: string; account_id: string }>(
        created,
      );
      expect(goal).toMatchObject({
        title: validGoal.title,
        status: 'active',
        account_id: user.accountId,
      });
      expect(created.json().data).not.toHaveProperty('accountId');

      const read = await app.inject({
        method: 'GET',
        url: `/api/v1/me/goals/${goal.goal_id}`,
        headers: { cookie: user.cookie },
      });
      expect(read.statusCode).toBe(200);
      expect(data(read)).toEqual(goal);

      const listed = await app.inject({
        method: 'GET',
        url: '/api/v1/me/goals?status=active&wellness_area=sleep',
        headers: { cookie: user.cookie },
      });
      expect(data<{ items: unknown[] }>(listed).items).toHaveLength(1);

      const edited = await app.inject({
        method: 'PATCH',
        url: `/api/v1/me/goals/${goal.goal_id}`,
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-patch-1' },
        payload: { title: 'Build a steady sleep routine', status: 'paused', end_date: '' },
      });
      expect(edited.statusCode).toBe(200);
      expect(data<{ title: string; status: string; end_date?: string }>(edited)).toMatchObject({
        title: 'Build a steady sleep routine',
        status: 'paused',
      });
      expect(data(edited)).not.toHaveProperty('end_date');

      const archived = await app.inject({
        method: 'PATCH',
        url: `/api/v1/me/goals/${goal.goal_id}`,
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-archive-1' },
        payload: { status: 'archived' },
      });
      expect(archived.statusCode).toBe(200);
      expect(data<{ status: string }>(archived).status).toBe('archived');

      const deleted = await app.inject({
        method: 'DELETE',
        url: `/api/v1/me/goals/${goal.goal_id}`,
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-delete-1' },
      });
      expect(deleted.statusCode).toBe(204);
      expect(deleted.headers['cache-control']).toBe('private, no-store');
      expect(
        data<{ items: unknown[] }>(
          await app.inject({
            method: 'GET',
            url: '/api/v1/me/goals',
            headers: { cookie: user.cookie },
          }),
        ).items,
      ).toEqual([]);
      const deletedRead = await app.inject({
        method: 'GET',
        url: `/api/v1/me/goals/${goal.goal_id}`,
        headers: { cookie: user.cookie },
      });
      expect(deletedRead.statusCode).toBe(404);
      expect(deletedRead.json().error.code).toBe('not_found');
      expect(deletedRead.json().error.request_id).toBe(deletedRead.headers['x-request-id']);
      const secondDelete = await app.inject({
        method: 'DELETE',
        url: `/api/v1/me/goals/${goal.goal_id}`,
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-delete-2' },
      });
      expect(secondDelete.statusCode).toBe(404);
    } finally {
      await app.close();
    }
  });

  it('prevents cross-account read, edit, and delete without revealing existence', async () => {
    const app = buildApp();
    try {
      const owner = await register(app, 'goal-owner@example.com', 'goal-owner-register');
      const other = await register(app, 'goal-other@example.com', 'goal-other-register');
      const created = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers: { cookie: owner.cookie, 'idempotency-key': 'goal-owner-create' },
        payload: validGoal,
      });
      const goalId = data<{ goal_id: string }>(created).goal_id;
      for (const response of [
        await app.inject({
          method: 'GET',
          url: `/api/v1/me/goals/${goalId}`,
          headers: { cookie: other.cookie },
        }),
        await app.inject({
          method: 'PATCH',
          url: `/api/v1/me/goals/${goalId}`,
          headers: { cookie: other.cookie, 'idempotency-key': 'goal-other-edit' },
          payload: { title: 'My own goal' },
        }),
        await app.inject({
          method: 'DELETE',
          url: `/api/v1/me/goals/${goalId}`,
          headers: { cookie: other.cookie, 'idempotency-key': 'goal-other-delete' },
        }),
      ]) {
        expect(response.statusCode).toBe(404);
        expect(response.json().error.code).toBe('not_found');
        expect(response.body).not.toContain(goalId);
      }
      const stillOwned = await app.inject({
        method: 'GET',
        url: `/api/v1/me/goals/${goalId}`,
        headers: { cookie: owner.cookie },
      });
      expect(stillOwned.statusCode).toBe(200);
    } finally {
      await app.close();
    }
  });

  it('rejects owner overrides, malformed requests, unsafe text, and changed idempotency payloads atomically', async () => {
    const app = buildApp();
    try {
      const user = await register(app, 'goal-validation@example.com', 'goal-validation-register');
      const headers = { cookie: user.cookie, 'idempotency-key': 'goal-validation-create' };
      const created = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers,
        payload: validGoal,
      });
      const original = data<{ goal_id: string }>(created);
      const unsafe = await app.inject({
        method: 'PATCH',
        url: `/api/v1/me/goals/${original.goal_id}`,
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-unsafe-update' },
        payload: { title: 'Increase my medication dosage' },
      });
      expect(unsafe.statusCode).toBe(422);
      expect(unsafe.json().error.code).toBe('unsafe_input');
      expect(unsafe.body).not.toContain('Increase my medication dosage');
      expect(unsafe.json().error.request_id).toBe(unsafe.headers['x-request-id']);

      const unchanged = await app.inject({
        method: 'GET',
        url: `/api/v1/me/goals/${original.goal_id}`,
        headers: { cookie: user.cookie },
      });
      expect(data<{ title: string }>(unchanged).title).toBe(validGoal.title);

      const ownerOverride = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-owner-override' },
        payload: { ...validGoal, account_id: 'attacker-account' },
      });
      expect(ownerOverride.statusCode).toBe(422);
      expect(ownerOverride.body).not.toContain('attacker-account');

      const invalidDate = await app.inject({
        method: 'PATCH',
        url: `/api/v1/me/goals/${original.goal_id}`,
        headers: { cookie: user.cookie, 'idempotency-key': 'goal-invalid-date' },
        payload: { end_date: '2026-02-30' },
      });
      expect(invalidDate.statusCode).toBe(422);

      const changedRetry = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers,
        payload: { ...validGoal, title: 'A different retry payload' },
      });
      expect(changedRetry.statusCode).toBe(409);
      expect(changedRetry.json().error.code).toBe('idempotency_key_reused');
      expect(
        data<{ items: unknown[] }>(
          await app.inject({
            method: 'GET',
            url: '/api/v1/me/goals',
            headers: { cookie: user.cookie },
          }),
        ).items,
      ).toHaveLength(1);
    } finally {
      await app.close();
    }
  });

  it('replays exact create retries once and paginates in stable order', async () => {
    const app = buildApp();
    try {
      const user = await register(app, 'goal-retry@example.com', 'goal-retry-register');
      const headers = { cookie: user.cookie, 'idempotency-key': 'goal-exact-retry' };
      const first = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers,
        payload: validGoal,
      });
      const retry = await app.inject({
        method: 'POST',
        url: '/api/v1/me/goals',
        headers,
        payload: validGoal,
      });
      expect(retry.statusCode).toBe(201);
      expect(retry.json().data).toEqual(first.json().data);

      for (let index = 0; index < 2; index += 1) {
        await app.inject({
          method: 'POST',
          url: '/api/v1/me/goals',
          headers: { cookie: user.cookie, 'idempotency-key': `goal-page-${index}` },
          payload: { ...validGoal, title: `Goal ${index}` },
        });
      }
      const pageOne = await app.inject({
        method: 'GET',
        url: '/api/v1/me/goals?limit=2',
        headers: { cookie: user.cookie },
      });
      expect(data<{ items: unknown[] }>(pageOne).items).toHaveLength(2);
      const cursor = pageOne.json().meta.next_cursor;
      expect(typeof cursor).toBe('string');
      const pageTwo = await app.inject({
        method: 'GET',
        url: `/api/v1/me/goals?limit=2&cursor=${encodeURIComponent(cursor)}`,
        headers: { cookie: user.cookie },
      });
      expect(data<{ items: unknown[] }>(pageTwo).items).toHaveLength(1);
      expect(pageTwo.json().meta.next_cursor).toBeNull();
    } finally {
      await app.close();
    }
  });
});
