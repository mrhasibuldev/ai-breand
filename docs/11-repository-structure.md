# NexusAI — Repository and Monorepo Structure

**Document type:** Phase 11 repository layout, package ownership, monorepo evaluation and build conventions  
**Phase:** Phase 11 — Technology Stack, Implementation Architecture & Development Foundation Planning  
**Status:** Approved — Phase 11 documentation gate passed; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-30  
**Scope:** Future repository design only. No folders, projects, packages, or build files are initialized.

## 1. Recommendation

Use a single TypeScript monorepo for the founder-led MVP. The web app, API, worker, shared contracts, policy artifacts and database documentation evolve together, so one pull request and one CI graph can validate cross-layer compatibility. Keep deployable applications separate inside the repository, with package boundaries that make later extraction possible.

## 2. Proposed tree

```text
/
├── apps/
│   ├── web/                 # Next.js browser application and public pages
│   ├── api/                 # Fastify REST API modular monolith
│   └── worker/              # Background jobs, lifecycle and provider work
├── packages/
│   ├── contracts/           # Versioned API request/response/error schemas
│   ├── domain/              # Shared domain types and module interfaces
│   ├── policy/              # Consent, safety, retention and routing identifiers
│   ├── ai-core/             # IntelligenceEngine/ModelGateway interfaces
│   ├── auth-core/           # Principal/session abstraction and auth events
│   ├── observability/       # Redacted telemetry contracts and correlation helpers
│   ├── ui/                  # Accessible design-system primitives (after Phase 12)
│   └── config/              # Typed non-secret configuration parsing
├── database/
│   ├── schema/              # Reviewed PostgreSQL schema source (future implementation)
│   ├── migrations/          # Ordered migration artifacts (future implementation)
│   └── seeds/               # Safe reference data only; no personal data
├── policies/
│   ├── prompts/             # Versioned system/context templates
│   ├── safety/              # Versioned safety policy and evaluation metadata
│   ├── privacy/             # Purpose/consent and retention references
│   └── routing/             # Model/provider routing policy
├── tests/
│   ├── contract/            # API and provider contract tests
│   ├── integration/         # Database, queue and module integration tests
│   ├── e2e/                 # Browser/user-journey tests with synthetic data
│   ├── security/            # Authorization, abuse and lifecycle negatives
│   └── ai-evals/            # Synthetic prompt-injection/safety evaluation corpus
├── scripts/                 # Non-production developer and validation utilities
├── infrastructure/          # Deployment descriptions and environment policy (future)
├── docs/                    # Phase-gated product and technical documentation
├── .github/                 # CI workflow definitions (future; host choice TBD)
├── .env.example             # Names and safe examples only; no secrets
├── package.json             # Workspace metadata (future)
├── lockfile                 # Exact package versions (future)
├── tsconfig.base.json       # Shared TypeScript policy (future)
└── README.md                # Developer entry point and phase status
```

The tree records the Phase 11 design target; current implementation is limited to the separately approved Phase 12 foundation and authorized Phase 13 Part 1 slice. `policies/` is deliberately separate from source so safety/prompt/configuration changes are reviewable and versioned. `database/` stores implementation artifacts only after the approved Phase 06 boundary is reopened by the implementation phase.

## 3. Top-level ownership

| Directory | Owner boundary | Rules |
| --- | --- | --- |
| `apps/web` | Frontend | Calls public API; cannot access secrets, database or provider SDKs |
| `apps/api` | Backend/domain | Owns REST adapters and module composition; enforces authz/policy |
| `apps/worker` | Platform/domain | Owns job consumers; uses scoped service identity and idempotency |
| `packages/contracts` | API governance | One source for schemas/errors; changes require contract review |
| `packages/domain` | Architecture | Interfaces/types only unless explicitly owned by a module |
| `packages/policy` | Security/privacy/safety | No policy bypass; versioned and audited |
| `packages/ai-core` | AI architecture | Provider-neutral; no provider SDK imports |
| `packages/auth-core` | Security | Principal/session abstraction; no raw secrets |
| `packages/observability` | Security/operations | Redaction and allow-list defaults |
| `database` | Data/platform | Mirrors approved 21-entity model and migration strategy |
| `policies` | Product/security/safety | Review-required artifacts; no untracked prompt strings |
| `tests` | Quality/security | Synthetic data only; evidence redaction required |
| `infrastructure` | Platform | Environment and least-privilege definitions; no secrets in Git |
| `docs` | Documentation owner | Phase source of truth and approval records |

## 4. Import and dependency rules

- `apps/web` may import `packages/contracts`, `packages/domain` (types), `packages/ui`, and safe client configuration only.
- `apps/api` and `apps/worker` may import contracts, domain interfaces, policy, auth-core, ai-core and observability.
- `packages/ai-core` may expose adapter interfaces but cannot import `apps/api` or provider SDKs.
- `packages/policy` must not depend on web presentation.
- Database implementation modules are consumed through a data-access package owned by the API/worker boundary; direct table access from UI or tests is prohibited.
- Test fixtures cannot be imported into production packages.

## 5. Monorepo versus multi-repo

| Approach | Benefits | Costs/risks | Decision |
| --- | --- | --- | --- |
| Monorepo | Shared contracts, atomic changes, one security policy, simple local setup, unified CI and versioning | Larger CI graph over time, tooling discipline, accidental cross-package imports | **Preferred for MVP** |
| Multi-repo | Independent ownership/deploys, smaller per-repo surface | Contract drift, duplicated tooling, difficult coordinated schema/API/AI/privacy changes, more credentials | Revisit after team/service boundaries emerge |

The monorepo does not mean one runtime: web, API and worker remain independently deployable workloads.

## 6. Package management and build system

Use a lockfile-based workspace package manager with a small task runner only if parallel app/package tasks justify it. The preferred category is pnpm workspaces plus a Turborepo-class task cache; exact tool is an ADR pending team preference and CI host. Build outputs are reproducible, dependency versions are pinned, and generated artifacts are reviewable.

Avoid Kubernetes, service meshes, custom internal registries, multi-repo release bots, or a large code-generation layer in the MVP. Add them only after measured need.

## 7. Branching and change ownership

- Protected default branch; required review for auth, policy, database, AI, lifecycle and infrastructure changes.
- Small feature branches and one coherent pull request per change.
- CODEOWNERS-style ownership for `policies/`, `database/`, `packages/auth-core`, `packages/ai-core`, and `infrastructure/` once implementation begins.
- A change that crosses API, database, AI or UI contracts must include traceability updates and an ADR when the decision is material.

## 8. Documentation entry path

The root README should link to the source-of-truth hierarchy, current phase, local setup guide, environment rules, security checklist, API contract, AI/memory boundaries, UI flows and approval checklists. A new developer or AI agent must be able to identify the current approval and authorization state: Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

## 9. Future extraction path

Keep provider adapters, AI workers, notification delivery and lifecycle workers behind interfaces. If extraction becomes necessary, move a package and its tests first, retain the same contracts and audit semantics, then split deployment. The public API, 21-entity model, consent/memory behavior and safety policy must not be rewritten solely to accommodate repository layout.

## 10. Phase boundary

This document defines a future repository structure only. It does not create folders, workspace manifests, package files, CI configuration, migration files, or source code.
