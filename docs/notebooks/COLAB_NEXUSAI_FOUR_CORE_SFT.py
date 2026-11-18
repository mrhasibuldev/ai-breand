# =============================================================================
# NEXUSAI FOUR-CORE SFT TRAINING CELL (free Colab GPU)
# Trains Core-02/03/04 specialists with the SAME verified local code path
# (sft_train.py + eval_core.py). Saves checkpoints + eval reports to Drive.
#
# SETUP (one-time, in Colab):
#   1. Upload this repo (or `git clone <repo>` then cd into it) so that
#      packages/ai-core exists at /content/nexusai or ./nexusai.
#   2. Set REPO below to that path.
#   3. Run all cells top-to-bottom. Checkpoints land in
#      /content/drive/MyDrive/NEXUSAI_FOUR_CORE/<core>/checkpoint_final.pt
# =============================================================================
import os, sys, subprocess, json, hashlib, glob

REPO = "/content/nexusai"          # <<< set to your checkout path
AI_CORE = os.path.join(REPO, "packages", "ai-core")
DRIVE_DIR = "/content/drive/MyDrive/NEXUSAI_FOUR_CORE"
EPOCHS = {"core02": 2, "core03": 8, "core04": 20}

# ---- GPU preflight ----
import torch
print("cuda:", torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU-ONLY")
if not torch.cuda.is_available():
    print("WARNING: no GPU — training will be very slow. Connect a T4 runtime.")

try:
    from google.colab import drive
    drive.mount("/content/drive")
except Exception as e:
    print("drive mount failed:", e)
os.makedirs(DRIVE_DIR, exist_ok=True)

sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))

# ---- per-core: train then evaluate (same commands as local runs) ----
RESULTS = {}
for core, data_dir_name in (("core02", "core02_reasoning"),
                            ("core03", "core03_math"),
                            ("core04", "core04_knowledge")):
    data_dir = os.path.join(AI_CORE, "data", data_dir_name)
    out_dir = os.path.join(DRIVE_DIR, core)
    ckpt = os.path.join(out_dir, "checkpoint_final.pt")
    print("=" * 70)
    print(f"TRAIN {core}  data={data_dir}  epochs={EPOCHS[core]}")
    print("=" * 70)
    r = subprocess.run(
        [sys.executable, "-X", "utf8", "-u",
         os.path.join(AI_CORE, "sft_train.py"),
         "--core", core, "--data-dir", data_dir,
         "--out", ckpt, "--epochs", str(EPOCHS[core]),
         "--batch-size", "8", "--lr", "3e-4", "--device", "auto"],
        cwd=AI_CORE)
    if r.returncode != 0 or not os.path.exists(ckpt):
        RESULTS[core] = {"status": "TRAINING_FAILED"}
        continue
    sha = hashlib.sha256(open(ckpt, "rb").read()).hexdigest()
    size = os.path.getsize(ckpt)
    print(f"checkpoint: {ckpt} sha256={sha} bytes={size}")

    report = os.path.join(DRIVE_DIR, f"{core}_eval.json")
    subprocess.run(
        [sys.executable, "-X", "utf8", "-u",
         os.path.join(AI_CORE, "eval_core.py"),
         "--core", core, "--ckpt", ckpt, "--data-dir", data_dir,
         "--out", report, "--max-new-tokens", "80", "--device", "auto"],
        cwd=AI_CORE)
    RESULTS[core] = {"status": "DONE", "sha256": sha, "bytes": size,
                     "eval_report": report}

json.dump(RESULTS, open(os.path.join(DRIVE_DIR, "results.json"), "w"), indent=1)
print(json.dumps(RESULTS, indent=1))
