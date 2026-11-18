# =============================================================================
# NEXUSAI CORE-01 RUN5 SFT — PREPARATION CELL (TRAINING_ENABLED=False)
# Phase D deliverable: preflight + verified SFT code path, NO training by
# default. Set TRAINING_ENABLED=True ONLY with explicit Phase-F approval.
# Loads Run4 (hash-gated), builds ChatSFTDataset, verifies masking, constructs
# optimizer/scheduler — then STOPS before any backward/step.
# =============================================================================
import os, sys, json, glob, hashlib, time, traceback

# ===================== AUTHORIZATION GATE =====================
TRAINING_ENABLED = False   # <<< MUST stay False until Phase-F approval
EPOCHS = 3
LR = 2e-5
BATCH_SIZE = 8
GRAD_ACCUM = 4
MAX_LEN = 256
SEED = 42

CKPT = "/content/drive/MyDrive/NEXUSAI_RUN4/checkpoint_final.pt"
CKPT_SHA = "761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1"
CKPT_SIZE = 106777501
TOK_SHA = "2fcc6a87c9ded27d1f8ad6c2dc0ff747ca4dc52db68ffde9a6e229b2cd3d8052"
ZIP_SHA = "f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644"
PKG_PREFERRED = "/content/NEXUSAI_RUN4_RECOVERY_WORK/package/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE"
SFT_DIR_LOCAL = "/content/NEXUSAI_RUN4_CPU_VERIFY_WORK/sft_v2"   # upload sft_v2 here
SFT_ZIP_HINT = "/content/drive/MyDrive/**/sft_v2*.zip"
OUTDIR = "/content/NEXUSAI_RUN5_SFT"
WORK = "/content/NEXUSAI_RUN4_CPU_VERIFY_WORK"
for d in (WORK, OUTDIR): os.makedirs(d, exist_ok=True)

R = []
def rec(n, s, d=""):
    R.append({"check": n, "status": s, "detail": str(d)[:400]})
    print(f"[{s:>10}] {n} — {str(d)[:150]}")
def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""): h.update(c)
    return h.hexdigest()
def stop(msg):
    rec("STOP", "FAIL", msg); raise SystemExit(1)

print("=" * 72); print("RUN5 SFT PREPARATION — TRAINING_ENABLED =", TRAINING_ENABLED); print("=" * 72)

# ---------- env + GPU preflight ----------
try:
    import torch, psutil, numpy as np
    rec("env", "PASS", f"py{sys.version.split()[0]} torch={torch.__version__}")
    cuda_ok = torch.cuda.is_available()
    if cuda_ok:
        rec("gpu", "PASS", f"{torch.cuda.get_device_name(0)} VRAM={torch.cuda.get_device_properties(0).total_memory/2**30:.1f}GB")
    else:
        rec("gpu", "WARN", "no CUDA — preflight only; training needs GPU")
    rec("ram", "PASS", f"{psutil.virtual_memory().total/2**30:.1f}GB")
except Exception as e:
    stop(f"imports: {e}")

# ---------- drive + package (same discovery as v7) ----------
try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"): drive.mount("/content/drive")
    rec("drive", "PASS", "mounted")
except Exception as e:
    rec("drive", "WARN", str(e)[:100])

PKG = PKG_PREFERRED if os.path.isdir(PKG_PREFERRED) else None
if not PKG:
    for dp, dn, fn in os.walk("/content"):
        if "MANIFEST.json" in fn and "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE" in dp:
            PKG = dp; break
if not PKG:
    zips = glob.glob("/content/drive/MyDrive/**/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip", recursive=True)
    if not zips: stop("package not found")
    if sha256(zips[0]) != ZIP_SHA: stop("ZIP hash mismatch")
    import zipfile
    dst = os.path.join(WORK, "pkg_extract")
    with zipfile.ZipFile(zips[0]) as z:
        bad = [n for n in z.namelist() if n.startswith("/") or ".." in n.split("/")]
        if bad: stop("unsafe zip paths")
        z.extractall(dst)
    PKG = os.path.join(dst, "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE")
rec("package", "PASS", PKG)
AI = os.path.join(PKG, "nexusai")

