# NexusAI — Privacy Architecture and Compliance Readiness

**Document type:** Phase 10 privacy-by-design, data classification, consent, provider, rights, and compliance-readiness architecture  
**Phase:** Phase 10 — Security, Privacy, Safety & Compliance Architecture  
**Status:** Approved — Phase 10 and Phase 11 documentation gates passed; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-30  
**Scope:** Privacy architecture and readiness considerations only. This is not legal advice and does not claim compliance or applicability.

## 1. Source of truth and privacy posture

The approved Phase 00–09 documents define the wellness-only MVP, consent-based Minimal Memory, 21-entity data model, 77-operation API, provider-neutral AI boundary, UI controls, and safety modes. This document defines how those flows should respect privacy without expanding data collection.

The product must not assume that “health and wellness” data is outside privacy regulation. Applicability depends on launch geography, users, purposes, relationships, data sources, providers, and thresholds that remain `TBD / Pending Decision`.

## 2. Privacy principles

- **Data minimization:** Collect only data necessary for a stated feature.
- **Purpose limitation:** Use data only for the disclosed goal (for example, planning, reminders, progress, or memory personalization).
- **Transparency:** Explain what is collected, why it is used, what the AI receives, and what is remembered.
- **Choice and consent:** Treat memory, optional personalization, notifications/channels, provider processing, and future integrations as distinct choices.
- **User control:** Provide access, correction, export, deletion, revoke, clear, and disable paths consistent with the approved lifecycle.
- **Privacy by default:** Guest data is ephemeral; memory is off by default; sensitive logging is off by default.
- **Accuracy and provenance:** Users can inspect and correct profile, plan, and memory information.
- **Security and confidentiality:** Encrypt restricted data, enforce ownership, limit operator access, and protect derived copies.
- **Retention limitation:** Keep data only as long as a documented purpose/legal basis requires; exact periods are TBD.
- **Accountability:** Version policies, record consent/audit evidence, and maintain a data-flow/copy inventory.

## 3. Data classification

| Level | Meaning | Handling baseline |
| --- | --- | --- |
| `PUBLIC` | Intended for anyone, such as published wellness disclaimer/policy copy | Integrity-controlled, cacheable where appropriate |
| `INTERNAL` | Operational information not intended for public disclosure | Role-limited, not in client responses unless needed |
| `PERSONAL` | Identifies or describes a user/account | Account ownership, access control, encryption in transit/at rest |
| `RESTRICTED` | Wellness, behavior, chat, plan, or memory content whose disclosure could harm trust | Strong encryption, purpose/consent gate, no raw logs, narrow access |
| `HIGHLY RESTRICTED` | Credentials, tokens, keys, recovery proofs, export artifacts, privileged/security evidence | Dedicated secret/key/store boundary, strict access, audited, shortest practical retention |

## 4. Data inventory and handling

| Data category | Classification | Primary purpose | Allowed access | Default prohibitions |
| --- | --- | --- | --- | --- |
| Email/account identity | PERSONAL | Authentication/account contact | Auth/account service; user self-view; narrow support | Provider prompts/log labels unless necessary |
| Profile/name/age or age-band/timezone | PERSONAL or RESTRICTED depending on field | Onboarding and personalization | User and purpose-specific services | Hidden age inference; unnecessary provider disclosure |
| Wellness profile/goals/routines | RESTRICTED | Planning and progress | User-owned services and approved context | Cross-account/support default access |
| Tasks/plans/check-ins/progress | RESTRICTED | Daily wellness tracking | User-owned services; bounded AI context | Clinical scoring or unrelated analytics |
| Conversations/messages | RESTRICTED | User chat history and current context | User-owned chat; AI gateway per request; support not default | Raw logs, unrestricted support, provider retention assumptions |
| Approved memory values | RESTRICTED/HIGHLY RESTRICTED | Explicit personalization purpose | Memory policy/service and user; narrow audited support only | Auto-save, unconsented retrieval, notification body, model training |
| Consent records | RESTRICTED | Evidence of choices and policy versions | User safe projection, privacy/security roles | Silent rewriting or inferred consent |
| Audit/safety/support events | INTERNAL/RESTRICTED | Accountability, security, incident review | Narrow operators/security; user-safe projections | Raw content, broad support/admin visibility |
| AI provider metadata | INTERNAL | Usage, latency, failure, policy operations | Operations/security; user coarse usage | Prompts, completions, secrets, provider payloads |
| Export artifacts | HIGHLY RESTRICTED | User-requested data copy | Requesting user and authorized lifecycle worker | Public URLs, indefinite retention, support browsing |
| Backups/replicas/derived indexes | RESTRICTED/HIGHLY RESTRICTED | Recovery/availability or bounded retrieval | Recovery/platform roles only | Restore into active service without lifecycle reconciliation |

## 5. Consent and purpose architecture

Consent is granular and current. The system should model at least the separate decisions already present in approved documents:

- product policies/Terms and Privacy acknowledgement;
- optional personalization context;
- AI memory retrieval/write;
- reminder use and optional notification channels;
- future integrations or data sources;
- any distinct provider processing or model-improvement use.

Each use records purpose, policy/version, decision, capture source, timestamp, and account scope in the approved consent boundary. The UI must not bundle optional memory, notifications, and model training into one preselected choice. A user can use chat when memory is disabled; the system omits memory rather than withholding unrelated core features.

The legal basis, controller/processor roles, consent wording, age/parental rules, and jurisdiction-specific notices remain TBD.

## 6. AI provider privacy

Before restricted wellness/chat/memory context is sent to an external provider, the system must document:

