# NexusAI Core-01 — Run4 Preflight Guide (Colab)

## Order of cells (fresh Colab notebook, GPU runtime)
1. **GPU Setup** — `COLAB_GPU_SETUP_CELL.py` → must print `GPU_READY`.
   If `GPU_NOT_AVAILABLE`: Runtime → T4 GPU → re-run.
2. **Clone + Recovery** — `COLAB_CLONE_RECOVERY_CELL.py` → checkpoint +
   tokenizer retrieved from GitHub via LFS, SHA verified.
3. **Dataset** — Run4 corpus still ships in the single-upload ZIP
   (385MB; NOT in git). Either upload
   `NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` (SHA `8b212964…`) to Drive,
   or download dataset separately after approval.
4. **Combined Preflight** — `COLAB_RUN4_COMBINED_PREFLIGHT_CELL.py` →
   `READY FOR TRAINING` or `BLOCKED`.
5. **Gate** — `COLAB_RUN4_TRAINING_GATE_CELL.py` → type exact phrase
   `START NEXUSAI CORE-01 TRAINING`.
6. **Train** — `COLAB_RUN4_TRAIN_CELL.py` → EPOCHS=5 (2 new), MAX_STEPS=8000,
   bs8×accum4, fp16, output `checkpoints/core01_run4/`.

## What changed vs ZIP-only flow
- Checkpoint no longer needs ZIP — comes from Git LFS via clone.
- Dataset still needs the ZIP (too large for git) OR Drive copy.

## Disconnect recovery
Re-run clone cell (idempotent), then resume cell picks latest checkpoint
in `core01_run4/` automatically.
