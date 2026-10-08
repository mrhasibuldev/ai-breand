# NexusAI — Phase 10 Security, Privacy & Safety Decisions

**Document type:** Phase 10 decision log, traceability, findings and approval gate  
**Phase:** Phase 10 — Security, Privacy, Safety & Compliance Architecture  
**Status:** Approved — Phase 10 and Phase 11 documentation gates passed; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-30  
**Scope:** Architecture and governance decisions only. No implementation or compliance certification is created.

## 1. Decision authority and source of truth

The approved documentation chain is:

1. [Project overview](00-project-overview.md) — product identity, mission and phase governance.
2. [Product discovery](01-product-discovery.md) — users, assumptions and unresolved product decisions.
3. [PRD](02-prd-nexus-ai-health-companion-mvp.md) — MVP scope, non-goals and acceptance intent.
4. [System architecture](03-system-architecture-outline.md) — trust boundaries and component responsibilities.
5. [Architecture review](04-architecture-review.md) — reviewed architecture findings and approvals.
6. [Database package](05-database-design.md) — approved entities, lifecycle and ownership model.
7. [DDL/migration package](06-database-implementation.md) — approved implementation specification (no automatic schema changes here).
8. [API package](07-api-design.md) — approved external/internal contracts and API security baseline.
9. [AI package](08-ai-intelligence-architecture.md) — provider-neutral brain, memory, planning and safety behavior.
10. [UI/UX package](09-ui-ux-architecture.md) — approved user flows, consent/revocation and safety presentation.
11. Phase 10 documents — security, privacy, safety and compliance controls; they may clarify controls but may not silently change prior domain contracts.

If documents conflict, the conflict is recorded here and resolved by an explicit user-approved change. No conflict with the approved Product/PRD/Architecture/Database/API/AI/UI domain model is proposed in this phase.

## 2. Security and privacy decision log

| ID | Decision | Rationale / consequence | Status |
| --- | --- | --- | --- |
| SEC-01 | Deny-by-default, zero-trust boundaries | Every request, worker job, provider call and operator action is authenticated, authorized, scoped and auditable | Accepted architecture |
| SEC-02 | User ownership is enforced at the service/data boundary | Prevents IDOR and cross-user access; `/me` is the normal user scope | Accepted architecture |
| SEC-03 | Support/admin receive metadata projections only by default | Limits insider exposure; chat, memory and health details require an approved, audited exception | Accepted architecture; exact matrix TBD |
| SEC-04 | MFA/step-up is required for privileged and destructive actions | Reduces account takeover and deletion/export abuse | Control required; provider/baseline TBD |
| SEC-05 | Minimal Memory is off by default and consent-gated | Memory is optional, reviewable, revocable and deletable; no silent auto-save | Accepted product/AI contract |
| SEC-06 | Revocation fails closed immediately; cleanup is asynchronous | Prevents continued use while queues, indexes, caches, providers and backups converge | Accepted lifecycle rule; propagation SLA TBD |
| SEC-07 | Model output is untrusted | Models cannot grant access, consent, tool permission, safety override or source-of-truth status | Accepted AI security rule |
| SEC-08 | Tools use explicit allowlists and confirmation | Prevents prompt-injected or hallucinated actions; every execution is validated and audited | Accepted AI contract; tool inventory TBD |
| SEC-09 | Provider-neutral adapter and minimal payloads | Enables provider replacement and avoids retaining raw provider payloads | Accepted architecture; provider/region TBD |
| SEC-10 | Encryption in transit and at rest with managed key controls | Reduces disclosure impact; keys/secrets are not stored in application data or logs | Control required; KMS/rotation details TBD |
| SEC-11 | Append-only, redacted audit trail | Supports accountability without putting health/chat content into ordinary logs | Accepted architecture; retention TBD |
| SEC-12 | Deletion, export and backup lifecycle are first-class controls | Account deletion must cover active, derived, queued, provider and backup copies with evidence | Accepted lifecycle rule; legal hold/windows TBD |
| SEC-13 | Safety modes are deterministic policy states around model calls | Wellness MVP must redirect/escalate unsafe or clinical requests and never present diagnosis/treatment as fact | Accepted AI/UI contract; owner/thresholds TBD |
| SEC-14 | Synthetic-only security test data | Prevents test environments from becoming an unapproved health-data store | Accepted testing rule |

