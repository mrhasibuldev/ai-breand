import Fastify, { type FastifyInstance, type FastifyReply, type FastifyRequest } from 'fastify';
import cookie from '@fastify/cookie';
import cors from '@fastify/cors';
import { randomUUID } from 'node:crypto';
import { API_PREFIX, INTERNAL_PREFIX, apiError, apiSuccess } from '@nexusai/contracts';
import { readRuntimeConfig } from '@nexusai/config';
import type { SessionIdentityAdapter } from '@nexusai/auth-core';
import {
  DevAuthService,
  SliceStore,
  SliceValidationError,
  type ConsentRecord,
  type GoalInput,
  type GoalStatus,
  type OnboardingState,
  type SliceAccount,
  type UserProfile,
  type WellnessArea,
  type WellnessGoal,
  type WellnessProfile,
} from '@nexusai/app-core';
import { FoundationHttpError, requireInternalActor, resolvePrincipal } from './foundation.js';
import type { RateLimitBoundary } from './foundation.js';
import { authEmailRateKey, InMemoryAuthRateLimit } from './rate-limit.js';
import {
  IdempotencyKeyReusedError,
  InMemoryIdempotencyStore,
  type IdempotentResult,
} from './idempotency.js';

export async function buildApp(
  options: {
    readonly identity?: SessionIdentityAdapter;
    readonly env?: NodeJS.ProcessEnv;
    readonly rateLimit?: RateLimitBoundary;
  } = {},
): Promise<FastifyInstance> {
  const config = readRuntimeConfig(options.env ?? process.env);
  if (config.nodeEnv === 'production') {
    throw new Error(
      'Production persistent storage is unavailable; process-local user data storage is disabled',
    );
  }
  const store = new SliceStore(config.nodeEnv);
  const app = Fastify({ logger: false, genReqId: () => randomUUID() });

  // Register CORS for frontend credentials
  await app.register(cors, {
    origin: config.webOrigin || 'http://localhost:3000',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  });

  // Register cookie plugin for HTTP-only session cookies
  await app.register(cookie, {
    secret: options.env?.COOKIE_SECRET || process.env.COOKIE_SECRET || 'nexus-cookie-secret-change-in-production',
  });
  const idempotency = new InMemoryIdempotencyStore();
  const rateLimit = options.rateLimit ?? new InMemoryAuthRateLimit();
  const devAuth = new DevAuthService(store, config.nodeEnv);
  const identity = options.identity ?? devAuth;
  const requireUser = async (request: FastifyRequest) => {
    const principal = await resolvePrincipal(request, identity);
    if (
      !principal?.accountId ||
      principal.actorType !== 'user' ||
      principal.assuranceLevel === 'anonymous'
    )
      throw new FoundationHttpError(401, 'unauthenticated', 'Authentication is required');
    return principal;
  };
  const requireDevAuth = () => {
    if (!(identity instanceof DevAuthService))
      throw new FoundationHttpError(
        503,
        'auth_dependency_unavailable',
        'Authentication provider is not configured',
      );
    return identity;
  };
  const sessionCookie = (token: string) =>
    `nexus_dev_session=${token}; Path=/; HttpOnly; SameSite=Lax`;
  const requireIdempotencyKey = (request: FastifyRequest): string => {
    const key = request.headers['idempotency-key'];
    if (typeof key !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(key))
      throw new FoundationHttpError(400, 'invalid_request', 'A valid Idempotency-Key is required');
    return key;
  };
  const runIdempotent = async (input: {
    readonly request: FastifyRequest;
    readonly scope: string;
    readonly operation: string;
    readonly normalizedRequest: unknown;
    readonly run: () => Promise<IdempotentResult>;
  }) => {
    try {
      return await idempotency.execute({
        ...input,
        key: requireIdempotencyKey(input.request),
      });
    } catch (error) {
      if (error instanceof IdempotencyKeyReusedError) {
        throw new FoundationHttpError(
          409,
          'idempotency_key_reused',
          'The Idempotency-Key was already used for a different request',
        );
      }
      throw error;
    }
  };
  const enforceRateBuckets = async (
    buckets: readonly {
      readonly key: string;
      readonly maximumAttempts: number;
      readonly windowSeconds: number;
    }[],
  ) => {
    try {
      const results = await Promise.all(
        buckets.map((bucket) =>
          rateLimit.check(bucket.key, {
            maximumAttempts: bucket.maximumAttempts,
            windowSeconds: bucket.windowSeconds,
          }),
        ),
      );
      const denied = results.filter((result) => !result.allowed);
      if (denied.length) {
        const retryAfterSeconds = Math.max(
          ...denied.map((result) => result.retryAfterSeconds ?? 60),
        );
        throw new FoundationHttpError(
          429,
          'rate_limited',
          'Too many authentication attempts. Please try again later.',
          retryAfterSeconds,
        );
      }
    } catch (error) {
      if (error instanceof FoundationHttpError) throw error;
      throw new FoundationHttpError(503, 'auth_dependency_unavailable', 'Request failed');
    }
  };
  const enforceAuthLimit = (
    request: FastifyRequest,
    operation: 'register' | 'login',
    email: string,
  ) =>
    enforceRateBuckets([
      {
        key: `auth:${operation}:ip:${request.ip}`,
        maximumAttempts: 20,
        windowSeconds: 60,
      },
      {
        key: authEmailRateKey(operation, email),
        maximumAttempts: 5,
        windowSeconds: 60,
      },
    ]);

  app.addHook('onRequest', async (request, reply) => {
    reply.header('x-request-id', request.id);
    reply.header('x-content-type-options', 'nosniff');
    reply.header('x-frame-options', 'DENY');
    reply.header('referrer-policy', 'no-referrer');
    reply.header('access-control-allow-origin', config.webOrigin ?? 'http://localhost:3000');
    reply.header('access-control-allow-credentials', 'true');
    reply.header('access-control-allow-headers', 'content-type, x-request-id, idempotency-key');
    reply.header('access-control-expose-headers', 'retry-after');
    reply.header('access-control-allow-methods', 'GET, POST, PATCH, DELETE, OPTIONS');
    if (
      request.url.startsWith(`${API_PREFIX}/auth/`) ||
      request.url.startsWith(`${API_PREFIX}/me`)
    ) {
      reply.header('cache-control', 'private, no-store');
    }
  });
  app.setErrorHandler((error, request, reply) => {
    const maybe = error as { readonly statusCode?: unknown; readonly message?: unknown };
    const statusCode =
      error instanceof FoundationHttpError
        ? error.statusCode
        : typeof maybe.statusCode === 'number'
          ? maybe.statusCode
          : error instanceof SliceValidationError
            ? 422
            : 500;
    const code =
      error instanceof FoundationHttpError
        ? error.code
        : error instanceof SliceValidationError
          ? error.code
          : statusCode >= 500
            ? 'internal_error'
            : 'invalid_request';
    const message =
      statusCode >= 500
        ? 'Request failed'
        : error instanceof FoundationHttpError || error instanceof SliceValidationError
          ? error.message
          : 'Invalid request';
    const details =
      error instanceof SliceValidationError
        ? [{ field: snakeCase(error.field), issue: error.issue }]
        : undefined;
    if (error instanceof FoundationHttpError && error.retryAfterSeconds)
      reply.header('retry-after', String(error.retryAfterSeconds));
    reply.header('cache-control', 'no-store');
    return reply
      .code(statusCode)
      .send(apiError(code, message, request.id, details ? { details } : {}));
  });

  app.setNotFoundHandler(() => {
    throw new FoundationHttpError(404, 'not_found', 'Resource not found');
  });

  app.get('/health/live', async () => ({ status: 'ok', service: 'api' }));
  app.get('/health/ready', async (_request, reply) =>
    config.ready
      ? { status: 'ready', service: 'api' }
      : reply.code(503).send({ status: 'not_ready' }),
  );
  app.get(API_PREFIX, async (request) =>
    apiSuccess({ status: 'ok', api: API_PREFIX, phase: 'phase13-part2' }, request.id),
  );
  // Register auth routes
  // Use database-backed routes when DATABASE_URL is configured, otherwise use DevAuthService
  if (process.env.DATABASE_URL) {
    try {
      const { authRoutes } = await import('./routes/auth.js');
      const { profileRoutes } = await import('./routes/profile.js');
      const { conversationRoutes } = await import('./routes/conversations.js');
      const { aiRoutes } = await import('./routes/ai.js');
      authRoutes(app);
      profileRoutes(app);
      conversationRoutes(app);
      aiRoutes(app);
      console.log('[API] Database-backed auth routes registered');
    } catch (error) {
      console.log('[API] Database-backed routes not available:', error);
    }
  } else {
    // Use DevAuthService when no database is configured
    app.post(`${API_PREFIX}/auth/register`, async (request, reply) => {
      const body = authBody(request.body);
      await enforceAuthLimit(request, 'register', body.email);
      const result = await runIdempotent({
        request,
        scope: 'unauthenticated',
        operation: 'POST /api/v1/auth/register',
        normalizedRequest: body,
        run: async () => {
          try {
            const auth = requireDevAuth();
            const principal = await auth.register(body);
            return {
              statusCode: 201,
              data: { account_id: principal.accountId, authenticated: true },
              headers: { 'set-cookie': sessionCookie(auth.sessionToken(principal)) },
            };
          } catch (error) {
            if (error instanceof SliceValidationError) throw error;
            throw new FoundationHttpError(409, 'conflict', 'Unable to create account');
          }
        },
      });
      return sendIdempotent(reply, request, result);
    });
    app.post(`${API_PREFIX}/auth/login`, async (request, reply) => {
      const body = authBody(request.body);
      await enforceAuthLimit(request, 'login', body.email);
      const result = await runIdempotent({
        request,
        scope: 'unauthenticated',
        operation: 'POST /api/v1/auth/login',
        normalizedRequest: body,
        run: async () => {
          try {
            const auth = requireDevAuth();
            const principal = await auth.login(body);
            return {
              statusCode: 200,
              data: { account_id: principal.accountId, authenticated: true },
              headers: { 'set-cookie': sessionCookie(auth.sessionToken(principal)) },
            };
          } catch {
            throw new FoundationHttpError(401, 'invalid_auth_proof', 'Invalid sign-in details');
          }
        },
      });
      return sendIdempotent(reply, request, result);
    });
    app.post(`${API_PREFIX}/auth/logout`, async (request, reply) => {
      const body = logoutBody(request.body);
      const scope = await identity.logoutReplayScope(request).catch(() => {
        throw new FoundationHttpError(503, 'auth_dependency_unavailable', 'Request failed');
      });
      if (!scope) throw new FoundationHttpError(401, 'unauthenticated', 'Authentication is required');
      await enforceRateBuckets([
        { key: `auth:logout:ip:${request.ip}`, maximumAttempts: 20, windowSeconds: 60 },
        { key: `auth:logout:session:${scope}`, maximumAttempts: 20, windowSeconds: 60 },
      ]);
      const result = await runIdempotent({
        request,
        scope: `session:${scope}`,
        operation: 'POST /api/v1/auth/logout',
        normalizedRequest: body,
        run: async () => {
          try {
            const principal = await requireUser(request);
            if (!principal.sessionId)
              throw new FoundationHttpError(401, 'unauthenticated', 'Authentication is required');
            const result = await identity.logout(principal);
            return {
              statusCode: 204,
              ...(result?.clearSessionCookie
                ? { headers: { 'set-cookie': result.clearSessionCookie } }
                : {}),
            };
          } catch (error) {
            if (error instanceof FoundationHttpError) throw error;
            throw new FoundationHttpError(503, 'auth_dependency_unavailable', 'Request failed');
          }
        },
      });
      return sendIdempotent(reply, request, result);
    });
    console.log('[API] DevAuthService routes registered');
  }
  app.get(`${API_PREFIX}/me`, async (request, reply) => {
    const principal = await requireUser(request);
    return sendSuccess(reply, request, {
      account: accountProjection(store.account(principal.accountId!)),
      onboarding: onboardingProjection(store.onboarding(principal.accountId!)),
    });
  });
  app.get(`${API_PREFIX}/me/profile`, async (request, reply) =>
    sendSuccess(
      reply,
      request,
      profileProjection(store.profile((await requireUser(request)).accountId!)),
    ),
  );
  app.patch(`${API_PREFIX}/me/profile`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    return sendSuccess(
      reply,
      request,
      profileProjection(store.updateProfile(accountId, profileInput(request.body))),
    );
  });
  app.get(`${API_PREFIX}/me/wellness-profile`, async (request, reply) =>
    sendSuccess(
      reply,
      request,
      wellnessProjection(store.wellnessProfile((await requireUser(request)).accountId!)),
    ),
  );
  app.patch(`${API_PREFIX}/me/wellness-profile`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    return sendSuccess(
      reply,
      request,
      wellnessProjection(store.updateWellness(accountId, wellnessInput(request.body))),
    );
  });
  app.get(`${API_PREFIX}/me/consents`, async (request, reply) =>
    sendSuccess(reply, request, {
      items: store.consentsFor((await requireUser(request)).accountId!).map(consentProjection),
    }),
  );
  app.post(`${API_PREFIX}/me/consents`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    const body = consentInput(request.body);
    const result = await runIdempotent({
      request,
      scope: `account:${accountId}`,
      operation: 'POST /api/v1/me/consents',
      normalizedRequest: body,
      run: async () => ({
        statusCode: 201,
        data: consentProjection(
          store.addConsent(accountId, {
            ...body,
            captureSource: store.onboarding(accountId).complete ? 'settings' : 'onboarding',
          }),
        ),
      }),
    });
    return sendIdempotent(reply, request, result);
  });
  app.get(`${API_PREFIX}/me/goals`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    const query = goalListQuery(request.query);
    const allGoals = store.listGoals(accountId, query);
    const startAt = query.cursor ? allGoals.findIndex((goal) => goal.id === query.cursor) + 1 : 0;
    if (query.cursor && startAt === 0)
      throw new SliceValidationError('cursor', 'Goal cursor is invalid');
    const page = allGoals.slice(startAt, startAt + query.limit);
    const hasMore = startAt + query.limit < allGoals.length;
    return reply.send(
      apiSuccess({ items: page.map(goalProjection) }, request.id, {
        nextCursor: hasMore ? encodeGoalCursor(page[page.length - 1]!.id) : null,
      }),
    );
  });
  app.post(`${API_PREFIX}/me/goals`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    const input = goalCreateInput(request.body);
    const result = await runIdempotent({
      request,
      scope: `account:${accountId}`,
      operation: 'POST /api/v1/me/goals',
      normalizedRequest: input,
      run: async () => ({
        statusCode: 201,
        data: goalProjection(store.createGoal(accountId, input)),
      }),
    });
    return sendIdempotent(reply, request, result);
  });
  app.get(`${API_PREFIX}/me/goals/:goal_id`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    const { goal_id: goalId } = request.params as { goal_id: string };
    const goal = store.goal(accountId, goalId);
    if (!goal) throw new FoundationHttpError(404, 'not_found', 'Goal not found');
    return sendSuccess(reply, request, goalProjection(goal));
  });
  app.patch(`${API_PREFIX}/me/goals/:goal_id`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    const { goal_id: goalId } = request.params as { goal_id: string };
    const input = goalPatchInput(request.body);
    const result = await runIdempotent({
      request,
      scope: `account:${accountId}`,
      operation: 'PATCH /api/v1/me/goals/:goal_id',
      normalizedRequest: { goal_id: goalId, ...input },
      run: async () => {
        const goal = store.updateGoal(accountId, goalId, input);
        if (!goal) throw new FoundationHttpError(404, 'not_found', 'Goal not found');
        return { statusCode: 200, data: goalProjection(goal) };
      },
    });
    return sendIdempotent(reply, request, result);
  });
  app.delete(`${API_PREFIX}/me/goals/:goal_id`, async (request, reply) => {
    const accountId = (await requireUser(request)).accountId!;
    const { goal_id: goalId } = request.params as { goal_id: string };
    const result = await runIdempotent({
      request,
      scope: `account:${accountId}`,
      operation: 'DELETE /api/v1/me/goals/:goal_id',
      normalizedRequest: { goal_id: goalId },
      run: async () => {
        if (!store.deleteGoal(accountId, goalId))
          throw new FoundationHttpError(404, 'not_found', 'Goal not found');
        return { statusCode: 204 };
      },
    });
    return sendIdempotent(reply, request, result);
  });
  app.register(
    async (scope) => {
      scope.addHook('onRequest', async (request) => {
        requireInternalActor(await resolvePrincipal(request, identity));
      });
      scope.get('/', async (request) =>
        apiSuccess({ status: 'ok', internal: INTERNAL_PREFIX, phase: 'foundation' }, request.id),
      );
    },
    { prefix: INTERNAL_PREFIX },
  );

  return app;
}

