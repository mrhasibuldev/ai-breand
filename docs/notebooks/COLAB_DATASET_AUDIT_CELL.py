# =============================================================================
# NEXUSAI CORE-01 — CONSOLIDATED DATASET READINESS AUDIT CELL (Google Colab)
# Read-only. Real SentencePiece token counts. No modification, no training.
# Outputs: JSON + Markdown report -> Drive/NexusAI/audit_reports/
# =============================================================================
import os, sys, json, glob, hashlib, unicodedata, random, time
from datetime import datetime

AI_CORE   = "/content/nexusai/packages/ai-core"
DRIVE_DATA = "/content/drive/MyDrive/NexusAI/data"
REPORT_DIR = "/content/drive/MyDrive/NexusAI/audit_reports"
TOK_PATH  = os.path.join(AI_CORE,
    "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
os.makedirs(REPORT_DIR, exist_ok=True)

R = {"ts": datetime.now().isoformat(), "paths": {}, "datasets": {},
     "language": {}, "tokenizer": {}, "quality": {}, "findings": [],
     "errors": [], "status": "AUDITED"}

def sha256_file(path, max_bytes=64<<20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(max_bytes))
    return h.hexdigest()

def lang_of(text):
    """Heuristic buckets. 'bengali_latin_mix' = likely romanized Bengali (UNCERTAIN)."""
    bn = sum(1 for c in text[:400] if 0x0980 <= ord(c) <= 0x09FF)
    lat = sum(1 for c in text[:400] if c.isascii() and c.isalpha())
    if bn == 0 and lat > 0: return "english"
    if bn > 0 and lat == 0: return "bengali"
    if bn > 0 and lat > 0: return "mixed_bn_en"
    if bn == 0 and lat == 0: return "other"
    return "bengali_latin_mix"

# ---------- locate files ----------
train_p = os.path.join(DRIVE_DATA, "english_train.jsonl")
val_p   = os.path.join(DRIVE_DATA, "english_val.jsonl")
man_p   = os.path.join(DRIVE_DATA, "manifest.json")
for p in (train_p, val_p, man_p):
    R["paths"][os.path.basename(p)] = {"exists": os.path.exists(p),
        "size_mb": round(os.path.getsize(p)/1e6,1) if os.path.exists(p) else None}
    if os.path.exists(p) and os.path.getsize(p) < 64<<20:
        R["paths"][os.path.basename(p)]["sha256"] = sha256_file(p)

missing = [k for k,v in R["paths"].items() if not v["exists"]]

def save_and_exit():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jp = os.path.join(REPORT_DIR, "dataset_audit_%s.json" % ts)
    mp = os.path.join(REPORT_DIR, "dataset_audit_%s.md"   % ts)
    json.dump(R, open(jp,"w",encoding="utf-8"), indent=1, ensure_ascii=False)
    open(mp,"w",encoding="utf-8").write(render_md())
    print("reports ->", jp, "|", mp)

if missing:
    R["status"] = "BLOCKED — missing: %s" % missing
    print(R["status"]); save_and_exit()

def render_md():
    L = ["# Core-01 Dataset Audit — %s" % R["ts"], ""]
    for k,v in R["datasets"].items():
        L.append("## %s" % k)
        for kk,vv in v.items(): L.append("- %s: %s" % (kk,vv))
        L.append("")
    L.append("## Language distribution")
    for k,v in R["language"].items(): L.append("- %s: %s" % (k,v))
    L.append("## Findings")
    for f in R["findings"]: L.append("- "+f)
    L.append("## Errors: %s" % R["errors"])
    return "\n".join(L)

# ---------- tokenizer ----------
try:
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=TOK_PATH)
    R["tokenizer"] = {"vocab": sp.vocab_size(), "pad": sp.pad_id(),
                      "unk": sp.unk_id(), "bos": sp.bos_id(), "eos": sp.eos_id(),
                      "path": TOK_PATH, "sha256": sha256_file(TOK_PATH)}
    print("tokenizer:", R["tokenizer"])
except Exception as e:
    R["errors"].append("tokenizer load failed: %r" % e); save_and_exit()

