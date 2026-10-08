# NexusAI — API Contract Catalog

**Document type:** Endpoint-level API contract  
**Phase:** Phase 07 — API Design  
**Status:** Approved — Phase 07 gate passed; Phase 08 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Base path:** `/api/v1`  
**Related:** [07-api-design.md](07-api-design.md), [07-api-authentication.md](07-api-authentication.md), [07-api-error-handling.md](07-api-error-handling.md), [07-api-security.md](07-api-security.md)

## 1. Contract conventions

This catalog is the normative MVP route inventory. It deliberately describes a stable public contract, not controllers, ORM calls, database migrations, or provider SDKs. Public routes use `/api/v1`; `/internal/v1/*` and `/health/*` are separate non-browser namespaces and are not part of the public base path.

### Auth and ownership shorthand

| Code | Meaning |
| --- | --- |
| `P` | Public; no account required |
| `G` | Guest demo capability required; ephemeral session owner only |
| `U` | Authenticated user session; resource must belong to caller’s `account_id` |
| `S` | Trusted support/admin identity plus approved scope and audit event |
| `I` | Internal service/worker identity; never browser-callable |

### Status profiles

| Profile | Success | Common errors |
| --- | --- | --- |
| `R` read | `200` | `401`, `403`, `404`, `429`, `500` |
| `W` write | `200`/`201` | `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500` |
| `A` async | `202` | `400`, `401`, `403`, `404`, `409`, `422`, `429`, `503` |
| `C` chat | `200` | `400`, `401`, `403`, `404`, `409`, `422`, `429`, `502`, `503`, `504` |
| `D` delete | `204` or `202` | `401`, `403`, `404`, `409`, `422`, `429`, `500` |
| `H` health | `200`/`503` | No user-data errors |

All errors use the envelope in [07-api-error-handling.md](07-api-error-handling.md). `IK` means the `Idempotency-Key` header is required; `—` means it is not required. Rate classes are named, non-binding until beta limits are approved.

## 2. Public, guest, and authentication endpoints

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 1 | `GET /public/policies/current` | `P` / none | Return current Terms, Privacy, wellness disclaimer, and policy versions; locale optional and validated | `200` `R`; `404` if unpublished locale | `public-low` / — / cache only published non-user copy |
| 2 | `POST /guest/demo/sessions` | `P` → `G` / ephemeral owner | Create bounded demo capability; body may contain only non-sensitive wellness intention; reject health free text | `201` `W`; `400`, `422`, `429` | `guest-strict` / required / no durable DB record |
| 3 | `POST /guest/demo/sessions/{demo_id}/interactions` | `G` / matching demo capability | Submit constrained sample interaction; validate session TTL, message quota, allowed fields, and non-sensitive content | `200` `C`; `401`, `404`, `422`, `429`, `503` | `guest-strict` / required / ephemeral response, no memory/reminder |
| 4 | `DELETE /guest/demo/sessions/{demo_id}` | `G` / matching demo capability | End demo and evict ephemeral state; idempotent if already expired | `204` `D`; `401`, `404`, `429` | `guest-strict` / required / no content in logs |
| 5 | `POST /auth/register` | `P` / creates account | Submit email and credential/identity assertion to auth boundary; require policy acknowledgement where configured; never log credential | `202` or `201` `W`; `400`, `409`, `422`, `429` | `auth-strict` / required / generic enumeration-safe response |
| 6 | `POST /auth/verify-email` | `P` / one-time proof | Verify opaque proof at auth boundary; proof is single-use and never persisted by NexusAI | `200` `W`; `400`, `401`, `409`, `429` | `auth-strict` / required / no token in response/logs |
| 7 | `POST /auth/login` | `P` / authenticates principal | Credential or external assertion; enforce rate limits and step-up hook; do not reveal whether email exists | `200` `W`; `401`, `429`, `503` | `auth-strict` / required / secure cookie or approved bearer abstraction |
| 8 | `POST /auth/logout` | `U` / current session | Revoke current session; safe to repeat | `204` `D`; `401`, `429` | `auth-strict` / required / only session metadata audited |
| 9 | `GET /auth/sessions` | `U` / own sessions | List current account’s session metadata (device label optional, created/last seen/expiry/status); never token | `200` `R`; `401`, `429` | `user-standard` / — / security metadata only |
| 10 | `DELETE /auth/sessions/{session_id}` | `U` / own session | Revoke a selected session; prevent deleting another account’s session | `204` `D`; `401`, `404`, `409` | `auth-strict` / required / audit revocation |
| 11 | `POST /auth/recovery/request` | `P` / none | Request recovery message; always generic response; throttle by IP/account signals | `202` `A`; `400`, `429` | `auth-strict` / required / no account enumeration |
| 12 | `POST /auth/recovery/confirm` | `P` / one-time proof | Complete recovery with approved credential/assertion; validate proof expiry and strength at auth boundary | `200` `W`; `400`, `401`, `409`, `429` | `auth-strict` / required / no raw credential persistence |
| 13 | `GET /me` | `U` / self | Return minimal account summary and lifecycle status; no auth subjects or token hashes | `200` `R`; `401`, `403` | `user-standard` / — / personal projection only |

