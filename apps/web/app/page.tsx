'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

type Profile = { display_name?: string; locale?: string; timezone?: string };
type Wellness = { wellness_areas: string[]; coaching_style?: string };
type Consent = {
  consent_type: string;
  decision: 'granted' | 'denied' | 'revoked' | 'superseded';
  captured_at: string;
};
type ApiEnvelope<T> = { data: T };
type ApiErrorEnvelope = { error?: { message?: string } };
type GoalStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived';
type Goal = {
  goal_id: string;
  account_id: string;
  wellness_area: string;
  title: string;
  description?: string;
  start_date: string;
  end_date?: string;
  status: GoalStatus;
  created_at: string;
  updated_at: string;
};
type GoalPayload = {
  wellness_area: string;
  title: string;
  description?: string;
  start_date: string;
  end_date?: string;
};
class GoalApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
  ) {
    super(code);
  }
}
const API = process.env.NEXT_PUBLIC_API_ORIGIN ?? 'http://localhost:4000';
const areas = ['sleep', 'movement', 'nutrition', 'stress', 'hydration', 'mindfulness', 'routine'];
const goalStatuses: GoalStatus[] = ['draft', 'active', 'paused', 'completed', 'archived'];

class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}/api/v1${path}`, {
    ...init,
    credentials: 'include',
    headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) },
  });
  const body = response.status === 204 ? null : ((await response.json()) as ApiEnvelope<T>);
  if (!response.ok) {
    const error = body as ApiErrorEnvelope | null;
    throw new ApiRequestError(error?.error?.message ?? 'Something went wrong', response.status);
  }
  return body?.data as T;
}

async function goalCall<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API}/api/v1/me/goals${path}`, {
      ...init,
      credentials: 'include',
      headers: {
        ...(init?.body !== undefined ? { 'content-type': 'application/json' } : {}),
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    throw new GoalApiError(0, 'network_error');
  }
  if (response.status === 204) return undefined as T;
  let body: { data?: T; error?: { code?: string } };
  try {
    body = (await response.json()) as typeof body;
  } catch {
    throw new GoalApiError(response.status, 'invalid_response');
  }
  if (!response.ok) throw new GoalApiError(response.status, body.error?.code ?? 'request_failed');
  return body.data as T;
}

function goalErrorMessage(error: unknown): string {
  if (error instanceof GoalApiError) {
    if (error.status === 401)
      return 'Your session has ended. Please sign in again to manage goals.';
    if (error.status === 404)
      return 'This goal is no longer available. Refresh your goals and try again.';
    if (error.status === 409)
      return 'This change conflicted with another request. Refresh your goals and try again.';
    if (error.code === 'unsafe_input')
      return 'This content cannot be stored as a wellness goal. Please revise the goal text.';
    if (error.code === 'validation_failed') return 'Please check the goal details and try again.';
  }
  return 'Goals are temporarily unavailable. Please try again.';
}

function localDate(timezone?: string): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(new Date());
  const part = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((item) => item.type === type)?.value ?? '';
  return `${part('year')}-${part('month')}-${part('day')}`;
}

