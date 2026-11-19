"""Phase 1 chat-stabilization regression tests.

Covers: Bengali numeral math routing/tool, safety_guard malformed-output
detection, and neural_generation_executed provenance for SFT specialists.
"""
import os
import sys

AI_CORE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ML = os.path.join(AI_CORE, "ml-service")
for p in (ML, AI_CORE, os.path.join(AI_CORE, "models")):
    if p not in sys.path:
        sys.path.insert(0, p)

from model_router import classify_intent_v2, try_math_tool, detect_language_v2
from safety_guard import check_output

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f" :: {detail}" if detail else ""))


# ---------- Bengali numeral recognition + math intent ----------
def test_bn_digit_math_intent():
    p1 = "১৫টি আম ৩ জনের মধ্যে সমান ভাগ করলে প্রত্যেকে কয়টি আম পাবে?"
    p2 = "একজন দোকানদারের কাছে ১০টি কলা ছিল। সে ৩টি বিক্রি করল এবং ২টি বন্ধুকে দিল।"
    check("bn-digit-share->MATH", classify_intent_v2(p1, "bengali") == "MATH",
          classify_intent_v2(p1, "bengali"))
    check("bn-digit-give->MATH", classify_intent_v2(p2, "bengali") == "MATH",
          classify_intent_v2(p2, "bengali"))
    # non-math Bengali must NOT be hijacked
    check("bn-chat-not-math", classify_intent_v2("আজ আবহাওয়া কেমন?", "bengali") == "CHAT")
    check("bn-word-no-digit-not-math",
          classify_intent_v2("ভাগ করা কলোনির কাজ", "bengali") != "MATH")


def test_bn_math_tool():
    ans, used = try_math_tool("১৫টি আম ৩ জনের মধ্যে সমান ভাগ করলে প্রত্যেকে কয়টি আম পাবে?")
    check("bn-share-tool", used and "5" in ans, f"{ans!r} used={used}")
    ans, used = try_math_tool("১০টি কলা ছিল। সে ৩টি বিক্রি করল এবং ২টি বন্ধুকে দিল। এখন কয়টি কলা?")
    check("bn-give-tool", used and "5" in ans, f"{ans!r} used={used}")
    ans, used = try_math_tool("What is 15 + 27?")
    check("ascii-plus-still-works", used and ans == "42", f"{ans!r}")
    ans, used = try_math_tool("১২ ÷ ৪ = ?")
    check("bn-digit-div", used and ans == "3", f"{ans!r}")


# ---------- safety_guard malformed/cross-language detection ----------
def test_output_guard():
    leak = "The first person is a total of 10 + 3 = <<10+10=15>>15 students. #### 20"
    r = check_output(leak, source="neural", expected_lang="bengali")
    check("markup-leak-rejected", not r["ok"] and r["reason"] == "calc_markup_leak", r["reason"])
    gib = "Bydamer is a bomburn in a tarmer cubble, and the evertensation. " * 2
    r = check_output(gib, source="neural", expected_lang="bengali")
    check("bn-input-en-gibberish-rejected",
          not r["ok"] and r["reason"] == "language_mismatch", r["reason"])
    good_bn = "দুঃখিত, আমি এই প্রশ্নের সঠিক উত্তর দিতে পারছি না। অন্যভাবে চেষ্টা করুন।"
    r = check_output(good_bn, source="neural", expected_lang="bengali")
    check("valid-bengali-passes", r["ok"], r["reason"])
    good_en = "The capital of France is Paris. It has been the capital for centuries."
    r = check_output(good_en, source="neural", expected_lang="english")
    check("valid-english-passes", r["ok"], r["reason"])
    # deterministic/fallback sources are not strict-checked
    r = check_output(leak, source="deterministic", expected_lang="bengali")
    check("deterministic-source-not-strict", r["ok"], r["reason"])
    # short legit answers not killed by language rule (len>=2 passes too_short)
    r = check_output("5টি", source="neural", expected_lang="bengali")
    check("short-answer-passes", r["ok"], r["reason"])


# ---------- neural_generation_executed provenance ----------
def test_registry_provenance_flag():
    import model_registry as mr
    # medium is already neural-flagged; verify nexus_sft kind now counts too
    reg = mr.registry
    eng = reg.load("nexus-medium")
    kind = eng["kind"]
    expected = kind in ("core01", "medium", "nexus_sft")
    # emulate the provenance expression used in generate()
    flag = kind in ("core01", "medium", "nexus_sft")
    check("medium-flag-true", flag is True and expected, f"kind={kind}")
    # nexus_sft kind must be included — inspect registry source contract
    import inspect
    src = inspect.getsource(type(reg).generate)
    check("nexus_sft-in-provenance-expr", '"nexus_sft"' in src,
          "generate() provenance must count nexus_sft as neural")


