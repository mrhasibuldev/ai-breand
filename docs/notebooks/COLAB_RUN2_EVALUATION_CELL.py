# =============================================================================
# NEXUSAI CORE-01 — RUN2 ENGLISH EVALUATION CELL (READ-ONLY INFERENCE)
# Loads checkpoints/core01_english_run2/checkpoint_final.pt (step 894).
# NO training, NO checkpoint writes. Outputs -> evaluations/core01_english_run2/
# =============================================================================
import os, sys, json, math, time, hashlib
from datetime import datetime
import torch

AI_CORE   = "/content/nexusai/packages/ai-core"
MODELS    = os.path.join(AI_CORE, "models")
CKPT      = "/content/drive/MyDrive/NexusAI/checkpoints/core01_english_run2/checkpoint_final.pt"
TEST_JSON = os.path.join(AI_CORE, "data/english_first/english_test.json")
TOK_PATH  = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
OUT_DIR   = "/content/drive/MyDrive/NexusAI/evaluations/core01_english_run2"
os.makedirs(OUT_DIR, exist_ok=True)
for pp in (AI_CORE, MODELS):
    if pp not in sys.path: sys.path.insert(0, pp)

from nexusai_core_01.config.model_config import NexusAICore01Config, ModelStatus
from core01.transformer import NexusAICore01
from core01.tokenizer_interface import NexusAITokenizer

E = {"ts": datetime.now().isoformat(), "ckpt": CKPT, "sections": {}}
def note(sec,k,v): E["sections"].setdefault(sec,{})[k]=v

# ---------- 1. load + verify ----------
print("\n===== 1. MODEL LOAD =====")
cfg = NexusAICore01Config()
tok = NexusAITokenizer(TOK_PATH, cfg)
model = NexusAICore01(cfg)
ck = torch.load(CKPT, map_location="cpu", weights_only=False)
model.load_state_dict(ck["model_state_dict"], strict=True)
n_params = model.count_parameters()
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device).eval()
cfg.model_status = ModelStatus(ck.get("model_status","PRETRAINING_COMPLETED"))
note("model", {"params": n_params, "device": device, "status": cfg.model_status.value,
               "ckpt_step": ck.get("step"), "ckpt_epoch": ck.get("epoch"),
               "ckpt_train_loss": ck.get("train_loss"), "ckpt_val_loss": ck.get("val_loss"),
               "vocab": cfg.vocab_size, "max_len": cfg.max_len})
print("params:", n_params, "| status:", cfg.model_status.value,
      "| step:", ck.get("step"), "| device:", device)
assert n_params == 8_842_560, "param count mismatch"

# ---------- 2. test-set loss / perplexity (bounded sample) ----------
print("\n===== 2. TEST LOSS / PERPLEXITY =====")
try:
    docs = json.load(open(TEST_JSON, encoding="utf-8"))
    sample = docs[:200]                      # bounded subset, documented
    sp = tok.sp
    losses, ntok = [], 0
    with torch.no_grad():
        for d in sample:
            ids = sp.encode(d["text"], out_type=int)
            ids = ids[:cfg.max_len]
            if len(ids) < 8: continue
            x = torch.tensor([ids[:-1]], device=device)
            y = torch.tensor([ids[1:]], device=device)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
                logits = model(x)
            loss = torch.nn.functional.cross_entropy(
                logits.reshape(-1, cfg.vocab_size).float(), y.reshape(-1), reduction="mean")
            losses.append(float(loss)); ntok += len(ids)-1
    avg = sum(losses)/len(losses)
    ppl = math.exp(min(avg, 20))
    note("test_loss", {"docs_used": len(losses), "of_total": len(docs),
                       "method": "teacher-forced CE, 512-token prefix, fp16 autocast" if device=="cuda" else "teacher-forced CE",
                       "mean_loss": round(avg,4), "perplexity": round(ppl,2), "tokens": ntok})
    print("test mean_loss=%.4f ppl=%.2f (n=%d docs)" % (avg, ppl, len(losses)))
except Exception as e:
    note("test_loss", {"error": repr(e)}); print("test loss failed:", repr(e))

