# NexusAI — Database Validation and Phase 06 Approval Checklist

**Document type:** DDL validation, traceability review, and phase-gate checklist  
**Phase:** Phase 06 — DDL / SQL / Migration Design  
**Status:** Approved — Phase 06 gate passed; Phase 07 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-29  
**Scope:** Static review of PRD → Architecture → ERD → Data Dictionary → DDL. No production database has been provisioned in this phase.

## 1. Validation method

This review compares the approved product and architecture requirements with the 21-entity logical model and PostgreSQL DDL. It checks entity/field parity, primary and foreign keys, same-account ownership, requiredness/defaults, states, indexes, soft-delete and append-only behavior, privacy boundaries, and migration safety.

- **Pass (static):** visible in the reviewed documentation/DDL and internally consistent.
- **Pass with runtime step:** design is present, but CI/staging must execute it on PostgreSQL.
- **TBD / Pending Decision:** intentionally unresolved product, legal, provider, or operations choice.
- **Proposed change:** would alter the approved logical model and requires explicit review.

### Cross-document consistency check — 2026-08-29

| Check | Result | Evidence |
| --- | --- | --- |
| Canonical product identity | Pass | Documents 00–06 identify NexusAI — Personal AI Health & Wellness Companion. |
| Active product direction | Pass | The superseded operations-copilot concept is not an active requirement. |
| PRD → architecture boundary | Pass | Wellness-only, non-diagnostic, consent-based chat and memory boundaries are preserved. |
| Phase status | Pass | **HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**: Phase 04 through Phase 11 are approved; Phase 12 is approved; Phase 13 is not started and pending explicit user approval and awaits explicit instructions. Current authorization is stated in the document header. |
| Unresolved decisions | Pass | Geography, age, provider, deletion, auth/MFA, roles, safety, retention, and recovery decisions remain TBD. |

## 2. PRD → Architecture → Database traceability

| Requirement/boundary | Database implementation | Result |
| --- | --- | --- |
| Guest limited wellness demo without durable data | No guest table; durable conversations require an account | Pass |
| Account, authentication boundary, and onboarding | `accounts`, hashed-only `auth_sessions`, `user_profiles`, `consent_records` | Pass |
| Personalized wellness guidance | `wellness_profiles`, `goals`, `routines`, `daily_plans`, `tasks` | Pass |
| Habit/check-in/progress tracking | `check_ins`; optional reflection is encrypted; no clinical measurements | Pass |
| AI wellness chat | `conversations`, ordered encrypted `messages`, minimized `ai_usage_events` | Pass |
| Consent-based Minimal Memory | `consent_records`, `memory_records`, lifecycle requests | Pass with runtime step |
| Wellness-only / no diagnosis | Wellness allow-lists; no diagnosis, medication, lab, or clinical entities | Pass |
| Reminder intent separated from delivery | `notification_preferences`, `reminders`, `notification_deliveries` | Pass |
| Safety accountability | Append-only `safety_events` with policy/classifier versions | Pass |
| Export, account deletion, memory clear | Idempotent `data_lifecycle_requests`; restrictive foreign keys | Pass with runtime step |
| Support isolation and audit | `support_access_events`, `audit_events`; authorization remains service-owned | Pass with TBD role matrix |
| Provider abstraction / no raw provider archive | Aliases, hashes, and usage counters only; no provider-payload table | Pass |
| Backup and recovery | Migration/backups documented; provider and RTO/RPO remain TBD | Pass with TBD |

## 3. Entity parity review

The approved ERD/data dictionary and DDL contain the same 21 entities. No entity is missing and no unnecessary domain entity was introduced.

