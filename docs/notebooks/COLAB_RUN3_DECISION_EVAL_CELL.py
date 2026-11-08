# =============================================================================
# NEXUSAI CORE-01 — RUN3 DECISION-MAKING EVALUATION CELL (READ-ONLY)
# Tests decision/reasoning capability of run3 ckpt with rubric scoring.
# NO training, NO external judge. Rubric = hand-written expected signals.
# Output -> evaluations/core01_english_run3_decision/<ts>/{json,md,txt}
# =============================================================================
import os, sys, json, time, re
from datetime import datetime
import torch

AI_CORE = "/content/nexusai/packages/ai-core"
MODELS  = os.path.join(AI_CORE,"models")
CKPT    = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english_run3/checkpoint_final.pt"
TOK     = os.path.join(AI_CORE,"data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
OUT_DIR = "/content/drive/MyDrive/NexusAI/evaluations/core01_english_run3_decision"
os.makedirs(OUT_DIR, exist_ok=True)
for pp in (AI_CORE, MODELS):
    if pp not in sys.path: sys.path.insert(0,pp)

from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
from core01.transformer import NexusAICore01
from core01.tokenizer_interface import NexusAITokenizer

cfg = NexusAICore01Config()
tok = NexusAITokenizer(TOK, cfg)
model = NexusAICore01(cfg)
ck = torch.load(CKPT, map_location="cpu", weights_only=False)
model.load_state_dict(ck["model_state_dict"], strict=True)
model = model.to("cuda" if torch.cuda.is_available() else "cpu").eval()
cfg.model_status = ModelStatus(ck.get("model_status","PRETRAINING_COMPLETED"))
print("loaded run3 ckpt | step", ck.get("step"), "| params", model.count_parameters(),
      "| device", next(model.parameters()).device)

# ---------- test suite: (category, prompt, expected_substrings_any, must_not_have) ----------
TESTS = [
 # A. simple binary decisions
 ("A_binary", "Choose one: is the sky blue or green? Answer with one word.", ["blue"], ["green"]),
 ("A_binary", "Is ice hot or cold? Answer with one word.", ["cold"], ["hot"]),
 ("A_binary", "Which is bigger: an elephant or a mouse? One word answer.", ["elephant"], ["mouse"]),
 ("A_binary", "Do fish live in water or in fire? One word.", ["water"], ["fire"]),
 # B. criteria comparison
 ("B_compare", "Two phones: Phone A costs $200 with 64GB storage, Phone B costs $350 with 256GB. If I need lots of storage and have $400, which should I choose? Answer briefly.", ["b","256","350"], []),
 ("B_compare", "Job A pays $50,000 and is 10 minutes away. Job B pays $55,000 but is 2 hours away. I value free time. Which job fits me better? Answer briefly.", ["a","closer","time"], []),
 # C. arithmetic / logic decisions
 ("C_math", "What is 25 + 37?", ["62"], []),
 ("C_math", "What is 144 divided by 12?", ["12"], []),
 ("C_logic", "All roses are flowers. Some flowers fade quickly. Can we conclude all roses fade quickly? Answer yes or no and why briefly.", ["no","not","cannot","can't"], ["yes, all roses"]),
 # D. multi-step
 ("D_multistep", "I have 3 bags with 8 apples each. I eat 5 apples. How many apples remain?", ["19"], []),
 ("D_multistep", "A shop sells pens for $2 each. You buy 4 pens and pay with a $10 note. How much change do you get?", ["2"], []),
 # E. missing information -> should not decide
 ("E_missing", "Should I take job offer X or job offer Y?", ["more information","don't know","cannot","need","details","salary","which","ask"], []),
 ("E_missing", "Which restaurant is better, Mario's or Luigi's?", ["more information","depends","don't know","cannot","taste","location","need"], []),
 # F. contradiction detection
 ("F_contradict", "This rule says: 'All employees must work on Sundays.' Another rule says: 'No employee may work on Sundays.' What should I do?", ["conflict","contradict","impossible","clarify","ask","both cannot","rules conflict"], []),
 # G. constrained choice
 ("G_constraint", "Pick a dessert that is both vegan and has no nuts. Options: chocolate cake, fruit salad, peanut brownie.", ["fruit","salad"], ["cake","brownie"]),
 ("G_constraint", "Choose a vehicle that is electric and seats 7 people. Options: electric sedan (5 seats), electric minivan (7 seats), gas SUV (7 seats).", ["minivan","electric"], ["sedan","suv","gas"]),
 # H. justification
 ("H_justify", "Why is regular exercise good for health? Give two reasons.", ["heart","weight","energy","stress","muscle","health"], []),
 ("H_justify", "Why should you not touch a hot stove? Explain briefly.", ["burn","hot","injure","hurt","danger","fire"], []),
 # I. abstention / honesty
 ("I_abstain", "What is the capital of the country of Zzyzxq?", ["don't know","no such","not exist","cannot","don't have","unknown","fictional","made up"], []),
 ("I_abstain", "Who won the 2035 World Cup?", ["don't know","future","hasn't","cannot","not happened","unknown","yet"], []),
 # J. consistency pair (two prompts each asked twice -> compare verbatim)
 ("J_consistency", "Is it better to save money or spend it all immediately? Answer in one sentence.", ["save","depends","both"], []),
 ("J_consistency", "Should you apologize when you are wrong? Answer yes or no with one reason.", ["yes","apolog","sorry","respect","trust"], []),
]

def gen(prompt, max_new=64):
    ids = tok.encode(prompt, add_special_tokens=True)
    x = torch.tensor([ids], dtype=torch.long, device=model.device if hasattr(model,'device') else next(model.parameters()).device)
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=x.is_cuda):
        out = model.generate(x, max_new_tokens=max_new, do_sample=False)
    return tok.decode(out[0].cpu().tolist()[len(ids):], skip_special_tokens=True).strip()

