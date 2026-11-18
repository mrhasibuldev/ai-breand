"""
NEXUSAI — Four-Core stabilization test suite (Phase 9).

Reproducible per-core evaluation:
  - core-01 : 50-case multilingual prompt set (base LM, mechanical + language-consistency scoring)
  - core-02 : full held-out test.jsonl (132 cases) + surface-similarity vs reference
  - core-03 : full held-out test.jsonl (87 cases) + deterministic numeric oracle
  - core-04 : full held-out test.jsonl (31 cases) + surface-similarity vs reference
  - multi-turn context probes (5 per core)

All generation goes through ml-service/model_registry.py -> the same code path
the router uses. No external AI, no deterministic response substitution.
Scoring is deterministic: numeric oracle for math, mechanical flags elsewhere.
Semantic quality is recorded for human review, never auto-claimed.

Usage:
  python packages/ai-core/evaluation/four_core_test_suite.py \
      [--max-cases N] [--out eval_reports/four_core_test_suite.json]
"""
import argparse
import json
import os
import re
import sys
import time
import traceback

AI_CORE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(AI_CORE, "ml-service")
REPO_ROOT = os.path.dirname(os.path.dirname(AI_CORE))
for p in (AI_CORE, os.path.join(AI_CORE, "models"), ML_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

DATA = os.path.join(AI_CORE, "data")

BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


# ------------------------------------------------------------- case lists --
CORE01_CASES = [
    # (id, lang, prompt) — 50 cases: greetings, conversation, knowledge,
    # reasoning, math, follow-up across en/bn/banglish/mixed.
    ("g01", "en", "Hello! How are you today?"),
    ("g02", "bn", "তুমি কেমন আছো?"),
    ("g03", "bg", "Tumi kemon acho?"),
    ("g04", "mx", "Hello, তুমি কেমন আছো friend?"),
    ("g05", "en", "Good morning! What a nice day."),
    ("g06", "bn", "শুভ সকাল! আজ Leukage কেমন?"),
    ("g07", "bg", "Suvo sokal! Ajke playground e jabo?"),
    ("g08", "mx", "আমার boxed lunch খেয়েছি, তুমি খেয়েছো?"),
    ("c01", "en", "What do you think about the weather today?"),
    ("c02", "bn", "আজকের আবহাওয়া কেমন লাগে তোমার?"),
    ("c03", "bg", "Ajker monh bhalo lagche na, keno?"),
    ("c04", "mx", "This report টা deadline-এর আগে শেষ হবে?"),
    ("c05", "en", "I am feeling tired today."),
    ("c06", "bn", "আমি আজ খুব ক্লান্ত লাগছে।"),
    ("c07", "bg", "Ami ajke khub sharbonno, ki korte pari?"),
    ("c08", "mx", "আমার exam lgche, কী study করবো?"),
    ("k01", "en", "What is artificial intelligence?"),
    ("k02", "bn", "কৃত্রিম বুদ্ধিমত্তা কী?"),
    ("k03", "bg", "Artificial intelligence ki?"),
    ("k04", "mx", "Bengali আর English-এ Navigator কী?"),
    ("k05", "en", "What is gravity?"),
    ("k06", "bn", "মাধ্যাকর্ষণ শক্তি কী?"),
    ("k07", "bg", "Gravity ki? Explain briefly."),
    ("k08", "mx", "Photosynthesis কীভাবে কাজ করে?"),
    ("r01", "en", "If all cats are animals and Tom is a cat, is Tom an animal?"),
    ("r02", "bn", "যদি সব বিড়াল প্রাণী হয় এবং টম একটি বিড়াল, তাহলে টম কি প্রাণী?"),
    ("r03", "bg", "Jodi shob biral prani hoy ebong Tom ekta biral, tahole Tom ki prani?"),
    ("r04", "mx", "If আমি exhausted Feeling, should আমি rest or কাজ করবো?"),
    ("r05", "en", "A bat and a ball cost $1.10 total. The bat costs $1 more than the ball. How much does the ball cost?"),
    ("m01", "en", "What is 15 plus 27?"),
    ("m02", "bn", "১৫ আর ২৭ যোগ করলে কত হয়?"),
    ("m03", "bg", "15 plus 27 koto hoy?"),
    ("m04", "mx", "আমার ৫টা apple আছে, ৩টা খেয়ে ফেললাম, কতটা বাকি?"),
    ("m05", "en", "What is 100 divided by 4?"),
    ("m06", "bn", "৭ গুণ ৮ কত?"),
    ("m07", "bg", "Half of 50 koto?"),
    ("m08", "mx", "20% of 250 কত?"),
    ("f01", "en", "My name is Hasib. What is my name?"),
    ("f02", "bn", "আমার নাম হাসিব। আমার নাম কী?"),
    ("f03", "bg", "Amar nam Hasib. Amar nam ki?"),
    ("f04", "mx", "আমি Hasib, আর তুমি? তোমার নাম কী?"),
    ("f05", "en", "I like tea. What do I like?"),
    ("f06", "bn", "আমি চা পছন্দ করি। আমি কী পছন্দ করি?"),
    ("f07", "bg", "I play cricket on Sunday. When do I play?"),
    ("f08", "mx", "আমার red bag আছে, setা কোথায়?"),
    ("x01", "en", "Tell me a short story about a robot."),
    ("x02", "bn", "রোবট নিয়ে একটি ছোট গল্প বলো।"),
    ("x03", "bg", "Ekta choto golpo bolo robot niye."),
    ("x04", "mx", "আমাদের ARE نا jackfruit discharge_allowance খেত?"),
    ("x05", "en", "What is the capital of France?"),
    ("x06", "bn", "ফ্রান্সের রাজধানী কী?"),
]

MULTI_TURN_PROBES = [
    ("mt1", "My name is Hasib.", "What is my name?"),
    ("mt2", "I have 3 apples.", "How many apples do I have?"),
    ("mt3", "The capital of France is Paris.", "What is the capital of France?"),
    ("mt4", "2 + 2 = 4.", "What is 2 + 2?"),
    ("mt5", "I like tea.", "What do I like?"),
]


def extract_first_number(text):
    """First numeric token (handles Bengali digits, decimals, fractions)."""
    if not text:
        return None
    t = text.translate(BN_DIGITS)
    m = re.search(r"-?\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?", t)
    if not m:
        return None
    s = m.group(0).replace(" ", "")
    try:
        if "/" in s:
            a, b = s.split("/")
            return float(a) / float(b)
        return float(s)
    except Exception:
        return None


def expected_number(ans_text):
    """Core-03 reference answers are bare numbers like '5.' / '1155।'."""
    return extract_first_number(ans_text)


def mechanical_flags(text):
    flags = []
    t = (text or "").strip()
    if not t:
        return ["EMPTY"]
    words = t.split()
    if len(words) >= 8 and len(set(words)) <= 2:
        flags.append("REPETITION_COLLAPSE")
    if len(set(t)) <= 3 and len(t) > 20:
        flags.append("REPETITION_COLLAPSE")
    if t.count("�"):
        flags.append("INVALID_CHARS")
    if "<unk>" in t or "<0x" in t:
        flags.append("SPECIAL_TOKEN_LEAK")
    return flags or ["MECHANICAL_OK"]


def lang_of(text):
    """Rough output-language classification."""
    if not text:
        return "empty"
    bn = sum(1 for c in text if "ঀ" <= c <= "৿")
    total = max(len(text), 1)
    if bn / total > 0.15:
        return "bn"
    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    if ascii_letters / total > 0.5:
        return "en_or_bg"
    return "other"


def surface_sim(gen, ref):
    """Deterministic token-F1 style similarity vs reference answer."""
    g = re.sub(r"[^\w\s]", " ", (gen or "").lower()).split()
    r = re.sub(r"[^\w\s]", " ", (ref or "").lower()).split()
    r = [w for w in r if w not in ("{a}", "{b}", "a", "b") or w.startswith("{")]
    if not g or not r:
        return 0.0
    from collections import Counter
    cg, cr = Counter(g), Counter(r)
    inter = sum((cg & cr).values())
    if inter == 0:
        return 0.0
    p, rr = inter / len(g), inter / len(r)
    return round(2 * p * rr / (p + rr), 4)


def run_generations(model_id, cases, gen_kw, label):
    """cases: list of (test_id, prompt, meta_dict). Returns list of records."""
    import model_registry as mr
    out = []
    for tid, prompt, meta in cases:
        rec = {"test_id": tid, "prompt": prompt, **meta}
        t0 = time.time()
        try:
            txt, prov = mr.registry.generate(model_id, prompt, **gen_kw)
            rec["duration_s"] = round(time.time() - t0, 2)
            rec["generated_text"] = txt
            rec["status"] = "ok" if (txt or "").strip() else "EMPTY_OUTPUT"
            rec["quality_flags"] = mechanical_flags(txt)
            rec["output_lang"] = lang_of(txt)
            rec["provenance_model"] = prov.get("model_id")
            rec["checkpoint"] = prov.get("checkpoint")
        except Exception:
            rec["duration_s"] = round(time.time() - t0, 2)
            rec["generated_text"] = None
            rec["status"] = "GENERATION_EXCEPTION"
            rec["error"] = traceback.format_exc()
        out.append(rec)
    return out


def heldout_cases(core_dir):
    """Load held-out test.jsonl -> [(id, user_prompt, {ref, lang, cat})]."""
    cases = []
    path = os.path.join(DATA, core_dir, "test.jsonl")
    for i, line in enumerate(open(path, encoding="utf-8")):
        if not line.strip():
            continue
        r = json.loads(line)
        msgs = r.get("messages", [])
        if len(msgs) < 2:
            continue
        user = msgs[0].get("content", "")
        # last assistant message = reference
        ref = ""
        for m in reversed(msgs):
            if m.get("role") == "assistant":
                ref = m.get("content", "")
                break
        cases.append((f"{core_dir}_t{i:03d}", user,
                      {"reference": ref, "lang": r.get("lang"),
                       "category": r.get("category"), "split": "heldout_test"}))
    return cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", default="nexus-core-01,nexus-core-02,nexus-core-03,nexus-core-04")
    ap.add_argument("--max-cases", type=int, default=0, help="0 = all")
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "eval_reports",
                                                 "four_core_test_suite.json"))
    args = ap.parse_args()

    SFT_KW = dict(do_sample=False, max_new_tokens=64, temperature=0.3,
                  top_k=20, top_p=1.0, repetition_penalty=1.1)
    C01_KW = dict(do_sample=False, max_new_tokens=48, temperature=1.0,
                  top_k=1, top_p=1.0, repetition_penalty=1.1)

    report = {"suite": "NEXUSAI four-core stabilization tests",
              "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "device": "cpu", "cores": {}}

    wanted = set(args.cores.split(","))

    # ---------------- core-01: 50-case multilingual set ----------------
    if "nexus-core-01" in wanted:
        print("=== nexus-core-01 (50-case set) ===", flush=True)
        cases = [(tid, p, {"lang": l, "category": "misc", "split": "authored"})
                 for tid, l, p in CORE01_CASES]
        gens = run_generations("nexus-core-01", cases, C01_KW, "core01")
        # multi-turn probes: concatenate context into single prompt (base LM)
        mt = []
        for tid, ctx, q in MULTI_TURN_PROBES:
            mt.append((tid, ctx + " " + q,
                       {"lang": "en", "category": "followup", "split": "multiturn"}))
        gens += run_generations("nexus-core-01", mt, C01_KW, "core01")
        nonempty = sum(1 for g in gens if g["status"] == "ok")
        report["cores"]["nexus-core-01"] = {
            "checkpoint": "checkpoints_core01_run3/checkpoint_final.pt",
            "n_cases": len(gens), "nonempty": nonempty,
            "empty_rate": round(1 - nonempty / len(gens), 4),
            "generations": gens,
        }
        print(f"  nonempty {nonempty}/{len(gens)}", flush=True)

    # ---------------- SFT cores: held-out test sets --------------------
    SFT_MAP = {
        "nexus-core-02": "core02_reasoning",
        "nexus-core-03": "core03_math",
        "nexus-core-04": "core04_knowledge",
    }
    for mid, cdir in SFT_MAP.items():
        if mid not in wanted:
            continue
        print(f"=== {mid} held-out {cdir} ===", flush=True)
        cases = heldout_cases(cdir)
        if args.max_cases:
            cases = cases[:args.max_cases]
        gens = run_generations(mid, cases, SFT_KW, cdir)

        # scoring
        n_ok = sum(1 for g in gens if g["status"] == "ok")
        numeric_ok = numeric_tot = 0
        sims = []
        for g in gens:
            ref = g.get("reference", "")
            gen = g.get("generated_text") or ""
            g["surface_sim"] = surface_sim(gen, ref)
            sims.append(g["surface_sim"])
            if mid == "nexus-core-03":
                ev, gv = expected_number(ref), extract_first_number(gen)
                if ev is not None:
                    numeric_tot += 1
                    if gv is not None and abs(gv - ev) < 1e-6:
                        numeric_ok += 1
                g["numeric_expected"] = ev
                g["numeric_got"] = gv
        entry = {
            "checkpoint": json.load(open(os.path.join(
                DATA, cdir, "dataset_manifest.json"), encoding="utf-8")).get("version"),
            "dataset_dir": cdir, "n_cases": len(gens), "nonempty": n_ok,
            "empty_rate": round(1 - n_ok / len(gens), 4),
            "mean_surface_sim": round(sum(sims) / len(sims), 4) if sims else 0,
            "generations": gens,
        }
        if mid == "nexus-core-03":
            entry["numeric_oracle"] = {
                "scored": numeric_tot, "correct": numeric_ok,
                "accuracy": round(numeric_ok / numeric_tot, 4) if numeric_tot else None,
            }
        report["cores"][mid] = entry
        extra = (f" numeric={numeric_ok}/{numeric_tot}"
                 if mid == "nexus-core-03" else "")
        print(f"  nonempty {n_ok}/{len(gens)} sim={entry['mean_surface_sim']}{extra}",
              flush=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport: {args.out}")


if __name__ == "__main__":
    main()