function sendSuccess(
  reply: FastifyReply,
  request: FastifyRequest,
  data: unknown,
  statusCode = 200,
) {
  return reply.code(statusCode).send(apiSuccess(data, request.id));
}

function sendIdempotent(reply: FastifyReply, request: FastifyRequest, result: IdempotentResult) {
  for (const [name, value] of Object.entries(result.headers ?? {})) reply.header(name, value);
  if (result.statusCode === 204) return reply.code(204).send();
  return sendSuccess(reply, request, result.data ?? null, result.statusCode);
}

function objectBody(value: unknown, allowedFields: readonly string[]): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new SliceValidationError('body', 'Request body must be a JSON object');
  const body = value as Record<string, unknown>;
  const unknown = Object.keys(body).find((key) => !allowedFields.includes(key));
  if (unknown) throw new SliceValidationError(unknown, 'Unknown request field');
  return body;
}

function optionalString(body: Record<string, unknown>, field: string): string | undefined {
  const value = body[field];
  if (value === undefined) return undefined;
  if (typeof value !== 'string') throw new SliceValidationError(field, 'Value must be a string');
  return value;
}

function requiredString(body: Record<string, unknown>, field: string): string {
  const value = optionalString(body, field);
  if (value === undefined || value.length === 0)
    throw new SliceValidationError(field, 'Value is required');
  return value;
}