## 3. Profile, wellness, consent, and notification preferences

Onboarding uses these canonical profile, wellness, consent, goal, routine, and preference routes as a composed flow. There is no duplicate `/onboarding` write endpoint; the final starter-plan request is handled by `POST /me/daily-plans`.

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 14 | `GET /me/profile` | `U` / self | Return display name, age band if approved, locale, timezone, lifecycle timestamps | `200` `R`; `401`, `403` | `user-standard` / — / personal data, `private no-store` |
| 15 | `PATCH /me/profile` | `U` / self | Partial update of display name/age band/locale/timezone; validate length, locale, IANA timezone, and unresolved age policy | `200` `W`; `400`, `401`, `409`, `422` | `user-standard` / optional / audit meaningful changes |
| 16 | `GET /me/wellness-profile` | `U` / self | Return bounded wellness areas, coaching style, and consented context only if current policy permits | `200` `R`; `401`, `403` | `user-standard` / — / restricted wellness, no clinical fields |
| 17 | `PATCH /me/wellness-profile` | `U` / self | Update allow-listed wellness areas/style/context; require field-level consent and reject diagnosis/medication content | `200` `W`; `400`, `401`, `403`, `422` | `user-standard` / optional / encrypted at service boundary |
| 18 | `GET /me/consents` | `U` / self | List consent history or latest effective decisions by optional `consent_type`; cursor pagination | `200` `R`; `401`, `422` | `user-standard` / — / no hidden policy text |
| 19 | `POST /me/consents` | `U` / self | Append a decision `{consent_type, policy_version, decision}`; version must be published/current; no update/delete of history | `201` `W`; `400`, `401`, `409`, `422` | `user-standard` / required / audit and append-only |
| 20 | `POST /me/consents/{consent_type}/revoke` | `U` / self | Append `revoked` decision and trigger affected controls; type must be revocable | `202` `A`; `400`, `401`, `409`, `422` | `expensive-lifecycle` / required / immediate retrieval stop, async cleanup |
| 21 | `GET /me/notification-preferences` | `U` / self | Return timezone, in-app toggle, safe-off future channel toggles, quiet hours | `200` `R`; `401`, `403` | `user-standard` / — / no sensitive preview content |
| 22 | `PUT /me/notification-preferences` | `U` / self | Replace preferences; validate timezone, paired `HH:MM` quiet hours, channel consent; only in-app reminder delivery active in MVP | `200` `W`; `400`, `401`, `409`, `422` | `user-standard` / optional / consent/audit on changes |

