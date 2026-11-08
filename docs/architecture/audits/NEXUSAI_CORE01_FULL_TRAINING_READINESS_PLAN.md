# NexusAI Core-01 — Full Training Readiness Plan

**Date:** 2026-11-08 · **Status: PLAN ONLY — no training authorized.**

## 1. Prerequisite repairs (blocking)

| # | Item | Status |
|---|---|---|
| 1 | `pretraining_driver.py`: `.to(device)` fix | ✅ **APPLIED + CPU-verified** (2026-11-08) |
| 2 | Commit repaired transformer.py + driver fix + notebooks | pending owner approval |
| 3 | Drive dataset audit cell run (`COLAB_DATASET_AUDIT_CELL.py`) | **prepared — awaiting Colab execution** |
| 4 | Bengali/Banglish data phase | separate project phase — **NOT READY** |

## 2. Verified training mechanics (code + tests)

- ✅ Causal mask, padding/key mask (fixed), next-token shift, `ignore_index=pad`
- ✅ AdamW + warmup-only scheduler + grad clip 1.0
- ✅ Grad accumulation: correct per-group mean (Phase 4.2.2)
- ✅ FP16 AMP + GradScaler on CUDA; bf16 correctly unavailable on sm_75
- ✅ Eval does not update params; val_loss computed properly
- ✅ Checkpoint: atomic write + .backup + model/opt/scheduler/RNG/scaler/tokenizer/status
- ✅ Resume: restores all state; verified CPU e2e (step2→4)
- ✅ Seed reproducibility (python/numpy/torch/cuda)
- ✅ Drive-persisted checkpoints survive Colab disconnect

## 3. Resource configurations (T4 15.64 GB)

| Config | batch×accum | est. VRAM | est. steps (98.5M tok) | Notes |
|---|---|---|---|---|
| **Conservative** | 8×2 (=16) | ~3–5 GB | ~12k | safest start |
| **Medium** | 16×2 (=32) | ~6–9 GB | ~6k | recommended after probe |
| **Higher** | 32×1 (=32) | ~10–13 GB | ~6k | risk OOM; only if probe shows headroom |

**Do NOT trust smoke 0.30 GB** — that was bs2×256 synthetic probe; real run uses seq512 + dataloader + optimizer states. Measure in a **short measured trial** (e.g., 50–100 steps) before committing to long run.

## 4. Recommended sequence

1. Apply driver `.to(device)` fix → verify
2. Dataset audit cell on Drive corpus
3. **Short measured trial**: `--max-steps 100`, chosen config → record tok/s, peak VRAM, loss trend
4. If stable → owner approves full run
5. Full run with ckpt every 500, eval every 500, logs to Drive
6. Post-training: evaluation cell + checkpoint validation + final report

## 5. Risks

| Risk | Mitigation |
|---|---|
| OOM at bs16×512 | start conservative; trial first |
| Colab disconnect | ckpts on Drive + `--resume` |
| Loss NaN/explode | grad clip + warmup + monitor; abort if NaN |
| Bengali quality poor | separate data phase (honest gap) |
| "PRETRAINING_COMPLETED" on tiny data | only trust after real corpus + eval |

## Status: `NOT READY` — dataset audit execution + measured trial remaining (device fix DONE)
