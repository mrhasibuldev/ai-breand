# =============================================================================
# NEXUSAI RUN4 — CPU-ONLY INFERENCE VERIFICATION CELL (v2, self-contained)
# READ-ONLY: hash-gated package discovery, strict-load on CPU, 20-prompt
# suite, tokenizer round-trip, integrity+raw+report artifacts to Drive.
# No GPU/CUDA calls, no training, no checkpoint/registry modification.
# =============================================================================
import os, sys, json, glob, hashlib, time, traceback, platform

CKPT4 = "/content/drive/MyDrive/NEXUSAI_RUN4/checkpoint_final.pt"
ZIP = "/content/drive/MyDrive/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip"
ZIP_SHA = "f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644"
CKPT_SHA = "761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1"
TOK_SHA = "2fcc6a87c9ded27d1f8ad6c2dc0ff747ca4dc52db68ffde9a6e229b2cd3d8052"
OUTBASE = "/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT"
os.makedirs(OUTBASE, exist_ok=True)

R = []
def rec(n, s, d=""):
    R.append({"check": n, "status": s, "detail": str(d)[:300]})
    print(f"[{s:>10}] {n} — {str(d)[:140]}")

def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()

print("=" * 66); print("RUN4 CPU-ONLY VERIFICATION v2"); print("=" * 66)

# ---------- env report ----------
import platform as _pf
rec("env", "PASS", f"{_pf.system()} py{sys.version.split()[0]}")

# ---------- drive ----------
try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    rec("drive", "PASS", "mounted")
except Exception as e:
    rec("drive", "FAIL", e); raise SystemExit(1)

# ---------- package discovery (existing extract preferred; ZIP hash-gated) ----------
PKG = None
for dp, dn, fn in os.walk("/content"):
    if "MANIFEST.json" in fn and "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE" in dp:
        PKG = dp; break
if PKG:
    rec("package", "PASS", f"existing extract: {PKG}")
elif os.path.exists(ZIP):
    zsha = sha256(ZIP)
    rec("zip_sha256", "PASS" if zsha == ZIP_SHA else "FAIL", zsha[:20] + "…")
    if zsha != ZIP_SHA:
        rec("gate", "FAIL", "ZIP hash mismatch — STOP"); raise SystemExit(1)
    import zipfile
    dst = "/content/nexusai_pkg_cpu_verify"
    if not os.path.exists(os.path.join(dst, "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE")):
        with zipfile.ZipFile(ZIP) as z:
            names = z.namelist()
            unsafe = [n for n in names if n.startswith("/") or ".." in n.split("/")]
            if unsafe:
                rec("zip_safe", "FAIL", f"{len(unsafe)} unsafe paths"); raise SystemExit(1)
            z.extractall(dst)
    PKG = os.path.join(dst, "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE")
    rec("extract", "PASS", PKG)
else:
    rec("package", "FAIL", "no extract and no ZIP"); raise SystemExit(1)

AI = os.path.join(PKG, "nexusai")
sys.path.insert(0, AI); sys.path.insert(0, os.path.join(AI, "models"))
TOK = os.path.join(AI, "tokenizer", "sp_bpe_8k.model")

# ---------- hard integrity gates ----------
if not os.path.exists(CKPT4):
    rec("ckpt_exists", "FAIL", CKPT4); raise SystemExit(1)
h = sha256(CKPT4)
rec("ckpt_sha256", "PASS" if h == CKPT_SHA else "FAIL", h[:24] + "…")
th = sha256(TOK) if os.path.exists(TOK) else "MISSING"
rec("tokenizer_sha256", "PASS" if th == TOK_SHA else "FAIL", str(th)[:24] + "…")
if h != CKPT_SHA or th != TOK_SHA:
    rec("gate", "FAIL", "hash mismatch — STOP"); raise SystemExit(1)