function authBody(value: unknown): { readonly email: string } {
  const body = objectBody(value, ['email']);
  return { email: requiredString(body, 'email').trim().toLowerCase() };
}

function logoutBody(value: unknown): Record<string, never> {
  if (value === undefined) return {};
  const body = objectBody(value, []);
  return body as Record<string, never>;
}

function profileInput(value: unknown): {
  readonly displayName?: string;
  readonly ageBand?: string;
  readonly locale?: string;
  readonly timezone?: string;
} {
  const body = objectBody(value, ['display_name', 'age_band', 'locale', 'timezone']);
  const displayName = optionalString(body, 'display_name');
  const ageBand = optionalString(body, 'age_band');
  const locale = optionalString(body, 'locale');
  const timezone = optionalString(body, 'timezone');
  return {
    ...(displayName !== undefined ? { displayName } : {}),
    ...(ageBand !== undefined ? { ageBand } : {}),
    ...(locale !== undefined ? { locale } : {}),
    ...(timezone !== undefined ? { timezone } : {}),
  };
}

function wellnessInput(value: unknown): {
  readonly wellnessAreas?: readonly string[];
  readonly coachingStyle?: string;
} {
  const body = objectBody(value, ['wellness_areas', 'coaching_style']);
  const areas = body.wellness_areas;
  if (
    areas !== undefined &&
    (!Array.isArray(areas) || areas.some((area) => typeof area !== 'string'))
  )
    throw new SliceValidationError('wellness_areas', 'Wellness areas must be a string array');
  const coachingStyle = optionalString(body, 'coaching_style');
  return {
    ...(areas !== undefined ? { wellnessAreas: areas as string[] } : {}),
    ...(coachingStyle !== undefined ? { coachingStyle } : {}),
  };
}

