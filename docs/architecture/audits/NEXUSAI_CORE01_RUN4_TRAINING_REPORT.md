# NEXUSAI CORE-01 RUN4 TRAINING REPORT

**Status: NOT YET EXECUTED — awaiting Colab run**

## Prepared
- Cell: `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` (syntax verified)
- Resume: run3 ckpt (step 1341) → new dir `checkpoints/core01_run4/` (overwrite guard)
- Config: fp16, bs8 × accum4, epochs=2, max_steps=6000 global, ckpt every 100, eval every 250
- Corpus: `corpus_train.jsonl` on Drive `MyDrive/NexusAI/data/run4/`

## Pre-flight verified
- run3 ckpt loads strictly, step/epoch/status confirmed
- Driver args corrected (--gradient-accumulation-steps, val-fraction holdout — no leakage)
- Resume via absolute ckpt path (proven in run3)

## To execute (user)
1. Upload corpus_train.jsonl → Drive/NexusAI/data/run4/
2. Colab: mount Drive, extract source bundle, run cell
3. Report train_run4_*.json back
