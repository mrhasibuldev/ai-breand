# =============================================================================
# NEXUSAI PHASE2 — RUN4 MULTILINGUAL CORPUS BUILDER
# Combines: cleaned_bangla (sampled) + english_first + tinystories + reasoning
# Output: data/phase2/run4_corpus/corpus_train.jsonl (+ manifest)
# Deterministic seed 42. No raw data modified.
# =============================================================================
import os, json, random, hashlib

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = DATA_DIR                                            # data/ dir itself
REPO = os.path.dirname(os.path.dirname(os.path.dirname(DATA_DIR)))  # repo root
OUT = os.path.join(DATA_DIR, "phase2", "run4_corpus")
os.makedirs(OUT, exist_ok=True)
random.seed(42)

BN_FILES = [
 ("bangla_wikipedia_mit", 45000, "bangla_general"),
 ("sangraha_bengali",      9000, "bangla_general"),
 ("bongchat_v1",          30000, "bangla_instruction"),
]
CLEAN = os.path.join(ROOT, "cleaned_bangla")
ENG_TRAIN = os.path.join(ROOT, "english_first", "english_train.json")
TINY = os.path.join(ROOT, "raw_english", "tinystories", "tinystories.jsonl")
RSN = os.path.join(DATA_DIR, "phase2", "reasoning", "reasoning_train.jsonl")

def reservoir_sample(path, k):
    """Deterministic even-stride sample of k docs."""
    # first count lines cheaply is expensive; use stride estimate then adjust
    # simpler: collect all texts? too big for wiki (168K lines ~844MB) — stream twice ok
    texts=[]
    with open(path,encoding='utf-8') as f:
        for line in f:
            try: r=json.loads(line)
            except: continue
            t=r.get("text","")
            if t.strip(): texts.append(t)
    n=len(texts)
    if n<=k: return texts
    stride=n/k
    return [texts[int(i*stride)] for i in range(k)]

def main():
    manifest={"seed":42,"components":{},"total_docs":0}
    out_path=os.path.join(OUT,"corpus_train.jsonl")
    total=0
    with open(out_path,'w',encoding='utf-8') as fo:
        # --- Bengali ---
        for name,k,cat in BN_FILES:
            p=os.path.join(CLEAN,name+".jsonl")
            docs=reservoir_sample(p,k)
            for t in docs:
                fo.write(json.dumps({"text":t,"category":cat,"lang":"bn_mixed","source":name},ensure_ascii=False)+"\n")
            manifest["components"][name]={"sampled":len(docs),"category":cat}
            total+=len(docs); print("bn",name,len(docs),flush=True)
        # --- English existing ---
        en=json.load(open(ENG_TRAIN,encoding='utf-8'))
        # english_train.json: list of docs or dicts? check
        texts=[]
        for it in en:
            if isinstance(it,str): texts.append(it)
            elif isinstance(it,dict):
                t=it.get("text") or it.get("content") or ""
                if t: texts.append(t)
        for t in texts:
            fo.write(json.dumps({"text":t,"category":"english_general","lang":"en","source":"english_first"},ensure_ascii=False)+"\n")
        manifest["components"]["english_first"]={"docs":len(texts),"category":"english_general"}
        total+=len(texts); print("en english_first",len(texts),flush=True)
        # --- TinyStories ---
        n=0
        with open(TINY,encoding='utf-8') as f:
            for line in f:
                try: r=json.loads(line)
                except: continue
                t=r.get("text","")
                if t.strip():
                    fo.write(json.dumps({"text":t,"category":"english_simple","lang":"en","source":"tinystories"},ensure_ascii=False)+"\n")
                    n+=1
        manifest["components"]["tinystories"]={"docs":n,"category":"english_simple"}
        total+=n; print("en tinystories",n,flush=True)
        # --- Reasoning (x3 weight via repetition, marked) ---
        n=0
        rows=[json.loads(l) for l in open(RSN,encoding='utf-8')]
        for rep in range(3):
            for r in rows:
                txt=f"Question: {r['instruction']}\nAnswer: {r['answer']}\nExplanation: {r['explanation']}"
                fo.write(json.dumps({"text":txt,"category":"reasoning_"+r["category"],"lang":r["lang"],"source":"reasoning_v1"},ensure_ascii=False)+"\n")
                n+=1
        manifest["components"]["reasoning_v1"]={"base_docs":len(rows),"repeats":3,"emitted":n}
        total+=n; print("reasoning emitted",n,flush=True)
    manifest["total_docs"]=total
    json.dump(manifest,open(os.path.join(OUT,"corpus_manifest.json"),"w",encoding='utf-8'),indent=1)
    print("TOTAL",total,"->",out_path)

if __name__=="__main__": main()
