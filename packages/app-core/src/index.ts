import { createHash, randomUUID } from 'node:crypto';
import type {
  AuthenticationService,
  Principal,
  SessionIdentityAdapter,
  SessionLogoutResult,
} from '@nexusai/auth-core';
import { evaluateWellnessFreeText } from '@nexusai/safety-core';

export type UserProfile = {
  readonly accountId: string;
  displayName?: string;
  ageBand?: string;
  locale?: string;
  timezone?: string;
  readonly updatedAt: string;
};

export type WellnessProfile = {
  readonly accountId: string;
  wellnessAreas: readonly string[];
  coachingStyle?: string;
  readonly status: 'active' | 'archived' | 'deleted';
  readonly updatedAt: string;
};

export type ConsentRecord = {
  readonly id: string;
  readonly accountId: string;
  readonly consentType: string;
  readonly policyVersion: string;
  readonly decision: 'granted' | 'denied' | 'revoked' | 'superseded';
  readonly capturedAt: string;
  readonly captureSource: string;
};

export type OnboardingState = {
  readonly complete: boolean;
  readonly profileComplete: boolean;
  readonly wellnessComplete: boolean;
  readonly consentChoicesRecorded: boolean;
};

export type SliceAccount = {
  readonly id: string;
  readonly email: string;
  readonly status: 'active';
};

export type GoalStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived' | 'deleted';
export type WellnessArea =
  'sleep' | 'movement' | 'nutrition' | 'stress' | 'hydration' | 'mindfulness' | 'routine';

export type WellnessGoal = {
  readonly id: string;
  readonly accountId: string;
  readonly wellnessArea: WellnessArea;
  readonly title: string;
  readonly description?: string;
  readonly startDate: string;
  readonly endDate?: string;
  readonly status: GoalStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly deletedAt?: string;
};

export type GoalInput = {
  readonly wellnessArea?: string;
  readonly title?: string;
  readonly description?: string;
  readonly startDate?: string;
  readonly endDate?: string;
  readonly status?: string;
};
type ValidatedGoalInput = Omit<GoalInput, 'endDate'> & { readonly endDate?: string | null };

const GOAL_AREAS = new Set<WellnessArea>([
  'sleep',
  'movement',
  'nutrition',
  'stress',
  'hydration',
  'mindfulness',
  'routine',
]);
const GOAL_STATUSES = new Set<GoalStatus>([
  'draft',
  'active',
  'paused',
  'completed',
  'archived',
  'deleted',
]);
const EDITABLE_GOAL_STATUSES = new Set<GoalStatus>([
  'draft',
  'active',
  'paused',
  'completed',
  'archived',
]);
const GOAL_DESCRIPTION_MAX_LENGTH = 2000;

export class SliceValidationError extends Error {
  constructor(
    readonly field: string,
    message: string,
    readonly code: 'validation_failed' | 'unsafe_input' = 'validation_failed',
    readonly issue = 'invalid_value',
  ) {
    super(message);
  }
}

export class SliceStore {
  constructor(private readonly environment = process.env.NODE_ENV ?? 'development') {
    this.ensureDevelopment();
  }

  private ensureDevelopment(): void {
    if (
      !['development', 'test'].includes(this.environment) ||
      !['development', 'test'].includes(process.env.NODE_ENV ?? 'development')
    )
      throw new Error('Process-local SliceStore is development/test-only');
  }

  private readonly accounts = new Map<string, SliceAccount>();
  private readonly profiles = new Map<string, UserProfile>();
  private readonly wellness = new Map<string, WellnessProfile>();
  private readonly consents = new Map<string, ConsentRecord[]>();
  private readonly goals = new Map<string, WellnessGoal>();

  createAccount(email: string): SliceAccount {
    this.ensureDevelopment();
    const normalized = email.trim().toLowerCase();
    if (!/^\S+@\S+\.\S+$/.test(normalized))
      throw new SliceValidationError('email', 'Enter a valid email');
    if ([...this.accounts.values()].some((account) => account.email === normalized))
      throw new Error('Account already exists');
    const account = { id: randomUUID(), email: normalized, status: 'active' as const };
    this.accounts.set(account.id, account);
    return account;
  }

