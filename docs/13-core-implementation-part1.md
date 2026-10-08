# Phase 13 — Core Application Implementation — Part 1 of 3

**Status:** Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Authorized slice:** Guest → Account/Auth Boundary → Onboarding → Basic Wellness Profile → Home Dashboard Foundation

**Current gate:** Phase 13 Part 1 is APPROVED. Phase 13 Part 2 is AUTHORIZED / IN PROGRESS for the bounded Goal Management slice. Findings and pending-review statements in the historical sections below record the earlier Part 1 review state and are not current project status.

## Scope implemented

This controlled vertical slice provides a working local-development journey from the public landing page through a non-persistent guest demonstration, development-only account boundary, onboarding, basic profile/wellness storage, and an authenticated dashboard shell. It does not implement the rest of NexusAI.

## Files created or changed

- `packages/app-core/*`: slice records, validation, in-memory repositories, onboarding state and development-only authentication adapter.
- `packages/contracts/*`: approved Phase 07 success/error envelope types and helpers.
- `apps/api/src/app.ts`, `idempotency.ts`: approved slice routes, API projections, cookie/session boundary, ownership enforcement, stable error handling and process-local idempotency replay.
- `apps/web/app/page.tsx`, `layout.tsx`, `globals.css`: responsive slice UI with native, keyboard-focusable wellness checkboxes, visible focus, selection instructions and accessible onboarding errors.
- `tests/slice-api.test.ts`: authentication, ownership, validation, request/response contract, request-ID and idempotency tests.
- Root/package configuration and canonical phase-status metadata.

## API routes implemented

