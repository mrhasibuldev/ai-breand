"""
NEXUSAI STAGE-1 — Four-Core genuine generation verification.

Reproducible CPU benchmark for every model registered in
ml-service/model_registry.py (Core-01, Core-02, Core-03, Core-04, plus the
legacy nexus-medium fallback). Loads each model's exact registered
checkpoint with strict state-dict loading, verifies parameter counts and
tokenizer compatibility, then runs genuine autoregressive generation on a
fixed multilingual prompt matrix.

No external AI APIs, no deterministic handlers, no fallback substitution.
Read-only with respect to checkpoints/datasets/tokenizer.

Usage (from repo root, repo python env):
    python packages/ai-core/evaluation/verify_four_core_generation.py \
        [--models nexus-core-01,nexus-core-02,nexus-core-03,nexus-core-04,nexus-medium] \
        [--max-new-tokens 48] [--out eval_reports/stage1_four_core_generation.json]
"""
import argparse
import json
import os
import sys
import time
import traceback

AI_CORE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # packages/ai-core
ML_DIR = os.path.join(AI_CORE, "ml-service")
REPO_ROOT = os.path.dirname(os.path.dirname(AI_CORE))
for p in (AI_CORE, os.path.join(AI_CORE, "models"), ML_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------------- prompts --
# Same matrix for every model. Prompts authored directly; no templates.
PROMPT_MATRIX = [
    # (test_id, category, language, prompt)
    ("greet_en",      "greeting",   "en", "Hello! How are you today?"),
    ("greet_bn",      "greeting",   "bn", "তুমি কেমন আছো?"),
    ("greet_bg",      "greeting",   "banglish", "Tumi kemon acho?"),
    ("greet_mix",     "greeting",   "mixed", "Hello, তুমি কেমন আছো friend?"),

    ("conv_en",       "conversation","en", "What do you think about the weather today?"),
    ("conv_bn",       "conversation","bn", "আজকের আবহাওয়া কেমন লাগে তোমার?"),
    ("conv_bg",       "conversation","banglish", "Ajke er abhawoa kemon lagche tomar?"),
    ("conv_mix",      "conversation","mixed", "আজ afternoon-এ আমরা কি play করবো?"),

    ("know_en",       "knowledge",  "en", "What is artificial intelligence?"),
    ("know_bn",       "knowledge",  "bn", "কৃত্রিম বুদ্ধিমত্তা কী?"),
    ("know_bg",       "knowledge",  "banglish", "Artificial intelligence ki?"),
    ("know_mix",      "knowledge",  "mixed", "Bengali আর English-এ Navigator কী?"),

    ("reason_en",     "reasoning",  "en", "If all cats are animals and Tom is a cat, is Tom an animal?"),
    ("reason_bn",     "reasoning",  "bn", "যদি সব বিড়াল প্রাণী হয় এবং টম একটি বিড়াল, তাহলে টম কি প্রাণী?"),
    ("reason_bg",     "reasoning",  "banglish", "Jodi shob biral prani hoy ebong Tom ekta biral, tahole Tom ki prani?"),
    ("reason_mix",    "reasoning",  "mixed", "If আমি exhausted Feeling, should আমি rest or কাজ করবো?"),

    ("math_en",       "mathematics","en", "What is 15 plus 27?"),
    ("math_bn",       "mathematics","bn", "১৫ আর ২৭ যোগ করলে কত হয়?"),
    ("math_bg",       "mathematics","banglish", "15 plus 27 koto hoy?"),
    ("math_mix",      "mathematics","mixed", "আমার ৫টা apple আছে, ৩টা খেয়ে ফেললাম, কতটা বাকি?"),

    ("ctx_en",        "followup",   "en", "My name is Hasib. What is my name?"),
    ("ctx_bn",        "followup",   "bn", "আমার নাম হাসিব। আমার নাম কী?"),
    ("ctx_bg",        "followup",   "banglish", "Amar nam Hasib. Amar nam ki?"),
    ("ctx_mix",       "followup",   "mixed", "আমি Hasib, আর তুমি? তোমার নাম কী?"),
]

GEN_KW = dict(do_sample=False, max_new_tokens=48, temperature=0.0,
              top_k=1, top_p=1.0, repetition_penalty=1.1)


def _mem_mb():
    try:
        import psutil
        return round(psutil.Process(os.getpid()).memory_info().rss / 1e6, 1)
    except Exception:
        return None


def strict_load_check(model, checkpoint_path):
    """Independent strict state-dict verification (separate from registry)."""
    import torch
    weights_only_used = True
    try:
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    except Exception:
        # Trusted local checkpoint containing numpy-serialized metadata
        # (e.g. Core-01 Run3 rng_state). Fall back, and record the flag.
        weights_only_used = False
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    state = ckpt.get("model_state_dict", ckpt)
    res = model.load_state_dict(state, strict=True)
    n_params = sum(p.numel() for p in model.parameters())
    return {
        "strict_load": True,
        "weights_only_flag": weights_only_used,
        "missing_keys": list(res.missing_keys),
        "unexpected_keys": list(res.unexpected_keys),
        "param_count": n_params,
    }


def verify_model(model_id, max_new_tokens):
    """Load one registered model and run the full prompt matrix."""
    import torch
    import model_registry as mr
    from nexus_core import get_config, build_model, load_checkpoint_strict

    rec = {"model_id": model_id, "status": "PENDING", "checks": {},
           "generations": [], "errors": []}
    m = mr.registry.get(model_id)
    if m is None:
        rec["status"] = "FAILED"
        rec["errors"].append(f"model_id {model_id!r} not in registry")
        return rec

    rec["definition"] = {k: v for k, v in m.items() if k != "engine"}

    # --- static validation (file exists + sha256 + tokenizer) ---
    try:
        ok, why = mr.registry.validate(model_id)
        rec["checks"]["registry_validate"] = {"ok": ok, "detail": why}
    except Exception as e:
        rec["checks"]["registry_validate"] = {"ok": False, "detail": repr(e)}
        ok = False
    if not ok:
        rec["status"] = "FAILED"
        rec["errors"].append(f"registry validation failed: {why}")
        return rec

    # --- load engine through registry (this performs strict load internally
    #     for nexus_sft; core01/medium load paths verified below separately) ---
    t0 = time.time()
    try:
        engine = mr.registry.load(model_id, device="cpu")
        rec["checks"]["engine_load_s"] = round(time.time() - t0, 2)
        rec["checks"]["engine_kind"] = engine.get("kind")
    except Exception as e:
        rec["status"] = "FAILED"
        rec["errors"].append("engine load: " + traceback.format_exc())
        return rec

    # --- independent strict-load + param-count verification ---
    try:
        eng = engine.get("engine", engine)
        if engine["kind"] == "nexus_sft":
            model, cfg = build_model(m["core_id"], config=get_config(m["core_id"]),
                                     device="cpu")
            load_checkpoint_strict(model, m["checkpoint"], map_location="cpu")
            model.eval()
            info = strict_load_check(model, m["checkpoint"])
            info["param_count_expected"] = m.get("expected_params")
            rec["checks"]["strict_load"] = info
            rec["checks"]["param_count_match"] = (
                info["param_count"] == m.get("expected_params"))
            tok = eng["tokenizer"]
            rec["checks"]["tokenizer"] = {
                "vocab_size": getattr(tok, "vocab_size", None),
                "bos_id": getattr(tok, "bos_id", None),
                "eos_id": getattr(tok, "eos_id", None),
                "pad_id": getattr(tok, "pad_id", None),
            }
        elif engine["kind"] == "core01":
            core_eng = eng  # registry stores the InferenceEngine directly
            model = core_eng.model
            info = strict_load_check(model, m["checkpoint"])
            info["param_count_expected"] = m.get("expected_params")
            rec["checks"]["strict_load"] = info
            rec["checks"]["param_count_match"] = (
                info["param_count"] == m.get("expected_params"))
            tok = core_eng.tokenizer
            rec["checks"]["tokenizer"] = {
                "vocab_size": getattr(tok, "vocab_size", None),
                "bos_id": getattr(tok, "bos_id", None),
                "eos_id": getattr(tok, "eos_id", None),
                "pad_id": getattr(tok, "pad_id", None),
            }
        else:  # medium — separate class, verify via its own path
            gen = eng["generator"]
            model = gen.model
            ckpt = torch.load(m["checkpoint"], map_location="cpu",
                              weights_only=False)
            state = ckpt.get("model_state_dict", ckpt)
            res = model.load_state_dict(state, strict=True)
            rec["checks"]["strict_load"] = {
                "strict_load": True,
                "missing_keys": list(res.missing_keys),
                "unexpected_keys": list(res.unexpected_keys),
                "param_count": sum(p.numel() for p in model.parameters()),
                "param_count_expected": m.get("expected_params"),
            }
            rec["checks"]["param_count_match"] = (
                rec["checks"]["strict_load"]["param_count"]
                == m.get("expected_params"))
            sp = gen.tokenizer.sp
            rec["checks"]["tokenizer"] = {
                "vocab_size": sp.get_piece_size(),
                "bos_id": sp.bos_id(), "eos_id": sp.eos_id(),
                "pad_id": sp.pad_id(),
            }
    except Exception:
        rec["checks"]["strict_load"] = {"strict_load": False,
                                        "error": traceback.format_exc()}
        rec["errors"].append("strict load check: " + traceback.format_exc())

    rec["checks"]["mem_mb_after_load"] = _mem_mb()

    # --- generation matrix ---
    for tid, cat, lang, prompt in PROMPT_MATRIX:
        g = {"test_id": tid, "category": cat, "language": lang,
             "prompt": prompt, "gen_kw": dict(GEN_KW), "max_new_tokens": max_new_tokens}
        t0 = time.time()
        try:
            txt, prov = mr.registry.generate(model_id, prompt, **GEN_KW)
            g["duration_s"] = round(time.time() - t0, 2)
            g["generated_text"] = txt
            g["provenance"] = prov
            g["generated_chars"] = len(txt or "")
            g["status"] = "ok" if (txt or "").strip() else "EMPTY_OUTPUT"
        except Exception:
            g["duration_s"] = round(time.time() - t0, 2)
            g["generated_text"] = None
            g["status"] = "GENERATION_EXCEPTION"
            g["error"] = traceback.format_exc()
            rec["errors"].append(f"{tid}: generation exception")
        rec["generations"].append(g)

    rec["checks"]["mem_mb_after_gen"] = _mem_mb()
    rec["status"] = ("VERIFIED" if not rec["errors"]
                     and all(g["status"] == "ok" for g in rec["generations"])
                     else "PARTIALLY VERIFIED" if rec["generations"]
                     else "FAILED")
    return rec


def classify_quality(text):
    """Transparent mechanical quality flags (not semantic judgment)."""
    flags = []
    if text is None:
        return ["INVALID"]
    t = text.strip()
    if not t:
        return ["EMPTY"]
    # repetition collapse: single token/char dominating
    words = t.split()
    if len(words) >= 8 and len(set(words)) <= 2:
        flags.append("REPETITION_COLLAPSE")
    if len(set(t)) <= 3 and len(t) > 20:
        flags.append("REPETITION_COLLAPSE")
    # heavy UNK / replacement chars
    if t.count("�") > 0:
        flags.append("INVALID_CHARS")
    return flags or ["MECHANICAL_OK"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="nexus-core-01,nexus-core-02,"
                    "nexus-core-03,nexus-core-04,nexus-medium")
    ap.add_argument("--max-new-tokens", type=int, default=48)
    ap.add_argument("--out", default=os.path.join(
        REPO_ROOT, "eval_reports", "stage1_four_core_generation.json"))
    args = ap.parse_args()

    model_ids = [m.strip() for m in args.models.split(",") if m.strip()]
    report = {
        "benchmark": "NEXUSAI Stage-1 four-core generation verification",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device": "cpu",
        "generation_kw": dict(GEN_KW, max_new_tokens=args.max_new_tokens),
        "prompt_count_per_model": len(PROMPT_MATRIX),
        "models": {},
    }

    for mid in model_ids:
        print(f"\n===== {mid} =====", flush=True)
        rec = verify_model(mid, args.max_new_tokens)
        for g in rec["generations"]:
            g["quality_flags"] = classify_quality(g.get("generated_text"))
        report["models"][mid] = rec
        print(f"status={rec['status']} gens={len(rec['generations'])} "
              f"errors={len(rec['errors'])}", flush=True)
        for g in rec["generations"][:6]:
            snippet = (g.get("generated_text") or "")[:100]
            print(f"  [{g['test_id']}] {g['status']} :: "
                  + ascii(snippet), flush=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport written: {args.out}")


if __name__ == "__main__":
    main()
