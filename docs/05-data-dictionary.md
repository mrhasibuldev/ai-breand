# NexusAI — Phase 05 Data Dictionary

**Product:** NexusAI — Personal AI Health & Wellness Companion  
**Phase:** Phase 05 — Database Design  
**Status:** Approved — Phase 05 gate passed; Phase 06 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Related design:** [05-database-design.md](05-database-design.md) · [05-erd.md](05-erd.md)  
**Scope:** Logical field definitions only. Types are technology-neutral; this is not SQL/DDL or an ORM specification.

## 1. Field legend and global rules

| Column | Meaning |
| --- | --- |
| **Type** | Logical type; physical engine mapping is a later decision. |
| **Req.** | `Required` means needed for a valid persisted record; `Optional` means nullable or conditionally populated. |
| **Default** | Safe system default only; `None` means no default is assumed. |
| **Key** | `PK` primary key, `FK` foreign key, `UK` unique constraint, or `Scoped UK` uniqueness with ownership scope. |
| **Constraints** | Validation, lifecycle, relationship, or privacy rule. |
| **Sensitivity** | `Personal`, `Restricted wellness`, `Restricted security`, or `Operational`. |

Global conventions:

- All durable IDs are opaque `UUID` values and are immutable.
- All timestamps are UTC `TIMESTAMP` values unless a field explicitly says local time/date.
- User-owned entities require `account_id` ownership validation in addition to foreign-key existence.
- `ENCRYPTED_TEXT` and `ENCRYPTED_JSON` indicate application/data-service encryption before persistence; key management is not defined here.
- Controlled `ENUM` values must be allow-listed by the owning domain and versioned when behavior changes.
- User-provided text is length-limited and validated at the application boundary; no raw restricted text is indexed for convenience.
- `deleted_at` is a lifecycle marker, not proof that all copies have been physically purged.

## 2. `accounts`

**Purpose:** Durable identity and account-lifecycle anchor. Authentication credential material belongs to the isolated auth boundary or approved identity provider; it is not stored here.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable, non-guessable | Internal account identifier. | Personal |
| `auth_issuer` | STRING(100) | Required | None | Part of UK | Provider/local issuer alias; not a secret. | Identity issuer alias. | Restricted security |
| `auth_subject` | STRING(255) | Required | None | Part of UK | Unique within `auth_issuer`; opaque provider subject. | External identity reference. | Restricted security |
| `email_normalized` | STRING(320) | Required | None | UK (non-purged) | Normalized for lookup; protect from enumeration. | Account email reference. | Personal |
| `status` | ENUM | Required | `active` | — | `active`, `suspended`, `deletion_pending`, `deleted`, `purged`. | Account lifecycle state. | Restricted security |
| `email_verified_at` | TIMESTAMP | Optional | None | — | Must be null until verification succeeds. | Verification instant. | Restricted security |
| `created_at` | TIMESTAMP | Required | Now | — | Immutable. | Account creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | Monotonic with meaningful mutation. | Last account mutation. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Set when deletion is accepted; not a physical purge guarantee. | Account deletion marker. | Restricted security |
| `purge_after` | TIMESTAMP | Optional | None | — | Set only by approved retention policy. | Earliest eligible purge time. | Restricted security |

## 3. `auth_sessions`

**Purpose:** Revocable session metadata for authenticated access. Raw session/refresh tokens are never stored.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Session identifier. | Restricted security |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Account must be active; cross-account reference forbidden. | Owning account. | Restricted security |
| `session_token_hash` | STRING(255) | Required | None | UK | Cryptographic hash only; rotate/revoke safely. | Server lookup verifier for the session. | Restricted security |
| `created_at` | TIMESTAMP | Required | Now | — | Immutable. | Session creation time. | Operational |
| `expires_at` | TIMESTAMP | Required | None | — | Must be after `created_at`; exact lifetime TBD. | Session expiry. | Restricted security |
| `last_seen_at` | TIMESTAMP | Required | Now | — | Cannot precede `created_at`. | Last accepted use. | Restricted security |
| `revoked_at` | TIMESTAMP | Optional | None | — | Set once; cannot precede creation. | Revocation instant. | Restricted security |
| `status` | ENUM | Required | `active` | — | `active`, `expired`, `revoked`. | Session state. | Restricted security |

