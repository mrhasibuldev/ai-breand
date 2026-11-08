# NEXUSAI_CORE01_PHASE4_1_CLOUD_GPU_FEASIBILITY_AUDIT

**Date**: 2026-11-06
**Type**: STRICT READ-ONLY — no downloads, no sessions, no training, no code changes
**Labels**: VERIFIED / ESTIMATED / ACCOUNT-DEPENDENT / NOT VERIFIED / REQUIRES APPROVAL

---

## 1. EXECUTIVE SUMMARY

- Core-01 verified: 8,842,560 params, UNTRAINED, ctx512, vocab8000 — matches all prior reports.
- **Local machine cannot train** (VERIFIED): no GPU, 4 CPU cores, 1.4GB free RAM, 4.8GB free disk.
- **Kaggle is the recommended free platform**: 2×T4 (16GB each), ~30 GPU-h/week, 12h sessions, 20GB persistent `/kaggle/working`. VERIFIED via official docs (as of Oct-Nov 2026 reporting).
- **Colab free is backup**: T4 when available, ~12h session, 90-min idle kill, no guaranteed GPU, dynamic quota. VERIFIED via official FAQ.
- **Code gap found**: training loop is FP32-only — no AMP/mixed-precision, no gradient accumulation, no multi-GPU (DDP). Single T4 is sufficient; 2×T4 would need code changes to exploit.
- **Time estimate revised downward**: previous 8-15h estimate was conservative. At ~53 MFLOPs/token and realistic T4 throughput, 45M training tokens ≈ **~1-4 hours FP32**, less with AMP. Needs an approved benchmark to confirm.
- Checkpoint size is tiny (~140MB each with optimizer state) — persistence is easy.

---

## 2. LOCAL HARDWARE LIMITATIONS — VERIFIED

| Resource | Actual | Training need | Verdict |
|---|---|---|---|
| GPU | none (torch 2.14.1+cpu, CUDA=False) | required | BLOCKED |
| RAM | 8.5GB total / 1.4GB free | 4-8GB | insufficient |
| Disk C: | 4.8GB free | corpus+ckpts | critical |
| Disk D: | 0.1GB free | — | unusable |
| CPU | 4 cores | — | diagnostic only |

## 3. KAGGLE FEASIBILITY — VERIFIED (official docs, recent)

| Item | Value | Label |
|---|---|---|
| Free GPU | 2× Tesla T4, 16GB each (P100 retired Sep 2026) | VERIFIED |
| Weekly quota | ~30 GPU-h (resets Sat UTC, "sometimes higher") | VERIFIED doc / ACCOUNT-DEPENDENT exact |
| Session | up to 12h | VERIFIED |
| Idle timeout | ~20 min interactive | VERIFIED |
| Persistent storage | 20GB `/kaggle/working` | VERIFIED |
| Internet | toggleable in settings | VERIFIED |
| Phone verification | required for GPU | VERIFIED |
| Payment info | NOT required for free tier | VERIFIED |
| Auto-charge | none on free tier | VERIFIED |
| Batch jobs via API/CLI | supported | VERIFIED |

## 4. GOOGLE COLAB FREE FEASIBILITY — VERIFIED (official FAQ)

| Item | Value | Label |
|---|---|---|
| GPU | T4 typical, sometimes K80; not guaranteed | VERIFIED/ACCOUNT-DEPENDENT |
| VRAM | 16GB (T4) | VERIFIED |
| Session | ~12h max, ~90min idle disconnect | VERIFIED |
| Quota | dynamic, unpublished (~100 compute units/mo reported) | ACCOUNT-DEPENDENT |
| Storage | ephemeral; Drive mount possible | VERIFIED |
| Payment | none for free tier | VERIFIED |
| Background execution | free tier = foreground only | VERIFIED |

## 5. OTHER PLATFORMS — brief

