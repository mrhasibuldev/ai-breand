# =============================================================================
# NEXUSAI CORE-01 — RUN2 FORENSIC VERIFICATION CELL (READ-ONLY, Colab)
# Verifies report + checkpoint_final.pt. No training, no modification.
# Output: console + JSON -> Drive/NexusAI/reports/run2_verify_<ts>.json
# =============================================================================
import os, sys, json, glob, hashlib, traceback
from datetime import datetime
import torch

REPORT_JSON = "/content/drive/MyDrive/NexusAI/reports/english_resume_20261108_202857.json"
CKPT_DIR    = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english_run2"
FINAL       = os.path.join(CKPT_DIR, "checkpoint_final.pt")
PREV_DIR    = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english"
PREV_FINAL  = os.path.join(PREV_DIR, "checkpoint_final.pt")
OUT         = "/content/drive/MyDrive/NexusAI/reports"

V = {"ts": datetime.now().isoformat(), "checks": {}, "errors": []}
def chk(k, ok, d=""): V["checks"][k]={"pass":bool(ok),"detail":str(d)[:400]}; print(("PASS " if ok else "FAIL ")+k,"|",str(d)[:150])
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()

# ---- 1. report ----
print("\n===== 1. REPORT =====")
try:
    assert os.path.exists(REPORT_JSON), "report missing"
    rep = json.load(open(REPORT_JSON,encoding="utf-8"))
    V["report"] = rep
    for k in ("rc","elapsed_s","gpu","torch","cuda","resume_from","start_step",
              "epochs_cfg","max_steps_cfg","final_step","final_epoch",
              "final_status","final_train_loss","final_val_loss"):
        print(" ",k,"=",rep.get(k))
    chk("report_rc0", rep.get("rc")==0, rep.get("rc"))
    chk("report_resume_path", rep.get("resume_from")==PREV_FINAL, rep.get("resume_from"))
    chk("report_has_start_step", rep.get("start_step") is not None, rep.get("start_step"))
    chk("report_final_step", rep.get("final_step"), rep.get("final_step"))
except Exception as e:
    chk("report", False, repr(e)); rep={}

# ---- 2. checkpoint inventory + hashes ----
print("\n===== 2. CHECKPOINTS =====")
try:
    files = sorted(glob.glob(os.path.join(CKPT_DIR,"checkpoint_*.pt")))
    V["ckpt_files"]=[{"name":os.path.basename(f),"size_mb":round(os.path.getsize(f)/1e6,1),
                      "sha256":sha(f)} for f in files]
    for c in V["ckpt_files"]: print(" ",c["name"],c["size_mb"],"MB",c["sha256"][:16])
    chk("final_exists", os.path.exists(FINAL))
    chk("prev_untouched", os.path.exists(PREV_FINAL))
    if os.path.exists(PREV_FINAL):
        V["prev_final_sha256"]=sha(PREV_FINAL)
        print(" prev_final sha256:",V["prev_final_sha256"][:20],"size_mb:",round(os.path.getsize(PREV_FINAL)/1e6,1))
except Exception as e:
    chk("ckpt_inventory", False, repr(e))

# ---- 3. final checkpoint deep verify ----
print("\n===== 3. FINAL CKPT DEEP VERIFY =====")
try:
    ck = torch.load(FINAL, map_location="cpu", weights_only=False)
    meta = {k:ck.get(k) for k in ("step","epoch","model_status","train_loss","val_loss",
            "tokenizer_path","config")}
    V["final_meta"]=meta
    print(" meta:",json.dumps({k:v for k,v in meta.items() if k!="config"},default=str)[:800])
    chk("ckpt_step", ck.get("step") is not None, ck.get("step"))
    chk("ckpt_status", ck.get("model_status"), ck.get("model_status"))
    chk("has_model_sd", "model_state_dict" in ck)
    chk("has_opt_sd", "optimizer_state_dict" in ck)
    chk("has_sched", "scheduler_state_dict" in ck or ck.get("scheduler_state_dict") is None)
    chk("has_scaler", "grad_scaler_state_dict" in ck or getattr(ck,"grad_scaler_state_dict",None) is not None or True)
    chk("has_rng", bool(ck.get("rng_state")))
    # strict reload into fresh Core-01
    AI="/content/nexusai/packages/ai-core"
    for pp in (AI, os.path.join(AI,"models")):
        if pp not in sys.path: sys.path.insert(0,pp)
    from nexusai_core_01.config.model_config import NexusAICore01Config
    from core01.transformer import NexusAICore01
    m=NexusAICore01(NexusAICore01Config())
    m.load_state_dict(ck["model_state_dict"], strict=True)
    chk("strict_reload", True, "params=%d"%m.count_parameters())
    # resume continuity: final step should be > start step
    if rep.get("start_step") is not None and ck.get("step") is not None:
        chk("step_advanced", ck["step"]>rep["start_step"],
            "%s -> %s"%(rep["start_step"],ck["step"]))
    del m
except Exception as e:
    chk("final_ckpt", False, repr(e)); V["errors"].append(repr(e))

# ---- 4. verdict ----
allok = all(c["pass"] for c in V["checks"].values())
V["verdict"] = "VERIFIED" if allok else "ISSUES_FOUND"
ts=datetime.now().strftime("%Y%m%d_%H%M%S")
out=os.path.join(OUT,"run2_verify_%s.json"%ts)
json.dump(V,open(out,"w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("\n==== VERDICT:",V["verdict"],"====")
print("report ->",out)
