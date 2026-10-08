# NexusAI — Phase 08 AI Architecture Decisions and Review

**Document type:** Phase 08 decision log, traceability review, risk register, and approval checklist  
**Phase:** Phase 08 — AI Brain, Personal Memory & Intelligence Architecture  
**Status:** Approved — Phase 08 gate passed; Phase 09 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-29  
**Scope:** Architecture review only. No AI implementation, provider integration, model training, vector deployment, API implementation, or Phase 09 work is authorized.

## 1. Review scope and source of truth

This review uses the approved Phase 00–07 documentation as its source of truth:

- Project vision and canonical product identity;
- Product discovery and MVP boundaries;
- PRD acceptance criteria and risks;
- system architecture and trust boundaries;
- 21-entity database/DDL model;
- 77-operation API contract, authentication, error, security, and validation boundaries.

The Phase 08 documents add intelligence-layer behavior without changing approved business entities or public API semantics. Any new capability not traceable to an approved requirement is marked `FUTURE` and requires a later product/privacy/safety gate.

## 2. Confirmed architectural decisions

| ID | Decision | Status | Rationale |
| --- | --- | --- | --- |
| AI-01 | NexusAI is a Personal AI Health & Wellness Companion; V1 is wellness-only | Confirmed | Matches canonical product, PRD, and safety boundary |
| AI-02 | The MVP uses an `IntelligenceEngine`/`ModelGateway` abstraction | Confirmed | Allows current provider use without business-logic lock-in |
| AI-03 | No proprietary foundation model or trained NexusAI LLM is claimed in V1 | Confirmed | Long-term vision is separated from current capability |
| AI-04 | Application policy owns consent, memory, safety, authorization, and domain state | Confirmed | A model cannot become the source of truth or override controls |
| AI-05 | Memory is Minimal Memory, off by default, purpose-bound, visible, editable, revocable, and deletable | Confirmed | Matches approved database/API lifecycle |
| AI-06 | Guest AI use is ephemeral and non-sensitive | Confirmed | Prevents guest data entering private accounts/memory |
| AI-07 | Safety is enforced before and after model calls | Confirmed | Supports normal, redirect, escalation, and blocked modes |
| AI-08 | Planning is bounded and proposal-first; domain services commit state | Confirmed | Preserves user confirmation and ownership |
| AI-09 | Tools are typed, allow-listed, permission-checked, validated, and audited | Confirmed | Prevents unrestricted autonomous access |
| AI-10 | Raw prompts, completions, hidden reasoning, and provider payloads are not core business data | Confirmed | Least-data-necessary and provider replacement |
| AI-11 | Private user content is not used for model training without separate explicit consent and approved policy | Confirmed | Matches PRD/privacy requirements |
| AI-12 | No API/database schema changes are proposed by Phase 08 | Confirmed | Phase boundary and approved model are preserved |

## 3. Product-to-intelligence traceability

| Approved requirement | Architecture realization | Database/API alignment | Phase 08 disposition |
| --- | --- | --- | --- |
| Guest can try limited features | Ephemeral guest context and bounded gateway flow | Guest routes; no guest durable entity | Implementable design; TTL/quota TBD |
| Registration/onboarding/personalization | Context assembler uses approved profile, wellness, consent, goals, routines, and preferences | `accounts`, `user_profiles`, `wellness_profiles`, `consent_records`; `/me/*` routes | In scope |
| Healthy habits, routines, reminders | Planning graph and typed first-party capabilities | `goals`, `routines`, `daily_plans`, `tasks`, `reminders`, notification entities | In scope; recurrence/channels TBD |
| Check-ins and progress | Progress-aware bounded planning suggestions | `check_ins`; derived progress API | In scope; no clinical inference |
| AI wellness chat | Input/context/safety/gateway/output pipeline | `conversations`, `messages`, `safety_events`, `ai_usage_events`; chat routes | In scope |
| Consent-based Minimal Memory | Candidate → consent → approved retrieval → revoke/delete lifecycle | `memory_records`, `consent_records`, `data_lifecycle_requests`, `audit_events`; memory routes | In scope; propagation TBD |
| Safety and non-diagnostic guidance | Dual-gate safety policy and four response modes | `safety_events`; chat response modes | In scope; policy owner/copy TBD |
| User-controlled deletion/export | Immediate read block plus bounded cleanup evidence | Lifecycle API and `data_lifecycle_requests` | In scope; provider/backup guarantees TBD |
| Least-privilege support | No default private transcript/memory access | Support API, `support_access_events`, `audit_events` | In scope; role matrix TBD |
| Future Personal AI capabilities | Stable gateway, memory, planning, tool, and policy seams | Existing model remains extensible | Explicitly FUTURE; not active MVP scope |