# ---------- Phase F: required Bengali/English routing prompts ----------
def test_required_routing_prompts():
    cases = [
        ("১৫টি আম ৩ জনের মধ্যে সমান ভাগ করলে প্রত্যেকে কয়টি আম পাবে?", "MATH"),
        ("১০ থেকে ৩ বিয়োগ করলে কত থাকে?", "MATH"),
        ("১২ × ৮ কত?", "MATH"),
        ("What is 15 divided by 3?", "MATH"),
        ("১০ + ২০ কত?", "MATH"),
        # number present but NOT math — must not be hijacked
        ("আমার বয়স ২৫ বছর। আমি কি একটি সাধারণ প্রশ্ন করতে পারি?", "NOT_MATH"),
    ]
    for p, want in cases:
        intent = classify_intent_v2(p, detect_language_v2(p)["lang"])
        if want == "MATH":
            check(f"route-MATH::{p[:30]}", intent == "MATH", intent)
        else:
            check(f"route-notmath::{p[:30]}", intent != "MATH", intent)
    # tool answers for the arithmetic ones
    for p, frag in [("১০ থেকে ৩ বিয়োগ করলে কত থাকে?", "7"),
                    ("১২ × ৮ কত?", "96"),
                    ("What is 15 divided by 3?", "5"),
                    ("১০ + ২০ কত?", "30")]:
        ans, used = try_math_tool(p)
        check(f"tool::{p[:30]}", used and frag in ans, f"{ans!r}")


# ---------- Phase E: extended output-guard coverage ----------
def test_output_guard_extended():
    valid = {
        "banglish": "Vai, ei jaygay tumi ekhon ki korte paro? Bolle ami help korbo.",
        "mixed_tech": "NexusAI একটি Transformer model ব্যবহার করে, which runs locally on CPU.",
        "math_expr": "The answer is 15 ÷ 3 = 5 and 12 × 8 = 96.",
        "code": "def add(a, b):\n    return a + b  # simple addition",
        "short_bn": "হ্যাঁ, পারি।",
        "proper_noun": "Hasibul Hasin is the founder of NexusAI.",
    }
    for name, txt in valid.items():
        r = check_output(txt, source="neural", expected_lang="bengali")
        check(f"guard-accept::{name}", r["ok"], r["reason"])
    bad = {
        "banana_corrupt": "<<1/5=30>>30 hunches. There were 5+3+4=<<10-5=15>>15 mience.",
        "empty": "   ",
        "repeat": "the the the the the the the the the the the the the the",
        "unclosed": "result = <<3*4=12 and more text without closing",
        "truncated_markup": "Answer: #### 4",
    }
    for name, txt in bad.items():
        r = check_output(txt, source="neural", expected_lang="bengali")
        check(f"guard-reject::{name}", not r["ok"], f"reason={r['reason']}")


# ---------- Phase D: registry provenance semantics ----------
def test_registry_provenance_semantics():
    """Real generation on a specialist must report neural_generation_executed."""
    import model_registry as mr
    txt, prov = mr.registry.generate("nexus-core-03", "What is 2 + 2?",
                                     max_new_tokens=8, temperature=0.0)
    check("core03-prov-flag", prov.get("neural_generation_executed") is True,
          str(prov.get("neural_generation_executed")))
    check("core03-prov-model", prov.get("model_id") == "nexus-core-03")
    check("core03-prov-sha", bool(prov.get("checkpoint_sha256")))
    # deterministic path: brain trace must show neural_ran False
    from model_router import brain
    r = brain.respond("তোমার নাম কী?", None, neural_only=False)
    tr = r.get("trace", {})
    check("det-route-no-neural", tr.get("neural_ran") is False and
          str(tr.get("route", "")).startswith(("deterministic", "registry", "tool")),
          str(tr.get("route")))
    # fallback path records fallback=True
    r2 = brain.respond("একটি ঘরে ৫টি মোমবাতি জ্বলছিল। বাতাসে ২টি নিভে গেল।", None, neural_only=False)
    tr2 = r2.get("trace", {})
    check("fallback-flag-present", "fallback" in tr2, str(tr2.get("route")))


# ---------- Phase C: guest history extraction (logic mirror) ----------
def test_guest_history_logic():
    """Mirror of intelligence-engine extractHistoryFromContext contract:
    history lives under context[0].history as [{role,content},...]."""
    ctx = [{"message": "m", "conversation_id": "g",
            "history": [{"role": "user", "content": "first"},
                        {"role": "assistant", "content": "reply"}]}]
    out = []
    for item in ctx:
        if isinstance(item, dict) and "history" in item:
            for msg in item["history"]:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    out.append({"role": msg["role"], "content": msg["content"]})
    check("guest-history-extracted", len(out) == 2 and out[0]["role"] == "user"
          and out[1]["content"] == "reply", str(out))
    # malformed entries skipped safely
    ctx_bad = [{"history": [{"role": "user"}, "junk", {"content": "x"},
                            {"role": "assistant", "content": "ok"}]}]
    out2 = []
    for item in ctx_bad:
        for msg in item["history"]:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                out2.append(msg)
    check("guest-history-malformed-safe", len(out2) == 1, str(out2))


if __name__ == "__main__":
    test_bn_digit_math_intent()
    test_bn_math_tool()
    test_output_guard()
    test_registry_provenance_flag()
    test_required_routing_prompts()
    test_output_guard_extended()
    test_registry_provenance_semantics()
    test_guest_history_logic()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("FAILED:", FAIL)
        sys.exit(1)
