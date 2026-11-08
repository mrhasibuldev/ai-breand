# NEXUSAI CORE-01 — PHASE 4.3.1 FINAL SAFETY REPORT

**Date**: 2026-11-06
**Type**: CONTROLLED CORRECTIVE PHASE — SFT gate + masking validation + checkpoint hardening. No training/GPU/downloads/uploads.

---

## 1. EXECUTIVE SUMMARY

- **SFT pretraining gate: now CODE-ENFORCED** — `InstructionTuningEngine` refuses to initialize without a validated pretrained checkpoint. 10/10 gate tests pass.
- **Response-only masking: mathematically verified** against an independent manual reference across 4+ edge cases.
- **Real reliability bug found & fixed**: failed checkpoint save previously destroyed the last good checkpoint (rename-then-write). Now non-destructive `copy2` backup + atomic `os.replace`. Proven by simulated disk-full test.
- Resume remains **epoch-granular approximate** — sampler state not checkpointed (documented limitation, not claimed exact).
- **77/77 tests pass** across all suites. Param count 8,842,560 unchanged. Model UNTRAINED.

## 2. GIT BASELINE

**Before**: `main @ 06a5070`; modified `core01/{__init__,dataset,training}.py`, `model_config.py`, ml-service pyc; untracked docs/data/notebooks.
**After**: same files modified further (`training.py`, `__init__.py`) + this report. No commit/push.
**Backups**: `/tmp/phase422_backup/training_pre431.py`, `dataset_pre431.py` (pre-4.3.1 copies).

## 3. ISSUE-BY-ISSUE

### ISSUE A — SFT ran on random weights (process-gated only)

**Root cause**: `InstructionTuningEngine.__init__` accepted any model with no proof of pretraining.

**Fix** (`core01/training.py`):
- New `PRETRAINED_STATUSES` = {PRETRAINING_COMPLETED, INSTRUCTION_TUNING_IN_PROGRESS, INSTRUCTION_TUNING_COMPLETED, PRODUCTION_READY}. Rejects UNTRAINED, RANDOMLY_INITIALIZED, PRETRAINING_IN_PROGRESS.
- New `validate_pretrained_checkpoint(path, config)` — checks: file exists → readable dict → non-empty tensor `model_state_dict` → `model_status` in allowed set → `config` metadata present → 6 architecture fields match (vocab/d_model/layers/heads/d_ff/max_len) → 4 special-token IDs match → returns data.
- `InstructionTuningEngine.__init__(..., pretrained_checkpoint=None)` — `None` → ValueError; valid path → `model.load_state_dict(strict=True)` loads pretrained weights before optimizer creation. Strict load catches residual arch mismatch.
- Old checkpoints without `config` metadata → **rejected** under documented strict-metadata policy (cannot prove compatibility).
- Exports added to `core01/__init__.py`.

**Tests** (`test_phase431.py`, all PASS):
| Case | Result |
|---|---|
| No checkpoint arg | ValueError ✅ |
| Nonexistent path | FileNotFoundError ✅ |
| UNTRAINED status | ValueError ✅ |
| PRETRAINING_IN_PROGRESS | ValueError ✅ |
| Arch mismatch (vocab 9000) | RuntimeError on strict load ✅ |
| Missing config metadata | ValueError ✅ |
| Special-token mismatch | ValueError ✅ |
| Valid PRETRAINING_COMPLETED | accepted + weights loaded ✅ |

### ISSUE B — Response-only masking needed deep validation

**Verification** (not just "some labels are pad"): built `ref_targets()` — an independent manual construction `[BOS]+instr+resp+[EOS]` with prompt targets zeroed — and compared `input_ids`/`targets` tensors exactly.

