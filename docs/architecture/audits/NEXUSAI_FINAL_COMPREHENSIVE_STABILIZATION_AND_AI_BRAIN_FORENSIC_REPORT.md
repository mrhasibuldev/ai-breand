# NexusAI — Final Comprehensive Stabilization & AI Brain Forensic Report

**Date:** 2026-11-19 · **Branch:** `main` · **HEAD:** `2c475adfefcce58b5e34a42076df76b46095641d` (= origin/main)
**Git state at audit:** 54 staged index-only untrackings · 20 modified · 34 untracked (reports/tests/preserved assets). No commit/push/reset performed at any point.

---

## Part 1 — Executive summary
NexusAI is a working three-tier application (Next.js web → Fastify API → FastAPI ML service) backed by **genuinely independent neural models** — verified by runtime traces, not just registry entries. Infrastructure is now stable and honestly instrumented: provenance badges reflect the real execution path, rejected neural output surfaces as fallback, and transient failures no longer cause false logouts.

**Honest bottom line:** the *plumbing* is correct and verified; the *neural models are early-stage* — most open-ended prompts produce gibberish or honest fallback. Deterministic handlers (identity/capability/math) and the math tool are accurate. No external AI is used anywhere.

## Part 2 — Live testing results
| Check | Result |
|---|---|
| Web :3000 | 200, Next 15.5.24 (intermittent OOM on ~1GB-free host — environmental) |
| API :4000 | listening; `/api/v1/me` 401 no-cookie, 401 bad-cookie (live Neon) |
| ML :8000 | `/health` ok; `/orchestrate` verified |
| Guest chat (desktop+mobile Playwright) | PASS — Bengali greeting → `Deterministic` badge, no console/page errors |
| Guest→auth, authenticated chat | **BLOCKED** — no isolated Neon test DB; write-path prohibited |
| Session preservation on transient failure | FIXED in code (401/403-only logout); live-auth verification blocked |

## Part 3 — Complete AI architecture
Request path: `ChatInterface` → `POST /api/v1/ai/chat` (optionalAuth) → `IntelligenceEngine` (10s→`AI_SERVICE_TIMEOUT_MS` configurable) → `POST :8000/orchestrate` → `safety_guard.check_input` → `model_router.NexusBrain.respond` → language detect → intent classify → route:
- **Deterministic handlers** (GREETING/THANKS/FAREWELL/IDENTITY/CAPABILITY): hardcoded trilingual templates — labeled `DETERMINISTIC_HANDLER`, never neural.
- **Tool** (`try_math_tool`): deterministic arithmetic incl. Bengali digits/word problems — labeled `TOOL`.
- **Specialists** (MATH→core-03, REASONING→core-02, KNOWLEDGE→core-04): registry-validated neural — labeled `NEURAL_MODEL`.
- **Primary/fallback neural** (core-01 → nexus-medium): labeled `NEURAL_MODEL`.
- **Fallback**: honest trilingual "can't answer" — labeled `FALLBACK`.
- **Safety guard**: input injection/harm screen; output rejects markup leaks, degenerate repetition, no-linguistic-content, and (fixed) Latin-prose-for-Bengali-input via letter-ratio rule.
- **Provenance**: `response_source`/`model_used`/`neural_ran`/`rejection_reason` flow API→UI badge.

## Part 4 — Actual model verification (runtime evidence)
| ID | Architecture | Params (measured) | Checkpoint | Tokenizer | Evidence |
|---|---|---|---|---|---|
| nexus-core-01 | Core-01 Transformer | 8,842,560 | checkpoints_core01_run3 (LFS, sha ad515c…) | sp_bpe_8k (8k vocab) | strict load PASS, generates |
| nexus-medium | MediumTransformer | 2,452,544 | checkpoints_medium/final_model.pt | sp_bpe_8k | loads 0.6s |
| nexus-core-02 | nexus_sft | 20,347,712 (measured) | checkpoints_core02_sft_v2 | sp_bpe_8k | registry available |
| nexus-core-03 | nexus_sft | 8,842,560 (measured) | checkpoints_core03_sft_v2 | sp_bpe_8k | registry available |
| nexus-core-04 | nexus_sft | 33,419,072 (measured) | checkpoints_core04_sft_v3 (sha e46383…) | sp_bpe_8k | **live generate 4.6s**, provenance `neural_generation_executed:true`, ckpt+tokenizer SHA256 recorded |

All five `runtime_status: available`; hash+tokenizer validated at load; strict state-dict loading; `weights_only=False` only for trusted local medium ckpt (documented).