- the exact purpose and minimum fields;
- current consent/policy decision;
- identifiers redacted or pseudonymized where practical;
- provider retention/deletion and training-use terms;
- regional processing and subprocessors;
- breach/incident notification and security commitments;
- data-subject request support and deletion propagation;
- exit/replacement plan.

If the provider cannot provide an approved answer or control, route to a safe deterministic response/alternative or block the operation. Do not promise that provider data is deleted merely because the primary database row is deleted.

Private user content must not be used for model training without separate explicit consent and an approved policy. Personalization, prompt/context improvement, memory update, and foundation-model training remain distinct processing purposes.

## 7. User rights and product controls

Subject to the applicable jurisdiction and approved policy, the product should be ready to support:

- access/view of profile, consent, memory, and user-owned content;
- correction/edit of profile, goals, routines, and memory;
- export in a commonly usable electronic form when the final format is approved;
- deletion/erasure and memory clear/revoke workflows;
- restriction/disable of memory and optional notifications;
- explanation of provider-bound data and retention where required;
- appeal/support path for denied or failed requests.

The API exposes lifecycle status rather than internal storage paths. The UI distinguishes accepted, queued, running, failed, and verified-completed requests. Legal exceptions, fees, identity verification, response windows, and exact formats remain TBD.

## 8. Data minimization and privacy-preserving defaults

- Guest interaction accepts constrained non-sensitive intent only.
- Onboarding optional lifestyle fields are skippable where policy permits.
- Memory values are bounded encrypted JSON with category/purpose constraints.
- AI context includes only current conversation, necessary goals/plans/check-ins, and eligible approved memory.
- Notifications contain non-sensitive text by default.
- Logs/metrics/traces omit raw chat, memory, prompts, completions, tokens, secrets, and export content.
- Derived summaries/indexes are treated as sensitive copies and carry consent/version/lifecycle metadata.
- Analytics use aggregate/coarse signals and avoid health-content labels.

## 9. Privacy impact review triggers

Perform a documented privacy/safety review before enabling:

- new health or biometric data;
- wearable/calendar/location/contacts integrations;
- children/minors or age-sensitive populations;
- automated profiling or decisions with meaningful effects;
- new provider/region/subprocessor;
- voice recordings/transcripts;
- payment/billing information;
- broader memory categories or cross-domain Life OS data;
- model training or dataset reuse;
- support/admin access to private content.

## 10. Compliance readiness (not an applicability or compliance claim)

| Framework/regime | Readiness relevance | Applicability status |
| --- | --- | --- |
| GDPR / UK GDPR-style obligations | Data minimization, purpose limitation, transparency, access/correction/erasure, security, processor/transfer controls, and accountability are useful design requirements. The GDPR text describes purpose limitation/data minimization and erasure rights. | `POTENTIALLY RELEVANT`; depends on offering/monitoring people in covered jurisdictions and legal-role analysis |
| CCPA/CPRA | California consumer rights, sensitive-personal-information handling, purpose limitation, minimization, deletion/correction/access, and non-discrimination may be relevant. CPPA materials describe these rights and requirements. | `POTENTIALLY RELEVANT`; thresholds, business role, data practices, and 2026 rules require counsel review |
| COPPA and age rules | If the service is directed to children under 13 or has actual knowledge of collecting their information, parental-consent and related controls may apply. | `PENDING`; minimum age, age assurance, and audience are unresolved |
| HIPAA Privacy/Security Rules | HHS states HIPAA applies to covered entities and business associates; a consumer wellness product is not automatically a covered entity. Relationship, data source, and service role must be assessed. | `POTENTIALLY RELEVANT`; no HIPAA applicability is claimed |
| FTC Health Breach Notification Rule | Consumer health applications outside HIPAA may have breach-notification obligations for unsecured identifiable health information. | `POTENTIALLY RELEVANT`; U.S. product/data-flow assessment required |
| SOC 2 | A future independent examination/report against Trust Services Criteria can provide assurance over security, availability, processing integrity, confidentiality, and privacy controls. | `FUTURE READINESS`; not a law or current attestation |
| PCI DSS | Relevant only if NexusAI stores, processes, or transmits payment-card data or affects the cardholder-data environment. The MVP has no approved payment/card flow. | `NOT IN CURRENT MVP SCOPE`; reassess before subscriptions/payments |

Official reference material consulted for this readiness summary:

- [EUR-Lex GDPR Regulation 2016/679, Articles 5, 17, and 32](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng)
- [California Privacy Protection Agency — CCPA/CPRA FAQ](https://cppa.ca.gov/faq)
- [FTC — COPPA Rule](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)
- [HHS — Covered Entities and Business Associates](https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html)
- [FTC — Health Breach Notification Rule](https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule)
- [AICPA — SOC 2 Trust Services Criteria](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2/)
- [PCI Security Standards Council — PCI DSS](https://www.pcisecuritystandards.org/standards/pci-dss/)

These references support readiness considerations only. Qualified legal/privacy review is required before launch or claims of compliance.

## 11. Privacy governance

Recommended governance artifacts:

- data inventory and system-of-record map;
- purpose/consent matrix;
- provider/subprocessor register;
- retention/deletion schedule;
- data-subject request procedure;
- privacy impact assessment trigger log;
- access/role review and break-glass review;
- incident and breach-notification playbook;
- policy/version and user-notice change log.

The accountable privacy owner and legal review authority are `TBD / Pending Decision`.

## 12. Phase boundary

This document defines privacy architecture and compliance readiness only. It does not provide legal advice, declare applicability, draft final legal notices, implement consent screens, or certify a framework.
