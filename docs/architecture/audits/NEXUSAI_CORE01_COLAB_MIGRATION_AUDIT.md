# NexusAI Core-01 — Kaggle → Google Colab Migration Audit & Plan

**Date:** 2026-11-08 · **Mode:** READ-ONLY — nothing deleted, modified, uploaded, or trained.
**Verified Colab env (owner-reported):** Python 3.13.16 · torch 2.14.1+cu130 · CUDA True · 1× Tesla T4.

---

## 1. Executive Summary

**Migration is LOW-RISK and mostly a notebook-layer change.** The entire Core-01 training stack (`core01/`, tokenizer, prep script, driver) contains **zero Kaggle dependencies** — verified by grep: no `/kaggle` paths, no Kaggle APIs. Imports are only stdlib + numpy + torch + sentencepiece (+pyarrow for prep). The Kaggle-specific layer is confined to `docs/notebooks/nexusai_core01_fineweb_pretraining.ipynb` (input detection, `/kaggle/*` paths, approval cells) and two diagnostic notebooks/scripts.

The verified 100.5M-token corpus lives in Kaggle `/kaggle/working` — **it must be exported before leaving Kaggle** (or regenerated on Colab; prep takes ~tens of minutes and needs the 2 GiB shard re-download).

## 2. Current Kaggle Infrastructure Status

| Component | Status |
|---|---|
| Package dataset `nexusai-core01-package` (atoplay) | exists on Kaggle (owner-verified accessible) |
| Prepared corpus (100,499,546 tok) | **historical** — `/kaggle/working` may be wiped; export needed |
| FineWeb shard 0 | same — may need re-download (~2 GiB) |
| GPU smoke test | **never ran** (NameError after runtime restart) |
| Training | **NOT STARTED** — Core-01 UNTRAINED |

## 3. Kaggle-Specific Files Inventory (Category A)

| File | Purpose | Kaggle-only? | After migration |
|---|---|---|---|
| `docs/notebooks/nexusai_core01_fineweb_pretraining.ipynb` | 12-cell gated workflow | **YES** (paths `/kaggle/input`, `/kaggle/working`, Input detection) | Replace with Colab notebook; keep as reference |
| `docs/notebooks/nexusai_core01_kaggle_gpu_diagnostic.ipynb` | GPU microbenchmark | YES | obsolete on Colab |
| `docs/notebooks/kaggle_core01_gpu_diagnostic.ipynb` | earlier diagnostic | YES | obsolete |
| `exports/nexusai_core01_gpu_diagnostic.py` | standalone GPU diag | mostly YES (paths) | superseded by Colab smoke cell |
| `exports/NEXUSAI_CORE01_KAGGLE_PACKAGE_MANIFEST.md` | package manifest | reusable doc | keep (rename-neutral content still valid) |
| `exports/nexusai_core01_kaggle_package/` + `.zip` | portable package | **NO — fully reusable** | upload to Drive instead of Kaggle Dataset |

## 4. Reusable NexusAI Components (Category B — all VERIFIED portable)

| File | Role |
|---|---|
| `core01/transformer.py` | NexusAICore01 architecture |
| `core01/training.py` | PretrainingEngine (AdamW, warmup LR, FP16+GradScaler, grad accum, atomic ckpt, RNG, finalize gate) + InstructionTuningEngine |
| `core01/dataset.py` | TextDataset + PackedTextDataset + cache provenance |
| `core01/pretraining_driver.py` | CLI: `--train-file --val-file --device --precision --batch-size --gradient-accumulation-steps --learning-rate --warmup-steps --epochs --max-steps --checkpoint-interval --eval-interval --resume --seed` |
| `core01/tokenizer_interface.py`, `inference.py`, `evaluation.py` | tokenizer wrapper, generation, eval |
| `models/nexusai_core_01/config/model_config.py` | config (8,842,560 params) |
| `data/prepare_english_corpus.py` | corpus prep (needs pyarrow; local parquet only) |
| tokenizer `sp_bpe_8k.model`/`.vocab` | SentencePiece 8K |

## 5. Dataset & Artifact Inventory (Category C)

| Artifact | Where now | Reusable on Colab? |
|---|---|---|
| `english_train.jsonl` / `english_val.jsonl` (100.5M tok) | Kaggle `/kaggle/working/.../prepared_dataset/` | **YES if exported** — download from Kaggle Output or re-run prep |
| `manifest.json`, reports, dedup report | same | YES (provenance must travel with data) |
| FineWeb shard 0 parquet (2.0 GiB) | Kaggle `/kaggle/working/.../raw/` | optional — needed only to re-prep; re-download ~10 min |
| Tokenizer files | inside package ZIP | YES (also in repo) |
| Core-01 checkpoints | **none exist** | n/a — training hasn't run |
| Legacy checkpoints (2.47M params etc.) | repo `models/checkpoints*/` | NOT for Core-01 (different arch) — keep for legacy app only |

