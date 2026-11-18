# Build NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip (manifest v2.1.0)
# Reproducible release builder. Run from repo root:
#   python exports/build_run4_single_upload.py
# Prints final outer ZIP size + SHA-256 -> inject into notebook cell.
import zipfile, hashlib, json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "exports", "NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip")

ENTRIES = [
    ("README_RUN4.md", "exports/README_RUN4.md", "markdown", False),
    ("cells/COLAB_RUN4_SINGLE_UPLOAD_CELL.py",
     "docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py", "python", False),
    ("preflight/COLAB_RUN4_PREFLIGHT_CELL.py",
     "docs/notebooks/COLAB_RUN4_PREFLIGHT_CELL.py", "python", True),
    ("training/NEXUSAI_CORE01_RUN4_BUNDLE.zip",
     "exports/NEXUSAI_CORE01_RUN4_BUNDLE_v4.zip", "zip", True),
    ("dataset/corpus_train.jsonl",
     "packages/ai-core/data/phase2/run4_corpus/corpus_train.jsonl", "jsonl", True),
    ("evidence/nexusai_run4_resume_smoke_evidence.json",
     "eval_reports/nexusai_run4_resume_smoke_evidence.json", "json", True),
    ("checkpoint/checkpoint_final.pt",
     "packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt",
     "checkpoint", True),
]

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()

def main():
    files = []
    for arc, src, typ, req in ENTRIES:
        sp = os.path.join(ROOT, src)
        if not os.path.exists(sp):
            sys.exit(f"MISSING SOURCE: {sp}")
        files.append({"path": arc, "source": src, "size": os.path.getsize(sp),
                      "sha256": sha256_file(sp), "type": typ,
                      "required": req, "purpose": typ})
    man = {"package": "NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE",
           "version": "2.3.0",
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "files": files}
    tmp = OUT + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("manifest.json", json.dumps(man, indent=1))
        for arc, src, *_ in ENTRIES:
            z.write(os.path.join(ROOT, src), arc)
    # verify before promoting
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        for f in files:
            h = hashlib.sha256()
            with z.open(f["path"]) as s:
                for c in iter(lambda: s.read(1 << 22), b""):
                    h.update(c)
            assert h.hexdigest() == f["sha256"], f"hash mismatch {f['path']}"
    os.replace(tmp, OUT)
    size = os.path.getsize(OUT)
    print("OUTER_ZIP:", OUT)
    print("SIZE:", size)
    print("SHA256:", sha256_file(OUT))
    for f in files:
        print(f"  {f['path']:55} {f['size']:>12} {f['sha256'][:16]}")

if __name__ == "__main__":
    main()