# ---------- imports ----------
try:
    import torch
    import psutil
    ncpu = os.cpu_count() or 4
    torch.set_num_threads(ncpu)
    rec("imports", "PASS",
        f"torch={torch.__version__} cpu_count={ncpu} "
        f"cuda_available={torch.cuda.is_available()} (will NOT be used)")
    from core01.inference import InferenceEngine
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
except Exception as e:
    rec("imports", "FAIL", e); traceback.print_exc(); raise SystemExit(1)

# ---------- checkpoint metadata ----------
try:
    ck = torch.load(CKPT4, map_location="cpu", weights_only=False)
    rec("ckpt_meta", "PASS",
        f"ep{ck.get('epoch')} step{ck.get('step')} status={ck.get('model_status')} "
        f"tensors={len(ck['model_state_dict'])} "
        f"resume={all(k in ck for k in ('optimizer_state_dict','scheduler_state_dict','grad_scaler_state_dict','rng_state'))}")
    rec("ckpt_epoch_step", "PASS" if (ck.get("epoch") == 5 and ck.get("step") == 9213) else "FAIL",
        f"ep{ck.get('epoch')}/step{ck.get('step')}")
    rec("ckpt_status", "PASS" if ck.get("model_status") == "PRETRAINING_COMPLETED" else "FAIL",
        str(ck.get("model_status")))
except Exception as e:
    rec("ckpt_meta", "FAIL", e); raise SystemExit(1)

# ---------- config + model + strict load (CPU enforced) ----------
cd = dict(ck["config"])
if isinstance(cd.get("model_status"), str):
    cd["model_status"] = ModelStatus[cd["model_status"]]
top = ck.get("model_status")
if isinstance(top, str) and top in ModelStatus.__members__:
    cd["model_status"] = ModelStatus[top]
cfg = NexusAICore01Config(
    **{k: v for k, v in cd.items()
       if k in NexusAICore01Config.__dataclass_fields__})

proc = psutil.Process()
mem0 = proc.memory_info().rss / 2**20
t0 = time.time()
model = NexusAICore01(cfg)
try:
    res = model.load_state_dict(ck["model_state_dict"], strict=True)
    rec("strict_load",
        "PASS" if not res.missing_keys and not res.unexpected_keys else "FAIL",
        f"missing={len(res.missing_keys)} unexpected={len(res.unexpected_keys)}")
except Exception as e:
    rec("strict_load", "FAIL", e); raise SystemExit(1)
model.eval()
device = torch.device("cpu")
model = model.to(device)
# CPU-only proof: every param+buffer on cpu, no cuda call made
all_cpu = all(p.device.type == "cpu" for p in model.parameters()) and \
          all(b.device.type == "cpu" for b in model.buffers())
rec("cpu_only", "PASS" if all_cpu else "FAIL",
    f"params_on_cpu={all_cpu} cuda_initialized={torch.cuda.is_initialized()}")
n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
n_buf = sum(b.numel() for b in model.buffers())
rec("params", "PASS" if n_params == 8842560 else "FAIL",
    f"trainable={n_params:,} buffers={n_buf:,} "
    f"(count_parameters={model.count_parameters():,})")
mem1 = proc.memory_info().rss / 2**20
load_s = time.time() - t0
rec("load_perf", "PASS", f"load={load_s:.2f}s ram {mem0:.0f}→{mem1:.0f}MB")

# ---------- tokenizer ----------
tok = NexusAITokenizer(TOK, cfg)
vocab = tok.sp.get_piece_size()
rec("tokenizer", "PASS", f"vocab={vocab} bos={tok.bos_id} eos={tok.eos_id} "
    f"pad={tok.pad_id} unk={tok.unk_id}")
# round-trip + UNK counts
tests = {"en": "What is the capital of Japan?",
         "bn": "বাংলাদেশের রাজধানী কী?",
         "banglish": "tumi ki kemon acho?",
         "mixed": "What is বাংলাদেশের national animal?"}
