# =============================================================================
# NEXUSAI CORE-01 — RESUME TRAINING CELL (run2, fresh Colab account)
# Resumes EXACT checkpoint: checkpoints/core01_english/checkpoint_final.pt
# Output -> NEW dir: checkpoints/core01_english_run2/  (run1 dir untouched)
# English-only, fp16, bs8 x accum4, epochs=2, max_steps=1000 (global step count)
# =============================================================================
import os, sys, subprocess, json, glob, time
from datetime import datetime

AI_CORE = "/content/nexusai/packages/ai-core"
SRC_CKPT_DIR = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english"
SRC_CKPT = os.path.join(SRC_CKPT_DIR, "checkpoint_final.pt")   # EXACT file, no glob
OUT_DIR  = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english_run2"
REPORTS  = "/content/drive/MyDrive/NexusAI/reports"
os.makedirs(OUT_DIR, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)

TRAIN = os.path.join(AI_CORE, "data/english_first/english_train.json")
VAL   = os.path.join(AI_CORE, "data/english_first/english_validation.json")
TOK   = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")

# ---- pre-flight: files + checkpoint must exist ----
import torch
for p in (TRAIN, VAL, TOK, SRC_CKPT):
    assert os.path.exists(p), "MISSING: %s" % p
assert torch.cuda.is_available(), "CUDA required — Runtime > T4 GPU"
prop = torch.cuda.get_device_properties(0)
print("GPU:", prop.name, "| VRAM %.2f GB" % (prop.total_memory/1e9),
      "| torch", torch.__version__, "| cuda", torch.version.cuda)

# ---- verify checkpoint metadata BEFORE training ----
ck = torch.load(SRC_CKPT, map_location="cpu", weights_only=False)
print("resume ckpt: step=%s epoch=%s status=%s train_loss=%s val_loss=%s" % (
    ck.get("step"), ck.get("epoch"), ck.get("model_status"),
    ck.get("train_loss"), ck.get("val_loss")))
assert ck.get("step") is not None, "checkpoint has no step — aborting"
assert "model_state_dict" in ck and "optimizer_state_dict" in ck
START_STEP = ck["step"]

# ---- driver cmd (module form REQUIRED) ----
cmd = [sys.executable, "-m", "core01.pretraining_driver",
       "--train-file", TRAIN, "--val-file", VAL,
       "--output-dir", OUT_DIR,
       "--tokenizer", TOK,
       "--device", "cuda", "--precision", "fp16",
       "--batch-size", "8", "--gradient-accumulation-steps", "4",
       "--learning-rate", "3e-4", "--warmup-steps", "100",
       "--epochs", "2", "--max-steps", "1000",
       "--checkpoint-interval", "100", "--eval-interval", "250",
       "--log-interval", "10",
       "--resume", SRC_CKPT]
print("CMD:", " ".join(cmd))
t0 = time.time()
r = subprocess.run(cmd, cwd=AI_CORE)
el = time.time() - t0

# ---- report ----
final = os.path.join(OUT_DIR, "checkpoint_final.pt")
last = os.path.join(OUT_DIR, "checkpoint_last.pt")
ckpts = sorted(glob.glob(os.path.join(OUT_DIR, "checkpoint_*.pt")))
rep = {"ts": datetime.now().isoformat(), "rc": r.returncode,
       "elapsed_s": round(el,1), "gpu": prop.name,
       "torch": torch.__version__, "cuda": torch.version.cuda,
       "resume_from": SRC_CKPT, "start_step": START_STEP,
       "epochs_cfg": 2, "max_steps_cfg": 1000,
       "note": "max_steps is GLOBAL step count; epochs=2 also bounds run",
       "ckpt_dir": OUT_DIR,
       "ckpts": [{"file": os.path.basename(c), "size_mb": round(os.path.getsize(c)/1e6,1)} for c in ckpts],
       "final_exists": os.path.exists(final)}
if os.path.exists(final):
    fck = torch.load(final, map_location="cpu", weights_only=False)
    rep["final_step"] = fck.get("step"); rep["final_epoch"] = fck.get("epoch")
    rep["final_status"] = fck.get("model_status")
    rep["final_train_loss"] = fck.get("train_loss")
    rep["final_val_loss"] = fck.get("val_loss")
json.dump(rep, open(os.path.join(REPORTS, "train_run2_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S")), "w"), indent=1)
print("\n==== RUN2 DONE rc=%s elapsed=%.0fs ====" % (r.returncode, el))
print(json.dumps(rep, indent=1)[:2000])
