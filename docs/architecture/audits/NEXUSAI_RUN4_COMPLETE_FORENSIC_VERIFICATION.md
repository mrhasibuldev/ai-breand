# NexusAI Run4 — Complete Training, Dataset & Model Forensic Verification

**Date:** 2026-11-17 · READ-ONLY · Local repo evidence + previously verified Colab results
**Drive access:** NOT available from this machine — Drive-only items marked UNVERIFIED.

## 1. Executive Summary
Run4 checkpoint is **hash-verified** (`761a5b14…`, ep5/step9213, strict load
PASS on Colab T4). The training dataset is **locally verified**
(216,193 records, sha `5f8572ed…`). Training logs, weight-diff, and "10K
package" meaning are **Drive-only → UNVERIFIED**. CPU inference cell is
prepared but not yet executed. Model quality remains the open question.

## 2. Artifact Inventory
| Artifact | Location | Status |
|---|---|---|
| Run4 ckpt | Drive `/NEXUSAI_RUN4/checkpoint_final.pt` | VERIFIED (Colab hash+load) |
| Run4 report/log | Drive `/NEXUSAI_RUN4/` | UNVERIFIED (not inspected) |
| Run4 audit outputs | Drive `NEXUSAI_RUN4_AUDIT/audit_20261116_210128/` | PARTIAL (metrics seen, raw outputs not reviewed) |
| Corpus | local `data/phase2/run4_corpus/corpus_train.jsonl` | VERIFIED |
| Corpus manifest | same dir `corpus_manifest.json` | VERIFIED |
| Tokenizer | local + package `sp_bpe_8k.model` | VERIFIED sha `2fcc6a87…` |
| Training driver | `core01/pretraining_driver.py` | VERIFIED source |

## 3. "10K Package" — UNVERIFIED
No artifact named "10K" exists in the repo. Closest matches: reasoning
subset emitted 10,233 docs (3,411 base × 3 repeats — intentional
augmentation, mild duplication by design). The "10K package" likely refers
to a Drive-side bundle not present locally → meaning UNRESOLVED, needs
Drive listing.

## 4. Dataset Integrity — VERIFIED (local corpus)
`corpus_train.jsonl`: 385,217,021 B · sha `5f8572ed…` · 216,193 records ·
0 malformed · schema `{text,category,lang,source}` · avg ~861 chars.

**Provenance (manifest):**
| component | docs | category |
|---|---|---|
| bangla_wikipedia_mit | 45,000 | bangla_general |
| sangraha_bengali | 9,000 | bangla_general |
| bongchat_v1 | 30,000 | bangla_instruction |
| english_first | 61,960 | english_general |
| tinystories | 60,000 | english_simple |
| reasoning_v1 | 10,233 (3,411×3) | reasoning_* |

Language dist (measured): en 60.5% · bn_mixed 38.9% · bn 0.4% ·
banglish 0.2% · mixed 0.07%. Earlier "thin BN" claim corrected — bn_mixed
is substantial; proper-script bn and banglish remain thin.

**Consumption status:** corpus was the Run4 `--train-file` input (driver
verified) — but per-record DataLoader consumption is only provable from
Colab logs → PARTIAL/UNVERIFIED for exact consumed count.

## 5. Training Execution — PARTIAL
Verified (Colab report + ckpt metadata): driver ran, resumed ep3→5,
step 1341→9213 (+7,872 steps), PRETRAINING_COMPLETED, exit 0,
train_loss ~3.177, val_loss ~2.915 (reported, ckpt fields exist).
NOT verified: per-epoch loss curve, batches/samples consumed, GPU name/
duration, failed batches — need `run4_training.log` from Drive.

## 6. Model Learning Evidence — PARTIAL
- Parameter updates: optimizer/scheduler/scaler/RNG state present in ckpt;
  strict load PASS; step advanced 1341→9213 → **updates occurred** (PASS).
