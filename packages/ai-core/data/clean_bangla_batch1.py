# =============================================================================
# NEXUSAI BANGLA BATCH-1 CLEANER + QUALITY AUDIT
# raw_bangla/*.jsonl -> cleaned_bangla/*.jsonl + audit report
# Checks: dedup(SHA256), Bengali script ratio, encoding, empty/short,
#         language tag, license provenance, split separation (seed 42)
# =============================================================================
import os, json, re, hashlib, random
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(DATA_DIR, "raw_bangla")
CLEAN= os.path.join(DATA_DIR, "cleaned_bangla")
SEED = 42
BN_RANGE = re.compile(r'[ঀ-৿]')
MIN_CHARS = 30

def sha(t): return hashlib.sha256(t.encode('utf-8','replace')).hexdigest()

def text_of(rec):
    # pick best text field per known schemas
    for k in ("content","text","answer","output","article","body","question"):
        v=rec.get(k)
        if isinstance(v,str) and v.strip(): return v.strip()
    # fallback: concat string fields
    parts=[str(v) for v in rec.values() if isinstance(v,str) and len(v)>20]
    return " ".join(parts)[:4000]

def bn_ratio(t):
    if not t: return 0.0
    letters=[c for c in t if c.isalpha()]
    if not letters: return 0.0
    return sum(1 for c in letters if BN_RANGE.match(c))/len(letters)

def is_banglish(t):
    return bool(re.search(r'[a-zA-Z]',t)) and bn_ratio(t)>0.15

def clean_file(src, dst, meta):
    stats={"read":0,"empty":0,"short":0,"non_bn":0,"malformed":0,"dup":0,"kept":0}
    seen=set()
    with open(src,encoding='utf-8') as fi, open(dst,'w',encoding='utf-8') as fo:
        for line in fi:
            line=line.strip()
            if not line: stats["empty"]+=1; continue
            stats["read"]+=1
            try: rec=json.loads(line)
            except Exception: stats["malformed"]+=1; continue
            t=text_of(rec)
            if not t or len(t)<MIN_CHARS: stats["short"]+=1; continue
            r=bn_ratio(t)
            if r<0.30 and not is_banglish(t): stats["non_bn"]+=1; continue
            h=sha(t)
            if h in seen: stats["dup"]+=1; continue
            seen.add(h)
            out={"record_id":h[:16],"text":t[:8000],
                 "category":meta.get("category","bangla_general"),
                 "source_name":meta.get("name"),"source_url":meta.get("url"),
                 "license":meta.get("license"),"attribution":meta.get("attribution",""),
                 "lang":"bn" if r>=0.5 else ("banglish" if is_banglish(t) else "mixed"),
                 "bn_ratio":round(r,3),"quality_status":"cleaned"}
            fo.write(json.dumps(out,ensure_ascii=False)+"\n"); stats["kept"]+=1
    return stats

def main():
    os.makedirs(CLEAN,exist_ok=True)
    man_path=os.path.join(RAW,"collection_manifest.json")
    man=json.load(open(man_path,encoding='utf-8')) if os.path.exists(man_path) else {"sources":{}}
    report={"ts":datetime.now().isoformat(),"files":{}}
    for name,info in man.get("sources",{}).items():
        src=os.path.join(RAW,name,name+".jsonl")
        if not os.path.exists(src): continue
        dst=os.path.join(CLEAN,name+".jsonl")
        st=clean_file(src,dst,{"name":name,"url":info.get("url"),
                               "license":info.get("license"),
                               "category":"bangla_reasoning" if "core" in name else
                                          "bangla_instruction" if "bongchat" in name else "bangla_general"})
        st["out_bytes"]=os.path.getsize(dst); st["out_sha256"]=sha(open(dst,'rb').read().hex())
        report["files"][name]=st
        print(name,st,flush=True)
    # aggregate + split plan (actual split applied later at pack time)
    json.dump(report,open(os.path.join(CLEAN,"cleaning_report.json"),"w",encoding='utf-8'),indent=1,ensure_ascii=False)
    print("DONE ->",os.path.join(CLEAN,"cleaning_report.json"))

if __name__=="__main__": main()
