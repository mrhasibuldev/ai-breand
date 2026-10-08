# NexusAI — Database Implementation Specification

**Document type:** Production-oriented database implementation specification  
**Phase:** Phase 06 — DDL / SQL / Migration Design  
**Status:** Approved — Phase 06 gate passed; Phase 07 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-29  
**Scope:** Physical database technology, SQL conventions, implementation boundaries, and traceability. This document does not define API endpoints, ORM models, or application code.

## 1. Source of truth and phase boundary

The approved logical database package controls this phase:

1. [`05-database-design.md`](05-database-design.md) — logical responsibilities, entities, lifecycle, ownership, and privacy rules.
2. [`05-erd.md`](05-erd.md) — entities, primary keys, foreign keys, and cardinality.
3. [`05-data-dictionary.md`](05-data-dictionary.md) — field-level requiredness, type intent, defaults, and constraints.
4. [`05-database-decisions.md`](05-database-decisions.md) — confirmed assumptions, recommendations, and unresolved decisions.

The product/architecture chain remains [`00-project-overview.md`](00-project-overview.md), [`01-product-discovery.md`](01-product-discovery.md), [`02-prd-nexus-ai-health-companion-mvp.md`](02-prd-nexus-ai-health-companion-mvp.md), [`03-system-architecture-outline.md`](03-system-architecture-outline.md), and [`04-architecture-review.md`](04-architecture-review.md).

No higher-level product, safety, age, geography, authentication, provider, retention, or support decision is silently resolved here. The old operations-copilot direction is historical only and is not a schema requirement.

## 2. Database technology decision

### 2.1 Options considered

| Option | MVP cost | Reliability / recovery | Integrity and security fit | Developer friendliness | Growth and migration fit | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Managed PostgreSQL | Low-to-medium; small managed tiers are available | Mature transactions, backups, replicas, and provider-managed PITR options | Strong PK/FK/CHECK/UNIQUE constraints, transactions, row/column privilege options, and encrypted storage integrations | Excellent SQL ecosystem, migration tooling, testing, and observability | Relational growth plus bounded `jsonb`; broad hosting portability | **Recommended** |
| Managed MySQL 8.4/InnoDB | Low-to-medium and widely available | Mature replication and backup ecosystem | Strong relational constraints and native JSON; some advanced constraint/index patterns are less portable | Very familiar and well supported | Good scale and migration tooling; portability depends on MySQL-specific behavior | Viable alternative |
| Managed MongoDB | Low-to-medium for simple document workloads | Replication and backups are mature; multi-document transaction use has trade-offs | Flexible schema and validation, but cross-entity ownership/integrity moves more into application code | Productive for document-first data | Useful for document-heavy future features, but relational lifecycle queries become more complex | Not selected for V1 |

### 2.2 Recommendation

Use a **managed PostgreSQL service**, targeting a provider-supported PostgreSQL major and pinning the tested major in deployment (the DDL uses standard PostgreSQL features and is intended to be portable across supported current majors). The cloud provider, region, tier, and exact major remain deployment decisions and therefore remain `TBD / Pending Decision`.