| # | Approved entity | DDL table | Relationship/constraint checked | Result |
| ---: | --- | --- | --- | --- |
| 1 | `accounts` | `nexus.accounts` | Identity and lifecycle anchor | Pass |
| 2 | `auth_sessions` | `nexus.auth_sessions` | Account FK; token hash only | Pass |
| 3 | `user_profiles` | `nexus.user_profiles` | One-to-one account | Pass |
| 4 | `wellness_profiles` | `nexus.wellness_profiles` | One-to-one account; bounded JSONB | Pass |
| 5 | `consent_records` | `nexus.consent_records` | Append-only account history | Pass |
| 6 | `goals` | `nexus.goals` | Account; composite ownership key | Pass |
| 7 | `routines` | `nexus.routines` | Optional same-account goal | Pass |
| 8 | `daily_plans` | `nexus.daily_plans` | Active account/date uniqueness | Pass |
| 9 | `tasks` | `nexus.tasks` | Plan/routine/goal same-account FKs | Pass |
| 10 | `check_ins` | `nexus.check_ins` | Optional same-account task | Pass |
| 11 | `conversations` | `nexus.conversations` | Authenticated account parent | Pass |
| 12 | `messages` | `nexus.messages` | Conversation and ordered uniqueness | Pass |
| 13 | `memory_records` | `nexus.memory_records` | Account, consent, optional source message | Pass |
| 14 | `notification_preferences` | `nexus.notification_preferences` | One-to-one account | Pass |
| 15 | `reminders` | `nexus.reminders` | Optional same-account task | Pass |
| 16 | `notification_deliveries` | `nexus.notification_deliveries` | Reminder history | Pass |
| 17 | `safety_events` | `nexus.safety_events` | Account and optional chat links | Pass |
| 18 | `data_lifecycle_requests` | `nexus.data_lifecycle_requests` | Scoped idempotency | Pass |
| 19 | `support_access_events` | `nexus.support_access_events` | Operator and subject accounts | Pass |
| 20 | `audit_events` | `nexus.audit_events` | Anonymizable actor/subject | Pass |
| 21 | `ai_usage_events` | `nexus.ai_usage_events` | Account and optional chat links | Pass |

**Missing entities:** None.  
**Unnecessary entities:** None. Billing/subscription and clinical data remain correctly excluded by the current PRD.

## 4. Field, type, and requiredness review

- Every Phase 05 dictionary field appears in its DDL table with the same logical meaning.
- `UUID` maps to `uuid`; generated IDs use `gen_random_uuid()`.
- `TIMESTAMP` maps to `timestamptz`; `DATE` remains a user-calendar date.
- `STRING(n)` maps to `varchar(n)` and `TEXT` to `text`.
- `ENCRYPTED_TEXT` and `ENCRYPTED_JSON` map to ciphertext-only `bytea`; there is no plaintext shadow column.
- Approved `JSON` maps to nullable `jsonb` where the dictionary marks it optional, with array/object shape checks and no broad content index.
- Required fields have `NOT NULL`; optional fields remain nullable. Safe defaults match the dictionary.
- Logical “current local date” defaults for `goals.start_date`, `daily_plans.plan_date`, and `check_ins.checkin_date` are intentionally domain-supplied rather than server `CURRENT_DATE`, because the account timezone is user-specific.
- Explicitly approved enum values use named `CHECK` constraints. An unresolved allow-list, such as coaching style, is not invented in SQL.

**Runtime action:** CI must compare `information_schema.columns` with a checked-in expected manifest derived from the approved dictionary.

## 5. PK/FK and ownership review

- All 21 tables use generated UUID primary keys.
- Every approved directly user-owned entity has `account_id`; messages inherit ownership from their approved conversation parent.
- Goal, routine, plan, and task links use composite `(account_id, id)` keys to block cross-account references.
- Memory records retain consent evidence and an optional source message without copying source content.
- Restricted-content and append-only history relationships use `ON DELETE RESTRICT`. Account purge preserves a minimal pseudonymized account anchor so audit references remain immutable.
- No user-editable string is a foreign/business key.

**Runtime action:** Add negative tests for cross-account FKs, orphan IDs, duplicate identities, duplicate active plans, and duplicate active memory fingerprints.

## 6. Constraints and indexes review

Structural checks cover lifecycle states, non-empty titles/reasons, date/time ordering, completion-state consistency, check-in kind, positive sequence/non-negative counters, quiet-hour pairing, JSON shape, and append-only history. Required index families cover:

- identity and session lookup;
- account/status/date lists;
- plan/task/check-in access;
- ordered messages and active memory;
- reminder due work and delivery retries;
- safety/lifecycle/support/audit/AI usage time windows.

No plaintext message, reflection, memory, or consented context is indexed. A staging review must run representative `EXPLAIN (ANALYZE, BUFFERS)` queries before beta.

## 7. Deletion, retention, and privacy review

- Soft-delete fields and lifecycle states match the approved dictionary; they are not treated as proof of physical purge.
- Restrictive FKs prevent accidental cascade deletion. Account purge must be an ordered, audited lifecycle operation.
- Memory revoke/clear must stop retrieval immediately and scrub eligible cache/queue/derived copies. Provider/backup propagation remains TBD.
- Raw passwords, session tokens, prompts, provider payloads/responses, clinical fields, location, and device telemetry are absent.
- Email, context, reflections, messages, memory, and export references require encryption/redaction outside SQL.
- Safe-off channel defaults do not replace current channel consent/provider approval checks.
- Backups, replicas, queues, caches, analytics, exports, and provider copies stay inside the privacy/deletion boundary.

