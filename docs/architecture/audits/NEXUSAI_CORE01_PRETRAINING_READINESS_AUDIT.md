# NexusAI Core-01 — Pretraining Readiness Audit (Phase: Dataset + Training Plan)

**Date:** 2026-11-07
**Status:** READ-ONLY audit. No code modified, no downloads, no training, no GPU consumed.
**Model:** `nexusai-core-01` — 8,842,560 params, vocab 8,000, ctx 512, status UNTRAINED.
**Prerequisite verified by owner:** Kaggle T4 x2 GPU diagnostic PASSED (FP32/FP16/GradScaler/checkpoint).

---

## 1. Dataset Inventory (verified by filesystem scan + tokenizer-based token estimates)

| Corpus | Path | Size | Est. tokens | Language reality |
|---|---|---|---|---|
| Phase-7 combined corpus | `data/experimental/phase7/tokenizer_corpus/corpus_combined.txt` | 11.08 MB | ~3.23 M | **99.97% English**; Bengali = 31 lines / 3,066 Unicode chars (0.03%); 8.8% exact-duplicate lines |
| Phase-9 expanded corpus | `data/experimental/phase9/curated/corpus_expanded.txt` | 10.98 MB | ~3.29 M | Same profile: English Wikipedia-style text + 31 Bengali lines; 0% dup lines |
| Phase-9.2 combined corpus | `data/experimental/phase9_2/corpus/combined.txt` | 0.19 MB | ~0.04 M | Bengali chat/SFT texts (726 bn + 1111 en + 14 mixed per manifest) |
| Phase-9.2 bengali.txt | same dir | 0.06 MB | ~0.01 M | Bengali only — **tiny** |
| Phase-8 train.txt | `data/experimental/phase8/data/train.txt` | 0.97 MB | ~0.28 M | Legacy experiment data |
| Dolly-15k (cleaned) | `data/collected/cleaned/dolly/` | 12.85 MB | ~1.5 M words | Instruction data — SFT asset, not pretraining corpus. License CC BY-SA 3.0 (conditional, attribution+share-alike) |
| GSM8K (cleaned) | `data/collected/cleaned/gsm8k/` | 4.92 MB | 8,792 records | Math reasoning — SFT/eval asset. MIT |
| Alpaca | `data/collected/small_datasets/alpaca_data.json` | 23.03 MB | ~52k records | Instruction data. License needs review (Alpaca is CC BY-NC 4.0 — non-commercial) |
| Wikipedia scrape | `data/collected/wikipedia/` | ~9 KB total | ~1,380 words | Negligible; 6/11 Bengali titles failed |
| Staging: love_emotion | `data/staging/love_emotion/` | ~40 KB | negligible | BN/EN/BN-Latn emotion pairs — SFT asset |
| `knowledge/` | `packages/ai-core/knowledge/` | ~0.2 MB | — | **PRIVATE — excluded from any training corpus** |

**Banglish:** effectively zero dedicated text (14–19 "mixed" lines in manifests; no romanized-Bengali corpus found).

## 2. Dataset Readiness Score: **NOT READY for meaningful pretraining**

Evidence:

- **Total usable pretraining text ≈ 3.2–3.3 M tokens** (phase-7/9 corpora overlap heavily — they are near-duplicates of each other, not additive).
- Chinchilla-style target for 8.8 M params ≈ **~176 M tokens** → current corpus is **~2%** of optimal, **~0.37 tokens/param**.
- **Bengali share ≈ 0.03%** of the large corpus. A Bengali-first companion model cannot learn Bengali from this.
- The corpus *is* sufficient for a **pipeline-validation run** (Stage-0: verify end-to-end training, checkpointing, resume, throughput on real data) — explicitly NOT for capability.

### Critical data-pipeline inefficiency (verified in `core01/dataset.py`)

`TextDataset` treats **each line as an independent example**, tokenizes it, then **pads to max_len=512**. Average corpus line ≈ 107 chars ≈ ~30 tokens → **~94% of every batch is padding**. There is no packed-sequence / cross-document context loader. Effective useful-token throughput is ~15–30× lower than it appears. This is the single biggest training-efficiency gap.

## 3. Model Architecture Readiness: **READY (unchanged)**

- Decoder-only Transformer, pre-norm, sinusoidal pos-enc, GELU, causal mask, 8,842,560 params — verified identical to spec; untouched by all phases.
- Tokenizer: SentencePiece BPE 8k, vocab 8,000, special IDs pad=0/unk=1/bos=2/eos=3 — loads correctly, used consistently.
- Inference safeguard marks model UNTRAINED — intact.

## 4. Training Pipeline Readiness: **MOSTLY READY, gaps listed**