## Part 5 — External AI API audit — **VERDICT: VERIFIED**
- **Static:** zero openai/anthropic/gemini/cohere/mistral/etc. in `apps/`, `packages/` runtime source; zero non-local outbound `fetch` in api/ml-service; pnpm-lock clean of AI SDKs.
- **Deps:** `requirements.txt` = torch/numpy/fastapi/uvicorn/pydantic/psutil/multipart/sentencepiece — all permitted infra.
- **Dev-only:** `data/.venv` contains HF `datasets` lib used solely by offline corpus-acquisition scripts (training data, not inference); `acquire_*.py` scripts reference HF dataset IDs — training-time only, never in request path.
- **Runtime network:** ML binds 127.0.0.1:8000, no outbound AI calls; API→ML is localhost only; Neon/AWS = infra, not AI.
- **Scope note:** audit covers repo source, manifests, lockfile, and observed runtime paths — VERIFIED for this scope.

## Part 6 — AI quality evaluation (21 prompts, live `/orchestrate`, saved `eval_reports/final_quality_eval.json`)
Honest scores (0–5, neural outputs only):
- **Identity/capability (A1–A3):** deterministic, correct (Hasibul, independent, honest limitations) — n/a neural.
- **Bengali open-ended (B1–B3, D1–D2, E1–E3, F1–F3, H1–H2):** mostly honest FALLBACK after neural rejection; a few wrong-but-fluent NEURAL_MODEL outputs (B1, C1-mixed).
- **English knowledge (C1–C2):** core-04 produced fluent but factually wrong/mixed-language text labeled NEURAL_MODEL — guard exempts English input; semantic wrongness undetectable cheaply.
- **Reasoning/error-recognition (E,F):** no genuine reasoning evidence — fallback or gibberish.
- **Conversation (G1–G2):** core-01 produced off-topic English fragments labeled NEURAL.

**Neural quality ≈ 1–2/5.** Correct inference ≠ intelligent output. Deterministic/tool paths are accurate. This is a model-capability limitation requiring future training — explicitly not claimed fixed.

## Part 7 — Root cause & remediation (this + prior missions, all verified)
| Issue | Root cause | Fix | Status |
|---|---|---|---|
| CSRF ::1 bypass | `&&`/`||` precedence | parenthesized + non-prod scoping | FIXED AND VERIFIED |
| Context dict leak | no key eviction | `_ctx_append` 500-cap | FIXED AND VERIFIED (600-insert test) |
| Language-guard digit hole | any `\d` exempted prose | letter-ratio rule | FIXED AND VERIFIED (live+matrix) |
| 166 vitest failures | async `buildApp()` not awaited + missing COOKIE_SECRET + CSRF test-env | 32 awaits, test env, localhost non-prod | FIXED AND VERIFIED (203/203) |
| Fake logout on transient failure | `getSession` any-nonOK→false; catch→setUser(null) | 401/403-only + preserve-on-error | FIXED, VERIFICATION PARTIAL (live-auth blocked) |
| Unbounded AI fetch / cancel-error | no timeout; AbortError→error bubble | 60s timeout + cancel distinction | FIXED AND VERIFIED |
| Stale a11y test | removed onboarding UI | rewritten to current contract | FIXED AND VERIFIED |
| Cold-start timeout | fixed 10s vs slow loads | `AI_SERVICE_TIMEOUT_MS` | FIXED AND VERIFIED |

## Part 8 — Regression results (this run)
- `pnpm test` (vitest, 8 files): **203 PASS / 0 FAIL**
- `test_phase1_stabilization.py`: **44/44** · `test_generation_repairs.py`: **13/13**
- api + web `tsc --noEmit`: clean
- Browser: desktop + mobile guest chat PASS, badges render, no page errors
- BLOCKED: authenticated write-path lifecycle (Neon no-write rule)

## Part 9 — Security & data integrity
Auth/session/CSRF verified at code+test level; live rejection paths verified; no secrets in diffs; `.env` untouched; checkpoints/tokenizer/datasets byte-identical; no destructive DB ops; no synthetic accounts written.

## Part 10 — Remaining blockers
1. Neon isolated test DB absent → authenticated lifecycle unverifiable without approval.
2. Neural quality low — needs future training (out of scope).
3. English-input guard gap: fluent-but-wrong neural output passes (semantic limitation).
4. Host RAM ~1GB free → dev-server OOM intermittent (environmental).

## Part 11 — GitHub readiness
Branch main, HEAD 2c475ad. 54 staged untrackings + 20 modified + reports — all verified, secrets clean, backups intact (`nexusai_phase1_backup_20261119`, `nexusai_backup_20261118_postfix`).

## Part 12 — Final verdict: **READY FOR GITHUB COMMIT/PUSH APPROVAL**
Evidence: all tests green, live services verified, AI independence proven, honest limitations documented, no blockers to code delivery. Neural quality is a known, documented limitation — not a delivery blocker.
