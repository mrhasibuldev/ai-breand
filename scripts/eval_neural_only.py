# Gate B — neural-only evaluation suite for NexusAI Core-01
# Hits /orchestrate with neural_only:true (bypasses all deterministic handlers).
# Run: python scripts/eval_neural_only.py   (ml-service must be running on :8000)
import json, urllib.request, time, os, sys

URL = "http://127.0.0.1:8000/orchestrate"
OUT = "eval_reports/nexusai_neural_only_evaluation.json"

def call(message, history=None):
    body = {"message": message, "neural_only": True, "diagnostic_mode": True}
    if history is not None:
        body["history"] = history  # API-side key — tests the compat fix end-to-end
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    r = json.loads(urllib.request.urlopen(req, timeout=300).read())
    return {"input": message, "history": history or [],
            "response": r.get("response"), "latency_ms": r.get("latency_ms"),
            "intent": r.get("intent"), "response_source": r.get("response_source"),
            "language": r.get("language"), "diagnostics": r.get("diagnostics"),
            "wall_s": round(time.time()-t0, 1)}

TESTS = [
    # A. English
    ("en_hello", "Hello."), ("en_who", "Who are you?"),
    ("en_creator", "Who created you?"),
    ("en_ai", "What is artificial intelligence?"),
    ("en_sky", "Why does the sky appear blue?"),
    ("en_computer", "Explain how a computer works."),
    ("en_ml", "What is machine learning?"),
    # B. Bengali
    ("bn_who", "তুমি কে?"), ("bn_creator", "তোমাকে কে তৈরি করেছে?"),
    ("bn_ai", "কৃত্রিম বুদ্ধিমত্তা কী?"), ("bn_sky", "আকাশ নীল দেখায় কেন?"),
    ("bn_computer", "কম্পিউটার কীভাবে কাজ করে?"),
    # C. Banglish
    ("bl_who", "Tumi ke?"), ("bl_creator", "Tomake ke create korse?"),
    ("bl_ai", "AI kivabe kaj kore?"), ("bl_computer", "Computer kivabe kaj kore?"),
    # D. Context (multi-turn)
    ("ctx_turn1", "My favorite subject is physics."),
    ("ctx_turn2", "Why do you think I like it?",
     [{"role":"user","content":"My favorite subject is physics."},
      {"role":"assistant","content":"Physics is a fascinating subject!"}]),
    ("ctx_followup", "Tell me more about it.",
     [{"role":"user","content":"My favorite subject is physics."},
      {"role":"assistant","content":"Physics is a fascinating subject!"}]),
    # E. Generalization (unseen phrasing)
    ("gen_unseen", "Zorblax quantum flux capacitors sell for how much?"),
    # F. Reasoning
    ("rs_math", "What is 17 plus 25?"),
    ("rs_logic", "If all cats are animals and Tom is a cat, is Tom an animal?"),
]

results = []
for t in TESTS:
    tid, msg = t[0], t[1]
    hist = t[2] if len(t) > 2 else None
    try:
        r = call(msg, hist)
    except Exception as e:
        r = {"input": msg, "error": str(e)}
    r["test_id"] = tid
    results.append(r)
    prov = ((r.get("diagnostics") or [{}])[0].get("provenance") or {})
    print(f"{tid:14} src={r.get('response_source','ERR'):16} "
          f"model={prov.get('model_id','?'):14} "
          f"out={(r.get('response') or r.get('error') or '')[:80]!r}")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nwrote {OUT} ({len(results)} tests)")
