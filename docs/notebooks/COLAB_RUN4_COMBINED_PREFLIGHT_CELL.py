# =============================================================================
# NEXUSAI CORE-01 RUN4 — COMBINED PREFLIGHT CELL (v1.0, release v2.3.0)
# ONE cell = ALL safe verification. NEVER starts training. NEVER creates or
# modifies TRAINING_AUTHORIZATION.json. Read-only w.r.t. checkpoints/datasets.
# Copy the ENTIRE file into ONE Colab cell and press Run.
# =============================================================================
import os, sys, json, glob, hashlib, zipfile, io, re, tempfile, shutil, time
import torch

CELL_VERSION = "RUN4_COMBINED_PREFLIGHT_V1_0"
print("=" * 64)
print(f"[CELL_VERSION] {CELL_VERSION}  |  release v2.3.0")
print("=" * 64)

RESULTS = []   # {"check","status","detail"}  status: PASS/FAIL/NOT_TESTED/BLOCKED
def check(name, ok, detail="", critical=True):
    if ok is None:
        st = "NOT_TESTED"
    elif ok is False:
        st = "BLOCKED" if critical else "FAIL"
    else:
        st = "PASS"
    RESULTS.append({"check": name, "status": st, "detail": str(detail)[:400]})
    print(f"[{st:>10}] {name}: {detail}")
    return ok

