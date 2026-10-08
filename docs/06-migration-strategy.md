# NexusAI — Database Migration Strategy

**Document type:** Migration and release-safety strategy  
**Phase:** Phase 06 — DDL / SQL / Migration Design  
**Status:** Approved — Phase 06 gate passed; Phase 07 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Target:** Managed PostgreSQL with versioned migrations  
**Related:** [06-database-implementation.md](06-database-implementation.md), [06-ddl.md](06-ddl.md), [06-database-validation.md](06-database-validation.md)

## 1. Principles

- Every production schema change is an immutable, versioned migration reviewed against the approved Phase 05 model.
- Migrations are forward-only in production. A “down” script may exist for disposable local/test environments, but it is not the production rollback mechanism for restricted data.
- Prefer additive, backward-compatible changes before application code begins depending on them.
- Never perform a destructive data change without an approved retention/deletion decision, backup verification, and an auditable change record.
- Keep migrations small enough to review, observe, and recover. Separate schema shape, data backfill, indexes, and constraint validation when a table is large.

## 2. Initial migration ordering

The initial schema is split into dependency-aware migration units. Exact filenames may follow the selected migration tool, but the order must remain equivalent.

| Order | Migration unit | Contents | Dependency |
| ---: | --- | --- | --- |
| 001 | Bootstrap | `pgcrypto` extension, `nexus` schema, common trigger functions | Provider permission |
| 002 | Identity | `accounts`, `auth_sessions` and identity indexes | Bootstrap |
| 003 | Profile and consent | `user_profiles`, `wellness_profiles`, `consent_records`, append-only trigger | Identity |
| 004 | Wellness planning | `goals`, `routines`, `daily_plans`, `tasks`, same-account keys and indexes | Identity/profile |
| 005 | Progress | `check_ins` and indexes | Tasks |
| 006 | Conversation | `conversations`, `messages`, ordered-message indexes | Identity |
| 007 | Memory | `memory_records`, consent/source FKs, active fingerprint index | Consent/messages |
| 008 | Notifications | `notification_preferences`, `reminders`, `notification_deliveries`, delivery indexes | Identity/tasks |
| 009 | Safety and lifecycle | `safety_events`, `data_lifecycle_requests` | Conversations/messages/identity |
| 010 | Governance and operations | `support_access_events`, `audit_events`, `ai_usage_events`, append-only triggers | Identity/conversations/messages |
| 011 | Validation and grants | Constraint/index verification, least-privilege grants, migration ledger update | All prior units |

The monolithic text in [06-ddl.md](06-ddl.md) follows the same dependency order and can be divided into these migration files without changing the logical model.

## 3. Transaction and locking strategy

- Run each small schema migration in a transaction where PostgreSQL permits transactional DDL.
- Keep deployment-time `lock_timeout` and `statement_timeout` bounded; fail safely rather than waiting indefinitely behind user traffic.
- Build large secondary indexes with `CREATE INDEX CONCURRENTLY` in a separate non-transactional migration when table volume warrants it. The migration runner must explicitly mark this exception.
- Avoid table-rewrite operations during peak traffic. Add a nullable column, backfill in batches, validate, and only then enforce `NOT NULL` in a later release when necessary.
- Do not use `DROP ... CASCADE` in production migrations. The approved model intentionally uses restrictive foreign keys and explicit lifecycle operations.

## 4. Rollback and forward-fix

### 4.1 Before deployment

1. Record migration version, owner, change ticket, expected lock profile, affected tables, and validation queries.
2. Take an encrypted provider snapshot and verify that point-in-time recovery/WAL archiving is healthy.
3. Run the migration on a production-sized staging copy and capture duration, locks, query plans, and constraint/index results.
4. Confirm an operator who can restore or promote the backup is available for the change window.

### 4.2 If a migration fails

- If the transaction has not committed, allow PostgreSQL to roll it back and keep the application on the previous compatible version.
- If an additive migration committed but an application release fails, continue serving the previous application against the compatible schema and investigate.
- For an incorrect data transformation or catastrophic schema outcome, use point-in-time restore or a controlled replica promotion; do not improvise destructive “undo” SQL against restricted data.
- Reconcile the migration ledger and audit record before retrying.

### 4.3 Forward-fix policy

Production corrections use a new migration that repairs the state, preserves valid user data, and adds a regression validation. Examples include adding a missing constraint as `NOT VALID`, cleaning invalid rows in a bounded job, then validating the constraint and enforcing it. Any logical-model change must be marked as a proposed change and reviewed against Phase 05 before implementation.

## 5. Seed and reference data

