# NexusAI Core-01 Run4 — Single Upload Guide

## Why single ZIP?
The old workflow needed 4 separate uploads (training ZIP, corpus, evidence JSON,
preflight cell). Colab upload widgets are session-bound and error-prone
("Upload widget is only available when the cell has been executed in the
current browser session"). One ZIP removes most of that friction.

## The one file to upload
`exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip`
- Size: **173,912,086 bytes** (~174 MB)
- SHA-256: `cd65b1aff281821a588b75e084531c9c2c044eb05fdb1c52501e27538d0bf81b`

## ZIP contents
```
NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip
├── README_RUN4.md
├── manifest.json                     (sha256+size of every file)
├── preflight/COLAB_RUN4_PREFLIGHT_CELL.py
├── training/NEXUSAI_CORE01_RUN4_BUNDLE.zip   (original, unchanged)
├── dataset/corpus_train.jsonl                (385,217,021 B raw)
└── evidence/nexusai_run4_resume_smoke_evidence.json
```

## Checkpoint
`checkpoint/checkpoint_final.pt` IS included (verified Run3, sha `ad515cade…`).
The cell stages it to `MyDrive/NexusAI/checkpoints/core01_english_run3/`
only if missing or identical — never overwrites a different file.

## Cell execution order (Colab)
1. **Cell 1 — `COLAB_RUN4_SINGLE_UPLOAD_CELL.py`** (paste contents or upload the
   `preflight/` file from inside the ZIP after extracting locally — simplest:
   paste the cell code directly into a notebook cell).
   - It first looks for the bundle on Drive at
     `MyDrive/NexusAI/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip`.
   - If absent, it uses the Colab upload widget (needs a fresh session — if it
     errors, restart the runtime and rerun the cell, or use the Drive method).
   - Validates ZIP integrity, manifest, and every payload SHA-256/size.
   - Stages files to:
     - `MyDrive/NexusAI/NEXUSAI_CORE01_RUN4_BUNDLE.zip`
     - `MyDrive/NexusAI/data/run4/corpus_train.jsonl`
     - `MyDrive/NexusAI/nexusai_run4_resume_smoke_evidence.json`
     - `/content/nexusai_run4_preflight/COLAB_RUN4_PREFLIGHT_CELL.py`
   - Verifies the Run3 checkpoint hash read-only.
   - Writes report to `MyDrive/NexusAI/reports/run4/`.
   - Never overwrites a different existing file (reports conflict instead).
2. **Cell 2 — `COLAB_RUN4_PREFLIGHT_CELL.py`** (the staged copy). Read-only
   verification of Drive assets → report in `reports/run4/`.
3. **Review** the preflight report. Only statuses
   `READY FOR USER REVIEW` / `READY WITH WARNINGS` are candidates.
4. **Cell 3 — training** (`COLAB_RUN4_TRAIN_CELL.py` inside the training ZIP):
   run ONLY after explicit human approval.

## Drive alternative (no upload widget)
Place the single ZIP at `MyDrive/NexusAI/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip`
via drive.google.com, then run Cell 1 — it detects the Drive copy automatically.
The interactive upload widget still requires a valid current browser session;
Colab disconnections can invalidate it — the Drive method avoids this entirely.

## Interpreting results
- `READY FOR USER REVIEW` — all checks pass (still NOT training authorization)
- `READY WITH WARNINGS` — non-critical warnings only
- `BLOCKED` — see `critical_failures` in the JSON report; do not proceed

## Run3 checkpoint safety
- Checksum-verified before and after every step; never overwritten.
- Training writes ONLY to `MyDrive/NexusAI/checkpoints/core01_run4/`.
- `checkpoint_final.pt` existing there → training cell exits early (no retrain).
- Resume picks `checkpoint_last.pt` → latest step ckpt → run3 as fallback.

## Known limitations
- CUDA/FP16 execution: NOT_TESTED (source-verified only).
- Scheduler LR-lambda rebuilt with Run4 step budget (PARTIALLY_VERIFIED).
- Pure-Bengali corpus share is small (819 records); Bengali relies on mixed data.
- ~6.8 GB Drive space needed for ~64 step-checkpoints during training.