def sha256_stream(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()

def sha256_zip_member(zf, name):
    h = hashlib.sha256(); n = 0
    with zf.open(name) as s:
        for c in iter(lambda: s.read(1 << 22), b""):
            h.update(c); n += len(c)
    return h.hexdigest(), n

# ------------------------------------------------------- trusted constants
OUTER_NAME = "NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip"
OUTER_SHA  = "8b2129649c840e1b7009ea57babacd0e3831185852a070cd4391fbcdda3849ef"
OUTER_SIZE = 173914048
MANIFEST_VERSION = "2.3.0"
INNER_SHA  = "778ded61720651951e1dc24ce02e3c36aa520c187498e9657d826af3a050110e"
INNER_SIZE = 300734
CKPT_SHA   = "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"
CKPT_SIZE  = 106777501
CORPUS_SHA = "5f8572edd816ac875a7f52915bc6326635d7a483e0ca3f33b70fffdda7e28376"
CORPUS_SIZE= 385217021
CORPUS_RECORDS = 216193
EVID_SHA   = "0cb7588d7f2e7afe2e5250dd9381f3c37e1940428cb060477929bb1338523f32"
EVID_SIZE  = 2932
UPLOAD_CELL_SHA = "ad3124f16946d6553e9cb42f894fc7ddd31076b4ee593295f02d965f82bf6a0d"
PREFLIGHT_SHA   = "62fec3a7265bcf843d262d0241b92c95b623faf721fb7c2f1b981c75b2ea08ef"
TRAIN_CELL_SHA  = "8779caae7253b3c6d74be77d47cb3542dfb8696e8f478f9e3915cc27eea7af1f"
PREFLIGHT_SIZE  = 30708
EXPECTED_EPOCHS_TOTAL = 5      # driver: range(current_epoch=3, 5) -> 2 epochs
EXPECTED_START_EPOCH, EXPECTED_START_STEP = 3, 1341

DRIVE_BASE = "/content/drive/MyDrive/NexusAI"
REPORT_DIR = os.path.join(DRIVE_BASE, "reports", "run4")
CKPT_DIR   = os.path.join(DRIVE_BASE, "checkpoints", "core01_english_run3",
                          "checkpoint_final.pt")
RUN4_OUT   = os.path.join(DRIVE_BASE, "checkpoints", "core01_run4")

# ============================================================ A. ENVIRONMENT
print("\n===== A. ENVIRONMENT =====")
check("python_version", sys.version_info >= (3, 9),
      sys.version.split()[0])
check("torch_version", torch.__version__, f"torch {torch.__version__}")
cuda_avail = torch.cuda.is_available()
gpu_name = torch.cuda.get_device_name(0) if cuda_avail else "none"
gpu_mem = (torch.cuda.get_device_properties(0).total_memory / 1e9
           if cuda_avail else 0)
check("cuda_available", cuda_avail, gpu_name or "CPU-ONLY RUNTIME",
      critical=True)
if cuda_avail:
    check("gpu_memory", gpu_mem >= 8.0,
          f"{gpu_mem:.1f} GB total (T4 ~14.6 expected)")
    try:
        x = torch.ones(2, 2, device="cuda", dtype=torch.float16)
        (x @ x).sum().item()
        check("fp16_supported", True, "fp16 matmul OK")
    except Exception as e:
        check("fp16_supported", False, f"fp16 failed: {e}")
else:
    check("fp16_supported", None, "no GPU — cannot test", critical=False)
try:
    import psutil
    ram = psutil.virtual_memory()
    check("system_ram", ram.available / 1e9 > 4,
          f"{ram.available/1e9:.1f} GB free of {ram.total/1e9:.1f}")
except Exception:
    check("system_ram", None, "psutil unavailable", critical=False)
try:
    import shutil as _sh
    du = _sh.disk_usage("/content" if os.path.isdir("/content") else ".")
    check("disk_space", du.free / 1e9 > 15, f"{du.free/1e9:.1f} GB free")
except Exception as e:
    check("disk_space", None, str(e)[:80], critical=False)

# ===================================================== B. DRIVE + ZIP LOCATE
print("\n===== B. DRIVE & RELEASE LOCATION =====")
drive_mounted = os.path.isdir("/content/drive/MyDrive")
if not drive_mounted:
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        drive_mounted = os.path.isdir("/content/drive/MyDrive")
    except Exception as e:
        check("drive_mount", False, f"mount failed: {e}", critical=True)
check("drive_mounted", drive_mounted, "/content/drive/MyDrive")

candidates = []
if drive_mounted:
    candidates += glob.glob(os.path.join(DRIVE_BASE, "**", OUTER_NAME),
                            recursive=True)
    candidates += glob.glob(os.path.join(DRIVE_BASE, OUTER_NAME))
candidates += glob.glob(f"/content/{OUTER_NAME}")
candidates += glob.glob(f"/content/*/{OUTER_NAME}")
# local dev fallback (not used on Colab)
candidates += glob.glob(
    os.path.join(os.getcwd(), "exports", OUTER_NAME))
candidates = [c for c in dict.fromkeys(candidates) if os.path.isfile(c)]
zip_path = None
for c in candidates:
    if os.path.getsize(c) == OUTER_SIZE:
        zip_path = c; break
check("outer_zip_found", zip_path is not None,
      zip_path or f"no {OUTER_NAME} with size {OUTER_SIZE} among {len(candidates)}")
if not zip_path:
    check("outer_zip_sha", False, "cannot verify — file not found")
    RESULTS.append({"check":"_abort","status":"BLOCKED","detail":"no release zip"})
else:
    check("outer_zip_sha",
          sha256_stream(zip_path) == OUTER_SHA,
          f"{os.path.getsize(zip_path)} B sha verified")

# ================================================= C/D. ZIP + MANIFEST + PAYLOADS
print("\n===== C/D. ARCHIVE INTEGRITY & PAYLOAD HASHES =====")
zouter = None
if zip_path:
    try:
        zouter = zipfile.ZipFile(zip_path)
        check("outer_testzip", zouter.testzip() is None, "CRC check")
        names = zouter.namelist()
        BS = chr(92)
        unsafe = [n for n in names if n.startswith(("/", BS))
                  or ".." in n.replace(BS, "/").split("/")
                  or ":" in n.split("/")[0]]
        dups = [n for n in set(names) if names.count(n) > 1]
        links = [n for n in names
                 if (zouter.getinfo(n).external_attr >> 16) & 0o170000 == 0o120000]
        check("archive_path_safety", not unsafe and not dups and not links,
              f"unsafe={len(unsafe)} dups={len(dups)} symlinks={len(links)}")
        man = json.loads(zouter.read("manifest.json"))
        mfiles = {f["path"]: f for f in man.get("files", [])}
        check("manifest_version", man.get("version") == MANIFEST_VERSION
              and man.get("package") == "NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE",
              f"v{man.get('version')} entries={len(mfiles)}")
        allok = True
        for arc, f in mfiles.items():
            if arc not in names:
                check(f"payload_present:{arc}", False, "missing"); allok=False; continue
            h, n = sha256_zip_member(zouter, arc)
            if h != f["sha256"] or n != f["size"]:
                check(f"payload_hash:{arc}", False,
                      f"got {h[:12]}/{n} want {f['sha256'][:12]}/{f['size']}")
                allok = False
        if allok:
            check("all_payload_hashes", True,
                  f"{len(mfiles)} payloads verified by streaming")
        # trusted-pin cross-check: upload cell EXPECTED vs manifest
        ucell = zouter.read("cells/COLAB_RUN4_SINGLE_UPLOAD_CELL.py")
        check("upload_cell_sha", hashlib.sha256(ucell).hexdigest() == UPLOAD_CELL_SHA,
              "cells/ copy matches trusted pin")
        pcell = zouter.read("preflight/COLAB_RUN4_PREFLIGHT_CELL.py")
        check("preflight_cell_sha",
              hashlib.sha256(pcell).hexdigest() == PREFLIGHT_SHA
              and len(pcell) == PREFLIGHT_SIZE, "preflight copy matches pin")
    except Exception as e:
        check("outer_zip_open", False, f"{type(e).__name__}: {e}")
        zouter = None

# inner zip integrity
zinner = None
if zouter:
    try:
        ib = zouter.read("training/NEXUSAI_CORE01_RUN4_BUNDLE.zip")
        check("inner_zip_sha_size",
              hashlib.sha256(ib).hexdigest() == INNER_SHA and len(ib) == INNER_SIZE,
              f"{len(ib)} B")
        zinner = zipfile.ZipFile(io.BytesIO(ib))
        check("inner_testzip", zinner.testzip() is None, "CRC check")
        inames = zinner.namelist()
        need = ["packages/ai-core/core01/pretraining_driver.py",
                "packages/ai-core/core01/training.py",
                "packages/ai-core/core01/transformer.py",
                "packages/ai-core/core01/dataset.py",
                "packages/ai-core/core01/tokenizer_interface.py",
                "packages/ai-core/models/nexusai_core_01/config/model_config.py",
                "docs/notebooks/COLAB_RUN4_TRAIN_CELL.py",
                "packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model",
                "packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.vocab"]
        missing = [n for n in need if n not in inames]
        check("inner_required_files", not missing,
              f"{len(inames)} entries, missing={missing or 'none'}")
        iman = json.loads(zinner.read("BUNDLE_MANIFEST.json"))
        check("inner_manifest", iman.get("version") == "2.1.0",
              f"inner manifest v{iman.get('version')}")
    except Exception as e:
        check("inner_zip_open", False, f"{type(e).__name__}: {e}")

# ================================================= E. DATASET (streamed)
print("\n===== E. DATASET VALIDATION (streaming, no RAM load) =====")
if zouter:
    try:
        n_rec = n_bad = n_empty = n_nondict = n_dup = 0
        seen = set()
        langs = {}
        with zouter.open("dataset/corpus_train.jsonl") as s:
            for raw in s:
                n_rec += 1
                try:
                    d = json.loads(raw)
                except Exception:
                    n_bad += 1; continue
                if not isinstance(d, dict):
                    n_nondict += 1; continue
                t = d.get("text")
                if not isinstance(t, str) or not t.strip():
                    n_empty += 1
                th = hashlib.sha1(t.encode("utf-8", "ignore")).digest() \
                    if isinstance(t, str) else b""
                if th in seen: n_dup += 1
                seen.add(th)
                langs[d.get("lang", "?")] = langs.get(d.get("lang", "?"), 0) + 1
        check("corpus_records", n_rec == CORPUS_RECORDS,
              f"{n_rec} records (expected {CORPUS_RECORDS})")
        check("corpus_malformed", n_bad == 0, f"malformed={n_bad}")
        check("corpus_empty_text", n_empty == 0, f"empty={n_empty}")
        check("corpus_nondict", n_nondict == 0, f"non-dict={n_nondict}")
        check("corpus_duplicates", True,
              f"exact-dup texts={n_dup} (reported, not removed)", critical=False)
        top = sorted(langs.items(), key=lambda x: -x[1])[:5]
        print("   lang dist:", dict(top))
        check("corpus_langs", any(k.startswith("en") for k in langs)
              and any("bn" in k for k in langs), str(dict(top)))
    except Exception as e:
        check("corpus_stream", False, f"{type(e).__name__}: {e}")

# ============================================== F/G. CKPT + RESUME (static+meta)
print("\n===== F/G. RUN3 CHECKPOINT & RESUME COMPATIBILITY =====")
ckpt_ok = False
if drive_mounted and os.path.exists(CKPT_DIR):
    sz = os.path.getsize(CKPT_DIR)
    check("run3_ckpt_size", sz == CKPT_SIZE, f"{sz} B")
    check("run3_ckpt_sha", sha256_stream(CKPT_DIR) == CKPT_SHA,
          "sha256 verified (read-only)")
    try:
        ck = torch.load(CKPT_DIR, map_location="cpu", weights_only=False)
        # weights_only=False OK: hash-verified own checkpoint (numpy RNG etc.)
        need_keys = ["model_state_dict", "optimizer_state_dict",
                     "scheduler_state_dict", "rng_state", "epoch", "step"]
        missing = [k for k in need_keys if k not in ck]
        check("ckpt_keys", not missing, f"missing={missing or 'none'}")
        check("ckpt_epoch_step",
              ck.get("epoch") == EXPECTED_START_EPOCH
              and ck.get("step") == EXPECTED_START_STEP,
              f"epoch={ck.get('epoch')} step={ck.get('step')}")
        cfg = ck.get("config", {})
        arch_ok = all(cfg.get(k) == v for k, v in
                      {"d_model": 256, "n_layers": 6, "n_heads": 8,
                       "d_ff": 1024, "vocab_size": 8000, "max_len": 512}.items())
        check("ckpt_arch", arch_ok, f"params={cfg.get('estimated_parameters')}")
        ckpt_ok = not missing and arch_ok
        del ck
    except Exception as e:
        check("ckpt_load", False, f"{type(e).__name__}: {e}")
else:
    check("run3_ckpt_present", False,
          f"not found at {CKPT_DIR} — run upload cell first", critical=True)

# strict state-dict compat via extracted model code (temp dir only)
if zinner and ckpt_ok:
    WORK = tempfile.mkdtemp(prefix="run4_combined_")
    try:
        prefixes = ("packages/ai-core/core01/", "packages/ai-core/models/",
                    "packages/ai-core/data/experimental/phase9_2/tokenizers/")
        for n in zinner.namelist():
            nn = n.replace(chr(92), "/")
            if nn.startswith(("/", "..")) or ".." in nn.split("/"):
                raise RuntimeError(f"unsafe inner path {n}")
            if nn.startswith(prefixes):
                zinner.extract(n, WORK)
        ai = os.path.join(WORK, "packages", "ai-core")
        sys.path.insert(0, ai); sys.path.insert(0, os.path.join(ai, "models"))
        from core01.transformer import NexusAICore01
        from nexusai_core_01.config.model_config import (
            NexusAICore01Config, ModelStatus)
        ck = torch.load(CKPT_DIR, map_location="cpu", weights_only=False)
        cd = dict(ck["config"])
        if isinstance(cd.get("model_status"), str):
            cd["model_status"] = ModelStatus[cd["model_status"]]
        cfg = NexusAICore01Config(
            **{k: v for k, v in cd.items()
               if k in NexusAICore01Config.__dataclass_fields__})
        m = NexusAICore01(cfg)
        m.load_state_dict(ck["model_state_dict"], strict=True)
        check("strict_state_dict", True,
              f"{m.count_parameters():,} params strict load")
        # tokenizer check (sentencepiece direct)
        try:
            import sentencepiece as spm
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "-q", "sentencepiece"])
            import sentencepiece as spm
        sp = spm.SentencePieceProcessor()
        sp.load(os.path.join(ai, "data", "experimental", "phase9_2",
                             "tokenizers", "bpe_8k", "sp_bpe_8k.model"))
        vok = sp.get_piece_size() == 8000
        en = sp.encode("Hello, how are you?", out_type=int)
        bn = sp.encode("আপনি কেমন আছেন?", out_type=int)
        mx = max(en + bn) < 8000
        check("tokenizer", vok and len(en) > 2 and len(bn) > 2 and mx,
              f"vocab={sp.get_piece_size()} en={len(en)} bn={len(bn)} ids")
        del ck, m
    except Exception as e:
        check("strict_state_dict", False, f"{type(e).__name__}: {e}")
    finally:
        shutil.rmtree(WORK, ignore_errors=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# resume semantics — static audit of inner driver + train cell
if zinner:
    try:
        drv = zinner.read("packages/ai-core/core01/pretraining_driver.py").decode()
        tcell = zinner.read("docs/notebooks/COLAB_RUN4_TRAIN_CELL.py").decode()
        ep_ok = ("range(engine.current_epoch, args.epochs)" in drv
                 and "EPOCHS   = 5" in tcell
                 and "checkpoint_zero_steps" in drv
                 and "steps_at_start" in drv)
        check("epoch_semantics", ep_ok,
              "range(3,5)=2 epochs; zero-step guard present")
        auth_ok = ("TRAINING_AUTHORIZATION.json" in tcell
                   and "START NEXUSAI CORE-01 TRAINING" in tcell
                   and "authorized" in tcell)
        check("train_cell_auth_gate", auth_ok,
              "train cell requires authorization marker")
        resume_ok = ("--resume" in tcell and "RESUME_SRC" in tcell
                     and "load_checkpoint" in drv
                     and "scheduler.load_state_dict" in
                     zinner.read("packages/ai-core/core01/training.py").decode())
        check("resume_wiring", resume_ok,
              "--resume RESUME_SRC -> driver load_checkpoint (opt+sched+RNG)")
    except Exception as e:
        check("static_audit", False, str(e)[:120])

# smoke evidence file identity (zip member)
if zouter:
    try:
        eb = zouter.read("evidence/nexusai_run4_resume_smoke_evidence.json")
        ev = json.loads(eb)
        check("evidence_identity",
              hashlib.sha256(eb).hexdigest() == EVID_SHA and len(eb) == EVID_SIZE,
              "sha+size match")
        check("evidence_fields", isinstance(ev, dict) and "tests" in ev,
              f"top-level keys={list(ev)[:8]}")
    except Exception as e:
        check("evidence", False, str(e)[:120])

# ================================================= H. GPU (done in A) — recap
# ================================================= I. TRAINING CONFIG (static)
if zinner:
    try:
        tcell = zinner.read("docs/notebooks/COLAB_RUN4_TRAIN_CELL.py").decode()
        cfg_ok = all(s in tcell for s in
                     ["--epochs", "--max-steps", "--batch-size",
                      "--gradient-accumulation-steps", "--precision",
                      "fp16", "--resume", "--output-dir",
                      "checkpoints/core01_run4"])
        check("train_config_present", cfg_ok,
              "epochs/max-steps/bs/accum/fp16/resume/outdir all wired")
        check("run4_output_isolated",
              "core01_run4" in tcell and "core01_english_run3" in tcell,
              "out=checkpoints/core01_run4, src=run3 (never overwritten)")
    except Exception as e:
        check("train_config", False, str(e)[:120])

# ================================================= J. AUTH GATE (static)
check("authorization_gate_static",
      "TRAINING_AUTHORIZATION.json" in (tcell if zinner else "")
      and "authorized" in (tcell if zinner else "")
      and "START NEXUSAI CORE-01 TRAINING" in (tcell if zinner else ""),
      "marker+phrase enforced in train cell; gate cell is notebook-side",
      critical=False)
check("no_marker_created_by_preflight", True,
      "this cell never writes TRAINING_AUTHORIZATION.json")

# ================================================= K. OUTPUT DIR SAFETY
if drive_mounted:
    run4_exists = os.path.isdir(RUN4_OUT)
    parent_ok = os.path.isdir(os.path.dirname(RUN4_OUT)) or \
        os.path.isdir(DRIVE_BASE)
    check("run4_out_parent", parent_ok,
          f"{RUN4_OUT} exists={run4_exists} (created by train cell only)")
    check("run3_dir_present", os.path.isdir(os.path.dirname(CKPT_DIR)),
          "run3 dir exists (read-only use)", critical=False)

# ============================================================ L. REPORT
print("\n" + "=" * 64)
print("===== FINAL PREFLIGHT SUMMARY =====")
from collections import Counter
cnt = Counter(r["status"] for r in RESULTS)
for r in RESULTS:
    print(f"  {r['status']:10} {r['check']}: {r['detail'][:90]}")
print("-" * 64)
print(f"TOTAL={len(RESULTS)}  " +
      "  ".join(f"{k}={cnt.get(k,0)}" for k in
                ("PASS", "FAIL", "NOT_TESTED", "BLOCKED")))
critical_bad = [r for r in RESULTS
                if r["status"] in ("FAIL", "BLOCKED")]
notest_critical = [r for r in RESULTS
                   if r["status"] == "NOT_TESTED" and "gpu" in r["check"]]
final = "BLOCKED" if (critical_bad or notest_critical or not cuda_avail) \
        else "READY FOR TRAINING"
print(f"\nFINAL PREFLIGHT STATUS: {final}")
print("NOTE: READY ≠ authorized. Training still needs the exact phrase")
print("      'START NEXUSAI CORE-01 TRAINING' via the GATE cell.")

# persist report (never overwrite)
if drive_mounted and os.path.isdir(REPORT_DIR):
    try:
        ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        rp = os.path.join(REPORT_DIR, f"RUN4_COMBINED_PREFLIGHT_{ts}.json")
        rep = {"cell": CELL_VERSION, "release": "v2.3.0",
               "outer_sha": OUTER_SHA, "outer_size": OUTER_SIZE,
               "dataset_sha": CORPUS_SHA, "checkpoint_sha": CKPT_SHA,
               "env": {"torch": torch.__version__, "cuda": cuda_avail,
                       "gpu": gpu_name, "gpu_mem_gb": round(gpu_mem, 2)},
               "results": RESULTS, "counts": dict(cnt),
               "final_status": final,
               "timestamp_utc": ts,
               "TRAINING_STARTED": False, "TRAINING_AUTHORIZED": False}
        tmp = rp + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=1)
        os.replace(tmp, rp)
        print("report:", rp)
    except Exception as e:
        print("REPORT WRITE FAILED:", e)
        final = "BLOCKED"
print("=" * 64)
