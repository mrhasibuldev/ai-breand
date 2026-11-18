# =============================================================================
# NEXUSAI RUN4 CPU VERIFICATION v7 — self-contained, read-only, CPU-only
# Reports -> /content/NEXUSAI_RUN4_CPU_AUDIT/ (local, never requires Drive write)
# Work    -> /content/NEXUSAI_RUN4_CPU_VERIFY_WORK/ (extract + runtime patches)
# weights_only=True only. strict=True. No training. No external AI.
# =============================================================================
import os, sys, json, glob, hashlib, time, traceback, re

CKPT = "/content/drive/MyDrive/NEXUSAI_RUN4/checkpoint_final.pt"
CKPT_SHA = "761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1"
CKPT_SIZE = 106777501
TOK_SHA = "2fcc6a87c9ded27d1f8ad6c2dc0ff747ca4dc52db68ffde9a6e229b2cd3d8052"
ZIP_SHA = "f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644"
PKG_PREFERRED = "/content/NEXUSAI_RUN4_RECOVERY_WORK/package/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE"
WORK = "/content/NEXUSAI_RUN4_CPU_VERIFY_WORK"
OUT = "/content/NEXUSAI_RUN4_CPU_AUDIT"
SRC_HASHES = {
    "core01/transformer.py": "c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc",
}
for d in (WORK, OUT):
    os.makedirs(d, exist_ok=True)
# write-permission preflight (local only — never depends on Drive)
try:
    _pf = os.path.join(OUT, ".write_test")
    open(_pf, "w").write("ok"); os.remove(_pf)
    rec_init = "PASS"
except Exception as e:
    rec_init = f"FAIL: {e}"

R = []
STATUS = {"checkpoint_integrity": "NOT TESTED", "safe_loading": "NOT TESTED",
          "architecture_compat": "NOT TESTED", "strict_loading": "NOT TESTED",
          "neural_generation": "NOT TESTED", "answer_quality": "NOT TESTED"}
def rec(n, s, d=""):
    R.append({"check": n, "status": s, "detail": str(d)[:400]})
    print(f"[{s:>10}] {n} — {str(d)[:150]}")
def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""): h.update(c)
    return h.hexdigest()
