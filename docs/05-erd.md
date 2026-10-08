# NexusAI — Phase 05 Logical ERD

**Product:** NexusAI — Personal AI Health & Wellness Companion  
**Phase:** Phase 05 — Database Design  
**Status:** Approved — Phase 05 gate passed; Phase 06 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Related design:** [05-database-design.md](05-database-design.md)  
**Scope:** Logical entity/relationship view only. This is not SQL, DDL, a migration, or an ORM model.

## 1. Reading guide

- Entity names are shown in `UPPER_SNAKE_CASE` for Mermaid compatibility; the corresponding logical names are the plural `snake_case` names used in the Data Dictionary.
- `PK` marks a primary key and `FK` marks a foreign key.
- `||` means exactly one, `o|` means zero or one, and `o{` means zero or many.
- A relationship marked optional reflects a nullable foreign key or a future-compatible association; ownership and cross-account validation still apply.
- Composite/scoped uniqueness (for example issuer + subject, account + date, conversation + sequence, and account + idempotency key) is defined in the Data Dictionary and main design rather than repeated as a single-field `UK` marker.
- Fields shown are important fields, not a physical schema commitment. Full field definitions, requiredness, defaults, constraints, and sensitivity are in [05-data-dictionary.md](05-data-dictionary.md).

## 2. Logical ERD

```mermaid
erDiagram
    ACCOUNTS {
        UUID id PK
        STRING auth_issuer
        STRING auth_subject
        STRING email_normalized UK
        ENUM status
        TIMESTAMP email_verified_at
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
        TIMESTAMP purge_after
    }

    AUTH_SESSIONS {
        UUID id PK
        UUID account_id FK
        STRING session_token_hash UK
        TIMESTAMP created_at
        TIMESTAMP expires_at
        TIMESTAMP last_seen_at
        TIMESTAMP revoked_at
        ENUM status
    }

    USER_PROFILES {
        UUID id PK
        UUID account_id FK UK
        STRING display_name
        STRING age_band
        STRING locale
        STRING timezone
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    WELLNESS_PROFILES {
        UUID id PK
        UUID account_id FK UK
        JSON wellness_areas
        ENCRYPTED_JSON consented_context
        ENUM coaching_style
        ENUM status
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    CONSENT_RECORDS {
        UUID id PK
        UUID account_id FK
        ENUM consent_type
        STRING policy_version
        ENUM decision
        TIMESTAMP captured_at
        TIMESTAMP revoked_at
        STRING capture_source
    }

    GOALS {
        UUID id PK
        UUID account_id FK
        ENUM wellness_area
        STRING title
        TEXT description
        ENUM status
        DATE start_date
        DATE end_date
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    ROUTINES {
        UUID id PK
        UUID account_id FK
        UUID goal_id FK
        STRING name
        JSON recurrence_spec
        STRING preferred_local_time
        STRING timezone
        ENUM status
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    DAILY_PLANS {
        UUID id PK
        UUID account_id FK
        DATE plan_date
        ENUM status
        ENUM plan_source
        TEXT rationale_summary
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    TASKS {
        UUID id PK
        UUID account_id FK
        UUID daily_plan_id FK
        UUID routine_id FK
        UUID goal_id FK
        STRING title
        ENUM task_type
        TIMESTAMP scheduled_for
        ENUM status
        INTEGER sort_order
        TIMESTAMP completed_at
        TIMESTAMP deleted_at
    }

    CHECK_INS {
        UUID id PK
        UUID account_id FK
        UUID task_id FK
        DATE checkin_date
        ENUM checkin_kind
        ENUM status
        ENCRYPTED_TEXT reflection
        TIMESTAMP recorded_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    CONVERSATIONS {
        UUID id PK
        UUID account_id FK
        ENUM status
        STRING title
        TIMESTAMP started_at
        TIMESTAMP ended_at
        TIMESTAMP deleted_at
    }

    MESSAGES {
        UUID id PK
        UUID conversation_id FK
        INTEGER sequence_no
        ENUM sender_role
        ENCRYPTED_TEXT content
        ENUM content_status
        TIMESTAMP created_at
        TIMESTAMP deleted_at
    }

    MEMORY_RECORDS {
        UUID id PK
        UUID account_id FK
        UUID consent_record_id FK
        UUID source_message_id FK
        ENUM category
        STRING purpose
        ENCRYPTED_JSON value
        ENUM status
        STRING content_fingerprint
        TIMESTAMP approved_at
        TIMESTAMP revoked_at
        TIMESTAMP expires_at
        TIMESTAMP deleted_at
    }

    NOTIFICATION_PREFERENCES {
        UUID id PK
        UUID account_id FK UK
        STRING timezone
        BOOLEAN in_app_enabled
        BOOLEAN email_enabled
        BOOLEAN push_enabled
        STRING quiet_hours_start
        STRING quiet_hours_end
        TIMESTAMP updated_at
    }

    REMINDERS {
        UUID id PK
        UUID account_id FK
        UUID task_id FK
        ENUM channel
        JSON schedule_spec
        TIMESTAMP next_due_at
        ENUM status
        TIMESTAMP created_at
        TIMESTAMP updated_at
        TIMESTAMP deleted_at
    }

    NOTIFICATION_DELIVERIES {
        UUID id PK
        UUID reminder_id FK
        ENUM status
        STRING provider_alias
        STRING provider_reference_hash
        TIMESTAMP attempted_at
        TIMESTAMP delivered_at
        STRING failure_category
    }

    SAFETY_EVENTS {
        UUID id PK
        UUID account_id FK
        UUID conversation_id FK
        UUID message_id FK
        ENUM risk_level
        ENUM policy_action
        STRING policy_version
        BOOLEAN escalation_shown
        STRING classifier_version
        TIMESTAMP created_at
    }

    DATA_LIFECYCLE_REQUESTS {
        UUID id PK
        UUID account_id FK
        ENUM request_type
        ENUM scope
        ENUM status
        STRING idempotency_key
        STRING artifact_reference
        TIMESTAMP requested_at
        TIMESTAMP completed_at
        TIMESTAMP artifact_expires_at
    }

    SUPPORT_ACCESS_EVENTS {
        UUID id PK
        UUID operator_account_id FK
        UUID subject_account_id FK
        ENUM access_scope
        STRING reason
        ENUM outcome
        TIMESTAMP started_at
        TIMESTAMP ended_at
        TIMESTAMP created_at
    }

    AUDIT_EVENTS {
        UUID id PK
        UUID actor_account_id FK
        UUID subject_account_id FK
        STRING event_type
        STRING entity_type
        UUID entity_id
        ENUM outcome
        STRING policy_version
        STRING correlation_id
        TIMESTAMP occurred_at
    }

    AI_USAGE_EVENTS {
        UUID id PK
        UUID account_id FK
        UUID conversation_id FK
        UUID message_id FK
        STRING provider_alias
        STRING model_class
        INTEGER input_units
        INTEGER output_units
        INTEGER latency_ms
        STRING safety_policy_version
        TIMESTAMP created_at
    }

    ACCOUNTS ||--o{ AUTH_SESSIONS : owns
    ACCOUNTS ||--|| USER_PROFILES : has
    ACCOUNTS ||--o| WELLNESS_PROFILES : has
    ACCOUNTS ||--o{ CONSENT_RECORDS : records
    ACCOUNTS ||--o{ GOALS : defines
    GOALS o|--o{ ROUTINES : guides
    ACCOUNTS ||--o{ ROUTINES : owns
    ACCOUNTS ||--o{ DAILY_PLANS : receives
    DAILY_PLANS ||--o{ TASKS : contains
    ROUTINES o|--o{ TASKS : instantiates
    GOALS o|--o{ TASKS : attributes
    ACCOUNTS ||--o{ TASKS : owns
    TASKS ||--o{ CHECK_INS : receives
    ACCOUNTS ||--o{ CHECK_INS : records
    ACCOUNTS ||--o{ CONVERSATIONS : starts
    CONVERSATIONS ||--o{ MESSAGES : contains
    ACCOUNTS ||--o{ MEMORY_RECORDS : owns
    CONSENT_RECORDS o|--o{ MEMORY_RECORDS : authorizes
    MESSAGES o|--o{ MEMORY_RECORDS : sources
    ACCOUNTS ||--|| NOTIFICATION_PREFERENCES : configures
    ACCOUNTS ||--o{ REMINDERS : schedules
    TASKS o|--o{ REMINDERS : triggers
    REMINDERS ||--o{ NOTIFICATION_DELIVERIES : produces
    ACCOUNTS ||--o{ SAFETY_EVENTS : generates
    CONVERSATIONS o|--o{ SAFETY_EVENTS : evaluates
    MESSAGES o|--o{ SAFETY_EVENTS : evaluates
    ACCOUNTS ||--o{ DATA_LIFECYCLE_REQUESTS : requests
    ACCOUNTS ||--o{ SUPPORT_ACCESS_EVENTS : operates
    ACCOUNTS ||--o{ SUPPORT_ACCESS_EVENTS : is_subject
    ACCOUNTS ||--o{ AUDIT_EVENTS : acts
    ACCOUNTS o|--o{ AUDIT_EVENTS : is_subject
    ACCOUNTS ||--o{ AI_USAGE_EVENTS : incurs
    CONVERSATIONS o|--o{ AI_USAGE_EVENTS : measures
    MESSAGES o|--o{ AI_USAGE_EVENTS : measures
```