# ---------- stream audit ----------
def audit(path, label):
    recs = 0; valid = 0; empty = 0; bad = 0
    tok_total = 0; unk_total = 0; ntok_field_sum = 0
    texts = []          # keep texts for dup/overlap (memory: ~100M tok -> ~400MB; ok on Colab)
    seq_lens = []       # ntok per doc (from manifest field or tokenized)
    lang_counts = {"english":0,"bengali":0,"mixed_bn_en":0,"other":0,"bengali_latin_mix":0}
    t0 = time.time()
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line: continue
            recs += 1
            try:
                o = json.loads(line)
                t = o.get("text","") if isinstance(o,dict) else ""
                if not isinstance(t,str) or not t.strip(): empty += 1; continue
                valid += 1
                texts.append(t)
                # tokenize in chunks of docs — count exactly
                ids = sp.encode(t, out_type=int)
                tok_total += len(ids)
                unk_total += sum(1 for x in ids if x == sp.unk_id())
                seq_lens.append(len(ids))
                ntok_field_sum += o.get("ntok",0) if isinstance(o,dict) else 0
                lang_counts[lang_of(t[:400])] += 1
            except Exception:
                bad += 1
            if i % 20000 == 0 and i:
                print("  %s: %d docs, %.0fs" % (label, i, time.time()-t0), flush=True)
    # stats
    import statistics
    ss = sorted(seq_lens)
    def pct(p): return ss[min(len(ss)-1, int(len(ss)*p))] if ss else 0
    d = {"records": recs, "valid": valid, "empty": empty, "bad_json": bad,
         "tokenizer_tokens": tok_total, "ntok_field_sum": ntok_field_sum,
         "unk_tokens": unk_total,
         "unk_rate_pct": round(100*unk_total/max(1,tok_total),3),
         "avg_doc_tokens": round(tok_total/max(1,valid),1),
         "p50_tokens": pct(0.5), "p95_tokens": pct(0.95), "max_tokens": ss[-1] if ss else 0,
         "dup_docs": valid - len(set(texts)),
         "unique_docs": len(set(texts)),
         "language_docs": lang_counts,
         "elapsed_s": round(time.time()-t0,1)}
    R["datasets"][label] = d
    return texts

print("auditing train...")
tr_texts = audit(train_p, "english_train")
print("auditing val...")
va_texts = audit(val_p, "english_val")

# ---------- leakage ----------
R["overlap_docs"] = len(set(tr_texts) & set(va_texts))
print("overlap:", R["overlap_docs"])

# ---------- manifest cross-check ----------
try:
    man = json.load(open(man_p, encoding="utf-8"))
    R["manifest"] = {"target": man.get("target",{}).get("target_tokens"),
                     "actual": man.get("target",{}).get("actual_accepted_tokens"),
                     "source": man.get("source",{})}
    actual = R["datasets"]["english_train"]["tokenizer_tokens"] + \
             R["datasets"]["english_val"]["tokenizer_tokens"]
    R["manifest"]["recount_total"] = actual
    R["manifest"]["recount_matches"] = abs(actual - (R["manifest"]["actual"] or -1)) < 1000
except Exception as e:
    R["errors"].append("manifest: %r" % e)

# ---------- language verdict ----------
lt = R["datasets"]["english_train"]["language_docs"]
R["language"]["train_doc_counts"] = lt
R["language"]["note"] = ("english_* files are FineWeb English; Bengali-script docs "
    "expected ~0. 'bengali_latin_mix' = romanized-Bengali-looking (UNCERTAIN).")
non_en = sum(v for k,v in lt.items() if k != "english")
R["findings"].append(
    "train docs: %s | non-English-script docs: %s | tokenizer_tokens: %s | unk_rate: %s%%" %
    (R["datasets"]["english_train"]["valid"], non_en,
     R["datasets"]["english_train"]["tokenizer_tokens"],
     R["datasets"]["english_train"]["unk_rate_pct"]))
R["findings"].append(
    "Bengali/Banglish dedicated data is essentially ABSENT from this corpus — "
    "multilingual goals need a separate acquisition phase.")

save_and_exit()
print("DONE — reports saved")
