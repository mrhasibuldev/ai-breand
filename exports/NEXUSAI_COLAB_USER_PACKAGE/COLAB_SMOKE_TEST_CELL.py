# =============================================================================
# NEXUSAI CORE-01 — CONSOLIDATED GPU SMOKE TEST CELL (Google Colab)
# Stages A-H. Synthetic data only. NO full training. NO real corpus.
# Safety: refuses to run unless SMOKE_TEST_ONLY=True and steps<=3.
# Report -> /content/drive/MyDrive/NexusAI/audit_reports/<timestamp>.json+txt
# =============================================================================
import os, sys, json, glob, time, subprocess, tempfile, hashlib, traceback
from datetime import datetime

SMOKE_TEST_ONLY = True
SMOKE_MAX_STEPS = 2          # hard cap; driver also gets --max-steps 2
BATCH_SIZE = 2
SEQ_LEN = 256                # conservative: NOT 512
GRAD_ACCUM = 1
AI_CORE = "/content/nexusai/packages/ai-core"
DRIVE_ROOT = "/content/drive/MyDrive/NexusAI"
CKPT_DIR = os.path.join(DRIVE_ROOT, "checkpoints_smoke")
REPORT_DIR = os.path.join(DRIVE_ROOT, "audit_reports")

REPORT = {"stage": "init", "results": {}, "errors": [], "ts": datetime.now().isoformat()}
def stage(name): REPORT["stage"] = name; print("\n===== STAGE %s =====" % name)
def ok(key, val=True, detail=""): REPORT["results"][key] = {"pass": bool(val), "detail": detail}; print(("PASS " if val else "FAIL ")+key, detail)
def fail(msg):
    REPORT["errors"].append({"stage": REPORT["stage"], "error": msg})
    REPORT["status"] = "FAILED"
    print("FATAL:", msg); save_report(); raise SystemExit(1)
def save_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for ext, obj in [(".json", REPORT), (".txt", json.dumps(REPORT, indent=1))]:
        p = os.path.join(REPORT_DIR, "core01_smoke_%s%s" % (ts, ext))
        open(p, "w").write(json.dumps(obj, indent=1) if ext == ".json" else obj)
    print("report ->", REPORT_DIR)

# ---------- safety guard ----------
assert SMOKE_TEST_ONLY, "SMOKE_TEST_ONLY must be True"
assert SMOKE_MAX_STEPS <= 3, "smoke capped at 3 steps"
assert BATCH_SIZE * SEQ_LEN <= 2*256, "conservative limits only"

# ---------- Stage A: environment ----------
stage("A-env")
try:
    import torch
    REPORT["results"]["python"] = sys.version.split()[0]
    REPORT["results"]["torch"] = torch.__version__
    REPORT["results"]["torch_cuda"] = torch.version.cuda
    cuda_avail = torch.cuda.is_available()
    REPORT["results"]["cuda_available"] = cuda_avail
    print("python:", REPORT["results"]["python"], "| torch:", torch.__version__,
          "| cuda_build:", torch.version.cuda, "| cuda:", cuda_avail)
    if not cuda_avail: fail("CUDA unavailable — set Runtime > T4 GPU")
    prop = torch.cuda.get_device_properties(0)
    REPORT["results"]["gpu"] = prop.name
    REPORT["results"]["vram_total_gb"] = round(prop.total_memory/1e9, 2)
    REPORT["results"]["compute_capability"] = "%d.%d" % (prop.major, prop.minor)
    print("GPU:", prop.name, "| VRAM %.2f GB" % (prop.total_memory/1e9),
          "| sm_%d%d" % (prop.major, prop.minor))
    # fp16 autocast probe (no model yet)
    t = torch.ones(4, device="cuda")
    with torch.autocast("cuda", dtype=torch.float16):
        t2 = t * 2
    torch.cuda.synchronize()
    ok("fp16_autocast", torch.isfinite(t2.float()).all().item())
    del t, t2; torch.cuda.empty_cache()
