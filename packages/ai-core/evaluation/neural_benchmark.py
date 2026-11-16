"""
NexusAI Core-01 Neural-Only Benchmark

Runs the ACTUAL model weights (Run3 checkpoint) directly — no API, no
deterministic handlers, no fallback. Produces honest generation evidence.

Usage (repo root):
    python packages/ai-core/evaluation/neural_benchmark.py
Output: eval_reports/neural_benchmark_<ts>.json + console table.
"""
import sys, os, json, time, re, hashlib
from datetime import datetime, timezone

AI_CORE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       os.pardir)                      # packages/ai-core
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))

import torch
from core01.transformer import NexusAICore01
from core01.tokenizer_interface import NexusAITokenizer
from nexusai_core_01.config.model_config import (
    NexusAICore01Config, ModelStatus)

CKPT = os.path.join(AI_CORE, "models", "checkpoints_core01_run3",
                    "checkpoint_final.pt")
TOK = os.path.join(AI_CORE, "data", "experimental", "phase9_2",
                   "tokenizers", "bpe_8k", "sp_bpe_8k.model")
OUT_DIR = os.path.join(os.path.dirname(AI_CORE), os.pardir,
                       "eval_reports")

# ---------------- prompt suite: (id, lang, category, prompt) ----------------
PROMPTS = [
    # English
    ("en_qa1",   "en", "qa",  "Question: What is the capital of Bangladesh? Answer:"),
    ("en_math1", "en", "math","Question: What is 12 plus 30? Answer:"),
    ("en_know1", "en", "fact","The sun rises in the"),
    ("en_conv1", "en", "chat","Hello! How are you today?"),
    ("en_inst1", "en", "inst","Write one sentence about trees."),
    # Bangla (Bengali script)
    ("bn_qa1",   "bn", "qa",  "প্রশ্ন: বাংলাদেশের রাজধানী কী? উত্তর:"),
    ("bn_math1", "bn", "math","প্রশ্ন: ১২ আর ৩০ যোগ করলে কত? উত্তর:"),
    ("bn_know1", "bn", "fact","সূর্য পূর্ব দিকে"),
    ("bn_conv1", "bn", "chat","আসসালামু আলাইকুম! আপনি কেমন আছেন?"),
    ("bn_inst1", "bn", "inst","গাছ সম্পর্কে একটি বাক্য লিখুন।"),
    # Banglish / mixed
    ("bg_qa1",   "banglish", "qa",  "Question: Bangladesh er rajdhani ki? Answer:"),
    ("bg_math1", "banglish", "math","Question: 12 add 30 koto? Answer:"),
    ("bg_conv1", "banglish", "chat","Hey, kemon acho?"),
    ("mx_qa1",   "mixed", "qa",     "What is বাংলাদেশের_INCREMENTAL... not used"),
]
PROMPTS = PROMPTS[:13]  # drop malformed last entry

def script_of(t):
    if re.search(r"[ঀ-৿]", t): return "bn"
    if re.search(r"[A-Za-z]", t): return "en"
    return "other"

def repetition_ratio(toks):
    if len(toks) < 4: return 0.0
    return 1.0 - len(set(toks)) / len(toks)

def main():
    t0 = time.time()
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    cd = dict(ck["config"])
    if isinstance(cd.get("model_status"), str):
        cd["model_status"] = ModelStatus[cd["model_status"]]
    cfg = NexusAICore01Config(
        **{k: v for k, v in cd.items()
           if k in NexusAICore01Config.__dataclass_fields__})
    model = NexusAICore01(cfg)
    model.load_state_dict(ck["model_state_dict"], strict=True)
    model.eval()
    tok = NexusAITokenizer(TOK, cfg)
    print(f"loaded ckpt epoch={ck.get('epoch')} step={ck.get('step')} "
          f"params={model.count_parameters():,} in {time.time()-t0:.0f}s")

    results = []
    for pid, lang, cat, prompt in PROMPTS:
        ids = torch.tensor([tok.encode(prompt)], dtype=torch.long)
        t1 = time.time()
        with torch.no_grad():
            out = model.generate(ids, max_new_tokens=48, temperature=0.8,
                                 top_k=50, top_p=0.9, do_sample=True,
                                 repetition_penalty=1.2)
        gen_ids = out[0, ids.shape[1]:].tolist()
        text = tok.decode(gen_ids)
        dt = time.time() - t1
        rep = repetition_ratio(gen_ids)
        results.append({
            "id": pid, "lang": lang, "category": cat, "prompt": prompt,
            "output": text.strip(),
            "output_script": script_of(text),
            "lang_match": script_of(text) == ("bn" if lang == "bn" else "en")
                          if lang in ("bn", "en") else None,
            "new_tokens": len(gen_ids),
            "repetition_ratio": round(rep, 3),
            "latency_s": round(dt, 2),
            "eos_hit": gen_ids and gen_ids[-1] == cfg.eos_id,
        })
        print(f"\n[{pid}] ({lang}/{cat}) {dt:.1f}s rep={rep:.2f}")
        print("  P:", prompt[:70])
        print("  O:", text.strip()[:160])

    # automated aggregate
    n = len(results)
    summary = {
        "benchmark": "neural_only_run3_cpu",
        "checkpoint": CKPT,
        "checkpoint_sha": hashlib.sha256(open(CKPT, 'rb').read()).hexdigest(),
        "params": model.count_parameters(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "n_prompts": n,
        "avg_latency_s": round(sum(r["latency_s"] for r in results) / n, 2),
        "avg_repetition": round(sum(r["repetition_ratio"] for r in results) / n, 3),
        "lang_match_rate": round(
            sum(1 for r in results if r["lang_match"]) /
            max(1, sum(1 for r in results if r["lang_match"] is not None)), 3),
        "eos_rate": round(sum(1 for r in results if r["eos_hit"]) / n, 3),
        "results": results,
        "note": ("Raw model outputs. Quality judged separately — low training "
                 "means weak outputs are EXPECTED, not a bug."),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    outp = os.path.join(OUT_DIR,
                        "neural_benchmark_" +
                        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") +
                        ".json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("\n==== SUMMARY ====")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"},
                     indent=1))
    print("report:", outp)

if __name__ == "__main__":
    main()