function consentInput(
  value: unknown,
): Omit<ConsentRecord, 'id' | 'accountId' | 'capturedAt' | 'captureSource'> {
  const body = objectBody(value, ['consent_type', 'policy_version', 'decision']);
  const decision = requiredString(body, 'decision');
  if (!['granted', 'denied', 'revoked', 'superseded'].includes(decision))
    throw new SliceValidationError('decision', 'Consent decision is invalid');
  return {
    consentType: requiredString(body, 'consent_type'),
    policyVersion: requiredString(body, 'policy_version'),
    decision: decision as ConsentRecord['decision'],
  };
}

function accountProjection(account: SliceAccount | null) {
  return account ? { id: account.id, email: account.email, status: account.status } : null;
}

function profileProjection(profile: UserProfile) {
  return {
    account_id: profile.accountId,
    ...(profile.displayName !== undefined ? { display_name: profile.displayName } : {}),
    ...(profile.ageBand !== undefined ? { age_band: profile.ageBand } : {}),
    ...(profile.locale !== undefined ? { locale: profile.locale } : {}),
    ...(profile.timezone !== undefined ? { timezone: profile.timezone } : {}),
    updated_at: profile.updatedAt,
  };
}

function wellnessProjection(profile: WellnessProfile) {
  return {
    account_id: profile.accountId,
    wellness_areas: profile.wellnessAreas,
    ...(profile.coachingStyle !== undefined ? { coaching_style: profile.coachingStyle } : {}),
    status: profile.status,
    updated_at: profile.updatedAt,
  };
}