- Loss improvement 4.43→2.92 val → learning signal real (PASS, reported).
- Weight diff Run3-vs-Run4: **UNVERIFIED** (both files not co-located
  locally; Colab could compute but wasn't asked).
- Generalization/generation quality: **UNVERIFIED** — benchmark metrics
  clean but semantic review of raw outputs still pending.

## 7. Checkpoint & Recovery — PASS
sha `761a5b14…` exact · 106,777,501 B · 100 tensors · full resume state ·
strict load on T4 PASS · CPU load test cell ready (not yet run).
Recoverable without GPU session: YES (ckpt+tokenizer+code all portable).

## 8. CPU-Only Inference — BLOCKED→READY
Cell `docs/notebooks/COLAB_RUN4_CPU_VERIFY_CELL.py` ready (hash-gated,
strict CPU load, 20 prompts, artifacts to Drive). Run3 CPU inference
already proven locally (~40 tok/s). Run4 CPU: NOT YET EXECUTED.

## 9. Language Evaluation — Run3 evidence (Run4 pending)
Run3 31-prompt live test: Bengali 5/5 EMPTY, English/Banglish gibberish,
0 correct answers → verdict C. Run4 mechanical metrics clean (0 empty/
leak on 18 prompts) but semantic quality UNKNOWN until raw outputs reviewed.

## 10. Large-Scale Storage Recommendation (research only)
For millions→billions of records, recommended architecture:
- **Raw:** JSONL + Zstd (good compression, streamable, tool-friendly)
- **Training:** packed binary token IDs (uint16/uint32 memmap) — smallest,
  fastest, no re-tokenization
- **Shards:** versioned tar/bin shards ~1-4GB each + per-shard SHA-256
- **Index/metadata:** SQLite (small) or Parquet+Zstd (analytics)
- **Loading:** streaming/memmap, bounded RAM; never load full corpus
Estimated: current 385MB JSONL ≈ ~200-300MB packed tokens; scales linearly.
Alternative considered: TFRecord/WebDataset — viable but heavier tooling;
packed-binary is simpler for this stack. Parquet alone insufficient for
raw text throughput.

## 11. GPU→CPU Continuity Plan
Minimum for CPU inference: Run4 ckpt + `sp_bpe_8k.model` + core01/*.py +
config + deps (torch CPU, sentencepiece, numpy, psutil) ≈ ~150MB total.
Sufficient — proven pattern with Run3. Resume-training additionally needs
optimizer/scheduler/scaler/RNG (all present in ckpt) + dataset + driver.

## 12. Verdicts
| Question | Answer |
|---|---|
| Drive got full dataset? | UNVERIFIED (Drive-side) — local corpus verified |
| Colab extracted it? | UNVERIFIED |
| DataLoader read it? | PARTIAL (driver ran; per-record proof needs log) |
| Samples consumed? | UNVERIFIED exact count |
| Weights changed? | PASS (step 1341→9213, full state) |
| Learned from data? | PARTIAL (loss improved; quality unproven) |
| Checkpoint valid/recoverable? | PASS |
| Runs on CPU w/o Colab? | READY (cell prepared; Run4 pending execution) |
| Meaningful BN/EN/Banglish? | UNVERIFIED for Run4 (Run3: NO) |
| "10K package" meaning? | UNRESOLVED — likely Drive-side |
| Storage architecture? | Recommended above |
| Next without risk? | Run CPU verify cell → review raw outputs → decide SFT |

## Missing evidence
run4_training.log · RUN4_FINAL_REPORT.json · weight-diff · raw benchmark
outputs · Drive file listing (for "10K") · Run4 CPU inference results.

## FINAL VERDICT: **PARTIAL — training verified, learning signal real,
quality and several Drive artifacts UNVERIFIED.**
Next: execute `COLAB_RUN4_CPU_VERIFY_CELL.py` + review
`ACTUAL_GENERATION_SAMPLES.json` → then SFT decision.
