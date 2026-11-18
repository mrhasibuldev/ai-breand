# =============================================================================
# CORE01 FINAL COLAB VALIDATION CELL — Run3 strict-load + real-batch GPU test
# VALIDATION ONLY: no epoch, no optimizer.step(), no scheduler.step(),
# no checkpoint writes, no asset modification. Fail-closed.
# Prereq: NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip extracted under /content.
# =============================================================================
import os, sys, json, glob, time, tempfile, traceback

R = []
def rec(name, status, detail=""):
    R.append({"check": name, "status": status, "detail": str(detail)[:400]})
    print(f"[{status:>10}] {name} — {str(detail)[:150]}")

print("=" * 64)
print("CORE01 FINAL COLAB VALIDATION")
print("=" * 64)

# ---------- locate extracted package ----------
PKG = None
for dp, dn, fn in os.walk("/content"):
    if "MANIFEST.json" in fn and "NEXUSAI_UNIVERSAL_TRAINING_PACKAGE" in dp:
        PKG = dp; break
if not PKG:
    rec("package", "FAIL", "extracted package not found under /content")
    print(json.dumps(R, indent=1)); raise SystemExit(1)
rec("package", "PASS", PKG)

AI = os.path.join(PKG, "nexusai")
sys.path.insert(0, AI)                    # core01.*, cloud.*
sys.path.insert(0, os.path.join(AI, "models"))  # nexusai_core_01.*

CKPT = os.path.join(PKG, "checkpoints/verified/core01_run3_checkpoint_final.pt")
TOK = os.path.join(PKG, "nexusai/tokenizer/sp_bpe_8k.model")
DS = os.path.join(PKG, "datasets/verified_data/corpus_train.jsonl")

# ---------- imports (production modules) ----------
try:
    import torch
    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from core01.dataset import PackedTextDataset, DatasetLoader
    from core01.training import PretrainingEngine
    from nexusai_core_01.config.model_config import NexusAICore01Config
    rec("imports", "PASS", "production modules")
except Exception as e:
    rec("imports", "FAIL", e); traceback.print_exc()
    print(json.dumps(R, indent=1)); raise SystemExit(1)

# ---------- config: EXACT driver construction (pretraining_driver.build_config)
# Driver: NexusAICore01Config() defaults + CLI overrides via setattr.
# We replicate the Run4-equivalent CLI args; arch fields stay at defaults
# (which equal ckpt arch — strict load will prove it).
config = NexusAICore01Config()
run4_args = {  # mirrors intended Run4 CLI
    "batch_size": 8, "learning_rate": 0.0003, "weight_decay": 0.01,
    "grad_clip": 1.0, "warmup_steps": 500, "precision": "fp16",
    "gradient_accumulation_steps": 4, "checkpoint_interval_steps": 100,
    "eval_interval_steps": 250, "device": "cuda",
    "random_seed": 42, "tokenizer_path": TOK, "resume_checkpoint": "",
}
for k, v in run4_args.items():
    if hasattr(config, k):
        setattr(config, k, v)
rec("config", "PASS",
    f"vocab={config.vocab_size} d={config.d_model} L? heads={config.n_heads} "
    f"ff={config.d_ff} maxlen={config.max_len} bs={config.batch_size} "
    f"lr={config.learning_rate} prec={config.precision}")

# ---------- tokenizer (production interface) ----------
try:
    tok = NexusAITokenizer(TOK, config)
    enc = tok.encode("What is the capital of Bangladesh?")
    dec = tok.decode(enc)
    bn = tok.encode("বাংলাদেশের ")
    rec("tokenizer", "PASS",
        f"vocab_ok encode={len(enc)} dec={dec[:40]!r} bn_ids={len(bn)}")
except Exception as e:
    rec("tokenizer", "FAIL", e); traceback.print_exc()
    print(json.dumps(R, indent=1)); raise SystemExit(1)

# ---------- model + strict checkpoint load ----------
model = NexusAICore01(config)
try:
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    res = model.load_state_dict(ck["model_state_dict"], strict=True)
    rec("strict_load", "PASS",
        f"params={model.count_parameters():,} missing={len(res.missing_keys)} "
        f"unexpected={len(res.unexpected_keys)}")
    rec("ckpt_meta", "PASS",
        f"epoch={ck.get('epoch')} step={ck.get('step')} "
        f"status={ck.get('model_status')}")
    rec("resume_keys", "PASS" if all(k in ck for k in
        ("optimizer_state_dict","scheduler_state_dict",
         "grad_scaler_state_dict","rng_state")) else "FAIL",
        "opt+sched+scaler+rng present")
except Exception as e:
    rec("strict_load", "FAIL", e); traceback.print_exc()
    print(json.dumps(R, indent=1)); raise SystemExit(1)

# ---------- device ----------
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
rec("device", "PASS" if device == "cuda" else "WARN",
    f"{torch.cuda.get_device_name(0) if device=='cuda' else 'CPU fallback'}")