**Data safety:** the 100M corpus is the most valuable artifact — ~400 MB jsonl. Export to Google Drive BEFORE abandoning Kaggle, or accept ~30–60 min re-prep on Colab.

## 6. Dependency & Compatibility Findings (Category D)

| Need | Colab status | Action |
|---|---|---|
| Python 3.13 | ✅ 3.13.16 | none |
| torch + CUDA | ✅ 2.14.1+cu130, T4 | none — driver uses standard AMP APIs |
| sentencepiece | ⚠️ likely missing | `pip install sentencepiece` (small wheel) |
| pyarrow | ⚠️ needed only for prep | `pip install pyarrow` at prep stage |
| numpy | ✅ present | none |
| `/kaggle/*` paths | ❌ absent on Colab | confined to notebook layer — **code itself clean** |
| GPU memory | T4 14.56 GB, single GPU | fp16 + packed seqs; bs32×512 fits (verify in smoke) |
| Checkpoint storage | Colab ephemeral ~100+ GB disk; Drive for persistence | save ckpts to Drive-mounted dir |
| Drive mount | `google.colab.drive.mount('/content/drive')` | standard, owner-authorized |

**Hardcoded-path audit:** `grep -rn kaggle core01/ prepare_english_corpus.py` → only comments. `pretraining_driver.py` takes all paths via CLI args. **No code changes needed for Colab.**

## 7. Safe Kaggle Cleanup Recommendations

| Item | Verdict |
|---|---|
| `nexusai_core01_kaggle_package.zip` + extracted dir | **Keep until Colab verified** — it IS the migration payload |
| Kaggle Dataset `nexusai-core01-package` | Keep until Colab package integrity passes Cell-equivalent check |
| Prepared corpus on `/kaggle/working` | **Export to Drive first**, then Kaggle copy disposable |
| FineWeb shard on `/kaggle/working` | disposable after corpus exported (re-downloadable) |
| `nexusai_core01_fineweb_pretraining.ipynb` (repo) | **Keep** — reference for cell logic; Colab notebook will mirror its gates |
| Kaggle diagnostic notebooks/scripts | Keep in repo (history); unused on Colab |
| Legacy checkpoints/datasets | untouched — unrelated to Core-01 |

**Nothing should be deleted now.** Cleanup only after Colab training verified.

## 8. Google Colab Architecture

```
/content/drive/MyDrive/NexusAI/          ← persistent (survives disconnects)
├── package/nexusai_core01_kaggle_package/   ← uploaded ZIP, extracted once
├── data/english_train.jsonl, english_val.jsonl, manifest.json  ← corpus
├── tokenizer/sp_bpe_8k.model                  ← (also inside package)
├── checkpoints/                               ← training output (atomic ckpts)
├── logs/                                      ← training logs
└── reports/                                   ← session reports

/content/working (ephemeral)
└── optional: fineweb shard0 parquet (if re-prepping)
```

Rationale: Drive for anything that must survive session end (corpus, checkpoints, manifests); runtime disk for temp/shard.

## 9. Required Files for Migration

| File | Source | Transport |
|---|---|---|
| package ZIP (306,348 B) | repo `exports/` or Desktop copy | upload to Drive once |
| english_train/val.jsonl + manifest (~400 MB) | Kaggle Output download → Drive | manual download+upload |
| `sp_bpe_8k.model` | inside ZIP / repo | included |
| Colab notebook (new) | to be created (needs approval) | repo `docs/notebooks/` |

## 10. Missing / NOT VERIFIED

- Colab notebook does not exist yet — **MISSING** (needs approval to create)
- Corpus presence on Colab/Drive — **NOT VERIFIED**
- sentencepiece/pyarrow on Colab — **NOT VERIFIED** (install at runtime)
- Driver GPU path on Colab torch 2.14 — code uses standard APIs; **NOT field-tested**
- Whether Kaggle corpus still exists — **UNKNOWN** (working dir volatile)

## 11. Google Colab Notebook Cell Plan (proposed, ~18 cells)