def stop(phase, msg):
    STATUS[phase] = "BLOCKED"
    rec("STOP", "FAIL", f"{phase}: {msg}")
    try:
        json.dump({"status": STATUS, "checks": R, "stopped_at": phase,
                   "error": msg,
                   "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                  open(os.path.join(OUT, "NEXUSAI_RUN4_CPU_VERIFICATION.json"), "w"), indent=1)
    except Exception:
        pass
    raise SystemExit(1)

print("=" * 72)
print("NEXUSAI RUN4 CPU VERIFICATION v7")
print("=" * 72)
rec("env", "PASS" if rec_init == "PASS" else "FAIL",
    f"py{sys.version.split()[0]} local_write={rec_init}")
if rec_init != "PASS":
    print("FATAL: cannot write reports locally"); raise SystemExit(1)

# ---------- Drive (conditional mount, read-only tolerant) ----------
try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    rec("drive", "PASS", "mounted-or-present (read-only OK)")
except Exception as e:
    rec("drive", "WARN", f"{e} — continuing if files reachable")

# ---------- package (preferred extract -> recursive -> hash-gated ZIP) ----------
PKG = PKG_PREFERRED if os.path.isdir(PKG_PREFERRED) else None
if not PKG:
    for dp, dn, fn in os.walk("/content"):
        if "MANIFEST.json" in fn and "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE" in dp:
            PKG = dp; break
if not PKG:
    zips = glob.glob("/content/drive/MyDrive/**/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip", recursive=True)
    if not zips: stop("checkpoint_integrity", "package not found")
    zh = sha256(zips[0])
    rec("zip_sha256", "PASS" if zh == ZIP_SHA else "FAIL", zh[:20] + "…")
    if zh != ZIP_SHA: stop("checkpoint_integrity", "ZIP hash mismatch")
    import zipfile
    dst = os.path.join(WORK, "pkg_extract")
    with zipfile.ZipFile(zips[0]) as z:
        bad = [n for n in z.namelist() if n.startswith("/") or ".." in n.split("/")]
        if bad: stop("checkpoint_integrity", f"{len(bad)} unsafe zip paths")
        z.extractall(dst)
    PKG = os.path.join(dst, "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE")
rec("package", "PASS", PKG)
AI = os.path.join(PKG, "nexusai")

# ---------- runtime patches on WORKING COPY only ----------
PATCHES = [
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
        return cls(**fields)'''),
]
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
        """Fixed generate: type-safe status, BOS-only prompt, generated-IDs
        decode, inference_mode."""
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
            "generated_ids": new_ids,
            "model_status": status_value,
            "warning": None if generated_text else "EMPTY_GENERATION"
        }

'''
patched = 0
for fpath, old, new in PATCHES:
    if not os.path.exists(fpath):
        stop("architecture_compat", f"missing {fpath}")
    src = open(fpath, encoding="utf-8").read()
    if new.strip() in src:
        patched += 1; continue
    if old not in src:
        stop("architecture_compat", f"pattern not found in {os.path.basename(fpath)}")
    open(fpath, "w", encoding="utf-8").write(src.replace(old, new, 1))
    patched += 1
inf = os.path.join(AI, "core01", "inference.py")
src = open(inf, encoding="utf-8").read()
if "generated_ids" in src and "inference_mode():" in src:
    patched += 1
else:
    a = src.find("    def generate("); b = src.find("    def load_checkpoint")
    if a < 0 or b <= a:
        stop("architecture_compat", "generate/load_checkpoint markers not found")
    src = src[:a] + FIXED_GENERATE + src[b:]
    open(inf, "w", encoding="utf-8").write(src)
    patched += 1
rec("source_patch", "PASS" if patched == len(PATCHES) + 1 else "FAIL",
    f"{patched}/{len(PATCHES)+1} fixes on working copy only")
if patched != len(PATCHES) + 1: raise SystemExit(1)

# source-hash gate (transformer must match manifest)
for rel, exp in SRC_HASHES.items():
    p = os.path.join(AI, rel)
    got = sha256(p) if os.path.exists(p) else "MISSING"
    rec(f"src:{rel}", "PASS" if got == exp else "FAIL", str(got)[:20] + "…")
    if got != exp: stop("architecture_compat", f"{rel} hash mismatch")
sys.path.insert(0, AI); sys.path.insert(0, os.path.join(AI, "models"))
TOK = os.path.join(AI, "tokenizer", "sp_bpe_8k.model")

# ---------- checkpoint + tokenizer gates ----------
if not os.path.exists(CKPT):
    hits = [p for p in glob.glob("/content/drive/MyDrive/**/*.pt", recursive=True)
            if os.path.getsize(p) == CKPT_SIZE]
    if hits: CKPT = hits[0]
if not os.path.exists(CKPT): stop("checkpoint_integrity", "checkpoint not found")
h = sha256(CKPT); sz = os.path.getsize(CKPT)
ok = (h == CKPT_SHA and sz == CKPT_SIZE)
rec("ckpt_sha256", "PASS" if ok else "FAIL", f"{h[:20]}… size={sz}")
STATUS["checkpoint_integrity"] = "PASS" if ok else "FAIL"
if not ok: stop("checkpoint_integrity", "not Run4")
th = sha256(TOK) if os.path.exists(TOK) else "MISSING"
rec("tokenizer_sha256", "PASS" if th == TOK_SHA else "FAIL", str(th)[:20] + "…")
if th != TOK_SHA: stop("safe_loading", "tokenizer hash mismatch")

# ---------- imports ----------
try:
    import torch, psutil
    torch.set_num_threads(os.cpu_count() or 4)
    rec("imports", "PASS", f"torch={torch.__version__} cuda_avail={torch.cuda.is_available()} (unused)")
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from core01.inference import InferenceEngine
    from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
except Exception as e:
    stop("architecture_compat", f"imports: {e}")

# ---------- safe deserialization ----------
ck = None; deser = "weights_only=True"
try:
    ck = torch.load(CKPT, map_location="cpu", weights_only=True)
    rec("deser", "PASS", "weights_only=True clean")
except Exception as e0:
    rec("deser_wonly", "WARN", f"weights_only=True failed: {str(e0)[:120]}")
    try:
        import numpy as np
        from torch.serialization import add_safe_globals
        cands = []
        for base in ("numpy._core", "numpy.core"):
            try:
                ma = __import__(f"{base}.multiarray", fromlist=["_reconstruct"])
                for attr in ("_reconstruct", "ndarray", "dtype"):
                    v = getattr(ma, attr, None)
                    if v is not None: cands.append(v)
            except Exception: pass
        try:
            import numpy as _np
            if hasattr(_np, "dtype"): cands.append(_np.dtype)
        except Exception: pass
        # numpy 2.x RNG state pickles dtype CLASSES (e.g. UInt32DType)
        try:
            import numpy.dtypes as _nd
            for _n in dir(_nd):
                _v = getattr(_nd, _n)
                if isinstance(_v, type) and _n.endswith("DType"):
                    cands.append(_v)
        except Exception: pass
        try:
            nr = __import__("numpy.random", fromlist=["RandomState", "Generator"])
            cands += [getattr(nr, "RandomState", None), getattr(nr, "Generator", None)]
        except Exception: pass
        cands = [c for c in dict.fromkeys(cands) if c is not None]
        add_safe_globals(cands)
        ck = torch.load(CKPT, map_location="cpu", weights_only=True)
        deser = f"weights_only=True+allowlist({len(cands)} numpy types)"
        rec("deser", "PASS", deser)
    except Exception as e2:
        stop("safe_loading", f"BLOCKED: {str(e2)[:200]}")
STATUS["safe_loading"] = "PASS"

# ---------- config + strict load ----------
_cfg_raw = ck.get("config")
if not isinstance(_cfg_raw, dict):
    stop("architecture_compat", "checkpoint missing 'config' dict")
cd = dict(_cfg_raw)
try:
    root_status = ModelStatus(ck.get("model_status"))
except Exception as e:
    stop("strict_loading", f"invalid ckpt root model_status {ck.get('model_status')!r}: {e}")
cd["model_status"] = root_status
try:
    cfg = NexusAICore01Config.from_dict(cd)
except Exception as e:
    stop("architecture_compat", f"config build: {e}")
rec("config_status", "PASS",
    f"root={ck.get('model_status')} snapshot={_cfg_raw.get('model_status')} → {cfg.model_status}")
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
    f"params+buffers_cpu={all_cpu} cuda_init={torch.cuda.is_initialized()} training={model.training}")
n_params = model.count_parameters()
rec("params", "PASS" if n_params == 8842560 else "WARN", f"{n_params:,}")
mem1 = proc.memory_info().rss / 2**20 if proc else 0
load_s = time.time() - t0
rec("load", "PASS", f"{load_s:.2f}s ram {mem0:.0f}→{mem1:.0f}MB")

# ---------- tokenizer + round-trips ----------
tok = NexusAITokenizer(TOK, cfg)
rec("tokenizer", "PASS", f"vocab={tok.sp.get_piece_size()} bos={tok.bos_id} eos={tok.eos_id}")
RT_TESTS = {"en": "Hello, how are you?",
            "bn": "হ্যালো, তুমি কেমন আছো?",
            "banglish": "Tumi kemon acho? Ami bhalo achi."}
rt = {}
for k, t in RT_TESTS.items():
    ids = tok.encode(t, add_special_tokens=False)
    dec = tok.decode(ids, skip_special_tokens=False)
    unk = sum(1 for i in ids if i == tok.unk_id)
    rt[k] = {"ids": len(ids), "unk": unk, "roundtrip_nonempty": dec.strip() != ""}
rec("tokenizer_roundtrip", "PASS" if all(v["roundtrip_nonempty"] for v in rt.values()) else "WARN",
    json.dumps(rt))

# ---------- instrument + generate ----------
fwd = {"n": 0}
_of = model.forward
def _cf(*a, **k):
    fwd["n"] += 1
    return _of(*a, **k)
model.forward = _cf
# capture generated IDs via decode wrapper (no source modification)
_last_ids = {"ids": None}
_od = tok.decode
def _cd(ids, **k):
    _last_ids["ids"] = list(ids)
    return _od(ids, **k)
tok.decode = _cd
eng = InferenceEngine(model, tok, cfg, device="cpu")

PROMPTS = [
    ("bn_name", "bn", "তোমার নাম কী?"),
    ("bn_how", "bn", "তুমি কীভাবে কাজ করো?"),
    ("bn_ai", "bn", "কৃত্রিম বুদ্ধিমত্তা কী?"),
    ("en_name", "en", "What is your name?"),
    ("en_how", "en", "How do you work?"),
    ("en_ai", "en", "What is artificial intelligence?"),
    ("bg_do", "banglish", "Tumi ki korte paro?"),
    ("bg_name", "banglish", "Tomar naam ki?"),
    ("bg_ai", "banglish", "AI manusher ki vabe upokar korte pare?"),
    ("rs_apple", "reason", "If I have 3 apples and buy 2 more, how many apples do I have?"),
    ("rs_sun", "reason", "Why does the sun appear bright during the day?"),
]
BN = re.compile(r"[ঀ-৿]")
outs = []
t_all = time.time()
for pid, lg, p in PROMPTS:
    fwd["n"] = 0; _last_ids["ids"] = None; t = time.time()
    try:
        with torch.inference_mode():
            r = eng.generate(p, max_new_tokens=32, do_sample=False)
        out = r.get("generated_text", ""); warn = r.get("warning")
        gen_ids = r.get("generated_ids") or _last_ids["ids"]
    except Exception as e:
        out, warn, gen_ids = "", f"EXC:{e}", None
    lat = time.time() - t
    words = out.split(); uniq = len(set(w.lower() for w in words)) / max(len(words), 1)
    outs.append({
        "id": pid, "lang": lg, "prompt": p, "output": out,
        "generated_ids": gen_ids, "gen_token_count": len(gen_ids) if gen_ids else 0,
        "warning": warn, "empty": not out.strip(),
        "input_tokens": len(tok.encode(p, add_special_tokens=False)),
        "forward_calls": fwd["n"], "latency_s": round(lat, 2),
        "tok_per_s": round(len(gen_ids)/lat, 1) if gen_ids and lat else None,
        "repetition_flag": len(words) >= 8 and uniq < 0.3,
        "prompt_leak_flag": out.strip().lower().startswith(p.strip().lower()[:20]),
        "bn_script_ratio": round(len(BN.findall(out)) / max(len(out), 1), 3),
    })
    print(f"{pid:9} fwd={fwd['n']:3} ids={len(gen_ids) if gen_ids else 0:2} "
          f"{'EMPTY' if not out.strip() else out[:70]!r} w={warn}")
total_s = time.time() - t_all
mem2 = proc.memory_info().rss / 2**20 if proc else 0
n = len(outs); empty = sum(1 for o in outs if o["empty"])
neural = all(o["forward_calls"] > 0 for o in outs if not o["empty"])
lat = [o["latency_s"] for o in outs]; avg_lat = sum(lat)/n; max_lat = max(lat)
rec("generation", "PASS" if n == 11 and neural else "WARN",
    f"{n}/11 empty={empty} forward_proof={neural} avg={avg_lat:.1f}s max={max_lat:.1f}s total={total_s:.0f}s")
rec("ram", "PASS", f"{mem0:.0f}→{mem1:.0f}→{mem2:.0f}MB")
STATUS["neural_generation"] = "PASS" if neural else "FAIL"

# ---------- post-test integrity re-hash ----------
h2 = sha256(CKPT); th2 = sha256(TOK)
drift = (h2 != h) or (th2 != th)
rec("post_hash", "PASS" if not drift else "FAIL",
    f"ckpt_unchanged={h2==h} tok_unchanged={th2==th}")

# ---------- quality diagnostics ----------
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
if empty == n: aq = "FAIL"
elif sum(o["heuristic_score_0_4"] for o in outs)/n >= 2.5: aq = "PRELIMINARY PASS"
else: aq = "NEEDS IMPROVEMENT"
STATUS["answer_quality"] = aq
rec("quality", "PASS", f"{aq} per-lang={json.dumps(agg)} (heuristic only)")

# ---------- reports ----------
raw = {"checkpoint": CKPT, "ckpt_sha256_before": h, "ckpt_sha256_after": h2,
       "ckpt_size": sz, "tokenizer_sha256_before": th, "tokenizer_sha256_after": th2,
       "deserialization": deser, "params": n_params, "device": "cpu",
       "cuda_initialized": torch.cuda.is_initialized(),
       "env": {"python": sys.version.split()[0], "torch": torch.__version__,
               "cpu_threads": torch.get_num_threads(),
               "ram_mb": [round(mem0), round(mem1), round(mem2)]},
       "perf": {"load_s": round(load_s, 2), "gen_total_s": round(total_s, 1),
                "avg_latency_s": round(avg_lat, 2), "max_latency_s": max_lat},
       "tokenizer_roundtrip": rt, "aggregate": agg, "status": STATUS,
       "results": outs, "checks": R,
       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(raw, open(os.path.join(OUT, "NEXUSAI_RUN4_CPU_VERIFICATION.json"), "w"),
          indent=1, ensure_ascii=False)
json.dump({"results": outs, "aggregate": agg, "status": STATUS},
          open(os.path.join(OUT, "NEXUSAI_RUN4_CPU_GENERATION_OUTPUTS.json"), "w"),
          indent=1, ensure_ascii=False)

body = [f"# Run4 CPU Verification Report v7 — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}\n\n",
        f"ckpt `{CKPT}` sha `{h[:20]}…`→`{h2[:20]}…` {'UNCHANGED' if h==h2 else 'DRIFT!'}\n",
        f"tok sha `{str(th)[:20]}…`→`{str(th2)[:20]}…` {'UNCHANGED' if th==th2 else 'DRIFT!'}\n",
        f"deser={deser} params={n_params:,} cpu_only={all_cpu} cuda_init={torch.cuda.is_initialized()}\n",
        f"load={load_s:.1f}s gen={total_s:.0f}s avg={avg_lat:.1f}s/prompt tok/s≈{round(32/avg_lat,1)} RAM {mem0:.0f}→{mem2:.0f}MB\n\n",
        "## Statuses\n"]
for k, v in STATUS.items(): body.append(f"- {k}: **{v}**\n")
body.append("\n## Tokenizer round-trips\n" + json.dumps(rt, indent=1) + "\n\n")
body.append("## Prompts\n")
for o in outs:
    body.append(f"### {o['id']} [{o['lang']}] heuristic={o['heuristic_score_0_4']}/4\n")
    body.append(f"P: {o['prompt']}\nOUT: {o['output']!r}\n")
    body.append(f"in_tok={o['input_tokens']} gen_ids={o['gen_token_count']} fwd={o['forward_calls']} "
                f"lat={o['latency_s']}s tok/s={o['tok_per_s']} empty={o['empty']} "
                f"rep={o['repetition_flag']} leak={o['prompt_leak_flag']} bn%={o['bn_script_ratio']} w={o['warning']}\n\n")
body.append("## Checks\n" + "".join(f"- [{c['status']}] {c['check']}: {c['detail']}\n" for c in R))
body.append("\n## Limitations\nHeuristic scores are mechanical only — NOT semantic quality. "
            "Human review of raw outputs required for real verdict. "
            "weights_only=True (+narrow numpy allowlist for RNG state). "
            "Drive write never required; optional copy attempted separately.\n")
rep = "".join(body)
open(os.path.join(OUT, "NEXUSAI_RUN4_CPU_VERIFICATION_REPORT.md"), "w",
     encoding="utf-8").write(rep)
open(os.path.join(OUT, "NEXUSAI_RUN4_CPU_FORENSIC_AUDIT.md"), "w",
     encoding="utf-8").write(
     "# Run4 CPU Forensic Audit (v7 runtime)\n\n" + rep +
     "\n\nGenerated by v7 cell — see VERIFICATION.json for machine-readable data.\n")

# optional Drive copy — fail gracefully, never required
try:
    dst = "/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT"
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(OUT):
        if f.startswith("NEXUSAI_RUN4_CPU"):
            import shutil; shutil.copy2(os.path.join(OUT, f), os.path.join(dst, f))
    rec("drive_copy", "PASS", "optional copy succeeded")
except Exception as e:
    rec("drive_copy", "WARN", f"skipped (Drive read-only or absent): {str(e)[:100]}")

# ---------- Bangla summary ----------
print("\n" + "=" * 72); print("সারসংক্ষেপ (Bangla)"); print("=" * 72)
for k, v in STATUS.items(): print(f"  {k}: {v}")
print(f"empty={empty}/{n} avg_lat={avg_lat:.1f}s RAM={mem2:.0f}MB post_hash_drift={drift}")
for lg, a in agg.items(): print(f"  {lg}: n={a['n']} empty={a['empty']} heuristic={a['avg_score']}/4")
print("heuristic = mechanical only; semantic review = you.")
print(f"Reports → {OUT}/ (4 files) | optional Drive copy attempted")
