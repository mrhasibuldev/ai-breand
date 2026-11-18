# Cloud Migration Guide

## Move training between providers
1. Get `NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip` onto the new environment
   (upload to Drive / attach dataset / git clone for checkpoint via LFS).
2. Extract → run `UNIVERSAL_CLOUD_PREFLIGHT_CELL.py`.
3. Checkpoint + dataset + tokenizer are identical everywhere (hash-verified),
   so resume is provider-agnostic: point `--resume` at the checkpoint dir.

## Provider notes
- **Colab**: GPU via Runtime menu; Drive mount for persistence; sessions die →
  save ckpts to Drive.
- **Kaggle**: GPU via accelerator setting; `/kaggle/input` for datasets;
  `/kaggle/working` ephemeral — copy ckpts out.
- **Generic Linux GPU**: install python deps (`torch`, `sentencepiece`,
  `numpy`, `psutil`), clone repo or extract package, run preflight cell logic.
- **CPU-only**: inference/eval fine; training impractical (8.8M model still
  slow) — use only for smoke tests.

## Never
- Do not treat Drive mount as cloud IAM authorization.
- Do not assume GPU exists — preflight reports honestly.
- Do not overwrite the verified Run3 checkpoint.
