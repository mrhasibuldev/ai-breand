# =============================================================================
# COLAB RUN4 EVALUATION — CPU-ONLY, READ-ONLY
# Reads the 6 existing audit files, prints all prompt outputs side-by-side,
# computes MECHANICAL metrics only, writes RUN3_VS_RUN4_QUALITY_REPORT.md.
# No torch/CUDA, no training, no checkpoint modification.
# =============================================================================
import json, os, re, sys

BASE = "/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT/audit_20261116_210128"
REQUIRED = [
    "ACTUAL_GENERATION_SAMPLES.json",
    "RUN3_VS_RUN4_COMPARISON.json",
    "RUN3_CHECKPOINT_VERIFICATION.json",
    "RUN4_CHECKPOINT_VERIFICATION.json",
    "CHECKPOINT_INTEGRITY_FINAL.json",
    "NEXUSAI_RUN4_VERIFICATION_AND_BENCHMARK_REPORT.md",
]
OUT = os.path.join(BASE, "RUN3_VS_RUN4_QUALITY_REPORT.md")
BN = re.compile(r"[ঀ-৿]")

print("=" * 70)
print("RUN4 EVALUATION — CPU-ONLY READ-ONLY")
print("=" * 70)

# ---------- validate inputs ----------
missing = [f for f in REQUIRED if not os.path.exists(os.path.join(BASE, f))]
if not os.path.isdir(BASE):
    print(f"FAIL: audit dir not found: {BASE}")
    sys.exit(1)
if missing:
    print("MISSING FILES:", missing)
    # continue with what exists for samples at least
samples_p = os.path.join(BASE, "ACTUAL_GENERATION_SAMPLES.json")
if not os.path.exists(samples_p):
    print("FATAL: ACTUAL_GENERATION_SAMPLES.json missing — cannot evaluate")
    sys.exit(1)
print(f"dir OK: {BASE}")
for f in REQUIRED:
    p = os.path.join(BASE, f)
    print(f"  {'OK ' if os.path.exists(p) else 'MISS'} {f}"
          + (f" ({os.path.getsize(p)}B)" if os.path.exists(p) else ""))

