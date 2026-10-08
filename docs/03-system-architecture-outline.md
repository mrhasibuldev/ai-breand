# NexusAI — Personal AI Health & Wellness Companion MVP System Architecture Outline

**Working title:** Nexus AI  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Document type:** System Architecture Outline  
**Phase:** System Architecture stage (repository sequence: 03)  
**Status:** Canonical approved baseline; Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. Unresolved decisions remain `TBD / Pending Decision`.  
**Date:** 2026-09-07  
**Predecessor:** [Phase 1 PRD](02-prd-nexus-ai-health-companion-mvp.md)  
**Scope rule:** This is a technology-neutral, implementation-level outline. It contains no application code, SQL, ORM definitions, database schema, API contract, or deployment configuration.

## 1. Purpose and architecture outcomes

এই নথির উদ্দেশ্য হলো PRD-তে অনুমোদিত Health Companion MVP-এর জন্য একটি নিরাপদ, privacy-first এবং পরিবর্তনযোগ্য system shape নির্ধারণ করা। এটি পরের ফেজগুলোর জন্য boundary ও dependency স্পষ্ট করবে।

Architecture should enable:

- Guest demo with strict isolation and rate limits.
- Secure registration, onboarding, consent, and session management.
- Wellness goals, routines, reminders, check-ins, and progress views.
- AI chat with safety controls and explicit memory consent.
- User-controlled memory inspection, edit, deletion, and revocation.
- Auditability without exposing sensitive content unnecessarily.
- Asynchronous work for AI calls, notifications, exports, and deletion jobs.
- Provider replacement (AI, email, notifications) without rewriting product logic.

## 2. Scope and non-goals

### In scope

- Responsive web client.
- Public/guest experience and authenticated user workspace.
- Application/API boundary, domain services, background processing, and external provider boundaries.
- Security zones, trust boundaries, data classification, high-level data flows, resilience, and observability.
- Architecture decisions that must be confirmed before database/API design.

### Out of scope for this phase

- Concrete framework, cloud vendor, model, queue, or database selection.
- Physical database schema, table/collection design, migrations, indexes, or SQL.
- Endpoint paths, request/response JSON, SDK code, prompts, or infrastructure-as-code.
- Production sizing, cost commitments, or regulatory/legal sign-off.

## 3. Architecture principles

1. **Wellness boundary first:** The system must enforce non-diagnostic product scope at both UX and server/AI policy layers.
2. **Consent is a gate:** Personalization and memory retrieval/write paths must check current consent, not just a historical flag.
3. **Least privilege:** User, support, admin, worker, and provider credentials have separate scopes.
4. **Private by default:** Sensitive content is minimized in logs, analytics, notifications, prompts, and support tooling.
5. **Single source of policy:** Safety, consent, retention, and deletion rules are versioned and centrally evaluated.
6. **Asynchronous by design:** Slow, retryable, or bulk work must not block interactive requests.
7. **Provider isolation:** AI and notification vendors are replaceable adapters behind controlled interfaces.
8. **Observable without surveillance:** Measure reliability and safety using minimized, access-controlled telemetry.
9. **Reversible decisions:** Keep domain boundaries modular so V1 can evolve to a broader personal companion without exposing a user to unsafe coupling.

## 4. System context

The following context diagram shows the actors and systems that interact with Nexus AI. The dashed boundary is the MVP product boundary; external providers are not trusted with more data than a specific operation requires.

```mermaid
flowchart LR
    Guest[Guest visitor]
    User[Registered user]
    Admin[Support / admin operator]
    Browser[Responsive web browser]

    subgraph Nexus["Nexus AI MVP boundary"]
        Web[Web client]
        Core[Application/API layer]
        Safety[Safety + consent policy]
        Jobs[Background jobs]
    end

    AI[AI model provider]
    Notify[Email / push provider]
    Identity[Optional identity provider]
    Monitor[Monitoring / alerting]

    Guest --> Browser
    User --> Browser
    Admin --> Browser
    Browser --> Web
    Web --> Core
    Core --> Safety
    Core --> Jobs
    Core --> AI
    Jobs --> Notify
    Core -. optional .-> Identity
    Core --> Monitor
    Jobs --> Monitor
```

