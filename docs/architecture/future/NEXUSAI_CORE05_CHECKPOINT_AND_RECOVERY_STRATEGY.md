# NexusAI Core-05 — Checkpoint & Recovery Strategy

**Status:** DESIGN ONLY. No Core-05 checkpoints created.

## 1. Versioned directory structure (proposed)

```
packages/ai-core/models/
  checkpoints_core05_sft_v1/     # first SFT run
  checkpoints_core05_sft_v2/     # iterations
  checkpoints_core05_pretrain_v1/ # future continued-pretrain (if approved)
```

Never reuse `checkpoints_core01..04`. Core-05 names make provenance unambiguous.

## 2. Checkpoint lifecycle (existing `CheckpointManager` already supports)

Each checkpoint must record:
- `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict`
- `epoch`, `step`, `train_loss`, `val_loss`
- `config` (full config dict incl. architecture fields)
- `model_status` (UNTRAINED → PRETRAINING_* → INSTRUCTION_TUNING_* → PRODUCTION_READY)
- `rng_state` (python/numpy/torch CPU+CUDA) — enables exact resume
- `tokenizer_path` — provenance
- `grad_scaler_state_dict` — for fp16 resume
- `timestamp`

VERIFIED: `training.py` `save_checkpoint`/`load_checkpoint`/`validate_pretrained_checkpoint` implement all of the above, including atomic save with `.backup` and RNG restore.

## 3. Integrity & verification

- Atomic write (temp + `os.replace`) prevents corrupt checkpoints — VERIFIED.
- `validate_pretrained_checkpoint` gates SFT on genuinely-trained weights and matching architecture fields — VERIFIED.
- For Core-05: add `dataset_manifest_hash` + `git_commit` to checkpoint metadata in the future implementation mission (recommended, not yet present).

## 4. Recovery procedure

1. Colab disconnect → latest `checkpoint_step*.pt` on Drive is authoritative.
2. New session: load config, `engine.load_checkpoint(path)` → restores weights, optimizer, scheduler, RNG.
3. Resume dataloader at recorded step/epoch (deterministic seed=42).
4. Verify `model_status` before any downstream use.

## 5. Ownership distinction

Core-05 checkpoints must carry `model_name="nexusai-core-05"` and a distinct config hash. Existing cores (01–04) are untouched. No weight sharing or copying between cores.
