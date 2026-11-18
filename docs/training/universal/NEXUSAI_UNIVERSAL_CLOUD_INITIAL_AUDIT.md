# Universal Cloud Training — Initial Audit (2026-11-16)

## Existing (VERIFIED)
- Core-01 model: `core01/transformer.py` — 8,842,560 params, pre-norm, 6L/256d/8H
- Training: `core01/pretraining_driver.py` + `training.py` — AdamW, LambdaLR, GradScaler, atomic ckpts, full resume (opt/sched/scaler/RNG)
- Tokenizer: `sp_bpe_8k.model` vocab 8000 (en+bn verified)
- Checkpoint: Run3 `checkpoint_final.pt` 106,777,501B sha `ad515cade…7830` — now on GitHub via LFS (main)
- Dataset: `corpus_train.jsonl` 385,217,021B sha `5f8572ed…` 216,193 rec — verified
- Router/registry/inference: `ml-service/` exists; neural_only mode present
- Prior Colab cells: GPU setup, clone+LFS recovery, combined preflight, gate, train — all on main

## Gaps found & fixed this phase
- No provider-independent env/hardware/storage abstraction → created `packages/ai-core/cloud/` (env_manager, hardware, storage, adapters[Colab/Kaggle/Generic], model_loader, dataset_manager, preflight)
- Local bugs fixed during dev: py-version string compare, storage writable dict, Colab false-positive on Windows
- Drive checkpoint step-files (core01_english*) — NOT locally accessible; recovery audit below

## Not verified / missing
- Old Drive step checkpoints (step100–1300): inaccessible locally → NOT VERIFIED, recovery report required
- GPU runtime: untested locally (CPU-only) — Colab cell provided
- phase10 ckpt: incompatible family, documented not routed