The implemented business routes use the approved `/api/v1` namespace. The final remediation below corrects the identified request/error discrepancies; it does not certify full Phase 07 implementation:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /me`
- `GET`, `PATCH /me/profile`
- `GET`, `PATCH /me/wellness-profile`
- `GET`, `POST /me/consents`

The existing infrastructure routes `/health/live`, `/health/ready`, `/api/v1`, and protected `/internal/v1` remain. No other business operation from the 77-operation catalog was implemented.

## Database entities used

The slice maps only to approved `accounts`, `auth_sessions`, `user_profiles`, `wellness_profiles`, and `consent_records`. The application uses an in-memory development repository; no SQL, migration, real PostgreSQL connection, production credentials, provider or region was introduced. Data resets when the API process restarts. The approved 21-entity model is unchanged.

## UI screens and states

- Public landing with wellness-only boundary.
- Static, non-sensitive, non-persistent guest demo.
- Sign-up/sign-in shell using the development adapter.
- Onboarding for display name, locale/timezone, allow-listed wellness focus areas and separate optional memory-consent choice.
- Dashboard with greeting, focus summary, onboarding status and truthful empty states for plans and AI Companion.
- Profile/settings editor and sign-out.
- Loading, error, empty, focus and mobile-responsive states.

## Authentication approach

`DevAuthService` is an in-memory adapter that throws in production. It stores only SHA-256 session-token hashes, exposes no password field, contains no credentials and issues an HttpOnly/SameSite development cookie. Logout uses `SessionIdentityAdapter`: the adapter supplies a non-secret, credential-bound replay scope, resolves the principal, revokes the session and optionally clears its own cookie. The scope remains stable after revocation for exact retries; it does not authenticate a request. A new logout execution requires an authenticated user with an account and session. Missing/invalid sessions return `401`; adapter failures return a safe `503`. Production auth provider, MFA, recovery assurance and session policy remain TBD.

## Security controls

- Every `/me/*` operation derives account ownership from the authenticated principal; request account IDs are not accepted.
- Profile/wellness PATCH request builders explicitly select writable fields; server-owned response fields are never copied into mutation bodies. The API continues to reject ownership overrides and unapproved wellness areas.
- The bounded `coaching_style` free-text field passes a deterministic storage policy before any wellness update is committed. Explicit diagnosis/prescription/medication/dosage, clinical triage/treatment, guaranteed-cure, clinician-replacement and emergency-service claims covered by the policy return `422 unsafe_input` with a safe field/issue pair. Rejected text is neither stored nor echoed. Legitimate wellness coaching remains supported; unsupported context fields remain rejected.
- `SliceStore` permits only development/test environments, checks the real process environment as well as explicit configuration, and guards construction and every read/write. Production API startup fails before a development store/server is created; a configured database URL alone never makes production ready. No persistent adapter is configured or selected by this batch.
- Guest content is static and never promoted to a private profile.
- API request/response fields use `snake_case`; successes and errors use the approved Phase 07 envelopes.
- API responses receive a server-generated request ID; body-bearing success/error envelopes correlate it with `x-request-id`. User/auth responses use `private, no-store`, and errors, including unmatched-route `404 not_found`, use `no-store`. Successful `204` logout has no response body.
- Required Phase 13 mutations use an operation- and principal/session-scoped process-local idempotency store. Exact retries replay the original result, changes to supported normalized payloads return `409 idempotency_key_reused`, and consent retries do not append duplicate records. The existing MEDIUM logout-body issue remains: unsupported bodies are discarded before hashing. This development state resets when the API process restarts.
- Public consent writes accept only `{consent_type, policy_version, decision}`. The server derives internal `capture_source` from onboarding completion at first execution; replay preserves the original record even if onboarding state changes.
- Memory remains off by default; onboarding records a granted or denied decision but creates no memory.
- No raw token is stored, no sensitive payload is logged and the dev adapter cannot run in production.

## Tests

Targeted tests cover unauthenticated denial, Phase 07 envelopes and naming, request-ID correlation, no-store headers, registration/session behavior, owned profile updates, cross-user isolation, wellness allow-list validation, consent/onboarding, first idempotent execution, exact and concurrent replay, changed-payload rejection, per-user scope, consent duplicate prevention and repeat logout. Foundation tests continue to cover safety, memory revocation, worker behavior, configuration and telemetry redaction.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

### HIGH remediation batch 1 validation

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

The Batch 1 and Batch 2 results and closure assessment below preserve the earlier evidence. The subsequent final re-review retained HIGH #1, #2 and #4; current remediation evidence follows these historical sections.

- Targeted tests: pass — 2 files, 17 tests.
- Typecheck: pass across all workspace projects.
- Targeted formatting check: pass.
- Lint: pass with the three pre-existing `no-console` warnings; those LOW/MEDIUM cleanup items are outside this batch.
- Production build: pass; the pre-existing Next.js ESLint-plugin warning remains outside this batch.
- Secret scan and architecture guardrails: pass.

### HIGH remediation batch 2 evidence

Changed files in this batch:

- `packages/app-core/src/index.ts`: guarded development repository and development session adapter.
- `packages/safety-core/src/index.ts`: bounded clinical-content storage validation.
- `packages/auth-core/src/index.ts`: provider-neutral logout replay and cookie-clearance contract.
- `packages/config/src/index.ts`: reject unknown runtime environments.
- `apps/api/src/app.ts`: guarded startup, authenticated logout and adapter-owned replay/response handling.
- `apps/web/app/page.tsx`, `apps/web/app/globals.css`: keyboard selection instructions, focusable checkbox styling, disabled-state styling, and preservation of JSON headers on onboarding requests with idempotency keys.
- `tests/high-remediation.test.ts`, `tests/slice-api.test.ts`: safety, environment and external-adapter regression coverage.
- `tests/browser/onboarding.spec.ts`, `playwright.config.ts`: real-browser keyboard-only onboarding and error-recovery tests against the local API.
- `package.json`, `pnpm-lock.yaml`, `.gitignore`: test-only Playwright dependency/runner, dependency-ordered foundation build, and generated test-artifact exclusions.
- This document: implementation evidence and limitations; no other canonical document changed.

Validation on 2026-09-19:

- Root foundation/API tests: **pass, 62 tests in 4 files**, including 41 Batch 2 cases. Safety tests check atomic rejection, unchanged persisted state, safe errors and legitimate wellness text; production tests cover direct construction/use, configuration override attempts and unavailable storage; external-adapter tests cover session isolation, concurrent/exact replay, missing/invalid/revoked sessions and safe revocation failure.
- Keyboard tests: **pass, 2 tests**, headless installed Chrome against the real local web/API services. All seven native options are reached by Tab, have a visible 3px focus outline and toggle with Space; Continue disables/enables correctly, and both normal onboarding and keyboard correction after an announced API error reach the dashboard. The captured focus screenshot was visually inspected. Run `pnpm test:keyboard` after installing Playwright Chromium, or set `PLAYWRIGHT_CHANNEL=chrome` to use installed Chrome.
- Repository-wide `pnpm test`: **fails** because the existing recursive package scripts run Vitest from packages/apps with no local test files. The root suite above covers all current Vitest test files. Existing duplicate `compilerOptions` keys also produce warnings. Neither unrelated harness cleanup is included in this batch.
- Formatting: **pass** for the repository check and new Playwright configuration.
- Typecheck and production build: **pass** across all workspace projects via `pnpm typecheck`, which runs the full recursive production build before typechecking. The existing Next.js ESLint-plugin warning remains; this build result does not imply that production API startup is permitted.
- Lint: **pass**, 0 errors and the 3 existing `no-console` warnings.
- Architecture guardrails and secret scan: **pass**.
- Dependency audit: **0 HIGH/CRITICAL**, 3 moderate package entries across 2 advisories: PostCSS (`GHSA-fxqj-rqcc-2cmp`) and Vitest/its mocker (`GHSA-82fw-gwwq-j7x9`). `pnpm audit --audit-level=high` passes; the full audit is not clean. These MEDIUM maintenance items remain outside the authorized four findings.
- Batch 1 regression coverage: API envelopes, server request-ID correlation, snake_case, no-store headers, exact/concurrent idempotency replay, changed-payload rejection and duplicate prevention pass. The API catalog remains unchanged at 77 operations; canonical Part 1 status remains blocked and Part 2 remains unauthorized.

No unresolved implementation item remains among the four scoped HIGH findings under the bounded development behavior tested above; closure is subject to re-review. Remaining non-HIGH items are the moderate dependency advisories, three console warnings, Next.js ESLint-plugin warning and the existing recursive-test/duplicate-tsconfig issues. Unresolved product/production decisions below remain unchanged.

Initial local tooling failures (missing pnpm shim, invalid generated package output and a stale Next.js dependency junction) were resolved with a temporary Corepack shim, dependency builds and lockfile-based dependency restoration. No production configuration or infrastructure was added. A browser-download network reset was avoided by using the installed Chrome test channel.

## Final HIGH remediation batch — pending re-review

Only HIGH #1, #2 and #4 are addressed. Implementation and regression checks are remediation evidence; these findings are not declared closed before re-review. Phase 13 Part 1 remains blocked and is not approved.

- **HIGH #1:** Searched every Markdown document in `docs/` and README for current phase/authorization claims. Current metadata now distinguishes Phase 04–12 approval, Phase 13 authorization, blocked Part 1 and unauthorized/unstarted Part 2. Old review outcomes, status rows and entry criteria are retained with `HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS` labels. Technical architecture and TBD decisions are unchanged.
- **HIGH #2:** Profile/settings PATCH bodies contain only writable fields. Unknown API routes use the normative `404 not_found` envelope, server request-ID correlation and `no-store`. Consent accepts the three approved public fields; capture metadata is server-owned, with no mandatory public `capture_source` field. All 77 catalog operation rows remain unchanged.
- **HIGH #4:** Extended the bounded lexical gate for explicit medication vocabulary, scheduled `take <substance>` directions, written quantities and gram-based dosage instructions. The three reported medication examples and additional schedule/dosage variants are rejected atomically. Ordinary wellness requests, walks, breaks and breathing remain allowed. The rules do not infer diagnoses or implement a medical knowledge engine; raw rejected content is not logged or echoed.

Changed application files: `apps/api/src/app.ts`, `apps/web/app/page.tsx`, `packages/safety-core/src/index.ts`.

Changed/added tests: `tests/slice-api.test.ts`, `tests/high-remediation.test.ts`, `tests/final-high-remediation.test.ts`, `tests/browser/profile-save.spec.ts`. The new browser regression asserts exact outgoing PATCH bodies, successful profile/wellness responses, request-ID/cache contracts and persistence after reload. API regressions cover unknown routes and three-field consent including duplicate prevention, changed-payload rejection and replay after onboarding completion. Safety regressions verify non-persistence and legitimate wellness acceptance.

Documentation files changed: README, every existing Phase 00–12 Markdown document except `05-database-design.md` (already consistent), and this report. These are status/history clarifications, not changes to technical contracts or architecture.

Validation on 2026-09-19 for this batch:

| Check                                      | Actual result                                                                                                                                                                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pnpm test:foundation`                     | PASS: 90 tests in 5 files, including 62 safety/production/external-adapter remediation cases and 7 new API regressions. This command runs all current root Vitest test files after dependency builds.                                      |
| `pnpm test:keyboard` with installed Chrome | PASS: 3 browser tests, comprising both keyboard onboarding tests and the new profile/wellness save regression.                                                                                                                             |
| Profile / wellness save probes             | PASS: both PATCH responses are `200`, outgoing bodies contain only writable fields, and edits survive reload.                                                                                                                              |
| Unknown-route probes                       | PASS: public and `/me` unknown routes return `404 not_found`, safe nested errors, server-generated correlated IDs and `no-store`.                                                                                                          |
| Three-field consent probe                  | PASS: `201`, correct stored decision, server-derived capture metadata, exact replay across onboarding completion, no duplicate history and `409` for changed supported payload.                                                            |
| Safety probes                              | PASS: reported medication inputs and additional dosage/schedule cases return `422 unsafe_input` without altering stored state; all four requested legitimate wellness examples return `200` and read back correctly.                       |
| Formatting                                 | PASS: root `format:check` plus supplemental checks for this document and Playwright configuration.                                                                                                                                         |
| Lint                                       | PASS: 0 errors, 3 existing console warnings. Two unused callback-parameter errors introduced during this batch were removed before the successful rerun.                                                                                   |
| Production build and typecheck             | PASS across all 15 workspace projects through `pnpm typecheck` inside `pnpm check`; it runs the full recursive production build first. The existing Next.js ESLint-plugin warning remains.                                                 |
| Recursive `pnpm test` / `pnpm check`       | FAIL: exit 1 at package-level Vitest discovery (`No test files found`). Formatting, lint, production build and typecheck passed before this known harness failure; the final redundant build stage of `check` was not reached.             |
| Architecture guardrails / secret scan      | PASS via `pnpm guardrails`.                                                                                                                                                                                                                |
| Full dependency audit                      | FAIL: exit 1; 3 moderate package entries across PostCSS `GHSA-fxqj-rqcc-2cmp` and Vitest/mocker `GHSA-82fw-gwwq-j7x9`; 0 high/critical.                                                                                                    |
| Documentation/scope verification           | PASS: all 77 API catalog rows and the entire technical contract body are unchanged; pre-existing TBD decision text is preserved. Only the three application files, four test files and status/evidence documentation listed above changed. |

No failure remains in the six focused remediation probes. Formal closure of HIGH #1, #2 and #4 remains pending re-review; this batch does not approve the phase. Production fail-closed behavior, provider-neutral logout, keyboard onboarding, API envelopes/IDs/cache headers, supported idempotency replay, duplicate prevention and ownership isolation retain passing regression coverage.

Remaining **MEDIUM** findings outside this batch: auth-strict rate-limit enforcement; recursive `pnpm test/check` configuration; Windows web dev port expansion; SPA/form-error focus and failed-logout handling; memory-consent restoration after reload; unsupported logout-body normalization; moderate dependency advisories. Remaining **LOW** findings: three console warnings, Next.js ESLint-plugin warning, and duplicate tsconfig keys. No unrelated remediation is included.

## Known limitations and deferred features

Persistence and idempotency replay state are process-local and development-only; both reset when the API process restarts. There is no email verification, password/credential flow, recovery, MFA, real database, production auth, AI, chat, plans, goals, tasks, reminders, progress, payment, voice, mobile app, wearable integration, admin experience or deployment. Dashboard future areas intentionally show truthful empty states.

The wellness free-text gate is a bounded lexical validation policy, not a clinical classifier, diagnosis engine, triage implementation or proof of complete multilingual/paraphrase detection. Production safety evaluation, governance, field-level consent/encryption and the wider approved architecture are not claimed complete by these development tests.

## Remaining TBD decisions

Launch geography/jurisdiction, minimum age and age-band policy, production authentication/MFA/session baseline, AI provider retention/training/region, memory deletion propagation, admin/support roles, safety ownership, retention/legal hold/backup semantics, RTO/RPO, beta scale and cost remain `TBD / Pending Decision`.

## Approved-document consistency

The Phase 12 approval and explicit Phase 13 authorization are recorded in `12-implementation-foundation-final-review.md`. Phases 04–12 are APPROVED; Phase 13 is AUTHORIZED / IN PROGRESS; Phase 13 Part 1 is BLOCKED — HIGH REMEDIATION / RE-REVIEW; Phase 13 Part 2 is NOT AUTHORIZED / NOT STARTED. The final batch addresses only the three findings retained by re-review (#1, #2 and #4) and protects the previous production, logout and keyboard fixes. This is remediation evidence, not Phase 13 Part 1 approval or a claim of full contract compliance or full accessibility.

**PHASE 13 PART 1 — BLOCKED — HIGH REMEDIATION / RE-REVIEW**
