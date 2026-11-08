# NexusAI Core-01 — Final Pilot Evidence Review

**Date:** 2026-11-09 · **Mode:** READ-ONLY · No training, no file modification, no push.

## 1. GPU Smoke Test log — ⚠️ PARTIALLY VERIFIED

| Item | Status | Evidence |
|---|---|---|
| GPU model / VRAM | user-reported: T4, ~15.64 GB | **NOT VERIFIED locally** — need `audit_reports/core01_smoke_*.json` from Drive |
| FP16 fwd/bwd, loss 9.0215, optimizer step | user-reported PASS | same — report file needed |
| Driver rc=0, ckpt create + strict reload | user-reported PASS | same |
| Resume (step detected, +1 step) | user-reported PASS | same |
| Final summary | `SMOKE TEST PASSED` | user-reported |

**To fully verify:** download `MyDrive/NexusAI/audit_reports/core01_smoke_<ts>.json` (and `.txt`) and share/paste — I will cross-check every field against claims.

## 2. English dataset — ✅ FULLY VERIFIED LOCALLY

`packages/ai-core/data/english_first/`:

| Check | Result |
|---|---|
| SHA-256 of all 3 files | **MATCH manifest** |
| File sizes | **MATCH manifest** |
| Counts | train 61,960 / val 958 / test 958 — exact |
| Tokens (real spm) | 7,214,029 / 106,224 / 108,486 = **7,428,739 total** |
| **Overlap train∩val∩test** | **0 / 0 / 0 — ZERO leakage** (independently recomputed) |
| Bengali chars in train sample | 0/5000 docs |
| Driver `load_texts` compat | 61,960 docs load ✅ |

## 3. 100M FineWeb corpus on Drive — ⚠️ NOT VERIFIED

Cannot access Drive from local. Known historically: 100,499,546 tokens, overlap=0 (Kaggle prep). **Current Drive state unknown** — run `COLAB_DATASET_AUDIT_CELL.py` to get real counts/hashes/leakage before relying on it.

## 4. Readiness plan review

Proposed pilot (from `NEXUSAI_CORE01_FULL_TRAINING_READINESS_PLAN.md`):
- device cuda / fp16 / bs16×accum2 (eff 32) / seq512 / lr3e-4 / warmup500 / ckpt+eval 500
- **VRAM est. ~6–9 GB** of 15.64 — smoke probe showed only 0.30 GB at bs2×256, so real usage unknown → **measured 50–100 step trial first**
- **Success criteria:** finite decreasing loss, val_loss finite, no NaN, stable VRAM, ckpt save+reload, resume works
- **Failure criteria:** OOM, NaN loss, grad explosion, ckpt corruption → stop, reduce bs, report
- Max steps for pilot: suggest `--max-steps 500` first measured trial (not full 6k)

## 5. Scope safety

- Pilot uses ONLY `english_first/` or Drive 100M corpus via `--train-file`
- Bengali/Banglish data untouched (preserved in repo)
- Existing checkpoints untouched (separate `checkpoints_pilot/` dir)
- No architecture/tokenizer changes

## 6. Evidence gaps — clearly marked

| Claim | Status |
|---|---|
| Smoke test PASSED on T4 | user-reported — **awaiting report JSON for full verification** |
| 100M corpus exists on Drive now | **NOT VERIFIED** |
| 100M corpus quality/leakage current | **NOT VERIFIED** (audit cell ready) |
| bs16×512 fits T4 | **NOT VERIFIED** — needs measured trial |
| Bengali readiness | **NOT READY** (data absent) |

## Final gate

Dataset (local English-first): **VERIFIED READY**
Smoke test: **user-reported PASS, awaiting artifact for full verification**
100M corpus: **NOT VERIFIED**
Pilot: **NOT STARTED — awaiting your explicit approval + smoke report artifact**
