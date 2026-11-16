# =============================================================================
# NEXUSAI CORE-01 — CLONE + CHECKPOINT RECOVERY CELL (Google Colab)
# Clones repo, pulls Run3 checkpoint via Git LFS, verifies SHA-256.
# Safe: read-only against remote; writes only to /content workspace.
# Requires: repo access (public OR Colab Secret GITHUB_TOKEN if private).
# =============================================================================
import os, subprocess, hashlib, json, sys, shutil

REPO = "https://github.com/mrhasibuldev/ai-breand.git"
BRANCH = "main"
CKPT_REL = "packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt"
MANIFEST_REL = "packages/ai-core/models/checkpoints_core01_run3/CHECKPOINT_MANIFEST.json"
EXPECTED_SHA = "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"
EXPECTED_SIZE = 106777501
WORK = "/content/nexusai_repo"
R = {"checks": []}
def rec(name, ok, detail=""):
    R["checks"].append({"check": name, "status": "PASS" if ok else "FAIL",
                        "detail": str(detail)[:300]})
    print(("PASS " if ok else "FAIL ") + name + (" — " + str(detail)[:140] if detail else ""))
    return ok

print("=== NEXUSAI CLONE + CHECKPOINT RECOVERY ===")

# 1. Git LFS
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "git-lfs"],
               check=False)
try:
    subprocess.run(["git", "lfs", "version"], check=True,
                   capture_output=True)
    rec("git-lfs", True)
except Exception:
    subprocess.run(["apt-get", "install", "-y", "git-lfs"],
                   capture_output=True)
    try:
        subprocess.run(["git", "lfs", "install", "--local"], check=True)
        rec("git-lfs", True, "installed via apt")
    except Exception as e:
        rec("git-lfs", False, e)

# 2. Auth for private repo (Colab Secrets -> env)
token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
clone_url = REPO
if token:
    clone_url = REPO.replace("https://", f"https://x-access-token:{token}@")

# 3. Clone (shallow, but LFS needs history? full clone of single branch ok)
if os.path.exists(WORK):
    shutil.rmtree(WORK)
ok = subprocess.run(["git", "clone", "--depth", "1", "-b", BRANCH,
                     clone_url, WORK]).returncode == 0
rec("clone", ok, WORK)
if not ok:
    print("Clone failed — if repo is private, add Colab Secret GITHUB_TOKEN.")
    print(json.dumps(R, indent=1)); raise SystemExit(1)

# 4. LFS pull for checkpoint only
os.chdir(WORK)
r = subprocess.run(["git", "lfs", "pull", "--include", CKPT_REL],
                   capture_output=True, text=True)
rec("lfs pull", r.returncode == 0, (r.stderr or "")[:200])

# 5. Verify checkpoint
ck = os.path.join(WORK, CKPT_REL)
ok = os.path.exists(ck) and os.path.getsize(ck) == EXPECTED_SIZE
rec("ckpt size", ok, os.path.getsize(ck) if os.path.exists(ck) else "missing")
h = hashlib.sha256()
if ok:
    with open(ck, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
rec("ckpt sha256", h.hexdigest() == EXPECTED_SHA, h.hexdigest()[:20])

# 6. Manifest cross-check
mp = os.path.join(WORK, MANIFEST_REL)
if os.path.exists(mp):
    m = json.load(open(mp))
    rec("manifest sha match",
        m.get("sha256") == EXPECTED_SHA, m.get("model_version"))

# 7. Safe structural load (weights_only=False required: numpy RNG state)
try:
    import torch
    obj = torch.load(ck, map_location="cpu", weights_only=False)
    rec("ckpt loads", "model_state_dict" in obj,
        f"ep={obj.get('epoch')} step={obj.get('step')}")
    rec("resume keys", all(k in obj for k in
        ("optimizer_state_dict","scheduler_state_dict",
         "grad_scaler_state_dict","rng_state")))
except Exception as e:
    rec("ckpt loads", False, e)

# 8. Tokenizer
import sentencepiece as spm
sp = spm.SentencePieceProcessor()
tok_rel = "packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model"
tp = os.path.join(WORK, tok_rel)
if os.path.exists(tp):
    sp.load(tp)
    rec("tokenizer vocab", sp.get_piece_size() == 8000, sp.get_piece_size())
    rec("bn encode", len(sp.encode("বাংলাদেশ")) > 0)
else:
    rec("tokenizer file", False, "missing — needed for training")

print("\n==== RECOVERY:", "PASS" if all(c["status"]=="PASS" for c in R["checks"]) else "CHECK FAILURES", "====")
print(json.dumps(R, indent=1)[:1200])
