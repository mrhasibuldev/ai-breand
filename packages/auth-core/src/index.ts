export type ActorType = 'guest' | 'user' | 'support' | 'admin' | 'security_admin' | 'worker';

export type Principal = {
  readonly accountId?: string;
  readonly actorType: ActorType;
  readonly sessionId?: string;
  readonly assuranceLevel: 'anonymous' | 'authenticated' | 'step_up';
};

export interface IdentityAdapter {
  resolvePrincipal(request: unknown): Promise<Principal | null>;
}

export type SessionLogoutResult = {
  readonly clearSessionCookie?: string;
};

export interface SessionIdentityAdapter extends IdentityAdapter {
  /** Non-secret, credential-bound scope, stable after revocation for exact logout retries.
   * Return null for missing/malformed credentials. This does not authenticate a request.
   */
  logoutReplayScope(request: unknown): Promise<string | null>;
  logout(principal: Principal): Promise<SessionLogoutResult | void>;
}

export interface AuthenticationService {
  register(input: unknown): Promise<Principal>;
  login(input: unknown): Promise<Principal>;
  logout(principal: Principal): Promise<SessionLogoutResult | void>;
  validateSession(input: unknown): Promise<Principal | null>;
  rotateSession(principal: Principal): Promise<Principal>;
  recover(input: unknown): Promise<void>;
  beginMfa(input: unknown): Promise<{ readonly challengeId: string }>;
  completeMfa(input: unknown): Promise<Principal>;
  requireStepUp(principal: Principal): Promise<Principal>;
}

export class UnconfiguredIdentityAdapter implements SessionIdentityAdapter {
  async logoutReplayScope(): Promise<null> {
    return null;
  }

  async resolvePrincipal(): Promise<Principal | null> {
    return null;
  }

  async logout(): Promise<void> {
    throw new Error('Authentication provider is not configured');
  }
}