PostgreSQL is the best fit because the MVP has many explicit relationships—account ownership, plans/tasks/check-ins, conversation/message ordering, consent/memory evidence, reminders/deliveries, and audit/lifecycle records. Database-level foreign keys and check constraints reduce the chance that an application bug creates cross-account or invalid lifecycle data. PostgreSQL transactions provide all-or-nothing writes, while `jsonb` is available for small versioned recurrence and allow-listed metadata without turning core entities into unbounded blobs. WAL archiving and managed-provider backup services support point-in-time recovery. These capabilities are documented in the [PostgreSQL constraints documentation](https://www.postgresql.org/docs/current/ddl-constraints.html), [transaction tutorial](https://www.postgresql.org/docs/current/tutorial-transactions.html), [JSON types documentation](https://www.postgresql.org/docs/current/datatype-json.html), and [continuous archiving/PITR documentation](https://www.postgresql.org/docs/current/continuous-archiving.html).

MySQL 8.4/InnoDB remains a credible fallback where the selected hosting environment standardizes on MySQL; its official documentation covers foreign-key actions and native JSON ([foreign keys](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html), [JSON](https://dev.mysql.com/doc/refman/8.4/en/json.html)). MongoDB supports transactions and schema validation, but its documented single-document atomicity and transaction trade-offs make the V1 relationship-heavy model less attractive ([transactions](https://www.mongodb.com/docs/v8.0/core/transactions/), [data modeling](https://www.mongodb.com/docs/v8.0/data-modeling/best-practices/)).

### 2.3 PostgreSQL implementation profile

- **Engine:** PostgreSQL, managed where possible.
- **Namespace:** `nexus` schema; `public` is reserved for extensions and provider defaults.
- **Identifier generation:** `uuid` with `pgcrypto` `gen_random_uuid()`; IDs are opaque and non-sequential.
- **Time:** `timestamptz` stored in UTC; dates represent the user’s configured local calendar date.
- **Local-date defaults:** logical “current local date” values are supplied by the domain service after applying the account timezone; SQL intentionally avoids server `CURRENT_DATE`, which could be wrong for the user.
- **Logical `STRING(n)`:** `varchar(n)` with non-empty checks where the dictionary requires a user-entered value.
- **Logical `TEXT`:** `text`; product-specific maximums remain an application validation concern unless explicitly listed in the dictionary.
- **Logical `ENCRYPTED_TEXT` / `ENCRYPTED_JSON`:** `bytea` ciphertext. Envelope encryption, key identifiers, rotation, and decrypt authorization live outside SQL.
- **Logical `JSON`:** `jsonb` only for bounded, non-sensitive, versioned metadata such as recurrence/schedule specifications and wellness-area selections.
- **Logical `ENUM`:** `text` plus named `CHECK` constraints rather than PostgreSQL enum types where Phase 05 defines an explicit list; unresolved catalogs remain service/policy-owned. This keeps approved state changes migration-friendly and visible in reviewable SQL.
- **Soft delete:** lifecycle/status columns and `deleted_at`; physical purge is performed by an approved lifecycle workflow, not by user-facing cascade deletes.
- **Append-only history:** consent, safety, support-access, and audit tables receive mutation-blocking triggers. Operational delivery/usage retention is handled by a controlled worker after a policy is approved.
- **Ownership isolation:** required `account_id` columns, composite parent keys for same-account child references, and service/data-access authorization checks. RLS is not enabled by default because the approved architecture has not yet selected a database session-identity contract.
- **Raw secrets:** no password, raw session token, API key, provider payload, prompt, or response archive is stored.

## 3. Physical mapping rules

### 3.1 Entity parity

The DDL contains exactly the 21 approved logical entities: `accounts`, `auth_sessions`, `user_profiles`, `wellness_profiles`, `consent_records`, `goals`, `routines`, `daily_plans`, `tasks`, `check_ins`, `conversations`, `messages`, `memory_records`, `notification_preferences`, `reminders`, `notification_deliveries`, `safety_events`, `data_lifecycle_requests`, `support_access_events`, `audit_events`, and `ai_usage_events`.

No payment/subscription table is created because the current PRD does not require billing. No clinical/diagnosis, wearable, location, household, or organization entity is introduced.

### 3.2 Ownership and same-account foreign keys

Each user-owned table stores `account_id`. For optional links such as a routine’s goal or a task’s plan/routine/goal, the parent table exposes a composite uniqueness key `(account_id, id)` and the child references `(account_id, parent_id)`. PostgreSQL’s default `MATCH SIMPLE` behavior allows the optional parent ID to be null while still enforcing same-account ownership when it is populated. Message ownership is inherited through its conversation because the approved model intentionally does not duplicate `account_id` on `messages`; data-access validation must preserve that invariant for message-linked safety, memory, and usage records.

### 3.3 Deletion behavior

Business, restricted-content, and history foreign keys use `ON DELETE RESTRICT`. Account deletion therefore cannot accidentally cascade through chat, memory, audit, or lifecycle data. The V1 purge design retains a minimal pseudonymized account anchor with `status = 'purged'` while erasing/replacing direct identity fields according to the approved lifecycle policy; this lets append-only audit references remain immutable. A deletion coordinator first disables access, revokes sessions, scrubs/minimizes dependent records, and only then completes the approved purge. Exact retained anchor fields, retention, legal holds, backup treatment, and provider deletion guarantees remain TBD.

### 3.4 Constraint ownership

SQL enforces structural invariants: type, requiredness, allow-listed state, timestamp ordering, non-negative counters, positive sequence/order values, JSON shape, and uniqueness. Application/domain services enforce policy-dependent rules that require current consent or cross-row evaluation—for example, whether a consent record is the latest granted memory consent, whether a reminder channel has separate approval, or whether a safety action may be shown in a particular geography.

## 4. DDL package contract

[`06-ddl.md`](06-ddl.md) is the authoritative SQL specification for this phase. It is organized so an initial migration can run in dependency order and be reviewed as text. The script is designed to be idempotent for bootstrap operations (`CREATE EXTENSION IF NOT EXISTS`, `CREATE SCHEMA IF NOT EXISTS`, named constraints/indexes, and `CREATE OR REPLACE FUNCTION`). Production migration tooling must still execute versioned migrations rather than repeatedly running the whole file.

The SQL includes:

- all 21 tables and their approved fields;
- primary keys, foreign keys, same-account composite foreign keys, and unique/partial unique indexes;
- named checks for allow-listed states, required pairings, ordering, and non-negative values;
- timestamp maintenance and append-only history triggers;
- ownership/status/time indexes required by the logical design;
- comments where an implementation boundary cannot be enforced by the database alone.

The SQL intentionally does not include API endpoints, seed user data, provider payload tables, application secrets, RLS policies requiring an unresolved session variable, or production connection credentials.

## 5. Operational and security boundaries

- Run migrations with a dedicated least-privilege migration identity; application identities receive only the grants needed by later API design.
- Keep database encryption at rest, TLS in transit, secret rotation, backup encryption, and key management in the deployment/security phase.
- Restrict direct SQL access; support/admin access is represented by `support_access_events` but is not granted by that table.
- Redact query parameters, ciphertext, email addresses, message content, and lifecycle artifacts from logs and traces.
- Monitor constraint violations, deadlocks, long-running queries, connection exhaustion, failed backups, replication lag, and lifecycle-job backlog.
- Treat database snapshots, replicas, queues, caches, and export artifacts as part of the same privacy/deletion boundary.

## 6. Implementation decisions that are not product decisions

These are physical recommendations, not changes to the approved domain model:

1. Use `text` + checks instead of engine enum types.
2. Use `bytea` for application-encrypted values; do not store plaintext alongside ciphertext.
3. Use composite ownership keys for same-account relationships where the approved schema already contains `account_id`.
4. Keep JSONB fields bounded and unindexed by default.
5. Keep account foreign keys restrictive and make deletion an explicit, auditable workflow.
6. Use partial unique indexes for active-only uniqueness (`accounts` email, active daily plans, active memory fingerprints).

If a future provider, jurisdiction, or availability requirement requires a different physical choice, record it as a proposed change and re-run the Phase 05 → Phase 06 traceability review; do not silently alter the approved logical model.

## 7. Unresolved decisions carried forward

The following remain `TBD / Pending Decision` and are intentionally not encoded as product policy:

- launch geography and applicable jurisdiction;
- minimum age and age-assurance approach;
- AI provider/model, retention, training use, regional processing, and provider-side deletion guarantees;
- memory deletion/revocation propagation guarantees, backups, legal holds, and completion evidence;
- authentication provider, MFA baseline, session lifetime/rotation, and account recovery assurance;
- admin/support role matrix and break-glass access procedure;
- safety-policy owner, release approval, escalation authority, and policy version lifecycle;
- exact retention windows, account deletion grace, legal holds, RTO/RPO, availability targets, beta scale, and database budget;
- whether future organization/household scope is needed.

## 8. Phase 06 document set

| Artifact | Purpose | Status |
| --- | --- | --- |
| `06-database-implementation.md` | Technology choice and physical implementation contract | Approved |
| `06-ddl.md` | PostgreSQL DDL specification | Approved |
| `06-migration-strategy.md` | Versioning, ordering, safety, rollback, and evolution | Approved |
| `06-database-validation.md` | Traceability, integrity, privacy, and Phase 06 approval checklist | Approved |

**Phase boundary:** Phase 06 ends after these documents are reviewed and explicitly approved. API design (Phase 07) is approved; application code, frontend, and AI implementation remain phase-gated.
