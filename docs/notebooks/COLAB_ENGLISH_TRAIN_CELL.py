# =============================================================================
# NEXUSAI CORE-01 — ENGLISH-FIRST TRAINING CELL (Google Colab, T4)
# Run ONLY after MASTER_GATE_CELL reports GATE_PASS.
# Conservative config + Drive checkpoints + resume support.
# =============================================================================
import os, sys, subprocess, json, time
from datetime import datetime

AI_CORE = "/content/nexusai/packages/ai-core"
DRIVE_CKPT = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english"
REPORTS = "/content/drive/MyDrive/NexusAI/reports"
os.makedirs(DRIVE_CKPT, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)

TRAIN = os.path.join(AI_CORE, "data/english_first/english_train.json")
VAL   = os.path.join(AI_CORE, "data/english_first/english_validation.json")
TOK   = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")

# ---- conservative T4 config (adjust only after measured run) ----
BS = 8                  # micro-batch
ACCUM = 4               # effective batch 32
MAX_STEPS = 500         # pilot bound — increase later with approval
CKPT_EVERY = 100
EVAL_EVERY = 250
LR = 3e-4
WARMUP = 100

import torch
assert torch.cuda.is_available(), "CUDA required — set Runtime > T4 GPU"
prop = torch.cuda.get_device_properties(0)
print("GPU:", prop.name, "VRAM %.1f GB" % (prop.total_memory/1e9))

cmd = [sys.executable, "-m", "core01.pretraining_driver",
       "--train-file", TRAIN, "--val-file", VAL,
       "--output-dir", DRIVE_CKPT,
       "--tokenizer", TOK,
       "--device", "cuda", "--precision", "fp16",
       "--batch-size", str(BS), "--gradient-accumulation-steps", str(ACCUM),
       "--learning-rate", str(LR), "--warmup-steps", str(WARMUP),
       "--epochs", "1", "--max-steps", str(MAX_STEPS),
       "--checkpoint-interval", str(CKPT_EVERY),
       "--eval-interval", str(EVAL_EVERY), "--log-interval", "10"]

# resume if a checkpoint already exists in Drive dir
import glob
ckpts = sorted(glob.glob(os.path.join(DRIVE_CKPT, "checkpoint_*.pt")))
if ckpts:
    cmd += ["--resume", ckpts[-1]]
    print("RESUME from:", os.path.basename(ckpts[-1]))
else:
    print("FRESH start")

print("CMD:", " ".join(cmd))
t0=time.time()
r = subprocess.run(cmd, cwd=AI_CORE)
elapsed = time.time()-t0

rep = {"ts": datetime.now().isoformat(), "rc": r.returncode,
       "elapsed_s": round(elapsed,1), "cmd": cmd,
       "ckpt_dir": DRIVE_CKPT,
       "ckpts": [os.path.basename(c) for c in glob.glob(os.path.join(DRIVE_CKPT,"checkpoint_*.pt"))]}
json.dump(rep, open(os.path.join(REPORTS,"train_%s.json"%datetime.now().strftime("%Y%m%d_%H%M%S")),"w"), indent=1)
print("\n==== TRAIN RUN DONE rc=%s elapsed=%.0fs ====" % (r.returncode, elapsed))
print("checkpoints:", rep["ckpts"])
