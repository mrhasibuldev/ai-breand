# NEXUSAI KAGGLE GPU BEGINNER GUIDE

How to use your existing Kaggle account to run NexusAI Core-01 GPU diagnostics and (later, with approval) training. **No payment information is ever required for the free tier.**

---

## 1. Key concepts (read first)

| Term | What it means |
|---|---|
| **Kaggle Notebook** | A cloud Jupyter notebook that runs on Kaggle's machines. Your code cells run there, not on your PC. |
| **GPU Accelerator** | The graphics card the notebook uses. Free tier offers **T4 x2** (two NVIDIA T4, 16GB each). You pick it in notebook settings. |
| **Input** | Files/datasets you attach to a notebook (e.g., our code, tokenizer, datasets). Stored under `/kaggle/input/`. |
| **Working Directory** | `/kaggle/working/` — your notebook's scratch space, **20GB, persists between sessions**. Put checkpoints here. |
| **Notebook Output** | Saved versions of your notebook + any files you explicitly save as output. |
| **Session** | One running notebook. Free GPU sessions last **up to ~12 hours** and die after ~20 min idle. |
| **Quota** | ~30 GPU-hours per week, resets Saturday UTC. One hour on T4 x2 counts as one hour (not two). |

## 2. Before you start (one-time)

1. Go to **kaggle.com** and log in with your existing account.
2. Verify your phone number if not done: **Settings → Phone Verification**. GPU stays greyed-out until verified.
3. Make sure you do **NOT** enter any payment/billing info — free tier needs none.

## 3. Create your first notebook

1. Click **Code → New Notebook**.
2. Top-right **Settings** (or the `...` menu → Session options):
   - **Accelerator: GPU T4 x2**
   - **Internet: ON** (needed to `pip install` and download datasets later)
3. Click **Save Version** or just run cells — a GPU session starts.

## 4. Verify the GPU works

Run this cell:

```python
import torch
print("CUDA:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none")
!nvidia-smi
```

Expected: `CUDA: True`, a Tesla T4 name, and an `nvidia-smi` table.

## 5. Get NexusAI code onto Kaggle (when approved)

**Option A — Kaggle Dataset (recommended for code):**
1. Zip `packages/ai-core/core01/`, `packages/ai-core/models/nexusai_core_01/`, and the tokenizer folder.
2. **Datasets → New Dataset** → upload zip → it appears under `/kaggle/input/<dataset-name>/`.

**Option B — GitHub:**
```python
!git clone https://github.com/mrhasibuldev/ai-breand.git
```
(works because our code is already pushed; private repo would need a token — do NOT share tokens in notebooks)

## 6. Load Core-01 and run a diagnostic (needs approval first)

```python
import sys, torch
sys.path.insert(0, "/kaggle/input/ai-breand/packages/ai-core")
sys.path.insert(0, "/kaggle/input/ai-breand/packages/ai-core/models")
from core01.transformer import NexusAICore01
from nexusai_core_01.config.model_config import NexusAICore01Config

cfg = NexusAICore01Config(device="cuda", precision="fp16",
                          batch_size=8, gradient_accumulation_steps=2)
model = NexusAICore01(cfg).cuda()
print("params:", model.count_parameters())
```

Expected: `params: 8842560`, no errors.

## 7. Checkpoints — save and resume

```python
from core01.training import PretrainingEngine
engine = PretrainingEngine(model, cfg, "/kaggle/working/ckpt")
# ... training happens here ...
engine.save_checkpoint(epoch=0, train_loss=2.1, val_loss=2.0,
                       filename="latest.pt")
# later / after restart:
engine.load_checkpoint("latest.pt")   # restores weights+optimizer+step+RNG
```

- `/kaggle/working/` survives session ends — checkpoints persist.
- Download them: notebook panel → **Output** → download file, or copy to a Kaggle Dataset.

## 8. If the session dies

1. Open the same notebook → **New Session** → GPU T4 x2 again.
2. Re-attach the same Inputs.
3. Load `latest.pt` from `/kaggle/working/ckpt/` and continue — training resumes from saved step.

## 9. Move a checkpoint to your own future GPU

The checkpoint is a plain `.pt` file. Copy it off Kaggle (Output download) onto any machine with PyTorch + CUDA and:

```python
engine.load_checkpoint("latest.pt")   # same code path everywhere
```

Nothing Kaggle-specific is stored inside it.

## 9b. Run the GPU diagnostic notebook (Phase 4.3 prep)

A ready-made diagnostic notebook exists at `docs/notebooks/kaggle_core01_gpu_diagnostic.ipynb`.

1. Kaggle → **Notebooks → New Notebook** → upload/paste the `.ipynb` (or copy cells).
2. Settings → **Accelerator: GPU T4 x2**, **Internet: ON**.
3. Attach project code as Input (see §5) — the notebook auto-detects `/kaggle/input/**/core01`.
4. **Run All** — it performs ONLY: env check, GPU identity, model init, tiny synthetic forward/backward, AMP/FP16 step, BF16 capability check, checkpoint save/load, and a 10-step throughput probe. **No real training, no datasets.**
5. Check output for: `params: 8842560`, `weights restored identical: True`, and the measured `tokens/sec`.
6. Checkpoint lands in `/kaggle/working/ckpt_diagnostic/` (persists ~between sessions).
7. **Save Version** to keep a record. Download `diag.pt` via the Output panel if wanted (~140MB).

Quota note: free GPU availability and the ~30 h/week quota can change without notice. If GPU is greyed out, complete phone verification in Settings.

## 10. Rules to remember

- Never upload `knowledge/`, `.env`, or private user files to Kaggle.
- Datasets marked NC/GPL (Alpaca raw, dailydialogue_bn, bangla-alpaca-orca, XL-Sum) stay excluded.
- Checkpoints of experiments go to `models/nexusai_core_01/experiments/`, never over legacy files.
- Every download/training step needs explicit owner approval first.
