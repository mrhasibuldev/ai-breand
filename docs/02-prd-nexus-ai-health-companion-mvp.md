# NexusAI — Personal AI Health & Wellness Companion MVP PRD

**Working title:** Nexus AI  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Document type:** Product Requirements Document (PRD)  
**Phase:** PRD stage (repository sequence: 02)  
**Status:** Canonical approved baseline; Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. Unresolved decisions remain `TBD / Pending Decision`.  
**Date:** 2026-08-28  
**Scope rule:** This document defines product requirements only. No application code, database schema, API contract, infrastructure configuration, or deployment work is approved by this document.

## 1. Decision vocabulary

- **CONFIRMED:** Explicitly stated in the project brief.
- **RECOMMENDATION:** A product recommendation for approval; it is not yet binding.
- **ASSUMPTION:** A working hypothesis that must be validated during discovery or testing.
- **TBD:** Not yet decided.
- **DECISION REQUIRED:** A choice that must be approved before the affected phase proceeds.

## 2. Product vision

Nexus AI will become a personal AI companion that learns gradually and transparently—with the user’s permission—remembers only useful preferences, supports everyday life, and earns trust over time.

**Version 1 is intentionally narrower:** a web-based health and wellness companion that helps people build healthy habits, follow routines, remember wellness tasks, and understand their progress. It is not a doctor, diagnostic service, emergency service, or substitute for professional medical care.

## 3. Problem statement

People often want to improve sleep, movement, hydration, mindfulness, nutrition routines, or medication-related reminders, but struggle to turn intentions into consistent daily behavior. Existing tools can be fragmented, generic, difficult to personalize, or unclear about what an AI system remembers. Users need a gentle, privacy-conscious companion that turns a small amount of consented context into practical guidance without making medical claims.

## 4. Goals and non-goals

### 4.1 MVP goals

1. Let a guest safely experience a limited wellness flow before registration.
2. Let a registered user complete onboarding and define wellness goals, routine preferences, and reminder preferences.
3. Provide personalized, non-diagnostic wellness guidance based on user-provided information and recorded progress.
4. Let users track selected habits and view understandable progress over time.
5. Provide an AI chat experience for wellness questions, planning, reflection, and encouragement.
6. Make memory explicit: users opt in, can inspect what is remembered, can edit or delete it, and can revoke permission.
7. Build security and privacy requirements into the MVP from the start.

### 4.2 Explicit non-goals for V1

- Medical diagnosis, treatment decisions, clinical triage, or disease prediction.
- Emergency response, crisis intervention, or replacement for a clinician.
- Medication prescribing, dosage changes, or clinical adherence claims.
- Continuous passive sensing from wearables, cameras, microphones, or location.
- Open-ended autonomous actions in external systems.
- Social/community features, clinician portals, insurance workflows, or employer surveillance.
- Native mobile apps; V1 is responsive web only.
- Training foundation models on private user data.

## 5. Target users and personas

### Primary persona — Wellness Builder

An adult who wants help building one to three everyday habits, such as consistent sleep, water intake, walking, stretching, mindfulness, or meal planning. They value low friction, encouragement, and control over personal data.

### Secondary persona — Routine Manager

An adult who benefits from structured reminders and check-ins, but does not want a complex clinical tracker. They may have changing schedules and need to pause, snooze, or adjust routines.

### Guest visitor

A person evaluating the product before creating an account. They can try a constrained demo and should not be asked to enter sensitive health details before registration.

### Internal admin/support role

An authorized operator who handles account/support and aggregate product health. Admin access must be least-privilege and auditable; admins do not receive unrestricted access to private chat or memory content by default.

## 6. Product principles

1. **Wellness, not diagnosis:** Use plain-language wellness framing and clear boundaries.
2. **Consent before memory:** No personal memory is saved for personalization unless the user explicitly opts in.
3. **Data minimization:** Collect only what is needed for the requested feature.
4. **User control:** Show, edit, export, delete, and revoke controls in understandable language.
5. **Explainable personalization:** Let users see why a recommendation or reminder was suggested.
6. **Safe uncertainty:** When a request may require medical judgment, acknowledge limits and recommend an appropriate professional resource.
7. **Gentle, non-judgmental experience:** Avoid shame, streak pressure, or manipulative engagement.
8. **Secure by default:** Strong authentication, encrypted storage/transit, role-based access, validation, auditability, and recoverability are product requirements.

## 7. User journeys

### 7.1 Guest journey

1. Visitor lands on the public website.
2. Visitor reads the wellness-only scope and privacy summary.
3. Visitor may try a limited demo using non-sensitive sample data or a minimal wellness intention.
4. Demo shows one example plan/check-in and a clear upgrade path.
5. Visitor chooses to create an account.

**Guest restrictions (recommendation):** no persistent health profile, no private AI memory, no sensitive free-text storage, limited messages per session, and no reminders until registration.

### 7.2 Registration and onboarding journey