export default function Home() {
  const [view, setView] = useState<
    'landing' | 'demo' | 'auth' | 'onboarding' | 'dashboard' | 'profile'
  >('landing');
  const [mode, setMode] = useState<'register' | 'login'>('register');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [timezone, setTimezone] = useState('UTC');
  const [selected, setSelected] = useState<string[]>([]);
  const [memoryConsent, setMemoryConsent] = useState(false);
  const [profile, setProfile] = useState<Profile>({});
  const [wellness, setWellness] = useState<Wellness>({ wellness_areas: [] });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [logoutBusy, setLogoutBusy] = useState(false);
  const [logoutError, setLogoutError] = useState('');
  const [saved, setSaved] = useState(false);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [goalsLoading, setGoalsLoading] = useState(false);
  const [goalsError, setGoalsError] = useState('');
  const [goalSuccess, setGoalSuccess] = useState('');
  const [goalFormOpen, setGoalFormOpen] = useState(false);
  const [goalSaving, setGoalSaving] = useState(false);
  const [goalFormError, setGoalFormError] = useState('');
  const [editingGoalId, setEditingGoalId] = useState<string | null>(null);
  const [goalDetails, setGoalDetails] = useState<Goal | null>(null);
  const [goalArea, setGoalArea] = useState('sleep');
  const [goalTitle, setGoalTitle] = useState('');
  const [goalDescription, setGoalDescription] = useState('');
  const [goalStartDate, setGoalStartDate] = useState(localDate());
  const [goalEndDate, setGoalEndDate] = useState('');
  const [goalStatus, setGoalStatus] = useState<GoalStatus>('active');
  const goalTitleRef = useRef<HTMLInputElement>(null);
  const goalActionRef = useRef<HTMLButtonElement>(null);
  const goalDetailsRef = useRef<HTMLElement>(null);
  const goalDetailsReturnRef = useRef<HTMLButtonElement | null>(null);
  const formErrorRef = useRef<HTMLParagraphElement>(null);
  const logoutErrorRef = useRef<HTMLParagraphElement>(null);
  const greeting = useMemo(
    () =>
      profile.display_name
        ? `Welcome back, ${profile.display_name}`
        : 'Welcome to your wellness space',
    [profile.display_name],
  );
  useEffect(() => {
    void loadAccount().catch(() => undefined);
  }, []);
  useEffect(() => {
    if (error) formErrorRef.current?.focus();
  }, [error]);
  useEffect(() => {
    if (logoutError) logoutErrorRef.current?.focus();
  }, [logoutError]);
  async function loadAccount() {
    const [account, p, w, consentResponse] = await Promise.all([
      call<{ onboarding: { complete: boolean } }>('/me'),
      call<Profile>('/me/profile'),
      call<Wellness>('/me/wellness-profile'),
      call<{ items: Consent[] }>('/me/consents'),
    ]);
    setProfile(p);
    setName(p.display_name ?? '');
    setTimezone(p.timezone ?? 'UTC');
    setWellness(w);
    setSelected(w.wellness_areas);
    const memoryDecision = consentResponse.items
      .filter((consent) => consent.consent_type === 'memory')
      .sort((left, right) => left.captured_at.localeCompare(right.captured_at))
      .at(-1);
    setMemoryConsent(memoryDecision?.decision === 'granted');
    setView(account.onboarding.complete ? 'dashboard' : 'onboarding');
    if (account.onboarding.complete) await loadGoals();
  }
  async function loadGoals() {
    setGoalsLoading(true);
    setGoalsError('');
    try {
      const result = await goalCall<{ items: Goal[] }>('');
      setGoals(result.items);
    } catch (e) {
      setGoalsError(goalErrorMessage(e));
    } finally {
      setGoalsLoading(false);
    }
  }
  function openGoalForm(goal?: Goal) {
    setGoalFormError('');
    setGoalSuccess('');
    setGoalDetails(null);
    setEditingGoalId(goal?.goal_id ?? null);
    setGoalArea(goal?.wellness_area ?? 'sleep');
    setGoalTitle(goal?.title ?? '');
    setGoalDescription(goal?.description ?? '');
    setGoalStartDate(goal?.start_date ?? localDate(profile.timezone));
    setGoalEndDate(goal?.end_date ?? '');
    setGoalStatus(goal?.status ?? 'active');
    setGoalFormOpen(true);
  }
  useEffect(() => {
    if (goalFormOpen) goalTitleRef.current?.focus();
  }, [goalFormOpen]);
  function closeGoalForm() {
    setGoalFormOpen(false);
    setGoalFormError('');
    window.setTimeout(() => goalActionRef.current?.focus(), 0);
  }
  async function saveGoal(event: React.FormEvent) {
    event.preventDefault();
    setGoalSaving(true);
    setGoalFormError('');
    setGoalsError('');
    setGoalSuccess('');
    const payload: GoalPayload = {
      wellness_area: goalArea,
      title: goalTitle,
      description: goalDescription,
      start_date: goalStartDate,
      ...(goalEndDate ? { end_date: goalEndDate } : {}),
    };
    if (editingGoalId) payload.end_date = goalEndDate;
    if (editingGoalId) {
      Object.assign(payload, { status: goalStatus });
    }
    try {
      await goalCall<Goal>(editingGoalId ? `/${editingGoalId}` : '', {
        method: editingGoalId ? 'PATCH' : 'POST',
        headers: { 'idempotency-key': crypto.randomUUID() },
        body: JSON.stringify(payload),
      });
      setGoalFormOpen(false);
      setGoalSuccess(editingGoalId ? 'Goal updated.' : 'Goal created.');
      await loadGoals();
      window.setTimeout(() => goalActionRef.current?.focus(), 0);
    } catch (e) {
      setGoalFormError(goalErrorMessage(e));
      goalTitleRef.current?.focus();
    } finally {
      setGoalSaving(false);
    }
  }
  useEffect(() => {
    if (goalDetails) goalDetailsRef.current?.focus();
  }, [goalDetails]);
  async function viewGoal(goalId: string, trigger: HTMLButtonElement) {
    setGoalsError('');
    setGoalSuccess('');
    goalDetailsReturnRef.current = trigger;
    try {
      setGoalDetails(await goalCall<Goal>(`/${goalId}`));
    } catch (e) {
      setGoalsError(goalErrorMessage(e));
    }
  }
  function closeGoalDetails() {
    setGoalDetails(null);
    window.setTimeout(() => goalDetailsReturnRef.current?.focus(), 0);
  }
  async function archiveGoal(goal: Goal) {
    setGoalsError('');
    setGoalSuccess('');
    try {
      await goalCall<Goal>(`/${goal.goal_id}`, {
        method: 'PATCH',
        headers: { 'idempotency-key': crypto.randomUUID() },
        body: JSON.stringify({ status: 'archived' }),
      });
      setGoalSuccess('Goal archived.');
      setGoalDetails(null);
      await loadGoals();
      window.setTimeout(() => goalActionRef.current?.focus(), 0);
    } catch (e) {
      setGoalsError(goalErrorMessage(e));
    }
  }
  async function deleteGoal(goal: Goal) {
    if (
      !window.confirm(
        'Soft-delete this goal from your list? This does not promise permanent erasure.',
      )
    )
      return;
    setGoalsError('');
    setGoalSuccess('');
    try {
      await goalCall<void>(`/${goal.goal_id}`, {
        method: 'DELETE',
        headers: { 'idempotency-key': crypto.randomUUID() },
      });
      setGoalSuccess('Goal removed from your list.');
      setGoalDetails(null);
      await loadGoals();
      window.setTimeout(() => goalActionRef.current?.focus(), 0);
    } catch (e) {
      setGoalsError(goalErrorMessage(e));
    }
  }
  async function authenticate(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await call<{ account_id: string; authenticated: boolean }>(`/auth/${mode}`, {
        method: 'POST',
        headers: { 'idempotency-key': crypto.randomUUID() },
        body: JSON.stringify({ email }),
      });
      await loadAccount();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to continue');
    } finally {
      setBusy(false);
    }
  }
  async function saveOnboarding(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await call<Profile>('/me/profile', {
        method: 'PATCH',
        body: JSON.stringify({ display_name: name, timezone, locale: 'en-US' }),
      });
      await call<Wellness>('/me/wellness-profile', {
        method: 'PATCH',
        body: JSON.stringify({ wellness_areas: selected }),
      });
      await call('/me/consents', {
        method: 'POST',
        headers: { 'idempotency-key': crypto.randomUUID() },
        body: JSON.stringify({
          consent_type: 'memory',
          policy_version: 'memory-foundation-v1',
          decision: memoryConsent ? 'granted' : 'denied',
        }),
      });
      await loadAccount();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to save');
    } finally {
      setBusy(false);
    }
  }
  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const [p, w] = await Promise.all([
        call<Profile>('/me/profile', {
          method: 'PATCH',
          body: JSON.stringify({
            display_name: profile.display_name,
            locale: profile.locale,
            timezone: profile.timezone,
          }),
        }),
        call<Wellness>('/me/wellness-profile', {
          method: 'PATCH',
          body: JSON.stringify({
            wellness_areas: wellness.wellness_areas,
            coaching_style: wellness.coaching_style,
          }),
        }),
      ]);
      setProfile(p);
      setWellness(w);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to save');
    } finally {
      setBusy(false);
    }
  }
  async function signOut() {
    setLogoutBusy(true);
    setLogoutError('');
    try {
      await call('/auth/logout', {
        method: 'POST',
        headers: { 'idempotency-key': crypto.randomUUID() },
      });
      setView('landing');
    } catch (cause) {
      if (cause instanceof ApiRequestError && cause.status === 401) {
        setView('landing');
      } else {
        setLogoutError('Sign out did not complete. Your session is still open; try again.');
      }
    } finally {
      setLogoutBusy(false);
    }
  }

  if (view === 'landing')
    return (
      <main className="shell">
        <nav>
          <span className="brand">
            Nexus<span>AI</span>
          </span>
          <button
            className="link"
            onClick={() => {
              setMode('login');
              setView('auth');
            }}
          >
            Sign in
          </button>
        </nav>
        <section className="hero">
          <p className="eyebrow">Your everyday wellness companion</p>
          <h1>Small steps, thoughtfully supported.</h1>
          <p className="lede">
            NexusAI helps you build healthy routines, reflect on progress, and stay accountable.
            Wellness guidance only—not a doctor.
          </p>
          <div className="actions">
            <button
              className="primary"
              onClick={() => {
                setMode('register');
                setView('auth');
              }}
            >
              Create a free account
            </button>
            <button className="secondary" onClick={() => setView('demo')}>
              Try the safe demo
            </button>
          </div>
          <div className="demo-card">
            <span className="dot" /> Guest mode · No private data saved{' '}
            <strong>Explore how it works →</strong>
          </div>
        </section>
        <footer>Private by design · You control personalization · Not medical advice</footer>
      </main>
    );
  if (view === 'demo')
    return (
      <main className="shell narrow">
        <button className="back" onClick={() => setView('landing')}>
          ← Home
        </button>
        <div className="card">
          <p className="eyebrow">Guest demo</p>
          <h1>A gentle next step.</h1>
          <p className="lede">
            Choose one small, general wellness action for today—like taking a short walk, drinking
            water, or setting a consistent bedtime.
          </p>
          <div className="demo-card">
            <span className="dot" /> This example is static and non-persistent. It does not collect
            health details or create memory.
          </div>
          <div className="actions">
            <button
              className="primary"
              onClick={() => {
                setMode('register');
                setView('auth');
              }}
            >
              Create an account
            </button>
            <button
              className="secondary"
              onClick={() => {
                setMode('login');
                setView('auth');
              }}
            >
              Sign in
            </button>
          </div>
        </div>
      </main>
    );
  if (view === 'auth')
    return (
      <main className="shell narrow">
        <button className="back" onClick={() => setView('landing')}>
          ← Back
        </button>
        <div className="card">
          <span className="brand">
            Nexus<span>AI</span>
          </span>
          <h1>{mode === 'register' ? 'Create your account' : 'Welcome back'}</h1>
          <p className="muted">
            Development authentication boundary. No password or provider is connected yet.
          </p>
          <form onSubmit={authenticate} aria-describedby={error ? 'app-form-error' : undefined}>
            <label>
              Email
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </label>
            <button className="primary full" disabled={busy}>
              {busy ? 'Please wait…' : mode === 'register' ? 'Continue' : 'Sign in'}
            </button>
          </form>
          <button
            className="link switch"
            onClick={() => setMode(mode === 'register' ? 'login' : 'register')}
          >
            {mode === 'register'
              ? 'Already have an account? Sign in'
              : 'New here? Create an account'}
          </button>
          {error && (
            <p className="error" id="app-form-error" role="alert" tabIndex={-1} ref={formErrorRef}>
              {error}
            </p>
          )}
        </div>
      </main>
    );
  if (view === 'onboarding')
    return (
      <main className="shell narrow">
        <div className="card">
          <div className="step">Step 1 of 1 · You can edit this later</div>
          <h1>Let’s make this yours.</h1>
          <p className="muted">
            Tell us only what helps with everyday wellness. NexusAI is not a doctor, and
            personalization is always under your control.
          </p>
          <form onSubmit={saveOnboarding} aria-describedby={error ? 'app-form-error' : undefined}>
            <label>
              Your name
              <input
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="How should we greet you?"
              />
            </label>
            <label>
              Timezone
              <select value={timezone} onChange={(e) => setTimezone(e.target.value)}>
                <option>UTC</option>
                <option>America/Los_Angeles</option>
                <option>America/New_York</option>
                <option>Europe/London</option>
                <option>Asia/Dhaka</option>
              </select>
            </label>
            <fieldset aria-describedby="focus-help">
              <legend>What would you like to focus on?</legend>
              <p className="muted" id="focus-help">
                Choose at least one area to continue.
              </p>
              <div className="choices">
                {areas.map((area) => (
                  <label
                    className={`choice ${selected.includes(area) ? 'selected' : ''}`}
                    key={area}
                  >
                    <input
                      type="checkbox"
                      checked={selected.includes(area)}
                      onChange={() =>
                        setSelected((old) =>
                          old.includes(area) ? old.filter((x) => x !== area) : [...old, area],
                        )
                      }
                    />
                    <span>{area}</span>
                  </label>
                ))}
              </div>
            </fieldset>
            <label className="consent">
              <input
                type="checkbox"
                checked={memoryConsent}
                onChange={(event) => setMemoryConsent(event.target.checked)}
              />
              <span>
                <strong>Allow future personalization memory</strong>
                <small>
                  Optional and off by default. This slice records your choice but creates no
                  memories. You can revoke it later.
                </small>
              </span>
            </label>
            <button className="primary full" disabled={busy || selected.length === 0}>
              {busy ? 'Saving…' : 'Continue to my dashboard'}
            </button>
          </form>
          {error && (
            <p className="error" id="app-form-error" role="alert" tabIndex={-1} ref={formErrorRef}>
              {error}
            </p>
          )}
        </div>
      </main>
    );
  if (view === 'profile')
    return (
      <main className="shell narrow">
        <button className="back" onClick={() => setView('dashboard')}>
          ← Dashboard
        </button>
        <div className="card">
          <span className="eyebrow">Profile & settings</span>
          <h1>Edit your setup</h1>
          <form onSubmit={saveProfile} aria-describedby={error ? 'app-form-error' : undefined}>
            <label>
              Name
              <input
                value={profile.display_name ?? ''}
                onChange={(e) => setProfile({ ...profile, display_name: e.target.value })}
              />
            </label>
            <label>
              Locale
              <input
                value={profile.locale ?? ''}
                onChange={(e) => setProfile({ ...profile, locale: e.target.value })}
              />
            </label>
            <label>
              Timezone
              <input
                value={profile.timezone ?? ''}
                onChange={(e) => setProfile({ ...profile, timezone: e.target.value })}
              />
            </label>
            <fieldset>
              <legend>Focus areas</legend>
              <div className="choices">
                {areas.map((area) => (
                  <label
                    className={`choice ${wellness.wellness_areas.includes(area) ? 'selected' : ''}`}
                    key={area}
                  >
                    <input
                      type="checkbox"
                      checked={wellness.wellness_areas.includes(area)}
                      onChange={() =>
                        setWellness({
                          ...wellness,
                          wellness_areas: wellness.wellness_areas.includes(area)
                            ? wellness.wellness_areas.filter((x) => x !== area)
                            : [...wellness.wellness_areas, area],
                        })
                      }
                    />
                    {area}
                  </label>
                ))}
              </div>
            </fieldset>
            <button className="primary full" disabled={busy}>
              {busy ? 'Saving…' : saved ? 'Saved ✓' : 'Save changes'}
            </button>
          </form>
          {error && (
            <p className="error" id="app-form-error" role="alert" tabIndex={-1} ref={formErrorRef}>
              {error}
            </p>
          )}
        </div>
      </main>
    );
  return (
    <main className="shell app">
      <nav>
        <span className="brand">
          Nexus<span>AI</span>
        </span>
        <div>
          <button className="link" onClick={() => setView('dashboard')}>
            Home
          </button>
          <button className="link" onClick={() => setView('profile')}>
            Profile
          </button>
          <button className="link" onClick={() => void signOut()} disabled={logoutBusy}>
            {logoutBusy ? 'Signing out…' : logoutError ? 'Retry sign out' : 'Sign out'}
          </button>
        </div>
      </nav>
      {logoutError && (
        <p className="error logout-error" role="alert" tabIndex={-1} ref={logoutErrorRef}>
          {logoutError}
        </p>
      )}
      <section className="dashboard">
        <p className="eyebrow">Your wellness dashboard</p>
        <h1>{greeting}</h1>
        <p className="lede">A calm place to keep your next healthy step in view.</p>
        <div className="grid">
          <article className="panel">
            <div className="panel-head">
              <h2>Your focus areas</h2>
              <span className="badge">{wellness.wellness_areas.length} selected</span>
            </div>
            <div className="chips">
              {wellness.wellness_areas.map((area) => (
                <span key={area}>{area}</span>
              ))}
            </div>
          </article>
          <article className="panel empty">
            <h2>Today’s plan</h2>
            <p>Your personalized plan will appear here when planning is available.</p>
            <span className="coming">Coming in a future phase</span>
          </article>
          <article className="panel empty">
            <h2>AI Companion</h2>
            <p>Chat is not enabled in this foundation slice. Your data stays yours.</p>
            <span className="coming">Provider-neutral by design</span>
          </article>
          <article className="panel">
            <h2>Onboarding</h2>
            <p className="success">✓ Complete</p>
            <button
              className="secondary"
              onClick={() => {
                setName(profile.display_name ?? '');
                setView('onboarding');
              }}
            >
              Edit wellness setup
            </button>
          </article>
        </div>
        <section className="panel goals-panel" aria-labelledby="goals-heading">
          <div className="panel-head">
            <div>
              <p className="eyebrow">Goals</p>
              <h2 id="goals-heading">Your goals</h2>
            </div>
            <button
              ref={goalActionRef}
              className="primary"
              onClick={() => openGoalForm()}
              disabled={goalsLoading || goalSaving}
            >
              + Create goal
            </button>
          </div>
          <p className="muted goal-purpose">
            Goals are private, user-provided wellness information for your account. They are not
            used for AI training or automatically saved as memory. They may be cleared when this
            development service restarts.
          </p>
          {goalsLoading && <p role="status">Loading your goals…</p>}
          {goalsError && (
            <div className="error" role="alert">
              <p>{goalsError}</p>
              {goalsError.startsWith('Your session') ? (
                <button className="secondary" onClick={() => void signOut()}>
                  Return to sign in
                </button>
              ) : (
                <button className="secondary" onClick={() => void loadGoals()}>
                  Try again
                </button>
              )}
            </div>
          )}
          {goalSuccess && (
            <p className="success" role="status">
              {goalSuccess}
            </p>
          )}
          {!goalsLoading && !goalsError && goals.length === 0 && (
            <div className="goal-empty">
              <h3>No goals yet</h3>
              <p>Create a wellness goal to get started.</p>
            </div>
          )}
          {!goalsLoading && goals.length > 0 && (
            <ul className="goal-list" aria-label="Your wellness goals">
              {goals.map((goal) => (
                <li className="goal-card" key={goal.goal_id}>
                  <div className="goal-card-main">
                    <h3>{goal.title}</h3>
                    <p className="muted">
                      {goal.wellness_area} · {goal.status}
                    </p>
                    <p className="goal-dates">
                      {goal.start_date}
                      {goal.end_date ? ` – ${goal.end_date}` : ''}
                    </p>
                  </div>
                  <div className="goal-actions">
                    <button
                      className="secondary"
                      onClick={(event) => void viewGoal(goal.goal_id, event.currentTarget)}
                    >
                      View
                    </button>
                    <button className="secondary" onClick={() => openGoalForm(goal)}>
                      Edit
                    </button>
                    {goal.status !== 'archived' && (
                      <button className="secondary" onClick={() => void archiveGoal(goal)}>
                        Archive
                      </button>
                    )}
                    <button className="danger" onClick={() => void deleteGoal(goal)}>
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
          {goalDetails && (
            <section
              className="goal-details"
              aria-labelledby="goal-details-heading"
              tabIndex={-1}
              ref={goalDetailsRef}
            >
              <div className="panel-head">
                <h3 id="goal-details-heading">Goal details</h3>
                <button className="link" onClick={closeGoalDetails}>
                  Close details
                </button>
              </div>
              <dl>
                <dt>Title</dt>
                <dd>{goalDetails.title}</dd>
                <dt>Wellness area</dt>
                <dd>{goalDetails.wellness_area}</dd>
                <dt>Status</dt>
                <dd>{goalDetails.status}</dd>
                <dt>Dates</dt>
                <dd>
                  {goalDetails.start_date}
                  {goalDetails.end_date ? ` – ${goalDetails.end_date}` : ''}
                </dd>
                {goalDetails.description && (
                  <>
                    <dt>Description</dt>
                    <dd>{goalDetails.description}</dd>
                  </>
                )}
              </dl>
            </section>
          )}
          {goalFormOpen && (
            <section className="goal-form-wrap" aria-labelledby="goal-form-heading">
              <h3 id="goal-form-heading" tabIndex={-1}>
                {editingGoalId ? 'Edit goal' : 'Create a goal'}
              </h3>
              <p className="muted">
                Add a general wellness goal you choose. Goal details stay on your account and are
                not used for memory or AI training.
              </p>
              <form
                onSubmit={saveGoal}
                aria-describedby={goalFormError ? 'goal-form-error' : 'goal-purpose'}
              >
                <label htmlFor="goal-area">Wellness area</label>
                <select
                  id="goal-area"
                  value={goalArea}
                  onChange={(event) => setGoalArea(event.target.value)}
                >
                  {areas.map((area) => (
                    <option key={area} value={area}>
                      {area}
                    </option>
                  ))}
                </select>
                <label htmlFor="goal-title">Goal title</label>
                <input
                  id="goal-title"
                  ref={goalTitleRef}
                  required
                  maxLength={160}
                  value={goalTitle}
                  onChange={(event) => setGoalTitle(event.target.value)}
                />
                <label htmlFor="goal-description">Description (optional)</label>
                <textarea
                  id="goal-description"
                  maxLength={2000}
                  value={goalDescription}
                  onChange={(event) => setGoalDescription(event.target.value)}
                />
                <label htmlFor="goal-start-date">Start date</label>
                <input
                  id="goal-start-date"
                  required
                  type="date"
                  value={goalStartDate}
                  onChange={(event) => setGoalStartDate(event.target.value)}
                />
                <label htmlFor="goal-end-date">End date (optional)</label>
                <input
                  id="goal-end-date"
                  type="date"
                  min={goalStartDate}
                  value={goalEndDate}
                  onChange={(event) => setGoalEndDate(event.target.value)}
                />
                {editingGoalId && (
                  <>
                    <label htmlFor="goal-status">Status</label>
                    <select
                      id="goal-status"
                      value={goalStatus}
                      onChange={(event) => setGoalStatus(event.target.value as GoalStatus)}
                    >
                      {goalStatuses.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                  </>
                )}
                {goalFormError && (
                  <p className="error" id="goal-form-error" role="alert">
                    {goalFormError}
                  </p>
                )}
                <div className="goal-actions">
                  <button className="primary" disabled={goalSaving}>
                    {goalSaving ? 'Saving…' : editingGoalId ? 'Save goal' : 'Create goal'}
                  </button>
                  <button
                    className="secondary"
                    type="button"
                    onClick={closeGoalForm}
                    disabled={goalSaving}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </section>
          )}
        </section>
      </section>
      <footer>
        Wellness support only · Not medical advice ·{' '}
        <button className="inline" onClick={() => setView('profile')}>
          Manage your information
        </button>
      </footer>
    </main>
  );
}