**Traceability result:** Every major MVP AI capability maps to an approved PRD requirement and an existing architecture/database/API boundary. Future proprietary Brain capabilities are explicitly separated from the MVP.

## 4. Intelligence architecture review

### 4.1 Personalization and identity

Pass with runtime controls. Session, short-term, approved long-term, derived, and user-controlled context are separated. The system does not claim a persistent model self and does not infer unrestricted profile facts. Age remains limited to approved profile/age-band handling; minimum age and age assurance are unresolved.

### 4.2 Memory

Pass with deletion-runtime controls. Candidate memory is ephemeral until consent; categories match the approved database constraint; retrieval checks consent, purpose, status, expiry, sensitivity, relevance, and ownership. Immediate fail-closed revocation is specified. Physical cleanup across derived copies, providers, and backups remains unresolved.

### 4.3 Planning and bounded agent behavior

Pass with confirmation/runtime controls. Goal → plan → task → routine → check-in → progress → adjustment is preserved. Proposals are structured and bounded; domain services remain state authority. No unrestricted autonomous system access is designed.

### 4.4 Tool execution

Pass with future-integration gates. MVP capabilities are first-party wellness operations; external calendar, search, wearable, messaging, and healthcare tools are future. Each capability requires permission, schema validation, output validation, auditability, idempotency, and failure behavior.

### 4.5 Safety

Pass with governance gate. Pre/post evaluation, response modes, output claim checks, memory restrictions, and fail-closed behavior are defined. No clinical protocol is invented. Safety owner, escalation authority, jurisdiction-specific copy, and evaluation thresholds remain TBD.

### 4.6 Provider abstraction and future Brain

Pass with provider decision gate. The gateway normalizes operations/errors/usage and keeps adapters replaceable. The roadmap distinguishes individual personalization/context/memory from model training. No proprietary model capability is claimed.

### 4.7 Privacy, security, and data flow

Pass with operational evidence required. Context is minimized; raw prompts/responses are excluded from ordinary telemetry; ownership and consent are checked at each boundary. Deletion, provider retention/training, regional processing, and legal hold behavior remain TBD.

### 4.8 Cost, performance, and observability

Pass at conceptual level. Deterministic work stays in application services; model routing, context budgets, async jobs, bounded retries, usage telemetry, and safe fallbacks are defined. Numeric quotas, budgets, latency targets, RTO/RPO, and beta scale remain TBD.

## 5. Missing and unnecessary capability review

### Missing MVP capabilities

No approved MVP AI capability is missing from the Phase 08 package. Chat, personalization, consented memory, planning, progress-aware suggestions, reminders, safety, deletion, and usage observability are represented.

### Intentionally excluded capabilities

- Diagnosis, treatment, dosage, clinical triage, emergency dispatch, or clinical records.
- Unrestricted conversation recall or “remember everything.”
- Automatic training of any model from private user conversations.
- Autonomous external actions, arbitrary tool calls, database/filesystem/shell access.
- Guest durable memory or cross-account context.
- Wearable, calendar, search, social, household, organization, billing, or clinician integrations.

These exclusions are consistent with the approved PRD and are not gaps.

## 6. Findings and risk register

| Finding | Severity | Impact | Required treatment |
| --- | --- | --- | --- |
| No approved provider retention/training/deletion and regional-processing contract | Critical for launch | User content may be processed under unknown terms | Provider/legal/privacy decision and evidence before real user data is sent |
| Safety policy owner, escalation authority, and jurisdictional guidance unresolved | High | Unsafe or inconsistent responses may reach users | Assign accountable owner, reviewed policy artifacts, and launch sign-off |
| Memory deletion/revocation propagation across caches, queues, providers, exports, and backups unresolved | High | Revoked data could persist in derived copies | Define evidence-based lifecycle contract; retrieval must fail closed meanwhile |
| Auth/MFA baseline and support/break-glass role matrix unresolved | High | Unauthorized access or unsafe operator visibility | Approve identity, step-up, scope, expiry, and audit model before implementation |
| Model capability/quality bar and safety evaluation thresholds unresolved | High | Model may be overconfident or unreliable | Define evaluation set, acceptance thresholds, regression process, and rollback |
| Durable idempotency store for non-lifecycle AI/tool mutations unresolved | Medium | Retries may duplicate a side effect | Decide gateway/cache versus durable ledger; never claim exactly-once without evidence |
| Retrieval technology, embedding/index retention, and provenance explanation unresolved | Medium | Relevance, cost, and deletion behavior may vary | Keep deterministic metadata fallback; approve index/data lifecycle separately |
| Context/token budgets, quotas, cost budget, latency/SLO, beta scale unresolved | Medium | Cost or performance may exceed safe operating limits | Capacity and budget decision before production rollout |
| Tool confirmation rules and recurrence/channel semantics incomplete | Medium | User may receive unexpected reminders or plan changes | Product decision and contract tests before tool enablement |
| Prompt/policy/version artifact ownership and release workflow not yet assigned | Medium | Inconsistent behavior and weak rollback/audit | Establish artifact registry, reviewer, effective time, and rollback process |
| Localization and provenance UX details unresolved | Low | Users may misunderstand guidance or memory origin | Define copy/localization and usability testing before broad launch |