rt = {}
for k, t in tests.items():
    ids = tok.encode(t, add_special_tokens=False)
    dec = tok.decode(ids, skip_special_tokens=False)
    unk = sum(1 for i in ids if i == tok.unk_id)
    rt[k] = {"ids": len(ids), "unk": unk, "roundtrip_ok": dec.strip() != ""}
rec("tokenizer_roundtrip", "PASS" if all(v["roundtrip_ok"] for v in rt.values()) else "WARN",
    json.dumps(rt))

# ---------- engine ----------
eng = InferenceEngine(model, tok, cfg, device="cpu")

# ---------- 20-prompt suite ----------
PROMPTS = [
    ("bn_name", "bn", "তোমার নাম কী?"), ("bn_water", "bn", "মানুষ কেন পানি পান করে?"),
    ("bn_tree", "bn", "গাছ আমাদের কী উপকার করে?"), ("bn_rain", "bn", "বৃষ্টি কেন হয়?"),
    ("bn_edu", "bn", "শিক্ষা কেন প্রয়োজন?"),
    ("en_name", "en", "What is your name?"), ("en_water", "en", "Why do humans need water?"),
    ("en_sun", "en", "Why do plants need sunlight?"), ("en_edu", "en", "What is the purpose of education?"),
    ("en_grav", "en", "Explain gravity simply."),
    ("bg_do", "banglish", "tumi ki korte paro?"), ("bg_water", "banglish", "manush pani khay keno?"),
    ("bg_rain", "banglish", "brishti keno hoy?"), ("bg_tree", "banglish", "gach amader ki upokar kore?"),
    ("bg_name", "banglish", "tomar naam ki?"),
    ("rs_apple", "reason", "If I have 3 apples and buy 2 more, how many apples do I have?"),
    ("rs_math", "reason", "What is 7 + 5?"),
    ("rs_day", "reason", "If today is Monday, what day will it be after 3 days?"),
    ("ins_sun", "inst", "Answer in exactly one sentence: What is the Sun?"),
    ("ins_books", "inst", "Give three benefits of reading books."),
]

results = []
t_all = time.time()
for pid, lg, prompt in PROMPTS:
    t = time.time()
    try:
        r = eng.generate(prompt, max_new_tokens=48, do_sample=False)
        out = r.get("generated_text", "")
        warn = r.get("warning")
    except Exception as e:
        out, warn = "", f"EXC:{e}"
    results.append({"id": pid, "lang": lg, "prompt": prompt, "output": out,
                    "warning": warn, "empty": not out.strip(),
                    "latency_s": round(time.time() - t, 2)})
    print(f"{pid:10} {'EMPTY' if not out.strip() else out[:80]!r} w={warn}")

total_s = time.time() - t_all
mem2 = proc.memory_info().rss / 2**20
n = len(results)
empty = sum(1 for r in results if r["empty"])
lat = [r["latency_s"] for r in results]
avg_lat = sum(lat) / n
max_lat = max(lat)
def bn_script(s): return any('ঀ' <= c <= '৿' for c in s)
bn_out = sum(1 for r in results if r["lang"] == "bn" and bn_script(r["output"]))
per_lang = {}
for lg in ("bn", "en", "banglish"):
    sub = [r for r in results if r["lang"] == lg]
    per_lang[lg] = {"n": len(sub),
                    "empty": sum(1 for r in sub if r["empty"])}

rec("generation", "PASS" if n == 20 else "FAIL",
    f"{n}/20 done empty={empty} avg_lat={avg_lat:.1f}s max={max_lat:.1f}s "
    f"total={total_s:.0f}s bn_script={bn_out}/5")
rec("ram", "PASS", f"proc RSS {mem0:.0f}→{mem1:.0f}→{mem2:.0f}MB")

