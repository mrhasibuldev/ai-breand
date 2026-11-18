# NexusAI — Full Project Forensic Audit (STAGE A)

**Date:** 2026-11-17 · READ-ONLY · repo `mrhasibuldev/ai-breand` · branch state: dirty (8 modified, many untracked)

## 1. Repository & git state
- remote: `https://github.com/mrhasibuldev/ai-breand.git`
- HEAD: `a8cc48b` (Run4 GPU infra + Run3 ckpt via LFS)
- **8 modified files uncommitted** (main.py, inference.py, model_config.py,
  pretraining_driver.py, current.json, README, COLAB cell, pyc) + ~100+ untracked
  docs/backups/audit files — large uncommitted surface before release
- Stack: pnpm monorepo — apps/{api,web,worker}, packages/* (18 pkgs),
  Python ai-core (FastAPI ml-service, core01, models)

## 2. Component inventory (verified status)

| component | path | status |
|---|---|---|
| Core-01 model | `core01/transformer.py` NexusAICore01 | **VERIFIED** (strict load, gen) |
| Core-01 inference | `core01/inference.py` | VERIFIED (post-fix) |
| Core-01 tokenizer | SentencePiece bpe_8k | VERIFIED (hash+roundtrips) |
| Training driver | `core01/pretraining_driver.py` + training.py | VERIFIED (Run4 completed) |
| Run4 checkpoint | Drive `NEXUSAI_RUN4/checkpoint_final.pt` sha `761a5b14…` | **VERIFIED** (Colab CPU) |
| Run3 checkpoint | `models/checkpoints_core01_run3/` sha `ad515cad…` | VERIFIED (local) |
| ML service | `ml-service/main.py` FastAPI :8000 | VERIFIED live (orchestrate/inference/metrics/eval) |
| Model registry | `ml-service/model_registry.py` | VERIFIED (validate/load/strict) |
| Model router/brain | `model_router.py` | VERIFIED (routes+labeled deterministic) |
| Safety guard | `ml-service/safety_guard.py` | VERIFIED (injection/harm/output) |
| Monitoring | `/metrics` + jsonl + `/eval/run` | VERIFIED |
| SFT dataset v2 | `data/sft_v2/` 103 rec | VERIFIED (leakage 0) |
| SFT masking | `core01/sft_dataset.py` | VERIFIED tensors |
| Run5 SFT cell | `docs/notebooks/COLAB_..._PREPARATION.py` | syntax OK, preflight NOT RUN |
| Medium model | `checkpoints_medium/` 2.47M | fallback only, weak |
| Small checkpoints | `checkpoints/checkpoint_epoch_*` | EXCLUDED (tok-incompatible) |
| Web app | `apps/web` Next.js | IMPLEMENTED, NOT VERIFIED this session |
| API | `apps/api` | IMPLEMENTED, NOT VERIFIED (port 4000 down earlier) |
| Memory/agent/knowledge pkgs | packages/* | PARTIALLY IMPLEMENTED (not audited deeply) |

## 3. Core-01 → Core-04 verdict
| model | reality |
|---|---|
| **Core-01** | REAL — only production neural model. Run3 serving, Run4 verified-Drive |
| **Core-02** | **NOT IMPLEMENTED** — docs/roadmap only |
| **Core-03** | **NOT IMPLEMENTED** — docs only |
| **Core-04** | **NOT IMPLEMENTED** — docs only |
Registry has 2 entries: `nexus-core-01` + `nexus-medium` (fallback, NOT a Core-0X). Multi-model routing exists but only 1 real model → "multi-model" is aspirational.

## 4. Verified capabilities (evidence)
- Run4: ckpt sha+size, weights_only=True+allowlist, strict load 0/0,
  CPU gen 11/11 prompts, tok roundtrips, hashes unchanged — **PASS**
- Run3 via service: `/orchestrate` neural route, `/model/status` 8.84M,
  `/inference` real output — **PASS**
- Quality: Run3 gibberish; Run4 poor-but-nonzero (5/11 empty) — **FAIL quality**
- Reasoning: not demonstrated — arithmetic/story noise only
- SFT: dataset+masking verified; **training NOT done**

## 5. Security/release risks
- `.env` present in repo root (edited earlier) — MUST exclude
- `checkpoints/*.pt` binaries, `node_modules/`, `dist/`, `__pycache__`,
  `data/.venv/`, `eval_reports/`, `hybrid-test-cookies.txt` — exclude
- Run4 ckpt is Drive-only (not in repo) — LFS policy decision needed
- ~100 untracked audit/report .md files — decide include vs exclude
- No LICENSE file seen — needed for public release
- Secrets scan required before push (keys in docs/scripts?)

## 6. Gap report (priority)
- P0: none blocking release of SOURCE (no secrets found yet — scan pending)
- P1: Core-02/03/04 absent (document as roadmap, don't fabricate)
- P1: conversational quality poor → SFT Phase F pending
- P2: val split tiny (5); eval heuristic-only
- P2: API/web unverified end-to-end
- P3: docs sprawl (~40 root-level report .md files) — organize

## STAGE A COMPLETE — AUDIT REPORT DELIVERED
Next: STAGE B (per-model verification — only Core-01+medium testable).
Awaiting direction; no changes made.