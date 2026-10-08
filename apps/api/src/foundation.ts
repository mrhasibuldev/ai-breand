import type { FastifyRequest } from 'fastify';
import type { IdentityAdapter, Principal } from '@nexusai/auth-core';

export interface RateLimitBoundary {
  check(
    key: string,
    policy?: { readonly maximumAttempts: number; readonly windowSeconds: number },
  ): Promise<{ readonly allowed: boolean; readonly retryAfterSeconds?: number }>;
}

export interface IdempotencyBoundary {
  begin(key: string, accountId?: string): Promise<'new' | 'replay' | 'in_flight'>;
  complete(key: string, accountId?: string): Promise<void>;
}

export class FoundationHttpError extends Error {
  constructor(
    readonly statusCode: number,
    readonly code: string,
    message: string,
    readonly retryAfterSeconds?: number,
  ) {
    super(message);
  }
}

export async function resolvePrincipal(
  request: FastifyRequest,
  identity: IdentityAdapter,
): Promise<Principal | null> {
  return identity.resolvePrincipal(request);
}

export function requireAuthenticated(principal: Principal | null): Principal {
  if (!principal || principal.assuranceLevel === 'anonymous') {
    throw new FoundationHttpError(401, 'unauthenticated', 'Authentication is required');
  }
  return principal;
}

export function requireInternalActor(principal: Principal | null): Principal {
  if (
    !principal ||
    !['worker', 'support', 'admin', 'security_admin'].includes(principal.actorType)
  ) {
    throw new FoundationHttpError(403, 'forbidden', 'Internal access is restricted');
  }
  return principal;
}