## 4. `user_profiles`

**Purpose:** Basic user-facing profile, locale, and timezone. Exact age collection is not decided; no date of birth is modeled.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Profile identifier. | Personal |
| `account_id` | UUID | Required | None | FK + UK → `accounts.id` | At most one active profile per account. | Owning account. | Personal |
| `display_name` | STRING(120) | Optional | None | — | Required before onboarding completion if product policy keeps name collection. | User-facing name; not legal identity. | Personal |
| `age_band` | STRING(40) | Optional | None | — | Allowed values and whether collection is enabled are TBD; never exact DOB by default. | Coarse age information only if approved. | Personal |
| `locale` | STRING(20) | Optional | None | — | Valid locale code; product fallback applies when absent. | Language/format preference. | Personal |
| `timezone` | STRING(64) | Optional | None | — | Valid IANA timezone when populated; required before reminders activate. | User display/scheduling timezone. | Personal |
| `created_at` | TIMESTAMP | Required | Now | — | — | Profile creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last profile update. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; account deletion workflow controls purge. | Profile deletion marker. | Restricted security |

## 5. `wellness_profiles`

**Purpose:** Bounded, consented wellness context used for personalization. It is not a medical record and must not become an unrestricted health blob.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Wellness profile identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK + UK → `accounts.id` | At most one active profile per account. | Owning account. | Restricted wellness |
| `wellness_areas` | JSON | Optional | Empty allow-listed set | — | Bounded values such as sleep, movement, hydration, mindfulness, nutrition routine; no diagnoses. | Selected wellness areas. | Restricted wellness |
| `consented_context` | ENCRYPTED_JSON | Optional | None | — | Only product-approved, explicitly consented context; bounded size/version. | Minimal lifestyle context needed for guidance. | Restricted wellness |
| `coaching_style` | ENUM | Optional | None | — | Allow-listed style; no clinical inference. | Preferred tone/format of guidance. | Personal |
| `status` | ENUM | Required | `active` | — | `active`, `archived`, `deleted`. | Profile lifecycle. | Restricted wellness |
| `created_at` | TIMESTAMP | Required | Now | — | — | Creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last mutation. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; exclude from personalization after deletion. | Deletion marker. | Restricted security |

## 6. `consent_records`

**Purpose:** Append-only history of policy and feature consent decisions. Current consent is derived from the latest applicable record; it is not a hidden mutable flag.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Consent decision identifier. | Restricted security |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Account ownership required. | Consenting account. | Restricted security |
| `consent_type` | ENUM | Required | None | Scoped history | Examples: terms, privacy, personalization, memory, reminders, channel. | What the user decided about. | Restricted security |
| `policy_version` | STRING(80) | Required | None | — | Version must map to a published policy artifact. | Policy/copy version shown to user. | Restricted security |
| `decision` | ENUM | Required | None | — | `granted`, `denied`, `revoked`, `superseded`; append-only. | User decision. | Restricted security |
| `captured_at` | TIMESTAMP | Required | Now | — | Immutable; UTC. | Decision time. | Restricted security |
| `revoked_at` | TIMESTAMP | Optional | None | — | Required for a direct revoke event where applicable. | Revoke time. | Restricted security |
| `capture_source` | STRING(40) | Required | None | — | `onboarding`, `settings`, `checkout`, `support`, or approved source. | Where the decision was captured. | Restricted security |

## 7. `goals`

**Purpose:** User-defined, non-clinical wellness goals.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Goal identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Cross-account references forbidden. | Owning account. | Restricted wellness |
| `wellness_area` | ENUM | Required | None | — | Allow-listed general wellness area; no disease/diagnosis values. | Area the goal supports. | Restricted wellness |
| `title` | STRING(160) | Required | None | — | User-editable, non-empty, length-limited. | Goal title. | Restricted wellness |
| `description` | TEXT | Optional | None | — | Bounded; no medical record intended. | Optional user explanation. | Restricted wellness |
| `status` | ENUM | Required | `active` | — | `draft`, `active`, `paused`, `completed`, `archived`, `deleted`. | Goal lifecycle. | Restricted wellness |
| `start_date` | DATE | Required | Current local date | — | Must not be after `end_date` when end exists. | Goal start date. | Restricted wellness |
| `end_date` | DATE | Optional | None | — | Calendar date in user timezone. | Optional target/end date. | Restricted wellness |
| `created_at` | TIMESTAMP | Required | Now | — | — | Creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last mutation. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; historical attribution may remain minimized. | Deletion marker. | Restricted security |

