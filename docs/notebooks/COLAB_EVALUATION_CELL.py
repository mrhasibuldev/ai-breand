# =============================================================================
# NEXUSAI CORE-01 — POST-TRAINING EVALUATION CELL (Google Colab)
# Run ONLY after full training produces checkpoint_final.pt.
# Honest neural-output evaluation — NO hardcoded answer handlers.
# =============================================================================
import os, sys, json, glob, math
from datetime import datetime
import torch

AI_CORE = "/content/nexusai/packages/ai-core"
DRIVE_FULL = "/content/drive/MyDrive/NexusAI/checkpoints_full"
REPORT_DIR = "/content/drive/MyDrive/NexusAI/audit_reports"
TOK = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
os.makedirs(REPORT_DIR, exist_ok=True)

for pp in (AI_CORE, os.path.join(AI_CORE, "models")):
    if pp not in sys.path: sys.path.insert(0, pp)
from nexusai_core_01.config.model_config import NexusAICore01Config
from core01.transformer import NexusAICore01
from core01.tokenizer_interface import NexusAITokenizer
from core01.inference import InferenceEngine

cfg = NexusAICore01Config()
tok = NexusAITokenizer(TOK, cfg)

# ---- locate checkpoint ----
final = os.path.join(DRIVE_FULL, "checkpoint_final.pt")
if not os.path.exists(final):
    cands = sorted(glob.glob(os.path.join(DRIVE_FULL, "checkpoint_*.pt")))
    final = cands[-1] if cands else None
assert final, "no trained checkpoint found"
ck = torch.load(final, map_location="cpu", weights_only=False)
print("ckpt:", os.path.basename(final), "| step:", ck.get("step"),
      "| status:", ck.get("model_status"))

model = NexusAICore01(cfg)
model.load_state_dict(ck["model_state_dict"], strict=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
infer = InferenceEngine(model, tok, cfg, device=device)

# ---- fixed eval set (NOT from training data) ----
EVAL = [
    ("en_qa", "The capital of France is"),
    ("en_reason", "If today is Monday, tomorrow is"),
    ("en_math", "Two plus two equals"),
    ("bn_question", "বাংলাদেশের mambo niyog kothay?"),
    ("banglish", "ami bhate pari je tumi ekta khub bhalo bondhu"),
    ("identity", "Who created you?"),
    ("mixed", "Hello, apni kemon achen?"),
]

results = []
for tag, prompt in EVAL:
    try:
        out = infer.generate(prompt, max_new_tokens=40, do_sample=False)
        results.append({"tag": tag, "prompt": prompt, "output": out})
        print("\n[%s] PROMPT: %s\nOUT: %s" % (tag, prompt, out))
    except Exception as e:
        results.append({"tag": tag, "prompt": prompt, "error": repr(e)})
        print("[%s] FAILED: %r" % (tag, e))

# ---- loss metrics from checkpoint metadata ----
metrics = {"final_step": ck.get("step"), "epoch": ck.get("epoch"),
           "train_loss": ck.get("train_loss"), "val_loss": ck.get("val_loss"),
           "model_status": ck.get("model_status")}
if metrics.get("val_loss") and metrics.get("train_loss"):
    metrics["perplexity_est"] = round(math.exp(min(metrics["val_loss"], 20)), 2)

# ---- repetition heuristic ----
for r in results:
    if "output" in r:
        words = r["output"].split()
        r["unique_ratio"] = round(len(set(words))/max(1,len(words)), 2)
        r["repetitive"] = r["unique_ratio"] < 0.4

REPORT = {"ts": datetime.now().isoformat(), "checkpoint": final,
          "metrics": metrics, "generations": results,
          "honesty_note": "Raw neural outputs only — no deterministic handlers. "
                          "Bengali/Banglish quality expected WEAK (English-only corpus)."}
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out = os.path.join(REPORT_DIR, "eval_%s.json" % ts)
json.dump(REPORT, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\n==== EVAL REPORT ====\nmetrics:", metrics, "\nreport ->", out)
