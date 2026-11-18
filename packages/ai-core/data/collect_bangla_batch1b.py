# =============================================================================
# NEXUSAI BANGLA BATCH-1b — STREAMING COLLECTOR (disk-safe)
# Streams HF datasets -> JSONL directly, NO parquet cache, bounded size.
# Sources: sangraha(verified/ben), BanglaCoRe-5000, BongChat-v1
# =============================================================================
import os, json, hashlib, time
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(DATA_DIR, "raw_bangla")
MANI = os.path.join(RAW, "collection_manifest.json")
MAX_BYTES_PER_SOURCE = 400*1024*1024   # 400MB cap each
MAX_DOCS = {"sangraha_bengali": 400000, "bangla_core_5000": 20000, "bongchat_v1": 150000}

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()

def stream_to_jsonl(repo, config, data_dir, out_path, max_docs, max_bytes):
    """Stream parquet rows -> jsonl lines until caps."""
    from datasets import load_dataset
    ds = load_dataset(repo, config, split=None, streaming=True)
    n=0; written=0; splits={}
    try:
        items = ds.items() if hasattr(ds,'items') else [(None,ds)]
    except Exception:
        items=[(None,ds)]
    with open(out_path,'w',encoding='utf-8') as f:
        for split_name, split_ds in items:
            for row in split_ds:
                if n>=max_docs: break
                rec={"_split":split_name or "train"}
                for k,v in row.items():
                    rec[k]= v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
                line=json.dumps(rec,ensure_ascii=False)+"\n"
                f.write(line); written+=len(line.encode()); n+=1
                if written>=max_bytes: break
            if n>=max_docs or written>=max_bytes: break
    return n, written

def main():
    from datasets import load_dataset
    man=json.load(open(MANI,encoding='utf-8')) if os.path.exists(MANI) else {"sources":{}}
    jobs=[
      dict(name="sangraha_bengali", repo="ai4bharat/sangraha", config="verified",
           data_dir="ben", license_="CC-BY-4.0",
           url="https://huggingface.co/datasets/ai4bharat/sangraha",
           note="Sangraha verified Bengali (streaming sample, ben subset ~77GB total)"),
      dict(name="bangla_core_5000", repo="Maruf204949/BanglaCoRe-5000", config=None,
           data_dir=None, license_="CC-BY-4.0",
           url="https://huggingface.co/datasets/Maruf204949/BanglaCoRe-5000",
           note="Bengali commonsense reasoning MCQ"),
      dict(name="bongchat_v1", repo="lumatic-ai/BongChat-v1-253k", config=None,
           data_dir=None, license_="MIT",
           url="https://huggingface.co/datasets/lumatic-ai/BongChat-v1-253k",
           note="BongChat instruction dataset (streaming sample)"),
    ]
    for s in jobs:
        name=s["name"]; outdir=os.path.join(RAW,name); os.makedirs(outdir,exist_ok=True)
        out=os.path.join(outdir,name+".jsonl")
        entry={"repo":s["repo"],"config":s["config"],"data_dir":s["data_dir"],
               "license":s["license_"],"url":s["url"],"note":s["note"],"status":"PENDING"}
        try:
            print("=== streaming",name,"===",flush=True); t0=time.time()
            # try (repo,config,data_dir) combos
            n=written=0
            try:
                if s["data_dir"]:
                    ds=load_dataset(s["repo"],s["config"],data_dir=s["data_dir"],split=None,streaming=True)
                else:
                    ds=load_dataset(s["repo"],s["config"],split=None,streaming=True)
                items = list(ds.items()) if hasattr(ds,'items') else [(None,ds)]
                with open(out,'w',encoding='utf-8') as f:
                    for sp,spds in items:
                        for row in spds:
                            if n>=MAX_DOCS[name]: break
                            rec={"_split":sp or "train"}
                            for k,v in row.items():
                                rec[k]= v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
                            line=json.dumps(rec,ensure_ascii=False)+"\n"
                            f.write(line); written+=len(line.encode()); n+=1
                            if written>=MAX_BYTES_PER_SOURCE: break
                        if n>=MAX_DOCS[name] or written>=MAX_BYTES_PER_SOURCE: break
            except Exception as e1:
                # fallback: config=None without data_dir
                print("  primary failed:",repr(e1)[:150],flush=True)
                ds=load_dataset(s["repo"],split=None,streaming=True)
                with open(out,'w',encoding='utf-8') as f:
                    for row in ds:
                        if n>=MAX_DOCS[name] or written>=MAX_BYTES_PER_SOURCE: break
                        rec={"_split":"train"}
                        for k,v in row.items():
                            rec[k]= v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
                        line=json.dumps(rec,ensure_ascii=False)+"\n"
                        f.write(line); written+=len(line.encode()); n+=1
            entry.update({"status":"OK","records":n,"bytes":written,
                          "file":out,"sha256":sha256_file(out),
                          "elapsed_s":round(time.time()-t0,1),
                          "note":s["note"]+" [STREAMED SAMPLE]"})
            print("OK",name,n,"records",round(written/1e6,1),"MB",flush=True)
        except Exception as e:
            entry.update({"status":"FAILED","error":repr(e)[:400]})
            print("FAILED",name,repr(e)[:200],flush=True)
        man["sources"][name]=entry
        json.dump(man,open(MANI,"w",encoding='utf-8'),indent=1,ensure_ascii=False)
    print("DONE")

if __name__=="__main__": main()
