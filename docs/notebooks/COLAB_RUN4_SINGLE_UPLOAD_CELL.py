# =============================================================================
# NEXUSAI CORE-01 RUN4 — SINGLE UPLOAD CELL v3.0 (Colab, self-contained)
# ONE ZIP in -> verify everything -> stage to Drive -> report. NO TRAINING.
# Manifest-driven extraction (exact archive paths), streaming SHA-256
# (385MB corpus never fully loaded), payload hashes are the trust anchor.
# Idempotent: identical files reused, conflicts stop safely.
# CELL_VERSION printed first — stale cells are detectable.
# =============================================================================
import os, sys, json, glob, hashlib, zipfile, shutil, tempfile, re
from datetime import datetime

CELL_VERSION = "v3.1"
print(f"[CELL_VERSION] {CELL_VERSION} — Run4 single-upload validator")

# Trusted release identity. The NOTEBOOK-embedded copy has these injected
# with the real values; the copy inside the ZIP keeps the placeholder
# (self-reference is impossible — a file cannot contain its own archive hash).
# Empty/placeholder => outer fingerprint recorded but NOT gated; every
# payload is still verified against the trusted hashes below.
RELEASE_SHA256 = "__RELEASE_SHA256__"
RELEASE_SIZE = 0

REPORT = {"ts": datetime.now().isoformat(), "checks": {}, "files": {},
          "warnings": [], "critical_failures": [],
          "TRAINING_STARTED": False, "TRAINING_AUTHORIZED": False,
          "PREFLIGHT_ONLY": True, "status": "BLOCKED"}

def note(k, v): REPORT["checks"][k] = v
def critical(k, m):
    note(k, "FAIL — " + m); REPORT["critical_failures"].append(f"{k}: {m}")
def warn(k, m):
    note(k, "WARN — " + m); REPORT["warnings"].append(f"{k}: {m}")