- **Lightning AI**: ~75 free T4-h (interruptible credits), 4h studio restart, 50GB persistent — viable 3rd option. VERIFIED (lightning.ai/pricing).
- **SageMaker Studio Lab**: CLOSED to new customers. VERIFIED.
- **Paperspace free**: old M4000/P4000 8GB, 12h shutdown — weaker than Kaggle. VERIFIED.

## 6. CORE-01 HARDWARE COMPATIBILITY — code inspection

| Capability | Status | Evidence |
|---|---|---|
| Single GPU (cuda) | WORKS — `device` param accepts "cuda", tensors `.to(device)` | training.py:160-201 |
| Mixed precision (AMP/FP16/BF16) | **NOT IMPLEMENTED** — pure FP32 loop | training.py train_epoch |
| Gradient accumulation | **NOT IMPLEMENTED** | — |
| Multi-GPU (DDP/DataParallel) | **NOT IMPLEMENTED** | — |
| Gradient clipping | implemented (grad_clip=1.0 config) | training.py:189 |
| LR warmup scheduler | implemented (LambdaLR) | training.py:150 |
| Checkpoint save/resume | implemented (model+opt+sched+epoch+step+losses+config+timestamp) | CheckpointManager |
| RNG state in checkpoint | **NOT saved** (minor — affects exact reproducibility) | TrainingCheckpoint fields |

**Implication**: single T4 works out-of-the-box in FP32. 2×T4 needs DDP code (not required — one T4 is enough). AMP would ~2× speed and halve VRAM but requires a small code addition (REQUIRES APPROVAL to modify).

## 7. GPU MEMORY ESTIMATES — ESTIMATED (theory, not measured)

Model: 8,842,560 params, d256, L6, H8, dff1024, vocab8000, seq512.

| Component | FP32 | With AMP (if added) |
|---|---|---|
| Weights | 35.4MB | 17.7MB |
| Gradients | 35.4MB | 17.7MB |
| AdamW m+v | 70.7MB | 70.7MB (FP32 master) |
| Static total | ~142MB | ~106MB |
| Activations @ batch16×seq512 | ~2-4GB (attn scores 16×8×512²×4B≈134MB/layer×6 + FFN intermediates) | ~half |
| **Total @ batch16** | **~3-4.5GB** | **~2-2.5GB** |

- batch 8: ~2GB | batch 16: ~3.5GB | batch 32: ~6GB — all fit 16GB T4 comfortably even FP32.
- CPU RAM on Kaggle: 29GB — dataset loading fine.

## 8. TRAINING-TIME ESTIMATE — ESTIMATED, needs benchmark

- FLOPs/token ≈ 6×8.84M ≈ 53 MFLOPs (fwd+bwd).
- Stage-2 plan: ~15M tokens × 3 epochs = 45M tokens → ~2,385 TFLOPs total.
- T4 FP32 realistic ~4-6 TFLOPS effective → **~110-165 GPU-hours**?? — NO, recompute: 2385/5 ≈ 477s... 

Corrected: 45e6 tokens × 53e6 FLOPs = 2.39e15 FLOPs = 2,385 TFLOPs. T4 FP32 peak 8.1, effective ~4 → ~600s ≈ **~10-30 min per epoch-equivalent**; total ≈ **~0.5-1.5h** realistic with overhead, call it **1-3h** to be safe. Previous 8-15h estimate was overly conservative.

- With AMP (if added): ~2× faster → under 1h likely.
- **REQUIRES APPROVAL**: a 50-100 step benchmark on Kaggle to measure real tokens/sec before committing to full run.

## 9. CHECKPOINT PERSISTENCE STRATEGY — RECOMMENDED

Checkpoint ~140MB (model+AdamW state, FP32). Plan:
- Save every ~30min AND every N steps to `/kaggle/working/ckpt/` (20GB persistent — holds ~100 checkpoints).
- Keep `latest.pt` + rolling `ckpt_step{N}.pt`; CheckpointManager already supports backup-on-save.
- After session: download `latest.pt` + manifest to local `models/nexusai_core_01/experiments/exp01/` (~140MB — fits in 4.8GB disk).
- Kaggle also offers dataset/output persistence via notebook output — supplementary.
- Colab alternative: download via browser or mount Drive (slower, less reliable for 140MB×N).

