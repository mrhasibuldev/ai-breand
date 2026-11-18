"""
Generic NexusAI held-out evaluator for Core-02/03/04 (and Core-01).

Loads a trained checkpoint, generates answers for test.jsonl records using
the SFT chat format, and reports per-category metrics:
  - exact_match: normalized generated text == normalized reference
  - contains:    all reference answer keywords present in generation
  - empty_rate:  fraction of empty generations
  - per-language and per-category breakdowns

Usage:
    python eval_core.py --core core03 --ckpt models/checkpoints_core03_sft_v1/checkpoint_final.pt \
        --data-dir data/core03_math --out eval_reports/core03_eval.json --max-samples 0
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

AI_CORE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))

import torch

from nexus_core import (build_model, get_config, load_checkpoint_strict,
                        chat_generate, status_of)
from core01.tokenizer_interface import create_default_tokenizer


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def keywords(answer):
    """Extract checkable tokens: numbers + words len>=4."""
    toks = re.findall(r"\d+\.?\d*|[a-zA-Z\u0980-\u09FF]{4,}", answer)
    return [t.lower() for t in toks]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--core", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--max-samples", type=int, default=0, help="0 = all")
    ap.add_argument("--max-new-tokens", type=int, default=80)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    device = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
    config = get_config(args.core)
    model, config = build_model(args.core, config=config, device=device)
    res = load_checkpoint_strict(model, args.ckpt, map_location=device)
    print(f"[eval] strict load ok missing={len(res.missing_keys)} "
          f"unexpected={len(res.unexpected_keys)}")

    tokenizer = create_default_tokenizer(config)

    test_path = os.path.join(args.data_dir, "test.jsonl")
    records = [json.loads(l) for l in open(test_path, encoding="utf-8") if l.strip()]
    if args.max_samples:
        records = records[:args.max_samples]

    per_cat = defaultdict(lambda: {"n": 0, "exact": 0, "contains": 0,
                                   "empty": 0, "ref": [], "gen": []})
    t0 = __import__("time").time()
    for i, r in enumerate(records):
        msgs = r["messages"]
        user = next(m["content"] for m in msgs if m["role"] == "user")
        ref = next(m["content"] for m in msgs if m["role"] == "assistant")
        cat = r.get("category", "unknown")
        lang = r.get("lang", "unknown")
        key = f"{cat}|{lang}"
        try:
            gen = chat_generate(model, tokenizer, user,
                                max_new_tokens=args.max_new_tokens,
                                device=device)
        except Exception as e:
            gen = f"__ERROR__ {e}"
        d = per_cat[key]
        d["n"] += 1
        d["empty"] += int(not gen.strip())
        d["exact"] += int(norm(gen) == norm(ref))
        kws = keywords(ref)
        d["contains"] += int(kws and all(k in norm(gen) for k in kws))
        if len(d["gen"]) < 3:
            d["ref"].append(ref[:200])
            d["gen"].append(gen[:200])
        if (i + 1) % 10 == 0:
            print(f"[eval] {i+1}/{len(records)} elapsed={__import__('time').time()-t0:.0f}s", flush=True)

    report = {
        "core": args.core, "ckpt": args.ckpt,
        "model_status": status_of(config),
        "device": device, "n_records": len(records),
        "categories": {},
    }
    total_n = total_exact = total_contains = total_empty = 0
    for k, d in sorted(per_cat.items()):
        report["categories"][k] = {
            "n": d["n"],
            "exact_match": round(d["exact"] / d["n"], 4),
            "contains": round(d["contains"] / d["n"], 4),
            "empty_rate": round(d["empty"] / d["n"], 4),
            "samples": [{"ref": r, "gen": g} for r, g in zip(d["ref"], d["gen"])],
        }
        total_n += d["n"]; total_exact += d["exact"]
        total_contains += d["contains"]; total_empty += d["empty"]
    report["overall"] = {
        "n": total_n,
        "exact_match": round(total_exact / max(total_n, 1), 4),
        "contains": round(total_contains / max(total_n, 1), 4),
        "empty_rate": round(total_empty / max(total_n, 1), 4),
    }
    print(json.dumps(report["overall"], indent=1))
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        json.dump(report, open(args.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"[eval] report -> {args.out}")


if __name__ == "__main__":
    main()
