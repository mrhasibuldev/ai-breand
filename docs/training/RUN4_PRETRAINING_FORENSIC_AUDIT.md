# Run4 Pretraining — Forensic Audit (Phase A/D/E)

**Date:** 2026-11-11 · Read-only audit · NO training executed.

## 1. Artifact inventory (fresh hashes)

| Asset | Size | SHA-256 | In bundle | Verified |
|---|---|---|---|---|
| `exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` | 173,912,644 | `eb693237…debe` | — | ✅ matches release identity |
| `docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py` | 19,018 | `76930d27…` | ✅ (manifest match) | ✅ |
| `docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` | 70,101 | `298915c9…` | — | ✅ embedded==source+injection |
| `COLAB_RUN4_PREFLIGHT_CELL.py` | 30,740 | `fe2e851b…` | ✅ | ✅ |
| `NEXUSAI_CORE01_RUN4_BUNDLE.zip` (inner) | 299,476 | `f91411e1…` | ✅ | ✅ |
| `corpus_train.jsonl` | 385,217,021 | `5f8572ed…` | ✅ | ✅ |
| `nexusai_run4_resume_smoke_evidence.json` | 2,932 | `0cb7588d…` | ✅ | ✅ |
| Run3 `checkpoint_final.pt` | 106,777,501 | `ad515cade…` | ✅ | ✅ |

Manifest v2.0.0, 7 entries, all hashes verified by streaming e2e (earlier session: 18/18 + 20/20 PASS).

## 2. Corpus deep-dive (actual data, 216,193 records scanned)

Schema: `{text, category, lang, source}` only — **no QA/instruction fields**.

| Source | Records | Nature |
|---|---|---|
| english_first | 61,960 | English text |
| tinystories | 60,000 | English stories |
| bangla_wikipedia_mit | 45,000 | Bengali Wikipedia articles |
| bongchat_v1 | 30,000 | Bengali general-knowledge/chat-style |
| reasoning_v1 | 10,233 | **QA format** math/logic (`Question:…Answer:…Explanation:`) |
| sangraha_bengali | 9,000 | Bengali |

Lang: en 130,753 · bn_mixed 84,000 · bn 819 · banglish 459 · mixed 162.

### Honest capability findings
- **Math/reasoning:** reasoning_v1 has 7,878 arithmetic-pattern hits — real QA math data exists ✅ (but only ~10k records, English)
- **Creator identity (`Hasibul`):** essentially ABSENT — 1 noise hit in bongchat, 9 unrelated "hasibul" name mentions in wiki. **The model will NOT reliably answer creator=Hasibul from this corpus.** Needs small instruction/SFT data later.
- **Love/affection conversation:** ~40 hits in bongchat + scattered wiki mentions — minimal conversational coverage.
- **Bengali QA consistency:** corpus is dominated by encyclopedic prose; conversational Bengali is thin (bongchat 30k of 216k).
- **banglish:** only 459 records — very thin.

## 3. Model architecture (verified from source+checkpoint)
- `NexusAICore01`: decoder-only Transformer, **8,842,560 params**
- d_model=256, n_layers=6, n_heads=8, d_ff=1024, max_len=512, vocab=8000
- Sinusoidal positional encoding, causal mask, pre-shifted labels,
  `ignore_index=pad_id`, no weight tying observed
- Tokenizer: `sp_bpe_8k` SentencePiece BPE, BOS=2 EOS=3 PAD=0, vocab 8000
  (en+bn encode verified live)
- Historical "2.45M/2-layer" reports are STALE — actual is 8.84M/6-layer.

## 4. Checkpoint (Run3) compatibility — FULL_RESUME_VERIFIED (repo, bounded smoke)
- epoch=3, step=1341, PRETRAINING_COMPLETED, losses 4.426/4.217
- model/optimizer/scheduler(last_epoch=1341)/GradScaler/RNG(python,numpy,torch_cpu,torch_cuda) all present
- smoke test: load→restore→1 opt step (1341→1342)→save→reload ✅
- scheduler caveat: lr-lambda rebuilt with Run4 step budget (PARTIALLY_VERIFIED)
- CUDA/FP16: NOT_TESTED (smoke was CPU/FP32)

## 5. Training config (train cell → driver)
- `--epochs 2 --max-steps 8000 --batch-size 8 --grad-accum 4 --precision fp16 --device cuda`
- `--val-fraction 0.02` doc-level split (no leakage), ckpt every 100 steps,
  eval every 250, resume via `--resume RESUME_SRC` → OUT_DIR `checkpoints/core01_run4/`
- Est.: ~103K packed blocks → ~3.2K opt steps/epoch → ~6.4K total < 8000 ✅
- Storage: ~64 ckpts × ~107MB ≈ 6.8GB Drive needed

## 6. Risks / blockers for stated goals
| Goal | Corpus support | Verdict |
|---|---|---|
| BN question→BN answer | weak-moderate (bongchat 30k) | PARTIAL — expect limited QA ability |
| EN question→EN answer | moderate | PARTIAL |
| Banglish | 459 records | WEAK |
| Math reasoning | reasoning_v1 10k QA | MODERATE (English-centric) |
| Creator = Hasibul | ~absent | **FAIL expected** — needs SFT data |
| Love/affection chat | ~40 records | WEAK |

**Recommendation:** Run4 pretraining is safe to run (integrity verified), but
post-training quality for conversational/identity goals will be limited by
data. A small instruction-tuning phase with targeted QA data (creator identity,
BN/EN QA pairs, Banglish) is the honest path to those behaviors — NOT more
pretraining on the same corpus.

## 7. Readiness status
- Release integrity: **PASS** (local e2e)
- Colab/Drive execution: **NOT_TESTED**
- GPU/FP16: **NOT_TESTED**
- Training: **NO-GO** pending Colab preflight + explicit approval
