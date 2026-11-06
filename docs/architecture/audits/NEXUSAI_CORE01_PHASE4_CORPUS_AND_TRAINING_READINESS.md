# NEXUSAI_CORE01_PHASE4_CORPUS_AND_TRAINING_READINESS

**Date**: 2026-11-06
**Type**: PREPARATION ONLY — no downloads, no corpus created, no training
**Status of every item is explicitly labeled: VERIFIED / PARTIALLY VERIFIED / NOT VERIFIED / PLANNED / BLOCKED BY APPROVAL**

---

## 1. EXECUTIVE SUMMARY

- Core-01 verified intact and training-ready (8,842,560 params, UNTRAINED, full pipeline present).
- **CRITICAL BLOCKER FOUND**: Local machine has only **4.8 GB free disk** (C:) and **1.4 GB available RAM**, 4 CPU cores, no GPU. This makes local corpus storage AND local training impractical.
- Dataset selection finalized from Phase 3.1 verified-safe list.
- **Free GPU (Kaggle/Colab) is effectively REQUIRED** — not optional — for both corpus processing and training, because local disk/RAM cannot hold the corpus.
- Two approval gates presented below: (A) dataset download, (B) training run. Neither is authorized yet.

---

## 2. CURRENT CORE-01 VERIFICATION — VERIFIED

| Item | Status | Evidence |
|---|---|---|
| Architecture exists | VERIFIED | `core01/transformer.py`, `models/nexusai_core_01/config/model_config.py` |
| Parameter count | VERIFIED | `count_parameters()` = **8,842,560** (re-run this session) |
| Status | VERIFIED | `model_status = UNTRAINED` |
| Tokenizer | VERIFIED | 8K SentencePiece, compatible, UNK=0.13% |
| Pretraining engine | VERIFIED | `PretrainingEngine` in `core01/training.py` |
| SFT engine | VERIFIED | `InstructionTuningEngine` |
| Checkpoint save/resume | VERIFIED | `CheckpointManager` + `TrainingCheckpoint` |
| Evaluation | VERIFIED | `ModelEvaluator` (9 tests, all pass) |
| GPU compat | VERIFIED (code) | device auto-detects cuda/cpu |
| Any training done | VERIFIED NO | no checkpoints under `nexusai_core_01/checkpoints/` |

**Conclusion**: No architectural problem found. Core-01 is ready as-is.

---

## 3. ACTUAL MODEL TRAINING STATUS — VERIFIED: NOT STARTED

No training has ever run on Core-01. Only random-init forward passes in tests.

---

## 4. HARDWARE & STORAGE REALITY — VERIFIED THIS SESSION

| Resource | Actual | Needed for training | Verdict |
|---|---|---|---|
| GPU | **None** (CUDA unavailable) | any real training | ❌ BLOCKED locally |
| RAM | 8.5 GB total / **1.4 GB free** | ~4-8 GB for batch | ❌ too tight |
| CPU | 4 cores, PyTorch 2.14.1+cpu | — | smoke tests only |
| Disk C: | **4.8 GB free** | corpus ~1-3 GB + ckpts | ❌ critical |
| Disk D: | 0.1 GB free | — | ❌ unusable |

**VERIFIED FACT**: Local machine cannot store or train the planned corpus. Free cloud GPU (Kaggle/Colab) is mandatory for Phase 4 execution.

---

## 5. SELECTED DATASETS (from Phase 3.1 verified-safe list)

| # | Dataset | Source | License | Role | Est. usable tokens |
|---|---|---|---|---|---|
| 1 | B-CORE subset | HF nahid-hub/B-CORE | CC BY 4.0 | Bengali pretrain | ~8M (sampled) |
| 2 | IndicTalk bn | HF LingoIITGN/IndicTalk | CC BY 4.0 | bn conversation + Romanized + mixed | ~2-4M |
| 3 | alpaca_chat_bangla | HF Mahadih534 | CC-BY-2.0 | bn instruction/SFT | ~2M subset |
| 4 | GSM8K | openai/gsm8k | MIT | math reasoning | ~0.76M |
| 5 | Ayon128 Banglish-English | HF Ayon128 | MIT | Banglish pairs | ~0.3M |
| 6 | Dolly 15K subset | databricks | CC BY-SA 3.0 | en general (optional) | ~1-1.5M |
| 7 | Project data (phase9/10, train_v2, staging) | local | owned | persona/emotion | ~0.1M |

**Excluded (verified unsafe/irrelevant)**: Alpaca raw (NC), dailydialogue_bn (NC-SA), XL-Sum (NC-SA), bangla-alpaca-orca (GPL-3.0), Bangla-SFT-50k (synthetic+unclear), knowledge/ (private), training/original_dataset.jsonl (junk).

**Download size estimate**: streamed/sampled subsets ≈ **1-3 GB total** — exceeds local free disk, so processing must happen on the cloud GPU or to an external drive (none available).