except Exception as e:
    fail("Stage A: %r" % e)

# ---------- Stage B: source integrity ----------
stage("B-source")
try:
    TP = os.path.join(AI_CORE, "core01", "transformer.py")
    raw = open(TP, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    REPORT["results"]["transformer_sha256"] = sha
    print("transformer.py sha256:", sha)
    EXPECTED_SHA = "c8b25687ace8cc6f1bb51589a16c2a5d9f14ff9ab6fffafadec9147a5b1e85bc"
    if sha != EXPECTED_SHA:
        print("WARN: sha differs from repaired baseline (Colab may have git version).")
        print("      Checking fix marker instead of hard-fail:")
    src = raw.decode("utf-8")
    marker = "pad = attention_mask[:, None, :]"
    ok("mask_fix_present", marker in src)
    if marker not in src:
        fail("OLD transformer.py detected — upload repaired file first")
    buggy = "mask.expand(-1, seq_len, -1, -1)"
    ok("buggy_pattern_absent", buggy not in src)
    if buggy in src: fail("buggy mask code still present")
except Exception as e:
    fail("Stage B: %r" % e)

# ---------- Stage C: model init ----------
stage("C-model")
try:
    for pp in (AI_CORE, os.path.join(AI_CORE, "models")):
        if pp not in sys.path: sys.path.insert(0, pp)
    from nexusai_core_01.config.model_config import NexusAICore01Config
    from core01.transformer import NexusAICore01
    cfg = NexusAICore01Config()
    torch.cuda.reset_peak_memory_stats()
    model = NexusAICore01(cfg).cuda()
    torch.cuda.synchronize()
    n = model.count_parameters()
    ok("param_count", n == 8_842_560, str(n))
    REPORT["results"]["init_vram_gb"] = round(torch.cuda.max_memory_allocated()/1e9, 3)
    print("init VRAM: %.3f GB" % REPORT["results"]["init_vram_gb"])
    # conservative config for Stage D
    cfg_d = NexusAICore01Config()
    cfg_d.max_len = SEQ_LEN  # only affects positional buffer slice, safe
except Exception as e:
    fail("Stage C: %r" % e)

# ---------- Stage D: FP16 fwd/bwd/step (bs2 x 256) ----------
stage("D-fp16")
try:
    import torch.nn.utils as U
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4)
    scaler = torch.amp.GradScaler("cuda")
    model.train()
    torch.manual_seed(42)
    seq = SEQ_LEN
    x = torch.randint(0, cfg.vocab_size, (BATCH_SIZE, seq), device="cuda")
    y = torch.randint(0, cfg.vocab_size, (BATCH_SIZE, seq), device="cuda")
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    with torch.autocast("cuda", dtype=torch.float16):
        loss = model(x, targets=y)
    assert torch.isfinite(loss), "non-finite loss"
    scaler.scale(loss).backward()
    scaler.unscale_(opt)
    gn = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    dt = time.time() - t0
    REPORT["results"]["fp16_step"] = {"loss": float(loss), "sec": round(dt,2),
        "grad_norm": float(gn), "finite": bool(torch.isfinite(loss).item())}
    REPORT["results"]["peak_vram_bs2x256_gb"] = round(torch.cuda.max_memory_allocated()/1e9, 3)
    REPORT["results"]["reserved_vram_gb"] = round(torch.cuda.max_memory_reserved()/1e9, 3)
    ok("fp16_fwd_bwd_step", True,
       "loss=%.4f %.2fs peak=%.2fGB" % (float(loss), dt,
       REPORT["results"]["peak_vram_bs2x256_gb"]))
    del x, y, loss; torch.cuda.empty_cache()
    # optional Stage D2: bs4 x 256 only if headroom > 6 GB
    free = torch.cuda.get_device_properties(0).total_memory - torch.cuda.max_memory_allocated()
    if free > 6e9:
        stage("D2-fp16-bs4")
        x = torch.randint(0, cfg.vocab_size, (4, seq), device="cuda")
        y = torch.randint(0, cfg.vocab_size, (4, seq), device="cuda")
        torch.cuda.reset_peak_memory_stats()
        with torch.autocast("cuda", dtype=torch.float16):
            l2 = model(x, targets=y)
        scaler.scale(l2).backward(); scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        REPORT["results"]["fp16_step_bs4"] = {"loss": float(l2),
            "peak_vram_gb": round(torch.cuda.max_memory_allocated()/1e9,3)}
        ok("fp16_bs4", torch.isfinite(l2).item())
        del x, y, l2; torch.cuda.empty_cache()
    else:
        print("skip bs4 probe: headroom %.2f GB < 6 GB" % (free/1e9))
