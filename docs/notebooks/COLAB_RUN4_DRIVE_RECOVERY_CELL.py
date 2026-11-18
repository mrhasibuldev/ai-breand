# =============================================================================
# NEXUSAI RUN4 DRIVE RECOVERY CELL — exhaustive, read-only, CPU-only
# Finds EVERY .pt/.model/.json/.log under MyDrive/NEXUSAI_RUN4 + Drive-wide
# checkpoint_final.pt search, hashes candidates, locates sha 761a5b14…
# Writes inventory JSON to Drive. No GPU, no torch.load on untrusted files.
# =============================================================================
import os, json, glob, hashlib, time

OUT = "/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT"
os.makedirs(OUT, exist_ok=True)
TARGET = "761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1"
RUN3 = "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"

def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    try:
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(chunk), b""):
                h.update(c)
        return h.hexdigest()
    except Exception:
        return None

from google.colab import drive
if not os.path.isdir("/content/drive/MyDrive"):
    drive.mount("/content/drive")

inv = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "run4_dir": "/content/drive/MyDrive/NEXUSAI_RUN4",
       "files": [], "hash_matches": {"run4_target": [], "run3": []},
       "errors": []}

# 1. exhaustive walk of NEXUSAI_RUN4 (no depth limit, no candidate cap)
root = inv["run4_dir"]
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        try:
            st = os.stat(p)
            inv["files"].append({
                "path": p, "size": st.st_size,
                "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                       time.gmtime(st.st_mtime)),
                "ext": os.path.splitext(f)[1].lower()})
        except Exception as e:
            inv["errors"].append(f"{p}: {e}")

# 2. Drive-wide search for checkpoint_final.pt / *.pt >50MB
big = []
for pat in ("/content/drive/MyDrive/**/*.pt",
            "/content/drive/MyDrive/**/*.pth",
            "/content/drive/MyDrive/**/*.safetensors",
            "/content/drive/MyDrive/**/*.bin"):
    for p in glob.glob(pat, recursive=True):
        try:
            if os.path.getsize(p) > 50_000_000:
                big.append(p)
        except Exception:
            pass
big = sorted(set(big))
inv["big_model_files"] = big

# 3. hash every .pt candidate (bounded: ckpt-sized files only)
cands = [f["path"] for f in inv["files"]
         if f["ext"] in (".pt", ".pth", ".bin", ".safetensors")
         and f["size"] > 10_000_000]
cands += [p for p in big if p not in cands]
seen = set(); cands = [p for p in cands if not (p in seen or seen.add(p))]
print(f"hashing {len(cands)} checkpoint-sized candidates…")
for i, p in enumerate(cands):
    d = sha256(p)
    inv["files"].append({"path": p, "sha256": d}) if False else None
    entry = {"path": p, "sha256": d, "size": os.path.getsize(p)}
    inv.setdefault("hashes", []).append(entry)
    tag = ""
    if d == TARGET: tag = " <== RUN4 TARGET MATCH"; inv["hash_matches"]["run4_target"].append(p)
    elif d == RUN3: tag = " <== RUN3"; inv["hash_matches"]["run3"].append(p)
    elif d and d.startswith("761a5b14"): tag = " <== prefix match?"
    print(f"[{i+1}/{len(cands)}] {os.path.basename(p)} {d[:16] if d else 'ERR'}…{tag}")

# 4. tokenizer/model/config search Drive-wide
for pat, key in (("**/*.model", "sp_models"), ("**/*.vocab", "vocabs"),
                 ("**/*config*.json", "configs"), ("**/*.jsonl", "jsonl")):
    hits = [p for p in glob.glob("/content/drive/MyDrive/" + pat, recursive=True)
            if "node_modules" not in p]
    inv[key] = hits[:200]
    print(f"{key}: {len(hits)} hits")

out = os.path.join(OUT, f"DRIVE_RECOVERY_{int(time.time())}.json")
json.dump(inv, open(out, "w"), indent=1)
print("\nWROTE:", out)
print("RUN4 TARGET MATCHES:", inv["hash_matches"]["run4_target"])
print("RUN3 MATCHES:", inv["hash_matches"]["run3"])
print("total files in NEXUSAI_RUN4:", len(inv["files"]))