  findAccountByEmail(email: string): SliceAccount | null {
    this.ensureDevelopment();
    return (
      [...this.accounts.values()].find((account) => account.email === email.trim().toLowerCase()) ??
      null
    );
  }

  account(accountId: string): SliceAccount | null {
    this.ensureDevelopment();
    return this.accounts.get(accountId) ?? null;
  }

  profile(accountId: string): UserProfile {
    this.ensureDevelopment();
    return this.profiles.get(accountId) ?? { accountId, updatedAt: new Date().toISOString() };
  }

  updateProfile(
    accountId: string,
    input: Partial<Pick<UserProfile, 'displayName' | 'ageBand' | 'locale' | 'timezone'>>,
  ): UserProfile {
    this.ensureDevelopment();
    const { displayName, ageBand, locale, timezone } = input;
    if (displayName !== undefined && (displayName.trim().length < 1 || displayName.length > 120))
      throw new SliceValidationError('displayName', 'Name must be 1–120 characters');
    if (ageBand !== undefined && ageBand.length > 40)
      throw new SliceValidationError('ageBand', 'Age band is too long');
    if (locale !== undefined && !/^[A-Za-z]{2,3}(?:[-_][A-Za-z]{2,4})?$/.test(locale))
      throw new SliceValidationError('locale', 'Use a valid locale such as en-US');
    if (timezone !== undefined) {
      try {
        Intl.DateTimeFormat(undefined, { timeZone: timezone });
      } catch {
        throw new SliceValidationError('timezone', 'Use a valid IANA timezone');
      }
    }
    const approved = {
      ...(displayName !== undefined ? { displayName } : {}),
      ...(ageBand !== undefined ? { ageBand } : {}),
      ...(locale !== undefined ? { locale } : {}),
      ...(timezone !== undefined ? { timezone } : {}),
    };
    const next = { ...this.profile(accountId), ...approved, updatedAt: new Date().toISOString() };
    this.profiles.set(accountId, next);
    return next;
  }

  wellnessProfile(accountId: string): WellnessProfile {
    this.ensureDevelopment();
    return (
      this.wellness.get(accountId) ?? {
        accountId,
        wellnessAreas: [],
        status: 'active',
        updatedAt: new Date().toISOString(),
      }
    );
  }

  updateWellness(
    accountId: string,
    input: { wellnessAreas?: readonly string[]; coachingStyle?: string },
  ): WellnessProfile {
    this.ensureDevelopment();
    const { wellnessAreas, coachingStyle } = input;
    const allowed = new Set([
      'sleep',
      'movement',
      'nutrition',
      'stress',
      'hydration',
      'mindfulness',
      'routine',
    ]);
    if (
      wellnessAreas &&
      (wellnessAreas.length > 7 || wellnessAreas.some((area) => !allowed.has(area)))
    )
      throw new SliceValidationError(
        'wellnessAreas',
        'Choose only approved general wellness areas',
      );
    if (coachingStyle !== undefined && coachingStyle.length > 80)
      throw new SliceValidationError('coachingStyle', 'Coaching style is too long');
    if (coachingStyle !== undefined) {
      const decision = evaluateWellnessFreeText(coachingStyle);
      if (!decision.allowed)
        throw new SliceValidationError(
          'coachingStyle',
          'Clinical content cannot be stored in a wellness profile',
          'unsafe_input',
          decision.reason,
        );
    }
    const next = {
      ...this.wellnessProfile(accountId),
      ...(wellnessAreas !== undefined ? { wellnessAreas } : {}),
      ...(coachingStyle !== undefined ? { coachingStyle } : {}),
      updatedAt: new Date().toISOString(),
    };
    this.wellness.set(accountId, next);
    return next;
  }