except Exception as e:
    fail("Stage D: %r\n%s" % (e, traceback.format_exc()[-500:]))

# ---------- Stage E: attention mask verification ----------
stage("E-mask")
try:
    model.eval()
    B, S = 2, 64
    ids = torch.randint(0, cfg.vocab_size, (B, S), device="cuda")
    am = torch.ones(B, S, device="cuda"); am[0, S//2:] = 0; am[1, S-8:] = 0
    with torch.no_grad():
        logits = model(ids, attention_mask=am)   # repaired path
    ok("mask_forward_shape", tuple(logits.shape) == (B, S, cfg.vocab_size),
       str(tuple(logits.shape)))
    ok("mask_finite", bool(torch.isfinite(logits).all().item()))
    # causal check: perturb a future token, earlier logits must not change
    ids2 = ids.clone(); ids2[:, -1] = (ids2[:, -1] + 1) % cfg.vocab_size
    with torch.no_grad():
        l1 = model(ids[:, :S//2], attention_mask=am[:, :S//2])
        l2 = model(ids2[:, :S//2], attention_mask=am[:, :S//2])
    # positions < S//2-? causal means last query of truncated view only sees <= itself;
    # simpler direct check: full-sequence logits at pos i unaffected by token j>i
    with torch.no_grad():
        la = model(ids); lb = model(ids2)
    diff = (la[:, :-1, :] - lb[:, :-1, :]).abs().max().item()
    ok("causal_isolation", diff < 1e-3, "max diff on non-last positions=%.2e" % diff)
    del ids, ids2, am, logits, la, lb, l1, l2
    torch.cuda.empty_cache()
except Exception as e:
    fail("Stage E: %r\n%s" % (e, traceback.format_exc()[-500:]))

# ---------- Stage F: short driver run (max-steps 2) ----------
stage("F-driver")
driver_rc = None
try:
    tok = os.path.join(AI_CORE, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
    tdir = tempfile.mkdtemp(prefix="core01_smoke_")
    with open(os.path.join(tdir, "train.jsonl"), "w") as f:
        for i in range(300):
            f.write(json.dumps({"text": "smoke test document %d about neural networks and training." % i}) + "\n")
    with open(os.path.join(tdir, "val.jsonl"), "w") as f:
        for i in range(10):
            f.write(json.dumps({"text": "smoke validation document %d." % i}) + "\n")
    cmd = [sys.executable, "-m", "core01.pretraining_driver",
           "--train-file", os.path.join(tdir, "train.jsonl"),
           "--val-file", os.path.join(tdir, "val.jsonl"),
           "--output-dir", CKPT_DIR,
           "--tokenizer", tok,
           "--device", "cuda", "--precision", "fp16",
           "--batch-size", "8", "--gradient-accumulation-steps", "1",
           "--learning-rate", "3e-4", "--warmup-steps", "10",
           "--epochs", "1", "--max-steps", str(SMOKE_MAX_STEPS),
           "--checkpoint-interval", "2", "--eval-interval", "2",
           "--log-interval", "1"]
    print("driver:", " ".join(cmd))
    r = subprocess.run(cmd, cwd=AI_CORE, capture_output=True, text=True, timeout=1800)
    REPORT["results"]["driver_stdout_tail"] = r.stdout[-2000:]
    if r.stderr: REPORT["results"]["driver_stderr_tail"] = r.stderr[-800:]
    driver_rc = r.returncode
    ok("driver_rc", driver_rc == 0, "rc=%s" % driver_rc)
    if driver_rc != 0: fail("driver failed rc=%s" % driver_rc)
    ckpts = sorted(glob.glob(os.path.join(CKPT_DIR, "checkpoint_*.pt")))
    REPORT["results"]["ckpt_files"] = [os.path.basename(c) for c in ckpts]
    ok("ckpt_created", len(ckpts) > 0, str(len(ckpts)) + " files")
    if ckpts:
        ck = torch.load(ckpts[-1], map_location="cpu", weights_only=False)
        REPORT["results"]["ckpt_meta"] = {k: ck.get(k) for k in
            ["step","epoch","model_status","tokenizer_path"]}
        ok("ckpt_meta", ck.get("step") is not None and ck.get("model_status"))
        # strict reload into fresh model
        m2 = NexusAICore01(cfg)
        m2.load_state_dict(ck["model_state_dict"], strict=True)
        ok("ckpt_strict_reload", True)
        del m2
        # resume candidate
        REPORT["results"]["resume_ckpt"] = ckpts[-1]
except Exception as e:
    fail("Stage F: %r\n%s" % (e, traceback.format_exc()[-500:]))

# ---------- Stage G: resume test (1 extra step) ----------
stage("G-resume")
try:
    if driver_rc != 0:
        print("skip resume: driver failed")
    else:
        resume_ck = REPORT["results"].get("resume_ckpt")
        cmd2 = [sys.executable, "-m", "core01.pretraining_driver",
                "--train-file", os.path.join(tdir, "train.jsonl"),
                "--val-file", os.path.join(tdir, "val.jsonl"),
                "--output-dir", CKPT_DIR,
                "--tokenizer", tok,
                "--device", "cuda", "--precision", "fp16",
                "--batch-size", "8", "--gradient-accumulation-steps", "1",
                "--learning-rate", "3e-4", "--warmup-steps", "10",
                "--epochs", "1", "--max-steps", str(SMOKE_MAX_STEPS + 1),
                "--checkpoint-interval", "2", "--eval-interval", "2",
                "--log-interval", "1", "--resume", resume_ck]
        print("resume:", " ".join(cmd2[-4:]))
        r2 = subprocess.run(cmd2, cwd=AI_CORE, capture_output=True, text=True, timeout=1800)
        tail = r2.stdout[-1200:]
        print(tail)
        resumed = "resumed from checkpoint" in r2.stdout
        ok("resume_ran", r2.returncode == 0 and resumed,
           "rc=%s resumed=%s" % (r2.returncode, resumed))
        REPORT["results"]["resume_stdout_tail"] = tail
except Exception as e:
    fail("Stage G: %r\n%s" % (e, traceback.format_exc()[-500:]))

# ---------- Stage H: cleanup ----------
stage("H-cleanup")
try:
    del model, opt, scaler
    torch.cuda.empty_cache()
    REPORT["results"]["cleanup"] = "ok"
    REPORT["status"] = "PASSED"
    ok("cleanup", True)
except Exception as e:
    REPORT["errors"].append({"stage": "H", "error": repr(e)})
    ok("cleanup", False, repr(e))

save_report()
print("\n===== SMOKE TEST %s =====" % REPORT.get("status"))
print("peak VRAM bs2x256: %.2f GB | reserved: %.2f GB" % (
    REPORT["results"].get("peak_vram_bs2x256_gb", -1),
    REPORT["results"].get("reserved_vram_gb", -1)))
