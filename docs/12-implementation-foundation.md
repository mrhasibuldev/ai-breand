# Phase 12 — Implementation Foundation

**Phase 12 Status:** APPROVED  
**Phase 13 Status:** AUTHORIZED / IN PROGRESS  
**Phase 13 Authorization:** EXPLICIT USER APPROVAL RECEIVED  
**Current project status:** Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

The foundation report below records the Phase 12 scope. At that time: Feature implementation is not started. Phase 13 Part 1 implementation is recorded separately in `13-core-implementation-part1.md`.

## Purpose

This document describes the development foundation for **NexusAI — Personal AI Health & Wellness Companion**. It turns the approved Phase 00–11 decisions into a small, modular TypeScript monorepo without implementing product features.

Part 2 adds only replaceable boundaries, validation contracts, local fakes, guardrails, and CI checks. It does not add business workflows or production integrations.

## Source of truth and boundaries

The canonical requirements remain `docs/00` through `docs/11`. The approved database model (21 entities), API contract (77 planned operations and `/api/v1`, `/internal/v1` prefixes), AI/memory/safety rules, privacy controls, and unresolved TBD decisions are unchanged. This phase adds scaffolding only; it does not replace those documents.

## Repository layout

```text
apps/
  web/       Next.js web shell and route boundary
  api/       Fastify HTTP composition and health endpoints
  worker/    Background-job entry point and job-kind boundary
packages/
  config/ observability/ contracts/ domain/ policy/
  auth-core/ ai-core/
database/    Database implementation boundary (no migrations yet)
tests/       Representative foundation tests
docs/        Phase-gated project documentation
```

The API is intentionally a modular monolith. Domain, policy, persistence, provider, and transport concerns are kept behind package/module boundaries so later implementation can evolve without changing public contracts.

## Runtime and tooling baseline

- Node.js 22 LTS and pnpm 11.
- TypeScript in strict mode, ESLint 9, Prettier 3, Vitest 3.
- Next.js 15/React 19 for the web shell.
- Fastify 5 for the API shell.
- A separate worker process for reminder, export, deletion, memory-cleanup, and AI job categories.
- Environment configuration is names-only in `.env.example`; no secret values are committed.

## API and ownership boundary

The API exposes only foundation routes at this stage: liveness, readiness, and prefix smoke routes. Planned product operations remain in the approved API documentation and are not stubbed as misleading endpoints. Future routes must use `/api/v1` or `/internal/v1`, enforce authenticated `/me` ownership, authorization, validation, idempotency, rate limits, correlation IDs, and safe error handling.

## AI, memory, and safety boundary

`packages/ai-core` defines provider-neutral `ModelGateway`, `IntelligenceEngine`, request/response, intent, planning, and memory-candidate types. A provider adapter is deliberately absent. Memory follows candidate → privacy/safety review → explicit user approval → approved record; it is off by default, purpose-bound, revocable, and deletable. `packages/policy` defines `NORMAL`, `WELLNESS_REDIRECT`, `SAFETY_ESCALATION`, and `BLOCKED`. No diagnosis, prescription, dosage, emergency dispatch, or autonomous action is implemented.

## Database and persistence boundary

`packages/database-core` provides connection, transaction, repository, health-check, migration-runner, and graceful-close interfaces plus an unconfigured fail-safe client. `database/README.md` points to the approved PostgreSQL design. No provider, credentials, connection, ORM schema, DDL execution, migration, or seed data is part of Phase 12. The eventual implementation must preserve ownership isolation, audit/history, soft-delete and retention rules, account deletion/export behavior, and least-data-necessary storage.

## Running the foundation

```text
pnpm install --ignore-scripts
pnpm dev
pnpm -r build
pnpm -r typecheck
pnpm test:foundation
pnpm lint
pnpm format:check
```

The root `check` script is intended for the complete foundation gate once all workspace packages are built.

## Part 2 boundaries and guardrails

- `packages/auth-core` defines provider-neutral registration, session, recovery, MFA, and step-up interfaces; `UnconfiguredIdentityAdapter` fails closed.
- `packages/ai-core` models the ordered context → safety → intent → planning → gateway → output validation → safety → action → memory-candidate pipeline. The model cannot authorize, consent, own data, or bypass policy.
- `packages/memory-core` requires consent for proposals/retrieval and supports approval, rejection, edit, delete, clear, revoke, and disable. Retrieval returns no records after consent revocation.
- `packages/safety-core` is an independent policy boundary; the four approved modes remain unchanged.
- `packages/worker-core` supplies typed jobs, idempotency, bounded retries, timeouts, failure telemetry, and no queue provider.
- `packages/observability` includes recursive redaction for credential, prompt, completion, payload, health, memory, and chat fields.
- `scripts/check-architecture.mjs` and `scripts/check-secrets.mjs` provide lightweight drift and secret checks. `.github/workflows/ci.yml` runs install, format, lint, typecheck, tests, build, audit, and guardrails only; it never deploys.

## Explicitly not implemented

Authentication provider integration/MFA, database connectivity and migrations, real API business endpoints, AI provider calls, memory persistence/revocation propagation, safety classifiers/escalation workflows, notifications, payments, queues, object storage, deployment, and production monitoring remain future phases. TBD business/legal decisions (launch geography, minimum age, AI retention/training, deletion propagation, auth baseline, admin/support matrix, safety-policy ownership, and related retention/RTO/RPO decisions) remain unresolved.
