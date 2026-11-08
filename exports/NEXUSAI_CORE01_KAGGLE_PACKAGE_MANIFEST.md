# NEXUSAI CORE-01 — KAGGLE PACKAGE MANIFEST

**Package**: `exports/nexusai_core01_kaggle_package.zip`
**Zip size**: 306,348 bytes (~299 KB)
**Zip SHA-256**: `1b0c66f03457eb764b08dacde5594e4093581b2b3f116ad9e3176a97d33be970`
**Contents**: 15 files inside top-level folder `nexusai_core01_kaggle_package/`
**Updated**: 2026-11-07 (Phase 6.1) — added `data/prepare_english_corpus.py` (local-Parquet English corpus prep, torch-free)

## INCLUDED FILES

| Package path | Original project path | Purpose | Req? | Size (B) | SHA-256 (16) |
|---|---|---|---|---|---|
| core01/transformer.py | packages/ai-core/core01/transformer.py | Model architecture | REQUIRED | 18,202 | a66edada90d4457c |
| core01/tokenizer_interface.py | packages/ai-core/core01/tokenizer_interface.py | SentencePiece wrapper + vocab check | REQUIRED | 7,477 | 47ff3e0b061bc5a9 |
| core01/dataset.py | packages/ai-core/core01/dataset.py | Datasets + splits + PackedTextDataset + cache provenance | REQUIRED | 19,752 | 25d6b2f2affc02f3 |
| core01/training.py | packages/ai-core/core01/training.py | Pretrain/SFT engines, checkpoints, AMP, on_step, finalize, scaler state | REQUIRED | 29,863 | 1bca6e60e7a8204c |
| core01/pretraining_driver.py | packages/ai-core/core01/pretraining_driver.py | Config-driven pretraining entry point (seeded, finalize-aware) | OPTIONAL (training only) | 16,072 | 2c5328c954ca4977 |
| core01/inference.py | packages/ai-core/core01/inference.py | Inference engine | OPTIONAL | 6,452 | 89f5e917082eda92 |
| core01/evaluation.py | packages/ai-core/core01/evaluation.py | 9-test evaluator | OPTIONAL | 12,975 | 3e06875ceebdc5a2 |
| core01/__init__.py | packages/ai-core/core01/__init__.py | Package exports | REQUIRED | 1,326 | a560c988413378cc |
| core01/README.md | packages/ai-core/core01/README.md | Docs | OPTIONAL | 3,182 | aff37b2f1bff57fe |
| models/nexusai_core_01/__init__.py | packages/ai-core/models/nexusai_core_01/__init__.py | Namespace | REQUIRED | 203 | 1634aa63f2439320 |
| models/nexusai_core_01/config/__init__.py | packages/ai-core/models/nexusai_core_01/config/__init__.py | Config exports | REQUIRED | 203 | 3df359ef83c91a60 |
| models/nexusai_core_01/config/model_config.py | packages/ai-core/models/nexusai_core_01/config/model_config.py | Hyperparameters | REQUIRED | 9,435 | 156cf111b9af3fe5 |
| data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model | same | 8K SentencePiece tokenizer | REQUIRED | 387,195 | 2fcc6a87c9ded27d |
| data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.vocab | same | Tokenizer vocab (aux) | OPTIONAL | 137,745 | 8e499079703b5f74 |
| data/prepare_english_corpus.py | packages/ai-core/data/prepare_english_corpus.py | English corpus prep (local parquet only, no download) | OPTIONAL (data prep) | 24,283 | d6db5e486da8cd10 |

## EXCLUDED (deliberately)

- `knowledge/`, `.env*`, credentials, user data — never included
- All checkpoints (`checkpoints_medium/`, any `.pt`) — diagnostic needs none
- Training datasets, `data/` project datasets, `data/staging/`
- `__pycache__`, `.venv`, Git history, frontend/backend app code
- `test_core01.py` (test harness, not needed at inference/diagnostic)

## DEPENDENCIES (must exist in target env)

- `torch` (>=2.0; CUDA build for GPU)
- `numpy` (>=1.24)
- `sentencepiece` (0.2.x) — **note: missing from ml-service/requirements.txt; install manually if absent**

## KAGGLE USAGE

1. Kaggle → Datasets → New Dataset → upload `nexusai_core01_kaggle_package.zip` → extract (or upload the folder).
2. New Notebook → attach dataset as Input.
3. `pip install sentencepiece` if missing (internet ON).
4. Run `exports/nexusai_core01_gpu_diagnostic.py <package_root>` or the diagnostic notebook.

## PORTABILITY NOTES

- No hardcoded `/kaggle/*`, `C:\`, or GPU-name assumptions in package code.
- `device`/`precision` come from `NexusAICore01Config` — set `device="cuda"`/`"auto"`/`"cpu"`, `precision="fp16"|"bf16"|"fp32"`.
- `create_default_tokenizer()` resolves tokenizer relative to package root — works anywhere the folder structure is preserved.
- Same zip works on Kaggle, local NVIDIA GPU, or future GPU server — only PyTorch+CUDA build differs.