1. User registers with email/password or an approved secure identity provider (TBD).
2. User verifies the account and accepts Terms of Service and Privacy Policy.
3. User sees a safety notice: Nexus AI is not a medical professional or emergency service.
4. User selects wellness areas and one to three initial goals.
5. User sets preferred check-in cadence, timezone, quiet hours, and reminder channels.
6. User reviews optional data categories and separately chooses whether AI may remember selected preferences.
7. User completes onboarding and receives a starter plan.

### 7.3 Daily use journey

1. User sees today’s plan and optional check-in.
2. User marks habits/tasks complete, skipped, or snoozed and may add a short reflection.
3. AI offers encouragement, a small next step, or a plan adjustment.
4. User can open chat for wellness planning or questions.
5. Any candidate memory is shown for confirmation before it is saved.

### 7.4 Progress journey

1. User opens progress view.
2. User sees trends for selected habits across week/month ranges.
3. User can inspect the underlying check-ins and correct or delete entries.
4. Insights are framed as observations, not medical conclusions.

### 7.5 Memory-control journey

1. User opens “What Nexus remembers.”
2. User sees each remembered item, its purpose, source/date, and status.
3. User can approve, edit, delete, or disable future memory.
4. Revoking memory permission stops new saves and triggers deletion/anonymization behavior defined in the Privacy Policy.

## 8. MVP feature requirements

### 8.1 Public website and guest demo

- Explain the product, wellness-only boundary, privacy posture, and account value.
- Provide a limited, rate-limited demo with sample/non-sensitive context.
- Never imply diagnosis, guaranteed outcomes, or emergency support.
- Provide clear registration and sign-in entry points.

### 8.2 Account and profile

- Register, sign in, sign out, verify email, reset password, and manage sessions.
- View and edit basic profile, timezone, locale, and notification preferences.
- Deactivate/delete account through a clear user flow.
- Record consent versions and timestamps.

### 8.3 Onboarding

- Capture selected wellness areas and goals.
- Capture routine constraints, preferred schedule, quiet hours, and reminder preferences.
- Explain optional fields and why they help.
- Support skip/later for non-essential questions.
- Provide a review screen before activating personalization.

### 8.4 Habits, routines, and reminders

- Create, edit, pause, resume, complete, skip, and snooze a habit/task.
- Support simple recurrence (daily, selected weekdays, or custom interval—final choice TBD).
- Allow reminder time and quiet-hour configuration.
- Show reminder delivery status and provide unsubscribe/disable controls.
- Avoid medical or medication-specific workflows in V1 unless separately approved after safety review.

### 8.5 Check-ins and progress

- Support quick check-ins with structured status plus optional free text.
- Show weekly and monthly completion/trend views for user-selected items.
- Allow correction and deletion of entries.
- Use neutral labels such as “completed,” “skipped,” and “not recorded”; do not create harmful competitive rankings.

### 8.6 AI wellness chat

- Support questions about habit planning, routines, reflections, and general wellness education.
- Ground responses in the user’s consented profile, active routines, and recorded progress only when permitted.
- Clearly separate user-provided facts, general wellness suggestions, and uncertainty.
- Refuse or safely redirect diagnosis, urgent symptoms, dosage changes, self-harm, or other high-risk requests.
- Include a visible “report response” or feedback control.
- Make it clear when a response is AI-generated.

### 8.7 Consent-based memory

- Memory is off by default unless the user opts in during onboarding or settings.
- Candidate memories require user confirmation before persistence.
- Each memory item must have a category, purpose, timestamp, source, and lifecycle status.
- Users can view, edit, delete individual items, clear all items, or disable memory.
- Chat should function when memory is disabled, using only the current conversation and explicitly available session context.

### 8.8 Notifications

- In-app reminders are required; email/push/SMS are **TBD** and must be separately consented.
- Respect timezone, quiet hours, frequency limits, and opt-out.
- Do not include sensitive health content in notification previews by default.

### 8.9 Admin and support (minimum)

- Role-based access for support/admin functions.
- View account status, consent status, usage/abuse signals, and audit events needed for support.
- No default access to full chat transcripts or memory content.
- Any exceptional access must have a documented reason and audit event.

## 9. Safety and content requirements

- Persistent UI copy must state: “Nexus AI provides general wellness support, not medical diagnosis or treatment.”
- If a user reports potentially urgent symptoms, the assistant must advise contacting local emergency services or an appropriate licensed professional, according to a reviewed safety policy.
- The assistant must not claim certainty, clinical authority, or that it has contacted help.
- Sensitive-topic handling (self-harm, eating disorders, abuse, medication, pregnancy, severe symptoms) requires tested safety responses and escalation guidance before launch.
- Product, prompt, and policy changes affecting safety require review and versioning.

## 10. Privacy and security product requirements

