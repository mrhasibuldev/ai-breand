# NexusAI — Technology Stack Recommendation

**Document type:** Phase 11 technology evaluation and recommendation  
**Phase:** Phase 11 — Technology Stack, Implementation Architecture & Development Foundation Planning  
**Status:** Approved — Phase 11 documentation gate passed; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-30  
**Scope:** Technology selection only. No project initialization, package installation, cloud provisioning, migration execution, or application code is created.

## 1. Selection principles

The stack must satisfy the approved web-first wellness MVP without changing the 21-entity PostgreSQL model, 77 API operations, provider-neutral AI boundary, consent-based Minimal Memory, safety modes, or Phase 10 controls. Choices are evaluated for MVP cost, reliability, security/privacy, operational burden, developer experience, portability, and a credible path to the long-term NexusAI Brain.

Founder/business-sensitive choices (launch geography, data region, provider contracts, age policy, MFA baseline, retention/training terms, and cost envelope) remain `TBD / Pending Decision`.

## 2. Recommended stack at a glance

| Layer | Preferred option | Approval status | Why |
| --- | --- | --- | --- |
| Web frontend | Next.js App Router + React + TypeScript | **Approved Phase 11 baseline** | Responsive UI, public landing/SEO, server/client composition, accessible ecosystem, future PWA/mobile boundary |
| API/backend | Node.js LTS + TypeScript + Fastify, modular monolith | **Approved Phase 11 baseline** | Strong API throughput, schema validation, shared types, AI orchestration and worker reuse |
| Database | Managed PostgreSQL | Conceptually approved; provider/region TBD | Preserves approved relational integrity, transactions, constraints, and PITR capability |
| Data access | Drizzle ORM + explicit SQL for exceptional queries | **Approved Phase 11 baseline** | Type-safe SQL-first access, readable migrations, preserves database constraints |
| Authentication | Managed OIDC-capable identity provider behind an adapter | Required baseline; vendor/MFA TBD | Avoids self-managed credential risk while keeping provider replaceable |
| Session | Secure, HttpOnly, SameSite cookie session for browser | Recommended; policy pending | Browser-first CSRF/XSS posture and revocation-friendly server session |
| Cache/rate limit | No Redis on day one; edge/API throttles plus PostgreSQL-backed bounded state | Recommended; scale trigger defined | Avoids extra service until measured need; Redis added when distributed limits/latency require it |
| Queue/jobs | PostgreSQL-backed job queue for MVP (e.g., a vetted Postgres job library) | Recommended; library/provider TBD | Reuses approved database, supports retries and lifecycle jobs without a second platform |
| Object storage | Private S3-compatible object storage | Category recommended; provider/region TBD | Encrypted, signed, expiring export artifacts and future attachments |
| AI | Commercial hosted model through `NexusAI IntelligenceEngine / ModelGateway` | Strategy recommended; provider/model TBD | Best MVP quality/latency with replaceable adapter and no proprietary model assumption |
| Retrieval | PostgreSQL structured retrieval first; evaluate `pgvector` later | Recommended | Minimal Memory MVP does not require a vector database |
| Validation | Shared TypeScript schemas with Zod at application boundary; Fastify response/request schemas | Recommended; exact tooling pending | Aligns with 77 contracts and produces safe, typed errors |
| API style | REST `/api/v1`, internal `/internal/v1`, stable error envelope | Approved contract; implementation pending | Matches Phase 07 and supports web/native clients |
| Analytics | First-party, event-only, privacy-minimized analytics | Recommended; vendor TBD | Avoids third-party collection of chat/wellness content |
| Observability | Structured redacted logs + metrics/traces + error monitoring | Required architecture; vendor TBD | Meets Phase 10 evidence and incident requirements |
| Hosting | Single-cloud managed services; AWS is a reference option, final provider/region TBD | Category recommended | Small-team simplicity now with extraction/scaling path later |
| Repository | TypeScript monorepo with `apps`, `packages`, `database`, `docs`, `tests` | Recommended | Shared contracts/policies and one release train reduce drift |
| Build/package | Native workspace tooling with a small task runner (pnpm/Turborepo class) | Recommended category; exact tool TBD | Reproducible builds without premature platform complexity |

## 3. Frontend evaluation