## 10. SESSION INTERRUPTION & RECOVERY — RECOMMENDED

- TrainingCheckpoint already stores epoch/step/losses/config; resume = load state dicts into fresh model+optimizer.
- Gap: RNG state not saved → resumed run won't be bit-identical; acceptable.
- Workflow: on restart, load latest checkpoint, continue from saved step. Documented in core01/README.

## 11. DATASET STORAGE STRATEGY — RECOMMENDED

- Download datasets **on Kaggle directly** (kernel internet on) → `/kaggle/working/data/` — avoids local 4.8GB disk limit entirely.
- Keep only `manifest.json` + token stats locally (~KB).
- Alternatively stream B-CORE subset via `datasets` streaming — no full 20.8GB download needed.

## 12. CLOUD-TO-LOCAL / FUTURE SELF-HOSTED GPU — PLANNED

- Hardware-independent parts: model config, tokenizer, dataset pipeline, checkpoint format (plain .pt dict), evaluation — all portable.
- CUDA-dependent: only `device="cuda"` string + `.to(device)` calls — portable by design.
- Migration path: train on Kaggle → download checkpoint → load on any future GPU machine with same PyTorch; architecture/tokenizer identical.
- Future minimum VRAM: 8GB is comfortable (batch16 AMP), 16GB ideal; even 6GB works at batch8.
- No platform lock-in: no Kaggle/Colab-specific APIs used in core01 code.

## 13. TECHNICAL BLOCKERS

1. Local disk (4.8GB) — corpus must live on Kaggle, not locally. VERIFIED.
2. No AMP in training loop — FP32 works but ~2× slower; adding AMP needs code approval. VERIFIED gap.
3. Free GPU availability not guaranteed at peak times — queue risk. ACCOUNT-DEPENDENT.
4. Banglish/reasoning data thin — quality ceiling regardless of compute. VERIFIED (Phase 3.1).
5. Kaggle account + phone verification required — owner action. REQUIRES APPROVAL/OWNER.

## 14. RISKS & LIMITATIONS

- Free-tier quotas change without notice; sessions die at 12h/idle.
- FP32-only training is slower; quality unaffected.
- Checkpoint resume works but RNG state absent → minor reproducibility gap.
- Model quality ceiling set by 8.84M params + ~15M tokens — realistic expectation: basic bilingual chat, not deep reasoning.

## 15. RECOMMENDED CLOUD PLATFORM

**Kaggle Notebooks** — primary. Reasons: documented 30 GPU-h/week, 2×T4, 12h sessions, 20GB persistent storage, phone-verify only, no payment info, batch API for reliability. Colab = backup. Lightning AI = third.

## 16. REQUIREMENTS BEFORE DATASET DOWNLOAD — REQUIRES APPROVAL

1. Owner approves Kaggle account creation + phone verification (owner must do this personally).
2. Owner approves dataset list from Phase 4 report (B-CORE sample, IndicTalk, alpaca_chat_bangla, GSM8K, Ayon128, optional Dolly).
3. Confirm download happens ON Kaggle (not local) to bypass disk limit.
4. Approve creating `data/corpus_v1/manifest.json` locally (metadata only).

## 17. REQUIREMENTS BEFORE MODEL TRAINING — REQUIRES APPROVAL

1. Corpus built + token stats verified (~15M tokens target).
2. Owner approves training config: pretrain Stage A, seq512, batch8-16, AdamW 3e-4, ~3 epochs, FP32 (or approve AMP code addition).
3. Owner approves Kaggle session start + checkpoint export to `models/nexusai_core_01/experiments/exp01/`.
4. Separate approval for SFT Stage B afterward.
5. No paid compute, no external uploads of private data, no production connection.

## 18. FINAL STOP CONDITION

**STOP.** No dataset downloaded, no session started, no GPU activated, no training run, no checkpoint created, no repo changes. Awaiting owner decision.