- Encrypt data in transit and at rest; secrets must not be stored in source control.
- Use secure authentication, session management, password reset, rate limiting, and input validation.
- Enforce tenant/user isolation and role-based access on every protected operation.
- Maintain tamper-evident audit logs for authentication, consent, memory changes, data export/deletion, admin access, and security events.
- Provide backup and restore capability with documented retention and access controls.
- Minimize sensitive data in logs, analytics, support tooling, and notifications.
- Define retention/deletion behavior for profile data, chat, check-ins, reminders, memory, backups, and derived analytics.
- Do not use private user content to train models without separate, explicit consent.
- Provide export and account deletion pathways subject to legally required retention.

## 11. MVP success metrics

Metrics are recommendations and require approval of targets after baseline testing.

### Activation

- Guest-to-registration conversion.
- Registration-to-onboarding completion.
- Time from registration to first activated goal.

### Engagement and value

- Percentage of activated users completing at least one check-in in week 1.
- Weekly active users and retained users at weeks 2 and 4.
- Habit/task completion rate, with skipped/snoozed rates shown separately.
- Percentage of users who report that guidance was helpful.
- Chat safety feedback and response-report rate.

### Trust and control

- Memory opt-in rate and percentage of candidate memories explicitly approved.
- Memory deletion/revocation completion success.
- Account deletion/export completion success.
- Security/privacy incident count and time to response.

### Guardrail metrics

- Unsafe-response rate from red-team and sampled evaluations.
- False claims of diagnosis or certainty.
- Notification opt-out and complaint rate.
- Data access-control test failures.

## 12. MVP acceptance criteria

The MVP is product-ready for a controlled beta only when:

1. A guest can complete the limited demo without an account or sensitive data collection.
2. A new user can register, consent, onboard, activate a goal, and configure reminders.
3. A user can complete/check/skip a routine and see a truthful progress view.
4. A user can chat about in-scope wellness topics and receives safe redirection for out-of-scope medical/urgent requests.
5. Memory is opt-in, reviewable, editable, deletable, and disabled when revoked.
6. Protected data is isolated by user/tenant and access is logged.
7. Account export and deletion flows work in a test environment and their outcomes are auditable.
8. Security, privacy, safety, backup/restore, and abuse-rate tests meet the agreed beta thresholds.
9. Terms of Service, Privacy Policy, wellness disclaimer, support contact, and incident process are available before external beta.

## 13. Risks and mitigations

| Risk | Impact | Initial mitigation | Owner/gate |
| --- | --- | --- | --- |
| Users interpret guidance as diagnosis | High | Persistent disclaimer, constrained scope, refusal/redirection tests, human-reviewed safety policy | Product + Safety review before beta |
| Sensitive data exposure | High | Data minimization, encryption, RBAC, tenant isolation, audit logs, secure deletion/export tests | Security review before implementation approval |
| AI saves unwanted memories | High | Memory off by default, explicit candidate confirmation, per-item controls, deletion audit | Product + Privacy review |
| Reminder fatigue or shame | Medium | Quiet hours, snooze/pause, neutral language, frequency caps, opt-out | UX review |
| Incorrect or overconfident AI output | High | Grounding boundaries, uncertainty language, evaluation set, report-response control | AI safety gate |
| Low retention/value | Medium | Narrow goals, fast onboarding, weekly progress feedback, interviews and beta analytics | Product discovery |
| Abuse, bots, or cost spikes | Medium | Rate limits, quotas, anomaly monitoring, guest restrictions | Engineering/security phase |
| Legal/regulatory misclassification | High | Keep V1 wellness-only, obtain qualified legal/privacy review, document data practices | Legal gate before public launch |

## 14. Open decisions required before later phases

1. **TBD / Pending Decision:** Initial launch geography and applicable privacy/regulatory jurisdictions.
2. **TBD / Pending Decision:** Minimum user age and age-verification/parental-consent policy.
3. **TBD / Pending Decision:** Whether V1 supports only individual accounts or also organizations/households.
4. **TBD / Pending Decision:** Authentication methods (email/password, social login, passkeys) and MFA requirement.
5. **TBD / Pending Decision:** Reminder channels for beta (in-app only vs email/push).
6. **TBD / Pending Decision:** Exact recurrence model and maximum number of active routines.
7. **TBD / Pending Decision:** Data retention periods for chat, check-ins, memory, logs, and backups.
8. **TBD / Pending Decision:** Approved AI provider/model and whether provider retention/training is disabled contractually.
9. **TBD / Pending Decision:** Safety escalation copy and jurisdiction-specific emergency guidance.
10. **TBD / Pending Decision:** Beta size, success thresholds, support model, and launch approval authority.

## 15. Phase gate

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

This section preserves the original PRD review gate and its prerequisites. Current status is recorded in the header: Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. The historical instructions below do not reopen approved gates or resolve existing TBD decisions.

**This PRD is complete for review, not approved for implementation.**

Before implementation and downstream design are authorized, the founder must approve:

- the health/wellness MVP scope and non-goals;
- the guest → registration → onboarding → guidance/progress/chat journey;
- consent-based memory behavior;
- security, privacy, and safety requirements;
- the open decisions that must be resolved now versus during later phases.

Approval should be recorded as one of: **Approved**, **Approved with changes**, or **Not approved**. No code is to be written until approval is recorded.
