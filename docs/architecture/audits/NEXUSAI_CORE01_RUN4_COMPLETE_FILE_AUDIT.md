# NEXUSAI CORE-01 RUN4 — COMPLETE FILE INVENTORY & PRE-TRAINING AUDIT

**Date:** 2026-11-10 · READ-ONLY · Nothing modified

## 1. Executive summary
All required Run4 artifacts exist and verify cleanly. **One important caveat:** the bundle ZIP contains the OLD buggy cell (pre-START_EPOCH fix) — use the fixed `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` instead, or rebuild the zip. Everything else is ready pending Drive uploads.

## 2. Complete file inventory (all .pt checkpoints found)
| Path | Size | Role |
|---|---|---|
| `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt` | 106.8MB | **RUN4 PARENT** ✅ sha256 `ad515cad…7830` |
| `packages/ai-core/models/checkpoints_medium/final_model.pt` | 29.5MB | production fallback |
| `packages/ai-core/models/checkpoints_medium/best_model.pt` | 29.5MB | dup of final |
| `checkpoints_medium/checkpoint_epoch_1-5.pt` | ~58MB ea | INCOMPATIBLE (char-74 vocab) |
| `packages/ai-core/models/checkpoints/checkpoint_epoch_1-5.pt` | 2.2MB ea | small model |
| `models/checkpoints/{real_data_run,validation_test,verification_run}/*.pt` | 10-25MB | old experimental runs (root-level `models/` dir) |
| `data/experimental/phase8|phase10/checkpoints/*.pt` | 4-30MB | historical experiment ckpts |

## 3. Required upload files — verified
| File | Path | Size | SHA-256 (prefix) | Status |
|---|---|---|---|---|
| Bundle | `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip` | 299,478 | `75af9fa2…` | ✅ zip integrity OK (`testzip:None`), 15 entries |
| Corpus | `packages/ai-core/data/phase2/run4_corpus/corpus_train.jsonl` | 385,217,021 | `5f8572ed…` | ✅ 216,193 lines, **0 malformed, 0 empty, 6,922 dup texts (3.2%), 209,271 unique** |
| Run3 ckpt | `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt` | 106,777,501 | `ad515cad…7830` ✅ matches trusted hash | step=1341, epoch=3, PRETRAINING_COMPLETED |
| Tokenizer | `…/bpe_8k/sp_bpe_8k.model` + `.vocab` | 387KB+137KB | `2fcc6a87…`/`8e499079…` | ✅ inside bundle too |
| Cell | `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` | 4,227 | `fda564af…` | ✅ syntax OK, START_STEP+START_EPOCH fixed |

## 4. ZIP internal audit
- `testzip()` → None (no corruption)
- Contains: 8 core01 modules, nexusai_core_01 config, tokenizer model+vocab, cell, manifest
- **⚠️ Cell inside ZIP is STALE** — lacks START_EPOCH fix (`'START_EPOCH = ck.get' in zip → False`)
- Missing from zip (by design): corpus, run3 ckpt (Drive uploads)

## 5. Dataset validation
- JSONL: 216,193/216,193 parse OK, 0 malformed, 0 empty text
- Duplicates: 6,922 exact-dup texts (3.2%) — mostly TinyStories/wiki overlaps, acceptable but noted
- Field schema: `text, category, lang, source` — matches `TEXT_FIELD="text"` ✅
- Bengali chars 47.1%; EN-dominant docs ~56%

## 6. Run3 compatibility
- sha256 == trusted `ad515cad…7830` ✅
- step=1341/epoch=3, optimizer+scheduler+rng+scaler states present → faithful resume ✅
- Config matches core01 transformer (d256/6L/8H/ff1024/ctx512/vocab8000) — strict-load proven ✅

## 7. Training cell audit (fixed version)
- Syntax ✅; START_STEP & START_EPOCH assigned line 48 before `del ck` line 52 ✅
- Paths: Drive-mounted BASE, asserts SRC_CKPT+TRAIN exist, OUT_DIR isolated ✅
- No delete/overwrite of run1-3 ✅; resume priority correct ✅
- Remaining runtime risk: only live-Colab items (Drive files present, GPU alloc)

## 8. Compatibility verdict
Bundle↔cell version: zip's cell stale → **use repo cell file**. Dataset↔driver ✅. Tokenizer↔model ✅. GPU: T4 14.56GB verified by user — 8.8M model fp16 needs <2GB ✅.

## 9. Errors & warnings
| # | Issue | Severity |
|---|---|---|
| W1 | ZIP contains pre-fix cell | MED — use fixed file or rebuild zip |
| W2 | 6,922 dup texts in corpus | LOW — acceptable |
| W3 | Extra root-level `models/checkpoints/*` dirs not in registry | INFO — excluded correctly |
| W4 | Corpus token count char-estimated | LOW |

## 10. Missing files
None for training itself. Drive-side requirements (user uploads): run3 ckpt → `NexusAI/checkpoints/core01_english_run3/`, corpus → `NexusAI/data/run4/`.

## 11. Readiness
- Colab preflight: **READY WITH CONDITIONS** (W1 fix + Drive uploads)
- Training: **NOT AUTHORIZED** — awaiting owner approval

## 12. Download/upload guide
| File | Exists at | Action |
|---|---|---|
| `NEXUSAI_CORE01_RUN4_BUNDLE.zip` | `exports/` | Upload to Colab (extract to `/content/nexusai`) |
| `corpus_train.jsonl` | `packages/ai-core/data/phase2/run4_corpus/` | Upload to **Google Drive** `NexusAI/data/run4/` |
| `checkpoint_final.pt` (run3) | `packages/ai-core/models/checkpoints_core01_run3/` | Upload to **Google Drive** `NexusAI/checkpoints/core01_english_run3/` |
| `COLAB_RUN4_TRAIN_CELL.py` | `docs/notebooks/` (FIXED) | Copy-paste into Colab cell — **do NOT use zip's stale copy** |

**প্রকৃত ৩টা file upload বাটনে select করতে: bundle zip + corpus jsonl + run3 checkpoint_final.pt** — cell আলাদা করে paste করতে হবে (fixed version)।
