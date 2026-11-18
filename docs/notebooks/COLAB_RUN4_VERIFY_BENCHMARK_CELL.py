# =============================================================================
# NEXUSAI RUN4 VERIFICATION + RUN3-vs-RUN4 NEURAL BENCHMARK CELL
# READ-ONLY evaluation: no training, no optimizer.step(), no ckpt writes.
# Applies the APPROVED inference fix to the workspace copy of inference.py
# (package ZIP predates the fix). Writes reports to Drive audit dir only.
# =============================================================================
import os, sys, json, glob, hashlib, time, traceback, shutil

EXPECTED = {
    "run3": {"sha": "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830",
             "size": 106777501, "epoch": 3, "step": 1341},
    "run4": {"sha": "761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1",
             "epoch": 5, "step": 9213},
}
OUTBASE = "/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT"
os.makedirs(OUTBASE, exist_ok=True)
TS = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(OUTBASE, f"audit_{TS}")
os.makedirs(OUT, exist_ok=True)
R = []
def rec(name, status, detail=""):
    R.append({"check": name, "status": status, "detail": str(detail)[:400]})
    print(f"[{status:>10}] {name} — {str(detail)[:150]}")

def sha256(p, chunk=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()

print("=" * 66); print("RUN4 VERIFY + RUN3-vs-RUN4 BENCHMARK"); print("=" * 66)

# ---------- env ----------
import platform
rec("env", "PASS", f"py{sys.version.split()[0]} torch={__import__('torch').__version__}")
try:
    import torch
    if torch.cuda.is_available():
        rec("gpu", "PASS", f"{torch.cuda.get_device_name(0)} "
            f"{torch.cuda.get_device_properties(0).total_memory/2**30:.1f}GB")
    else:
        rec("gpu", "WARN", "CPU-only — benchmark will run on CPU (slower)")
except Exception as e:
    rec("gpu", "FAIL", e)

# ---------- drive ----------
try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    rec("drive", "PASS", "mounted")
except Exception as e:
    rec("drive", "FAIL", e)

# ---------- locate package ----------
PKG = None
for dp, dn, fn in os.walk("/content"):
    if "MANIFEST.json" in fn and "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE" in dp:
        PKG = dp; break
if not PKG:
    zips = glob.glob("/content/drive/MyDrive/**/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip", recursive=True)
    if zips:
        import zipfile
        dst = "/content/nexusai_pkg_extract"
        with zipfile.ZipFile(zips[0]) as z: z.extractall(dst)
        PKG = os.path.join(dst, "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE")
if not PKG or not os.path.isdir(PKG):
    rec("package", "FAIL", "package not found/extracted"); raise SystemExit(1)
rec("package", "PASS", PKG)

AI = os.path.join(PKG, "nexusai")
sys.path.insert(0, AI); sys.path.insert(0, os.path.join(AI, "models"))

# ---------- apply APPROVED inference fix to workspace copy ----------
INF = os.path.join(AI, "core01", "inference.py")
src = open(INF, encoding="utf-8").read()
OLD_ENC = """        # Encode prompt
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        
        # Generate
        with torch.no_grad():"""
NEW_ENC = """        # Encode prompt: BOS only, NO terminal EOS (unfinished prompt).
        content_ids = self.tokenizer.encode(prompt, add_special_tokens=False)
        input_ids = [self.tokenizer.bos_id] + content_ids
        max_len = getattr(self.config, "max_len", 512)
        if len(input_ids) > max_len:
            input_ids = [self.tokenizer.bos_id] + input_ids[-(max_len - 1):]
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        prompt_len = input_ids.shape[1]
        
        # Generate
        with torch.inference_mode():"""
OLD_DEC = """        # Decode
        generated_ids = generated_ids[0].cpu().tolist()
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Remove prompt from response
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return {
            "generated_text": generated_text,
            "model_status": self.config.model_status.value,
            "warning": None
        }"""
NEW_DEC = """        # Decode ONLY generated tokens (model.generate returns full seq)
        new_ids = generated_ids[0, prompt_len:].cpu().tolist()
        generated_text = self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        
        return {
            "generated_text": generated_text,
            "model_status": self.config.model_status.value,
            "warning": None if generated_text else "EMPTY_GENERATION"
        }"""
try:
    if OLD_ENC in src and OLD_DEC in src:
        src = src.replace(OLD_ENC, NEW_ENC).replace(OLD_DEC, NEW_DEC)
        open(INF, "w", encoding="utf-8").write(src)
        rec("inference_fix", "PASS", "approved fix applied to workspace copy")
    elif NEW_ENC.split("\n")[1].strip() in src:
        rec("inference_fix", "PASS", "already applied")
    else:
        rec("inference_fix", "FAIL", "patch anchors not found — source differs")
except Exception as e:
    rec("inference_fix", "FAIL", e)

# ---------- imports ----------
try:
    import torch
    from core01.inference import InferenceEngine
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from nexusai_core_01.config.model_config import (
        NexusAICore01Config, ModelStatus)
    rec("imports", "PASS", "production modules")
except Exception as e:
    rec("imports", "FAIL", e); traceback.print_exc(); raise SystemExit(1)

TOK = os.path.join(AI, "tokenizer", "sp_bpe_8k.model")
CKPT3 = os.path.join(PKG, "checkpoints/verified/core01_run3_checkpoint_final.pt")
CKPT4_CANDS = [
    "/content/drive/MyDrive/NEXUSAI_RUN4/checkpoint_final.pt",
    "/content/drive/MyDrive/NexusAI/checkpoints/core01_run4/checkpoint_final.pt",
]
CKPT4 = next((p for p in CKPT4_CANDS if os.path.exists(p)), None)
if not CKPT4:
    hits = glob.glob("/content/drive/MyDrive/**/checkpoint_final.pt", recursive=True)
    CKPT4 = hits[0] if hits else None

# ---------- checkpoint verification ----------
def verify_ckpt(path, exp, tag):
    out = {"tag": tag, "path": path}
    if not path or not os.path.exists(path):
        out["exists"] = False; rec(f"{tag}_exists", "FAIL", path); return out, None
    out["exists"] = True
    out["size"] = os.path.getsize(path)
    out["sha256"] = sha256(path)
    out["sha_match"] = out["sha256"] == exp["sha"]
    rec(f"{tag}_sha", "PASS" if out["sha_match"] else "FAIL",
        f"{out['sha256'][:20]}… size={out['size']}")
    try:
        ck = torch.load(path, map_location="cpu", weights_only=False)
        out["epoch"] = ck.get("epoch"); out["step"] = ck.get("step")
        out["status"] = ck.get("model_status")
        out["keys"] = sorted(ck.keys())
        sd = ck["model_state_dict"]
        out["tensors"] = len(sd)
        out["resume_keys"] = all(k in ck for k in
            ("optimizer_state_dict","scheduler_state_dict",
             "grad_scaler_state_dict","rng_state"))
        rec(f"{tag}_meta", "PASS",
            f"ep{out['epoch']}/step{out['step']} status={out['status']} "
            f"tensors={out['tensors']} resume={out['resume_keys']}")
        return out, ck
    except Exception as e:
        rec(f"{tag}_load", "FAIL", e); return out, None

v3, ck3 = verify_ckpt(CKPT3, EXPECTED["run3"], "run3")
v4, ck4 = verify_ckpt(CKPT4, EXPECTED["run4"], "run4")
json.dump(v3, open(os.path.join(OUT, "RUN3_CHECKPOINT_VERIFICATION.json"), "w"), indent=1)
json.dump(v4, open(os.path.join(OUT, "RUN4_CHECKPOINT_VERIFICATION.json"), "w"), indent=1)

if not (v3.get("sha_match") and v4.get("sha_match")):
    rec("gate", "FAIL", "checkpoint hash mismatch — benchmark STOPPED")
    raise SystemExit(1)

# ---------- model+tokenizer+engine builder ----------
def build_engine(ck, tag):
    cd = dict(ck["config"])
    if isinstance(cd.get("model_status"), str):
        cd["model_status"] = ModelStatus[cd["model_status"]]
    # truthful status from top-level metadata
    top = ck.get("model_status")
    if isinstance(top, str) and top in ModelStatus.__members__:
        cd["model_status"] = ModelStatus[top]
    cfg = NexusAICore01Config(
        **{k: v for k, v in cd.items()
           if k in NexusAICore01Config.__dataclass_fields__})
    model = NexusAICore01(cfg)
    res = model.load_state_dict(ck["model_state_dict"], strict=True)
    assert not res.missing_keys and not res.unexpected_keys
    tok = NexusAITokenizer(TOK, cfg)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    eng = InferenceEngine(model, tok, cfg, device=dev)
    rec(f"{tag}_strict_load", "PASS",
        f"params={model.count_parameters():,} dev={dev}")
    return eng

e3 = build_engine(ck3, "run3")
e4 = build_engine(ck4, "run4")

# ---------- prompt suite (fixed, identical for both) ----------
PROMPTS = [
    # (id, lang_group, category, prompt)
    ("bn_stmt", "bn", "bengali", "বাংলাদেশ একটি সুন্দর দেশ।"),
    ("bn_qa",   "bn", "bengali", "বাংলাদেশের রাজধানী কী?"),
    ("bn_id",   "bn", "bengali", "তোমার নাম কী? তুমি কে?"),
    ("bn_inst", "bn", "bengali", "একটি_sentence_বাংলায়_লিখো।"),
    ("bn_expl", "bn", "bengali", "বৃষ্টি কেন হয়? ব্যাখ্যা করো।"),
    ("en_greet","en", "english", "Hello! How are you today?"),
    ("en_qa",   "en", "english", "What is the capital of France?"),
    ("en_inst", "en", "english", "Write one sentence about the moon."),
    ("en_expl", "en", "english", "Explain what a computer is in one sentence."),
    ("en_chat", "en", "english", "Thank you for your help!"),
    ("bg_qa",   "banglish", "banglish", "Bangladesh er rajdhani ki?"),
    ("bg_inst", "banglish", "banglish", "Gach niye ekta sentence likho."),
    ("mx_qa",   "mixed", "mixed", "What is বাংলাদেশের national animal?"),
    ("mx_chat", "mixed", "mixed", "Ami bhalo achi, tumi ki?"),
    ("ma_add",  "en", "math", "What is 7 plus 8? Answer:"),
    ("ma_mul",  "en", "math", "What is 6 times 9? Answer:"),
    ("ma_word", "en", "math", "Tom has 5 apples and buys 3 more. How many now?"),
    ("ma_bn",   "bn", "math", "৫ আর ৭ যোগ করলে কত?"),
]

def run_bench(engine, tag, mode, **kw):
    torch.manual_seed(42)
    res = []
    for pid, lg, cat, prompt in PROMPTS:
        t = time.time()
        try:
            r = engine.generate(prompt, max_new_tokens=48, **kw)
            out = r.get("generated_text", "")
            warn = r.get("warning")
        except Exception as e:
            out, warn = "", f"EXC:{e}"
        dt = time.time() - t
        # metrics
        import re
        bn = bool(re.search(r"[ঀ-৿]", out))
        prompt_in_out = out.strip().startswith(prompt.strip()[:20])
        res.append({"id": pid, "lang": lg, "cat": cat, "prompt": prompt,
                    "output": out, "warning": warn, "latency_s": round(dt, 2),
                    "empty": len(out.strip()) == 0,
                    "bn_script": bn,
                    "prompt_leak": prompt_in_out})
    n = len(res)
    def rate(f): return round(sum(1 for r in res if f(r)) / n, 3)
    summary = {
        "tag": tag, "mode": mode, "kw": kw, "n": n,
        "empty_rate": rate(lambda r: r["empty"]),
        "prompt_leak_rate": rate(lambda r: r["prompt_leak"]),
        "bn_output_rate_all": rate(lambda r: r["bn_script"]),
        "avg_latency_s": round(sum(r["latency_s"] for r in res) / n, 2),
        "results": res,
    }
    json.dump(summary, open(os.path.join(
        OUT, f"{tag.upper()}_BENCHMARK_{mode.upper()}.json"), "w"),
        indent=1, ensure_ascii=False)
    print(f"[{tag}/{mode}] empty={summary['empty_rate']} "
          f"leak={summary['prompt_leak_rate']} lat={summary['avg_latency_s']}s")
    return summary

s3g = run_bench(e3, "run3", "greedy", do_sample=False)
s4g = run_bench(e4, "run4", "greedy", do_sample=False)
s3s = run_bench(e3, "run3", "sample", do_sample=True, temperature=0.8,
                top_k=50, top_p=0.9)
s4s = run_bench(e4, "run4", "sample", do_sample=True, temperature=0.8,
                top_k=50, top_p=0.9)

# ---------- comparison ----------
def cmp(a, b):
    return {"metric": "x"}
comparison = {
    "greedy": {"run3": {k: s3g[k] for k in
                ("empty_rate","prompt_leak_rate","avg_latency_s")},
               "run4": {k: s4g[k] for k in
                ("empty_rate","prompt_leak_rate","avg_latency_s")}},
    "sample": {"run3": {k: s3s[k] for k in
                ("empty_rate","prompt_leak_rate","avg_latency_s")},
               "run4": {k: s4s[k] for k in
                ("empty_rate","prompt_leak_rate","avg_latency_s")}},
    "note": "lower empty/leak is better; latency informational only",
}
json.dump(comparison, open(os.path.join(
    OUT, "RUN3_VS_RUN4_COMPARISON.json"), "w"), indent=1)

# samples file (all outputs preserved verbatim)
samples = {"greedy": {"run3": s3g["results"], "run4": s4g["results"]},
           "sample": {"run3": s3s["results"], "run4": s4s["results"]}}
json.dump(samples, open(os.path.join(
    OUT, "ACTUAL_GENERATION_SAMPLES.json"), "w"),
    indent=1, ensure_ascii=False)

# ---------- post-benchmark integrity ----------
post = {"run3_sha_after": sha256(CKPT3), "run4_sha_after": sha256(CKPT4)}
post["run3_unchanged"] = post["run3_sha_after"] == EXPECTED["run3"]["sha"]
post["run4_unchanged"] = post["run4_sha_after"] == EXPECTED["run4"]["sha"]
json.dump(post, open(os.path.join(
    OUT, "CHECKPOINT_INTEGRITY_FINAL.json"), "w"), indent=1)
rec("integrity_final", "PASS" if post["run3_unchanged"] and
    post["run4_unchanged"] else "FAIL", str(post))

# ---------- report ----------
md = f"""# Run4 Verification + Run3-vs-Run4 Benchmark — {TS}
Env: {platform.system()} py{sys.version.split()[0]} torch={torch.__version__}
GPU: {'yes' if torch.cuda.is_available() else 'no'}
Package: {PKG}
Run3: {CKPT3}\n  sha={v3.get('sha256','')[:24]}… ep{v3.get('epoch')} step{v3.get('step')} val_loss={ck3.get('val_loss')}\nRun4: {CKPT4}\n  sha={v4.get('sha256','')[:24]}… ep{v4.get('epoch')} step{v4.get('step')} val_loss={ck4.get('val_loss')} train_loss={ck4.get('train_loss')}
Inference fix applied to workspace copy: see checks.

## Greedy comparison
run3: {json.dumps({k:s3g[k] for k in ('empty_rate','prompt_leak_rate','avg_latency_s')})}
run4: {json.dumps({k:s4g[k] for k in ('empty_rate','prompt_leak_rate','avg_latency_s')})}

## Sample comparison (temp0.8 top_k50 top_p0.9 seed42)
run3: {json.dumps({k:s3s[k] for k in ('empty_rate','prompt_leak_rate','avg_latency_s')})}
run4: {json.dumps({k:s4s[k] for k in ('empty_rate','prompt_leak_rate','avg_latency_s')})}

Integrity after: run3_unchanged={post['run3_unchanged']} run4_unchanged={post['run4_unchanged']}
Full outputs: ACTUAL_GENERATION_SAMPLES.json in this folder.
"""
open(os.path.join(OUT, "NEXUSAI_RUN4_VERIFICATION_AND_BENCHMARK_REPORT.md"),
     "w", encoding="utf-8").write(md)

print("\n" + "=" * 66)
print("DONE. Output dir:", OUT)
print("=" * 66)
