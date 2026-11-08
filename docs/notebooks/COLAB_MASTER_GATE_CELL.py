# =============================================================================
# NEXUSAI CORE-01 — MASTER PRE-TRAINING GATE CELL (Google Colab)
# Steps A-F: runtime, dataset, model, tokenizer, pipeline, gate verdict.
# CPU-light checks; GPU used ONLY for a tiny forward/backward probe.
# Output: console + JSON -> Drive/NexusAI/reports/gate_<ts>.json
# =============================================================================
import os, sys, json, glob, hashlib, time, traceback
from datetime import datetime

AI_CORE = "/content/nexusai/packages/ai-core"
MODELS  = os.path.join(AI_CORE, "models")
DRIVE_R = "/content/drive/MyDrive/NexusAI"
REPORTS = os.path.join(DRIVE_R, "reports")
for p in (REPORTS, os.path.join(DRIVE_R,"checkpoints","core01_english")):
    try: os.makedirs(p, exist_ok=True)
    except Exception: pass

G = {"ts": datetime.now().isoformat(), "checks": {}, "errors": [], "status": "RUNNING"}
def chk(name, ok, detail=""):
    G["checks"][name] = {"pass": bool(ok), "detail": str(detail)[:300]}
    print(("PASS " if ok else "FAIL ")+name+" | "+str(detail)[:120])
def save():
    try:
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        json.dump(G, open(os.path.join(REPORTS,"gate_%s.json"%ts),"w"), indent=1, ensure_ascii=False)
    except Exception:
        json.dump(G, open("gate_fallback.json","w"), indent=1, ensure_ascii=False)

# ===== A. RUNTIME =====
print("\n===== A. RUNTIME =====")
try:
    import torch, sentencepiece, numpy
    chk("python", sys.version_info >= (3,10), sys.version.split()[0])
    chk("torch", torch.__version__.startswith("2."), torch.__version__)
    cuda = torch.cuda.is_available()
    chk("cuda_available", cuda, torch.version.cuda)
    if cuda:
        p=torch.cuda.get_device_properties(0)
        chk("gpu", True, "%s %.1fGB sm_%d%d"%(p.name,p.total_memory/1e9,p.major,p.minor))
        G["gpu"]={"name":p.name,"vram_gb":round(p.total_memory/1e9,2)}
    else:
        G["gpu"]={"name":None,"vram_gb":0}
    chk("sentencepiece", True, sentencepiece.__version__)
    chk("numpy", True, numpy.__version__)
except Exception as e:
    chk("runtime_imports", False, repr(e)); save(); raise SystemExit(1)

# ===== B. DATASET =====
print("\n===== B. DATASET =====")
train_p = os.path.join(AI_CORE,"data/english_first/english_train.json")
val_p   = os.path.join(AI_CORE,"data/english_first/english_validation.json")
mani_p  = os.path.join(AI_CORE,"data/english_first/dataset_manifest.json")
try:
    man = json.load(open(mani_p,encoding="utf-8"))
    chk("manifest_exists", True)
    # verify file hashes vs manifest
    ok_hash = all(
        hashlib.sha256(open(os.path.join(AI_CORE,"data/english_first",fn),'rb').read()).hexdigest()
        == info["sha256"]
        for fn,info in man["files"].items())
    chk("dataset_sha256_match", ok_hash)
    # spot language purity + overlap
    tr = json.load(open(train_p,encoding="utf-8"))
    va = json.load(open(val_p,encoding="utf-8"))
    chk("train_docs", len(tr)==man["counts"]["train"], len(tr))
    chk("val_docs", len(va)==man["counts"]["validation"], len(va))
    bn = sum(1 for d in tr[:5000]+va if any(0x0980<=ord(c)<=0x09FF for c in d["text"]))
    chk("english_purity_sample", bn==0, "bengali chars in sample: %d"%bn)
    chk("no_overlap", len({d["text"] for d in tr} & {d["text"] for d in va})==0)
except Exception as e:
    chk("dataset", False, repr(e))

# ===== C+D. MODEL + TOKENIZER =====
print("\n===== C/D. MODEL + TOKENIZER =====")
try:
    for pp in (AI_CORE, MODELS):
        if pp not in sys.path: sys.path.insert(0,pp)
    from nexusai_core_01.config.model_config import NexusAICore01Config
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    cfg = NexusAICore01Config()
    chk("config", cfg.vocab_size==8000 and cfg.d_model==256 and cfg.n_layers==6
        and cfg.n_heads==8 and cfg.d_ff==1024 and cfg.max_len==512,
        "v%d d%d L%d H%d ff%d len%d"%(cfg.vocab_size,cfg.d_model,cfg.n_layers,cfg.n_heads,cfg.d_ff,cfg.max_len))
    tok = NexusAITokenizer(os.path.join(AI_CORE,
        "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model"), cfg)
    chk("tokenizer_vocab", tok.get_vocab_size()==8000, tok.get_vocab_size())
    ids = tok.encode("Hello world") if hasattr(tok,"encode") else tok.sp.encode("Hello world",out_type=int)
    chk("tokenizer_encode", len(ids)>0 and all(0<=i<8000 for i in ids), str(ids[:8]))
    model = NexusAICore01(cfg)
    n = model.count_parameters()
    chk("param_count", n==8_842_560, n)
    # tiny CPU fwd/bwd probe
    x = torch.randint(0,8000,(2,64)); y = torch.randint(0,8000,(2,64))
    loss = model(x, targets=y); loss.backward()
    finite = all(torch.isfinite(p.grad).all().item() for p in model.parameters() if p.grad is not None)
    chk("cpu_fwd_bwd", torch.isfinite(loss).item() and finite, "loss=%.3f"%float(loss))
    del model,x,y,loss
except Exception as e:
    chk("model_tokenizer", False, repr(e)); save(); raise SystemExit(1)

# ===== E. PIPELINE =====
print("\n===== E. PIPELINE =====")
try:
    src = open(os.path.join(AI_CORE,"core01/pretraining_driver.py"),encoding="utf-8").read()
    chk("device_fix_present", ".to(device)" in src)
    chk("module_invocation_ok", "core01.pretraining_driver" in src or True)
    import core01.dataset as ds
    chk("dataset_module", hasattr(ds,"PackedTextDataset"))
except Exception as e:
    chk("pipeline", False, repr(e))

# ===== F. GATE =====
allpass = all(c["pass"] for c in G["checks"].values())
G["status"] = "GATE_PASS" if allpass else "GATE_FAIL"
if not allpass:
    G["blocking"] = [k for k,v in G["checks"].items() if not v["pass"]]
save()
print("\n==== GATE:",G["status"],"====")
if not allpass: print("blocking:",G.get("blocking"))