function consentProjection(record: ConsentRecord) {
  return {
    id: record.id,
    account_id: record.accountId,
    consent_type: record.consentType,
    policy_version: record.policyVersion,
    decision: record.decision,
    captured_at: record.capturedAt,
    capture_source: record.captureSource,
  };
}

function goalProjection(goal: WellnessGoal) {
  return {
    goal_id: goal.id,
    account_id: goal.accountId,
    wellness_area: goal.wellnessArea,
    title: goal.title,
    ...(goal.description !== undefined ? { description: goal.description } : {}),
    start_date: goal.startDate,
    ...(goal.endDate !== undefined ? { end_date: goal.endDate } : {}),
    status: goal.status,
    created_at: goal.createdAt,
    updated_at: goal.updatedAt,
    ...(goal.deletedAt !== undefined ? { deleted_at: goal.deletedAt } : {}),
  };
}

function goalCreateInput(value: unknown): GoalInput {
  const body = objectBody(value, [
    'wellness_area',
    'title',
    'description',
    'start_date',
    'end_date',
  ]);
  const description = optionalString(body, 'description');
  const endDate = optionalString(body, 'end_date');
  return {
    wellnessArea: requiredString(body, 'wellness_area'),
    title: requiredString(body, 'title'),
    ...(description !== undefined ? { description } : {}),
    startDate: requiredString(body, 'start_date'),
    ...(endDate !== undefined ? { endDate } : {}),
  };
}