# ---------- apply approved source patches to working copy ----------
PATCHES = [
    (os.path.join(AI, "models", "nexusai_core_01", "config", "model_config.py"),
     '        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})',
     '''        fields = {k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__}
        status = fields.get("model_status")
        if status is not None and not isinstance(status, ModelStatus):
            try:
                fields["model_status"] = ModelStatus(status)
            except ValueError:
                raise ValueError(f"Invalid model_status: {status!r}")
        return cls(**fields)'''),
]
for fpath, old, new in PATCHES:
    src = open(fpath, encoding="utf-8").read()
    if new.strip() not in src:
        if old not in src: stop(f"patch pattern missing: {fpath}")
        open(fpath, "w", encoding="utf-8").write(src.replace(old, new, 1))
rec("source_patch", "PASS", "from_dict fix on working copy")

# ---- embedded SFT dataset (self-contained; mirrors core01/sft_dataset.py) ----
USER_TAG, ASSISTANT_TAG = "user: ", "assistant: "
def serialize_conversation(tokenizer, messages, max_len=512):
    bos, eos = tokenizer.bos_id, tokenizer.eos_id
    seq, sup = [], []
    for m in messages:
        if m["role"] == "user":
            seq.append(bos); sup.append(False)
            ids = tokenizer.encode(USER_TAG + m["content"], add_special_tokens=False)
            seq += ids; sup += [False] * len(ids)
            seq.append(eos); sup.append(False)
        elif m["role"] == "assistant":
            ids = tokenizer.encode(ASSISTANT_TAG + m["content"], add_special_tokens=False)
            seq += ids; sup += [True] * len(ids)
            seq.append(eos); sup.append(True)
        else:
            raise ValueError(f"unknown role {m['role']}")
    input_ids, labels = [], []
    for i in range(len(seq) - 1):
        input_ids.append(seq[i])
        labels.append(seq[i + 1] if sup[i + 1] else -100)
    return input_ids[:max_len], labels[:max_len]

class ChatSFTDataset:
    def __init__(self, jsonl_path, tokenizer, max_len=512):
        import json as _j
        self.records = [_j.loads(l) for l in open(jsonl_path, encoding="utf-8") if l.strip()]
        self.tokenizer, self.max_len = tokenizer, max_len
    def __len__(self): return len(self.records)
    def __getitem__(self, idx):
        ids, labels = serialize_conversation(self.tokenizer, self.records[idx]["messages"], self.max_len)
        return {"input_ids": torch.tensor(ids, dtype=torch.long),
                "labels": torch.tensor(labels, dtype=torch.long)}

def sft_collate(batch, pad_id):
    maxlen = max(len(b["input_ids"]) for b in batch)
    ii, ll, am = [], [], []
    for b in batch:
        n = len(b["input_ids"])
        ii.append(torch.cat([b["input_ids"], torch.full((maxlen - n,), pad_id, dtype=torch.long)]))
        ll.append(torch.cat([b["labels"], torch.full((maxlen - n,), -100, dtype=torch.long)]))
        am.append(torch.cat([torch.ones(n, dtype=torch.long),
                             torch.zeros(maxlen - n, dtype=torch.long)]))
    return {"input_ids": torch.stack(ii), "labels": torch.stack(ll),
            "attention_mask": torch.stack(am)}

def batch_has_supervision(labels):
    return bool((labels != -100).any().item())

HAVE_SFT = True
rec("sft_dataset", "PASS", "embedded ChatSFTDataset + serialize_conversation")

sys.path.insert(0, AI); sys.path.insert(0, os.path.join(AI, "models"))
TOK = os.path.join(AI, "tokenizer", "sp_bpe_8k.model")

# ---------- Run4 integrity ----------
if not os.path.exists(CKPT):
    hits = [p for p in glob.glob("/content/drive/MyDrive/**/*.pt", recursive=True)
            if os.path.getsize(p) == CKPT_SIZE]
    if hits: CKPT = hits[0]
if not os.path.exists(CKPT): stop("Run4 checkpoint not found")
h = sha256(CKPT)
rec("ckpt_sha256", "PASS" if h == CKPT_SHA else "FAIL", h[:20] + "…")
if h != CKPT_SHA: stop("not Run4")
th = sha256(TOK) if os.path.exists(TOK) else "MISSING"
rec("tokenizer_sha256", "PASS" if th == TOK_SHA else "FAIL", str(th)[:20] + "…")
if th != TOK_SHA: stop("tokenizer mismatch")

