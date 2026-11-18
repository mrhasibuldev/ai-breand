# =============================================================================
# NEXUSAI CORE-01 — LOCAL EVALUATION SCRIPT (run3 checkpoint)
# Usage: place checkpoint_final.pt at MODELS_DIR/checkpoint_final.pt then:
#   python scripts/eval_core01_run3.py
# READ-ONLY inference. No training. Saves JSON+MD report.
# =============================================================================
import os, sys, json, math, time
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_CORE = os.path.join(ROOT, "packages", "ai-core")
MODELS_DIR = os.path.join(AI_CORE, "models")
CKPT = os.path.join(MODELS_DIR, "checkpoints_core01_run3", "checkpoint_final.pt")
TOK_PATH = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
OUT_DIR = os.path.join(ROOT, "eval_reports", "core01_run3")
os.makedirs(OUT_DIR, exist_ok=True)

for pp in (AI_CORE, MODELS_DIR):
    if pp not in sys.path: sys.path.insert(0, pp)

from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
from core01.transformer import NexusAICore01
from core01.tokenizer_interface import NexusAITokenizer

print("loading ckpt:", CKPT)
assert os.path.exists(CKPT), "checkpoint missing — download run3 checkpoint_final.pt here first"
cfg = NexusAICore01Config()
tok = NexusAITokenizer(TOK_PATH, cfg)
model = NexusAICore01(cfg)
ck = torch.load(CKPT, map_location="cpu", weights_only=False)
model.load_state_dict(ck["model_state_dict"], strict=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device).eval()
cfg.model_status = ModelStatus(ck.get("model_status", "PRETRAINING_COMPLETED"))
print("params:", model.count_parameters(), "| step:", ck.get("step"),
      "| epoch:", ck.get("epoch"), "| status:", ck.get("model_status"),
      "| train_loss:", ck.get("train_loss"), "| val_loss:", ck.get("val_loss"),
      "| device:", device)

PROMPTS = [
 # English
 ("en","What is the capital of France?"),
 ("en","What is 15 plus 27?"),
 ("en","If a train travels 60 miles in one hour, how far in 3 hours?"),
 ("en","What comes next: 2, 4, 6, 8, ?"),
 ("en","Tell me a short story about a dog."),
 # Bengali
 ("bn","বাংলাদেশের রাজধানী কী?"),
 ("bn","২ যোগ ২ কত?"),
 ("bn","পানি কেন ভেজা হয়?"),
 # Banglish
 ("banglish","tumi kemon achho?"),
 ("banglish","ami akhon khabo, tumi ki bolba?"),
 # mixed
 ("mixed","Hello, আমি কীভাবে পড়াশোনা করব?"),
 # reasoning / decision
 ("reason","A bat and ball cost $1.10. Bat costs $1 more. Ball cost?"),
 ("reason","All birds can fly. Penguins are birds. Can penguins fly?"),
 ("decision","Choose: cheap but slow laptop or expensive fast laptop. I need speed for work."),
 ("abstain","What is the capital of Zzyzxq?"),
]

def gen(prompt, max_new=64):
    ids = tok.encode(prompt, add_special_tokens=True)
    x = torch.tensor([ids], dtype=torch.long, device=device)
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
        out = model.generate(x, max_new_tokens=max_new, do_sample=False)
    return tok.decode(out[0].cpu().tolist()[len(ids):], skip_special_tokens=True).strip()

def rep_rate(t):
    w=t.split()
    return round(1-len(set(w))/len(w),3) if len(w)>=4 else 0.0

results=[]; t0=time.time()
for lang,p in PROMPTS:
    try: resp=gen(p)
    except Exception as e: resp=""; print("ERR",p,repr(e))
    results.append({"lang":lang,"prompt":p,"response":resp,"rep_rate":rep_rate(resp),
                    "empty":not bool(resp.strip()),"n_words":len(resp.split())})
    print("[%s] %s -> %s" % (lang,p[:40],resp[:80].replace("\n"," ")))

# test-set loss (bounded)
test_p = os.path.join(AI_CORE,"data/english_first/english_test.json")
test_loss={"note":"skipped"}
try:
    docs=json.load(open(test_p,encoding="utf-8"))[:200]
    losses=[]
    with torch.no_grad():
        for d in docs:
            ids=tok.sp.encode(d["text"],out_type=int)[:cfg.max_len]
            if len(ids)<8: continue
            x=torch.tensor([ids[:-1]],device=device); y=torch.tensor([ids[1:]],device=device)
            with torch.autocast(device_type="cuda",dtype=torch.float16,enabled=(device=="cuda")):
                logits=model(x)
            losses.append(float(torch.nn.functional.cross_entropy(
                logits.reshape(-1,cfg.vocab_size).float(),y.reshape(-1))))
    avg=sum(losses)/len(losses)
    test_loss={"docs":len(losses),"mean_loss":round(avg,4),"perplexity":round(math.exp(min(avg,20)),2)}
    print("test_loss",test_loss)
except Exception as e:
    test_loss={"error":repr(e)}

rep={"ts":time.strftime("%Y%m%d_%H%M%S"),"ckpt":CKPT,"ckpt_meta":{k:ck.get(k) for k in ("step","epoch","model_status","train_loss","val_loss")},
     "params":model.count_parameters(),"device":device,"elapsed_s":round(time.time()-t0,1),
     "method":"greedy 64 tokens, verbatim","test_loss":test_loss,"results":results}
ts=rep["ts"]
json.dump(rep,open(os.path.join(OUT_DIR,"eval_%s.json"%ts),"w",encoding="utf-8"),indent=1,ensure_ascii=False)
md=["# Core-01 Run3 Local Eval","","step %s epoch %s tl=%s vl=%s"%(ck.get("step"),ck.get("epoch"),ck.get("train_loss"),ck.get("val_loss")),
    "params %d | device %s"%(model.count_parameters(),device),"","## Samples"]
for r in results: md.append("**[%s]** %s\n\n> %s\n\n%s\n"%(r["lang"],r["prompt"],r["prompt"],r["response"]))
open(os.path.join(OUT_DIR,"eval_%s.md"%ts),"w",encoding="utf-8").write("\n".join(md))
print("\nDONE ->",OUT_DIR)
