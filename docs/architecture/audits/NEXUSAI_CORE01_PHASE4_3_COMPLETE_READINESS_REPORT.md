# NEXUSAI CORE-01 — PHASE 4.3 COMPLETE READINESS REPORT

**Date**: 2026-11-06
**Type**: PRE-TRAINING READINESS — safe fixes + verification only. No downloads, no training, no GPU sessions, no uploads.
**Verdicts**: VERIFIED / FIXED AND TESTED / NOT VERIFIED / BLOCKED / REQUIRES OWNER ACTION

---

## 1. EXECUTIVE SUMMARY

- One real pipeline gap found and fixed: **SFT had no response-only loss masking** → `InstructionDataset(mask_prompt=True)` added, mathematically verified.
- Phase 4.2.2 corrections independently re-verified (12/12).
- Checkpoint/resume: reliable for model+opt+sched+step+RNG+tokenizer_path; **DataLoader shuffle order is NOT checkpointed** — approximate resume only (documented, not silently claimed exact).
- Kaggle diagnostic notebook created (`docs/notebooks/kaggle_core01_gpu_diagnostic.ipynb`) — synthetic only, no training.
- Training package manifest created. Kaggle guide updated.
- **Model remains UNTRAINED. No real checkpoints exist.**
- **Verdict: READY for owner-approved Kaggle GPU diagnostic.**

## 2. GIT BASELINE

**Before**: `main @ 06a5070`; modified `core01/__init__.py`, `core01/training.py`, `model_config.py`, `ml-service pyc` (pre-existing); untracked `data/`, audit docs, `docs/guides/`.
**After**: same + `core01/dataset.py` modified; new `docs/notebooks/`, `NEXUSAI_CORE01_TRAINING_PACKAGE_MANIFEST.md`, this report.
**Backups**: `/tmp/phase422_backup/` (training.py, model_config.py from Phase 4.2.2).

## 3. PHASE 4.2.2 CORRECTION RE-VERIFICATION — FIXED AND TESTED

| Check | Result |
|---|---|
| 8b/accum3, 7b/accum3, 2b/accum3, 6b/accum3, 4b/accum2 group gradients vs independent mean | allclose, maxdiff ≤7.5e-9 — VERIFIED |
| Optimizer steps = ceil(groups) | VERIFIED |
| Scheduler steps = optimizer steps | VERIFIED (3==3) |
| No gradient reuse between groups (zero_grad at group start) | VERIFIED by inspection + tests |
| SFT engine identical logic | VERIFIED (same code pattern) |
| tokenizer_path: config field, engine arg, checkpoint save, load warning, old-ckpt compat | VERIFIED 12/12 |

## 4. NEW FIX THIS PHASE — SFT RESPONSE-ONLY LOSS — FIXED AND TESTED

**Original issue**: `InstructionDataset` concatenated `instruction + response` and computed loss over ALL tokens — the model would be trained to reproduce the prompt, not just learn to answer.

**Correction**: `mask_prompt: bool = False` param added to `InstructionDataset.__init__`. When True, instruction/response are encoded separately (`[BOS] instr resp [EOS]`), and target positions predicting instruction tokens are set to `pad_id` — which `F.cross_entropy(ignore_index=pad_id)` already ignores. Transformer untouched. Default False = exact old behavior (backward compatible).

**Tests** (`test_phase43.py`, 14/14 PASS):
- prompt positions == pad_id ✓
- real targets == response tokens + EOS exactly ✓
- targets == shifted token sequence with masked prefix ✓
- old joint format unchanged when mask_prompt=False ✓
- truncation edge keeps ≥1 real target ✓
- pretraining next-token shift correct (input=ids[:-1], target=ids[1:]) ✓
- split_dataset: 80/10/10, no overlap, deterministic seed ✓

**Recommendation for SFT stage**: use `mask_prompt=True`.

## 5. CHECKPOINT & RESUME RELIABILITY

| State | Saved? | Restored? | Status |
|---|---|---|---|
| Model weights | ✓ | ✓ bit-identical | VERIFIED |
| Optimizer state | ✓ | ✓ | VERIFIED |
| Scheduler state | ✓ | ✓ | VERIFIED |
| Epoch / global step | ✓ | ✓ | VERIFIED |
| Config (incl. precision, accum, tokenizer_path) | ✓ | via to_dict | VERIFIED |
| Python/NumPy/torch CPU/CUDA RNG | ✓ | ✓ | VERIFIED |
| Tokenizer path | ✓ | warning if absent | FIXED AND TESTED |
| **DataLoader shuffle/sampler order** | ✗ | ✗ | **NOT VERIFIED — approximate resume only** |
| Atomic write (.tmp→replace) | ✓ | — | VERIFIED |
| Interrupted-save safety | backup rename + atomic | — | VERIFIED |

**Resume limitation (honest)**: `DataLoader(shuffle=True)` order depends on torch RNG at iterator creation. RNG state IS restored, so with `num_workers=0` and identical code the order is *practically* reproducible, but it is **not guaranteed bit-exact** across PyTorch versions/GPU environments. For strict determinism, `shuffle_train=False` can be used. Dataset content changes between save/resume will shift batches — expected.

**Security**: `weights_only=False` retained ONLY in `CheckpointManager.load_checkpoint` for self-produced checkpoints (NumPy RNG state requires it). Never load foreign `.pt` files — pickle RCE risk documented in code comment.

## 6. TRAINING PIPELINE VERIFICATION