  addConsent(
    accountId: string,
    input: Omit<ConsentRecord, 'id' | 'accountId' | 'capturedAt'>,
  ): ConsentRecord {
    this.ensureDevelopment();
    if (!input.consentType || !input.policyVersion || !input.captureSource)
      throw new SliceValidationError('consent', 'Consent metadata is required');
    if (input.consentType !== 'memory' || input.policyVersion !== 'memory-foundation-v1')
      throw new SliceValidationError(
        'consentType',
        'Consent policy is not available in this slice',
      );
    if (!['granted', 'denied', 'revoked', 'superseded'].includes(input.decision))
      throw new SliceValidationError('decision', 'Consent decision is invalid');
    if (!['onboarding', 'settings'].includes(input.captureSource))
      throw new SliceValidationError('captureSource', 'Consent source is invalid');
    const record = { ...input, id: randomUUID(), accountId, capturedAt: new Date().toISOString() };
    this.consents.set(accountId, [...(this.consents.get(accountId) ?? []), record]);
    return record;
  }

  consentsFor(accountId: string): readonly ConsentRecord[] {
    this.ensureDevelopment();
    return this.consents.get(accountId) ?? [];
  }

  listGoals(
    accountId: string,
    filters: { readonly status?: GoalStatus; readonly wellnessArea?: WellnessArea } = {},
  ): readonly WellnessGoal[] {
    this.ensureDevelopment();
    return [...this.goals.values()]
      .filter(
        (goal) =>
          goal.accountId === accountId &&
          goal.status !== 'deleted' &&
          (filters.status === undefined || goal.status === filters.status) &&
          (filters.wellnessArea === undefined || goal.wellnessArea === filters.wellnessArea),
      )
      .sort((left, right) =>
        left.createdAt === right.createdAt
          ? left.id.localeCompare(right.id)
          : left.createdAt.localeCompare(right.createdAt),
      )
      .map(cloneGoal);
  }

  goal(accountId: string, goalId: string): WellnessGoal | null {
    this.ensureDevelopment();
    const goal = this.goals.get(goalId);
    return goal?.accountId === accountId && goal.status !== 'deleted' ? cloneGoal(goal) : null;
  }

  createGoal(accountId: string, input: GoalInput): WellnessGoal {
    this.ensureDevelopment();
    const approved = validateGoalInput(input, true);
    const now = new Date().toISOString();
    const goal: WellnessGoal = {
      id: randomUUID(),
      accountId,
      wellnessArea: approved.wellnessArea as WellnessArea,
      title: approved.title!,
      ...(approved.description !== undefined ? { description: approved.description } : {}),
      startDate: approved.startDate!,
      ...(approved.endDate !== undefined && approved.endDate !== null && approved.endDate !== ''
        ? { endDate: approved.endDate }
        : {}),
      status: (approved.status as GoalStatus | undefined) ?? 'active',
      createdAt: now,
      updatedAt: now,
    };
    this.goals.set(goal.id, goal);
    return cloneGoal(goal);
  }

  updateGoal(accountId: string, goalId: string, input: GoalInput): WellnessGoal | null {
    this.ensureDevelopment();
    const current = this.goal(accountId, goalId);
    if (!current) return null;
    const approved = validateGoalInput(input, false, current);
    const next: WellnessGoal = {
      ...current,
      ...(approved.wellnessArea !== undefined
        ? { wellnessArea: approved.wellnessArea as WellnessArea }
        : {}),
      ...(approved.title !== undefined ? { title: approved.title } : {}),
      ...(approved.description !== undefined ? { description: approved.description } : {}),
      ...(approved.startDate !== undefined ? { startDate: approved.startDate } : {}),
      ...(approved.endDate !== undefined && approved.endDate !== null
        ? { endDate: approved.endDate }
        : {}),
      ...(approved.status !== undefined ? { status: approved.status as GoalStatus } : {}),
      updatedAt: new Date().toISOString(),
    };
    if (approved.endDate === null) {
      const { endDate: unusedEndDate, ...withoutEndDate } = next;
      void unusedEndDate;
      this.goals.set(goalId, withoutEndDate);
      return cloneGoal(withoutEndDate);
    }
    this.goals.set(goalId, next);
    return cloneGoal(next);
  }