## 4. Goals and routines

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 23 | `GET /me/goals` | `U` / self | List goals with optional `status`, `wellness_area`, cursor, and limit | `200` `R`; `401`, `422` | `user-standard` / — / account-scoped |
| 24 | `POST /me/goals` | `U` / self | Create non-clinical goal `{wellness_area,title,description,start_date,end_date}`; reject diagnosis/treatment language | `201` `W`; `400`, `401`, `409`, `422` | `user-standard` / optional / restricted wellness |
| 25 | `GET /me/goals/{goal_id}` | `U` / self | Return one owned goal | `200` `R`; `401`, `404` | `user-standard` / — / IDOR-safe 404 |
| 26 | `PATCH /me/goals/{goal_id}` | `U` / self | Update permitted fields/status; validate date order and lifecycle transition | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / audit status change |
| 27 | `DELETE /me/goals/{goal_id}` | `U` / self | Soft-delete goal; preserve minimized attribution where policy permits | `204` `D`; `401`, `404`, `409` | `user-standard` / required / no cascade claim |
| 28 | `GET /me/routines` | `U` / self | List routines with status/goal filters and cursor | `200` `R`; `401`, `422` | `user-standard` / — / account-scoped |
| 29 | `POST /me/routines` | `U` / self | Create routine `{goal_id?,name,recurrence_spec,preferred_local_time?,timezone?}`; validate bounded recurrence and same-account goal | `201` `W`; `400`, `401`, `404`, `409`, `422` | `user-standard` / optional / restricted wellness |
| 30 | `GET /me/routines/{routine_id}` | `U` / self | Return one owned routine | `200` `R`; `401`, `404` | `user-standard` / — / IDOR-safe 404 |
| 31 | `PATCH /me/routines/{routine_id}` | `U` / self | Update name/recurrence/timezone/status; no retroactive rewrite of historical check-ins | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / audit lifecycle |
| 32 | `DELETE /me/routines/{routine_id}` | `U` / self | Soft-delete/pause generation; existing task history follows retention policy | `204` `D`; `401`, `404`, `409` | `user-standard` / required / no future jobs |

## 5. Daily plans, tasks, check-ins, and progress

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 33 | `GET /me/daily-plans` | `U` / self | Read plans by local `from_date`/`to_date` or cursor; return task summaries, not hidden prompt text | `200` `R`; `401`, `422` | `user-standard` / — / account/time scoped |
| 34 | `POST /me/daily-plans` | `U` / self | Create a user plan or request starter plan with `{plan_date,generation_mode?,rationale_summary?}`; the server assigns `plan_source`, and AI-assisted generation may return async status | `201` or `202` `W/A`; `401`, `409`, `422`, `503` | `user-standard` or `ai-interactive` / required for generation / no raw prompt |
| 35 | `GET /me/daily-plans/{plan_id}` | `U` / self | Return owned plan and ordered task projections | `200` `R`; `401`, `404` | `user-standard` / — / IDOR-safe 404 |
| 36 | `PATCH /me/daily-plans/{plan_id}` | `U` / self | Update status/rationale permitted by lifecycle; validate active-date uniqueness | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / no clinical inference |
| 37 | `POST /me/daily-plans/{plan_id}/tasks` | `U` / self | Add task `{title,task_type,scheduled_for,routine_id?,goal_id?,sort_order}`; same-account FK checks | `201` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / restricted wellness |
| 38 | `GET /me/tasks/{task_id}` | `U` / self | Return one owned task and current check-in summary | `200` `R`; `401`, `404` | `user-standard` / — / IDOR-safe 404 |
| 39 | `PATCH /me/tasks/{task_id}` | `U` / self | Update title/schedule/status/sort order; completion state is represented by check-in endpoint | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / audit status |
| 40 | `DELETE /me/tasks/{task_id}` | `U` / self | Soft-delete task and prevent future reminder generation | `204` `D`; `401`, `404`, `409` | `user-standard` / required / preserve minimal history |
| 41 | `GET /me/check-ins` | `U` / self | List by task/date/status with cursor; exclude soft-deleted reflections | `200` `R`; `401`, `422` | `user-standard` / — / encrypted reflection only to owner |
| 42 | `POST /me/check-ins` | `U` / self | Create `{task_id?,checkin_date,checkin_kind,status,reflection?}`; validate kind/task pairing and same-account ownership | `201` `W`; `401`, `404`, `409`, `422` | `user-standard` / required / reflection encrypted, no medical measurements |
| 43 | `PATCH /me/check-ins/{check_in_id}` | `U` / self | Correct status/reflection/date within policy; preserve recorded timestamp | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / audit correction |
| 44 | `DELETE /me/check-ins/{check_in_id}` | `U` / self | Soft-delete check-in; recompute derived progress | `204` `D`; `401`, `404`, `409` | `user-standard` / required / no raw reflection in audit |
| 45 | `GET /me/progress` | `U` / self | Return truthful week/month aggregates from check-ins; validate range, goal/routine filters; no medical conclusions | `200` `R`; `401`, `422`, `503` | `user-standard` / — / derived read model, no rankings |