### Context assumptions

- The browser is an untrusted client; all authorization decisions are server-side.
- AI, notification, and identity providers are external trust boundaries.
- No wearable, location, camera, microphone, or passive sensor is required for V1.
- Admin/support access is exceptional and auditable; private chat/memory is not visible by default.

## 5. Logical container architecture

This is a logical decomposition, not a promise to deploy each box as a separate microservice. For the MVP, several containers may be packaged together while retaining these security and ownership boundaries.

```mermaid
flowchart TB
    subgraph Client["Client zone"]
        WebApp[Responsive web app]
    end

    subgraph Edge["Edge / ingress zone"]
        CDN[Static delivery / CDN]
        WAF[WAF + abuse throttling]
        Gateway[API gateway / request correlation]
    end

    subgraph App["Application trust zone"]
        Auth[Auth + session boundary]
        Profile[Profile + onboarding]
        Wellness[Goals + routines + check-ins]
        Progress[Progress + insight read model]
        Reminder[Reminder orchestration]
        Chat[Chat orchestration]
        Memory[Memory control]
        Policy[Safety, consent + retention policy]
        Privacy[Export + deletion coordinator]
        Audit[Audit event writer]
    end

    subgraph Async["Asynchronous execution zone"]
        Queue[Durable job queue]
        Worker[Worker pool]
    end

    subgraph Data["Protected data zone"]
        Primary[(Encrypted application data store)]
        SecureStore[(Encrypted object / export store)]
        Cache[(Ephemeral cache + rate limits)]
        AuditStore[(Append-only audit store)]
    end

    subgraph External["External provider boundaries"]
        Model[AI provider adapter]
        Messaging[Notification provider adapter]
        AuthId[Optional identity provider]
    end

    WebApp --> CDN
    WebApp --> WAF
    WAF --> Gateway
    Gateway --> Auth
    Gateway --> Profile
    Gateway --> Wellness
    Gateway --> Progress
    Gateway --> Reminder
    Gateway --> Chat
    Gateway --> Memory
    Gateway --> Privacy

    Auth --> AuthId
    Auth --> Primary
    Profile --> Policy
    Profile --> Primary
    Wellness --> Policy
    Wellness --> Primary
    Progress --> Primary
    Reminder --> Policy
    Reminder --> Queue
    Chat --> Policy
    Chat --> Memory
    Chat --> Model
    Chat --> Primary
    Memory --> Policy
    Memory --> Primary
    Privacy --> Queue
    Privacy --> SecureStore
    Privacy --> Primary
    Policy --> Primary

    Auth -. audit .-> Audit
    Profile -. audit .-> Audit
    Wellness -. audit .-> Audit
    Chat -. audit .-> Audit
    Memory -. audit .-> Audit
    Privacy -. audit .-> Audit
    Audit --> AuditStore

    Queue --> Worker
    Worker --> Reminder
    Worker --> Privacy
    Worker --> Messaging
    Worker --> Model
    Worker --> Primary
    Worker --> Audit
    Gateway --> Cache
    Worker --> Cache
```

## 6. Container responsibilities and boundaries

| Container | Owns | Must not own / do |
| --- | --- | --- |
| Web app | Presentation, client-side validation hints, accessibility, safe copy | Authorization, secrets, final validation, direct provider calls |
| WAF/gateway | TLS termination, request limits, correlation IDs, coarse abuse controls | Business authorization or sensitive content logging |
| Auth/session | Registration, verification, sign-in, recovery, session lifecycle, MFA hook | Wellness interpretation or memory decisions |
| Profile/onboarding | Basic profile, goals, preferences, consent capture | Implicitly enabling memory without current consent |
| Wellness | Goals, routines, check-ins, reminder intent | Diagnosis, clinical claims, provider credentials |
| Progress | Aggregations and user-facing trends | New sensitive facts not originating in approved domain events |
| Reminder | Schedule intent, quiet hours, delivery preferences | Sending sensitive content by default or bypassing opt-out |
| Chat orchestration | Context assembly, prompt policy, model adapter call, response labeling | Direct persistence of candidate memories without approval |
| Memory control | Candidate memory, confirmation, retrieval eligibility, edit/delete/revoke | Unbounded conversation recall or hidden profile inference |
| Safety/consent policy | Scope checks, high-risk routing, consent/retention decisions | Storing full chat or becoming an unreviewed clinical engine |
| Privacy coordinator | Export, deletion, revocation workflows and status | Ad-hoc destructive deletion without audit and retry handling |
| Audit writer | Structured security/privacy/admin events | Sensitive raw payloads or mutable event history |
| Worker/queue | Retryable AI, notification, export, deletion work | Unbounded retries, bypassing policy or authorization |

