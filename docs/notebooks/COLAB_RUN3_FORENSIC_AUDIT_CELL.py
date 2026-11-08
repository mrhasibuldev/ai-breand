# =============================================================================
# NEXUSAI CORE-01 — RUN3 FORENSIC AUDIT CELL (READ-ONLY, Colab)
# Verifies run3 ckpt + report, compares run1/2/3, resume chain.
# NO training. NO modification. Output -> reports/run3_audit_<ts>.json/.md
# =============================================================================
import os, sys, json, glob, hashlib
from datetime import datetime
import torch

BASE   = "/content/drive/MyDrive/NexusAI"
CKPTS  = {r: os.path.join(BASE,"checkpoints","core01_english"+s)
          for r,s in [("run1",""),("run2","_run2"),("run3","_run3")]}
REPORTS= os.path.join(BASE,"reports")
R3REP  = os.path.join(REPORTS,"train_run3_20261108_205015.json")
R3MD   = os.path.join(REPORTS,"train_run3_20261108_205015.md")
AI     = "/content/nexusai/packages/ai-core"
TOK    = os.path.join(AI,"data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
for pp in (AI, os.path.join(AI,"models")):
    if pp not in sys.path: sys.path.insert(0,pp)

A = {"ts": datetime.now().isoformat(), "runs": {}, "checks": {}, "notes": []}
def chk(k,ok,d=""):
    A["checks"][k]={"status":"PASS" if ok else "FAIL","detail":str(d)[:400]}
    print(("PASS " if ok else "FAIL ")+k+" | "+str(d)[:140])
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def ckmeta(p):
    ck=torch.load(p,map_location="cpu",weights_only=False)
    return {"step":ck.get("step"),"epoch":ck.get("epoch"),
            "model_status":ck.get("model_status"),
            "train_loss":ck.get("train_loss"),"val_loss":ck.get("val_loss"),
            "has_model_sd":"model_state_dict" in ck,
            "has_opt_sd":"optimizer_state_dict" in ck,
            "n_model_tensors":len(ck.get("model_state_dict",{})),
            "size_bytes":os.path.getsize(p),"sha256":sha(p)}

# ===== 1. per-run checkpoint audit =====
print("\n===== 1. CHECKPOINTS =====")
for run,d in CKPTS.items():
    final=os.path.join(d,"checkpoint_final.pt")
    try:
        assert os.path.exists(final), "missing"
        m=ckmeta(final); m["path"]=final; A["runs"][run]=m
        print(run, json.dumps({k:m[k] for k in ("step","epoch","model_status","train_loss","val_loss","size_bytes")},default=str))
        chk(run+"_exists", True)
        chk(run+"_loadable", m["has_model_sd"] and m["has_opt_sd"])
    except Exception as e:
        A["runs"][run]={"error":repr(e)}; chk(run,e)

# ===== 2. run3 report =====
print("\n===== 2. RUN3 REPORT =====")
try:
    rep=json.load(open(R3REP,encoding="utf-8")); A["report"]=rep
    for k in ("rc","elapsed_s","gpu","start_step","final_step","final_epoch",
              "final_status","final_train_loss","final_val_loss","resume_from"):
        print(" ",k,"=",rep.get(k))
    chk("report_rc0",rep.get("rc")==0)
    chk("report_resume_src",rep.get("resume_from")==CKPTS["run2"]+"/checkpoint_final.pt",
        rep.get("resume_from"))
    chk("report_start_step_894",rep.get("start_step")==894)
    chk("report_final_step_1341",rep.get("final_step")==1341)
    chk("report_final_epoch_3",rep.get("final_epoch")==3)
    chk("md_exists",os.path.exists(R3MD))
except Exception as e:
    chk("report",False,repr(e))

# ===== 3. cross-run comparison =====
print("\n===== 3. COMPARISON =====")
exp={"run1":(447,1,5.8646,4.8492),"run2":(894,2,4.7238,4.4748),"run3":(1341,3,4.4259,4.2169)}
for run,(es,ee,tl,vl) in exp.items():
    m=A["runs"].get(run,{})
    ok=(m.get("step")==es and m.get("epoch")==ee
        and m.get("train_loss") is not None and m.get("val_loss") is not None)
    chk("cmp_"+run, ok,
        "step=%s epoch=%s tl=%s vl=%s"%(m.get("step"),m.get("epoch"),m.get("train_loss"),m.get("val_loss")))
    A["runs"][run]["matches_expected"]=ok

# ===== 4. resume chain =====
print("\n===== 4. RESUME CHAIN =====")
try:
    r2=A["runs"].get("run2",{}); r3=A["runs"].get("run3",{})
    chk("chain_step_continuity", r3.get("step",0)>r2.get("step",0),
        "%s -> %s"%(r2.get("step"),r3.get("step")))
    chk("chain_epoch_progression", r3.get("epoch",0)>r2.get("epoch",0),
        "%s -> %s"%(r2.get("epoch"),r3.get("epoch")))
    # loss monotonic-ish (informational, not hard gate)
    A["notes"].append("loss trend run1->3 train: %.4f -> %.4f -> %.4f"%(
        A["runs"]["run1"]["train_loss"],A["runs"]["run2"]["train_loss"],A["runs"]["run3"]["train_loss"]))
    A["notes"].append("val trend: %.4f -> %.4f -> %.4f"%(
        A["runs"]["run1"]["val_loss"],A["runs"]["run2"]["val_loss"],A["runs"]["run3"]["val_loss"]))
except Exception as e: chk("chain",False,repr(e))

# ===== 5. strict reload + param count =====
print("\n===== 5. MODEL VERIFY =====")
try:
    from nexusai_core_01.config.model_config import NexusAICore01Config
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    cfg=NexusAICore01Config(); m=NexusAICore01(cfg)
    ck=torch.load(CKPTS["run3"]+"/checkpoint_final.pt",map_location="cpu",weights_only=False)
    m.load_state_dict(ck["model_state_dict"],strict=True)
    chk("strict_reload_r3",True,"params=%d"%m.count_parameters())
    tok=NexusAITokenizer(TOK,cfg); chk("tokenizer_vocab",tok.get_vocab_size()==8000)
    del m
except Exception as e: chk("model_verify",False,repr(e))

# ===== verdict =====
fails=[k for k,v in A["checks"].items() if v["status"]=="FAIL"]
A["verdict"]="AUDIT_PASS" if not fails else "ISSUES:"+str(fails)
ts=datetime.now().strftime("%Y%m%d_%H%M%S")
jp=os.path.join(REPORTS,"run3_audit_%s.json"%ts)
json.dump(A,open(jp,"w",encoding="utf-8"),indent=1,ensure_ascii=False)
md=["# Run3 Forensic Audit","", "verdict: **%s**"%A["verdict"],"",
    "## Runs"]
for r,m in A["runs"].items():
    md.append("- **%s**: step=%s epoch=%s tl=%s vl=%s size=%sB sha=%s"%(
        r,m.get("step"),m.get("epoch"),m.get("train_loss"),m.get("val_loss"),
        m.get("size_bytes"),str(m.get("sha256"))[:16]))
md+=["","## Checks"]+ ["- %s %s | %s"%(v["status"],k,v["detail"][:100]) for k,v in A["checks"].items()]
mp=jp.replace(".json",".md"); open(mp,"w",encoding="utf-8").write("\n".join(md))
print("\n==== AUDIT:",A["verdict"],"====")
print("JSON ->",jp); print("MD   ->",mp)