| Option | Advantages | Disadvantages | MVP cost/complexity | Decision |
| --- | --- | --- | --- | --- |
| Next.js + React | Public landing/SEO, server rendering where useful, client components for chat/dashboard, mature accessibility tooling, future PWA path | Framework conventions and server/client boundary require discipline; hosting choices can add platform coupling | Low–medium; one web deployment | **Preferred** |
| React SPA (Vite class) | Simple mental model, flexible hosting, small client-only bundle | SEO/public pages need extra work; auth/session and data fetching become more client-heavy; no shared server boundary | Low initial, medium integration | Alternative if SEO is dropped |
| Other full-stack frameworks | May offer batteries-included routing or different performance tradeoffs | Smaller team familiarity/ecosystem or migration cost is unknown | Medium–high uncertainty | Not preferred for MVP |

Next.js App Router is recommended for the responsive guest-to-account journey, public wellness boundary pages, authenticated dashboard, AI chat, planning, memory controls, and accessible settings. Keep product logic in the API/domain boundary; do not rely on server actions as an authorization substitute. The official App Router documentation describes server/client components and built-in navigation/deployment patterns: [Next.js App Router](https://nextjs.org/docs/app), [deployment guidance](https://nextjs.org/docs/app/getting-started/deploying).

## 4. Backend evaluation

| Option | Advantages | Disadvantages | MVP cost/complexity | Decision |
| --- | --- | --- | --- | --- |
| TypeScript + Node.js + Fastify | Shared types with web, strong JSON API fit, good validation/serialization, efficient AI/queue I/O, one hiring/tooling ecosystem | Async error handling and CPU-heavy work need discipline; TypeScript build complexity | Low–medium | **Preferred** |
| Python (FastAPI class) | Excellent AI/data ecosystem, readable APIs, strong validation, easy experimentation | Separate language/toolchain from web, duplicated contracts/types, async worker conventions need care | Medium | Viable alternative |
| Other backend framework | Could provide larger batteries-included platform | Adds migration/familiarity risk without an MVP requirement | Medium–high | Not justified |

Fastify is preferred with explicit JSON Schema/Zod integration and response validation. Its official documentation covers TypeScript and schema validation: [Fastify TypeScript](https://fastify.dev/docs/latest/Reference/TypeScript/), [Fastify validation](https://fastify.dev/docs/v5.8.x/Reference/Validation-and-Serialization/).

## 5. Application architecture style

Use a **modular monolith**: one deployable API and one worker process, with strict internal modules. Do not begin with microservices. Modules are:

- Identity/session adapter
- Account/profile
- Wellness (goals, routines, plans, tasks, check-ins, progress)
- Reminders/notification delivery
- Conversation/message
- Consent/memory
- AI IntelligenceEngine/ModelGateway
- Safety/policy
- Lifecycle (export, deletion, revocation)
- Support/admin projections
- Audit/usage/observability

Each module owns its application interfaces and policy checks. It may use the shared PostgreSQL database only through data-access boundaries. A future extraction candidate is the AI worker/provider adapter or notification worker, but extraction occurs only after measured load/team need.

## 6. Managed PostgreSQL evaluation

| Category | Advantages | Disadvantages | Decision |
| --- | --- | --- | --- |
| Major-cloud managed PostgreSQL | Mature backups/PITR, private networking, KMS integration, multiple regions and scaling options | Higher baseline operations/cost; region and IAM complexity | Reference option |
| Developer-focused managed PostgreSQL | Fast setup, strong local workflow, lower early cost | Fewer enterprise controls/regions or workload ceilings may matter later | Candidate for early beta |
| Self-hosted PostgreSQL | Maximum control and portability | Patch, backup, replication, incident and security burden is too high for MVP | Reject for MVP |

Managed PostgreSQL remains the technology decision. Provider, region, tier, connection pooling, backup retention and contractual terms cannot be selected responsibly until launch geography and data-processing decisions are approved. Managed services such as Amazon RDS document automated backups and point-in-time recovery; this is representative of the capability required, not a final vendor choice: [RDS backup/restore](https://docs.aws.amazon.com/AmazonRDS/latest/gettingstartedguide/managing-backup-restore.html).

## 7. ORM/data-access evaluation

| Option | Strengths | Tradeoffs | Decision |
| --- | --- | --- | --- |
| Drizzle ORM + SQL escape hatch | SQL-first, type-safe, readable generated SQL/migrations, good PostgreSQL coverage, low runtime abstraction | Smaller ecosystem than Prisma; team must own patterns and complex-query review | **Preferred** |
| Prisma | Excellent schema/client DX, mature relation tooling, broad community | Generated abstraction can obscure approved constraints/SQL; migration and provider coupling must be reviewed | Alternative |
| Query builder/SQL-first (Kysely/node-postgres) | Maximum SQL transparency and portability | More hand-written types/boilerplate; easier drift without shared schema discipline | Alternative for data-heavy modules |

Drizzle is the approved Phase 11 baseline because Phase 05/06 explicitly prioritize PostgreSQL constraints, composite ownership keys, append-only records and migration-readable SQL. Complex or security-sensitive queries may use reviewed SQL through the same transaction/authorization boundary.

## 8. Authentication and session baseline

Use a managed OIDC-capable identity provider behind a NexusAI adapter, with secure browser cookies and server-side session metadata. This is a technology recommendation, not a vendor selection. Required capabilities are registration, verification, recovery, revocation, MFA readiness, step-up, suspicious-login signals and auditability.

Self-managed password auth is rejected for MVP unless a later security review demonstrates equivalent controls, staffing and recovery assurance. Passkeys should remain a future-ready capability of the identity adapter, not a reason to delay launch. Final provider, MFA mandatory scope, cookie attributes, session lifetime and geography remain High/TBD decisions from Phase 10.

## 9. Cache, queue and object storage

- **Cache:** Start without Redis. Use edge/API rate limiting and bounded PostgreSQL state. Add managed Redis only when multi-instance rate limits, hot read latency, or queue coordination cannot meet measured targets. Any cache key must include account/lifecycle generation where data is user-scoped.
- **Queue:** Use a PostgreSQL-backed queue for MVP AI jobs, reminder delivery, exports, deletion, memory cleanup and retries. Isolate worker roles and keep jobs idempotent. Move to a managed queue when throughput/availability evidence warrants it.
- **Object storage:** Use a private, encrypted S3-compatible bucket for temporary exports and future profile images/attachments. Objects need opaque keys, account scope, short-lived signed access, expiry, malware/content controls for future uploads, and deletion/backup lifecycle hooks.

## 10. AI, retrieval and routing

Commercial hosted inference through `NexusAI IntelligenceEngine / ModelGateway` is the MVP default. The provider adapter receives a minimized, consent/purpose-eligible context and returns a normalized result; product modules never import a provider SDK directly.

Minimal Memory uses PostgreSQL structured filters and bounded encrypted records first. Do not add an external vector database at MVP. If retrieval quality later requires semantic search, evaluate `pgvector` inside the approved PostgreSQL boundary before considering an external vector platform. Model routing is policy-driven: inexpensive model for simple wellness transformations, stronger model for complex planning, deterministic safety gates for high-risk content, and a safe fallback when provider policy/availability is uncertain.

## 11. Validation, API and notification approach

- Define shared schemas for each of the 77 approved operations; validate request, authorization context and response.
- Keep REST versioning and error envelopes exactly aligned with Phase 07; implementation must not invent routes.
- Use correlation IDs, bounded pagination cursors and durable idempotency for lifecycle/consequential operations.
- In-app reminders are the only approved MVP notification channel. Email/push/SMS adapters remain disabled until separately consented and approved.

## 12. Analytics, observability and quality

Use first-party event names for activation, goal/plan use, AI usage, failures, latency, retention and deletion/export success. Do not send raw chat, wellness text, memory, prompts, completions, identifiers, or notification content to third-party analytics.

The observability baseline is structured redacted logs, metrics, traces, error monitoring, provider/queue health and security alerts, subject to [10-security-architecture.md](10-security-architecture.md). Formatting, linting, type checks, unit/integration/contract/E2E tests and security scans are required before implementation approval.

## 13. Package management and monorepo

Use a single TypeScript monorepo with workspace package management. Prefer a boring, lockfile-based package manager and a small task runner only when multiple apps/packages need coordinated tasks. Exact package manager/build tool is an ADR pending team preference and CI host. Avoid code generation, service meshes, Kubernetes, or multi-repo release orchestration for MVP.

## 14. Feature flags and configuration

Feature-flag only high-risk/reversible capabilities: Minimal Memory, AI provider/model route, reminder delivery expansion, new planning behavior, and beta cohorts. Keep flags typed, owner-assigned, audited and removable. Environment variables hold non-secret configuration; secrets manager holds credentials/keys; prompt/policy versions are reviewed artifacts, not random source strings. No secret belongs in Git or client bundles.

## 15. Alternatives and revisit triggers

Revisit this recommendation when: launch geography changes provider constraints; beta load exceeds single-process/managed PostgreSQL limits; AI cost/latency requires routing; privacy terms prevent a provider; a second native client needs a different auth transport; or staffing supports service extraction. Every revisit requires an ADR and Phase 11/12 gate review.

## 16. Phase boundary

This document recommends technologies only. It does not initialize frontend/backend projects, install packages, create infrastructure, choose a final vendor/region, execute migrations, or write application code.