## 6. Conversations, messages, AI interaction, and feedback

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 46 | `GET /me/conversations` | `U` / self | List own conversations with cursor and status filter | `200` `R`; `401`, `422` | `user-standard` / — / private no-store |
| 47 | `POST /me/conversations` | `U` / self | Create empty authenticated conversation `{title?}`; title is non-diagnostic and bounded | `201` `W`; `401`, `422` | `user-standard` / optional / no guest persistence |
| 48 | `GET /me/conversations/{conversation_id}` | `U` / self | Return metadata and message count, not full history by default | `200` `R`; `401`, `404` | `user-standard` / — / content minimized |
| 49 | `PATCH /me/conversations/{conversation_id}` | `U` / self | Rename/end conversation; validate lifecycle and title | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / audit lifecycle |
| 50 | `DELETE /me/conversations/{conversation_id}` | `U` / self | Soft-delete conversation and exclude messages from future context | `204` `D`; `401`, `404`, `409` | `expensive-lifecycle` / required / deletion workflow |
| 51 | `GET /me/conversations/{conversation_id}/messages` | `U` / self | Cursor-paginated ordered messages; owner only; redacted/deleted content projected safely | `200` `R`; `401`, `404`, `422` | `user-standard` / — / no provider payload |
| 52 | `POST /me/conversations/{conversation_id}/messages` | `U` / self | Send `{content,client_message_id?,context_preferences?}`; validate length/scope, current consent, safety before/after AI; response may include candidate memory | `200` `C`; `401`, `404`, `409`, `422`, `429`, `502`, `503`, `504` | `ai-interactive` / required / encrypted messages, minimized provider context |
| 53 | `POST /me/conversations/{conversation_id}/messages/{message_id}/report` | `U` / self | Report an assistant response `{category?,comment?}`; metadata-only audit event, no unrestricted feedback table | `202` `A`; `401`, `404`, `409`, `422` | `user-standard` / required / no raw content in audit |

## 7. Memory and consent-controlled personalization

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 54 | `GET /me/memories` | `U` / self | List approved/revoked/expired memories by status/category; return purpose/source/date and user-readable value only to owner | `200` `R`; `401`, `403`, `422` | `user-standard` / — / never return fingerprint/ciphertext |
| 55 | `POST /me/memories/candidates/{candidate_id}/approve` | `U` / self | Approve/edit/reject an ephemeral candidate `{decision,purpose?,value?,category?}` where `decision` is `approved` or `rejected`; verify candidate/session binding and current memory consent | `201` or `204` `W`; `401`, `404`, `409`, `422` | `expensive-lifecycle` / required / candidate expires, no hidden save |
| 56 | `PATCH /me/memories/{memory_id}` | `U` / self | Edit purpose/category/value or expiry; re-check consent and allow-list | `200` `W`; `401`, `404`, `409`, `422` | `expensive-lifecycle` / required / encrypted value, audit change |
| 57 | `DELETE /me/memories/{memory_id}` | `U` / self | Revoke/delete one memory; retrieval stops immediately; cleanup may be async | `202` `A`; `401`, `404`, `409`, `422` | `expensive-lifecycle` / required / no plaintext in logs |
| 58 | `POST /me/memory-controls/clear` | `U` / self | Clear all durable memories for account; idempotent lifecycle request | `202` `A`; `401`, `409`, `422`, `429` | `expensive-lifecycle` / required / immediate retrieval disable |
| 59 | `POST /me/memory-controls/revoke` | `U` / self | Revoke memory consent, disable future saves/retrieval, enqueue cleanup; does not claim provider/backup deletion | `202` `A`; `401`, `409`, `422`, `429` | `expensive-lifecycle` / required / consent and audit evidence |

