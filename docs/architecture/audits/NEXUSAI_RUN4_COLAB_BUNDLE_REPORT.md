# NEXUSAI CORE-01 RUN4 — COLAB BUNDLE EXECUTION REPORT

**Date:** 2026-11-10 · No training started · No checkpoints modified

## Bundle
- **File:** `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip`
- **Size:** 299,478 bytes (292KB)
- **SHA-256:** `75af9fa29c4c551f864cf53bdc18baa4e5244b52ed8c20b7f3150ddd8e1b97d3`
- **Entries:** 15 (14 files + BUNDLE_MANIFEST.json)

## Contents
| Path | Purpose |
|---|---|
| `packages/ai-core/core01/*.py` (8 files) | transformer, tokenizer_interface, dataset, training, inference, evaluation, pretraining_driver |
| `packages/ai-core/models/nexusai_core_01/config/` | model_config.py (8.84M arch, vocab 8000, ctx 512) |
| `.../tokenizers/bpe_8k/sp_bpe_8k.model` + `.vocab` | SentencePiece tokenizer (verified multilingual) |
| `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` | resume-safe Run4 training cell |
| `BUNDLE_MANIFEST.json` | Drive prerequisites + pip deps |

## Independent-run verification
- All .py files parse (ast) ✅
- Driver entry `python -m core01.pretraining_driver` present ✅
- Cell sys.path inserts `ai-core` + `ai-core/models` ✅
- Tokenizer model+vocab included (no external dep) ✅
- Checkpoint/resume logic inside `training.py` CheckpointManager ✅
- Deps: torch, sentencepiece, numpy (Colab preinstalled)

## Drive prerequisites (user uploads)
1. `NexusAI/checkpoints/core01_english_run3/checkpoint_final.pt` — already on Drive ✅
2. `NexusAI/data/run4/corpus_train.jsonl` — **upload 385MB file**

## Colab execution steps
1. Mount Drive; extract ZIP to `/content/nexusai` (entries preserve `packages/...` paths)
2. `pip install -q sentencepiece` (torch/numpy preinstalled)
3. Paste & run `COLAB_RUN4_TRAIN_CELL.py` contents in a cell
4. Cell auto-resumes: run4 ckpt → latest → run3; writes only to `checkpoints/core01_run4/`

## Not included (by design)
- english_first data (corpus on Drive replaces it)
- Run3 ckpt (already on Drive, 107MB — not duplicated in bundle)
- Evaluation cells (run post-training)

## Verdict: bundle READY for Colab Run4.