## 3. Product-to-security traceability

| Source requirement | Security/privacy control | Evidence document |
| --- | --- | --- |
| Wellness-only, non-diagnostic MVP | Safety modes, refusal/redirect, clinical-claim tests and human ownership | PRD; 08 safety; 10 AI/security/testing |
| Guest → account upgrade | Rate limits, enumeration resistance, verification, session security and consent capture | PRD; 07 auth/security; 10 auth/threat |
| Personalization and progress | `/me` ownership, row-level predicates, input validation, integrity tests | PRD; 05 DB; 07 API; 10 threat/testing |
| AI chat | Context minimization, prompt isolation, output validation, provider abstraction and redacted telemetry | PRD; 08 AI; 10 AI/privacy |
| Permission-based Minimal Memory | Consent/version records, proposal/confirmation UI, revoke/delete, derived-copy cleanup | 05 DB; 08 memory; 09 UX; 10 privacy/retention/AI |
| Reminders/notifications | Least-content payloads, channel/quiet-hour controls, delivery audit without health text | PRD; 05 DB; 09 screens; 10 privacy/threat |
| Account deletion/export | Step-up, queued lifecycle, tombstones, provider/backup treatment and evidence | 07 API; 09 UX; 10 retention/incident |
| Security-first platform | Encryption, secrets, RBAC, audit, backups, validation, monitoring and incident response | 03 architecture; 04 review; 10 security |
| Future personal-AI extensibility | Versioned policies, provider-neutral interfaces, scoped tools, schema/API evolution gates | 08 architecture; 10 AI/testing/decisions |

## 4. Compliance readiness posture

The MVP is not declared compliant or certified. Applicability depends on launch geography, age, business model, data relationships and legal review. The readiness posture is intentionally “controls planned / applicability pending”:

| Regime | Current posture | Design implication |
| --- | --- | --- |
| GDPR | Potentially relevant; applicability and roles TBD | Purpose limitation, minimization, security, access/erasure workflows and breach process are designed for review |
| CCPA/CPRA | Potentially relevant for California consumers; thresholds/applicability TBD | Notice, access/delete/correct/opt-out handling and no dark patterns require product/legal confirmation |
| COPPA | Age/minimum-age and actual-knowledge posture TBD | Do not knowingly collect from under-13 users until age/parental-consent decision is approved |
| HIPAA | Not assumed applicable; entity/BAA relationship TBD | Do not market as HIPAA-covered; assess covered-entity/business-associate role before integrations |
| FTC HBNR | Potentially relevant to a consumer health app; scope/legal review TBD | Maintain incident evidence and a notification decision path |
| SOC 2 | Future readiness, not certification | Map controls/evidence to Trust Services Criteria if a later assurance project is approved |
| PCI DSS | Keep payment data out of NexusAI where possible; applicability depends on payment integration | Use a tokenized payment provider and confirm scope before subscriptions |

