# Gate B — history contract unit tests for ml-service._normalize_history
# Run: python test_history_contract.py   (from ml-service dir)
import sys, os, json, logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
logging.disable(logging.CRITICAL)

import main  # noqa: E402  (module import is safe; uvicorn only under __main__)
N = main._normalize_history

results = []
def t(name, body, msg, expect_len=None, expect_first=None, expect_last=None):
    try:
        out = N(body, msg)
        ok = True
        note = ""
        if expect_len is not None and len(out) != expect_len:
            ok = False; note = f"len {len(out)}!={expect_len}"
        if expect_first is not None and out and out[0]["content"] != expect_first:
            ok = False; note = f"first={out[0]['content']!r}"
        if expect_last is not None and out and out[-1]["content"] != expect_last:
            ok = False; note = f"last={out[-1]['content']!r}"
        results.append((name, "PASS" if ok else "FAIL", note or json.dumps(out, ensure_ascii=False)[:120]))
    except Exception as e:
        results.append((name, "FAIL", f"EXC {e}"))

H2 = [{"role":"user","content":"My favorite subject is physics."},
      {"role":"assistant","content":"Physics is fascinating!"}]

t("history_only", {"history":H2}, "Why do I like it?", expect_len=2)
t("conv_history_only", {"conversation_history":H2}, "q", expect_len=2)
t("both_identical", {"history":H2,"conversation_history":H2}, "q", expect_len=2)
t("conflict_conv_wins", {"history":[{"role":"user","content":"WRONG"}],
                          "conversation_history":H2}, "q",
  expect_len=2, expect_first="My favorite subject is physics.")
t("empty", {"history":[],"conversation_history":[]}, "q", expect_len=0)
t("missing", {}, "q", expect_len=0)
t("null", {"history":None,"conversation_history":None}, "q", expect_len=0)
t("malformed", {"history":[42,{"role":"user"},{"content":"ok msg"},"plain string"]}, "q",
  expect_len=2, expect_last="plain string")
t("order_preserved", {"history":[{"role":"user","content":"first"},{"role":"assistant","content":"second"},{"role":"user","content":"third"}]},
  "q", expect_len=3, expect_first="first", expect_last="third")
t("current_msg_dedup", {"history":H2+[{"role":"user","content":"same msg"}]}, "same msg",
  expect_len=2)
t("long_truncation", {"history":[{"role":"user","content":f"m{i}"} for i in range(30)]}, "q", expect_len=12,
  expect_first="m18", expect_last="m29")
t("bengali", {"history":[{"role":"user","content":"আমি Киев থেকে এসেছি"}]}, "q", expect_len=1)
t("mixed_roles_str", {"history":["hello","hi there"]}, "q", expect_len=2)

fails = [r for r in results if r[1]=="FAIL"]
for r in results: print(f"{r[1]:4} {r[0]:28} {r[2]}")
print(f"\n{len(results)-len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