| Component | Status |
|---|---|
| Causal LM (next-token, no future leak) | VERIFIED — `input=ids[:-1]`, `target=ids[1:]`, tril mask, test confirms |
| Padding handling | VERIFIED — pad_id ignored in loss; padding_idx in embedding |
| Attention mask | causal + optional padding mask path inspected |
| Loss | `F.cross_entropy(ignore_index=pad_id)` VERIFIED |
| Train/val/test separation | `split_dataset` deterministic, no overlap VERIFIED; leakage prevention = manual dedup at corpus build (future) |
| SFT gating | SFT engine exists separately; **nothing prevents running it on random weights — operationally gated by process (pretrain first), not code-enforced**. Documented; inference engine refuses generation while UNTRAINED. |
| UNTRAINED safeguard | inference returns warning + empty output for UNTRAINED — VERIFIED earlier |

## 7. MIXED PRECISION / T4 COMPATIBILITY — code-verified, hardware NOT TESTED

- fp16: autocast + GradScaler, unscale→clip→step→update order correct — VERIFIED (code)
- bf16: gated by `torch.cuda.is_bf16_supported()`; **T4 (Turing sm_75) lacks bf16 → auto-falls back to fp16** — correct-by-design
- accum + AMP + clipping interaction: correct order in both engines
- CPU fallback: `use_amp=False`, FP32 — TESTED
- OOM handling: none implemented — batch size must be found by benchmark (Part 9)
- Checkpoint under AMP: state_dicts are FP32 master weights — portable — VERIFIED by design

## 8. KAGGLE READINESS — REQUIRES OWNER ACTION

- Diagnostic notebook: `docs/notebooks/kaggle_core01_gpu_diagnostic.ipynb` — 9 cells, synthetic only, asserts param count, tests FP32+FP16 step, bf16 capability, checkpoint round-trip, 10-step throughput probe.
- Guide updated with §9b (notebook usage). No credentials requested; quotas noted as changeable.
- Package manifest: `NEXUSAI_CORE01_TRAINING_PACKAGE_MANIFEST.md` — exact file list + Kaggle layout.

## 9. DATASET & LICENSE READINESS (from Phase 3.1 — unchanged, no downloads)

| Dataset | Source | License | Status |
|---|---|---|---|
| B-CORE subset | HF nahid-hub/B-CORE | CC BY 4.0 | approved experimental; attribution required; component-level sources may add terms — NOT legal clearance |
| IndicTalk bn | HF LingoIITGN/IndicTalk | CC BY 4.0 | approved experimental |
| alpaca_chat_bangla | HF Mahadih534 | CC-BY-2.0 | approved experimental |
| GSM8K | openai/gsm8k | MIT | approved |
| Ayon128 Banglish-English | HF Ayon128 | MIT | approved experimental |
| Dolly 15K (optional) | databricks | CC BY-SA 3.0 | conditional — share-alike obligations |
| Project data (phase9/10 etc.) | local | owned | usable; `knowledge/` EXCLUDED always |

Rejected (verified): Alpaca raw (NC), dailydialogue_bn (NC-SA), XL-Sum (NC-SA), bangla-alpaca-orca (GPL-3.0), Bangla-SFT-50k (unclear).

**Leakage plan (future corpus build)**: dedup exact+near-dup, language-ID, split 90/5/5 train/val/test BEFORE token-counting, keep parallel translation pairs out of both train and eval of the same item, manifest records source+license per file.

## 10. RESOURCE & TRAINING CONFIG

- Local: 4 CPU, ~1.8GB free RAM, 4.2GB disk — **cannot train locally** (VERIFIED).
- Kaggle T4 16GB: est. VRAM need ~3-4.5GB @ batch16 seq512 FP32, ~2-2.5GB FP16 — fits with headroom (ESTIMATED).
- Throughput: UNKNOWN until notebook Cell 9 measures tokens/sec — previous 8-15h figure treated as unverified estimate only.
- Benchmark-first plan: synthetic batch → measure tok/s + peak VRAM → scale batch → extrapolate epoch time.

## 11. TESTS EXECUTED THIS PHASE

| Suite | Command | Result |
|---|---|---|
| Phase 4.2.2 corrections | `python %TEMP%/test_phase422.py` | 12/12 PASS |
| Phase 4.2 safety | `python %TEMP%/test_phase42.py` | 23/23 PASS |
| Phase 4.3 new (SFT mask, splits, shift) | `python %TEMP%/test_phase43.py` | 14/14 PASS |
| Core-01 regression | `python test_core01.py` | 9/9 PASS |
| **Total** | | **58/58 PASS** |

All CPU-only, synthetic/in-memory, temp dirs. No GPU test run (impossible locally — CUDA unavailable).

## 12. FINAL VERDICTS

| Question | Verdict |
|---|---|
| Core-01 ready for controlled GPU diagnostic? | **YES — READY** |
| Phase 4.2.2 corrections verified? | **FIXED AND TESTED** |
| Checkpoint/resume reliable? | **YES for state; approximate for data order** |
| Pretraining pipeline verified? | **VERIFIED (CPU/synthetic)** |
| SFT gated behind pretraining? | **Process-gated only — documented, not code-enforced** |
| Kaggle diagnostic notebook ready? | **YES — owner must run it** |
| Model still UNTRAINED? | **YES — no real checkpoints exist** |

## 13. REMAINING BLOCKERS / OWNER ACTIONS

1. **REQUIRES OWNER ACTION**: run `kaggle_core01_gpu_diagnostic.ipynb` on Kaggle (GPU T4 x2, internet on) — verifies real fp16/GradScaler/VRAM/throughput.
2. **REQUIRES OWNER ACTION**: approve dataset download list (Phase 4 report) — downloads happen ON Kaggle, not locally.
3. **REQUIRES OWNER ACTION**: approve training config after diagnostic numbers arrive.
4. Optional fix later: code-enforce SFT-requires-pretrained-checkpoint guard.
5. Optional: deterministic sampler for bit-exact resume.

**STOP — awaiting owner review and explicit approval before any Kaggle session, upload, download, or training.**
