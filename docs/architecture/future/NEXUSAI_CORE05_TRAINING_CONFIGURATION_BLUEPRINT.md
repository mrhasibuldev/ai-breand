# NexusAI Core-05 — Training Configuration Blueprint

**Status:** PROPOSAL ONLY — not implemented, not executed.
**Prerequisite:** Dataset V5 must exist and pass validation (currently BLOCKED — see Stage-0 audit).

## 1. Architecture Configuration (proposed)

```python
# models/nexusai_core_05/config/model_config.py (NEW file, future mission)
model_name = "nexusai-core-05"
vocab_size = 8000
d_model = 512
n_layers = 12
n_heads = 8
d_ff = 2048
max_len = 1024          # raise from 512; PE buffer supports it
dropout = 0.1
positional_encoding = "sinusoidal"
pad_id, unk_id, bos_id, eos_id = 0, 1, 2, 3
estimated_parameters ≈ 45,928,608  # VERIFIED by formula
```

Reuse `core01/transformer.py`, `core01/training.py`, `core01/sft_dataset.py` unchanged — they are config-driven. Only a new config class + thin wrapper are needed.

## 2. SFT Configuration — T4 (16 GB) recommended starting point

| Parameter | Value | Rationale |
|---|---|---|
| precision | bf16 | T4 supports bf16; halves activation memory, no GradScaler needed |
| batch_size (micro) | 8 | seq 512 comfortable; seq 1024 use 4 |
| gradient_accumulation_steps | 8 | effective batch 64 |
| optimizer | AdamW | existing |
| learning_rate | 3e-4 | matches core01 config; consider 1e-4 for 45M to be safe |
| warmup_steps | 100 | existing |
| weight_decay | 0.01 | existing |
| grad_clip | 1.0 | existing |
| epochs | 3 | start; early-stop on val_loss |
| max_len | 512 first, 1024 second run | staged: prove at 512, extend after |
| checkpoint_interval | 250 steps | T4 sessions are short; frequent saves |
| eval_interval | 250 steps | val_loss tracking |
| seed | 42 | reproducibility |

Estimated VRAM at seq512/batch8/bf16: weights ~92MB + grads ~92MB + AdamW ~184MB + activations (dominant, ~2–4GB) → fits comfortably in 16GB. Seq1024/batch4/bf16 also fits.

## 3. Alternative configurations by GPU memory

| GPU | Config | Notes |
|---|---|---|
| T4 16GB | seq512 b8 accum8, or seq1024 b4 accum16 | recommended |
| L4/A10 24GB | seq1024 b8 accum8 | faster iteration |
| A100 40/80GB | seq1024 b16 accum4, bf16 | headroom for larger batch |
| CPU only | NOT recommended for training | inference only |

## 4. Step planning (SFT on ~1–3k records)

- v4-size dataset (~1.1k train): ~14 steps/epoch at effective batch 64 → 3 epochs ≈ 42 optimizer steps. Very fast (<1h on T4). **This is a pipeline smoke test, not capability training.**
- V5-size (~2–4k train): ~30–60 steps/epoch → still <2h. Real capability needs the future pretraining stage.

## 5. Recovery strategy

- Checkpoint every 250 steps + epoch end; atomic save with `.backup` already implemented.
- On Colab disconnect: download `checkpoint_*.pt` + `rng` state to Drive before session end; resume via `resume_checkpoint` + `load_checkpoint` (RNG states restore — VERIFIED in code).
- Never overwrite `checkpoints_core01..04`; use `checkpoints_core05_sft_v1/` naming.

## 6. What this config does NOT do

- Does not pretrain. Does not create general knowledge. Does not fix tokenizer fragmentation. Does not guarantee multilingual quality — those need V5 + future corpus + eval gates.