## 8. `routines`

**Purpose:** Repeatable habit/routine definitions used to generate daily task instances.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Routine identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Cross-account references forbidden. | Owning account. | Restricted wellness |
| `goal_id` | UUID | Optional | None | FK → `goals.id` | If present, goal must belong to same account. | Optional supporting goal. | Restricted wellness |
| `name` | STRING(160) | Required | None | — | Non-empty, length-limited. | Routine name. | Restricted wellness |
| `recurrence_spec` | JSON | Required | None | — | Versioned, bounded recurrence representation; exact recurrence model TBD. | When routine produces tasks. | Restricted wellness |
| `preferred_local_time` | STRING(5) | Optional | None | — | `HH:MM` local time when populated. | Preferred reminder/task time. | Personal |
| `timezone` | STRING(64) | Optional | None | — | Valid IANA timezone when populated; account timezone fallback otherwise. | Scheduling timezone. | Personal |
| `status` | ENUM | Required | `active` | — | `draft`, `active`, `paused`, `archived`, `deleted`. | Routine lifecycle. | Restricted wellness |
| `created_at` | TIMESTAMP | Required | Now | — | — | Creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last mutation. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; no future task generation. | Deletion marker. | Restricted security |

## 9. `daily_plans`

**Purpose:** One user-facing plan for a calendar date; plan content may be user-created, template-generated, or AI-assisted.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Plan identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Cross-account references forbidden. | Owning account. | Restricted wellness |
| `plan_date` | DATE | Required | Current local date | Scoped UK | One active plan per account/date; timezone-aware generation. | Calendar date represented. | Restricted wellness |
| `status` | ENUM | Required | `draft` | — | `draft`, `active`, `completed`, `archived`, `deleted`. | Plan lifecycle. | Restricted wellness |
| `plan_source` | ENUM | Required | `user` | — | `user`, `template`, `ai_assisted`, `system`; source does not imply authority. | How plan was created. | Operational |
| `rationale_summary` | TEXT | Optional | None | — | Bounded, non-clinical, no hidden prompt/system text. | User-facing explanation of plan choices. | Restricted wellness |
| `created_at` | TIMESTAMP | Required | Now | — | — | Creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last mutation. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; tasks follow lifecycle policy. | Deletion marker. | Restricted security |

## 10. `tasks`

**Purpose:** Concrete task instances shown in a daily plan and optionally attributed to a routine or goal.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Task identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Must match all optional parent accounts. | Owning account. | Restricted wellness |
| `daily_plan_id` | UUID | Optional | None | FK → `daily_plans.id` | If present, same-account plan. | Containing daily plan. | Restricted wellness |
| `routine_id` | UUID | Optional | None | FK → `routines.id` | If present, same-account routine. | Source routine. | Restricted wellness |
| `goal_id` | UUID | Optional | None | FK → `goals.id` | If present, same-account goal. | Optional attribution goal. | Restricted wellness |
| `title` | STRING(180) | Required | None | — | Non-empty, bounded. | User-facing task title. | Restricted wellness |
| `task_type` | ENUM | Required | `habit` | — | `habit`, `reflection`, `wellness_education`, `planning`. | General task category; no clinical task type. | Restricted wellness |
| `scheduled_for` | TIMESTAMP | Optional | None | — | UTC instant derived from user timezone. | Optional scheduled time. | Personal |
| `status` | ENUM | Required | `pending` | — | `pending`, `completed`, `skipped`, `snoozed`, `cancelled`, `deleted`. | Task lifecycle. | Restricted wellness |
| `sort_order` | INTEGER | Required | `0` | — | Non-negative. | Display order within plan. | Operational |
| `completed_at` | TIMESTAMP | Optional | None | — | Only populated for completed state. | Completion instant. | Restricted wellness |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; preserve minimal audit reference. | Deletion marker. | Restricted security |

## 11. `check_ins`