def sha256_file(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()
def compute_status():
    if REPORT["critical_failures"]: return "BLOCKED"
    if REPORT["warnings"]: return "READY WITH WARNINGS"
    return "READY FOR USER REVIEW"

BUNDLE_NAME = "NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip"
BUNDLE_STEM = "NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE"
BUNDLE_RE = re.compile(
    r"^" + re.escape(BUNDLE_STEM) + r"(?: \(\d+\))?\.zip$", re.IGNORECASE)

# Trusted payload identities (hardcoded here = trust anchor; the notebook
# cell is the authoritative copy, NOT the copy inside the ZIP).
EXPECTED = {
    "COLAB_RUN4_PREFLIGHT_CELL.py":
        ("62fec3a7265bcf843d262d0241b92c95b623faf721fb7c2f1b981c75b2ea08ef",
         30708, "preflight",
         "/content/nexusai_run4_preflight/COLAB_RUN4_PREFLIGHT_CELL.py"),
    "NEXUSAI_CORE01_RUN4_BUNDLE.zip":
        ("778ded61720651951e1dc24ce02e3c36aa520c187498e9657d826af3a050110e",
         300734, "trainzip",
         "DRIVE:NexusAI/NEXUSAI_CORE01_RUN4_BUNDLE.zip"),
    "corpus_train.jsonl":
        ("5f8572edd816ac875a7f52915bc6326635d7a483e0ca3f33b70fffdda7e28376",
         385217021, "corpus",
         "DRIVE:NexusAI/data/run4/corpus_train.jsonl"),
    "nexusai_run4_resume_smoke_evidence.json":
        ("0cb7588d7f2e7afe2e5250dd9381f3c37e1940428cb060477929bb1338523f32",
         2932, "evidence",
         "DRIVE:NexusAI/nexusai_run4_resume_smoke_evidence.json"),
    "checkpoint_final.pt":
        ("ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830",
         106777501, "checkpoint",
         "DRIVE:NexusAI/checkpoints/core01_english_run3/checkpoint_final.pt"),
}
REQUIRED_KINDS = {"preflight", "trainzip", "corpus", "evidence", "checkpoint"}

# ------------------------------------------------------------- Drive -------
DRIVE_OK = False
try:
    from google.colab import drive
    drive.mount("/content/drive")
    DRIVE_OK = os.path.isdir("/content/drive/MyDrive")
    note("drive_mount", "ok" if DRIVE_OK else "mounted but MyDrive missing")
except Exception as e:
    note("drive_mount", f"FAILED: {e}")
if not DRIVE_OK:
    critical("drive_mount", "Drive unavailable — cannot stage/report safely")
BASE = "/content/drive/MyDrive/NexusAI" if DRIVE_OK else None
REPORT_DIR = os.path.join(BASE, "reports/run4") if BASE else None
if REPORT_DIR:
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
        _probe = os.path.join(REPORT_DIR, ".write_probe")
        with open(_probe, "w") as _f:
            _f.write("ok")
        os.remove(_probe)
    except Exception as e:
        critical("report_dir", f"cannot create/write: {e}"); REPORT_DIR = None

# ------------------------------------------------- 1. obtain the bundle ----
zip_path = None
if DRIVE_OK:
    for cand in (os.path.join(BASE, BUNDLE_NAME),
                 os.path.join("/content/drive/MyDrive", BUNDLE_NAME),
                 os.path.join("/content", BUNDLE_NAME)):
        if os.path.exists(cand):
            zip_path = cand; break
    if zip_path:
        note("bundle_source", f"drive:{zip_path}")
if zip_path is None:
    try:
        from google.colab import files
        note("bundle_source", "upload_widget")
        print("=" * 60)
        print("UPLOAD WIDGET: select ONLY the ZIP file")
        print(f"  -> {BUNDLE_NAME}")
        print("  -> Colab may show '...BUNDLE (1).zip' — that is OK")
        print("  -> DO NOT select .py / .ipynb / .json files")
        print("=" * 60)
        ups = files.upload()
        nonzip = [n for n in ups if not n.lower().endswith(".zip")]
        if nonzip:
            critical("bundle_upload",
                     f"non-ZIP file(s) uploaded: {nonzip} — "
                     f"select {BUNDLE_NAME} instead")
        hits = [os.path.join("/content", n) for n in ups if BUNDLE_RE.match(n)]
        if hits:
            zip_path = hits[0]
        else:
            anyz = [os.path.join("/content", n) for n in ups
                    if n.lower().endswith(".zip")]
            if anyz:
                critical("bundle_name",
                         f"unrelated zip uploaded: {anyz[0]} — expected "
                         f"{BUNDLE_NAME} (or Colab ' (N)' duplicate suffix)")
    except Exception as e:
        critical("bundle_upload", f"upload failed: {e}")

if not zip_path or not os.path.exists(zip_path):
    critical("bundle_zip", f"{BUNDLE_NAME} not found via Drive or upload")

# ---- outer fingerprint (informational; payload hashes are the trust anchor)
outer_ok = bool(zip_path and os.path.exists(zip_path))
if outer_ok:
    try:
        osz = os.path.getsize(zip_path); osh = sha256_file(zip_path)
        release_pinned = (RELEASE_SHA256 not in ("", "__RELEASE_SHA256__")
                          and RELEASE_SIZE > 0)
        release_match = (osh == RELEASE_SHA256 and osz == RELEASE_SIZE) \
            if release_pinned else None
        REPORT["files"]["outer_bundle"] = {
            "path": zip_path, "size": osz, "sha256": osh,
            "release_pinned": release_pinned,
            "release_match": release_match}
        if release_pinned:
            note("outer_bundle",
                 "PASS" if release_match else "FAIL — not the trusted release")
            if not release_match:
                critical("outer_bundle",
                         f"size={osz} sha={osh[:16]}… != pinned release "
                         f"{RELEASE_SIZE}B/{RELEASE_SHA256[:16]}…")
                outer_ok = False
        else:
            note("outer_bundle",
                 f"recorded {osz}B sha={osh[:16]}… (release sha not pinned "
                 "in this copy; payload hashes remain authoritative)")
        canon = os.path.join("/content", BUNDLE_NAME)
        if os.path.abspath(zip_path) != os.path.abspath(canon):
            try:
                if os.path.exists(canon):
                    if sha256_file(canon) == osh:
                        os.remove(zip_path); zip_path = canon
                    else:
                        critical("bundle_canonical",
                                 f"{canon} exists with different content")
                        outer_ok = False
                else:
                    shutil.copy2(zip_path, canon); zip_path = canon
                note("bundle_canonical", f"ok -> {zip_path}")
            except Exception as e:
                critical("bundle_canonical", f"rename/copy failed: {e}")
                outer_ok = False
    except Exception as e:
        critical("outer_bundle", f"read error: {e}"); outer_ok = False

# ------------------------------------- 2. manifest-driven verify+extract ---
def norm_arc(n):
    return n.replace("\\", "/").lstrip("/")

def is_unsafe(n):
    p = norm_arc(n).split("/")
    return (n.startswith(("/", "\\")) or ".." in p
            or bool(re.match(r"^[A-Za-z]:", n)) or "" in p)

def stream_extract(zf, arc, dst):
    """Stream one member to dst while hashing; returns (sha, size)."""
    h = hashlib.sha256(); size = 0
    with zf.open(arc) as src, open(dst, "wb") as out:
        for c in iter(lambda: src.read(1 << 22), b""):
            h.update(c); out.write(c); size += len(c)
    return h.hexdigest(), size

stage_dir = None
if outer_ok:
    try:
        z = zipfile.ZipFile(zip_path)
        bad = z.testzip()
        names = z.namelist()
        trav = [n for n in names if is_unsafe(n)]
        # reject symlink entries (unix mode S_IFLNK in external_attr)
        links = [n for n in names
                 if (z.getinfo(n).external_attr >> 16) & 0o170000 == 0o120000]
        # reject duplicate archive paths
        dups = [n for n in set(names) if names.count(n) > 1]
        if bad is not None:
            critical("bundle_zip", f"corrupt member: {bad}")
        elif trav:
            critical("bundle_zip", f"unsafe paths: {trav}")
        elif links:
            critical("bundle_zip", f"symlink entries: {links}")
        elif dups:
            critical("bundle_zip", f"duplicate archive paths: {dups}")
        else:
            note("bundle_zip", f"ok — {len(names)} entries, testzip clean")
            # --- manifest is the structural authority ---
            man = None
            for cand in ("manifest.json", "MANIFEST.json"):
                if cand in names:
                    try:
                        man = json.loads(z.read(cand))
                    except Exception as e:
                        critical("manifest", f"unparseable: {e}")
                    break
            if man is None:
                critical("manifest", "manifest.json missing")
            mfiles = {}
            if isinstance(man, dict):
                for f in man.get("files", []):
                    p = norm_arc(f.get("path", ""))
                    if p:
                        mfiles[p] = f
            # resolve EXPECTED basenames to exactly one manifest path each
            resolved = {}
            for base_name, (exp_sha, exp_size, kind, stage) in EXPECTED.items():
                hits = [p for p in mfiles
                        if p.rsplit("/", 1)[-1] == base_name]
                if len(hits) != 1:
                    critical("payload_" + kind,
                             f"{base_name}: {len(hits)} manifest matches "
                             f"(need exactly 1): {hits}")
                    continue
                resolved[kind] = hits[0]
            # verify + extract every manifest-declared file (streaming)
            stage_dir = tempfile.mkdtemp(prefix="run4_stage_")
            allok = True
            for arc, f in mfiles.items():
                if arc not in names:
                    critical("manifest_entry", f"declared but absent: {arc}")
                    allok = False; continue
                safe_local = arc.replace("/", "_")
                dst = os.path.join(stage_dir, safe_local)
                try:
                    h, sz = stream_extract(z, arc, dst)
                except Exception as e:
                    critical("extract_" + arc, f"failed: {e}"); allok = False
                    continue
                exp_sha = f.get("sha256"); exp_size = f.get("size")
                ok = (exp_sha is None or h == exp_sha) and \
                     (exp_size is None or sz == exp_size)
                REPORT["files"][arc] = {"size": sz, "sha256": h,
                                        "manifest_sha": exp_sha, "match": ok}
                if not ok:
                    critical("payload_hash_" + arc,
                             f"hash/size mismatch got {h[:16]}…/{sz}")
                    allok = False
            # trusted-identity gate on the 5 required payloads
            for base_name, (exp_sha, exp_size, kind, stage) in EXPECTED.items():
                arc = resolved.get(kind)
                if arc is None:
                    continue  # already critical'd above
                info = REPORT["files"].get(arc, {})
                if not (info.get("sha256") == exp_sha
                        and info.get("size") == exp_size):
                    critical("payload_trusted_" + kind,
                             f"{base_name} != trusted sha/size")
                    allok = False
                else:
                    note("payload_" + kind, f"PASS ({arc})")
            REPORT["checks"]["payloads_verified"] = allok
            # dataset streaming sanity (first 2000 non-empty lines)
            corpus_arc = resolved.get("corpus")
            if corpus_arc and allok:
                try:
                    with z.open(corpus_arc) as cf:
                        cnt = 0; badline = 0
                        for raw in cf:
                            if not raw.strip():
                                continue
                            try:
                                json.loads(raw)
                            except Exception:
                                badline += 1
                            cnt += 1
                            if cnt >= 2000:
                                break
                    note("dataset_stream_sample",
                         f"first {cnt} records parsed, {badline} malformed")
                    if badline:
                        warn("dataset_stream_sample", f"{badline} malformed in sample")
                except Exception as e:
                    warn("dataset_stream_sample", f"sample failed: {e}")
            # -------------------------------- 3. stage to Drive -------------
            if allok and DRIVE_OK:
                for kind, arc in resolved.items():
                    if kind not in REQUIRED_KINDS:
                        continue
                    base_name, (_, _, _, stage) = next(
                        (b, v) for b, v in EXPECTED.items() if v[2] == kind)
                    sp = os.path.join(stage_dir, arc.replace("/", "_"))
                    target = (stage if not stage.startswith("DRIVE:")
                              else os.path.join("/content/drive", stage[6:]))
                    try:
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        if os.path.exists(target):
                            if sha256_file(target) == sha256_file(sp):
                                note("stage_" + kind,
                                     "already present & identical — skip")
                                continue
                            critical("stage_" + kind,
                                     f"target exists with DIFFERENT content: {target}")
                            continue
                        shutil.copy2(sp, target)
                        if sha256_file(target) != sha256_file(sp):
                            critical("stage_verify_" + kind,
                                     "staged copy hash mismatch")
                        else:
                            note("stage_" + kind, f"ok -> {target}")
                    except Exception as e:
                        critical("stage_" + kind, f"copy failed: {e}")
            # -------------------------------- 4. resume-state spot check ---
            if allok and DRIVE_OK:
                ck = os.path.join("/content/drive/MyDrive/NexusAI",
                                  "checkpoints/core01_english_run3/checkpoint_final.pt")
                if os.path.exists(ck):
                    try:
                        import torch
                        d = torch.load(ck, map_location="cpu", weights_only=False)
                        ok = (d.get("epoch") == 3 and d.get("step") == 1341
                              and "optimizer_state_dict" in d
                              and "scheduler_state_dict" in d
                              and "rng_state" in d)
                        note("resume_state",
                             "FULL" if ok else "INCOMPLETE — see fields")
                        REPORT["files"]["resume_state"] = {
                            "epoch": d.get("epoch"), "step": d.get("step"),
                            "status": d.get("model_status"),
                            "has_optimizer": "optimizer_state_dict" in d,
                            "has_scheduler": "scheduler_state_dict" in d,
                            "has_scaler": d.get("grad_scaler_state_dict") is not None,
                            "rng_keys": sorted((d.get("rng_state") or {}).keys()),
                        }
                        if not ok:
                            critical("resume_state", "missing required fields")
                        del d
                    except Exception as e:
                        critical("resume_state", f"load failed: {e}")
                else:
                    critical("resume_state", "checkpoint missing after staging")
        z.close()
    except Exception as e:
        critical("bundle_zip", f"cannot process: {e}")

REPORT["status"] = compute_status()

# ------------------------------------------------------------- report ------
report_paths = {}
if REPORT_DIR:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    def render():
        j = json.dumps(REPORT, indent=1, ensure_ascii=False)
        return {"json": j, "txt": j,
                "md": "# RUN4 SINGLE-UPLOAD REPORT v3\n\n```json\n" + j + "\n```\n"}
    def wp(ext):
        b = os.path.join(REPORT_DIR, f"RUN4_SINGLE_UPLOAD_{stamp}.{ext}")
        p, i = b, 1
        while os.path.exists(p):
            p = b.replace(f".{ext}", f"_{i}.{ext}"); i += 1
        return p
    for ext in ("json", "txt", "md"):
        p = wp(ext)
        try:
            open(p, "w", encoding="utf-8").write(render()[ext])
            report_paths[ext] = p
        except Exception as e:
            critical("report_write", f"{ext}: {e}")
    REPORT["status"] = compute_status()

print("\n================= SINGLE UPLOAD RESULT v3 =================")
print(json.dumps(REPORT["checks"], indent=1, ensure_ascii=False))
print("critical:", REPORT["critical_failures"])
print("warnings:", REPORT["warnings"])
print("reports:", report_paths)
print("STATUS:", REPORT["status"])
print("TRAINING_STARTED:", REPORT["TRAINING_STARTED"],
      "| TRAINING_AUTHORIZED:", REPORT["TRAINING_AUTHORIZED"])
if REPORT["status"] == "READY FOR USER REVIEW":
    print("\nNext: run the preflight cell, then review reports/run4/.")