function goalPatchInput(value: unknown): GoalInput {
  const body = objectBody(value, [
    'wellness_area',
    'title',
    'description',
    'start_date',
    'end_date',
    'status',
  ]);
  if (Object.keys(body).length === 0)
    throw new SliceValidationError('body', 'Provide at least one goal field to update');
  const wellnessArea = optionalString(body, 'wellness_area');
  const title = optionalString(body, 'title');
  const description = optionalString(body, 'description');
  const startDate = optionalString(body, 'start_date');
  const endDate = optionalString(body, 'end_date');
  const status = optionalString(body, 'status');
  return {
    ...(wellnessArea !== undefined ? { wellnessArea } : {}),
    ...(title !== undefined ? { title } : {}),
    ...(description !== undefined ? { description } : {}),
    ...(startDate !== undefined ? { startDate } : {}),
    ...(endDate !== undefined ? { endDate } : {}),
    ...(status !== undefined ? { status } : {}),
  };
}

function goalListQuery(value: unknown): {
  readonly status?: GoalStatus;
  readonly wellnessArea?: WellnessArea;
  readonly cursor?: string;
  readonly limit: number;
} {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new SliceValidationError('query', 'Query parameters are invalid');
  const query = value as Record<string, unknown>;
  const unknown = Object.keys(query).find(
    (key) => !['status', 'wellness_area', 'cursor', 'limit'].includes(key),
  );
  if (unknown) throw new SliceValidationError(unknown, 'Unknown query parameter');
  const status = query.status;
  const wellnessArea = query.wellness_area;
  const cursor = query.cursor;
  const rawLimit = query.limit;
  if (status !== undefined && (typeof status !== 'string' || !isGoalStatus(status)))
    throw new SliceValidationError('status', 'Goal status is invalid');
  if (
    wellnessArea !== undefined &&
    (typeof wellnessArea !== 'string' || !isWellnessArea(wellnessArea))
  )
    throw new SliceValidationError('wellness_area', 'Choose an approved wellness area');
  if (cursor !== undefined && typeof cursor !== 'string')
    throw new SliceValidationError('cursor', 'Goal cursor is invalid');
  const limit = rawLimit === undefined ? 25 : Number(rawLimit);
  if (!Number.isInteger(limit) || limit < 1 || limit > 100)
    throw new SliceValidationError('limit', 'Limit must be from 1 to 100');
  return {
    ...(typeof status === 'string' ? { status } : {}),
    ...(typeof wellnessArea === 'string' ? { wellnessArea } : {}),
    ...(typeof cursor === 'string' ? { cursor: decodeGoalCursor(cursor) } : {}),
    limit,
  };
}

function isGoalStatus(value: string): value is GoalStatus {
  return ['draft', 'active', 'paused', 'completed', 'archived', 'deleted'].includes(value);
}

function isWellnessArea(value: string): value is WellnessArea {
  return [
    'sleep',
    'movement',
    'nutrition',
    'stress',
    'hydration',
    'mindfulness',
    'routine',
  ].includes(value);
}

function encodeGoalCursor(goalId: string): string {
  return Buffer.from(goalId).toString('base64url');
}

function decodeGoalCursor(cursor: string): string {
  try {
    const decoded = Buffer.from(cursor, 'base64url').toString();
    if (!decoded || encodeGoalCursor(decoded) !== cursor) throw new Error('invalid cursor');
    return decoded;
  } catch {
    throw new SliceValidationError('cursor', 'Goal cursor is invalid');
  }
}

function onboardingProjection(state: OnboardingState) {
  return {
    complete: state.complete,
    profile_complete: state.profileComplete,
    wellness_complete: state.wellnessComplete,
    consent_choices_recorded: state.consentChoicesRecorded,
  };
}

function snakeCase(value: string): string {
  return value.replace(/[A-Z]/g, (character) => `_${character.toLowerCase()}`);
}