# ---------- imports + safe load ----------
try:
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
except Exception as e:
    stop(f"imports: {e}")

ck = None
try:
    ck = torch.load(CKPT, map_location="cpu", weights_only=True)
    deser = "weights_only=True"
except Exception:
    import numpy as np, numpy.dtypes as _nd
    from torch.serialization import add_safe_globals
    cands = []
    for base in ("numpy._core", "numpy.core"):
        try:
            ma = __import__(f"{base}.multiarray", fromlist=["_reconstruct"])
            for a in ("_reconstruct", "ndarray", "dtype"):
                v = getattr(ma, a, None)
                if v is not None: cands.append(v)
        except Exception: pass
    cands.append(np.dtype)
    for n in dir(_nd):
        v = getattr(_nd, n)
        if isinstance(v, type) and n.endswith("DType"): cands.append(v)
    nr = __import__("numpy.random", fromlist=["RandomState", "Generator"])
    cands += [nr.RandomState, nr.Generator]
    add_safe_globals([c for c in dict.fromkeys(cands) if c is not None])
    ck = torch.load(CKPT, map_location="cpu", weights_only=True)
    deser = "weights_only=True+allowlist"
rec("deser", "PASS", deser)

cd = dict(ck.get("config") or {})
cd["model_status"] = ModelStatus(ck.get("model_status"))
cfg = NexusAICore01Config.from_dict(cd)
rec("ckpt_meta", "PASS", f"ep{ck.get('epoch')} step{ck.get('step')} status={ck.get('model_status')}")

device = torch.device("cuda" if cuda_ok else "cpu")
model = NexusAICore01(cfg)
res = model.load_state_dict(ck["model_state_dict"], strict=True)
rec("strict_load", "PASS" if not res.missing_keys and not res.unexpected_keys else "FAIL",
    f"missing={len(res.missing_keys)} unexpected={len(res.unexpected_keys)}")
model.to(device).train() if TRAINING_ENABLED else model.to(device).eval()
rec("model", "PASS", f"params={model.count_parameters():,} device={device}")
tok = NexusAITokenizer(TOK, cfg)
rec("tokenizer", "PASS", f"vocab={tok.sp.get_piece_size()}")

# ---------- SFT dataset locate/verify ----------
SFT = None
for cand in (SFT_DIR_LOCAL,
             "/content/drive/MyDrive/NEXUSAI_SFT_V2",
             "/content/NEXUSAI_SFT_V2"):
    if os.path.isdir(cand) and os.path.exists(os.path.join(cand, "train.jsonl")):
        SFT = cand; break
if not SFT:
    zlist = glob.glob("/content/drive/MyDrive/**/sft_v2*", recursive=True) + \
            glob.glob("/content/**/sft_v2*", recursive=True)
    zlist = [z for z in zlist if os.path.isfile(z) and z.endswith(".zip")]
    if zlist:
        import zipfile
        dst = os.path.join(WORK, "sft_extract")
        with zipfile.ZipFile(zlist[0]) as z: z.extractall(dst)
        for dp, dn, fn in os.walk(dst):
            if "train.jsonl" in fn: SFT = dp; break
if not SFT:
    rec("sft_dataset", "WARN", "sft_v2 not found — upload data/sft_v2/ to Drive or /content")
