"""NexusAI Core-01 — English-first local dataset builder.

Reads repo English candidate files, filters to verified English, dedups,
counts REAL SentencePiece tokens, deterministic split -> english_first/.
Read-only on sources; never modifies originals. No network.
"""
import os, sys, json, hashlib, re, random
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
AI_CORE = os.path.dirname(HERE)
MODELS = os.path.join(AI_CORE, "models")
for p in (AI_CORE, MODELS):
    if p not in sys.path: sys.path.insert(0, p)

TOK = os.path.join(HERE, "experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
OUT = os.path.join(HERE, "english_first")
SEED = 42
MIN_CHARS = 80
MAX_CHARS = 20000

SOURCES_TXT = [
    "experimental/phase7/tokenizer_corpus/corpus_english.txt",
    "experimental/phase9/curated/corpus_expanded.txt",
    "experimental/phase9_2/corpus/english.txt",
    "experimental/phase8/data/train.txt",
    "experimental/phase8/data/val.txt",
]
SOURCES_JSONL = [
    "collected/cleaned/dolly/dolly-15k_cleaned.jsonl",
    "collected/cleaned/gsm8k/gsm8k_train_cleaned.jsonl",
    "collected/cleaned/gsm8k/gsm8k_test_cleaned.jsonl",
]
# staging love_emotion_en (English subset of app data)
STAGING_EN = os.path.join(AI_CORE, "..", "..", "data", "staging", "love_emotion", "love_emotion_en.jsonl")

def is_english(text):
    bn = sum(1 for c in text if 0x0980 <= ord(c) <= 0x09FF)
    return bn <= max(2, int(0.005 * len(text)))

def norm(t):
    return re.sub(r"\s+", " ", t).strip().lower()

def doc_from_jsonl_obj(o):
    if not isinstance(o, dict): return None
    parts = []
    for k in ("text", "content", "article", "abstract"):
        if isinstance(o.get(k), str) and o[k].strip(): parts.append(o[k].strip())
    ins = o.get("instruction") or o.get("input") or o.get("question")
    ctx = o.get("context","")
    resp = o.get("response") or o.get("output") or o.get("expected_response") or o.get("answer")
    if ins and resp:
        if ctx: parts.append(f"{ins}\n{ctx}\n{resp}")
        else: parts.append(f"{ins}\n{resp}")
    return "\n".join(parts) if parts else None

def main():
    os.makedirs(OUT, exist_ok=True)
    docs, stats = [], {"read":0,"empty":0,"short":0,"non_english":0,"malformed":0}
    src_counts = {}

    for rel in SOURCES_TXT:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p): stats.setdefault("missing",[]).append(rel); continue
        n0 = len(docs)
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                t = line.strip()
                if not t: stats["empty"] += 1; continue
                stats["read"] += 1
                if len(t) < MIN_CHARS: stats["short"] += 1; continue
                if len(t) > MAX_CHARS: t = t[:MAX_CHARS]
                if not is_english(t): stats["non_english"] += 1; continue
                docs.append(t); src_counts[rel] = src_counts.get(rel,0)+1
        print("txt", rel, "->", len(docs)-n0, "docs")

    for rel in SOURCES_JSONL:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p): stats.setdefault("missing",[]).append(rel); continue
        n0 = len(docs)
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                stats["read"] += 1
                try: o = json.loads(line)
                except Exception: stats["malformed"] += 1; continue
                t = doc_from_jsonl_obj(o)
                if not t: stats["empty"] += 1; continue
                if len(t) < MIN_CHARS: stats["short"] += 1; continue
                if not is_english(t): stats["non_english"] += 1; continue
                docs.append(t); src_counts[rel] = src_counts.get(rel,0)+1
        print("jsonl", rel, "->", len(docs)-n0, "docs")

    st = os.path.abspath(STAGING_EN)
    if os.path.exists(st):
        n0=len(docs)
        with open(st, encoding="utf-8", errors="replace") as f:
            for line in f:
                line=line.strip()
                if not line: continue
                try: o=json.loads(line)
                except Exception: stats["malformed"]+=1; continue
                t=doc_from_jsonl_obj(o)
                if t and len(t)>=MIN_CHARS and is_english(t):
                    docs.append(t); src_counts["staging/love_emotion_en"] = src_counts.get("staging/love_emotion_en",0)+1
        print("staging en ->", len(docs)-n0, "docs")

    # dedup exact (normalized)
    seen, dedup = set(), []
    for d in docs:
        k = hashlib.sha1(norm(d).encode()).hexdigest()
        if k in seen: continue
        seen.add(k); dedup.append(d)
    stats["dedup_removed"] = len(docs)-len(dedup)
    docs = dedup

    # tokenize count (real SentencePiece)
    import sentencepiece as spm
    sp = spm.SentencePieceProcessor(model_file=TOK)
    ntoks = []
    for d in docs:
        ntoks.append(len(sp.encode(d, out_type=int)))
    total_tok = sum(ntoks)

    # deterministic split by doc hash (source-level leakage safe: hash of text)
    random.seed(SEED)
    idx = list(range(len(docs)))
    random.shuffle(idx)
    n=len(idx); nval=max(1,int(n*0.015)); ntest=max(1,int(n*0.015))
    te=set(idx[:ntest]); va=set(idx[ntest:ntest+nval]); tr=set(idx[ntest+nval:])
    splits={"train":sorted(tr),"validation":sorted(va),"test":sorted(te)}

    os.makedirs(OUT, exist_ok=True)
    manifest={"created":datetime.now().isoformat(),"seed":SEED,
              "tokenizer":os.path.basename(TOK),"vocab":sp.vocab_size(),
              "sources":src_counts,"stats":stats,
              "counts":{"total_docs":len(docs),"train":len(tr),"validation":len(va),"test":len(te),
                        "total_tokens":total_tok,
                        "train_tokens":sum(ntoks[i] for i in tr),
                        "val_tokens":sum(ntoks[i] for i in va),
                        "test_tokens":sum(ntoks[i] for i in te),
                        "avg_doc_tokens":round(total_tok/max(1,len(docs)),1),
                        "max_doc_tokens":max(ntoks) if ntoks else 0},
              "files":{}}
    for name,key in [("english_train","train"),("english_validation","validation"),("english_test","test")]:
        path=os.path.join(OUT,name+".json")
        with open(path,"w",encoding="utf-8") as f:
            json.dump([{"text":docs[i],"ntok":ntoks[i]} for i in splits[key]],f,ensure_ascii=False)
        h=hashlib.sha256(open(path,'rb').read()).hexdigest()
        manifest["files"][name+".json"]={"sha256":h,"bytes":os.path.getsize(path)}

    qpath=os.path.join(OUT,"dataset_quality_report.json")
    json.dump({"stats":stats,"counts":manifest["counts"],"sources":src_counts},
              open(qpath,"w"),indent=1)
    mpath=os.path.join(OUT,"dataset_manifest.json")
    json.dump(manifest,open(mpath,"w"),indent=1)
    print("\n==== RESULT ====")
    print(json.dumps(manifest["counts"],indent=1))
    print("dedup removed:",stats["dedup_removed"],"| non_english:",stats["non_english"])
    print("out:",OUT)

if __name__=="__main__":
    main()
