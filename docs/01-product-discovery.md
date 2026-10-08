# NexusAI — Personal AI Health & Wellness Companion — Product Discovery

**Product name:** NexusAI  
**Current product direction:** Personal AI Health & Wellness Companion  
**Document type:** Canonical Product Discovery / Phase 02  
**Status:** Canonical approved baseline; Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. Unresolved decisions remain `TBD / Pending Decision`.  
**Last updated:** 2026-09-07  
**Source of truth:** The hierarchy in the section below controls product decisions; unresolved items remain `TBD / Pending Decision`.

## SOURCE OF TRUTH

**Canonical product:** `NexusAI — Personal AI Health & Wellness Companion`.

Document authority for the current project:

1. `00-project-overview.md` — Project Vision & Mission; canonical product identity and long-term direction.
2. `01-product-discovery.md` — Product Discovery; problem, users, hypotheses, scope rationale and validation assumptions.
3. `02-prd-nexus-ai-health-companion-mvp.md` — PRD; testable MVP requirements and acceptance criteria.
4. `03-system-architecture-outline.md` — System Architecture; logical boundaries, trust boundaries and runtime flows.
5. `04-architecture-review.md` — Architecture Review; findings, corrective actions and phase gates.
6. `05-database-design.md` — approved Phase 05 conceptual database-design artifact.
7. Future API Design.
8. Future AI/Memory Design.
9. Future UI/UX Design.
10. Future Implementation.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

> Pre-existing later-phase files are outside the authority of the 2026-09-07 Phase 04 approval and remain untouched pending separate review.

**Current authorization:** Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

When documents conflict, the higher document in this hierarchy wins. A lower-level document must flag the conflict and request correction; it must not invent a new requirement. The old operations-copilot concept is historical only and is labeled **SUPERSEDED / HISTORICAL — NOT CURRENT PRODUCT REQUIREMENT**.

## 1. Discovery purpose

এই document-এ NexusAI Health Companion MVP-এর target users, problem, value hypothesis, user journey, feature boundaries, safety posture, memory evolution এবং validation plan সংজ্ঞায়িত করা হয়েছে। এটি PRD-এর product rationale; এটি API, database schema বা implementation specification নয়।

## 2. Canonical product statement

NexusAI হলো এমন একটি personal AI health and wellness companion, যা user-এর permission নিয়ে gradually personalize করে, healthy habits ও routines organize করতে সাহায্য করে, reminders/check-ins-এর মাধ্যমে progress track করে এবং safe, non-diagnostic wellness guidance দেয়।

### Historical note

একটি পুরোনো discovery draft-এ NexusAI-কে professional-service teams-এর operations copilot হিসেবে বর্ণনা করা হয়েছিল। সেটি **SUPERSEDED / HISTORICAL — NOT CURRENT PRODUCT REQUIREMENT**। Operations-copilot roles, workflows, citations, client-service review বা B2B workspace assumptions বর্তমান Health Companion MVP-তে প্রযোজ্য নয়।

## 3. User problem

অনেক মানুষ স্বাস্থ্যকর habit শুরু করতে চান, কিন্তু intention-কে দৈনন্দিন routine-এ রূপান্তর করা কঠিন হয়। Common pain points:

- goals অনেক বড় বা অস্পষ্ট হওয়ায় শুরু করা কঠিন;
- reminders বিচ্ছিন্ন বা অতিরিক্ত হওয়ায় routine টেকে না;
- progress বোঝার মতো simple feedback থাকে না;
- generic wellness advice ব্যক্তিগত schedule বা preference-এর সঙ্গে মেলে না;
- AI কী মনে রাখছে তা স্পষ্ট নয়;
- health-related প্রশ্নে সাধারণ advice এবং medical advice-এর সীমা বিভ্রান্তিকর হতে পারে।

## 4. Target users and jobs-to-be-done

### 4.1 Wellness Builder

**Profile:** একজন adult user, যিনি sleep, movement, hydration, mindfulness, nutrition routine বা অনুরূপ everyday wellness habit উন্নত করতে চান।

**Job:** “আমার লক্ষ্যকে ছোট, বাস্তবসম্মত daily action-এ ভাঙতে সাহায্য করো; আমি কতটা এগোলাম তা দেখাও; আমাকে বিচার না করে adjust করতে দাও।”

### 4.2 Routine Manager

**Profile:** পরিবর্তনশীল schedule-এর user, যিনি reminder, quiet hours, pause/snooze এবং check-in control চান।

