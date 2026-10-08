# NexusAI — API Error Handling Specification

**Document type:** Error contract, status mapping, and client behavior  
**Phase:** Phase 07 — API Design  
**Status:** Approved — Phase 07 gate passed; Phase 08 through Phase 11 approved; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Related:** [07-api-design.md](07-api-design.md), [07-api-contract.md](07-api-contract.md), [07-api-security.md](07-api-security.md)

## 1. Goals

Errors must be consistent, actionable, privacy-preserving, safe for a wellness product, and stable across provider/database replacements. Clients must never need to parse database errors, stack traces, provider messages, or localized prose to decide whether to retry.

## 2. Normative error envelope

```json
{
  "error": {
    "code": "validation_failed",
    "message": "One or more fields are invalid.",
    "details": [
      {"field": "timezone", "issue": "invalid_timezone"},
      {"field": "title", "issue": "too_long"}
    ],
    "request_id": "req_opaque",
    "retryable": false,
    "retry_after_seconds": null
  }
}
```

Rules:

- `code` is a stable machine-readable identifier; clients branch on it, not `message`.
- `message` is safe, concise, and user-displayable after client localization. It never contains SQL, stack traces, provider names/credentials, tokens, email existence, raw health/chat content, or internal paths.
- `details` is optional and contains allow-listed field/issue pairs only. Sensitive rejected values are never echoed.
- `request_id` is always present and matches the response header where available.
- `retryable` is explicit. `retry_after_seconds` is included only for throttling or known temporary dependencies.
- Error responses use `Cache-Control: no-store` unless they are a generic public health response.

## 3. HTTP status mapping

| HTTP status | API meaning | Typical codes | Client behavior |
| ---: | --- | --- | --- |
| `400` | Malformed request syntax or unsupported content | `malformed_json`, `unsupported_media_type`, `invalid_request` | Fix request shape; do not retry unchanged |
| `401` | Missing/invalid/expired authentication | `unauthenticated`, `session_expired`, `invalid_auth_proof` | Re-authenticate; preserve unsent user draft locally only if safe |
| `403` | Authenticated but action/role/account unavailable | `forbidden`, `account_unavailable`, `consent_required`, `step_up_required` | Do not retry without changed authorization/consent |
| `404` | Resource not found or intentionally hidden for IDOR safety | `not_found`, `demo_expired`, `lifecycle_request_not_found` | Treat as absent; do not probe IDs |
| `409` | State, ownership, uniqueness, or idempotency conflict | `conflict`, `idempotency_key_reused`, `active_plan_exists`, `lifecycle_in_progress` | Refresh state or use a new key after user review |
| `413` | Body/content exceeds safe limit | `payload_too_large`, `content_too_large` | Reduce content; do not retry unchanged |
| `415` | Unsupported media type | `unsupported_media_type` | Send JSON or approved export media type |
| `422` | Semantically invalid field/value | `validation_failed`, `invalid_cursor`, `invalid_recurrence`, `unsafe_input` | Fix indicated fields; do not retry unchanged |
| `429` | Rate/quota/abuse limit | `rate_limited`, `ai_quota_exceeded`, `guest_quota_exceeded` | Honor `Retry-After`; apply backoff |
| `500` | Unexpected internal failure | `internal_error` | Retry only if `retryable=true`; show generic support path |
| `502` | Upstream provider returned unusable response | `ai_provider_invalid`, `notification_provider_invalid` | Retry according to class; never expose provider payload |
| `503` | Temporary dependency/policy/maintenance failure | `dependency_unavailable`, `ai_unavailable`, `auth_dependency_unavailable`, `policy_unavailable` | Retry with backoff if indicated; preserve independent features |
| `504` | Upstream timeout | `ai_timeout`, `dependency_timeout` | Retry idempotently; never claim AI success |

## 4. Error code catalog

### Request and validation

`malformed_json`, `invalid_request`, `validation_failed`, `invalid_cursor`, `unsupported_media_type`, `payload_too_large`, `content_too_large`, `invalid_timezone`, `invalid_date_range`, `invalid_recurrence`, `invalid_quiet_hours`, `unsafe_input`, `unsupported_channel`, `invalid_lifecycle_transition`.

### Authentication and authorization

`unauthenticated`, `session_expired`, `session_revoked`, `invalid_auth_proof`, `account_unavailable`, `forbidden`, `role_required`, `scope_required`, `step_up_required`, `consent_required`.

### Resource and conflict

