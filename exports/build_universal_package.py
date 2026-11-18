"""Build NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip — self-contained, verified."""
import os, sys, json, zipfile, hashlib, shutil
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
AI = os.path.join(REPO, "packages", "ai-core")
OUT = os.path.join(REPO, "exports", "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip")
STAGE = os.path.join(REPO, "exports", "_universal_pkg_stage")
ROOT = "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE"

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()

def add(src, arc):
    dst = os.path.join(STAGE, arc)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return {"src": os.path.relpath(src, REPO).replace("\\", "/"),
            "arc": arc.replace("\\", "/"),
            "size": os.path.getsize(src), "sha256": sha256(src)}

def main():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)
    files = []

    # --- code ---
    code = [
        "packages/ai-core/core01/__init__.py",
        "packages/ai-core/core01/transformer.py",
        "packages/ai-core/core01/tokenizer_interface.py",
        "packages/ai-core/core01/dataset.py",
        "packages/ai-core/core01/training.py",
        "packages/ai-core/core01/inference.py",
        "packages/ai-core/core01/evaluation.py",
        "packages/ai-core/core01/pretraining_driver.py",
        "packages/ai-core/cloud/__init__.py",
        "packages/ai-core/cloud/env_manager.py",
        "packages/ai-core/cloud/hardware.py",
        "packages/ai-core/cloud/storage.py",
        "packages/ai-core/cloud/adapters.py",
        "packages/ai-core/cloud/model_loader.py",
        "packages/ai-core/cloud/dataset_manager.py",
        "packages/ai-core/cloud/preflight.py",
        "packages/ai-core/models/nexusai_core_01/__init__.py",
        "packages/ai-core/models/nexusai_core_01/config/__init__.py",
        "packages/ai-core/models/nexusai_core_01/config/model_config.py",
        "docs/notebooks/UNIVERSAL_CLOUD_PREFLIGHT_CELL.py",
    ]
    for rel in code:
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            arc = os.path.join(ROOT, "nexusai", rel.split("packages/ai-core/")[-1]
                               if "packages/ai-core/" in rel else rel)
            files.append(add(p, arc))
        else:
            print("MISSING code:", rel)

    # --- tokenizer ---
    for ext in ("model", "vocab"):
        p = os.path.join(AI, "data/experimental/phase9_2/tokenizers/bpe_8k",
                         f"sp_bpe_8k.{ext}")
        files.append(add(p, os.path.join(ROOT, "nexusai", "tokenizer",
                                         f"sp_bpe_8k.{ext}")))

    # --- checkpoint (Run3, real file) ---
    ck = os.path.join(AI, "models/checkpoints_core01_run3/checkpoint_final.pt")
    files.append(add(ck, os.path.join(ROOT, "checkpoints", "verified",
                                     "core01_run3_checkpoint_final.pt")))
    man = os.path.join(AI, "models/checkpoints_core01_run3",
                       "CHECKPOINT_MANIFEST.json")
    files.append(add(man, os.path.join(ROOT, "checkpoints", "metadata",
                                       "core01_run3_manifest.json")))

    # --- dataset ---
    ds = os.path.join(AI, "data/phase2/run4_corpus/corpus_train.jsonl")
    dm = os.path.join(AI, "data/phase2/run4_corpus/corpus_manifest.json")
    files.append(add(ds, os.path.join(ROOT, "datasets", "verified_data",
                                      "corpus_train.jsonl")))
    if os.path.exists(dm):
        files.append(add(dm, os.path.join(ROOT, "datasets", "manifests",
                                          "corpus_manifest.json")))

    # --- README / VERSION ---
    readme = os.path.join(STAGE, ROOT, "README.md")
    os.makedirs(os.path.dirname(readme), exist_ok=True)
    with open(readme, "w", encoding="utf-8") as f:
        f.write("""# NEXUSAI UNIVERSAL TRAINING PACKAGE
Self-contained Core-01 training package. See docs/ for guides.
Quick start: extract -> run UNIVERSAL_CLOUD_PREFLIGHT_CELL -> verify -> train.
""")
    ver = {"package": "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE",
           "version": "1.0.0", "built": datetime.now(timezone.utc).isoformat(),
           "source_repo": "mrhasibuldev/ai-breand", "source_commit": None}
    import subprocess
    try:
        ver["source_commit"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except Exception:
        pass
    with open(os.path.join(STAGE, ROOT, "VERSION.json"), "w") as f:
        json.dump(ver, f, indent=1)

    # --- manifest + sha256sums ---
    man = {"package": ver["package"], "version": "1.0.0",
           "built": ver["built"], "source_commit": ver["source_commit"],
           "file_count": len(files), "files": files}
    with open(os.path.join(STAGE, ROOT, "MANIFEST.json"), "w") as f:
        json.dump(man, f, indent=1)
    with open(os.path.join(STAGE, ROOT, "SHA256SUMS.txt"), "w") as f:
        for it in files:
            f.write(f"{it['sha256']}  {it['arc']}\n")

    # --- zip ---
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=6) as z:
        for dp, dn, fn in os.walk(STAGE):
            for name in fn:
                p = os.path.join(dp, name)
                z.write(p, os.path.relpath(p, STAGE))
    print("ZIP:", OUT, os.path.getsize(OUT), "bytes,",
          len(files), "payload files")
    print("zip sha256:", sha256(OUT))
    shutil.rmtree(STAGE)

if __name__ == "__main__":
    main()