---

## 6. LANGUAGE DISTRIBUTION TARGET (planned)

For the ~15M-token Stage-2 corpus:
- Bengali script: ~35% (~5M)
- English: ~30% (~4.5M)
- Romanized Bengali: ~15% (~2M)
- Mixed/code-switched + parallel: ~20% (~3M)

Parallel translation pairs counted separately from natural conversation. Bengali oversampled early because it is the weakest language.

---

## 7. PRETRAINING STRATEGY — PLANNED

- Stage A: causal LM on mixed corpus, seq_len 512, batch ~8-16 (T4 16GB), AdamW lr ~3e-4, ~3 epochs ≈ 45M tokens seen.
- On 2×T4 Kaggle: est. ~8-15 GPU-hours → fits in one 12h session.
- Checkpoint every ~30 min to `/kaggle/working`, download after.

## 8. SFT STRATEGY — PLANNED

- Stage B: instruction/response on alpaca_chat_bangla + IndicTalk + GSM8K + project SFT, lr ~1e-5-3e-5, ~1-2 epochs.
- Separate engine already implemented.

## 9. TRAINING PIPELINE VERIFICATION — VERIFIED

`PretrainingEngine`, `InstructionTuningEngine`, `CheckpointManager`, `DatasetLoader`, `ModelEvaluator` all present and import cleanly. CPU forward+loss verified in Phase 1 tests.

---

## 10. DOWNLOAD APPROVAL REQUEST — BLOCKED BY APPROVAL

Before downloading, requesting approval for:

| Dataset | Source | Why | Size | License | Destination |
|---|---|---|---|---|---|
| B-CORE sample (~0.1-0.2%) | huggingface.co/datasets/nahid-hub/B-CORE-bengali-corpus | Bengali pretrain | ~200-500 MB streamed | CC BY 4.0 | `data/corpus_v1/bn_bcore/` |
| IndicTalk bn | huggingface.co/datasets/LingoIITGN/IndicTalk | conversation+Banglish | ~50-150 MB | CC BY 4.0 | `data/corpus_v1/indic_talk/` |
| alpaca_chat_bangla | huggingface.co/datasets/Mahadih534/alpaca_chat_bangla | bn SFT | ~30-80 MB | CC-BY-2.0 | `data/corpus_v1/bn_sft/` |
| GSM8K | github/openai gsm8k | math reasoning | ~5 MB | MIT | `data/corpus_v1/gsm8k/` |
| Ayon128 Banglish-English | HF Ayon128/Banglish-English | Banglish pairs | ~5 MB | MIT | `data/corpus_v1/banglish/` |
| Dolly subset (optional) | HF databricks-dolly-15k | en general | ~5-10 MB | CC BY-SA 3.0 | `data/corpus_v1/en_dolly/` |

**Problem**: `data/corpus_v1/` on C: has only 4.8 GB free — fits if kept ≤ ~2 GB, but tight. Alternative: process on Kaggle directly (download there, don't store locally), keeping only manifests locally.

**Files created**: `data/corpus_v1/**` + `data/corpus_v1/manifest.json`. Nothing else touched.

---

## 11. TRAINING APPROVAL REQUEST — BLOCKED BY APPROVAL

| Item | Value |
|---|---|
| Model | nexusai-core-01 (8,842,560 params, UNTRAINED) |
| Stage | A: pretraining (then B: SFT) |
| Corpus | corpus_v1 (~15M tokens target) |
| Hardware | Kaggle 2×T4 (free) — local CPU insufficient |
| Config | seq512, batch 8-16, AdamW 3e-4, ~3 epochs, ckpt every 30min |
| Est. runtime | ~8-15 GPU-hours (1-2 sessions) |
| Checkpoint dest | `models/nexusai_core_01/checkpoints/` + `experiments/exp01/` |
| Untouched | legacy checkpoints_medium/, tokenizer, all app code, knowledge/ |
| Risks | free GPU not guaranteed; session kills → resume from ckpt; Bengali quality may still be weak |

---

## 12. KNOWN LIMITATIONS

- Local disk/RAM effectively force cloud GPU use.
- Banglish data remains thin; IndicTalk-Romanized is the main source.
- Bengali reasoning/decision data scarce — model will be better at conversation than deep reasoning initially.
- 8.84M params caps overall capability.
- License: CC-BY attribution tracking needed; GPL/NC sets excluded.

## 13. RECOMMENDED NEXT STEP

Owner chooses:
- **Option A (recommended)**: approve dataset download → I build `corpus_v1/` + manifest + token stats → then request training approval for Kaggle run.
- **Option B**: approve a Kaggle-first flow where datasets download directly on Kaggle (no local storage needed) — requires owner to create/verify Kaggle account.
- **Option C**: free up disk space first, then local CPU smoke test only.

**STOP — awaiting explicit owner decision on download + training approvals.**