## 7. Trust boundaries and data classification

### 7.1 Trust boundaries

```mermaid
flowchart LR
    U[Untrusted browser] -->|TLS + session token| E[Edge boundary]
    E -->|validated request| A[Application boundary]
    A -->|least-privilege service identity| D[Protected data boundary]
    A -->|minimized, policy-approved context| P[External provider boundary]
    W[Worker identity] -->|scoped jobs only| D
    S[Support/admin identity] -->|justified, audited access| A
    P -. never receives .-> H[Unapproved raw health content]
```

### 7.2 Data classes (conceptual; no schema implied)

| Class | Examples | Required handling |
| --- | --- | --- |
| Restricted health/wellness content | Check-in text, chat content, memory items, goal context | Strong encryption, narrow access, minimized prompt/log exposure, explicit retention/deletion |
| Personal account data | Email, timezone, preferences, consent records | Encryption, access control, export/delete support |
| Operational data | Job status, delivery status, feature flags, quotas | Integrity, retries, limited retention |
| Security/audit data | Login events, consent changes, admin access, deletion events | Append-only/tamper evidence, controlled access, retention policy |
| Aggregate telemetry | Counts, latency, error categories, safety evaluation outcomes | De-identify/minimize; never use raw content by default |

### 7.3 Prompt/data minimization rule

Before any AI call, the chat orchestrator asks the policy layer for an allowed context bundle. The bundle may include only the current user message, necessary active routine/progress context, and consented memory. The provider adapter must strip identifiers and disallowed fields where practical, and must return provider-retention status for operational review.

## 8. Key runtime flows

### 8.1 Guest demo to registration

```mermaid
sequenceDiagram
    autonumber
    actor G as Guest
    participant B as Browser
    participant E as Edge/API
    participant D as Guest demo boundary
    participant A as Auth
    participant P as Profile

    G->>B: Open public site
    B->>E: Request demo session
    E->>D: Create rate-limited, non-persistent session
    D-->>B: Return demo capability
    G->>B: Try sample wellness flow
    B->>E: Submit constrained demo input
    E->>D: Validate and process without private memory
    D-->>B: Return bounded example guidance
    G->>B: Choose Create account
    B->>A: Submit registration
    A-->>B: Verification required
    G->>B: Verify account and accept policies
    B->>P: Start onboarding
```

### 8.2 Onboarding, consent, and first plan

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant B as Browser
    participant API as Application/API
    participant C as Consent + safety policy
    participant P as Profile/wellness domain
    participant Q as Job queue
    participant W as Worker

    U->>B: Select goals and routine preferences
    B->>API: Submit onboarding data
    API->>C: Validate scope and consent choices
    C-->>API: Allow/deny decisions + policy version
    API->>P: Persist approved profile/preferences
    P->>Q: Enqueue starter-plan job
    Q->>W: Deliver job
    W->>C: Check current consent and safety policy
    W->>P: Create bounded starter plan
    P-->>B: Show plan when ready