**Purpose:** User progress records for a task or daily reflection. No medical measurements are modeled in V1.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Check-in identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Must match task account when task exists. | Owning account. | Restricted wellness |
| `task_id` | UUID | Optional | None | FK → `tasks.id` | Same-account task; null for daily/general check-in. | Related task instance. | Restricted wellness |
| `checkin_date` | DATE | Required | User-local current date | — | Calendar date in account timezone. | Date being recorded. | Restricted wellness |
| `checkin_kind` | ENUM | Required | `task` | — | `task`, `daily_reflection`. | Check-in context. | Restricted wellness |
| `status` | ENUM | Required | `completed` | — | `completed`, `skipped`, `not_recorded`, `snoozed`. | User-reported progress state. | Restricted wellness |
| `reflection` | ENCRYPTED_TEXT | Optional | None | — | Bounded free text; never required for completion. | Optional private reflection. | Restricted wellness |
| `recorded_at` | TIMESTAMP | Required | Now | — | Immutable original record time. | When recorded. | Restricted wellness |
| `updated_at` | TIMESTAMP | Required | Now | — | User correction updates this value. | Last correction time. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; excluded from progress aggregates. | Deletion marker. | Restricted security |

## 12. `conversations`

**Purpose:** Durable container for authenticated AI wellness chats. Guest demo conversations are ephemeral and outside this model.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Conversation identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Authenticated account only. | Owning account. | Restricted wellness |
| `status` | ENUM | Required | `active` | — | `active`, `ended`, `deleted`. | Conversation lifecycle. | Restricted wellness |
| `title` | STRING(160) | Optional | None | — | User-facing label only; no auto-generated diagnosis. | Optional conversation title. | Restricted wellness |
| `started_at` | TIMESTAMP | Required | Now | — | Immutable. | Start time. | Operational |
| `ended_at` | TIMESTAMP | Optional | None | — | Must be after start. | End time. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; messages follow deletion policy. | Deletion marker. | Restricted security |

## 13. `messages`

**Purpose:** Ordered user/assistant message content within a conversation. System prompts and raw provider payloads are not stored here.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Message identifier. | Restricted wellness |
| `conversation_id` | UUID | Required | None | FK → `conversations.id` | Same-account ownership inherited from conversation. | Parent conversation. | Restricted wellness |
| `sequence_no` | INTEGER | Required | None | Scoped UK with conversation | Positive, strictly ordered per conversation. | Display/context order. | Operational |
| `sender_role` | ENUM | Required | None | — | `user` or `assistant`; no persisted hidden system role in MVP. | Message author class. | Restricted wellness |
| `content` | ENCRYPTED_TEXT | Required | None | — | Bounded; encrypt before persistence; user deletion supported. | Message text. | Restricted wellness |
| `content_status` | ENUM | Required | `active` | — | `active`, `redacted`, `deleted`, `blocked`. | Content lifecycle/safety state. | Restricted security |
| `created_at` | TIMESTAMP | Required | Now | — | Immutable. | Message creation time. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; exclude from future context. | Deletion marker. | Restricted security |

## 14. `memory_records`

**Purpose:** User-approved, purpose-bound Minimal Memory. Unapproved candidates should remain ephemeral until the user confirms them.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Memory identifier. | Restricted wellness |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Account must own the record. | Owning account. | Restricted wellness |
| `consent_record_id` | UUID | Required | None | FK → `consent_records.id` | Must point to applicable granted memory consent. | Consent evidence. | Restricted security |
| `source_message_id` | UUID | Optional | None | FK → `messages.id` | If present, same-account message; source content is not copied. | Optional origin message. | Restricted wellness |
| `category` | ENUM | Required | None | — | `name`, `age_band`, `wellness_goal`, `preference`, `daily_habit`, `plan_preference`; no diagnosis category. | Memory category. | Restricted wellness |
| `purpose` | STRING(160) | Required | None | — | Specific personalization purpose; not “all future use.” | Why it is remembered. | Restricted wellness |
| `value` | ENCRYPTED_JSON | Required | None | — | Bounded, user-approved value; schema/version allow-listed. | Remembered content. | Restricted wellness |
| `status` | ENUM | Required | `approved` | — | Durable states: `approved`, `revoked`, `expired`, `deleted`; candidate state is ephemeral. | Memory lifecycle. | Restricted security |
| `content_fingerprint` | STRING(128) | Optional | None | Scoped uniqueness when used | Privacy-safe deduplication only; must not permit plaintext recovery. | Optional duplicate-prevention fingerprint. | Restricted security |
| `approved_at` | TIMESTAMP | Required | Now on confirmation | — | Must exist before status `approved`. | User approval time. | Restricted security |
| `revoked_at` | TIMESTAMP | Optional | None | — | Set on revoke; retrieval must stop immediately. | Revoke time. | Restricted security |
| `expires_at` | TIMESTAMP | Optional | None | — | Optional purpose-based expiry. | Automatic expiry time. | Restricted security |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete marker before approved purge. | Deletion marker. | Restricted security |