No Phase 08 finding requires changing the approved 21-entity database model or 77-operation API contract. The findings are gates, operational decisions, or later implementation controls.

## 7. Future architecture risks

- **Model drift:** provider/model updates can alter safety or tone; use versioned evaluation and controlled rollout.
- **Memory poisoning:** an incorrect or adversarial candidate could become durable; retain explicit review, purpose limits, and edit/delete controls.
- **Inference leakage:** derived summaries or embeddings may reveal more than the source; treat them as sensitive derived copies with lifecycle rules.
- **Prompt injection:** user or retrieved content may attempt to override policy; keep policy layers separate and validate tool calls outside the model.
- **Provider lock-in:** vendor-specific features may leak into business logic; preserve normalized gateway schemas and adapter contract tests.
- **Autonomy creep:** convenience tools may become consequential actions; require a new capability gate for every side effect.
- **Proprietary Brain transition:** internal model ownership may create false trust; apply the same privacy, safety, quality, and audit gates.
- **Data-copy sprawl:** caches, queues, exports, telemetry, and indexes may outlive source data; maintain a copy inventory and deletion evidence.
- **Scope/regulatory drift:** wellness features may be interpreted as clinical; maintain persistent boundaries and qualified review.

## 8. Remaining TBD / Pending Decisions

- Launch geography, privacy jurisdiction, minimum age, and age assurance.
- Authentication provider, transport, MFA, recovery, session lifetime, and step-up baseline.
- Admin/support role matrix, break-glass procedure, operator expiry, and private-content access policy.
- Safety policy owner, escalation authority, jurisdiction-specific guidance, and release governance.
- AI provider/model, provider retention/training, regional processing, subprocessors, and deletion guarantees.
- Memory revocation/deletion propagation, derived-copy retention, backup/legal-hold handling, and exact retention windows.
- Retrieval/index/embedding approach, semantic search necessity, and derived-context retention.
- Exact recurrence model, reminder channels, planning/tool quotas, and confirmation rules.
- Model quality/safety thresholds, context/token budgets, rate limits, beta scale, cost, latency, RTO/RPO, and availability targets.
- Export format/download mechanism, localization, and user-facing memory provenance UX.

These are intentionally not answered by Phase 08.

## 9. Phase 08 Approval Checklist

### Documentation and architecture

- [x] Approved Phase 00–07 documents were reviewed as source of truth.
- [x] AI intelligence pipeline and layer responsibilities are documented.
- [x] Personal AI identity and context classes are separated.
- [x] Consent-based memory lifecycle, taxonomy, retrieval, and deletion behavior are documented.
- [x] Goal → plan → task → routine → check-in → progress → adjustment is documented.
- [x] Bounded planning and typed tool/action boundaries are documented.
- [x] Safety modes, pre/post gates, escalation boundaries, and fail-closed behavior are documented.
- [x] Modular policy/context assembly is documented; no giant prompt is required.
- [x] Provider/model abstraction and future proprietary Brain roadmap are documented.
- [x] End-to-end AI data flows, trust boundaries, privacy, observability, and failures are documented.
- [x] Product → PRD → Architecture → Database → API → AI traceability review is complete.
- [x] Critical/high/medium/low findings and future risks are recorded.
- [x] No implementation code, model training, vector deployment, or Phase 09 work was created.

### Approval items

- [x] User approves the AI intelligence architecture and layer boundaries.
- [x] User approves the consent-based memory architecture and accepts deletion/provider items as TBD.
- [x] User approves bounded planning, tool authorization, and no-unrestricted-autonomy rules.
- [x] User approves the safety modes and governance boundary without treating them as clinical protocols.
- [x] User approves the provider abstraction and future proprietary Brain roadmap.
- [x] User acknowledges that unresolved provider, safety, identity, retention, and operating decisions require resolution before implementation/release.

## 10. Gate disposition

**Current disposition:** Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

> **Current disposition:** `Phase 08 through Phase 11 approved; Phase 12 approved; Phase 13 not started and pending explicit user approval; awaiting explicit instructions.`

The Phase 08 architecture package is complete and approved. Phase 09 through Phase 11 are also approved. Phase 12 Implementation Foundation / Project Initialization Part 2 is complete; full application implementation remains outside this authorization.
