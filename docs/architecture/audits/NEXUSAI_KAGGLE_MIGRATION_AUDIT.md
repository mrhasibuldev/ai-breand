# NexusAI — Kaggle Training Environment Migration & Dataset Forensic Audit

**Date:** 2026-11-07 · **Mode:** READ-ONLY — nothing modified, downloaded, uploaded, or trained.
**New Kaggle env (owner-reported, not re-verified by me):** Python 3.13.16, torch 2.11.0+cu130, CUDA 13.0, 2× Tesla T4 (14.56 GB each), numpy 2.1.3, pandas 2.3.3, sklearn 1.6.1.

---

## A. Current Project Status

| Component | Status | Evidence |
|---|---|---|
| Core-01 model code | VERIFIED | `packages/ai-core/core01/` + `models/nexusai_core_01/` — 8,842,560 params, vocab 8,000, ctx 512 |
| Core-01 tokenizer | VERIFIED | `sp_bpe_8k.model` + `.vocab` under `data/experimental/phase9_2/tokenizers/bpe_8k/` |
| Core-01 pretraining driver | VERIFIED | `core01/pretraining_driver.py` + `PackedTextDataset` + `PretrainingEngine` (Phase 5/5.1 hardened) |
| Core-01 trained checkpoint | **MISSING** | No Core-01 checkpoint with trained weights exists anywhere in repo |
| 100M-token English corpus | **MISSING** | Never prepared; prep script ready but never run on real data |
| FineWeb shard | **MISSING** | Never downloaded |
| Portable Kaggle package | VERIFIED | `exports/nexusai_core01_kaggle_package.zip` — 306,348 B, 15 files, sha256 `1b0c66f0…be970` |
| Notebook | VERIFIED | `docs/notebooks/nexusai_core01_fineweb_pretraining.ipynb` (23 cells, 4 approval gates) |
| Local GPU | MISSING | `torch.cuda.is_available()=False`, no nvidia-smi — this PC cannot train |

## B. Dataset Inventory

| File | Size | Records | Format | Verdict |
|---|---|---|---|---|
| `packages/ai-core/data/train_v2.json` | 152 KB | **502** | `[{"messages":[{role,content}…]}]` chat/SFT format | Legacy instruction data for OLD SimpleTokenizer model — NOT usable by Core-01 pretraining driver directly |
| `packages/ai-core/data/train_final.json` | 11 KB | ~10 | plain sentence list | Toy data |
| `training/train.json` + `val.json` | 1.8/0.6 KB | 10/2 texts | `{texts,config,metadata}` | Verification fixture only |
| `training/original_dataset.jsonl` | 144 KB | **1 record** (140 KB text blob) | single JSON dict | Single-document dump — not a corpus |
| `data/public_datasets/v1.0*/` | ~1–7 KB | handful | json | Negligible |
| `data/synthetic/` | ~7 KB | handful | json | Synthetic only |
| `data/collected/{dolly,gsm8k}/` | jsonl | dolly-15k + gsm8k | instruction pairs | SFT candidates for LATER phase, not pretraining |
| `data/experimental/phase7/tokenizer_corpus/corpus_combined.txt` | **11.2 MB / 103,749 lines** | ~103K docs | plain text lines | **Only real pretraining-scale corpus** — measured ~3.47M Core-01 tokens (Phase 5). English+mixed, NOT 100M |
| `data/experimental/phase9/curated/corpus_expanded.txt` | 11.1 MB | — | plain text | Similar scale, unverified token count |
| `data/staging/love_emotion/*.jsonl` | small | — | bn/en emotion chat | Bengali SFT material, later phase |

**Duplicate/incomplete check:** not exhaustively measurable per-file without loading all; `train_v2.json` is valid JSON with consistent `messages` schema. No corrupt files found in spot checks. **No dataset is suitable for 100M-token pretraining as-is.**

## C. Checkpoint Inventory

| Checkpoint | Params (measured) | Architecture | Status |
|---|---|---|---|
| `models/checkpoints*/checkpoint_epoch_*.pt` | ~185K–2.1M | Legacy small transformer | Loadable by legacy code only |
| `packages/ai-core/models/checkpoints*/` | ~2.2M | Legacy small | same |
| `packages/ai-core/models/checkpoints_medium/*` (incl. `final_model.pt`, `best_model.pt`) | **2,468,928** | Legacy MEDIUM transformer | Best legacy model; vocab = old SimpleTokenizer (8K BPE but DIFFERENT tokenizer) |
| `data/experimental/phase8|phase10/checkpoints/` | ~2.47M / ~29MB files | Legacy medium variants | Experimental |
| **Core-01 checkpoints** | — | — | **NONE exist.** All Core-01 `.pt` files were temp test artifacts (deleted). Core-01 is UNTRAINED. |

**Compatibility verdict:** legacy checkpoints CANNOT initialize Core-01 (different arch: 2.47M vs 8.84M params, different tokenizer). Core-01 must train from random init — by design.

## D. Training Script Inventory

**Legacy path (old model, do NOT use for Core-01):**
`train_with_v2.py` / `train_medium_model.py` / `retrain_model.py` → `SimpleTokenizer` + `Small/MediumTransformer` + `training/pipeline.py` (`TrainingPipeline`, `CheckpointManager`) → outputs to `models/checkpoints*/`. Execution order: tokenizer → dataset (`training/dataset.py`) → model → pipeline.train → checkpoint.

