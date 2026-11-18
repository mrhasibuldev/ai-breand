# =============================================================================
# NEXUSAI UNIVERSAL — GOOGLE COLAB SETUP & PREFLIGHT CELL (v2)
# One cell: Drive mount -> ZIP locate -> SHA verify -> safe extract -> deps ->
# GPU/CUDA -> dataset+tokenizer -> Run3 strict load -> resume inspect ->
# synthetic dry-run -> JSON report. NEVER starts training.
# Idempotent: safe to re-run.
# =============================================================================
import os, sys, json, glob, hashlib, zipfile, subprocess, time, tempfile

PKG_NAME = "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE"
ZIP_SHA = "f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644"
ZIP_SIZE = 173913680
WORK = "/content/nexusai_pkg"
REPORTS = "/content/nexusai_reports"
os.makedirs(REPORTS, exist_ok=True)

R = []
def rec(name, status, detail=""):
    R.append({"check": name, "status": status, "detail": str(detail)[:300]})
    print(f"[{status:>10}] {name} — {str(detail)[:130]}")

def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()

print("=" * 60)
print("NEXUSAI UNIVERSAL COLAB SETUP & PREFLIGHT v2")
print("=" * 60)

# ---------- 1. Drive mount ----------
try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    rec("drive_mount", "PASS", "/content/drive/MyDrive")
except Exception as e:
    rec("drive_mount", "FAIL", e)

# ---------- 2. Locate ZIP ----------
cands = []
for base in ("/content/drive/MyDrive", "/content"):
    cands += glob.glob(os.path.join(base, "**", PKG_NAME + ".zip"),
                       recursive=True)
cands = [c for c in cands if os.path.getsize(c) == ZIP_SIZE] or cands
zip_path = cands[0] if cands else None
if zip_path:
    rec("zip_locate", "PASS", f"{zip_path} ({len(cands)} candidate(s))")
else:
    rec("zip_locate", "FAIL",
        f"upload {PKG_NAME}.zip to Drive first "
        f"(expect {ZIP_SIZE} bytes)")

# ---------- 3. ZIP SHA-256 ----------
if zip_path:
    h = sha256(zip_path)
    rec("zip_sha256", "PASS" if h == ZIP_SHA else "FAIL", h[:24] + "…")

# ---------- 4. Safe extract ----------
if zip_path:
    try:
        z = zipfile.ZipFile(zip_path)
        bad = z.testzip()
        rec("zip_integrity", "PASS" if bad is None else "FAIL", bad or "clean")
        # path-safety check
        unsafe = [n for n in z.namelist()
                  if n.startswith("/") or ".." in n.split("/")]
        rec("zip_safe_paths", "PASS" if not unsafe else "FAIL",
            f"{len(unsafe)} unsafe" if unsafe else "clean")
        if os.path.exists(WORK):
            import shutil; shutil.rmtree(WORK)
        z.extractall(WORK)
        rec("extract", "PASS", WORK)
    except Exception as e:
        rec("extract", "FAIL", e)

# ---------- 5. Manifest + payload hashes ----------
pkg_root = os.path.join(WORK, PKG_NAME)
man_p = os.path.join(pkg_root, "MANIFEST.json")
if os.path.exists(man_p):
    try:
        man = json.load(open(man_p))
        rec("manifest", "PASS", f"{man.get('file_count')} files")
        bad = []
        for it in man.get("files", []):
            p = os.path.join(pkg_root, it["arc"])
            if not os.path.exists(p) or os.path.getsize(p) != it["size"]:
                bad.append(it["arc"]); continue
            if it["size"] > 50_000_000:      # hash big files only spot-wise
                continue
            if sha256(p) != it["sha256"]:
                bad.append(it["arc"])
        rec("payload_hashes", "PASS" if not bad else "FAIL",
            f"{len(bad)} bad" if bad else "all small files verified")
        # checkpoint full hash (authoritative)
        ck = os.path.join(pkg_root, "checkpoints/verified/core01_run3_checkpoint_final.pt")
        if os.path.exists(ck):
            rec("ckpt_sha256",
                "PASS" if sha256(ck) ==
                "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"
                else "FAIL", "ad515cade…")
        else:
            rec("ckpt_present", "FAIL", "missing")
    except Exception as e:
        rec("manifest", "FAIL", e)
else:
    rec("manifest", "FAIL", "MANIFEST.json not found after extract")

# ---------- 6. Dependencies ----------
need = {"torch": None, "sentencepiece": None, "numpy": None, "psutil": None}
for pkg in need:
    try:
        m = __import__(pkg)
        rec(f"dep_{pkg}", "PASS", getattr(m, "__version__", "?"))
    except ImportError:
        rec(f"dep_{pkg}", "FAIL", "missing — pip install required")