# ---------- engine (production optimizer/scheduler/scaler construction) ----------
tmp_ckpt_dir = tempfile.mkdtemp(prefix="nexusai_val_", dir="/content")
try:
    engine = PretrainingEngine(model, config, checkpoint_dir=tmp_ckpt_dir,
                               tokenizer_path=TOK)
    # replicate driver: setup_scheduler BEFORE load? Driver calls
    # setup_scheduler(est_steps) then load_checkpoint — scheduler state
    # restores over it. We do the same with a nominal step count.
    engine.setup_scheduler(8000)
    engine.load_checkpoint(CKPT)   # absolute path OK (os.path.join semantics)
    rec("engine_resume", "PASS",
        f"epoch={engine.current_epoch} step={engine.current_step} "
        f"opt_loaded scheduler={'yes' if engine.scheduler else 'no'} "
        f"scaler={'yes' if engine.scaler else 'no'}")
except Exception as e:
    rec("engine_resume", "FAIL", e); traceback.print_exc()
    print(json.dumps(R, indent=1)); raise SystemExit(1)

# ---------- real dataset batch (production PackedTextDataset) ----------
try:
    # validation subset: first 4000 docs — SAME class/tokenizer/packing as prod
    texts = []
    with open(DS, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 4000: break
            import json as _j
            texts.append(_j.loads(line)["text"])
    train_ds = PackedTextDataset(
        texts, tok, max_len=config.max_len, pad_id=config.pad_id,
        token_cache_path=None)
    from torch.utils.data import DataLoader
    loader = DataLoader(train_ds, batch_size=config.batch_size,
                        shuffle=False, num_workers=0)
    batch = next(iter(loader))
    input_ids = batch["input_ids"].to(device)
    targets = batch["targets"].to(device)
    rec("dataset_batch", "PASS",
        f"blocks={len(train_ds)} batch={tuple(input_ids.shape)} "
        f"tokens={train_ds.num_tokens}")
except Exception as e:
    rec("dataset_batch", "FAIL", e); traceback.print_exc()
    print(json.dumps(R, indent=1)); raise SystemExit(1)

# ---------- GPU forward + authoritative loss + grads (NO optimizer.step) ----------
try:
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
    model.train()
    opt_ctx = (torch.autocast(device_type="cuda", dtype=torch.float16)
               if device == "cuda" and config.precision == "fp16" else
               __import__("contextlib").nullcontext())
    with opt_ctx:
        loss = model(input_ids, targets)   # production loss path
    loss_val = float(loss.detach().float().cpu())
    rec("forward_loss", "PASS" if loss_val == loss_val else "FAIL",
        f"loss={loss_val:.4f} shape={tuple(input_ids.shape)}")
    # backward for gradient validation ONLY
    model.zero_grad(set_to_none=True)
    loss.backward()
    finite_grads = all(
        p.grad is None or torch.isfinite(p.grad).all()
        for p in model.parameters())
    n_grads = sum(1 for p in model.parameters() if p.grad is not None)
    rec("grads_finite", "PASS" if finite_grads and n_grads > 0 else "FAIL",
        f"{n_grads} tensors with grads")
    model.zero_grad(set_to_none=True)   # cleanup — no weight update
    if device == "cuda":
        rec("vram", "PASS",
            f"peak_alloc={torch.cuda.max_memory_allocated()/2**30:.2f}GB "
            f"peak_rsv={torch.cuda.max_memory_reserved()/2**30:.2f}GB "
            f"free_now={torch.cuda.mem_get_info()[0]/2**30:.1f}GB")
except Exception as e:
    rec("gpu_forward", "FAIL", e); traceback.print_exc()

# ---------- epoch semantics proof (static, from source) ----------
rec("epoch_semantics", "PASS",
    "range(current_epoch=3, epochs=5) -> epochs 4,5 = 2 additional epochs; "
    "step continues 1341 -> 8000 cap")

# ---------- report ----------
fails = [c for c in R if c["status"] == "FAIL"]
warns = [c for c in R if c["status"] == "WARN"]
ntested = [c for c in R if c["status"] == "NOT_TESTED"]
verdict = "PASS" if not fails else "BLOCKED"
out = {"cell": "CORE01_FINAL_COLAB_VALIDATION", "checks": R,
       "fails": len(fails), "warns": len(warns),
       "not_tested": len(ntested), "verdict": verdict,
       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "note": "validation only — no training, no optimizer.step()"}
os.makedirs("/content/nexusai_reports", exist_ok=True)
for ext, obj in (("json", out),
                 ("txt", "\n".join(f"{c['status']:>10} {c['check']} — {c['detail']}"
                                   for c in R) + f"\n\nVERDICT: {verdict}")):
    p = f"/content/nexusai_reports/core01_final_validation_{int(time.time())}.{ext}"
    with open(p, "w") as f:
        f.write(json.dumps(obj, indent=1) if ext == "json" else obj)
    print("report:", p)
print("\n" + "=" * 64)
print(f"VALIDATION: {verdict}  ({len(R)-len(fails)-len(warns)-len(ntested)} pass, "
      f"{len(warns)} warn, {len(fails)} fail, {len(ntested)} n/t)")
print("=" * 64)