No user, clinical, payment, or provider payload seed data is required for the MVP. Where Phase 05 defines an explicit allow-list (for example task types, safety actions, and lifecycle states), it is represented by named SQL checks; values whose complete list is not yet specified (for example wellness-area and consent-type catalogs) remain service/policy-owned. If a future product decision requires editable reference catalogs, introduce them as a separately approved reference-data migration; do not silently add global catalog entities to this phase.

## 6. Production migration safety

- Use a dedicated migration role; application roles must not own tables or run arbitrary DDL.
- Verify encrypted backups, TLS, secret rotation, and provider maintenance policy before production use; exact provider/region is still TBD.
- Migrations must be observable through structured, redacted events: version, start/end, duration, outcome, lock wait, and correlation ID. Never log ciphertext, email, message text, memory values, or export references.
- Pause or drain lifecycle workers when a migration touches their queue/state tables, then resume with idempotent leases.
- Do not enqueue new reminders, exports, memory-clear, or account-delete jobs that depend on a not-yet-committed schema.
- Gate destructive/retention migrations behind explicit privacy and product approval, with a tested restore path.
- Validate foreign-key counts, orphan checks, unique-index predicates, trigger presence, and append-only behavior after every release.

## 7. Zero/minimal-downtime release pattern

For an additive change:

1. **Expand:** add nullable column/table/index; deploy code that can read both old and new shapes.
2. **Backfill:** process bounded batches with retry-safe checkpoints and no raw restricted data in logs.
3. **Verify:** compare counts/checksums at the appropriate privacy-safe granularity; inspect locks and replication lag.
4. **Contract:** switch reads/writes, validate the constraint, then remove obsolete shape only after the retention window and rollback period.

For a new entity, create the table and indexes first, deploy compatible code second, and enable user-facing writes only after Phase 06 validation passes. For a deletion or retention change, disable new writes and run the lifecycle coordinator before physical purge.

## 8. Backups, recovery, and replicas

- Maintain encrypted automated snapshots plus continuous WAL/PITR where the selected managed provider supports it.
- Test restore and selective export procedures on a schedule; an untested backup is not a recovery control.
- Keep backup retention and deletion exceptions aligned with the future approved retention/legal-hold policy. The exact windows, RTO, RPO, replica topology, and recovery authority remain TBD.
- Treat read replicas, analytics extracts, caches, queues, temporary export artifacts, and provider-side copies as part of the privacy boundary. A migration is not complete if it leaves a stale restricted copy in a derived store.
- Do not use replicas for destructive lifecycle completion checks until replication lag is within the approved bound.

## 9. Future schema evolution

Potential future extensions—organization/household scope, additional notification channels, provider routing metadata, richer wellness programs, or a billing module—must be additive modules with their own requirements and privacy review. They must not force speculative V1 columns or weaken account ownership. If a future module needs multi-tenant ownership, introduce a reviewed scope key and backfill all user-owned tables before enabling shared ownership.

## 10. Migration risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Long locks from indexes/constraints | Staging rehearsal, bounded timeouts, concurrent index builds, `NOT VALID` then validate |
| Orphan/cross-account links | Composite same-account FKs, orphan queries, transaction-level ownership checks |
| Rollback cannot restore restricted data | Encrypted snapshot/PITR before change; forward-fix instead of destructive down migration |
| Sensitive data in migration logs | Structured redaction, no row payload logging, restricted migration role |
| Backfill duplicates or repeats | Idempotent checkpoints, unique constraints, deterministic keys, retry-safe batches |
| Lifecycle job races | Pause/drain workers, leases, idempotency key, explicit schema compatibility |
| Backup/replica retains deleted data | Document retention exception, track purge evidence, test derived-store cleanup |
| Provider-specific SQL lock-in | Standard PostgreSQL features, isolated migration units, technology decision record |

## 11. Unresolved migration decisions

- Managed PostgreSQL provider, region, tested major version, tier, and migration tool.
- Availability, RTO/RPO, replica, backup-retention, legal-hold, and disaster-recovery targets.
- Exact retention/grace periods for account, messages, memories, audit, delivery, and usage data.
- Whether a future policy requires RLS and the session-identity contract needed to enable it.
- Production change-window authority, on-call ownership, and restore/promote permissions.
- Whether editable reference catalogs are needed instead of static checks.

These are `TBD / Pending Decision`; this document does not invent them.

## 12. Phase boundary

Migration strategy passed the Phase 06 review gate after the user explicitly approved the DDL/SQL/migration package. Runtime staging execution remains a follow-up validation task; API design and application implementation remain separately phase-gated.