  deleteGoal(accountId: string, goalId: string): boolean {
    this.ensureDevelopment();
    const current = this.goal(accountId, goalId);
    if (!current) return false;
    const now = new Date().toISOString();
    this.goals.set(goalId, { ...current, status: 'deleted', deletedAt: now, updatedAt: now });
    return true;
  }

  onboarding(accountId: string): OnboardingState {
    this.ensureDevelopment();
    const profile = this.profile(accountId);
    const wellness = this.wellnessProfile(accountId);
    const consents = this.consentsFor(accountId);
    const profileComplete = Boolean(profile.displayName && profile.locale && profile.timezone);
    const wellnessComplete = wellness.wellnessAreas.length > 0;
    const consentChoicesRecorded = consents.some((record) => record.consentType === 'memory');
    return {
      profileComplete,
      wellnessComplete,
      consentChoicesRecorded,
      complete: profileComplete && wellnessComplete && consentChoicesRecorded,
    };
  }
}

function validateGoalInput(
  input: GoalInput,
  creating: boolean,
  current?: WellnessGoal,
): ValidatedGoalInput {
  const field = (name: keyof GoalInput, value: string | undefined) => {
    if (value === undefined) {
      if (creating && ['wellnessArea', 'title', 'startDate'].includes(name))
        throw new SliceValidationError(name, 'This field is required');
      return undefined;
    }
    return value;
  };
  const wellnessArea = field('wellnessArea', input.wellnessArea);
  const title = field('title', input.title);
  const description = field('description', input.description);
  const startDate = field('startDate', input.startDate);
  const endDate = input.endDate;
  const status = field('status', input.status);

  if (wellnessArea !== undefined && !GOAL_AREAS.has(wellnessArea as WellnessArea))
    throw new SliceValidationError('wellnessArea', 'Choose an approved wellness area');
  if (title !== undefined && (!title.trim() || title.length > 160))
    throw new SliceValidationError('title', 'Title must contain 1 to 160 characters');
  if (description !== undefined && description.length > GOAL_DESCRIPTION_MAX_LENGTH)
    throw new SliceValidationError(
      'description',
      `Description must be ${GOAL_DESCRIPTION_MAX_LENGTH} characters or fewer`,
    );
  if (startDate !== undefined && !isCalendarDate(startDate))
    throw new SliceValidationError('startDate', 'Use a valid YYYY-MM-DD date');
  if (endDate !== undefined && endDate !== null && endDate !== '' && !isCalendarDate(endDate))
    throw new SliceValidationError('endDate', 'Use a valid YYYY-MM-DD date');
  if ((endDate === '' || endDate === null) && !creating) {
    // Empty date is the explicit API representation for clearing an optional end date.
  }
  if (status !== undefined && !GOAL_STATUSES.has(status as GoalStatus))
    throw new SliceValidationError('status', 'Goal status is invalid');
  if (creating && status === 'deleted')
    throw new SliceValidationError('status', 'A goal cannot be created as deleted');
  if (!creating && status === 'deleted')
    throw new SliceValidationError('status', 'Use the delete operation to remove a goal');
  if (!creating && status !== undefined && !EDITABLE_GOAL_STATUSES.has(status as GoalStatus))
    throw new SliceValidationError('status', 'Goal status is invalid');

  const effectiveTitle = title ?? current?.title ?? '';
  const effectiveDescription = description ?? current?.description ?? '';
  const safety = evaluateWellnessFreeText([effectiveTitle, effectiveDescription].join('\n'));
  if (!safety.allowed)
    throw new SliceValidationError(
      title !== undefined ? 'title' : 'description',
      'This content cannot be stored as a wellness goal',
      'unsafe_input',
      safety.reason,
    );

  const effectiveStart = startDate ?? current?.startDate;
  const effectiveEnd =
    endDate === '' || endDate === null ? undefined : (endDate ?? current?.endDate);
  if (effectiveStart && effectiveEnd && effectiveStart > effectiveEnd)
    throw new SliceValidationError('endDate', 'End date must be on or after start date');

  return {
    ...(wellnessArea !== undefined ? { wellnessArea: wellnessArea as WellnessArea } : {}),
    ...(title !== undefined ? { title: title.trim() } : {}),
    ...(description !== undefined ? { description: description.trim() } : {}),
    ...(startDate !== undefined ? { startDate } : {}),
    ...(endDate !== undefined ? { endDate: endDate === '' ? null : endDate } : {}),
    ...(status !== undefined ? { status } : {}),
  };
}

function isCalendarDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
}

function cloneGoal(goal: WellnessGoal): WellnessGoal {
  return { ...goal };
}

/** Development-only adapter. It is intentionally impossible to use in production. */
export class DevAuthService implements SessionIdentityAdapter, AuthenticationService {
  private readonly sessions = new Map<string, string>();
  constructor(
    private readonly store: SliceStore,
    private readonly environment = 'development',
  ) {}
  private ensureDev(): void {
    if (
      !['development', 'test'].includes(this.environment) ||
      !['development', 'test'].includes(process.env.NODE_ENV ?? 'development')
    )
      throw new Error('Development authentication is disabled in production');
  }
  async logoutReplayScope(request: unknown): Promise<string | null> {
    this.ensureDev();
    const headers = (request as { headers?: Record<string, unknown> }).headers ?? {};
    const token = String(headers.cookie ?? '').match(/(?:^|;\s*)nexus_dev_session=([^;]+)/)?.[1];
    return token ? this.hashToken(token) : null;
  }
  async resolvePrincipal(request: unknown): Promise<Principal | null> {
    this.ensureDev();
    const headers = (request as { headers?: Record<string, unknown> }).headers ?? {};
    const cookie = String(headers.cookie ?? '');
    const token = cookie.match(/(?:^|;\s*)nexus_dev_session=([^;]+)/)?.[1];
    const accountId = token ? this.sessions.get(this.hashToken(token)) : undefined;
    return accountId
      ? {
          accountId,
          actorType: 'user',
          ...(token ? { sessionId: token } : {}),
          assuranceLevel: 'authenticated',
        }
      : null;
  }
  async register(input: unknown): Promise<Principal> {
    this.ensureDev();
    const body = input as { email?: string };
    const account = this.store.createAccount(body.email ?? '');
    return this.issue(account.id);
  }
  async login(input: unknown): Promise<Principal> {
    this.ensureDev();
    const body = input as { email?: string };
    const account = this.store.findAccountByEmail(body.email ?? '');
    if (!account) throw new Error('Invalid credentials');
    return this.issue(account.id);
  }
  async logout(principal: Principal): Promise<SessionLogoutResult> {
    this.ensureDev();
    if (principal.sessionId) this.sessions.delete(this.hashToken(principal.sessionId));
    return { clearSessionCookie: 'nexus_dev_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax' };
  }
  async validateSession(input: unknown): Promise<Principal | null> {
    return this.resolvePrincipal(input);
  }
  async rotateSession(principal: Principal): Promise<Principal> {
    await this.logout(principal);
    return this.issue(principal.accountId ?? '');
  }
  async recover(): Promise<void> {
    this.ensureDev();
  }
  async beginMfa(): Promise<{ readonly challengeId: string }> {
    this.ensureDev();
    return { challengeId: randomUUID() };
  }
  async completeMfa(): Promise<Principal> {
    throw new Error('MFA provider is not configured');
  }
  async requireStepUp(principal: Principal): Promise<Principal> {
    return principal;
  }
  sessionToken(principal: Principal): string {
    return principal.sessionId ?? '';
  }
  private issue(accountId: string): Principal {
    const token = randomUUID();
    this.sessions.set(this.hashToken(token), accountId);
    return { accountId, actorType: 'user', sessionId: token, assuranceLevel: 'authenticated' };
  }
  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }
}