## 15. `notification_preferences`

**Purpose:** One active per-account configuration for reminders, quiet hours, and channel opt-in.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Preference record identifier. | Personal |
| `account_id` | UUID | Required | None | FK + UK → `accounts.id` | At most one active record per account. | Owning account. | Personal |
| `timezone` | STRING(64) | Required | None | — | Valid IANA timezone; reminder activation requires it. | Scheduling timezone. | Personal |
| `in_app_enabled` | BOOLEAN | Required | `true` | — | Cannot be true if account has globally disabled reminders. | In-app reminder channel. | Personal |
| `email_enabled` | BOOLEAN | Optional | Safe-off recommendation (TBD) | — | Must require separate channel consent and provider approval. | Future email channel toggle. | Personal |
| `push_enabled` | BOOLEAN | Optional | Safe-off recommendation (TBD) | — | Must require separate channel consent and provider approval. | Future push channel toggle. | Personal |
| `quiet_hours_start` | STRING(5) | Optional | None | — | `HH:MM`; exact product default TBD. | Quiet-hour start in local timezone. | Personal |
| `quiet_hours_end` | STRING(5) | Optional | None | — | `HH:MM`; must be paired with start. | Quiet-hour end in local timezone. | Personal |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last preference mutation. | Operational |

## 16. `reminders`

**Purpose:** Reminder scheduling intent, separate from actual delivery attempts.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Reminder identifier. | Personal |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Cross-account references forbidden. | Owning account. | Personal |
| `task_id` | UUID | Optional | None | FK → `tasks.id` | If present, same-account task. | Optional task being reminded. | Restricted wellness |
| `channel` | ENUM | Required | `in_app` | — | `in_app` is MVP; other channels require separate approval/consent. | Delivery channel. | Personal |
| `schedule_spec` | JSON | Required | None | — | Versioned, bounded recurrence/time representation; exact model TBD. | Reminder schedule intent. | Personal |
| `next_due_at` | TIMESTAMP | Optional | None | — | UTC; recalculated from schedule and quiet hours. | Next eligible delivery time. | Operational |
| `status` | ENUM | Required | `active` | — | `active`, `paused`, `disabled`, `deleted`. | Reminder lifecycle. | Personal |
| `created_at` | TIMESTAMP | Required | Now | — | — | Creation time. | Operational |
| `updated_at` | TIMESTAMP | Required | Now | — | — | Last mutation. | Operational |
| `deleted_at` | TIMESTAMP | Optional | None | — | Soft-delete; no future delivery. | Deletion marker. | Restricted security |

## 17. `notification_deliveries`

**Purpose:** Delivery attempt and provider outcome metadata; it is never the scheduling source of truth.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Delivery attempt identifier. | Operational |
| `reminder_id` | UUID | Required | None | FK → `reminders.id` | Same-account ownership inherited. | Source reminder. | Operational |
| `status` | ENUM | Required | `queued` | — | `queued`, `sent`, `delivered`, `failed`, `cancelled`. | Attempt outcome. | Operational |
| `provider_alias` | STRING(80) | Required | `internal` for in-app | — | Internal adapter alias; not a business key. | Provider/channel adapter label. | Operational |
| `provider_reference_hash` | STRING(128) | Optional | None | — | Hash only; no raw provider message ID if avoidable. | Correlation to provider outcome. | Operational |
| `attempted_at` | TIMESTAMP | Required | Now | — | Immutable attempt time. | Attempt instant. | Operational |
| `delivered_at` | TIMESTAMP | Optional | None | — | Must follow attempt time. | Delivery confirmation time. | Operational |
| `failure_category` | STRING(80) | Optional | None | — | Coarse allow-listed category; no raw provider error/payload. | Reason class for failure. | Operational |

