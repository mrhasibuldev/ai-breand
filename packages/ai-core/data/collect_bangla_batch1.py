# =============================================================================
# NEXUSAI BANGLA BATCH-1 COLLECTOR (approved sources only)
# Downloads to data/raw_bangla/<source>/ as JSONL + provenance manifest.
# NO training. Raw data immutable after write.
# =============================================================================
import os, json, hashlib, time, traceback
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(DATA_DIR, "raw_bangla")
MANI = os.path.join(RAW, "collection_manifest.json")

SOURCES = [
 dict(name="bangla_wikipedia_mit", repo="sagorsarker/bangla-wikipedia",
      config=None, license_="MIT",
      url="https://huggingface.co/datasets/sagorsarker/bangla-wikipedia",
      note="Bangla Wikipedia dump 2025-06-20, ~995MB, 171K articles"),
 dict(name="sangraha_bengali", repo="ai4bharat/sangraha", config="bn",
      license_="CC-BY-4.0",
      url="https://huggingface.co/datasets/ai4bharat/sangraha",
      note="Sangraha verified Bengali subset"),
 dict(name="bangla_core_5000", repo="Maruf204949/BanglaCoRe-5000",
      config=None, license_="CC-BY-4.0",
      url="https://huggingface.co/datasets/Maruf204949/BanglaCoRe-5000",
      note="Bengali commonsense reasoning MCQ, 5000 items"),
 dict(name="bongchat_v1", repo="lumatic-ai/BongChat-v1-253k",
      config=None, license_="MIT",
      url="https://huggingface.co/datasets/lumatic-ai/BongChat-v1-253k",
      note="BongChat instruction dataset"),
]

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()

def ds_to_jsonl(ds, out_path, text_fields):
    n=0
    with open(out_path,'w',encoding='utf-8') as f:
        for split in ds.keys() if hasattr(ds,'keys') else [None]:
            data = ds[split] if split else ds
            for row in data:
                rec={"_split":split or "train"}
                for k,v in row.items():
                    rec[k]= v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
                f.write(json.dumps(rec,ensure_ascii=False)+"\n"); n+=1
    return n

def main():
    from datasets import load_dataset
    os.makedirs(RAW, exist_ok=True)
    man={"ts":datetime.now().isoformat(),"sources":{},"errors":[]}
    for s in SOURCES:
        name=s["name"]; outdir=os.path.join(RAW,name); os.makedirs(outdir,exist_ok=True)
        out=os.path.join(outdir,name+".jsonl")
        entry={"repo":s["repo"],"config":s["config"],"license":s["license_"],
               "url":s["url"],"note":s["note"],"status":"PENDING"}
        try:
            print("=== downloading",name,"===",flush=True)
            t0=time.time()
            try:
                ds=load_dataset(s["repo"],s["config"])
            except Exception:
                ds=load_dataset(s["repo"])   # config may differ
            n=ds_to_jsonl(ds,out,text_fields=None)
            entry.update({"status":"OK","records":n,"elapsed_s":round(time.time()-t0,1),
                          "file":out,"sha256":sha256_file(out),
                          "bytes":os.path.getsize(out)})
            print("OK",name,n,"records",round(time.time()-t0,1),"s",flush=True)
        except Exception as e:
            entry.update({"status":"FAILED","error":repr(e)[:400]})
            man["errors"].append({"source":name,"error":repr(e)[:400]})
            print("FAILED",name,repr(e)[:200],flush=True)
        man["sources"][name]=entry
        json.dump(man,open(MANI,"w",encoding="utf-8"),indent=1,ensure_ascii=False)
    print("\nDONE. manifest ->",MANI)

if __name__=="__main__":
    main()