## 8. Reminders and notification delivery

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 60 | `GET /me/reminders` | `U` / self | List reminder intent by status/task; include next due and in-app channel only | `200` `R`; `401`, `422` | `user-standard` / — / no sensitive preview |
| 61 | `POST /me/reminders` | `U` / self | Create `{task_id?,channel,schedule_spec,next_due_at?}`; current MVP requires `channel=in_app`, consent and quiet-hour checks | `201` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / safe reminder text |
| 62 | `GET /me/reminders/{reminder_id}` | `U` / self | Return owned reminder intent | `200` `R`; `401`, `404` | `user-standard` / — / IDOR-safe 404 |
| 63 | `PATCH /me/reminders/{reminder_id}` | `U` / self | Pause/resume/disable or update schedule; prevent delivery after disable | `200` `W`; `401`, `404`, `409`, `422` | `user-standard` / optional / audit preference change |
| 64 | `DELETE /me/reminders/{reminder_id}` | `U` / self | Soft-delete reminder and cancel future delivery jobs | `204` `D`; `401`, `404`, `409` | `user-standard` / required / no sensitive delivery payload |
| 65 | `GET /me/reminders/{reminder_id}/deliveries` | `U` / self | Read delivery status/attempt metadata; provider reference is never returned raw | `200` `R`; `401`, `404`, `422` | `user-standard` / — / operational metadata only |

## 9. Export, deletion, usage, support, internal safety, and health

| # | Method and path | Auth / ownership | Purpose; request and validation | Success / errors | Rate / IK / privacy |
| ---: | --- | --- | --- | --- | --- |
| 66 | `GET /me/data-requests` | `U` / self | List own export/delete/memory-clear requests by status and cursor | `200` `R`; `401`, `422` | `expensive-lifecycle` / — / status only |
| 67 | `POST /me/data-requests` | `U` / self | Create `{request_type,scope}` for export/account deletion/memory clear; scope/type pair and re-auth policy validated | `202` `A`; `401`, `409`, `422`, `429` | `expensive-lifecycle` / required / no artifact in response |
| 68 | `GET /me/data-requests/{request_id}` | `U` / self | Return status, timestamps, safe artifact metadata; download requires separate short-lived approved access | `200` `R`; `401`, `404` | `expensive-lifecycle` / — / no public URL |
| 69 | `GET /me/usage` | `U` / self | Return coarse AI usage/limit status and reset window; no provider payload or other users’ data | `200` `R`; `401`, `429` | `user-standard` / — / operational projection |
| 70 | `POST /support/access-events` | `S` / approved operator scope | Create justified, time-bounded support access request `{subject_account_id,access_scope,reason}`; exact role matrix TBD | `201` `W`; `401`, `403`, `409`, `422`, `429` | `support-restricted` / required / reason audited, content denied by default |
| 71 | `GET /support/accounts/{account_id}/status` | `S` / account-status scope | View account lifecycle/verification/session-risk summary; no wellness/chat content | `200` `R`; `401`, `403`, `404` | `support-restricted` / — / support access audited |
| 72 | `GET /support/accounts/{account_id}/consents` | `S` / consent-status scope | View consent types/versions/decisions and timestamps; no encrypted values | `200` `R`; `401`, `403`, `404` | `support-restricted` / — / restricted security |
| 73 | `GET /support/accounts/{account_id}/usage-signals` | `S` / usage-support scope | View coarse usage, abuse/rate-limit, delivery/lifecycle signals; no prompts/content | `200` `R`; `401`, `403`, `404` | `support-restricted` / — / minimized operational data |
| 74 | `GET /support/accounts/{account_id}/audit-events` | `S` / audit-review scope | Read filtered audit metadata with cursor/time bounds; raw content excluded | `200` `R`; `401`, `403`, `404`, `422` | `support-restricted` / — / append-only metadata |
| 75 | `POST /internal/v1/safety/evaluate` | `I` / service scope | Evaluate redacted content/context before/after AI; return provider-neutral action and policy version; never browser-callable | `200` `W`; `401`, `403`, `422`, `503` | internal restricted limit / required / restricted content only in memory, metadata persisted |
| 76 | `GET /health/live` | `P` / infrastructure | Process liveness; no dependency or user data | `200` `H` | no user rate class / — |
| 77 | `GET /health/ready` | `P` / infrastructure | Readiness for required dependencies; return generic status only | `200` or `503` `H` | internal network preferred / — / no secrets |

## 10. Request and response schemas

### 10.1 Common headers