```

### 8.3 Chat with consented memory

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant B as Browser
    participant API as Chat API
    participant C as Safety + consent policy
    participant M as Memory control
    participant W as Wellness/progress context
    participant L as AI provider adapter
    participant A as Audit

    U->>B: Ask wellness question
    B->>API: Send message with active session
    API->>C: Classify scope and risk
    alt High-risk or out-of-scope
        C-->>API: Safe redirect response policy
        API-->>B: Wellness disclaimer + professional help guidance
    else In-scope
        API->>M: Request eligible memories
        M->>C: Verify current memory consent
        C-->>M: Allowed memory set or empty
        API->>W: Request minimal routine/progress context
        API->>L: Send minimized, policy-approved context
        L-->>API: AI response + provider metadata
        API-->>B: Labelled response + feedback control
        API->>A: Record metadata-only audit event
    end
    opt Candidate memory detected
        API-->>B: Ask user to approve memory
        U->>B: Approve/edit/reject
        B->>M: Persist only approved result
        M->>A: Record consented memory change
    end
```

### 8.4 Check-in, progress, and reminder

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant B as Browser
    participant API as Wellness API
    participant P as Wellness/progress domain
    participant R as Reminder orchestrator
    participant Q as Queue
    participant N as Notification adapter

    U->>B: Mark routine complete/skip/snooze
    B->>API: Submit check-in event
    API->>P: Validate ownership and write event
    P-->>B: Updated progress view
    P->>R: Recalculate next reminder intent
    R->>Q: Enqueue delivery if allowed
    Q->>N: Send non-sensitive reminder
    N-->>R: Delivery status
```

### 8.5 Account deletion and memory revocation

```mermaid
sequenceDiagram
    autonumber
    actor U as User
    participant B as Browser
    participant API as Privacy coordinator
    participant C as Consent + retention policy
    participant Q as Job queue
    participant W as Deletion worker
    participant A as Audit store

    U->>B: Request memory clear or account deletion
    B->>API: Confirm destructive action
    API->>C: Resolve scope, retention exceptions, and policy version
    C-->>API: Approved deletion plan
    API->>Q: Enqueue idempotent deletion/export job
    API-->>B: Show pending/completed status
    Q->>W: Execute scoped deletion
    W->>W: Remove or anonymize data in each approved store
    W->>A: Record completion/failure metadata
    W-->>API: Return status for user-facing confirmation
```

## 9. Cross-cutting architecture concerns

### Identity and authorization

- Treat browser sessions as untrusted input; validate session, tenant/user ownership, and role on every protected operation.
- Separate end-user, support, admin, worker, and provider identities.
- Use short-lived access credentials, secure refresh/session rotation, revocation, and rate limits.
- Keep authorization policy independent of UI visibility.

### Safety enforcement

- Apply deterministic scope/risk checks before and after model calls.
- Keep system safety policy/version separate from user-editable content.
- Store only the metadata needed to evaluate and audit safety behavior.
- Maintain a reviewed evaluation set for diagnosis-like, emergency, medication, self-harm, eating-disorder, and other high-risk prompts.

### Consent and memory

- Consent is granular: product policies, personalization, reminders, optional channels, and AI memory are separate decisions.
- Memory retrieval and memory writes both require current consent and purpose compatibility.
- A revoked consent must invalidate future retrieval and enqueue cleanup of derived copies according to the approved retention policy.

### Reliability and idempotency

- Interactive flows should degrade gracefully when AI or notification providers are unavailable.
- Queue jobs need idempotency keys, bounded retries, dead-letter handling, and operator visibility.
- Deletion/export jobs must be resumable and safe to retry.
- Avoid making a successful check-in depend on a successful AI response.

### Observability

- Emit correlation IDs, latency, status, dependency outcome, policy version, and coarse error category.
- Redact health content, chat text, memory text, tokens, and secrets from logs by default.
- Alert on authentication abuse, authorization failures, unsafe-response evaluations, provider outages, queue growth, deletion failures, and unusual data access.
- Keep operational telemetry logically separate from restricted user content.

## 10. High-level deployment topology (technology-neutral)

```mermaid
flowchart TB
    User[User browser] --> Edge[CDN / WAF / TLS]
    Edge --> Web[Web delivery]
    Edge --> API[Stateless application/API runtime]
    API --> Store[(Encrypted primary data service)]
    API --> Cache[(Ephemeral cache / limits)]
    API --> Queue[Managed durable queue]
    Queue --> Worker[Isolated worker runtime]
    Worker --> Store
    Worker --> Providers[Provider adapters]
    API --> Providers
    API --> Audit[(Append-only audit service)]
    Worker --> Audit
    Store --> Backup[Encrypted backup service]
    Audit --> Backup
    API --> Obs[Metrics / traces / redacted logs]
    Worker --> Obs
