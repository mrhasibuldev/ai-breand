# =============================================================================
# NEXUSAI BANGLA CORPUS CLEANER v2 — APPROVED PHASE 1
# Streaming, deterministic, non-destructive. Raw data untouched.
# Input : data/raw_bangla/<src>/<src>.jsonl
# Output: data/cleaned_bangla/<src>.jsonl + cleaning_report.json + rejects log
# =============================================================================
import os, json, re, html, hashlib, time
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RAW  = os.path.join(DATA_DIR, "raw_bangla")
CLEAN= os.path.join(DATA_DIR, "cleaned_bangla")
SEED = 42
MIN_CHARS = 40
MAX_CHARS = 8000

HTML_TAG  = re.compile(r'<[^>]{1,200}>')
HTML_ENT  = re.compile(r'&[a-zA-Z#0-9]{1,10};')
NAV_HINT  = re.compile(r'(home|login|sign in|subscribe|menu|navigation|footer|copyright|all rights reserved|cookie)', re.I)
WS        = re.compile(r'[ \t]+')
BN        = re.compile(r'[ঀ-৿]')
LAT       = re.compile(r'[a-zA-Z]')

def sha(t): return hashlib.sha256(t.encode('utf-8','replace')).hexdigest()

def text_of(rec):
    for k in ("content","text","article","body","answer","output","question"):
        v=rec.get(k)
        if isinstance(v,str) and v.strip(): return v.strip()
    if isinstance(rec.get("messages"),list):
        return " ".join(str(m.get("content","")) for m in rec["messages"] if isinstance(m,dict))
    parts=[str(v) for v in rec.values() if isinstance(v,str) and len(v)>20]
    return " ".join(parts)[:MAX_CHARS]

def bn_ratio(t):
    letters=[c for c in t if c.isalpha()]
    return sum(1 for c in letters if BN.match(c))/len(letters) if letters else 0.0

def is_banglish(t): return bool(LAT.search(t)) and bn_ratio(t)>0.10

def rep_ratio(t):
    w=t.split()
    if len(w)<8: return 0.0
    return 1-len(set(w))/len(w)

def clean_text(t, rej):
    if not t or len(t.strip())<MIN_CHARS: rej["short"]=rej.get("short",0)+1; return None
    t=html.unescape(t)
    t=HTML_TAG.sub(' ',t); t=HTML_ENT.sub(' ',t)
    t=WS.sub(' ',t).strip()
    if len(t)<MIN_CHARS: rej["after_html_strip"]=rej.get("after_html_strip",0)+1; return None
    # nav/boilerplate: very short + many nav keywords
    nav_hits=len(NAV_HINT.findall(t))
    if len(t)<300 and nav_hits>=3: rej["boilerplate"]=rej.get("boilerplate",0)+1; return None
    if rep_ratio(t)>0.6: rej["repetitive"]=rej.get("repetitive",0)+1; return None
    r=bn_ratio(t)
    if r<0.30 and not is_banglish(t): rej["non_bn"]=rej.get("non_bn",0)+1; return None
    if r>0.9 and not BN.search(t): rej["corrupt"]=rej.get("corrupt",0)+1; return None
    return t[:MAX_CHARS], r

