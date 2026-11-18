# =============================================================================
# NEXUSAI CORE-01 — RUN 4 MULTILINGUAL TRAINING CELL (Colab)
# Resume from verified run3 ckpt -> NEW dir checkpoints_core01_run4/
# Corpus: multilingual corpus_train.jsonl (uploaded to Drive)
# fp16, bs8 x accum4, epochs configurable, global max_steps cap.
# NO overwrites of run1/2/3. NO architecture/tokenizer changes.
# =============================================================================
import os, sys, json, glob, subprocess, time
from datetime import datetime

from google.colab import drive
drive.mount("/content/drive")

AI_CORE = "/content/nexusai/packages/ai-core"
for pp in (AI_CORE, os.path.join(AI_CORE, "models")):
    if pp not in sys.path: sys.path.insert(0, pp)

BASE      = "/content/drive/MyDrive/NexusAI"
SRC_CKPT  = os.path.join(BASE, "checkpoints/core01_english_run3/checkpoint_final.pt")
OUT_DIR   = os.path.join(BASE, "checkpoints/core01_run4")
REPORTS   = os.path.join(BASE, "reports"); os.makedirs(REPORTS, exist_ok=True)

# ---- AUTHORIZATION GATE: refuse to train without explicit user phrase ----
# The gate cell (COLAB_RUN4_TRAINING_GATE_CELL.py) writes this marker ONLY
# after the user types the exact phrase AND preflight is not BLOCKED.
AUTH_FILE = os.path.join(REPORTS, "run4", "TRAINING_AUTHORIZATION.json")
if not os.path.exists(AUTH_FILE):
    print("[BLOCKED] No training authorization marker found.")
    print("Run the TRAINING GATE cell first and type the exact phrase:")
    print("  START NEXUSAI CORE-01 TRAINING")
    raise SystemExit(1)
try:
    _auth = json.load(open(AUTH_FILE, encoding="utf-8"))
except Exception as _e:
    print(f"[BLOCKED] authorization marker unreadable: {_e}")
    raise SystemExit(1)
if not (_auth.get("authorized") is True
        and _auth.get("phrase") == "START NEXUSAI CORE-01 TRAINING"):
    print("[BLOCKED] authorization marker invalid — phrase mismatch.")
    raise SystemExit(1)
print(f"[AUTHORIZED] {_auth.get('authorized_utc')} "
      f"preflight={_auth.get('preflight_status')}")
TRAIN     = os.path.join(BASE, "data/run4/corpus_train.jsonl")   # UPLOAD THIS FILE TO DRIVE FIRST
VAL       = TRAIN   # driver splits internally if needed; else reuse
TEXT_FIELD = "text"

# ---- guards ----
import hashlib
def _sha256_stream(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()

assert os.path.exists(SRC_CKPT), "run3 ckpt missing on Drive"
assert os.path.getsize(SRC_CKPT) == 106777501, "run3 ckpt size mismatch — aborting"
assert _sha256_stream(SRC_CKPT) == \
    "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830", \
    "run3 ckpt sha256 mismatch — aborting"
assert os.path.exists(TRAIN), "corpus_train.jsonl missing — upload to Drive/MyDrive/NexusAI/data/run4/ first"
os.makedirs(OUT_DIR, exist_ok=True)
# Resume-safe: never refuse existing ckpts; pick resume source by priority.
existing = sorted(glob.glob(os.path.join(OUT_DIR,"checkpoint_*.pt")))
if os.path.exists(os.path.join(OUT_DIR,"checkpoint_final.pt")):
    print("run4 already has checkpoint_final.pt — nothing to do"); raise SystemExit(0)
RESUME_SRC = None
for cand in ("checkpoint_last.pt","checkpoint_final.pt"):
    p=os.path.join(OUT_DIR,cand)
    if os.path.exists(p): RESUME_SRC=p; break
if RESUME_SRC is None and existing:
    RESUME_SRC=sorted(existing)[-1]  # latest step ckpt
if RESUME_SRC is None:
    RESUME_SRC = SRC_CKPT  # fresh start from verified run3

# ---- verify resume ckpt BEFORE training ----
import torch
ck = torch.load(RESUME_SRC, map_location="cpu", weights_only=False)
assert "model_state_dict" in ck and "optimizer_state_dict" in ck, \
    "resume ckpt incomplete — aborting"
if RESUME_SRC == SRC_CKPT:
    assert ck.get("step") == 1341, "run3 ckpt step mismatch — aborting"
START_STEP = ck["step"]; START_EPOCH = ck.get("epoch", 0)
print("resume ckpt: %s step=%s epoch=%s status=%s tl=%s vl=%s" % (
    os.path.basename(RESUME_SRC), ck.get("step"), ck.get("epoch"),
    ck.get("model_status"), ck.get("train_loss"), ck.get("val_loss")))
del ck

# EPOCHS is the TOTAL target epoch count (driver: range(current_epoch, epochs)).
# Run3 completed epoch=3 -> 3+2 = 5 gives exactly TWO additional epochs.
EPOCHS   = 5        # 3 completed (run3) + 2 new epochs
MAX_STEPS= 8000     # global cap; resume at step 1341 -> ~6.6K steps available
cmd = [sys.executable, "-m", "core01.pretraining_driver",
       "--train-file", TRAIN, "--text-field", TEXT_FIELD,
       "--val-fraction", "0.02",
       "--epochs", str(EPOCHS), "--max-steps", str(MAX_STEPS),
       "--batch-size", "8", "--gradient-accumulation-steps", "4",
       "--checkpoint-interval", "100", "--eval-interval", "250",
       "--precision", "fp16", "--device", "cuda",
       "--resume", RESUME_SRC,
       "--output-dir", OUT_DIR]
t0=time.time()
rc = subprocess.run(cmd, cwd=AI_CORE).returncode
rep = {"rc": rc, "elapsed_s": round(time.time()-t0,1),
       "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
       "resume_from": RESUME_SRC, "start_step": START_STEP, "start_epoch": START_EPOCH,
       "epochs_cfg": EPOCHS, "max_steps_cfg": MAX_STEPS,
       "corpus": TRAIN, "out_dir": OUT_DIR}
final = os.path.join(OUT_DIR, "checkpoint_final.pt")
if os.path.exists(final):
    fck = torch.load(final, map_location="cpu", weights_only=False)
    rep["final_step"]=fck.get("step"); rep["final_epoch"]=fck.get("epoch")
    rep["final_status"]=fck.get("model_status")
    rep["final_train_loss"]=fck.get("train_loss"); rep["final_val_loss"]=fck.get("val_loss")
    rep["steps_executed"] = (fck.get("step") or 0) - START_STEP
    rep["epochs_executed"] = (fck.get("epoch") or 0) - START_EPOCH
    if rep["steps_executed"] <= 0:
        rep["WARNING"] = "ZERO steps executed — NOT a real training run"
jp = os.path.join(REPORTS, "train_run4_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S"))
json.dump(rep, open(jp,"w"), indent=1)
print("\n==== RUN4 DONE rc=%s ====" % rc)
print("report:", jp)
print(json.dumps(rep, indent=1))