## 18. `safety_events`

**Purpose:** Metadata about safety classification and action for accountability and evaluation. Raw prompts are excluded by default.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Safety event identifier. | Restricted security |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Persisted events require authenticated owner; guest telemetry stays ephemeral/minimized. | Account associated with event. | Restricted security |
| `conversation_id` | UUID | Optional | None | FK → `conversations.id` | Same-account conversation. | Optional conversation context. | Restricted security |
| `message_id` | UUID | Optional | None | FK → `messages.id` | Same-conversation message. | Optional message context. | Restricted security |
| `risk_level` | ENUM | Required | `none` | — | `none`, `low`, `medium`, `high`, `critical`; policy-defined. | Risk classification. | Restricted security |
| `policy_action` | ENUM | Required | None | — | `allow`, `caution`, `redirect`, `block`, `escalation_guidance`. | Action taken by safety policy. | Restricted security |
| `policy_version` | STRING(80) | Required | None | — | Must map to reviewed policy artifact. | Safety policy version. | Restricted security |
| `escalation_shown` | BOOLEAN | Required | `false` | — | True only when approved escalation copy was displayed. | Whether guidance was shown. | Restricted security |
| `classifier_version` | STRING(80) | Optional | None | — | Internal version alias; no raw model payload. | Classifier/policy evaluator version. | Operational |
| `created_at` | TIMESTAMP | Required | Now | — | Immutable. | Event time. | Operational |

## 19. `data_lifecycle_requests`

**Purpose:** Idempotent workflow record for account export, account deletion, or memory-clear operations.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Lifecycle request identifier. | Restricted security |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Requester/subject account. | Account whose data is affected. | Restricted security |
| `request_type` | ENUM | Required | None | — | `export`, `account_delete`, `memory_clear`. | Requested operation. | Restricted security |
| `scope` | ENUM | Required | None | — | `memory`, `account`, or approved narrower scope; caller must specify explicitly. | Data scope. | Restricted security |
| `status` | ENUM | Required | `requested` | — | `requested`, `queued`, `running`, `completed`, `failed`, `cancelled`. | Workflow state; never claim complete early. | Restricted security |
| `idempotency_key` | STRING(160) | Required | None | Scoped UK | Prevents duplicate destructive/export jobs within retention window. | Retry-safe request key. | Restricted security |
| `artifact_reference` | STRING(255) | Optional | None | — | Opaque internal encrypted-store reference; never public URL. | Temporary export artifact pointer. | Restricted security |
| `requested_at` | TIMESTAMP | Required | Now | — | Immutable. | Request time. | Restricted security |
| `completed_at` | TIMESTAMP | Optional | None | — | Set only after verified completion. | Completion time. | Restricted security |
| `artifact_expires_at` | TIMESTAMP | Optional | None | — | Required for export artifact; must be after creation. | Automatic export expiry. | Restricted security |

## 20. `support_access_events`

**Purpose:** Justified, time-bounded exceptional operator access record. It does not grant access by itself; authorization policy remains external to this record.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Support-access event identifier. | Restricted security |
| `operator_account_id` | UUID | Required | None | FK → `accounts.id` | Must represent approved support/admin identity. | Operator account. | Restricted security |
| `subject_account_id` | UUID | Required | None | FK → `accounts.id` | Target user account; must be distinct unless self-support is approved. | Subject of support action. | Restricted security |
| `access_scope` | ENUM | Required | None | — | `account_status`, `reminder_delivery`, `export_status`, or future approved scope; private content is not default. | Narrow access scope. | Restricted security |
| `reason` | STRING(500) | Required | None | — | Human-entered, bounded, non-sensitive justification. | Why access was requested. | Restricted security |
| `outcome` | ENUM | Required | `requested` | — | `requested`, `approved`, `denied`, `completed`, `expired`. | Access decision/outcome. | Restricted security |
| `started_at` | TIMESTAMP | Required | None | — | Must follow approval when approval is required. | Access start. | Restricted security |
| `ended_at` | TIMESTAMP | Optional | None | — | Must follow start. | Access end/expiry. | Restricted security |
| `created_at` | TIMESTAMP | Required | Now | — | Immutable. | Event creation time. | Operational |

