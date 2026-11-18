# NexusAI Core-01 Run4 — Single Upload Bundle v2.2

ONE ZIP contains EVERYTHING for Run4 preflight + training prep.
**Upload filename must be exactly:** `NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip`
(Colab may rename it to `... (1).zip` etc. — that is accepted automatically.)

## Contents
- `manifest.json` — SHA-256 + size for every file (v2.2.0)
- `cells/COLAB_RUN4_SINGLE_UPLOAD_CELL.py` — reference copy of the validator
  (authoritative cell is embedded in the Colab notebook)
- `preflight/COLAB_RUN4_PREFLIGHT_CELL.py` — read-only preflight checker
- `training/NEXUSAI_CORE01_RUN4_BUNDLE.zip` — training code bundle
  (model, driver, tokenizer, train cell)
- `dataset/corpus_train.jsonl` — corpus (385,217,021 B, 216,193 records)
- `evidence/nexusai_run4_resume_smoke_evidence.json` — resume evidence
- `checkpoint/checkpoint_final.pt` — verified Run3 checkpoint
  (106,777,501 B, sha `ad515cade…`)

## How to use (beginner)
1. Open `docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` in Colab
   (fresh tab, GPU runtime).
2. Run the upload cell — it prints `[CELL_VERSION] v3.1`, accepts the ZIP
   (or `... (n).zip`), verifies outer release identity + manifest + every
   payload hash, safely extracts, and stages files to Drive:
   `MyDrive/NexusAI/data/run4/`, `.../checkpoints/core01_english_run3/`,
   `.../NEXUSAI_CORE01_RUN4_BUNDLE.zip`, `.../reports/run4/`.
3. Run the preflight cell (Cell 14) — read-only verification of
   checkpoint, corpus, tokenizer, resume wiring, evidence.
4. Review reports in `MyDrive/NexusAI/reports/run4/` (JSON+TXT+MD).
5. Training is a SEPARATE step requiring explicit approval — nothing here
   starts training. `TRAINING_AUTHORIZED` stays False.

## Status meanings
- `READY FOR USER REVIEW` / `READY WITH WARNINGS` — proceed to preflight
- `BLOCKED` — a critical check failed; send the report, do not retry blindly

## Safety
- Identical existing files are reused; different content → BLOCKED, never
  overwritten. The Run3 checkpoint is hash-verified and never modified.
- Run4 outputs go only to `checkpoints/core01_run4/`.