def loadj(name):
    p = os.path.join(BASE, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

samp = loadj("ACTUAL_GENERATION_SAMPLES.json")
comp = loadj("RUN3_VS_RUN4_COMPARISON.json")
v3 = loadj("RUN3_CHECKPOINT_VERIFICATION.json") or {}
v4 = loadj("RUN4_CHECKPOINT_VERIFICATION.json") or {}
integ = loadj("CHECKPOINT_INTEGRITY_FINAL.json") or {}

# ---------- mechanical metrics ----------
def metrics(rs):
    n = len(rs) or 1
    return {
        "n": len(rs),
        "empty": round(sum(1 for r in rs if r.get("empty")) / n, 3),
        "leak": round(sum(1 for r in rs if r.get("prompt_leak")) / n, 3),
        "bn_out": round(sum(1 for r in rs if r.get("bn_script")) / n, 3),
        "avg_len": round(sum(len(r.get("output", "")) for r in rs) / n, 1),
        "warn": sum(1 for r in rs if r.get("warning")),
    }

def heuristic(r):
    """Mechanical only: non-empty + no prompt-leak + not degenerate-repetitive."""
    o = (r.get("output") or "").strip()
    if not o: return -2
    if r.get("prompt_leak"): return -1
    w = o.split()
    if len(w) >= 8 and len(set(w)) / len(w) < 0.3: return 0
    return 1

report = []
report.append("# Run3 vs Run4 Quality Report (mechanical + raw outputs)\n")
report.append(f"Run3: ep{v3.get('epoch')} step{v3.get('step')} "
              f"sha={str(v3.get('sha256'))[:20]}…\n")
report.append(f"Run4: ep{v4.get('epoch')} step{v4.get('step')} "
              f"sha={str(v4.get('sha256'))[:20]}…\n")
report.append(f"Integrity: run3_unchanged={integ.get('run3_unchanged')} "
              f"run4_unchanged={integ.get('run4_unchanged')}\n")
report.append("NOTE: metrics below are MECHANICAL ONLY (empty/leak/bn-script/"
              "length). They do NOT measure semantic quality.\n")

for mode in ("greedy", "sample"):
    if mode not in samp: continue
    r3, r4 = samp[mode]["run3"], samp[mode]["run4"]
    m3, m4 = metrics(r3), metrics(r4)
    report.append(f"\n## {mode.upper()} — mechanical\n")
    report.append("| metric | run3 | run4 |\n|---|---|---|\n")
    for k in ("empty", "leak", "bn_out", "avg_len", "warn"):
        report.append(f"| {k} | {m3[k]} | {m4[k]} |\n")
    # per-language breakdown (mechanical)
    for lg in ("bn", "en", "banglish", "mixed"):
        s3 = [r for r in r3 if r.get("lang") == lg]
        s4 = [r for r in r4 if r.get("lang") == lg]
        if not s3: continue
        a, b = metrics(s3), metrics(s4)
        report.append(f"| {lg}:empty | {a['empty']} | {b['empty']} |\n")
        report.append(f"| {lg}:bn_out | {a['bn_out']} | {b['bn_out']} |\n")

# ---------- per-prompt side-by-side (both modes) ----------
for mode in ("greedy", "sample"):
    if mode not in samp: continue
    r3, r4 = samp[mode]["run3"], samp[mode]["run4"]
    report.append(f"\n## {mode.upper()} — per-prompt raw outputs\n")
    better = worse = equal = 0
    for a, b in zip(r3, r4):
        sa, sb = heuristic(a), heuristic(b)
        v = "BETTER" if sb > sa else ("WORSE" if sb < sa else "EQUAL")
        if v == "BETTER": better += 1
        elif v == "WORSE": worse += 1
        else: equal += 1
        report.append(f"### {a.get('id')} | {a.get('cat')} | {a.get('lang')} "
                      f"| heuristic: {v}\n")
        report.append(f"P: {a.get('prompt')}\n")
        report.append(f"R3: {a.get('output','')[:400]}\n")
        report.append(f"    (empty={a.get('empty')} warn={a.get('warning')} "
                      f"lat={a.get('latency_s')}s)\n")
        report.append(f"R4: {b.get('output','')[:400]}\n")
        report.append(f"    (empty={b.get('empty')} warn={b.get('warning')} "
                      f"lat={b.get('latency_s')}s)\n\n")
    report.append(f"Heuristic tally ({mode}): better={better} worse={worse} "
                  f"equal={equal} — MECHANICAL ONLY, not semantic verdict\n")

report.append("\n## Verdict guidance\n"
              "Mechanical metrics cannot establish semantic quality. "
              "Human review of the raw outputs above is required for the "
              "final RUN4-vs-RUN3 recommendation.\n")

open(OUT, "w", encoding="utf-8").write("".join(report))
print(f"\nWROTE REPORT: {OUT}")

# ---------- console dump for paste-back ----------
print("\n" + "=" * 70)
print("RAW OUTPUTS — paste this block back for qualitative analysis")
print("=" * 70)
for mode in ("greedy", "sample"):
    if mode not in samp: continue
    print(f"\n########## {mode.upper()} ##########")
    for a, b in zip(samp[mode]["run3"], samp[mode]["run4"]):
        print(f"\n### {a.get('id')} | {a.get('cat')} | {a.get('lang')}")
        print(f"P:  {a.get('prompt')}")
        print(f"R3: {a.get('output','')[:280]!r} empty={a.get('empty')} warn={a.get('warning')}")
        print(f"R4: {b.get('output','')[:280]!r} empty={b.get('empty')} warn={b.get('warning')}")
print("\n===== END =====")