```

Deployment requirements to validate later:

- Separate environments (local/development, staging, production) with isolated credentials and data.
- No production secrets in client bundles, source control, or logs.
- Private network path and restricted egress for protected data services where supported.
- Independent backup access, restore testing, and documented recovery objectives.
- Controlled release and rollback path for web, API, workers, prompts, and policy versions.

## 11. Failure modes and graceful degradation

| Failure | User-visible behavior | Required protection |
| --- | --- | --- |
| AI provider timeout/outage | Explain temporary unavailability; preserve check-in/routine functions | Timeout, bounded retry, circuit breaker, no duplicate charge/request |
| Notification provider outage | Show in-app reminder status; retry later | Queue durability, idempotent delivery, opt-out honored |
| Queue backlog | Show pending status, never claim work completed | Backpressure, age alert, dead-letter review |
| Cache loss | Recompute or reject safely; never treat cache as source of truth | Short TTL, fail-closed rate-limit fallback where needed |
| Audit write failure | Block security-sensitive mutations or use protected fallback | Audit integrity policy, operator alert |
| Data-store partial failure | Read-only or limited mode; preserve user clarity | Transactions/consistency plan deferred to database phase |
| Policy service unavailable | Fail closed for memory writes and high-risk AI calls | Versioned local safe defaults |
| Account deletion job failure | Clearly show pending/failed status and support path | Idempotent retries, reconciliation report, audit trail |

## 12. Architecture decisions deferred to later phases

The following must not be silently decided in this outline:

1. Runtime/framework and programming language.
2. Hosting/cloud region and residency model.
3. Relational/document/search data-store choice and physical schema.
4. Queue, cache, object storage, and observability products.
5. Authentication provider, MFA/passkey strategy, and session library.
6. AI model/provider, prompt versioning, provider retention, and regional processing.
7. Notification channel/provider and message templates.
8. Exact API resources and event contracts.
9. Retention periods, deletion semantics for backups, and legal holds.
10. Availability, latency, RTO/RPO, beta scale, and cost budgets.

These choices belong in the Database Design, API Design, Authentication Flow, Tech Stack, Deployment, and Security phases.

## 13. Phase 2 review checklist

- [ ] PRD scope, non-goals, and user journey are accurately reflected.
- [ ] Guest data cannot enter authenticated private memory by accident.
- [ ] All sensitive data paths cross a policy/consent boundary.
- [ ] AI provider receives only minimized, policy-approved context.
- [ ] Memory retrieval, write, edit, revoke, and delete paths are represented.
- [ ] Admin/support access is least-privilege and auditable.
- [ ] Async jobs, retries, idempotency, and failure behavior are represented.
- [ ] Logging/monitoring avoids raw health content by default.
- [ ] Deployment topology is conceptual and contains no implementation commitment.
- [ ] No code or database schema has been created in this phase.

## 14. Architecture stage gate

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

This section preserves the original architecture review gate and its prerequisites, including the original stage numbering. Current status is recorded in the header: Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. The historical instructions below do not reopen approved gates or resolve existing TBD decisions.

This architecture outline is ready for review, not yet approved for implementation.

Before the Database Design stage begins, approval must confirm:

- the logical container boundaries;
- the trust boundaries and data classifications;
- the consent/memory and safety enforcement points;
- the synchronous versus asynchronous flow split;
- the failure/degradation expectations;
- which deferred decisions must be resolved in Phase 3 versus later.

**Approval states:** `Approved` · `Approved with changes` · `Not approved`  
**Implementation rule:** No code or database schema work starts until this Phase 2 gate is approved.
