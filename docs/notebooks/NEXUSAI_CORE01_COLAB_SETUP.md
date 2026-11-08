# NexusAI Core-01 — Complete Kaggle → Google Colab Migration Guide

**For:** the project owner (no programming experience needed — every step says exactly where to click).
**Goal:** move Core-01 training from Kaggle to Google Colab (1× Tesla T4) and prepare for the first real training run.
**Companion files:** notebook `NexusAI_Core01_Google_Colab_Training.ipynb` · audit `docs/architecture/audits/NEXUSAI_CORE01_COLAB_MIGRATION_AUDIT.md`

> ⚠️ **Nothing trains automatically.** Two flags (`APPROVE_SMOKE_TEST`, `APPROVE_FULL_TRAINING`) stay `False` until you choose to enable them.

---

## Part 1 — Every file you need (verified locations)

| # | File | Exact location | What it does | Inside ZIP? | Needs Kaggle download? | Goes to Drive? |
|---|---|---|---|---|---|---|
| 1 | `nexusai_core01_kaggle_package.zip` | `C:\Users\Nusaiba\Desktop\` **and** repo `exports/` | whole Core-01 code+tokenizer package | — | No (already local) | **YES → `NexusAI/package/`** |
| 2 | `english_train.jsonl` | **Kaggle only** — `/kaggle/working/nexusai_core01/prepared_dataset/` | 103,846 training docs / 99.0M tokens | No | **YES — download from Kaggle Output** | **YES → `NexusAI/data/`** |
| 3 | `english_val.jsonl` | same Kaggle folder | 1,581 val docs / 1.49M tokens | No | YES (same download) | YES → `NexusAI/data/` |
| 4 | `manifest.json` | same | provenance + real SHA-256 hashes | No | YES (same download) | YES → `NexusAI/data/` |
| 5 | `preparation_report.md` | same | human-readable prep summary | No | YES (same download) | YES → `NexusAI/data/` |
| 6 | `deduplication_report.json` | same | dedup statistics | No | YES (same download) | YES → `NexusAI/data/` |
| 7 | `sp_bpe_8k.model` + `.vocab` | inside the ZIP at `data/experimental/phase9_2/tokenizers/bpe_8k/` | SentencePiece tokenizer | **YES** | No | No — comes with ZIP |
| 8 | Training scripts (`pretraining_driver.py`, `training.py`, `dataset.py`, `transformer.py`, `model_config.py`) | inside the ZIP under `core01/` + `models/` | model + training engine | **YES** | No | No — comes with ZIP |
| 9 | `NexusAI_Core01_Google_Colab_Training.ipynb` | repo `docs/notebooks/` | the Colab notebook | No | No | No — import into Colab directly |
| 10 | FineWeb shard 0 parquet (~2 GiB) | Kaggle `/kaggle/working/.../raw/` (if it still exists) | raw source | No | optional | **NO — do not upload** (only needed to re-prepare corpus) |

**Key fact:** files 2–6 exist **only on Kaggle** — they are not in this repo. If Kaggle's working storage was wiped, they must be regenerated (see Part 3 fallback).

---

## Part 2 — Step 1: Download files from Kaggle

1. Go to **https://www.kaggle.com** → log in → **Your Work → Notebooks** → open `NexusAI-Core-Training`.
2. In the notebook, find the cell that ran corpus preparation (Cell 7). Below the code there is an **Output** area.
3. Click the **folder/download icon** (or the "..." → Download) to download the output. You want the `prepared_dataset` contents — specifically the 5 files in rows 2–6 above.
4. If the notebook's Output only shows logs, use the left sidebar **Output** tab → browse files → download `prepared_dataset/` (or the individual files).
5. **Verify you got all 5 files** before continuing:
   - `english_train.jsonl` (~390 MB)
   - `english_val.jsonl` (~10 MB)
   - `manifest.json`
   - `preparation_report.md`
   - `deduplication_report.json`
6. **Do NOT delete anything on Kaggle yet.** Keep the dataset until Colab training is verified.

### If Kaggle storage was cleared (files gone)

- Re-open the Kaggle notebook, re-run Cells 2–9 (setup cells recreate everything; Cell 6 re-downloads the ~2 GiB shard only if missing).
- Then re-run Cell 7 prep (~30–60 min) and Cell 8 audit.
- Download the fresh `prepared_dataset/` output.

---

## Part 3 — Step 2: Upload files to Google Drive

1. Go to **https://drive.google.com** → log in.
2. Click **New → Folder** → name it exactly `NexusAI`.
3. Inside `NexusAI`, create 4 subfolders: `package`, `data`, `checkpoints`, `logs` (notebook also makes `checkpoints_smoke`, `checkpoints_full`, `reports` automatically).
4. **Upload the ZIP:** open `NexusAI/package/` → **New → File upload** → select `nexusai_core01_kaggle_package.zip` from your Desktop.
5. **Upload the corpus:** open `NexusAI/data/` → upload all 5 files from Part 2.
6. **Verify:** each file shows a green check / "Available offline" not needed; sizes should be non-zero. Expected final tree:

```
MyDrive/NexusAI/
├── package/
│   └── nexusai_core01_kaggle_package.zip      (306,348 bytes)
├── data/
│   ├── english_train.jsonl
│   ├── english_val.jsonl
│   ├── manifest.json
│   ├── preparation_report.md
│   └── deduplication_report.json
├── checkpoints/  checkpoints_smoke/  checkpoints_full/
├── logs/
└── reports/
```

> The ZIP must be the **306,348-byte** file — the notebook checks its SHA-256 and refuses a wrong version.

---

## Part 4 — Step 3: Connect Google Colab

1. Open **https://colab.research.google.com/** → log in with the same Google account.
2. **File → Upload notebook** → select `NexusAI_Core01_Google_Colab_Training.ipynb` from `docs/notebooks/` in this repo (or drag the file in).
3. **Runtime → Change runtime type → T4 GPU** (Hardware accelerator). This gives 1× Tesla T4, ~14.5 GB VRAM.
4. Run cells **top to bottom**, one at a time (Shift+Enter). Do not use "Run all" for gated cells.

---

## Part 5 — Cell-by-cell execution guide

| Cells | Title | Run it? | Expected success output | Common errors → fix |
|---|---|---|---|---|
| 1 | Overview | read only | — | — |
| 2 | Environment | ✅ yes | python 3.13, torch 2.14, `cuda available: True`, GPU Tesla T4 | `sentencepiece MISSING` → run `!pip install -q sentencepiece`; `pyarrow MISSING` → `!pip install -q pyarrow` |
| 3 | Drive mount | ✅ yes | `DRIVE_ROOT: /content/drive/MyDrive/NexusAI`, package+data dirs listed | `PACKAGE_DIR exists: False` → files not uploaded to Drive yet (redo Part 3) |
| 4 | Package verify | ✅ yes | `zip sha256: 1b0c66f0…` `sha256 match: True`, `PACKAGE_OK = True` | `sha256 match: False` → wrong ZIP uploaded; `PACKAGE INIT FAILED` → check folder names |
| 5 | Tokenizer | ✅ yes | `vocab_size: 8000`, `decode ok` | assertion error → wrong tokenizer file inside package |
| 6 | Dataset audit | ✅ yes | `train: 103,846 docs / 99,011,035 tokens`, `overlap: 0`, `DATASET_OK: True` | `MISSING dataset files` → upload `data/` files; token counts different → tell developer, don't train |
| 7 | Model + VRAM probe | ✅ yes (needs T4) | `params: 8842560`, peak VRAM printed | CUDA unavailable → set runtime to T4; OOM → note it, smoke uses bs32 |
| 8 | Config review | ✅ yes | prints the exact smoke command | — (read-only) |
| 9 | **Smoke test** | ⏸ **ONLY after setting `APPROVE_SMOKE_TEST = True`** | ~200 steps, loss decreasing, checkpoints in `checkpoints_smoke/` | OOM → edit cmd to `--batch-size 16 --gradient-accumulation-steps 2` |
| 10 | Smoke review | ✅ yes | checkpoint list + status/step printed | no checkpoints → smoke failed, check Cell 9 output |
| 11 | **Full training** | ⏸ **ONLY after `APPROVE_FULL_TRAINING = True` AND good smoke results** | `checkpoint_final.pt` = `PRETRAINING_COMPLETED` | session cut → resume next session (Part 7) |
| 12 | Checkpoint verify | ✅ after training | status/step/RNG/scaler fields printed | no checkpoints → training hasn't run |
| 13 | Generation test | ✅ after training | English continuations printed | inference error → send output to developer |
| 14 | Session report | ✅ always at end | status table → paste into README log | — |

**Approval flags stay `False` by default.** Change them one at a time, only when that stage is next.

---

## Part 6 — Smoke test vs full training (plain words)

- **Smoke test (Cell 9):** ~200 optimizer steps on real data. Proves the pipeline works end-to-end (data loads, GPU trains, checkpoints save). It does **NOT** mean the model learned anything useful.
- **Full training (Cell 11):** the real run over ~98.5M tokens. Takes hours; may span multiple Colab sessions. Success = `checkpoint_final.pt` marked `PRETRAINING_COMPLETED` + sane validation loss + readable generation output.

## Part 7 — Resuming after a Colab disconnect

Colab kills sessions (~12h or idle). Checkpoints live on **Drive**, so nothing is lost:

1. New Colab session → same notebook → Runtime T4.
2. Re-run Cells 2–7 (they re-verify everything; variables don't persist).
3. In Cell 11's command, add `--resume checkpoint_last.pt` to the driver args (the file must be inside the `--output-dir`, i.e. `checkpoints_full/`).
4. Training continues approximately from the last epoch boundary.

## Part 8 — Backup rules

- Checkpoints already write to Drive (`checkpoints_smoke/`, `checkpoints_full/`) — they persist automatically.
- After training, also download `checkpoint_final.pt` locally as an extra backup.
- Keep the Kaggle dataset + notebook until Colab training is verified — then Kaggle can be retired.

## Part 9 — Troubleshooting quick table

| Symptom | Meaning | Fix |
|---|---|---|
| `NameError`/`PACKAGE_OK is not defined` | kernel restarted | re-run Cells 2–7 in order |
| `MISSING dataset files` | `data/` not in Drive | redo Part 3 step 5 |
| `sha256 match: False` | wrong ZIP version | re-upload the 306,348-byte ZIP |
| `CUDA unavailable` | CPU runtime | Runtime → T4 GPU |
| OOM | batch too big for T4 | `--batch-size 16 --gradient-accumulation-steps 2` |
| `DATASET_OK` fails overlap | data bug | STOP — send manifest to developer |
| Session dies mid-run | Colab limit | Part 7 resume procedure |

## Part 10 — Honesty notes

- The 100.5M corpus was made on **Kaggle** (verified historically). Colab consumes the exported files — it does not re-download FineWeb unless you choose to re-prep.
- English-only 100M tokens → the model will be weak in Bengali/Banglish. Expected, not a bug.
- UNTRAINED until `checkpoint_final.pt` exists with `PRETRAINING_COMPLETED`.
