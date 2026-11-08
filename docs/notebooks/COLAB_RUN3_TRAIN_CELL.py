# =============================================================================
# NEXUSAI CORE-01 — RUN 3 ENGLISH TRAINING CELL (fresh resume, Colab)
# Resume ONLY from run2 final ckpt (step 894, epoch 2).
# Output -> NEW dir checkpoints/core01_english_run3/  (run1/run2 untouched)
# English-only, fp16, bs8 x accum4, epochs=3, max_steps=1500 (global step count)
# =============================================================================
import os, sys, subprocess, json, glob, time
from datetime import datetime

AI_CORE = "/content/nexusai/packages/ai-core"
SRC_CKPT = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english_run2/checkpoint_final.pt"
OUT_DIR  = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english_run3"
REPORTS  = "/content/drive/MyDrive/NexusAI/reports"
os.makedirs(OUT_DIR, exist_ok=True); os.makedirs(REPORTS, exist_ok=True)

TRAIN = os.path.join(AI_CORE, "data/english_first/english_train.json")
VAL   = os.path.join(AI_CORE, "data/english_first/english_validation.json")
TOK   = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")

import torch
for p in (TRAIN, VAL, TOK, SRC_CKPT):
    assert os.path.exists(p), "MISSING: %s" % p
assert torch.cuda.is_available(), "CUDA required — Runtime > T4 GPU"
prop = torch.cuda.get_device_properties(0)
print("GPU:", prop.name, "| VRAM %.2f GB" % (prop.total_memory/1e9),
      "| torch", torch.__version__, "| cuda", torch.version.cuda)

# ---- verify resume ckpt BEFORE training ----
ck = torch.load(SRC_CKPT, map_location="cpu", weights_only=False)
print("resume ckpt: step=%s epoch=%s status=%s train_loss=%s val_loss=%s" % (
    ck.get("step"), ck.get("epoch"), ck.get("model_status"),
    ck.get("train_loss"), ck.get("val_loss")))
assert ck.get("step") is not None and "model_state_dict" in ck \
   and "optimizer_state_dict" in ck, "checkpoint incomplete — aborting"
assert ck.get("step") == 894, "unexpected start step %s (expected 894)" % ck.get("step")
START_STEP = ck["step"]

# ---- driver cmd (module form REQUIRED). epochs=3, max_steps global ----
cmd = [sys.executable, "-m", "core01.pretraining_driver",
       "--train-file", TRAIN, "--val-file", VAL,
       "--output-dir", OUT_DIR,
       "--tokenizer", TOK,
       "--device", "cuda", "--precision", "fp16",
       "--batch-size", "8", "--gradient-accumulation-steps", "4",
       "--learning-rate", "3e-4", "--warmup-steps", "100",
       "--epochs", "3", "--max-steps", "1500",
       "--checkpoint-interval", "100", "--eval-interval", "250",
       "--log-interval", "10",
       "--resume", SRC_CKPT]
print("CMD:", " ".join(cmd))
t0 = time.time()
r = subprocess.run(cmd, cwd=AI_CORE)
el = time.time() - t0

# ---- report ----
final = os.path.join(OUT_DIR, "checkpoint_final.pt")
ckpts = sorted(glob.glob(os.path.join(OUT_DIR, "checkpoint_*.pt")))
rep = {"ts": datetime.now().isoformat(), "run": "core01_english_run3",
       "rc": r.returncode, "elapsed_s": round(el,1), "gpu": prop.name,
       "torch": torch.__version__, "cuda": torch.version.cuda,
       "resume_from": SRC_CKPT, "start_step": START_STEP,
       "epochs_cfg": 3, "max_steps_cfg": 1500,
       "note": "max_steps is GLOBAL step count; epochs=3 bounds run to epoch 3",
       "ckpt_dir": OUT_DIR,
       "ckpts": [{"file": os.path.basename(c), "size_mb": round(os.path.getsize(c)/1e6,1)} for c in ckpts],
       "final_exists": os.path.exists(final), "errors": [] if r.returncode==0 else ["rc=%s"%r.returncode]}
if os.path.exists(final):
    fck = torch.load(final, map_location="cpu", weights_only=False)
    rep["final_step"] = fck.get("step"); rep["final_epoch"] = fck.get("epoch")
    rep["final_status"] = fck.get("model_status")
    rep["final_train_loss"] = fck.get("train_loss")
    rep["final_val_loss"] = fck.get("val_loss")
    rep["final_sha256_note"] = "see ckpts list sizes; compute externally if needed"

json_path = os.path.join(REPORTS, "train_run3_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S"))
json.dump(rep, open(json_path,"w"), indent=1)
md_path = json_path.replace(".json", ".md")
md = ["# NexusAI Core-01 Run3 Training Report","",
      "- Resume from: `%s` (step %s)" % (SRC_CKPT, START_STEP),
      "- Output: `%s`" % OUT_DIR,
      "- rc=%s elapsed=%.0fs GPU=%s" % (r.returncode, el, prop.name),
      "- final_step=%s epoch=%s status=%s" % (rep.get("final_step"),rep.get("final_epoch"),rep.get("final_status")),
      "- train_loss=%s val_loss=%s" % (rep.get("final_train_loss"),rep.get("final_val_loss")),
      "- checkpoints: %s" % [c["file"] for c in rep["ckpts"]], "",
      "```json", json.dumps(rep, indent=1), "```"]
open(md_path,"w").write("\n".join(md))
print("\n==== RUN3 DONE rc=%s elapsed=%.0fs ====" % (r.returncode, el))
print(json.dumps(rep, indent=1)[:2000])
print("JSON report ->", json_path); print("MD report ->", md_path)