`not_found`, `demo_expired`, `active_plan_exists`, `duplicate_message`, `idempotency_key_reused`, `conflict`, `lifecycle_in_progress`, `already_completed`, `resource_deleted`.

### Limits and dependencies

`rate_limited`, `guest_quota_exceeded`, `ai_quota_exceeded`, `ai_timeout`, `ai_unavailable`, `ai_provider_invalid`, `policy_unavailable`, `auth_dependency_unavailable`, `notification_provider_invalid`, `dependency_timeout`, `dependency_unavailable`, `internal_error`.

### Safety outcomes

Safety is normally a successful response with `response_mode = redirect` or `blocked`, not an HTTP failure. Use an error only when the request cannot be safely processed at all:

- `unsafe_input` (`422`) when the submitted body violates API content rules before policy evaluation.
- `safety_policy_unavailable` (`503`) when the policy service cannot produce a safe decision; fail closed for memory writes and high-risk AI calls.
- `safety_blocked` (`200` response mode preferred; `403` only if the entire operation is prohibited by policy).

The API never exposes classifier scores, hidden policy text, or emergency-provider claims.

## 5. Retry and backoff rules

- Retry only when `retryable=true`, or for documented `502/503/504` classes with an idempotency key.
- Use exponential backoff with jitter; clients must honor `Retry-After`.
- Never automatically retry login, registration, destructive deletion, memory clear, or AI send without an idempotency key.
- If a timeout occurs after an AI request may have been accepted, retrieve the original result using the same idempotency key or conversation message list; do not send a new message blindly.
- A successful check-in remains successful even if AI, notification, or progress read-model refresh fails; the API returns a warning or eventual status instead of rolling back the check-in.
- Lifecycle workers retry bounded jobs and expose status through `data_lifecycle_requests`; they do not claim completion on partial failure.

## 6. Validation error details

Allowed detail shape:

```json
{
  "field": "recurrence_spec.interval",
  "issue": "must_be_positive"
}
```

Do not include the rejected plaintext reflection, message, memory value, password, token, provider error, or database constraint name. For sensitive free text, return only `unsafe_input` or `content_too_large`.

## 7. Authentication and enumeration safety

- Unknown email, wrong password, unverified email, and account-not-found conditions share safe generic responses where the caller is unauthenticated.
- Protected resource IDs belonging to another account resolve to `404 not_found`, not a distinguishing `403`.
- Session/recovery proofs are never echoed, logged, or returned in an error.
- Rate-limit responses do not confirm account existence or reveal operator/security thresholds.

## 8. AI and provider failure behavior

When the AI provider fails, the API:

1. stops bounded retries at the adapter boundary;
2. records minimized `ai_usage_events`/audit metadata if available;
3. does not persist a fabricated assistant message;
4. returns `ai_unavailable`, `ai_timeout`, or `ai_provider_invalid` with safe wording;
5. keeps check-ins, plans, routines, progress, and memory visibility available where independent;
6. never includes provider payloads, model prompts, credentials, or raw upstream errors.

Provider-specific failures are mapped to the stable catalog so a future adapter replacement does not change the public contract.

## 9. Lifecycle and deletion errors

- Duplicate export/delete/memory-clear requests with the same normalized key return the original lifecycle response.
- A different request with a reused key returns `409 idempotency_key_reused`.
- A conflicting destructive request returns `409 lifecycle_in_progress` and the current safe status reference.
- A failed lifecycle job returns `200` status with `status=failed` through the status endpoint; it does not expose row-level failure details or sensitive artifact paths.
- A deletion/revocation response never claims provider, backup, queue, cache, or replica deletion until the approved policy has evidence.

## 10. Internal logging and support

Logs and traces record status, stable code, route template, request/correlation ID, latency, and coarse dependency category. They do not record error bodies, query parameters, ciphertext, raw health/chat/reflection text, memory values, password/token material, provider payloads, or export URLs.

Support tooling receives the same safe error projection. Direct database errors are mapped to `internal_error` and correlated for restricted operator review.

## 11. Client guidance

- Show the safe `message` or a localized client message for user-correctable errors.
- Render `response_mode=redirect/blocked` as reviewed wellness/safety copy, not as a generic red error banner.
- Preserve idempotency keys across network retries for the same logical action.
- Avoid displaying raw request IDs except when helping a user contact support.
- Do not infer medical meaning from status codes, progress aggregates, or safety modes.

## 12. Open decisions

Exact numeric rate limits, localization strategy, provider-specific retry contracts, support escalation copy, jurisdiction-specific safety responses, and authentication step-up rules remain `TBD / Pending Decision`.