## 8. Normalization and scalability review

- Core facts are normalized; repeating relationships use foreign keys, not arrays.
- JSONB is limited to bounded/versioned metadata and is not used for goals, tasks, messages, or audit payloads.
- Ordered messages page by conversation/sequence without indexing content.
- Audit, usage, delivery, and message tables may grow quickly. Retention and partition thresholds remain pending beta volume and RTO/RPO decisions.
- Composite ownership indexes have an integrity benefit but need production-like size/selectivity measurement.
- Future tenant/household support requires a separately approved scope-key migration; it is not pre-added.

## 9. Migration-safety review

- Initial migration order follows FK dependency order.
- Production execution uses an immutable versioned ledger even though bootstrap operations are repeatable.
- Transactional DDL, bounded locks, concurrent large indexes, staging rehearsal, forward-fix, snapshot/PITR, and worker coordination are documented.
- Destructive down-migrations and `DROP ... CASCADE` are prohibited for production restricted data.

**Runtime action:** The first staging run must capture duration, locks, constraint/index/trigger inventory, backup health, and restore evidence.

## 10. Findings and proposed changes

1. **Static result:** 21/21 entities match; no product-direction contradiction, missing entity, or unnecessary entity was found.
2. **Ownership boundary:** The approved model does not duplicate `account_id` on `messages`; same-account checks for message-linked memory/safety/usage remain service/data-access responsibilities.
3. **Cross-row policy:** Latest granted consent, channel consent, role authority, geography/age eligibility, provider deletion, and safety policy cannot be proven by structural SQL alone.
4. **Runtime pending:** SQL execution, query plans, lock behavior, backup restore, and migration timing require a provisioned staging PostgreSQL instance.

**Proposed changes:** None. A future addition such as `messages.account_id`, RLS policy columns, editable catalogs, billing, or clinical data would change the approved model and must be separately proposed and approved.

## 11. Unresolved decisions

- Launch geography, jurisdiction, minimum age, and age assurance.
- AI provider/model, retention/training policy, regional processing, and provider-side deletion.
- Memory revocation/deletion propagation across caches, jobs, providers, exports, and backups.
- Authentication/MFA, session/recovery policy, and any RLS session-identity contract.
- Admin/support role matrix and break-glass authority.
- Safety-policy ownership, approval, and escalation governance.
- Exact retention, deletion grace/legal holds, backup exceptions, RTO/RPO, availability, beta scale, and cost.
- Managed PostgreSQL provider, region, exact major/tier, migration tool, and production change authority.

These remain `TBD / Pending Decision`; the DDL does not invent answers.

## 12. Phase 06 Approval Checklist

### Documentation and scope

- [x] Approved Phase 05 design, ERD, dictionary, and decisions were reviewed before SQL generation.
- [x] Product/architecture documents 00–04 were checked for consistency.
- [x] No API, endpoint, backend/frontend code, AI implementation, or UI implementation was created.
- [x] No payment, clinical, wearable, location, household, or organization entity was invented.
- [x] The historical operations-copilot concept is not an active requirement.

### Technology and DDL

- [x] PostgreSQL was compared with suitable alternatives and justified.
- [x] DDL contains exactly the 21 approved entities.
- [x] PKs, FKs, ownership, requiredness, uniqueness, checks, indexes, soft-delete, and history behavior are covered.
- [x] Encrypted fields map to ciphertext-only storage; raw secrets/provider payloads are excluded.
- [x] Static ERD/data-dictionary/DDL traceability review passed.
- [ ] A real PostgreSQL staging instance has executed the migrations and runtime checks.

### Migration and approval

- [x] Ordering, dependencies, rollback, forward-fix, seed stance, safety, backups, minimal downtime, and evolution are documented.
- [x] Known privacy, scalability, and runtime risks are identified.
- [x] User approves the PostgreSQL recommendation and Phase 06 package.
- [ ] Provider/region/major, RTO/RPO, retention, and recovery authority are approved before production deployment.

## 13. Gate disposition

**Current disposition:** `Phase 06 approved; runtime validation pending as a follow-up task.`

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

> Documentation and static traceability are complete, and Phase 06 is approved by the user. Runtime staging validation remains pending. Phase 07 through Phase 11 are approved; Phase 12 Implementation Foundation / Project Initialization Part 2 is complete and Final Review is in progress.

**Current project status:** Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. Runtime staging validation remains pending.
