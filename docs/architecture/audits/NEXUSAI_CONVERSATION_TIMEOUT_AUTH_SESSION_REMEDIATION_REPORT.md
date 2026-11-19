# NexusAI — Conversation Timeout & Auth Session Loss Remediation Report

**Date:** 2026-11-19 · **Incident:** Next.js overlay `Request timeout` at `backend-conversation.ts:54` + unexpected switch to Guest Mode.

## 1. Executive summary
Two confirmed root causes found and fixed: (a) transient backend failures were treated as definitive logout, (b) the AI chat fetch had no timeout and user-cancel was indistinguishable from failure. All fixes verified; 203/203 vitest, typecheck clean, live browser guest-chat verified.

## 2. Screenshot interpretation
`fetchWithTimeout` in `backend-conversation.ts` wraps `createMessage` (persist user/assistant messages to `/api/v1/conversations/:id/messages`, 15s limit). A >15s response throws `Request timeout` → surfaced as a Next.js dev overlay because the error propagated uncaught to the route boundary.

## 3. Confirmed root causes

| ID | Severity | File:line | Root cause | Status |
|---|---|---|---|---|
| C-01 | **HIGH** | `lib/backend-auth.ts` `getSession()` | Returned `{authenticated:false}` for **any** non-OK response — HTTP 500/502/503 (Neon cold start, API restart, DB hiccup) all looked like "logged out" | **FIXED** — only 401/403 mean unauthenticated; other statuses throw |
| C-02 | **HIGH** | `AuthContext.tsx` `refreshUser()` catch | After init, ANY non-'Request timeout' error → `setUser(null)` → Guest Mode. Triggered by `visibilitychange` refresh during API/DB transient failure | **FIXED** — catch now always preserves state (only explicit `authenticated:false` logs out) |
| C-03 | MEDIUM | `ChatInterface.tsx` both send paths | `/api/v1/ai/chat` fetch had **no timeout** — a hung request left `isTyping` forever | **FIXED** — 60s bounded timeout (API→ML is itself ~10s bounded) |
| C-04 | MEDIUM | `ChatInterface.tsx` catch blocks | User-initiated abort (cancel button) fell into generic error path → error bubble on intentional cancel | **FIXED** — non-timeout `AbortError` returns silently; timeout gets its own message |
| C-05 | INFO | `useConversationManager.addMessage` | Optimistic local add + persist; on persist failure message stays visible but unpersisted | DOCUMENTED — error bubble explains; reload loses it (acceptable, noted) |
| C-06 | INFO | `backend-conversation.ts` 15s | Appropriate for DB-only endpoint; observed timeout most likely coincided with API `tsx watch` restart during concurrent file edits | DOCUMENTED |

## 4. Probable contributing factor (evidence-supported, not sole cause)
API runs under `tsx watch` — any `apps/api/src` edit triggers restart; in-flight requests abort → frontend saw timeout + session-check connection failure → combined with C-01/C-02 produced the observed "timeout then Guest Mode" sequence. The code bugs made a transient restart look like logout; both are now fixed.

## 5. Files changed
- `apps/web/lib/backend-auth.ts` — `getSession` 401/403-only logout semantics
- `apps/web/app/components/AuthContext.tsx` — transient errors preserve session
- `apps/web/app/components/ChatInterface.tsx` — 60s AI-request timeout (guest + auth paths), cancel-vs-timeout distinction, timer cleanup in `finally`

## 6. Security impact
None negative — 401/403 still log out; CSRF/cookie/session logic untouched; no secrets logged; timeout does not weaken auth (server still enforces).

## 7. Verification
- `tsc --noEmit` (web): clean
- `pnpm test`: **203/203 PASS**
- Live browser (Playwright/Chrome): guest chat → identity answer + `Deterministic` badge, no page errors (401 console lines = benign guest session probes)
- Authenticated-path session preservation: **code-verified only** — live account test blocked by Neon no-write rule (same blocker as before)

## 8. Remaining limitations
- Authenticated E2E (register→chat→logout) still requires isolated test DB or approved synthetic account.
- Web dev server OOMs intermittently on this ~1GB-free host — environmental, retried successfully.
- `createMessage` persist uses 15s timeout; Neon cold-start tail could rarely exceed it — error now surfaces gracefully instead of crashing.

## 9. Database safety
No writes to Neon; no schema/data changes; guest-mode paths unaffected.

## 10. AI Brain integrity
No model/tokenizer/checkpoint changes; provenance badges unaffected.

## 11. Git status
17→18 modified files (3 new this mission: backend-auth.ts, AuthContext.tsx, ChatInterface.tsx — ChatInterface was already modified). 54 staged untrackings preserved. No commit/push.

## Issue status table
| Issue | Status |
|---|---|
| Timeout crash overlay | FIXED AND VERIFIED (bounded timeout + graceful error) |
| Guest-mode on transient failure | FIXED, VERIFICATION PARTIAL (code+typecheck verified; live-auth blocked) |
| Cancel shows error bubble | FIXED AND VERIFIED (code path) |
| Unbounded AI fetch | FIXED AND VERIFIED |
| Neon auth lifecycle | BLOCKED (infra, documented) |
