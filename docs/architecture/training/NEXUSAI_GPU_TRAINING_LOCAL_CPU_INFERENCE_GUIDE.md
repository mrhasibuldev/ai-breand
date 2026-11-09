# NEXUSAI — GPU TRAINING → LOCAL CPU INFERENCE GUIDE

## The idea in one line
Train on a **rented/temporary GPU** (Colab/Kaggle free), save the checkpoint, download it, and run it on your **own CPU** forever after.

## Verified workflow (already proven for runs 1–3)
1. **Local:** code + data in repo (`packages/ai-core/`)
2. **Bundle:** `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip` (code+tokenizer+cell)
3. **Colab:** mount Drive → extract bundle → upload corpus → run `COLAB_RUN4_TRAIN_CELL.py`
4. **Drive:** checkpoints saved under `NexusAI/checkpoints/core01_run4/` every 100 steps + final
5. **Download:** `checkpoint_final.pt` → `packages/ai-core/models/checkpoints_core01_run4/`
6. **CPU:** `scripts/eval_core01_run3.py`-style inference — no GPU, no internet AI

## Verified CPU numbers (run3, same arch as run4)
- Model load: ~0.3s build, strict load instant
- RAM: ~382MB peak (8GB PC fine)
- Speed: ~42 tokens/sec → 100 tokens ≈ 2.4s
- Offline: torch + sentencepiece only

## Checkpoint safety rules
- Never overwrite: each run gets own directory
- Resume: exact-path `--resume`, restores model+optimizer+scheduler+RNG
- Verify: `torch.load` + `load_state_dict(strict=True)` + SHA-256
- Keep Drive + local copies

## Interruption recovery
Driver saves `checkpoint_last.pt` per epoch + step ckpts; cell auto-resumes latest.

## Not yet implemented
- INT8/INT4 quantization (optional future optimization)
- Multi-turn memory in core01 inference (app-layer concern)
