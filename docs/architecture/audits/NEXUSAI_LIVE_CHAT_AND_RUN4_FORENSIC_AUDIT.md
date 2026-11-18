# NexusAI Live Chat & Run4 Forensic Audit

**Date:** 2026-11-17 · LIVE stack: web:3000 / api:4000 / ml:8000 · READ-ONLY · 15-prompt live suite via real `/api/v1/ai/chat`

## A. Executive Summary
Website chat answers come from **three honest, labeled sources**:
deterministic handlers (greetings/identity/capability/math-tool), genuine
Core-01 **Run3** neural generation, and a labeled fallback. **Run4 is used
NOWHERE** — exists only on Google Drive: not copied, not registered, not
loaded. Neural outputs are real model generations but semantically weak.
No external AI anywhere in the path.

## B. Verified Request Lifecycle
```mermaid
flowchart TD
  A[Browser chat :3000] -->|POST /api/v1/ai/chat| B[Fastify API :4000<br/>optionalAuth, guest ok]
  B --> C[intelligence-engine.ts<br/>providerAlias='nexusai-python-ml']
  C -->|POST /orchestrate {message,history}| D[FastAPI ML :8000]
  D --> E[model_router.brain.respond]
  E --> F[detect_language_v2 + classify_intent_v2]
  F -->|GREETING/THANKS/FAREWELL/IDENTITY/CAPABILITY| G[deterministic handler<br/>LABELED in trace]
  F -->|MATH + tool match| H[tool:deterministic_math]
  F -->|else| I[registry.generate 'nexus-core-01']
  I --> J[model_registry: validate sha256 →<br/>create_inference_engine → CPU]
  J --> K[InferenceEngine.generate<br/>BOS-only prompt, slice new tokens]
  K --> L[Core-01 Run3 ckpt ad515cade…]
  L -->|text| M{degenerate?}
  M -->|no| N[route=neural:nexus-core-01]
  M -->|yes/empty| O[route=fallback LABELED]
  G & H & N & O --> P[reply: response, provider, latencyMs]
  P --> B --> A
```

## C. Response Source Classification (live-verified)
| Source | Status | Where |
|---|---|---|
| A. Own neural (Core-01) | ✅ real | `route=neural:nexus-core-01`, sha `ad515cade…` |
| B. Deterministic handlers | ✅ labeled | greeting/thanks/farewell/identity/capability |
| C. Template | ✅ (handler text) | labeled, honest |
| D. Cache/DB | ❌ none found | no cache in path |
| E. Fallback | ✅ labeled | `route:"fallback"`, honest message |
| F. External AI | **NONE** | grep clean; alias `nexusai-python-ml` |

## D. Live Chat Test Results (`POST /api/v1/ai/chat`, 15 prompts)
| # | Prompt | Route | Latency | Output (excerpt) |
|---|---|---|---|---|
| 1 | Hello. | deterministic:greeting | 67ms | "Hello! I'm NexusAI…" |
| 2 | Who are you? | registry:identity | 8ms | correct identity |
| 3 | Who created you? | registry:identity | 7ms | correct identity |
| 4 | Explain independent AI model | **neural** | 7872ms | gibberish |
| 5 | What is AI? | **neural** | 1724ms | gibberish |
| 6 | 15 apples − 6 | fallback | 823ms | honest "can't answer" |
| 7 | Why sky blue? | fallback | 2390ms | honest fallback |
| 8 | তুমি কেমন আছো? | **neural** | 1246ms | math-word gibberish |
| 9 | বাংলাদেশের রাজধানী? | **neural** | 1440ms | gibberish |
| 10 | কৃত্রিম বুদ্ধিমত্তা কী? | **neural** | 221ms | "bath is 4x+64=…" |
| 11 | Tumi ki Bangla bujhte paro? | **neural** | 1237ms | gibberish |
| 12 | training vs inference | fallback | 37ms | honest fallback |
| 13 | photosynthesis | **neural** | 241ms | gibberish |
| 14 | learned patterns/knowledge | **neural** | 538ms | gibberish |
| 15 | explain in two steps | **neural** | 103ms | "If), the total of/…" |

Raw outputs preserved: `exports/live_chat_audit_20261117.json`.

## E. Checkpoint & Registry (verified live)
- Registry `nexus-core-01` → `models/checkpoints_core01_run3/checkpoint_final.pt`
- sha256 `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` ✅
- Provenance block captured: `engine=core01, load_s=0.49, vocab=8000, CPU`
- Lazy-loaded ONCE, resident in memory.

## F. Run3 vs Run4 — five states
| State | Run3 | Run4 |
|---|---|---|
| Exists | ✅ local+Git LFS | ✅ Drive only |
| Trained | ✅ verified | reported, hash unverified locally |
| Copied to project | ✅ | ❌ |
| Registered | ✅ | ❌ |
| Loaded by website | ✅ | ❌ |

## G. Language Capability (evidence)
- Tokenizer en/bn/banglish encode/decode: **VERIFIED**
- Neural generation EN: **PARTIAL** (fluent surface, wrong content)
- Neural generation BN: **FAIL** (English/mixed gibberish on BN prompts)
- Banglish: **PARTIAL** (language detected; generation poor)
- Instruction following / reasoning: **NOT DEMONSTRATED**

## H. Root Causes (ranked, evidence-backed)
1. **Run4 not integrated** — registry→Run3 only (PROVEN).
2. **Undertrained** — pretraining only; 216K prose docs, no SFT.
3. **Bengali generation absent** — corpus ~62% EN, BN encyclopedic.
4. **Math word problems → fallback** — tool regex misses phrasing (honest).
5. `config.model_status=UNTRAINED` metadata bug — **NOT blocking**:
   `inference.py:144` restores status from top-level `PRETRAINING_COMPLETED`.
6. Deterministic routes mask neural quality for greetings/identity/math —
   honest labeling, but users see "smart" answers that aren't neural.

## I. Recommended Fix Plan (NOT implemented)
- **P0:** verify Run4 sha in Colab (`761a5b14…`) → copy ckpt to project →
  add registry entry → live provenance re-check. Files: `model_registry.py`.
- **P1:** build conversational SFT dataset (bn/en/banglish) → SFT on Colab →
  new separate checkpoint. Files: new dataset + `training.py` SFT path.
- **P2:** re-run this chat suite + `neural_benchmark_v2` → compare honestly.
- **P3:** scale decision only after measured improvement.
- **P4:** extend math-tool patterns (optional).

## J. What Must Not Change
Run3/Run4 ckpts, tokenizer, datasets, registry (until approved),
architecture, DB, UI, auth — all untouched. No training, no commits, no
external AI used.

## K. Evidence & Limitations
- VERIFIED: request path, routes, provenance, checkpoint sha, CPU inference,
  15 live responses, no external AI.
- HISTORICAL (unverified locally): Run4 existence/hash/loss values — Drive-only.
- BLOCKED: Run4 quality comparison — needs Colab benchmark cell.
- MISSING: pixel-level UI render test (API layer verified instead).

## Provenance Design Review (proposal only)
Current trace is good (route/model/provenance/latency). Add: `request_id`,
`tokenizer_sha256`, `neural_generation_executed`, `deterministic_handler`,
`fallback_used`, `generation_status` (ok/empty/degenerate) — server-side only,
never expose internals to users.

## Verdicts
Connection **PASS** · Neural exec **PASS (Run3)** · Run4 used **FAIL** ·
Quality **PARTIAL** · E2E **PASS** · CPU **PASS** · External AI **NONE**