## 21. `audit_events`

**Purpose:** Append-only or tamper-evident security, privacy, consent, lifecycle, policy, and admin history.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable; append-only. | Audit event identifier. | Restricted security |
| `actor_account_id` | UUID | Optional | None | FK → `accounts.id` | Null only for approved system actor; actor identity must be traceable elsewhere. | Who initiated the event. | Restricted security |
| `subject_account_id` | UUID | Optional | None | FK → `accounts.id` | Target account where applicable. | Whose data/action was affected. | Restricted security |
| `event_type` | STRING(120) | Required | None | — | Allow-listed event taxonomy; no raw content. | Action/event category. | Restricted security |
| `entity_type` | STRING(80) | Required | None | — | Allow-listed logical entity name. | Entity affected. | Restricted security |
| `entity_id` | UUID | Optional | None | — | Null for aggregate/system event; otherwise internal ID. | Affected entity reference. | Restricted security |
| `outcome` | ENUM | Required | None | — | `success`, `failure`, `denied`, `pending`. | Event outcome. | Restricted security |
| `policy_version` | STRING(80) | Optional | None | — | Policy reference when a policy decision is involved. | Relevant policy version. | Restricted security |
| `correlation_id` | STRING(120) | Required | Generated | — | Must not contain secrets or raw user content. | Cross-service trace reference. | Operational |
| `occurred_at` | TIMESTAMP | Required | Now | — | Immutable UTC instant. | Event occurrence time. | Restricted security |

## 22. `ai_usage_events`

**Purpose:** Minimized AI-provider and latency telemetry for reliability, quota, and cost monitoring. It is not a prompt/response archive.

| Field | Type | Req. | Default | Key | Constraints | Description | Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | UUID | Required | Generated | PK | Immutable. | Usage event identifier. | Operational |
| `account_id` | UUID | Required | None | FK → `accounts.id` | Ownership required; aggregate provider telemetry must be separately minimized. | Account charged/associated for usage. | Operational |
| `conversation_id` | UUID | Optional | None | FK → `conversations.id` | Same-account conversation. | Optional chat context reference. | Operational |
| `message_id` | UUID | Optional | None | FK → `messages.id` | Same-account message; no content copy. | Optional message association. | Operational |
| `provider_alias` | STRING(80) | Required | None | — | Internal alias, not provider business ID. | Provider adapter label. | Operational |
| `model_class` | STRING(80) | Required | None | — | Abstract class/tier; exact model choice is TBD. | Model category used. | Operational |
| `input_units` | INTEGER | Optional | None | — | Non-negative; only if provider reports it. | Coarse input usage count. | Operational |
| `output_units` | INTEGER | Optional | None | — | Non-negative; only if provider reports it. | Coarse output usage count. | Operational |
| `latency_ms` | INTEGER | Optional | None | — | Non-negative; no prompt/response content. | Provider call latency. | Operational |
| `safety_policy_version` | STRING(80) | Optional | None | — | Policy reference for the call. | Safety policy applied. | Operational |
| `created_at` | TIMESTAMP | Required | Now | — | Immutable. | Usage event time. | Operational |

## 23. Cross-entity sensitivity and access summary

| Group | Entities | Default access |
| --- | --- | --- |
| Identity/security | `accounts`, `auth_sessions`, `consent_records`, `audit_events`, `support_access_events` | Auth/security services; least privilege; audited |
| Restricted wellness | `wellness_profiles`, `goals`, `routines`, `daily_plans`, `tasks`, `check_ins`, `conversations`, `messages`, `memory_records` | Owning user and narrowly scoped product services |
| Reminder/operations | `notification_preferences`, `reminders`, `notification_deliveries`, `ai_usage_events` | Owning user for settings; workers for delivery/telemetry |
| Safety | `safety_events` | Safety/authorized operators; no raw content by default |
| Lifecycle | `data_lifecycle_requests` | Owning user plus privacy worker/status surfaces |

## 24. Explicitly not modeled

No entity/field is defined for diagnosis, disease, symptoms, medication, dosage, prescriptions, lab values, clinical records, insurance, wearable telemetry, location history, or raw AI provider payloads. Adding any such data requires a new product/privacy/safety decision and phase-gated documentation.
