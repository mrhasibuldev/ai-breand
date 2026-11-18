# NEXUSAI CORE-01 RUN4 — COLAB BUNDLE & CELL AUDIT

**Date:** 2026-11-10 · READ-ONLY · Nothing modified/executed

## 1. Verified findings

**Bundle (`exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip`, 299,478 B):**
- Contains all 8 core01 modules + `nexusai_core_01` config package + sp_bpe_8k tokenizer (.model 387KB + .vocab 137KB) + the cell + manifest — **self-sufficient for training**
- Driver imports only torch/numpy/sentencepiece — all preinstalled on Colab ✅
- Tokenizer path inside bundle matches checkpoint's recorded `tokenizer_path` (`/content/nexusai/...`) ✅

**Cell (`COLAB_RUN4_TRAIN_CELL.py`):**
- Mounts Drive, asserts run3 ckpt + corpus exist before doing anything ✅
- Resume priority: `checkpoint_final.pt` in OUT_DIR → `checkpoint_last.pt` → latest step ckpt → run3 SRC ✅ (never refuses, never deletes)
- OUT_DIR = `checkpoints/core01_run4` — **fully isolated from run1/2/3** ✅
- No `rm`/delete/overwrite of any existing artifact anywhere in cell ✅
- Driver: strict `load_state_dict`, atomic `os.replace` checkpoint saves, resume restores model+optimizer+scheduler+RNG+grad-scaler ✅
- `--resume` absolute path is safe on Linux (`os.path.join(dir,"/abs")`→"/abs") ✅

**Run3 checkpoint:** sha256 `ad515cad…7830` verified, step=1341 — matches cell's assert ✅

**Dataset:** `corpus_train.jsonl` 216,193 docs, `text` field matches `TEXT_FIELD="text"` ✅

## 2. Critical risks
| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | `START_EPOCH` undefined (line 68) → NameError AFTER training; JSON report fails | LOW (training safe) | 1-line fix needed |
| R2 | Run3 ckpt must exist on Drive at `NexusAI/checkpoints/core01_english_run3/` — if never uploaded, assert fails | MED | verify Drive contents first |
| R3 | Corpus 385MB must be uploaded to `NexusAI/data/run4/` | MED | user action |
| R4 | Colab session disconnect mid-run | LOW | resume-safe by design |
| R5 | `weights_only=False` torch.load | LOW | self-produced ckpt only |

## 3. Missing files/info
- Run4 checkpoint dir on Drive (created by cell ✅)
- Confirmation run3 ckpt + corpus already on Drive (user must verify)
- GPU type/RAM — only knowable inside Colab session
- Exact tokenized corpus count (char-estimate ~53M only)

## 4. Required corrections
1. **Cell line ~49:** add `START_EPOCH = ck.get("epoch", 0)` before `rep` dict — prevents post-training crash. (Needs approval to edit.)
2. Optional: print resolved RESUME_SRC before training (already printed ✅)

## 5. Safe Run4 execution plan
1. Owner approves 1-line cell fix
2. Verify Drive: `NexusAI/checkpoints/core01_english_run3/checkpoint_final.pt` + `NexusAI/data/run4/corpus_train.jsonl` present
3. Colab: upload+extract bundle to `/content/nexusai`, paste cell, run
4. On disconnect: re-run same cell — auto-resumes from latest ckpt
5. After `checkpoint_final.pt`: download → I verify sha256/strict-load → neural-only eval vs run3 → promote decision

## Run3 overwrite risk: **NONE** — read-only source, isolated output dir, atomic writes.