def score(text, expected, forbidden):
    t = text.lower()
    hit = any(s.lower() in t for s in expected)
    forb = any(s.lower() in t for s in forbidden)
    return ("PASS" if hit and not forb else "FAIL"), hit, forb

results=[]; agg={}
t0=time.time()
for i,(cat,prompt,exp,forb) in enumerate(TESTS):
    try:
        resp = gen(prompt)
        st,hit,fbd = score(resp,exp,forb)
    except Exception as e:
        resp=""; st="ERROR"; hit=fbd=False
    results.append({"cat":cat,"prompt":prompt,"response":resp,"verdict":st,
                    "rubric_expected_any":exp,"rubric_forbidden":forb})
    a=agg.setdefault(cat,{"n":0,"pass":0,"fail":0,"error":0})
    a["n"]+=1; a["pass" if st=="PASS" else "fail" if st=="FAIL" else "error"]+=1
    print("[%s] %s -> %s | %s" % (st, cat, prompt[:50], resp[:70].replace("\n"," ")))

# consistency: repeat each J prompt once more, compare verbatim
j_prompts = [t[1] for t in TESTS if t[0]=="J_consistency"]
j_first  = {r["prompt"]: r["response"] for r in results if r["cat"]=="J_consistency"}
for p2 in j_prompts:
    try:
        r2 = gen(p2)
        consistency = (j_first.get(p2,"").strip().lower()==r2.strip().lower())
        agg["J_consistency"]["repeat_identical_%d"%j_prompts.index(p2)] = consistency
        print("consistency repeat identical:", consistency)
        results.append({"cat":"J_consistency","prompt":p2+" [repeat]","response":r2,"verdict":"INFO"})
    except Exception as e:
        agg["J_consistency"]["repeat_identical_%d"%j_prompts.index(p2)] = None

for cat,a in agg.items():
    a["pass_rate"]=round(a["pass"]/max(1,a["n"]),3)
E={"ts":datetime.now().isoformat(),"ckpt":CKPT,"ckpt_step":ck.get("step"),
   "params":model.count_parameters(),"elapsed_s":round(time.time()-t0,1),
   "method":"greedy decode, 64 tokens, rubric keyword scoring (no external judge)",
   "aggregate":agg,"results":results}
ts=datetime.now().strftime("%Y%m%d_%H%M%S")
sub=os.path.join(OUT_DIR,ts); os.makedirs(sub,exist_ok=True)
json.dump(E,open(os.path.join(sub,"decision_eval.json"),"w",encoding="utf-8"),indent=1,ensure_ascii=False)
json.dump(results,open(os.path.join(sub,"raw_samples.json"),"w",encoding="utf-8"),indent=1,ensure_ascii=False)
md=["# Core-01 Run3 Decision Evaluation","","step %s | params %d"%(ck.get("step"),model.count_parameters()),"",
    "## Aggregate","```json",json.dumps(agg,indent=1),"```","","## Limitations",
    "- Rubric = hand-written keyword matching; PASS means expected signal present, NOT verified reasoning.",
    "- Greedy decode only; consistency check uses verbatim repeat comparison.",
    "- Keyword match cannot distinguish genuine decision-making from pattern continuation.",
    "- No external judge used; qualitative judgment requires human review of samples.txt.","",
    "## Samples"]
for r in results:
    md.append("**[%s] %s**\n\n> %s\n\n%s\n"%(r["verdict"],r["cat"],r["prompt"],r["response"]))
open(os.path.join(sub,"decision_eval.md"),"w",encoding="utf-8").write("\n".join(md))
open(os.path.join(sub,"samples.txt"),"w",encoding="utf-8").write(
    "\n\n".join("[%s] %s\nQ: %s\nA: %s"%(r["verdict"],r["cat"],r["prompt"],r["response"]) for r in results))
print("\n==== DONE ===="); print("outputs ->",sub)
print(json.dumps(agg,indent=1))
