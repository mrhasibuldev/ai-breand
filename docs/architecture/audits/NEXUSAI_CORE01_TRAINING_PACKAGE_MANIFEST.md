# NEXUSAI CORE-01 — PORTABLE TRAINING PACKAGE MANIFEST

Minimal file set required to run Core-01 training on Kaggle (or any CUDA machine).
Everything is relative to `packages/ai-core/` unless noted.

## REQUIRED FILES

| File | Why required |
|---|---|
| `core01/__init__.py` | package exports |
| `core01/transformer.py` | model architecture (NexusAICore01) |
| `core01/tokenizer_interface.py` | SentencePiece wrapper + vocab validation |
| `core01/dataset.py` | TextDataset, TokenizedDataset, InstructionDataset (mask_prompt), DatasetLoader, split_dataset |
| `core01/training.py` | PretrainingEngine, InstructionTuningEngine, CheckpointManager, AMP/accumulation/RNG helpers |
| `core01/inference.py` | InferenceEngine (post-training eval/generation) |
| `core01/evaluation.py` | ModelEvaluator (9-test suite) |
| `core01/README.md` | usage notes (optional but useful) |
| `models/nexusai_core_01/__init__.py` | namespace package |
| `models/nexusai_core_01/config/__init__.py` | config exports |
| `models/nexusai_core_01/config/model_config.py` | NexusAICore01Config (all hyperparams incl. precision/accum/tokenizer_path) |
| `data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model` | the 8K SentencePiece tokenizer (~387KB) |

## EXTERNAL DEPENDENCIES (preinstalled on Kaggle)

- `torch` (2.x, CUDA build)
- `sentencepiece`
- `numpy`

No other project files needed. No frontend/backend, no `knowledge/`, no `.env`, no legacy checkpoints.

## KAGGLE LAYOUT PLAN

```
/kaggle/input/nexusai-core-01-code/     <- uploaded dataset (the files above, preserving dirs)
/kaggle/input/sp_bpe_8k.model           <- tokenizer (or keep inside code dataset)
/kaggle/working/ckpt/                   <- checkpoints (persistent, 20GB)
/kaggle/working/data/                   <- downloaded corpora (future, approved only)
/kaggle/working/logs/                   <- training logs
```

## CHECKPOINT OUTPUT (future, post-approval)

`models/nexusai_core_01/experiments/expNN/` locally — never `checkpoints_medium/`, never overwrite legacy.

## DIAGNOSTIC NOTEBOOK

`docs/notebooks/kaggle_core01_gpu_diagnostic.ipynb` — run BEFORE any training; synthetic data only.