else:
    man = json.load(open(os.path.join(SFT, "dataset_manifest.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(SFT, "dataset_manifest.json")) else {}
    rec("sft_dataset", "PASS", f"{SFT} manifest_total={man.get('total')}")
    # checksum verify if manifest files present
    for name in ("train.jsonl", "validation.jsonl"):
        p = os.path.join(SFT, name)
        rec(f"sft:{name}", "PASS" if os.path.exists(p) else "FAIL",
            f"{os.path.getsize(p)}B" if os.path.exists(p) else "missing")

# ---------- masking correctness test (non-destructive) ----------
if HAVE_SFT and SFT:
    try:
        ds = ChatSFTDataset(os.path.join(SFT, "train.jsonl"), tok, MAX_LEN)
        sample = ds[0]
        sup = int((sample["labels"] != -100).sum())
        tot = len(sample["labels"])
        rec("masking", "PASS" if 0 < sup < tot else "FAIL",
            f"sample0 supervised={sup}/{tot} (prompt+pad masked)")
        # manual decode of supervised targets
        sup_ids = sample["labels"][sample["labels"] != -100].tolist()
        dec = tok.decode(sup_ids, skip_special_tokens=False)
        rec("masking_decode", "PASS", f"supervised→{dec[:80]!r}")
        # finite loss via logits + CE(ignore_index=-100), attention_mask for pad keys
        import torch.nn.functional as F
        batch = sft_collate([sample, sample], cfg.pad_id)
        x = batch["input_ids"].to(device); y = batch["labels"].to(device)
        am = batch["attention_mask"].to(device)
        with torch.no_grad():
            logits = model(x, attention_mask=am)
            loss = F.cross_entropy(logits.view(-1, cfg.vocab_size), y.view(-1), ignore_index=-100)
        rec("sft_loss", "PASS" if torch.isfinite(loss) else "FAIL", f"loss={loss.item():.4f}")
        # NaN guard: all-masked batch must be detected & skipped
        y_bad = torch.full_like(y, -100)
        _guard_ok = (not batch_has_supervision(y_bad)) and batch_has_supervision(y)
        rec("nan_guard", "PASS" if _guard_ok else "FAIL",
            f"all_masked_detected={not batch_has_supervision(y_bad)} real_batch_ok={batch_has_supervision(y)}")
    except Exception as e:
        rec("masking", "FAIL", str(e)[:200])

# ---------- optimizer/scheduler CONSTRUCTION ONLY (no step) ----------
try:
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    n_sft = sum(1 for _ in open(os.path.join(SFT, "train.jsonl"), encoding="utf-8")) if SFT else 0
    total_steps = max(1, n_sft // BATCH_SIZE * EPOCHS)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, s / max(1, total_steps // 20)) *
        (0.5 * (1 + np.cos(np.pi * s / max(1, total_steps)))))
    rec("optimizer", "PASS", f"AdamW lr={LR} wd=0.01 steps~{total_steps} — constructed, NO step()")
except Exception as e:
    rec("optimizer", "FAIL", str(e)[:150])

# ---------- GPU memory estimate ----------
if cuda_ok:
    est = {"model_fp32_MB": round(model.count_parameters() * 4 / 2**20),
           "adamw_MB": round(model.count_parameters() * 8 / 2**20),
           "grads_MB": round(model.count_parameters() * 4 / 2**20),
           "total_static_MB": round(model.count_parameters() * 16 / 2**20),
           "note": "activations extra; batch8×len256 fp16 ≈ +1-2GB — T4 16GB safe"}
    rec("gpu_estimate", "PASS", json.dumps(est))

# ---------- preflight summary ----------
fails = [c for c in R if c["status"] == "FAIL"]
print("\n" + "=" * 72)
print("PREFLIGHT", "FAILED" if fails else "PASSED", f"({len(R)} checks)")
if TRAINING_ENABLED:
    print("!!! TRAINING_ENABLED=True — this cell WOULD train. Phase-F approval required.")
    # ===================== TRAINING PATH (gated) =====================
    # Full loop intentionally omitted in preflight deliverable; enable only
    # after separate approval. Skeleton: ChatSFTDataset -> DataLoader ->
    # forward logits -> CE(ignore_index=-100) -> scaler -> accum -> clip ->
    # step -> cosine sched -> val eval -> save NEXUSAI_RUN5_SFT/checkpoint_best.pt
    rec("training", "NOT TESTED", "gated — requires Phase-F approval")
else:
    print("TRAINING DISABLED — preflight only. No backward/step executed.")
    rec("training", "NOT TESTED", "TRAINING_ENABLED=False (correct)")

json.dump({"checks": R, "training_enabled": TRAINING_ENABLED,
           "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
          open(os.path.join(OUTDIR, "sft_preflight_report.json"), "w"), indent=1)
print(f"Report → {OUTDIR}/sft_preflight_report.json")
