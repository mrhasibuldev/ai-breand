# =============================================================================
# NEXUSAI CORE-01 RUN4 — BOUNDED GPU SMOKE TEST CELL (REVIEW DRAFT v1.0)
# PURPOSE: verify GPU runtime path ONLY. NOT training. NOT a production checkpoint.
# Safe to insert as a NEW cell AFTER Cell 6 (upload/staging) in
#   docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb
# Hard limits: batch<=2, seq_len<=64, ONE forward, ONE backward, ONE optional
# scaler step on a THROWAWAY optimizer. Temp dir only. Never touches Drive
# checkpoints or the Run3/production artifacts.
# =============================================================================
import os, sys, json, glob, hashlib, zipfile, shutil, tempfile, time, re
import torch

CELL_VERSION = "RUN4_GPU_SMOKE_V1_0"
print("[CELL_VERSION]", CELL_VERSION)

RESULTS = []
def check(name, ok, detail="", status=None):
    st = status or ("PASS" if ok else "FAIL")
    RESULTS.append({"check": name, "status": st, "detail": str(detail)[:300]})
    print(f"[{st}] {name}: {detail}")
    return ok

def sha256_stream(path, limit=None):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk); n += len(chunk)
            if limit and n >= limit: break
    return h.hexdigest()

# ---------------------------------------------------------------- 1. GPU gate
if not torch.cuda.is_available():
    print("[BLOCKED] CUDA unavailable — GPU smoke test cannot run.")
    print(json.dumps({"status": "BLOCKED", "reason": "no_cuda"}, indent=2))
    raise SystemExit

dev = "cuda"
gpu_name = torch.cuda.get_device_name(0)
gpu_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
check("gpu_available", True, f"{gpu_name} | {gpu_mem_gb:.1f} GB")
if gpu_mem_gb < 4.0:
    print("[BLOCKED] GPU memory < 4GB — insufficient for smoke test.")
    raise SystemExit

fp16_ok = torch.cuda.is_bf16_supported() or True  # fp16 autocast supported on all modern CUDA
try:
    x = torch.ones(2, 2, device=dev, dtype=torch.float16)
    (x @ x).sum().item()
    fp16_ok = True
except Exception as e:
    fp16_ok = False
check("fp16_tensor_support", fp16_ok,
      "supported" if fp16_ok else "NOT_SUPPORTED", "PASS" if fp16_ok else "NOT_SUPPORTED")

# ------------------------------------------------- 2. locate verified assets
DRIVE_BASE = "/content/drive/MyDrive/NexusAI"
INNER_ZIP_SHA = "f91411e1ac2793c4c8c1a5b5b90c74c4409382a2933b3862e3bcb4d9bd82b4a5"
INNER_ZIP_SIZE = 299476
CKPT_SHA = "ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830"
CKPT_SIZE = 106777501

candidates = []
candidates += glob.glob(os.path.join(DRIVE_BASE, "**", "NEXUSAI_CORE01_RUN4_BUNDLE*.zip"), recursive=True)
candidates += glob.glob("/content/NEXUSAI_CORE01_RUN4_BUNDLE*.zip")
inner_zip = None
for c in candidates:
    if os.path.getsize(c) == INNER_ZIP_SIZE and sha256_stream(c) == INNER_ZIP_SHA:
        inner_zip = c; break
if not check("inner_bundle_verified", inner_zip is not None,
             inner_zip or "no verified inner bundle found on Drive/content"):
    raise SystemExit

ckpt_candidates = glob.glob(os.path.join(DRIVE_BASE, "**", "checkpoint_final.pt"), recursive=True)
ckpt_path = None
for c in ckpt_candidates:
    if "core01_english_run3" in c.replace("\\", "/") and \
       os.path.getsize(c) == CKPT_SIZE and sha256_stream(c) == CKPT_SHA:
        ckpt_path = c; break
if not check("run3_checkpoint_verified", ckpt_path is not None,
             ckpt_path or "no hash-verified Run3 checkpoint found"):
    raise SystemExit