**Core-01 path (the real one):**
`core01/pretraining_driver.py` (CLI) → `PackedTextDataset` (`core01/dataset.py`) → `PretrainingEngine` (`core01/training.py`: AdamW, warmup LR, FP16 AMP+GradScaler, grad accum, atomic ckpt, RNG, finalize→`PRETRAINING_COMPLETED`). SFT later via `InstructionTuningEngine` gated by `validate_pretrained_checkpoint`.

## E. Kaggle Environment Compatibility

| Need | Status in new env |
|---|---|
| torch 2.11+cu130, CUDA 13, 2×T4 | ✅ present (owner-verified) |
| numpy/pandas/sklearn | ✅ present |
| **sentencepiece** | ⚠️ **likely MISSING** — not in reported list; needed by `NexusAITokenizer`. Install: `pip install sentencepiece` (small, pure wheel) |
| **pyarrow** | ⚠️ needed ONLY for FineWeb parquet prep; install when reaching Cell 7 (`pip install pyarrow`) |
| Core-01 code | ✅ self-contained in ZIP; imports torch+sentencepiece only |
| Python 3.13 compat | ✅ code uses stdlib+torch+spm only; no version-sensitive deps found |

## F. ZIP Archive Analysis

`exports/nexusai_core01_kaggle_package.zip` — **306,348 B, 15 files, sha256 `1b0c66f0…be970`, integrity clean.** Contains core01/ (all modules incl. driver+prep script), models/nexusai_core_01/, tokenizer .model+.vocab. **This is the ONLY zip in repo** — the "old exported ZIP" from earlier workflows no longer exists here; it likely contained legacy-model assets and is superseded anyway. The current ZIP is sufficient for Core-01 work.

## G. Exact Upload Instructions (new Kaggle account)

1. Kaggle → **Datasets → New Dataset** → upload `nexusai_core01_kaggle_package.zip` (from `C:\Users\Nusaiba\Desktop\` copy or `exports/`). Title it e.g. `nexusai-core01-package`. **This makes it available as notebook Input.** (Alternative: notebook → Add Input → upload — but Dataset is cleaner/reusable.)
2. Kaggle → **Notebooks → New Notebook** named `NexusAI-Core-Training` → **File → Import** `docs/notebooks/nexusai_core01_fineweb_pretraining.ipynb`.
3. Notebook → **Add Input** → select `nexusai-core01-package` dataset.
4. Settings: Internet **ON** (needed for FineWeb + pip), Accelerator: start **CPU** for Cells 1–8; switch to **GPU T4 x2** only for Cells 9–11.
5. Add-ons: `sentencepiece` (Cell 2 will tell you if missing), `pyarrow` before Cell 7.
6. Do NOT upload: `knowledge/`, `.env`, checkpoints, datasets, `data/` corpora, git — none are needed; the ZIP already excludes them.

## H. Package Installation Plan (minimal)

| Package | Needed? | Version | Why |
|---|---|---|---|
| torch | already installed | 2.11.0+cu130 | training |
| sentencepiece | **YES — install** | latest stable | Core-01 tokenizer |
| pyarrow | YES at Cell 7 | latest | parquet reading |
| numpy/pandas/sklearn | already | — | present |
| transformers/datasets | **NO** | — | not used by Core-01 path |
| All legacy deps | NO | — | old model path unused |

## I. Recommended Sequence

Cells 2–4 (verify pkg/tokenizer) → Cell 5 (FineWeb verify) → **approve** Cell 6 download (~2 GiB, CPU) → **approve** Cell 7 prep (~30–60 min CPU, 100M tok) → Cell 8 audit → switch GPU → Cell 9 → **approve** Cell 10 smoke (~200 steps) → review metrics → **approve** Cell 11 full run (est. ~1 epoch ≈ 190k micro-steps at bs32×512 — compute real estimate from pilot tok/s; likely multi-session → use `--resume`).

## J. Risks

- **sentencepiece missing** → Cell 4 fails fast; fix = one pip install.
- **Kaggle session timeout (9–12h)** mid-prep → prep script resume-safe at row-group boundaries; mid-training → `checkpoint_last.pt` + `--resume`.
- **100M tokens ≈ ~3 epochs** on T4 — could exceed one session; checkpoint resume handles it, but plan for 2–3 sessions.
- **VRAM**: bs32×512×6L on T4 14.5GB — fp16 should fit; if OOM, driver batch-size↓ + accum↑.
- **Disk**: shard 2.1GB + corpus ~0.5GB + checkpoints ~150MB each ×N — `/kaggle/working` ~20GB is enough but checkpoint rotation absent → monitor.
- **License**: ODC-By attribution must be recorded (manifest does this automatically).
- Old Kaggle account sessions/data: **inaccessible to me** — if old checkpoints matter, owner must re-upload manually; nothing in repo depends on them.
- Python 3.13 + torch 2.11: verified compatible per owner; sentencepiece wheel availability for 3.13 should be confirmed at install (it ships cp313 wheels currently).

## K. Final Recommendation

**VERIFIED — READY for owner execution.** Next action is entirely yours: upload the ZIP as a Kaggle Dataset, import the notebook, run Cells 2–8 on CPU with the two approval flags, then GPU stages. Core-01 remains **UNTRAINED** until `checkpoint_final.pt` with `PRETRAINING_COMPLETED` exists and is verified.
