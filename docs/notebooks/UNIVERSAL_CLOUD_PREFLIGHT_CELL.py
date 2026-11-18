# =============================================================================
# NEXUSAI UNIVERSAL CLOUD PREFLIGHT CELL
# Works on Colab / Kaggle / generic Linux GPU. Read-only; never trains.
# Usage: extract NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip, then run this cell
# with PKG pointing at the extracted folder (default /content/nexusai_pkg).
# =============================================================================
import os, sys, glob, json

PKG = "/content/nexusai_pkg"
if not os.path.isdir(PKG):
    zips = glob.glob("/content/**/*.zip", recursive=True) + \
           glob.glob("/content/drive/MyDrive/**/*.zip", recursive=True)
    print("ZIPs found:", zips[:5])
    # try common extract locations
    for cand in ("/content", "/content/drive/MyDrive"):
        if os.path.isdir(os.path.join(cand, "nexusai")):
            PKG = cand

# locate the cloud package inside extracted tree
for root in (PKG, "/content", os.path.expanduser("~")):
    for dp, dn, fn in os.walk(root):
        if "cloud" in dn and "ai-core" in dp:
            sys.path.insert(0, dp)
            break
        if dp.count(os.sep) - root.count(os.sep) > 4:
            dn[:] = []
    else:
        continue
    break

try:
    from cloud.preflight import run_preflight
except Exception as e:
    print("Could not import cloud.preflight — extract the package first.", e)
    raise

# locate artifacts
ckpt = dataset = None
for dp, dn, fn in os.walk("/content"):
    if "checkpoint_final.pt" in fn and "run3" in dp:
        ckpt = os.path.join(dp, "checkpoint_final.pt")
    if "corpus_train.jsonl" in fn:
        dataset = os.path.join(dp, "corpus_train.jsonl")
    if ckpt and dataset:
        break

rep = run_preflight(
    repo_root="/content",
    checkpoint=ckpt,
    dataset=dataset,
    dataset_sha=("5f8572edd816ac875a7f52915bc6326635d7a483e0ca3f33b70fffdda7e28376"
                 if dataset else None),
    dataset_records=216193 if dataset else None,
)
print("\n==== UNIVERSAL PREFLIGHT:",
      "READY" if rep.ready_for_training else "BLOCKED", "====")