def process(src_name, src_path, dst_path, rej_path, meta):
    stats={"read":0,"kept":0,"rejects":{},"tokens_raw":0,"tokens_clean":0,
           "bn_only":0,"en_only":0,"mixed":0,"other":0,"chars_clean":0}
    seen=set(); rejects=open(rej_path,'w',encoding='utf-8')
    import sentencepiece as spm
    sp=spm.SentencePieceProcessor(model_file=os.path.join(
        DATA_DIR,"experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model"))
    t0=time.time()
    with open(src_path,encoding='utf-8') as fi, open(dst_path,'w',encoding='utf-8') as fo:
        for line in fi:
            line=line.strip()
            if not line: stats["rejects"]["empty_line"]=stats["rejects"].get("empty_line",0)+1; continue
            stats["read"]+=1
            try: rec=json.loads(line)
            except Exception: stats["rejects"]["malformed"]=stats["rejects"].get("malformed",0)+1; continue
            t=text_of(rec)
            rej={}
            c=clean_text(t,rej) if t else (stats["rejects"].__setitem__("empty_text",stats["rejects"].get("empty_text",0)+1) or None)
            if c is None:
                for k,v in rej.items(): stats["rejects"][k]=stats["rejects"].get(k,0)+v
                rejects.write(json.dumps({"reason":"rejected","src_line":stats["read"]},ensure_ascii=False)+"\n")
                continue
            t2,r=c
            if len(t2)<MIN_CHARS: stats["rejects"]["post_clean_short"]=stats["rejects"].get("post_clean_short",0)+1; continue
            h=sha(t2)
            if h in seen:
                stats["rejects"]["exact_dup"]=stats["rejects"].get("exact_dup",0)+1
                rejects.write(json.dumps({"reason":"exact_dup","sha":h[:16]},ensure_ascii=False)+"\n")
                continue
            seen.add(h)
            lat=len(LAT.findall(t2))
            lang="bn" if r>=0.6 and lat==0 else ("en" if lat>0 and r<0.1 else ("mixed" if lat>0 else "bn"))
            stats[{"bn":"bn_only","en":"en_only"}.get(lang,"mixed") if lang in("bn","en") else "mixed"]+=1
            stats["chars_clean"]+=len(t2)
            try:
                stats["tokens_clean"]+=len(sp.encode(t2[:8000],out_type=int))
            except Exception: pass
            out={"record_id":h[:16],"text":t2,"category":meta.get("category","bangla_general"),
                 "source_name":meta.get("name"),"source_url":meta.get("url"),
                 "license":meta.get("license"),"lang":lang,"bn_ratio":round(r,3),
                 "quality_status":"cleaned","split":"unassigned"}
            fo.write(json.dumps(out,ensure_ascii=False)+"\n")
            stats["kept"]+=1
            if stats["read"]%50000==0: print("  ",src_name,stats["read"],"read",stats["kept"],"kept",flush=True)
    rejects.close()
    stats["elapsed_s"]=round(time.time()-t0,1)
    stats["kept_rate"]=round(stats["kept"]/max(1,stats["read"]),3)
    return stats

def main():
    os.makedirs(CLEAN,exist_ok=True)
    man=json.load(open(os.path.join(RAW,"collection_manifest.json"),encoding='utf-8'))
    meta_map={
      "bangla_wikipedia_mit":{"category":"bangla_general","name":"bangla-wikipedia","license":"MIT (packaging); content CC BY-SA 3.0","url":"https://huggingface.co/datasets/sagorsarker/bangla-wikipedia"},
      "sangraha_bengali":{"category":"bangla_general","name":"sangraha-verified-bn","license":"CC-BY-4.0","url":"https://huggingface.co/datasets/ai4bharat/sangraha"},
      "bongchat_v1":{"category":"bangla_instruction","name":"bongchat-v1","license":"MIT","url":"https://huggingface.co/datasets/lumatic-ai/BongChat-v1-253k"},
    }
    report={"ts":datetime.now().isoformat(),"files":{}}
    for name,meta in meta_map.items():
        src=os.path.join(RAW,name,name+".jsonl")
        if not os.path.exists(src): print("SKIP missing",src); continue
        dst=os.path.join(CLEAN,name+".jsonl")
        rej=os.path.join(CLEAN,name+"_rejects.jsonl")
        print("=== cleaning",name,"===",flush=True)
        st=process(name,src,dst,rej,meta)
        st["out_bytes"]=os.path.getsize(dst)
        st["reject_log"]=rej
        report["files"][name]=st
        print("DONE",name,json.dumps({k:st[k] for k in ("read","kept","kept_rate","tokens_clean","elapsed_s")}),flush=True)
        json.dump(report,open(os.path.join(CLEAN,"cleaning_report.json"),"w",encoding='utf-8'),indent=1,ensure_ascii=False)
    print("ALL DONE ->",os.path.join(CLEAN,"cleaning_report.json"))

if __name__=="__main__": main()