# ---------- 7. GPU / CUDA ----------
try:
    import torch
    if torch.cuda.is_available():
        rec("cuda", "PASS", torch.version.cuda)
        rec("gpu", "PASS",
            f"{torch.cuda.get_device_name(0)} "
            f"{torch.cuda.get_device_properties(0).total_memory/2**30:.1f}GB")
        x = torch.randn(256, 256, device="cuda")
        y = (x @ x).sum().item(); torch.cuda.synchronize()
        torch.cuda.empty_cache()
        rec("cuda_matmul", "PASS" if y == y else "FAIL", "compute ok")
    else:
        rec("cuda", "FAIL", "torch.cuda.is_available()=False — CPU runtime?")
        rec("gpu", "FAIL", "no GPU — Runtime→Change runtime type→T4 GPU")
except Exception as e:
    rec("cuda", "FAIL", e)

# ---------- 8. Synthetic dry-run (model fwd+bwd on CPU-safe tiny batch) ----------
try:
    sys.path.insert(0, os.path.join(pkg_root, "nexusai"))
    sys.path.insert(0, os.path.join(pkg_root, "nexusai", "models"))
    # package layout: nexusai/core01, nexusai/models/nexusai_core_01, nexusai/cloud
    import torch
    from core01.transformer import NexusAICore01
    from nexusai_core_01.config.model_config import (
        NexusAICore01Config, ModelStatus)
    ck_p = os.path.join(pkg_root, "checkpoints/verified/core01_run3_checkpoint_final.pt")
    ck = torch.load(ck_p, map_location="cpu", weights_only=False)
    cd = dict(ck["config"])
    if isinstance(cd.get("model_status"), str):
        cd["model_status"] = ModelStatus[cd["model_status"]]
    cfg = NexusAICore01Config(
        **{k: v for k, v in cd.items()
           if k in NexusAICore01Config.__dataclass_fields__})
    m = NexusAICore01(cfg)
    m.load_state_dict(ck["model_state_dict"], strict=True)
    rec("model_strict_load", "PASS", f"params={m.count_parameters():,}")
    rec("resume_state",
        "PASS" if all(k in ck for k in
        ("optimizer_state_dict","scheduler_state_dict",
         "grad_scaler_state_dict","rng_state")) else "FAIL",
        f"ep{ck.get('epoch')}/step{ck.get('step')}")
    # synthetic forward+backward (2x16 tokens, no dataset)
    m.train()
    ids = torch.randint(0, cfg.vocab_size, (2, 16))
    tgt = torch.randint(0, cfg.vocab_size, (2, 16))
    loss = m(ids, targets=tgt)
    if not isinstance(loss, torch.Tensor):
        loss = loss.loss if hasattr(loss, "loss") else loss[0]
    loss.backward()
    rec("synthetic_bwd", "PASS" if torch.isfinite(loss) else "FAIL",
        f"loss={float(loss):.3f}")
except Exception as e:
    rec("synthetic_dryrun", "FAIL", e)

# ---------- 9. Dataset + tokenizer presence ----------
ds = os.path.join(pkg_root, "datasets/verified_data/corpus_train.jsonl")
tk = os.path.join(pkg_root, "nexusai/tokenizer/sp_bpe_8k.model")
rec("dataset", "PASS" if os.path.exists(ds) and
    os.path.getsize(ds) == 385217021 else "FAIL",
    os.path.getsize(ds) if os.path.exists(ds) else "missing")
rec("tokenizer", "PASS" if os.path.exists(tk) else "FAIL", tk)

# ---------- 10. Report ----------
fails = [c for c in R if c["status"] == "FAIL"]
warns = [c for c in R if c["status"] == "WARN"]
verdict = ("READY" if not fails else "BLOCKED")
out = {"cell": "UNIVERSAL_COLAB_SETUP_V2",
       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "zip_sha_expected": ZIP_SHA, "checks": R,
       "fails": len(fails), "warns": len(warns),
       "verdict": verdict,
       "note": "READY != authorized. Training needs explicit approval."}
rp = os.path.join(REPORTS, f"universal_preflight_{int(time.time())}.json")
with open(rp, "w") as f:
    json.dump(out, f, indent=1)
print("\n" + "=" * 60)
print(f"PREFLIGHT: {verdict}  ({len(R)-len(fails)-len(warns)} pass, "
      f"{len(warns)} warn, {len(fails)} fail)")
print("report:", rp)
print("=" * 60)
