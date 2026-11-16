# NexusAI Core-01 — Colab GPU Setup Guide

## Symptom
Preflight reported `torch 2.14.1+cpu`, `CUDA available: False`, no GPU.

## Root cause (two possibilities — check in order)
1. **CPU runtime selected** — Colab defaults can be CPU-only.
   Fix: `Runtime → Change runtime type → T4 GPU → Save`, then re-run.
2. **CPU-only torch build installed** — some setups pip-install `+cpu`.
   On a GPU runtime, reinstall CUDA build:
   ```python
   !pip uninstall -y torch torchvision
   !pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```
   (Match the CUDA build to the runtime's driver; cu121/cu124/cu126 all work
   on current Colab T4.)

## Verification cell
Run `docs/notebooks/COLAB_GPU_SETUP_CELL.py` in ONE Colab cell.
It checks: torch import, `torch.cuda.is_available()`, GPU name, CUDA version,
VRAM, a real CUDA matmul, RAM, disk. Ends with `GPU_READY` or `GPU_NOT_AVAILABLE`.

## A notebook cannot grant itself a GPU
If the cell reports `GPU_NOT_AVAILABLE`, the runtime is CPU — change it
manually in the Colab menu and re-run. No code can bypass this.

## VRAM fit (Core-01 Run4)
Model 8.84M params · bs8 × accum4 · seq512 · fp16.
Estimate: weights+AdamW ~0.5GB, activations ~1–2GB → **T4 16GB is ample**;
even free-tier T4 suffices. No configuration change needed.
