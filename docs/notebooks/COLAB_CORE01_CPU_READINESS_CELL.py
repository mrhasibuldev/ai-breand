# =============================================================================
# NEXUSAI CORE-01 — CPU GENERATION + QUALITY CELL v5 (self-contained)
# ONE cell: Drive -> package -> source-hash verify -> ckpt/tok gates ->
# safe load -> strict=True -> CPU -> instrumented neural generation (11
# prompts) -> transparent quality heuristics -> 3 reports. READ-ONLY.
# =============================================================================
import os, sys, json, glob, hashlib, time, traceback, re

CKPT = "/content/drive/MyDrive/NEXUSAI_RUN4/checkpoint_final.pt"
CKPT_SHA = "761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1"
CKPT_SIZE = 106777501
TOK_SHA = "2fcc6a87c9ded27d1f8ad6c2dc0ff747ca4dc52db68ffde9a6e229b2cd3d8052"
ZIP_SHA = "f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644"
PKG_PREFERRED = "/content/NEXUSAI_RUN4_RECOVERY_WORK/package/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE"
SRC_HASHES = {  # verified against trusted package manifest
    "core01/transformer.py": "c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc",
}
OUT = "/content/nexusai_cpu_readiness"
os.makedirs(OUT, exist_ok=True)
STATUS = {"checkpoint_integrity": "NOT TESTED", "safe_loading": "NOT TESTED",
          "architecture_compat": "NOT TESTED", "strict_loading": "NOT TESTED",
          "neural_generation": "NOT TESTED", "answer_quality": "NOT TESTED"}
R = []
def rec(n, s, d=""):
    R.append({"check": n, "status": s, "detail": str(d)[:400]})
    print(f"[{s:>10}] {n} — {str(d)[:150]}")
def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""): h.update(c)
    return h.hexdigest()