| # | Cell | Does | Pass condition |
|---|---|---|---|
| 1 | md | overview + approval-gate explanation | — |
| 2 | code | env info: python/torch/cuda/GPU/disk/RAM | torch.cuda.is_available() |
| 3 | code | `drive.mount` + locate `/content/drive/MyDrive/NexusAI/package` | package dir found |
| 4 | code | extract ZIP if needed; verify sha256 `1b0c66f0…` | `PACKAGE_OK` |
| 5 | code | tokenizer load: vocab 8000, IDs, encode/decode | `TOKENIZER_OK` |
| 6 | code | dataset check: jsonl exist, manifest token count, overlap audit | `DATASET_OK` |
| 7 | code | VRAM estimate + batch-size sanity (model init on cuda:0, dummy fwd/bwd) | fits <14 GB |
| 8 | code | **`APPROVE_SMOKE_TEST=False`** gate → driver `--max-steps 200 --precision fp16 --device cuda` | finite loss, ckpt saved |
| 9 | code | smoke eval: loss curve, val_loss, tok/s, VRAM peak | owner reviews |
| 10 | code | **`APPROVE_FULL_TRAINING=False`** gate → full driver cmd | `checkpoint_final.pt` COMPLETED |
| 11 | code | ckpt verification: load fresh, param count 8,842,560, status field | verified |
| 12 | code | generation test (EN/BN/Banglish prompts — honest quality) | outputs logged |
| 13 | code | export ckpts+logs+manifest to Drive | files listed |
| 14 | code | session log table print | — |

## 12. Recommended Initial Training Strategy (estimates marked)

- Dataset: verified 100.5M tokens — suitable for first run.
- Model/arch: unchanged; 8.8M params is small — T4 fine.
- Sequence 512 (fixed), fp16 AMP (T4 sm_75, no bf16), AdamW, warmup-only LR (implemented), grad clip (implemented).
- Batch: start bs=32 micro × accum=1; if OOM → bs16 × accum2. **Measure in smoke — do not guess.**
- Smoke: `--max-steps 200` on real data → measure step time, tok/s, VRAM.
- Full: epochs≈1–3 over ~98.5M train tokens; steps ≈ tokens/(bs×512) ≈ 6k–18k optimizer steps (**estimate** — compute from measured tok/s).
- Checkpoint every 500 steps + epoch end; eval every 500.
- Colab free-tier session ~12h max — likely needs 1–3 sessions; `--resume checkpoint_last.pt` continues.

## 13. GPU Memory & Resources

- T4 14.56 GB; model 8.8M params (~35 MB fp32) + AdamW states (~105 MB) + activations dominate.
- bs32×512×6L fp16: expected to fit with headroom (**estimate** — smoke verifies).
- CPU RAM: corpus jsonl streaming OK; token cache `.npy` ~200 MB.

## 14. Data Safety & Backup Plan

1. **Now:** download Kaggle `prepared_dataset/` → upload to Drive `NexusAI/data/` (preserves manifest+hashes).
2. Checkpoints → Drive `checkpoints/` after every session.
3. Repo remains source of truth for code; Drive for artifacts.
4. Never delete Kaggle dataset until Colab package check passes.

## 15. Documentation Update Plan (after approval)

- New `docs/notebooks/nexusai_core01_colab_pretraining.ipynb`
- README: add Colab section mirroring Kaggle guide (keep Kaggle section as history)
- New `docs/architecture/audits/NEXUSAI_CORE01_COLAB_MIGRATION_REPORT.md` (this audit's home)
- Session log rows per real Colab session

## 16. Risks & Blockers

| Risk | Level | Mitigation |
|---|---|---|
| Corpus lost if Kaggle working wiped before export | **HIGH** | export to Drive FIRST |
| Colab disconnect mid-training | MED | ckpt→Drive every session; `--resume` |
| Colab free GPU availability/quotas | MED | T4 usually available; verify Cell 2 |
| sentencepiece wheel on py3.13 | LOW | pure-python+native wheel exists; install test |
| Driver untested on torch 2.14 | LOW | standard APIs; smoke verifies |
| Drive storage quota (~15 GB free tier) | MED | corpus 0.4 GB + ckpts ~0.2 GB each — fine |

## 17. Exact Next Steps (owner approval needed)

1. Export Kaggle `prepared_dataset/` → Google Drive `NexusAI/data/` (or approve re-prep on Colab).
2. Upload package ZIP → Drive `NexusAI/package/`.
3. Approve creation of Colab notebook (Cells 1–14 plan above).
4. Run Cells 2–7 verification → approve smoke (Cell 8) → review → approve full (Cell 10).

## 18. Final Readiness Assessment

**CONDITIONALLY READY** — code/package fully portable (VERIFIED); corpus transport is the only real dependency (action needed); Colab notebook not yet written (approval needed). Core-01 remains **UNTRAINED**.
