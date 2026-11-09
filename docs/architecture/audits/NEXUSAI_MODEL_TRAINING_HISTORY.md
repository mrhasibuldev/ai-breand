# NEXUSAI MODEL TRAINING HISTORY

## Core-01 runs (English-first, Colab T4, fp16)

| Run | Steps | Epoch | Train loss | Val loss | Checkpoint |
|---|---|---|---|---|---|
| 1 | 447 | 1 | 5.8646 | 4.8492 | Drive `core01_english/` |
| 2 | 894 | 2 | 4.7238 | 4.4748 | Drive `core01_english_run2/` |
| 3 | 1341 | 3 | 4.4259 | 4.2169 | `models/checkpoints_core01_run3/` sha256 `ad515c…7830` |

- Dataset: english_first, 63,876 docs / 7.43M tokens, 99%+ English
- Config: bs8×accum4, lr 3e-4, warmup, AdamW, ctx 512, packed sequences
- Resume chain verified: each run resumes exact prior checkpoint (step/epoch/optimizer/scheduler/RNG)

## Production model (separate, legacy)
- `models/checkpoints_medium/final_model.pt`: 2,452,544 params, 2L/128/2H, max_len 128
- Poor quality (gibberish/fallback); NOT Core-01; do not confuse

## Run4 (prepared, not executed)
- Corpus: `data/phase2/run4_corpus/corpus_train.jsonl` — 216,193 docs / ~60.4M tokens (BN ~60%)
- Cell: `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` (resume-safe, run3→run4 isolation)
- Bundle: `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip` sha256 `75af9fa2…`
- Status: **awaiting Colab execution**