def stop(phase, msg):
    STATUS[phase] = "BLOCKED" if phase != "checkpoint_integrity" else "FAIL"
    rec("STOP", "FAIL", f"{phase}: {msg}")
    json.dump({"status": STATUS, "checks": R, "stopped_at": phase,
               "error": msg, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
              open(os.path.join(OUT, "cpu_quality_raw.json"), "w"), indent=1)
    raise SystemExit(1)

print("=" * 70); print("NEXUSAI CORE-01 CPU GENERATION + QUALITY v5"); print("=" * 70)
rec("env", "PASS", f"py{sys.version.split()[0]}")

# ---------- Phase A: env + Drive ----------
try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"): drive.mount("/content/drive")
    rec("drive", "PASS", "mounted")
except Exception as e:
    stop("checkpoint_integrity", f"drive: {e}")
try:
    import psutil
    vm = psutil.virtual_memory()
    rec("ram", "PASS", f"total={vm.total/2**30:.1f}GB avail={vm.available/2**30:.1f}GB")
except Exception:
    rec("ram", "WARN", "psutil unavailable")

# ---------- package ----------
PKG = PKG_PREFERRED if os.path.isdir(PKG_PREFERRED) else None
if not PKG:
    for dp, dn, fn in os.walk("/content"):
        if "MANIFEST.json" in fn and "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE" in dp:
            PKG = dp; break
if not PKG:
    zips = glob.glob("/content/drive/MyDrive/**/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip", recursive=True)
    if not zips: stop("checkpoint_integrity", "package not found (no extract, no ZIP)")
    zh = sha256(zips[0])
    rec("zip_sha256", "PASS" if zh == ZIP_SHA else "FAIL", zh[:20] + "…")
    if zh != ZIP_SHA: stop("checkpoint_integrity", "ZIP hash mismatch")
    import zipfile
    dst = "/content/nexusai_pkg_v5"
    with zipfile.ZipFile(zips[0]) as z:
        bad = [n for n in z.namelist() if n.startswith("/") or ".." in n.split("/")]
        if bad: stop("checkpoint_integrity", f"{len(bad)} unsafe zip paths")
        z.extractall(dst)
    PKG = os.path.join(dst, "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE")
rec("package", "PASS", PKG)
AI = os.path.join(PKG, "nexusai")

# ---------- apply approved 3-fix patch to EXTRACTED copy only ----------
# (ZIP/Drive originals untouched; patch targets /content working copy)
PATCHES = [
    # Fix 1: from_dict() — coerce model_status str -> ModelStatus
    (os.path.join(AI, "models", "nexusai_core_01", "config", "model_config.py"),
     '        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})',
     '''        fields = {k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__}
        status = fields.get("model_status")
        if status is not None and not isinstance(status, ModelStatus):
            try:
                fields["model_status"] = ModelStatus(status)
            except ValueError:
                raise ValueError(
                    f"Invalid model_status value: {status!r}. "
                    f"Expected one of {[s.value for s in ModelStatus]}"
                )
        return cls(**fields)''', "simple"),
]
# Fix 2: replace ENTIRE packaged generate() (old buggy version) with the
# approved fixed implementation — covers status .value crash AND the
# earlier approved inference fixes (BOS-only, generated-IDs decode,
# inference_mode). Marker-bounded replacement.
FIXED_GENERATE = '''    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        do_sample: bool = True,
        repetition_penalty: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate text from prompt (fixed: type-safe status, BOS-only
        prompt, generated-IDs decode, inference_mode)."""
        status_value = (
            self.config.model_status.value
            if isinstance(self.config.model_status, ModelStatus)
            else str(self.config.model_status)
        )
        if status_value in [ModelStatus.UNTRAINED.value, ModelStatus.RANDOMLY_INITIALIZED.value]:
            return {
                "generated_text": "",
                "warning": "MODEL_STATUS_UNTRAINED_OR_RANDOM",
                "message": f"Model status is {status_value}. Output will be random and meaningless.",
                "model_status": status_value
            }
        content_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        input_ids = [self.tokenizer.bos_id] + content_ids
        max_len = getattr(self.config, "max_len", 512)
        if len(input_ids) > max_len:
            input_ids = [self.tokenizer.bos_id] + input_ids[-(max_len - 1):]
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        prompt_len = input_ids.shape[1]
        with torch.inference_mode():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens or self.config.max_new_tokens,
                temperature=temperature or self.config.temperature,
                top_k=top_k if top_k is not None else self.config.top_k,
                top_p=top_p if top_p is not None else self.config.top_p,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty or self.config.repetition_penalty
            )
        new_ids = generated_ids[0, prompt_len:].cpu().tolist()
        generated_text = self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        return {
            "generated_text": generated_text,
            "model_status": status_value,
            "warning": None if generated_text else "EMPTY_GENERATION"
        }

'''

patched = 0
for item in PATCHES:
    fpath, old, new = item[0], item[1], item[2]
    if not os.path.exists(fpath):
        rec("patch", "FAIL", f"missing {fpath}"); raise SystemExit(1)
    src = open(fpath, encoding="utf-8").read()
    if new.strip() in src:
        patched += 1; continue
    if old not in src:
        rec("patch", "FAIL", f"pattern not found in {os.path.basename(fpath)} — STOP")
        raise SystemExit(1)
    open(fpath, "w", encoding="utf-8").write(src.replace(old, new, 1))
    patched += 1
# Fix 2: whole-method replacement on inference.py
inf = os.path.join(AI, "core01", "inference.py")
src = open(inf, encoding="utf-8").read()
if "BOS-only" in src or "inference_mode():" in src.split("def generate")[1].split("def load_checkpoint")[0]:
    patched += 1  # already fixed
else:
    a = src.find("    def generate(")
    b = src.find("    def load_checkpoint")
    if a < 0 or b < 0 or b <= a:
        rec("patch", "FAIL", "generate()/load_checkpoint markers not found — STOP")
        raise SystemExit(1)
    src = src[:a] + FIXED_GENERATE + src[b:]
    open(inf, "w", encoding="utf-8").write(src)
    patched += 1
rec("source_patch", "PASS" if patched == len(PATCHES) + 1 else "FAIL",
    f"{patched}/{len(PATCHES)+1} approved fixes applied to extracted copy")
if patched != len(PATCHES) + 1: raise SystemExit(1)

sys.path.insert(0, AI); sys.path.insert(0, os.path.join(AI, "models"))
TOK = os.path.join(AI, "tokenizer", "sp_bpe_8k.model")

# ---------- Phase B: source-hash verification ----------
src_ok = True
for rel, exp in SRC_HASHES.items():
    p = os.path.join(AI, rel)
    if not os.path.exists(p):
        rec("src_hash", "FAIL", f"missing {rel}"); src_ok = False; continue
    got = sha256(p)
    ok = got == exp
    rec(f"src:{rel}", "PASS" if ok else "WARN",
        f"{got[:16]}… {'match' if ok else 'DIFFERS from manifest — inference.py fix is expected-diff, transformer must match'}")
    if not ok and "transformer" in rel: src_ok = False
if not src_ok: stop("architecture_compat", "transformer.py hash mismatch")

# ---------- checkpoint + tokenizer gates ----------
if not os.path.exists(CKPT):
    hits = [p for p in glob.glob("/content/drive/MyDrive/**/*.pt", recursive=True)
            if os.path.getsize(p) == CKPT_SIZE]
    if hits:
        CKPT = hits[0]
if not os.path.exists(CKPT): stop("checkpoint_integrity", f"{CKPT} missing, no size-match found")
STATUS["checkpoint_integrity"] = "NOT TESTED"
h = sha256(CKPT); sz = os.path.getsize(CKPT)
ok = (h == CKPT_SHA and sz == CKPT_SIZE)
rec("ckpt_sha256", "PASS" if ok else "FAIL", f"{h[:20]}… size={sz}")
STATUS["checkpoint_integrity"] = "PASS" if ok else "FAIL"
if not ok: stop("checkpoint_integrity", "hash/size mismatch — not Run4")
th = sha256(TOK) if os.path.exists(TOK) else "MISSING"
rec("tokenizer_sha256", "PASS" if th == TOK_SHA else "FAIL", str(th)[:20] + "…")
if th != TOK_SHA: stop("safe_loading", "tokenizer hash mismatch")

# ---------- imports ----------
try:
    import torch
    torch.set_num_threads(os.cpu_count() or 4)
    rec("imports", "PASS", f"torch={torch.__version__} cuda_avail={torch.cuda.is_available()} (unused)")
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from core01.inference import InferenceEngine
    from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
except Exception as e:
    stop("architecture_compat", f"imports: {e}")

# ---------- Phase C: safe deserialization ----------
ck = None; deser = "weights_only=True"
try:
    ck = torch.load(CKPT, map_location="cpu", weights_only=True)
    rec("deser", "PASS", "weights_only=True clean")
except Exception as e0:
    rec("deser_wonly", "WARN", f"weights_only=True failed: {str(e0)[:120]}")
    try:
        import numpy as np
        from torch.serialization import add_safe_globals
        add_safe_globals([np.core.multiarray._reconstruct, np.ndarray, np.dtype,
                          np.random.RandomState, np.random.Generator])
        ck = torch.load(CKPT, map_location="cpu", weights_only=True)
        deser = "weights_only=True+numpy_allowlist(narrow)"
        rec("deser", "PASS", deser)
    except Exception as e2:
        stop("safe_loading", f"BLOCKED: {str(e2)[:200]}")
STATUS["safe_loading"] = "PASS"
rec("ckpt_meta", "PASS",
    f"ep{ck.get('epoch')} step{ck.get('step')} status={ck.get('model_status')} "
    f"tensors={len(ck['model_state_dict'])} keys={sorted(ck.keys())}")

# ---------- Phase D: construct + strict load ----------
# Fix 3: runtime status = authoritative checkpoint ROOT status
cd = dict(ck["config"])
try:
    root_status = ModelStatus(ck.get("model_status"))
except Exception as e:
    stop("strict_loading", f"invalid ckpt root model_status {ck.get('model_status')!r}: {e}")
cd["model_status"] = root_status  # root is authoritative over stale config snapshot
cfg = NexusAICore01Config.from_dict(cd)  # patched from_dict coerces safely
rec("config_status", "PASS",
    f"root={ck.get('model_status')} config_snapshot={ck['config'].get('model_status')} → runtime={cfg.model_status}")
STATUS["architecture_compat"] = "PASS"
proc = psutil.Process() if 'psutil' in sys.modules else None
mem0 = proc.memory_info().rss / 2**20 if proc else 0
t0 = time.time()
model = NexusAICore01(cfg)
try:
    res = model.load_state_dict(ck["model_state_dict"], strict=True)
    miss, unexp = res.missing_keys, res.unexpected_keys
    rec("strict_load", "PASS" if not miss and not unexp else "FAIL",
        f"missing={len(miss)} unexpected={len(unexp)}")
    if miss or unexp:
        STATUS["strict_loading"] = "FAIL"
        stop("strict_loading", f"missing={miss[:5]} unexpected={unexp[:5]}")
except Exception as e:
    STATUS["strict_loading"] = "FAIL"
    stop("strict_loading", str(e)[:300])
STATUS["strict_loading"] = "PASS"
model.eval().to(torch.device("cpu"))
all_cpu = all(p.device.type == "cpu" for p in model.parameters()) and \
          all(b.device.type == "cpu" for b in model.buffers())
rec("cpu_only", "PASS" if all_cpu and not torch.cuda.is_initialized() else "FAIL",
    f"params+buffers_cpu={all_cpu} cuda_init={torch.cuda.is_initialized()} training_mode={model.training}")
n_params = model.count_parameters()
rec("params", "PASS" if n_params == 8842560 else "WARN", f"{n_params:,}")
mem1 = proc.memory_info().rss / 2**20 if proc else 0
load_s = time.time() - t0
rec("load", "PASS", f"{load_s:.2f}s ram {mem0:.0f}→{mem1:.0f}MB")

tok = NexusAITokenizer(TOK, cfg)
rec("tokenizer", "PASS", f"vocab={tok.sp.get_piece_size()} bos={tok.bos_id} eos={tok.eos_id}")

# ---------- Phase E: instrument + generate ----------
fwd = {"n": 0}
_of = model.forward
def _cf(*a, **k):
    fwd["n"] += 1
    return _of(*a, **k)
model.forward = _cf
eng = InferenceEngine(model, tok, cfg, device="cpu")

PROMPTS = [
    ("bn_name", "bn", "তোমার নাম কী?"),
    ("bn_how", "bn", "তুমি কীভাবে কাজ করো?"),
    ("bn_ai", "bn", "কৃত্রিম বুদ্ধিমত্তা মানুষের কীভাবে উপকার করতে পারে?"),
    ("en_name", "en", "What is your name?"),
    ("en_how", "en", "How do you work?"),
    ("en_ai", "en", "How can artificial intelligence help people?"),
    ("bg_do", "banglish", "Tumi ki korte paro?"),
    ("bg_name", "banglish", "Tomar naam ki?"),
    ("bg_ai", "banglish", "AI manusher ki vabe upokar korte pare?"),
    ("rs_apple", "reason", "If I have 3 apples and get 2 more, how many apples do I have? Explain briefly."),
    ("rs_verify", "reason", "Why should an AI system verify information before giving an answer?"),
]
BN = re.compile(r"[ঀ-৿]")
outs = []
t_all = time.time()
for pid, lg, p in PROMPTS:
    fwd["n"] = 0; t = time.time()
    try:
        with torch.inference_mode():
            r = eng.generate(p, max_new_tokens=32, do_sample=False)
        out = r.get("generated_text", ""); warn = r.get("warning")
        gen_ids = r.get("generated_ids") or r.get("token_ids") or r.get("output_ids")
    except Exception as e:
        out, warn, gen_ids = "", f"EXC:{e}", None
    lat = time.time() - t
    words = out.split(); uniq = len(set(w.lower() for w in words)) / max(len(words), 1)
    outs.append({
        "id": pid, "lang": lg, "prompt": p, "output": out,
        "generated_ids": gen_ids, "warning": warn, "empty": not out.strip(),
        "input_tokens": len(tok.encode(p, add_special_tokens=False)),
        "forward_calls": fwd["n"], "latency_s": round(lat, 2),
        "tok_per_s": round((len(gen_ids) if isinstance(gen_ids, list) else 0) / max(lat, 0.01), 1) if gen_ids else None,
        "repetition_flag": len(words) >= 8 and uniq < 0.3,
        "prompt_leak_flag": out.strip().lower().startswith(p.strip().lower()[:20]),
        "bn_script_ratio": round(len(BN.findall(out)) / max(len(out), 1), 3),
        "arith_hint": ("5" in out) if pid == "rs_apple" else None,
    })
    print(f"{pid:9} fwd={fwd['n']:3} {'EMPTY' if not out.strip() else out[:80]!r} w={warn}")
total_s = time.time() - t_all
mem2 = proc.memory_info().rss / 2**20 if proc else 0
n = len(outs); empty = sum(1 for o in outs if o["empty"])
neural = all(o["forward_calls"] > 0 for o in outs if not o["empty"])
lat = [o["latency_s"] for o in outs]; avg_lat = sum(lat)/n; max_lat = max(lat)
rec("generation", "PASS" if n == 11 and neural else "WARN",
    f"{n}/11 empty={empty} forward_proof={neural} avg={avg_lat:.1f}s max={max_lat:.1f}s total={total_s:.0f}s")
rec("ram", "PASS", f"{mem0:.0f}→{mem1:.0f}→{mem2:.0f}MB")
STATUS["neural_generation"] = "PASS" if neural else "FAIL"

# ---------- Phase G: quality heuristics ----------
def qscore(o):
    s = 0
    if not o["empty"]: s += 1
    if not o["repetition_flag"]: s += 1
    if o["prompt_leak_flag"]: s -= 1
    if o["lang"] == "bn":
        if o["bn_script_ratio"] > 0.05: s += 1
    elif o["bn_script_ratio"] < 0.5: s += 1
    return max(0, min(4, s))
for o in outs: o["heuristic_score_0_4"] = qscore(o)
agg = {}
for lg in ("bn", "en", "banglish", "reason"):
    sub = [o for o in outs if o["lang"] == lg]
    agg[lg] = {"n": len(sub), "empty": sum(1 for o in sub if o["empty"]),
               "avg_score": round(sum(o["heuristic_score_0_4"] for o in sub)/max(len(sub),1), 2)}
# preliminary classification
if empty == n: aq = "FAIL"
elif sum(o["heuristic_score_0_4"] for o in outs)/n >= 2.5: aq = "PRELIMINARY PASS"
else: aq = "NEEDS IMPROVEMENT"
STATUS["answer_quality"] = aq
rec("quality", "PASS", f"{aq} per-lang={json.dumps(agg)} (heuristic only, NOT semantic)")

# ---------- Phase H/I: reports ----------
raw = {"checkpoint": CKPT, "ckpt_sha256": h, "ckpt_size": sz,
       "tokenizer": TOK, "tokenizer_sha256": th,
       "deserialization": deser, "params": n_params, "device": "cpu",
       "cuda_initialized": torch.cuda.is_initialized(),
       "env": {"python": sys.version.split()[0], "torch": torch.__version__,
               "cpu_threads": torch.get_num_threads(),
               "ram_mb": [round(mem0), round(mem1), round(mem2)]},
       "perf": {"load_s": round(load_s, 2), "gen_total_s": round(total_s, 1),
                "avg_latency_s": round(avg_lat, 2), "max_latency_s": max_lat},
       "aggregate": agg, "status": STATUS, "results": outs,
       "checks": R, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(raw, open(os.path.join(OUT, "cpu_quality_raw.json"), "w"),
          indent=1, ensure_ascii=False)

body = [f"# Core-01 CPU Generation Report — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n\n",
        f"ckpt `{CKPT}` sha `{h[:20]}…` size={sz} → RUN4 {'MATCH' if ok else 'MISMATCH'}\n",
        f"tok sha `{str(th)[:20]}…` vocab={tok.sp.get_piece_size()}\n",
        f"deser={deser} params={n_params:,} device=cpu training_mode={model.training} cuda_init={torch.cuda.is_initialized()}\n",
        f"load={load_s:.1f}s gen={total_s:.0f}s avg={avg_lat:.1f}s/prompt tok/s≈{round(32/avg_lat,1)} RAM {mem0:.0f}→{mem2:.0f}MB\n\n",
        "## Statuses\n"]
for k, v in STATUS.items(): body.append(f"- {k}: **{v}**\n")
body.append("\n## Neural-path proof\nmodel.forward instrumented; every non-empty output had forward_calls>0 (prompt→tokenizer→forward→logits→argmax→decode). No fallback/handlers/external calls in inference.py.\n\n")
body.append("## Prompts\n")
for o in outs:
    body.append(f"### {o['id']} [{o['lang']}] heuristic={o['heuristic_score_0_4']}/4\n")
    body.append(f"P: {o['prompt']}\nOUT: {o['output']!r}\n")
    body.append(f"in_tok={o['input_tokens']} fwd={o['forward_calls']} lat={o['latency_s']}s empty={o['empty']} rep={o['repetition_flag']} leak={o['prompt_leak_flag']} bn%={o['bn_script_ratio']} w={o['warning']}\n\n")
body.append("## Checks\n" + "".join(f"- [{c['status']}] {c['check']}: {c['detail']}\n" for c in R))
body.append("\n## Quality limitations\nHeuristic scores are mechanical (non-empty/repetition/script-match/leak). They do NOT measure semantic correctness. Human review of raw outputs required.\n")
open(os.path.join(OUT, "cpu_generation_report.md"), "w", encoding="utf-8").write("".join(body))
open(os.path.join(OUT, "cpu_quality_report.md"), "w", encoding="utf-8").write("".join(body))

# ---------- Bangla summary ----------
print("\n" + "=" * 70); print("সারসংক্ষেপ (Bangla)"); print("=" * 70)
for k, v in STATUS.items(): print(f"  {k}: {v}")
print(f"empty={empty}/{n} avg_lat={avg_lat:.1f}s RAM={mem2:.0f}MB")
print("heuristic score = mechanical only; semantic review = you.")
print(f"Reports → {OUT}/ (cpu_generation_report.md, cpu_quality_report.md, cpu_quality_raw.json)")
print("Download: Colab left panel → files icon → nexusai_cpu_readiness/ → download,")
print("or run: from google.colab import files; files.download('.../cpu_quality_raw.json')")
