# NEXUSAI BENGALI RUN4 PLAN

## Status: PREPARED — awaiting Colab execution
- Corpus: `data/phase2/run4_corpus/corpus_train.jsonl` — 216,193 docs / ~60.4M tokens / BN≈60% / sha256 `5f8572ed…`
- Composition: wiki 45K + sangraha 9K + bongchat 30K + english_first 62K + tinystories 60K + reasoning 10.2K
- Cell: `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` — resume-safe, run3→run4 isolated dir
- Bundle: `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip` sha256 `75af9fa2…`

## Execution steps (user)
1. Upload corpus_train.jsonl (385MB) → Drive `NexusAI/data/run4/`
2. Colab: extract bundle → run cell → checkpoints to `checkpoints/core01_run4/`
3. Download `checkpoint_final.pt` → `models/checkpoints_core01_run4/`
4. I run eval suite vs run3 baseline

## Config
fp16, bs8×accum4 (eff 32), epochs=2, max_steps=8000, ckpt/100, eval/250, lr 3e-4, warmup — same as run3.

## Success criteria (honest)
- val_loss < 4.0
- Bengali-script output on BN prompts (currently fails)
- No English regression
- CPU inference still works (~same footprint)

## Risks
- Corpus Bengali-heavy → possible EN forgetting (mitigated: 40% EN/mixed)
- Colab session limits → resume-safe cell handles
- Reasoning data is template-based → limited reasoning gain expected