# ---------- 3. generation evaluation ----------
print("\n===== 3. GENERATION =====")
PROMPTS = [
 # factual / knowledge
 "What is the capital of France?",
 "What is the largest planet in the solar system?",
 "Who wrote the book Romeo and Juliet?",
 "What is the chemical symbol for water?",
 "What year did World War II end?",
 # math
 "What is 15 plus 27?",
 "What is 7 times 8?",
 "If a train travels 60 miles in one hour, how far does it go in 3 hours?",
 "What is 100 divided by 4?",
 "What is 12 minus 5?",
 # reasoning / comprehension
 "If today is Monday, what day is it tomorrow?",
 "Which is heavier: a kilogram of steel or a kilogram of feathers?",
 "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
 "What comes next in the sequence: 2, 4, 6, 8, ?",
 "Is the statement 'All birds can fly' always true?",
 # conversation / everyday
 "Hello, how are you?",
 "What is your name?",
 "Can you help me write a thank you note?",
 "What should I eat for a healthy breakfast?",
 "Tell me a short story about a cat.",
 # english comprehension
 "Read this sentence and answer: 'The cat sat on the mat because it was tired.' Why did the cat sit on the mat?",
 "What is the main idea of a story about a lost dog finding its way home?",
 "What does the word 'brave' mean?",
 # open-ended
 "Explain what artificial intelligence is in one sentence.",
 "What are three benefits of exercise?",
 "Describe the weather in winter.",
 "What is the difference between a virus and a bacterium?",
 "Give me one tip for learning English.",
]

CONFIGS = [
 ("greedy",      dict(do_sample=False)),
 ("temp0.8_topk50", dict(do_sample=True, temperature=0.8, top_k=50)),
]

def rep_rate(text):
    w = text.split()
    if len(w) < 4: return 0.0
    return 1 - len(set(w))/len(w)

def is_gibberish(text):
    letters = [c for c in text if c.isalpha()]
    if not letters: return True
    vowels = sum(c.lower() in "aeiou" for c in letters)
    return vowels/len(letters) < 0.15 or len(set(text.split())) <= 2 and len(text)>30

results = []
samples_md = []
for cfgname, kw in CONFIGS:
    for i, prompt in enumerate(PROMPTS):
        t0=time.time()
        try:
            ids = tok.encode(prompt, add_special_tokens=True)
            x = torch.tensor([ids], dtype=torch.long, device=device)
            with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
                out = model.generate(x, max_new_tokens=64,
                                     temperature=kw.get("temperature"),
                                     top_k=kw.get("top_k"),
                                     top_p=kw.get("top_p"),
                                     do_sample=kw["do_sample"])
            gen_ids = out[0].cpu().tolist()[len(ids):]
            text = tok.decode(gen_ids, skip_special_tokens=True).strip()
        except Exception as e:
            text = ""; note("gen_errors", cfgname+"_"+str(i), repr(e))
        lat = time.time()-t0
        results.append({"config":cfgname,"idx":i,"prompt":prompt,"response":text,
                        "latency_s":round(lat,2),"rep_rate":round(rep_rate(text),3),
                        "empty":not bool(text.strip()),"gibberish":is_gibberish(text),
                        "n_tokens":len(text.split())})
        if cfgname=="greedy":
            samples_md.append("### Q%d: %s\n\n**Prompt:** %s\n\n**Response:** %s\n" % (i+1,prompt,prompt,text))
    print("config",cfgname,"done")

note("generation", {"configs": list(CONFIGS and [c[0] for c in CONFIGS]),
                    "n_prompts": len(PROMPTS), "max_new_tokens": 64,
                    "results": results})
# aggregate metrics per config
agg={}
for c in CONFIGS:
    rs=[r for r in results if r["config"]==c[0]]
    agg[c[0]]={"n":len(rs),
               "empty_rate":round(sum(r["empty"] for r in rs)/len(rs),3),
               "gibberish_rate":round(sum(r["gibberish"] for r in rs)/len(rs),3),
               "mean_rep_rate":round(sum(r["rep_rate"] for r in rs)/len(rs),3),
               "mean_latency_s":round(sum(r["latency_s"] for r in rs)/len(rs),2)}
note("generation_metrics", agg)
print(json.dumps(agg,indent=1))

# ---------- 4. save outputs ----------
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
json.dump(E, open(os.path.join(OUT_DIR,"eval_%s.json"%ts),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
md = ["# NexusAI Core-01 Run2 Evaluation","","Checkpoint: `%s`"%CKPT,
      "Step %s | epoch %s | status %s"%(ck.get("step"),ck.get("epoch"),ck.get("model_status")),
      "Params: %d | device: %s"%(n_params,device),"",
      "## Aggregate metrics","```json",json.dumps(agg,indent=1),"```","",
      "## Greedy samples","".join(samples_md)]
open(os.path.join(OUT_DIR,"eval_%s.md"%ts),"w",encoding="utf-8").write("\n".join(md))
open(os.path.join(OUT_DIR,"samples_%s.txt"%ts),"w",encoding="utf-8").write(
    "\n\n".join("Q: %s\nA: %s"%(r["prompt"],r["response"]) for r in results if r["config"]=="greedy"))
print("\noutputs ->",OUT_DIR)
print("DONE — evaluation only, no training")