## 3. Relationship notes

1. `ACCOUNTS` is the ownership anchor. Every user-owned record carries `account_id`, even when another foreign key also identifies its parent.
2. `USER_PROFILES` is one-to-one; `WELLNESS_PROFILES` is optional one-to-one because the user may skip optional context.
3. `GOALS` and `ROUTINES` are separate so a goal can be adjusted without rewriting historical task/check-in instances.
4. `TASKS` are daily-plan instances. `ROUTINES`, `GOALS`, and `TASKS` use optional links to avoid forcing every task into an unapproved structure.
5. `CHECK_INS` record progress; progress dashboards are derived from them and are not a second editable source of truth.
6. `CONVERSATIONS` and `MESSAGES` are durable only for authenticated users. Guest demo interactions remain outside this durable model unless a later privacy-approved design changes that boundary.
7. `MEMORY_RECORDS` require both ownership and an appropriate consent decision. A source message is optional because a memory can be user-entered or imported from an approved workflow later.
8. `SAFETY_EVENTS`, `AUDIT_EVENTS`, and `SUPPORT_ACCESS_EVENTS` store accountability metadata, not unrestricted raw content.
9. `DATA_LIFECYCLE_REQUESTS` drives asynchronous export, memory-clear, and account-deletion work; it is not itself a copy of the exported data.
10. `AI_USAGE_EVENTS` keeps provider alias/model class and operational measurements separate from business content so provider replacement remains possible.

## 4. Deliberately absent relationships/entities

- No payment/subscription entity: monetization is not an approved MVP requirement.
- No clinical/medical entity: diagnosis, medication, labs, treatment, and disease data are outside V1.
- No organization/household entity: individual-user ownership is the current assumption; future scope is TBD.
- No wearable/device entity: passive sensing is not an MVP requirement.
- No raw AI-provider payload entity: provider requests/responses are minimized and not part of the core business model.
