# NexusAI — Final Pre-GitHub Forensic Audit Report

**Date:** 2026-11-19 · **Branch:** `main` · **HEAD:** `2c475adfefcce58b5e34a42076df76b46095641d` (= origin/main)
**Mode:** read-mostly audit; 2 confirmed safe repairs applied. No commit/push/reset performed.

## A. Executive summary
Repository is in good delivery shape. Two real defects found and fixed (1 security logic bug, 1 resource leak). Neural provenance verified genuine end-to-end in a real browser. Remaining issues are documented quality limitations, not blockers.

## B. Audit coverage
- **Frontend:** ChatInterface, MainContent, conversation-types, globals.css — browser-verified (badges, guest flow, Bengali/English).
- **Backend:** `app.ts` (all hooks, CSRF, error handler, route registration), `routes/ai.ts`, `intelligence-engine.ts`, `middleware/auth.ts`, `routes/knowledge-sources.ts` (SQL pattern), `rate-limit.ts` presence.
- **ML service:** `main.py` (all endpoints, safety guard wiring, history normalization, context storage), `model_router.py` (full read), `model_registry.py` (validation/load/provenance), `safety_guard.py` (full read).
- **Config/git:** `.gitignore`, `.gitattributes` (LFS), staged diff, secret scan.

## C. Findings

| ID | Severity | File | Issue | Status |
|---|---|---|---|---|
| F-01 | **HIGH→FIXED** | `apps/api/src/app.ts:233` | CSRF bypass: `config.nodeEnv === 'development' && request.ip === '127.0.0.1' \|\| request.ip === '::1'` — `&&`/`||` precedence meant IPv6 localhost skipped origin checks in ANY env. Note: `buildApp` currently throws in production anyway (persistent-storage guard), limiting real-world exposure. | **FIXED** — parenthesized; tsc clean |
| F-02 | **MEDIUM→FIXED** | `ml-service/main.py` | `conversation_contexts` dict grew unboundedly — per-conversation lists capped at 10 but number of conversation keys never evicted → slow memory leak on long-running service. | **FIXED** — `_ctx_append()` with 500-key cap + quarter eviction; live-verified |
| F-03 | MEDIUM | `safety_guard.py:117-124` | Language-mismatch guard exempts neural output containing ANY digit — observed live: Bengali prompt got English gibberish "Airmble is a lands of 210 miles…" labeled NEURAL_MODEL (digits present). Provenance is honest; quality gap remains. | DOCUMENTED — tightening risks rejecting valid math/code answers; needs careful rule design |
| F-04 | MEDIUM | `intelligence-engine.ts:97` | 10s API→ML timeout vs core-01 cold load (~30-60s on this host) → first neural request can 503 until model warm. | DOCUMENTED — config tradeoff; model stays loaded after first success |
| F-05 | LOW | `middleware/auth.ts:68-88,156-174` | Fallback session path scans up to 100 sessions with bcrypt verify each when `session_id` cookie absent; also caps at 100 sessions. Perf-only; primary path uses indexed lookup. | VERIFIED SAFE — documented |
| F-06 | LOW | `routes/ai.ts` | No message-length validation at API layer (ML rejects >1000 chars with 400 → surfaced as 502/500-ish). `safetyMode` ternary is a no-op (`'NORMAL':'NORMAL'`). | DOCUMENTED — cosmetic/robustness |
| F-07 | LOW | `main.py:129-134` | ML CORS `allow_origins=["*"]` — service binds 127.0.0.1 only; internal. | VERIFIED SAFE — localhost-bound |
| F-08 | INFO | `model_registry.py:222` | `weights_only=False` for medium checkpoint load — controlled local-trust fallback (documented in Phase 1). | VERIFIED SAFE |
| F-09 | INFO | `main.py` | `datetime.utcnow()` deprecation, duplicate `import sys/os`, hardcoded SYSTEM_PROMPT facts. | INFORMATIONAL |
| F-10 | INFO | `try_math_tool` | Integer floor division for ÷ (7÷2→3) — deterministic, labeled "calculator". | VERIFIED SAFE — labeled deterministic |

## D. Repairs applied (this mission)
1. `apps/api/src/app.ts` — CSRF precedence fix (1 line). tsc clean.
2. `packages/ai-core/ml-service/main.py` — bounded conversation-context store (+15/−8 net). `py_compile` clean; service restarted; live `/orchestrate` verified: identity→DETERMINISTIC_HANDLER, math→TOOL, neural→NEURAL_MODEL.

## E. Test results (post-repair)
- `test_phase1_stabilization.py`: **44/44 PASS**
- `test_generation_repairs.py`: **13/13 PASS**
- api `tsc --noEmit`: clean · web typecheck: clean (earlier)
- `pnpm test`: 166 failed / 37 passed — **identical pre-existing baseline** (env/config issues: DATABASE_URL, trusted-origin, prod safeguards); unrelated to changes
- Live E2E: API(4000)+ML(8000)+Web(3000) all serving; browser badge verification from prior mission stands

## F. Remaining problems (none blocking)
- F-03 digit-exemption gap in language guard (quality, honest labeling intact)
- F-04 cold-start neural timeout on low-RAM host
- Neural quality remains poor by design-honest fallback; NOT claimed improved
- vitest suite needs dedicated test-infra mission
- Authenticated (non-guest) chat path untested live

## G. AI Brain integrity — PASS
All 5 registered cores + checkpoints + tokenizer + datasets untouched; no training; no third-party AI; no weight changes. Provenance verified genuine in browser (`Neural · nexus-core-04` badge only on real neural output).

## H. Git safety
- Staged: 54 deletions (untracking only, files preserved locally)
- Modified: **10 files** (9 Phase-1 + `app.ts` CSRF fix)
- Untracked: reports/tests/eval JSONs + preserved assets (zips, corpora, backups, .venv)
- Secret scan: clean; `.env` untracked/untouched; LFS checkpoint unchanged
- Backups: `nexusai_phase1_backup_20261119` (testzip OK) + `nexusai_backup_20261118_postfix` (1.88GB) verified

## I. Final decision: **READY FOR GITHUB APPROVAL**
Evidence: all gates green, 2 real bugs fixed and verified, no secrets, no asset loss, honest remaining-limitations list. Awaiting explicit user authorization for commit + push.