| Case | Result |
|---|---|
| short instr / short resp | exact match ✅ |
| long instr / short resp | exact match ✅ |
| special chars | exact match ✅ |
| empty response | EOS target preserved ✅ |
| instruction > max_len (truncated) | ≥1 real target kept ✅ |
| response > max_len (truncated) | prompt masked, response kept ✅ |
| mask_prompt=False | byte-identical to old joint format ✅ |

Alignment proof: `targets[t]=token_ids[t+1]`; response tokens begin at index `len(instr_ids)+1`, so masking `targets[:len(instr_ids)]` removes exactly the instruction-prediction positions; EOS always survives (clamped `min(k, len-1)`).

### ISSUE C — Failed checkpoint save destroyed previous checkpoint

**Root cause**: `save_checkpoint` did `os.rename(old → .backup)` BEFORE `torch.save`. If save failed (disk full, kill), the good checkpoint existed only as `.backup`.

**Fix**: `shutil.copy2` backup (non-destructive) + write `.tmp` + `os.replace` atomic overwrite. Original stays valid until the atomic swap succeeds.

**Test**: simulated `torch.save` raising `OSError` → previous `good.pt` byte-identical afterward, no `.tmp` leftover. ✅

### ISSUE D — DataLoader/sampler resume state

**Assessment**: exact mid-epoch batch-position restoration is **not practical** without a custom sampler + iterator checkpoint (significant complexity, no DDP need). Epoch-level checkpoints + full RNG restore give *practically reproducible* order with `num_workers=0`, but **bit-exactness is NOT guaranteed** across PyTorch versions/GPU environments. **Status: NOT VERIFIED as exact — documented limitation retained.** Safe approximate resume preserved.

## 4. FILES CHANGED

- `packages/ai-core/core01/training.py` — gate + validator + backup fix
- `packages/ai-core/core01/__init__.py` — new exports
- (dataset.py unchanged this phase — masking verified as-is)

## 5. NOTEBOOK VERIFICATION

`docs/notebooks/kaggle_core01_gpu_diagnostic.ipynb` inspected: synthetic `torch.randint` data only, no training loop, asserts `params==8,842,560`, tests FP32+FP16 autocast+GradScaler step, bf16 capability, checkpoint save/load round-trip, 10-step throughput probe, prints peak VRAM. Uses `PretrainingEngine` only → unaffected by new SFT gate. **READY for owner to run manually.**

## 6. TEST COMMANDS & RESULTS

| Command | Result |
|---|---|
| `python -m py_compile core01/training.py core01/__init__.py` | PASS |
| `python %TEMP%/test_phase431.py` | **19/19 PASS** |
| `python %TEMP%/test_phase422.py` (updated for gate) | 12/12 PASS |
| `python %TEMP%/test_phase42.py` | 23/23 PASS |
| `python %TEMP%/test_phase43.py` | 14/14 PASS |
| `python test_core01.py` | 9/9 PASS |
| **Total** | **77/77 PASS** |

## 7. FINAL ANSWERS

- **SFT technically blocked until valid pretrained checkpoint?** YES — code-enforced, 10 rejection/acceptance paths tested.
- **Response-only masking mathematically verified?** YES — exact tensor match vs independent reference.
- **Checkpoint recovery reliable?** YES for state; failed-write now provably safe.
- **Exact-resume limitations?** Sampler/batch-position not checkpointed → approximate (documented).
- **All regression tests passing?** YES — 77/77.
- **Kaggle notebook ready for manual owner run?** YES.
- **Core-01 still UNTRAINED?** YES — no real checkpoints, param count 8,842,560.

## 8. REMAINING OWNER ACTIONS — REQUIRES OWNER ACTION

1. Run diagnostic notebook on Kaggle (GPU T4 x2).
2. Approve dataset download list.
3. Approve training config after measured throughput.
4. (Optional future) deterministic sampler for bit-exact resume; SFT data pipeline (instruction/response JSONL → InstructionDataset).

**STOP — awaiting owner review. No training, downloads, uploads, GPU sessions, commits, or pushes performed.**