References: [GDPR text](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng), [CPPA FAQ](https://cppa.ca.gov/faq), [CPPA regulations](https://cppa.ca.gov/regulations/), [FTC COPPA Rule](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa), [HHS covered entities/business associates](https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html), [FTC Health Breach Notification Rule](https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule), [AICPA SOC 2 criteria](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2/), [PCI DSS](https://www.pcisecuritystandards.org/standards/pci-dss/).

## 5. Findings and blockers

### Critical

No new Critical finding is accepted. Any cross-user disclosure, auth bypass, unconsented memory/provider use, unsafe consequential tool execution, or deletion resurrection is a release blocker and must be escalated immediately.

### High — launch blockers unless explicitly remediated and approved

- **H-01 Identity baseline unresolved:** auth provider, MFA requirement, session/cookie model, recovery and suspicious-login controls are not selected.
- **H-02 Privileged-access boundary unresolved:** exact support/admin/security/privacy/safety role matrix, break-glass approvers and expiry are pending.
- **H-03 Provider/data-region risk unresolved:** AI provider, model, retention/training, processing region and deletion guarantees are pending.
- **H-04 Lifecycle assurance unresolved:** exact retention windows, legal-hold policy, backup purge behavior, deletion propagation SLA and RTO/RPO are pending.
- **H-05 Safety governance unresolved:** named policy owner, escalation authority, jurisdictional copy and evaluation thresholds are pending.

### Medium

- Rate-limit, quota, bot-detection and beta-scale targets are not set.
- Notification content/channel/quiet-hour and localization decisions can create privacy leakage.
- Durable idempotency and audit evidence storage details require implementation review.
- Independent penetration testing and compliance evidence scope are not scheduled.

### Low

- Future device integrations, advanced analytics and regionalization may add data classes and consent surfaces.
- Security UX copy and final brand/accessibility testing remain implementation work after this gate.

## 6. Remaining TBD / Pending decisions

1. Launch geography, jurisdictions and legal entity/data-controller roles.
2. Minimum age, age assurance and parental-consent approach.
3. AI provider/model, processing regions, provider retention/training, deletion and fallback terms.
4. Memory deletion/revocation propagation guarantees across caches, indexes, queues, providers and backups.
5. Authentication provider, cookie vs bearer transport, MFA baseline, session/recovery policy.
6. Admin/support role matrix, break-glass dual-control and private-content visibility.
7. Safety policy owner, escalation partner, thresholds, copy and review cadence.
8. Exact retention windows, legal-hold authority and backup expiry/purge method.
9. RTO/RPO, beta scale, rate limits, cost/latency targets and continuity-test cadence.
10. Reminder channels/recurrence/quiet hours, localization and export format/lifecycle.
11. Key-management service, rotation cadence, incident staffing and notification authority.

These are intentionally not invented or silently resolved by Phase 10.

## 7. Phase 10 approval checklist

### Documentation complete

- [x] Security architecture and trust boundaries are documented.
- [x] Threat model covers account, API, data, AI, tool, insider, provider, availability and lifecycle threats.
- [x] Authentication, session, RBAC/ABAC, ownership and break-glass controls are documented.
- [x] Data classification, minimization, consent, privacy rights and compliance-readiness posture are documented.
- [x] Memory privacy, AI/provider/tool security and safe failure behavior are documented.
- [x] Admin/support access, audit, retention/deletion, export and backup implications are documented.
- [x] Incident response and security/privacy/safety testing strategy are documented.
- [x] Product → PRD → Architecture → Database → API → AI → UI/UX → Security traceability is reviewed.
- [x] No application code, API implementation, DDL/migration, UI implementation or Phase 11 artifact was created.

### Approval items

- [x] User approved the Phase 10 security, privacy, safety and compliance architecture package.
- [x] User explicitly accepted the listed High blockers as mandatory public-beta/production gates pending decisions.
- [ ] Owners and dates are assigned for the unresolved identity, privileged-access, provider, lifecycle and safety decisions.

## 8. Phase boundary and gate disposition

**Current disposition:** Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

> **Current disposition:** `Phase 10 and Phase 11 approved; Phase 12 approved; Phase 13 not started and pending explicit user approval; awaiting explicit instructions.`

This package defines security, privacy, safety and compliance architecture only. Phase 10 and Phase 11 approval do not approve public beta or production; the High blockers remain mandatory gates. Phase 12 Implementation Foundation / Project Initialization Part 2 is complete; no proposed change to the approved domain model is submitted.
