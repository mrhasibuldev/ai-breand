# NEXUSAI CORE-01 — CROSS-PLATFORM COMPATIBILITY REPORT

**Date**: 2026-11-06 | **Scope**: packaging + CPU validation only. No GPU activated, no training.

---

## 1. WHAT WAS INCLUDED / EXCLUDED

**Included** (13 files, ~780KB uncompressed): full `core01/` package, `models/nexusai_core_01/` config, 8K SentencePiece tokenizer (`.model` + `.vocab`). See `NEXUSAI_CORE01_KAGGLE_PACKAGE_MANIFEST.md` for per-file SHA-256.

**Excluded**: checkpoints, datasets, `knowledge/`, `.env`, credentials, app code, `__pycache__`, `.venv`, git history. No private or training data.

## 2. VERIFIED FACTS

| Check | Result | Evidence |
|---|---|---|
| Param count | **8,842,560 — exact match** | diagnostic on extracted zip: PASS |
| Tokenizer load | vocab=8000, specials 0/1/2/3 | PASS |
| Imports self-contained | only torch/numpy/sentencepiece/stdlib + intra-package | grep audit |
| Hardcoded paths in package | **none** — `create_default_tokenizer` uses package-relative path; `sys.path` bootstrap is relative | grep audit |
| Zip integrity | extracts cleanly, 13 files, no pycache | verified |
| CPU diagnostic | **13/13 PASS** on extracted copy | actual run |
| CPU forward/backward | loss finite, grads computed, no weight update | PASS |
| AMP resolution logic | fp32/fp16/bf16 → correct dtype/None on CPU | PASS |
| SFT gate | `validate_pretrained_checkpoint` present in packaged training.py | code present |

## 3. GPU COMPATIBILITY — VERIFIED vs NOT TESTED

| Platform | Status |
|---|---|
| Kaggle T4 FP16+GradScaler | **NOT TESTED** — code path correct-by-design, needs notebook run |
| Kaggle T4 BF16 | NOT TESTED — expected unsupported (Turing) → auto fp16 fallback by `is_bf16_supported()` |
| Local NVIDIA GPU | NOT TESTED — no CUDA device on this machine |
| Future GPU server | NOT TESTED — same code, device-agnostic |
| CPU fallback | **TESTED — works** |

**Honest statement**: Kaggle/CUDA compatibility is code-verified only. The packaged diagnostic script + notebook must be run on the actual GPU to claim hardware verification.

## 4. PATH & DEVICE PORTABILITY

- `resolve_device`: `"cpu"` literal, `"auto"` → cuda-if-available, `"cuda[:N]"` → cuda or cpu fallback. No GPU-name or index hardcoding.
- `resolve_amp_dtype`: fp16→GradScaler path; bf16→`is_bf16_supported()` gate with fp16 fallback; CPU/fp32→no AMP. Unsupported precision never silently changes model math — it falls back explicitly.
- Checkpoint dirs are constructor args — no `/kaggle/working` hardcode in package (only in the notebook, which is correct for Kaggle).
- `sys.path` bootstrap in `core01/*.py` derives paths from `__file__` — works at any install location.

## 5. FUTURE GPU MIGRATION

**No code changes required** to move from Kaggle → local NVIDIA → future server:
- Same zip, same architecture, same tokenizer.
- Only env differences: PyTorch CUDA build, driver, `device`/`precision` config values.
- Checkpoints are plain `.pt` dicts — load anywhere.
- Minimum useful VRAM ~8GB (batch16 FP16); 16GB comfortable.

## 6. REMAINING RISKS / LIMITATIONS

1. `sentencepiece` not in `ml-service/requirements.txt` — must be installed on target (Kaggle has it preinstalled; verify).
2. FP16 on pre-Turing GPUs (e.g., K80/Pascal) works via GradScaler; BF16 needs Ampere+.
3. OOM handling not implemented — batch size must be tuned per GPU via diagnostic throughput probe.
4. Approximate (not bit-exact) resume — sampler state not checkpointed.
5. No DDP/multi-GPU — single GPU only by design.

## 7. OWNER MANUAL STEPS

1. Upload `nexusai_core01_kaggle_package.zip` to Kaggle as a Dataset (or extract folder into notebook input).
2. New Notebook → GPU T4 x2 → Internet ON.
3. `pip install sentencepiece` if import fails.
4. Run diagnostic notebook (`docs/notebooks/nexusai_core01_kaggle_gpu_diagnostic.ipynb`) or `python nexusai_core01_gpu_diagnostic.py <package_root>`.
5. Report measured tokens/sec + peak VRAM back for training-config decision.

**STOP — no training, downloads, uploads, GPU sessions, commits, or pushes performed.**