Verified present (`core01/training.py`, `dataset.py`):
- AdamW + linear-warmup LambdaLR, grad clipping config, label smoothing n/a.
- FP32 / FP16-AMP+GradScaler / BF16-with-fallback (`resolve_amp_dtype`), `resolve_device` CPU fallback.
- Gradient accumulation with **mathematically correct partial-group averaging** (Phase 4.2.2 fix, tested).
- Atomic checkpoint writes, non-destructive backup, RNG state (python/numpy/torch cpu+cuda), optimizer+scheduler state, tokenizer provenance, approximate resume (sampler state not checkpointed — documented limitation).
- SFT gate: code-enforced pretrained-checkpoint requirement (Phase 4.3.1).
- Response-only loss masking for SFT (verified vs manual reference).

Gaps:
1. **No top-level `train()` orchestrator** — `PretrainingEngine` exposes `train_epoch`/`evaluate`/`save`/`load`; a driver script must wire dataset→loader→engine. (Missing component, not a bug.)
2. **No packed-sequence loader** (see §2) — needs new code before real runs.
3. **LR schedule = warmup only, no decay** — acceptable for a short stage-0 run; add cosine/linear decay before long runs.
4. **No multi-GPU**: no DataParallel/DDP anywhere — T4 x2 cannot be used as one job. Options: single-GPU run, or two independent runs/experiments.
5. `warmup_steps`, `checkpoint_interval_steps`, `eval_interval_steps`, `resume_checkpoint`, `device`, `precision`, `gradient_accumulation_steps` are all config-driven — good.

## 5. GPU Resource Plan — Kaggle T4 x2 (16 GB each)

**Recommendation: use ONE T4 (`cuda:0`), not both.** Multi-GPU is not implemented; do not assume x2.

VRAM estimate (8.8 M model — tiny):
- Weights+grads+AdamW ≈ ~160 MB. Activations dominate.
- batch 32 × seq 512, fp16 autocast: activations ≈ ~0.5–1.5 GB → **far below 16 GB**.

Suggested Stage-0 config (safe starting point, owner-tunable):

| Param | Value | Rationale |
|---|---|---|
| device | `cuda` (single GPU) | DDP not implemented |
| precision | `fp16` | T4 has no BF16 (sm_75); `resolve_amp_dtype` auto-falls-back anyway |
| batch_size | 32 | micro-batch |
| gradient_accumulation_steps | 1–2 | effective batch 32–64 seqs |
| max_len | 512 | config default; corpus lines are short so real seqs mostly padded (see §2) |
| learning_rate | 3e-4 (config default) | standard for this scale; short run tolerant |
| warmup_steps | 100–500 | config default 100 |
| checkpoint_interval_steps | 250–500 | ~150–200 MB per ckpt (model+optimizer+RNG) |
| epochs | 1–3 on 3.2 M-token corpus ≈ 200–600 steps/epoch | will overfit — that is expected for stage-0 |

Throughput estimate: T4 fp16 ≈ 65 TFLOPS; ~53 MFLOP/token fwd+bwd → theoretical ceiling ~1M tok/s, realistic small-model MFU 10–30% → **~50k–200k tok/s**. The entire 3.2 M-token corpus ≈ **under ~1 minute/epoch** compute-wise; data loading (per-line tokenization) will dominate wall-clock. Expect step-time of tens of ms.

## 6. Missing Components (before real pretraining)

1. **Bengali/Banglish corpus at scale** — REQUIRES OWNER APPROVAL for download. Candidates (license review needed): Bengali Wikipedia dump, OSCAR-2301 bn, Bangla literature (Project Gutenberg BN), Banglish social corpora. Even 50–100 MB Bengali text would transform readiness.
2. **Packed-sequence dataset loader** — concatenate token stream into fixed 512-token blocks (BOS/EOS document boundaries preserved); ~15–30× compute efficiency vs current per-line padding.
3. **Driver script** for pretraining (build corpus → split → loaders → PretrainingEngine → checkpoint loop).
4. **LR decay schedule** for runs beyond smoke-test length.
5. Optional: corpus dedup pass (8.8% exact-dup lines in phase-7 corpus) and quality filter.
6. Optional: `sentencepiece` pinned in a requirements file for non-Kaggle envs.

## 7. Exact Next Actions (all require owner approval)

1. **Owner decision A — Stage-0 validation run (recommended first):** approve a bounded run on the existing ~3.2 M-token corpus (e.g., ≤500 steps) purely to verify end-to-end training/checkpoint/resume/throughput on Kaggle T4. No capability claims will be made; model stays effectively UNTRAINED-equivalent (random-init + tiny exposure).
2. **Owner decision B — dataset acquisition:** approve specific Bengali/English/Banglish sources + licenses + download destination (Kaggle-side preferred; local disk C: has only ~4.8 GB free).
3. **Code task (needs approval to modify):** implement packed-sequence loader + pretraining driver script. No architecture/tokenizer changes.
4. After stage-0 metrics (tok/s, loss curve, VRAM), set real training config and corpus manifest → then approve real pretraining.

## Prohibitions honored

No source modified, no files deleted, no downloads, no training, no GPU consumed, no architecture/tokenizer changes, no external APIs, no commits.
