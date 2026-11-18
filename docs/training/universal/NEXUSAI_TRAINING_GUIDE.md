# NexusAI Core-01 Training Guide

## Prerequisites
- Python ≥3.9, torch (CUDA build for GPU), sentencepiece, numpy, psutil
- Verified checkpoint (Git LFS on main or package `checkpoints/verified/`)
- Dataset `corpus_train.jsonl` (package `datasets/verified_data/`)
- Tokenizer `sp_bpe_8k.model` (package `nexusai/tokenizer/`)

## Preflight (mandatory first step)
Run `UNIVERSAL_CLOUD_PREFLIGHT_CELL.py` — must print READY before training.
READY ≠ authorized; human must still approve the run.

## Train (Run4 continuation)
```
python packages/ai-core/core01/pretraining_driver.py \
  --checkpoint <run3 ckpt> --dataset <corpus_train.jsonl> \
  --tokenizer <sp_bpe_8k.model> --output <run4 dir> \
  --epochs 5 --max-steps 8000 --batch-size 8 \
  --gradient-accumulation-steps 4 --precision fp16 --device cuda
```
(EPOCHS=5 → exactly 2 new epochs after Run3 epoch 3. Zero-step guard active.)

## Resume after disconnect
Re-run preflight → point driver at latest `checkpoint_step*.pt`/`checkpoint_last.pt`
in the run4 dir → same command; optimizer/scheduler/scaler/RNG restore.

## Verify
`test_run4_infra.py` (6 tests) + `neural_benchmark_v2.py` for quality baseline.