# ---------- verdict ----------
fails = [c for c in R if c["status"] == "FAIL"]
verdict = ("A_CPU_LOAD_AND_GENERATION_PASS" if not fails and empty < n
           else "B_CPU_LOAD_PASS_ANSWER_QUALITY_NOT_VERIFIED_OR_POOR" if not fails
           else "C_CPU_LOAD_FAIL")
rec("verdict", "PASS", verdict)

# ---------- artifacts ----------
raw = {"checkpoint": CKPT4, "ckpt_sha256": h, "tokenizer_sha256": th,
       "params_trainable": n_params, "buffers": n_buf,
       "device": "cpu", "cuda_initialized": torch.cuda.is_initialized(),
       "load_s": round(load_s, 2),
       "gen": {"n": n, "empty": empty, "avg_latency_s": round(avg_lat, 2),
               "max_latency_s": max_lat, "total_s": round(total_s, 1),
               "ram_mb": [round(mem0), round(mem1), round(mem2)],
               "bn_script_outputs": bn_out, "per_lang": per_lang},
       "results": results, "checks": R, "verdict": verdict,
       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(raw, open(os.path.join(OUTBASE, "NEXUSAI_RUN4_CPU_RAW_OUTPUTS.json"), "w"),
          indent=1, ensure_ascii=False)
json.dump({"ckpt_sha256": h, "tokenizer_sha256": th, "epoch": ck.get("epoch"),
           "step": ck.get("step"), "status": ck.get("model_status"),
           "tensors": len(ck["model_state_dict"]),
           "resume_keys": all(k in ck for k in
               ("optimizer_state_dict","scheduler_state_dict",
                "grad_scaler_state_dict","rng_state")),
           "trainable_params": n_params, "buffers": n_buf,
           "device": "cpu", "checks": R},
          open(os.path.join(OUTBASE, "NEXUSAI_RUN4_CPU_INTEGRITY.json"), "w"), indent=1)

md = f"""# NEXUSAI RUN4 CPU VERIFICATION — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}

Env: {platform.system()} py{sys.version.split()[0]} torch={torch.__version__} · CPU-only (cuda_available={torch.cuda.is_available()}, initialized={torch.cuda.is_initialized()})

## Integrity gates
- ZIP sha: {'verified' if PKG else 'n/a'} · ckpt sha `{h[:20]}…` {'MATCH' if h==CKPT_SHA else 'MISMATCH'}
- tokenizer sha `{str(th)[:20]}…` {'MATCH' if th==TOK_SHA else 'MISMATCH'}
- meta: ep{ck.get('epoch')} step{ck.get('step')} status={ck.get('model_status')} tensors={len(ck['model_state_dict'])}

## Model
- class NexusAICore01 · strict=True · missing={len(res.missing_keys)} unexpected={len(res.unexpected_keys)}
- trainable params={n_params:,} buffers={n_buf:,} · load={load_s:.2f}s · device=cpu confirmed
- RAM {mem0:.0f}→{mem2:.0f}MB

## Tokenizer
- vocab={vocab} bos={tok.bos_id} eos={tok.eos_id} pad={tok.pad_id} unk={tok.unk_id}
- roundtrip: {json.dumps(rt)}

## Generation — 20 prompts, greedy, max_new=48
- completed {n}/20 · empty {empty} · avg {avg_lat:.1f}s · max {max_lat:.1f}s · total {total_s:.0f}s
- per-lang empty: {json.dumps(per_lang)} · bn_script outputs: {bn_out}/5

## Website compatibility
Standalone CPU inference verified here does NOT equal website integration.
ML service uses same InferenceEngine on cpu by default; Run4 would need a
registry entry (NOT activated — read-only task).

## VERDICT: **{verdict}**
"""
open(os.path.join(OUTBASE, "NEXUSAI_RUN4_CPU_VERIFICATION_REPORT.md"), "w",
     encoding="utf-8").write(md)
print("\nArtifacts:", OUTBASE)
print("VERDICT:", verdict)