**Job:** “আমার দৈনন্দিন routine মনে করিয়ে দাও, কিন্তু আমার ওপর চাপ সৃষ্টি করো না।”

### 4.3 Guest evaluator

**Profile:** account তৈরির আগে product পরীক্ষা করা visitor।

**Job:** “আমার sensitive information না দিয়েই বুঝতে চাই productটি আমার জন্য উপকারী কি না।”

### 4.4 Authorized support/admin

**Profile:** account/support operations সামলানো সীমিত privilege-এর operator।

**Job:** “Account, abuse বা delivery সমস্যা সমাধান করতে চাই, কিন্তু private chat/memory অযথা দেখতে চাই না।”

## 5. Product hypotheses

| Hypothesis | MVP signal | Validation approach |
| --- | --- | --- |
| Small, explicit goals improve activation | User activates at least one goal after onboarding | Usability test + beta funnel |
| Gentle reminders improve routine consistency | Week-1 check-in/completion rate improves without high opt-out | Controlled reminder experiment after baseline |
| Progress views create perceived value | Users return to progress view and report usefulness | Interviews + event metrics |
| Consent-based minimal memory increases trust | Users inspect/approve memory and report clarity | Memory-control usability test |
| Wellness-only boundaries reduce unsafe interpretation | Low diagnosis/overconfidence rate in safety evaluation | Red-team prompts + sampled review |

Targets are **TBD / Pending Decision** until baseline traffic and beta cohort are known.

## 6. MVP experience

### 6.1 Guest/basic experience

- Public landing page explains wellness-only scope and privacy summary.
- Limited demo uses sample or minimal non-sensitive context.
- Demo has rate limits, session expiry and no private persistent memory.
- User can see a bounded example plan/guidance and then register.

### 6.2 Account-based experience

- Secure registration, verification, sign-in, recovery and session management.
- Onboarding captures name, age, goals, relevant lifestyle context, routine preferences and consent choices.
- User can skip optional questions and revise settings later.
- Personalized guidance uses only allowed, consented context.

### 6.3 Ongoing experience

- Daily plan and optional check-in.
- Habit/routine completion, skip, snooze, pause and resume.
- Progress/trend view across understandable time ranges.
- AI chat for in-scope wellness planning, reflection and general education.
- Candidate memory shown for confirmation before saving.

## 7. Feature discovery and prioritization

### Must have — MVP

- Guest landing/demo.
- Account registration, verification, sign-in, recovery and deletion request.
- Onboarding: name, age, goals, basic lifestyle context, timezone and reminder preferences.
- Habit/routine creation and simple recurrence.
- In-app reminders with quiet hours, pause/snooze and opt-out.
- Check-ins and progress tracking.
- AI wellness chat with scope/safety handling.
- Minimal consent-based memory with inspect/edit/delete/revoke.
- Privacy/security controls, auditability, abuse limits and support contact.

### Should have — controlled beta or early post-MVP

- Additional reminder channels after separate consent and provider review.
- More flexible habit templates.
- Better progress insights with transparent explanations.
- Data export improvements and user-facing activity history.
- Accessibility polish and localization beyond the launch locale.

### Not MVP

- Mobile apps, wearables, voice-first interaction or robotics।
- Clinical integrations, clinician portal or medical records।
- Medication prescribing, dosage management or treatment plans।
- Social/community features or employer surveillance।
- Autonomous external actions or broad Life OS workflows।
- Proprietary foundation model claims or private-data model training without separate consent.

## 8. Health and safety discovery boundary

NexusAI V1 must remain a general wellness companion. The product may support habit planning, routine design, reflection, general health education and progress observation. It must not diagnose, prescribe, triage, claim clinical certainty or present itself as emergency care.

High-risk categories requiring reviewed handling include:

- emergency symptoms;
- self-harm or suicide risk;
- medication and dosage changes;
- severe or rapidly worsening symptoms;
- eating-disorder-related requests;
- pregnancy or other contexts where generic advice may be unsafe;
- requests to replace a licensed professional.

The exact escalation copy, local emergency guidance and safety policy owner are **TBD / Pending Decision**.

## 9. Memory discovery

### MVP: Minimal Memory

With explicit user consent, the product may remember:

- name;
- age;
- wellness goals;
- preferences;
- relevant daily habits;
- previous plans;
- progress/check-in information।

Memory rules:

- off by default unless the user opts in;
- candidate memories require confirmation;
- each item has a purpose, source and lifecycle status;
- user can inspect, edit, delete, clear all or revoke future memory;
- chat remains usable when memory is disabled;
- no hidden inference or unbounded conversation recall.

