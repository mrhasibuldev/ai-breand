# =============================================================================
# NEXUSAI CORE-01 — ONE-CELL COLAB INITIALIZATION (fresh account)
# Upload ZIP -> verify SHA256 -> extract -> deps -> Drive -> run GATE cell.
# Does NOT start training.
# Expected ZIP SHA256: see BUNDLE_SHA256 below (update after rebuild)
# =============================================================================
import os, sys, json, hashlib, zipfile, subprocess, importlib

BUNDLE_NAME   = "NEXUSAI_CORE01_COLAB_TRAINING_BUNDLE.zip"
DEST          = "/content/nexusai"
# NOTE: a zip cannot contain its own sha256 (self-reference). Integrity is
# verified via testzip() + internal BUNDLE_MANIFEST.json consistency instead.
# The authoritative zip SHA256 is published in the delivery report.

# ---------- 1. upload ----------
from google.colab import files
print("Select the bundle ZIP:", BUNDLE_NAME)
up = files.upload()
if BUNDLE_NAME not in up:
    # accept whatever single zip was uploaded
    zips = [k for k in up.keys() if k.endswith(".zip")]
    assert len(zips) == 1, "expected exactly one zip upload, got %s" % list(up.keys())
    src = zips[0]
else:
    src = BUNDLE_NAME

# ---------- 2. verify integrity + manifest consistency ----------
sha = hashlib.sha256(open(src,'rb').read()).hexdigest()
print("uploaded sha256:", sha, "(compare with delivery report)")
z = zipfile.ZipFile(src); bad = z.testzip()
assert bad is None, "corrupt zip member: %s" % bad
names = z.namelist()
required = [
 "packages/ai-core/core01/pretraining_driver.py",
 "packages/ai-core/core01/transformer.py",
 "packages/ai-core/models/nexusai_core_01/config/model_config.py",
 "packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model",
 "packages/ai-core/data/english_first/english_train.json",
 "packages/ai-core/data/english_first/english_validation.json",
 "docs/notebooks/COLAB_MASTER_GATE_CELL.py",
 "docs/notebooks/COLAB_ENGLISH_TRAIN_CELL.py",
 "docs/notebooks/COLAB_INIT_CELL.py",
]
missing = [r for r in required if r not in names]
assert not missing, "bundle missing required entries: %s" % missing
# internal manifest consistency: every manifest file hash must match zip content
man = json.loads(z.read("BUNDLE_MANIFEST.json").decode())
bad_hash = [f for f,info in man["files"].items()
            if hashlib.sha256(z.read(f)).hexdigest() != info["sha256"]]
assert not bad_hash, "manifest/hash mismatch: %s" % bad_hash
print("zip verified:", len(names), "entries, manifest consistent")

# ---------- 3. extract (no deletion of unrelated dirs) ----------
os.makedirs(DEST, exist_ok=True)
z.extractall(DEST)
print("extracted to", DEST)

# ---------- 4. deps (only missing ones) ----------
for pkg in ("sentencepiece", "pyarrow"):
    try:
        importlib.import_module(pkg); print(pkg, "already installed")
    except ImportError:
        subprocess.run([sys.executable,"-m","pip","install","-q",pkg], check=True)
        print(pkg, "installed")

# ---------- 5. Drive ----------
from google.colab import drive
try:
    drive.mount("/content/drive")
except Exception as e:
    print("drive mount issue:", e)
for d in ["reports","checkpoints/core01_english","data","audit_reports"]:
    os.makedirs(os.path.join("/content/drive/MyDrive/NexusAI", d), exist_ok=True)
print("drive dirs ready")

# ---------- 6. env summary ----------
import torch
print("\npython:", sys.version.split()[0], "| torch:", torch.__version__,
      "| cuda build:", torch.version.cuda, "| cuda avail:", torch.cuda.is_available())
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print("GPU:", p.name, "VRAM %.2f GB" % (p.total_memory/1e9))

# ---------- 7. run gate ----------
print("\n===== RUNNING MASTER GATE =====")
gate = os.path.join(DEST, "docs/notebooks/COLAB_MASTER_GATE_CELL.py")
code = open(gate, encoding="utf-8").read()
exec(compile(code, gate, "exec"), {"__name__": "__main__"})