| Header | Requirement |
| --- | --- |
| `Authorization` or secure session cookie | One approved authentication transport; exact baseline TBD |
| `Idempotency-Key` | Required for registration/login/recovery mutations, AI message send, consent revoke, memory/lifecycle changes, and destructive/support operations where listed |
| `X-Request-Id` | Optional bounded client value; server returns a safe generated `request_id` |
| `If-None-Match` | Optional for non-sensitive public policy reads only |
| `Content-Type: application/json` | Required for JSON bodies |

### 10.2 Registration/login projection

```json
{
  "email": "user@example.test",
  "credential": "accepted only at the auth boundary; never logged or stored by NexusAI",
  "identity_provider": "provider-neutral optional assertion",
  "policy_acceptances": [
    {"consent_type": "terms", "policy_version": "terms-v1"},
    {"consent_type": "privacy", "policy_version": "privacy-v1"}
  ]
}
```

Responses return `account_id` only after the approved identity assurance step, verification status, and safe session metadata. They never return password hashes, raw tokens, auth subjects, or provider credentials.

### 10.3 User-owned resource projection

```json
{
  "id": "uuid-string",
  "account_id": "opaque-owner-reference",
  "status": "active",
  "created_at": "2026-08-29T12:00:00Z",
  "updated_at": "2026-08-29T12:00:00Z"
}
```

The API may omit `account_id` from ordinary `/me` responses when it adds no user value. It must never accept a client-selected account ID to widen access.

### 10.4 Chat request/response

Request:

```json
{
  "content": "Help me plan a short evening wind-down routine.",
  "client_message_id": "client-generated-idempotency-scope",
  "context_preferences": {
    "include_active_routines": true,
    "include_progress_summary": true,
    "include_memory": false
  }
}
```

Response:

```json
{
  "data": {
    "conversation_id": "uuid-string",
    "user_message": {"id": "uuid-string", "sender_role": "user", "content": "...", "content_status": "active"},
    "assistant_message": {"id": "uuid-string", "sender_role": "assistant", "content": "...", "content_status": "active"},
    "response_mode": "wellness",
    "is_ai_generated": true,
    "safety": {"disclaimer_code": "wellness_scope_v1", "guidance_code": null},
    "memory_candidate": null
  },
  "meta": {"request_id": "req_opaque"},
  "warnings": []
}
```

For a high-risk or out-of-scope message, `response_mode` is `redirect` or `blocked`, `guidance_code` points to reviewed copy, and no unsafe clinical claim is returned. Internal risk scores are not exposed to the browser.

### 10.5 Memory projection

```json
{
  "id": "uuid-string",
  "category": "daily_habit",
  "purpose": "Personalize evening routine suggestions",
  "value": {"habit": "short wind-down"},
  "status": "approved",
  "source_message_id": "uuid-string-or-null",
  "approved_at": "2026-08-29T12:00:00Z",
  "expires_at": null,
  "revoked_at": null
}
```

`content_fingerprint`, ciphertext, consent internals, and provider identifiers are never returned. Values are decrypted only after owner authorization and current consent evaluation.

### 10.6 Lifecycle request projection

```json
{
  "id": "uuid-string",
  "request_type": "export",
  "scope": "account",
  "status": "queued",
  "requested_at": "2026-08-29T12:00:00Z",
  "completed_at": null,
  "artifact_expires_at": null
}
```

`artifact_reference` is internal and is never exposed. A completed export is not claimed until every promised source and retention exception has been evaluated.

## 11. Pagination, concurrency, and idempotency

- List requests accept `limit` and opaque `cursor`; invalid/expired cursors return `422 invalid_cursor`.
- Writes return a representation or a lifecycle reference after the authoritative transaction. Clients must not infer success from a timeout.
- Repeating an identical `Idempotency-Key` with the same normalized request returns the original result. Reusing it with a different request returns `409 idempotency_key_reused`.
- Chat idempotency covers user-message persistence and provider invocation; a retry must not create duplicate user/assistant messages.
- Lifecycle idempotency maps to `(account_id, idempotency_key)` from the approved database model.
- Concurrent edits use server-side lifecycle/version checks; exact ETag/version field is an implementation decision and must not weaken ownership.

## 12. Contract-level exclusions

There is no V1 endpoint for diagnosis, symptoms, medication/dosage, treatment, emergency dispatch, clinician messaging, wearable telemetry, location tracking, social/community content, billing, unrestricted memory, raw provider payload retrieval, or support access to full chat/memory by default.