# ------------------------------------------------------- 3. temp extraction
WORK = tempfile.mkdtemp(prefix="nexusai_gpu_smoke_")
print("[WORKDIR]", WORK)
try:
    seen_paths = set()
    with zipfile.ZipFile(inner_zip) as z:
        bad = z.testzip()
        if bad: raise RuntimeError(f"corrupt zip entry: {bad}")
        # extract ONLY code+tokenizer assets needed for smoke (small files)
        need_prefixes = ("packages/ai-core/core01/", "packages/ai-core/models/",
                         "packages/ai-core/data/experimental/phase9_2/tokenizers/")
        for info in z.infolist():
            raw = info.filename
            n = raw.replace("\\", "/")
            if n.startswith("/") or ".." in n.split("/") or "" in n.split("/"):
                raise RuntimeError(f"unsafe path in bundle: {raw}")
            if "\\" in raw or re.match(r"^[A-Za-z]:", raw):
                raise RuntimeError(f"unsafe path in bundle: {raw}")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise RuntimeError(f"symlink entry rejected: {raw}")
            norm = n.lstrip("/")
            if norm in seen_paths:
                raise RuntimeError(f"duplicate archive path: {raw}")
            seen_paths.add(norm)
            if n.startswith(need_prefixes):
                z.extract(info, WORK)
    ai_core = os.path.join(WORK, "packages", "ai-core")
    sys.path.insert(0, ai_core)
    sys.path.insert(0, os.path.join(ai_core, "models"))

    # sentencepiece dependency
    try:
        import sentencepiece  # noqa
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "sentencepiece"])

    from core01.transformer import NexusAICore01
    from core01.tokenizer_interface import NexusAITokenizer
    from nexusai_core_01.config.model_config import (
        NexusAICore01Config, ModelStatus)
    check("imports", True, "core01.transformer + tokenizer_interface + config")

    # ------------------------------------------------- 4. load checkpoint
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    # weights_only=False is REQUIRED: our own checkpoint holds numpy RNG +
    # optimizer state. Trust boundary: sha256 verified above before this load.
    cfg_dict = dict(ck["config"])
    if isinstance(cfg_dict.get("model_status"), str):
        cfg_dict["model_status"] = ModelStatus[cfg_dict["model_status"]]
    cfg_fields = {f for f in NexusAICore01Config.__dataclass_fields__}
    cfg = NexusAICore01Config(**{k: v for k, v in cfg_dict.items() if k in cfg_fields})
    check("config_built", cfg.vocab_size == 8000 and cfg.d_model == 256,
          f"vocab={cfg.vocab_size} d_model={cfg.d_model} layers={cfg.n_layers}")

    model = NexusAICore01(cfg)
    model.load_state_dict(ck["model_state_dict"], strict=True)
    n_params = sum(p.numel() for p in model.parameters())
    check("strict_state_dict_load", True,
          f"{n_params:,} params loaded strict=True (expected ~8,842,560)")

    tok_path = os.path.join(ai_core, "data", "experimental", "phase9_2",
                            "tokenizers", "bpe_8k", "sp_bpe_8k.model")
    tok = NexusAITokenizer(tok_path, cfg)
    ids_en = tok.encode("Hello, how are you?")
    ids_bn = tok.encode("আপনি কেমন আছেন?")
    check("tokenizer_encode", len(ids_en) > 2 and len(ids_bn) > 2,
          f"en_ids={len(ids_en)} bn_ids={len(ids_bn)} vocab={tok.get_vocab_size()}")

    model.to(dev).train()
    torch.manual_seed(42)

    # ------------------------------------------- 5. bounded forward pass
    BATCH, SEQ = 2, 32   # hard limits — far below training batch (8x~500)
    vocab = cfg.vocab_size
    input_ids = torch.randint(2, vocab, (BATCH, SEQ), device=dev)
    pad_id = cfg.pad_id
    input_ids[:, -4:] = pad_id  # exercise padding path
    attn = (input_ids != pad_id).long()

    t0 = time.time()
    with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=fp16_ok):
        logits = model(input_ids, attention_mask=attn)
    fwd_ms = (time.time() - t0) * 1000
    ok_shape = tuple(logits.shape) == (BATCH, SEQ, vocab)
    ok_finite = torch.isfinite(logits.float()).all().item()
    check("forward_pass", ok_shape and ok_finite,
          f"logits{tuple(logits.shape)} finite={ok_finite} {fwd_ms:.0f}ms")
    if not (ok_shape and ok_finite):
        raise RuntimeError("forward pass failed")

    # ------------------------------------- 6. backward + grad validation
    # Manual causal-LM loss: predict token t+1 from logits at t.
    labels = input_ids[:, 1:]
    pred = logits[:, :-1, :].float()
    loss = torch.nn.functional.cross_entropy(
        pred.reshape(-1, vocab), labels.reshape(-1), ignore_index=pad_id)
    check("loss_finite", torch.isfinite(loss).item(), f"loss={loss.item():.4f}")

    loss.backward()
    grads = [p.grad for p in model.parameters() if p.grad is not None]
    finite_grads = all(torch.isfinite(g.float()).all().item() for g in grads)
    n_with_grad = len(grads)
    total_params = sum(1 for _ in model.parameters())
    check("backward_grads", finite_grads and n_with_grad == total_params,
          f"{n_with_grad}/{total_params} tensors have finite grads")
    if not (finite_grads and n_with_grad == total_params):
        raise RuntimeError("backward/gradient validation failed")

    # grad clipping smoke (matches config grad_clip=1.0)
    torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
    check("grad_clip", True, f"max_norm<= {cfg.grad_clip}")

    # -------------------------------------- 7. FP16/GradScaler verification
    if fp16_ok:
        try:
            from torch.amp import GradScaler
            scaler = GradScaler(device="cuda")
            opt = torch.optim.AdamW(model.parameters(), lr=1e-5)
            model.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits2 = model(input_ids, attention_mask=attn)
            loss2 = torch.nn.functional.cross_entropy(
                logits2[:, :-1, :].float().reshape(-1, vocab),
                labels.reshape(-1), ignore_index=pad_id)
            scaler.scale(loss2).backward()
            scaler.unscale_(opt)
            gn = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
            # ONE bounded step on a THROWAWAY optimizer — checkpoint untouched
            scaler.step(opt); scaler.update()
            model.zero_grad(set_to_none=True)
            check("fp16_gradscaler", torch.isfinite(loss2).item(),
                  f"scaled backward+step OK, grad_norm={gn:.3f}")
        except Exception as e:
            check("fp16_gradscaler", False, f"FAIL: {e}")
    else:
        check("fp16_gradscaler", None, "GPU/torch lacks fp16 — NOT_SUPPORTED",
              status="NOT_SUPPORTED")

    # ------------------------------------- 8. save/reload verification
    sd_path = os.path.join(WORK, "smoke_state_dict.pt")
    torch.save(model.state_dict(), sd_path)
    model2 = NexusAICore01(cfg)
    model2.load_state_dict(torch.load(sd_path, map_location="cpu",
                                    weights_only=True), strict=True)
    same = all(torch.equal(model2.state_dict()[k].cpu(),
                           model.state_dict()[k].cpu())
               for k in model.state_dict())
    check("save_reload_state_dict", same and os.path.getsize(sd_path) > 1_000_000,
          f"state_dict roundtrip identical, {os.path.getsize(sd_path):,} bytes")
    if not same:
        raise RuntimeError("save/reload mismatch")

    peak_mb = torch.cuda.max_memory_allocated() / 1e6
    check("gpu_memory_peak", peak_mb < 6000, f"peak={peak_mb:.0f} MB (<6000 limit)")

finally:
    # ------------------------------------------------------- 9. cleanup
    del model, logits, loss
    try:
        import gc; gc.collect()
    except Exception:
        pass
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    shutil.rmtree(WORK, ignore_errors=True)
    print("[CLEANUP] temp dir removed, GPU cache cleared")

# ------------------------------------------------------------------ verdict
fails = [r for r in RESULTS if r["status"] == "FAIL"]
nots = [r for r in RESULTS if r["status"] == "NOT_SUPPORTED"]
print("\n===== GPU SMOKE SUMMARY =====")
for r in RESULTS:
    print(f"  {r['status']:14} {r['check']}: {r['detail']}")
verdict = "FAIL" if fails else ("PASS_WITH_NOT_SUPPORTED" if nots else "PASS")
print(f"\nSMOKE_RESULT: {verdict}")
print("TRAINING_STARTED: False | TRAINING_AUTHORIZED: False | SMOKE_ONLY: True")