### Future evolution

Architecture should permit a staged path:

1. **Minimal Memory (MVP):** small set of consented wellness context.
2. **Smart Personal Memory:** richer, user-approved patterns and preferences with stronger explanations.
3. **Full Life Memory:** broader cross-domain personal context, only after separate product, privacy, security and safety approvals.

Future levels are not MVP requirements and must not be backfilled into current data collection.

## 10. Trust and privacy discovery

Users should understand:

- what data is collected and why;
- which data is optional;
- whether AI memory is on or off;
- what an AI provider receives for a specific request;
- how to correct, export or delete data;
- how reminders and notifications can be paused or disabled.

The following are **TBD / Pending Decision** and must not be guessed in implementation:

- launch geography;
- minimum age and age assurance;
- applicable privacy/regulatory jurisdiction;
- retention periods for chat, check-ins, memory, audit logs and backups;
- AI provider retention/training policy and regional processing;
- authentication/MFA baseline;
- admin/support role matrix and exceptional access process.

## 11. Business and operating assumptions

The initial product is assumed to be an individual-user web experience. Organization/household accounts, pricing, billing, support staffing and monetization are **TBD / Pending Decision** unless separately approved.

Professional recommendation (not a confirmed requirement): begin with a controlled beta, small cohort, explicit support channel, conservative AI quotas and feature flags for safety-affecting changes.

## 12. Validation plan before implementation

1. Test guest demo comprehension and wellness disclaimer comprehension.
2. Test onboarding length, optional-field clarity and goal activation.
3. Test reminder controls, quiet hours and non-judgmental language.
4. Test progress interpretation for false medical inference.
5. Test memory approval, inspection, edit, revoke and deletion comprehension.
6. Build a safety evaluation set for diagnosis-like, emergency and other high-risk prompts.
7. Validate provider privacy terms, retention and data-processing assumptions.
8. Define beta SLO, support, incident and recovery expectations.

## 13. Discovery decisions ledger

| Decision | Current state | Evidence/source | Next gate |
| --- | --- | --- | --- |
| Product direction | **Confirmed canonical:** Health & Wellness Companion | Current project brief + `00-project-overview.md` | PRD/architecture consistency |
| Platform | **Confirmed:** Web-first | Current project brief | UI/UX + deployment planning |
| MVP memory | **Confirmed:** Minimal Memory, consent-based | Current project brief | Memory architecture/privacy |
| AI implementation | **Recommendation:** provider/model abstraction; proprietary model future | Current project brief | Tech stack/provider review |
| Clinical scope | **Confirmed boundary:** non-diagnostic wellness only | Current project brief + PRD | Safety review |
| Launch geography | **TBD / Pending Decision** | Not provided | Legal/privacy gate |
| Minimum age | **TBD / Pending Decision** | Not provided | Legal/privacy gate |
| Privacy jurisdiction | **TBD / Pending Decision** | Not provided | Legal/privacy gate |
| Provider retention/training | **TBD / Pending Decision** | Not provided | AI/provider review |
| Auth/MFA | **TBD / Pending Decision** | Not provided | Authentication design |
| Admin/support roles | **TBD / Pending Decision** | Not provided | Security design |
| Safety owner | **TBD / Pending Decision** | Not provided | Safety governance |
| RTO/RPO | **TBD / Pending Decision** | Not provided | Deployment/recovery design |
| Beta scale | **TBD / Pending Decision** | Not provided | Capacity/cost planning |
| Cost budget | **TBD / Pending Decision** | Not provided | Tech stack/operations |

## 14. Source-of-truth and phase gate

This Product Discovery document is canonical for product rationale, user/problem framing and MVP discovery assumptions. The PRD is canonical for testable product requirements; the System Architecture is canonical for logical system boundaries; the Architecture Review is canonical for review findings and gates.

Current phase status: Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

The following restrictions preserve the original discovery-stage gate. Subsequent Phase 04–12 approvals and the narrowly scoped Phase 13 authorization above supersede these old prerequisites; they do not resolve any TBD decision or authorize Part 2.

Until Phase 05 is explicitly approved and the next phase is separately authorized:

- do not create SQL, DDL, migrations, database connections, or ORM implementation;
- do not write backend/frontend/AI/UI application code or API implementation;
- do not integrate an AI provider or create production infrastructure;
- do not treat pre-existing later-phase artifacts as authorization to advance.
