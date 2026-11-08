# NexusAI Core-01 — Google Colab Setup Guide (Kaggle-free)

**Goal:** everything happens inside Google Colab — clone GitHub → download FineWeb → prepare 100M-token corpus → GPU train. **Kaggle is not used.**
**Notebook:** `docs/notebooks/NexusAI_Core01_Google_Colab_Training.ipynb` (43 cells, 21 code).
**Verified env (owner, historical):** Python 3.13.16 · torch 2.14.1+cu130 · CUDA True · 1× Tesla T4. Re-verified every run in Cell 2.
**Repo:** `https://github.com/mrhasibuldev/ai-breand` — **PUBLIC** (anonymous clone works, verified via `git ls-remote`).

---

## Part 1 — What you need BEFORE starting

| Item | Where | Notes |
|---|---|---|
| Google account | colab.research.google.com | same account owns Drive |
| Repo access | public GitHub | no token/password needed |
| ~6 GB free Colab disk | checked in Cell 7 | shard 2.1 GB + corpus ~0.5 GB + ckpts |
| Internet | Colab default ON | needed for clone + FineWeb download |

**Nothing to download/upload manually.** The notebook clones the repo and downloads FineWeb itself.

## Part 2 — Start the notebook

1. Open **https://colab.research.google.com/** → sign in.
2. **File → Upload notebook** → select `NexusAI_Core01_Google_Colab_Training.ipynb` (from repo `docs/notebooks/` — download it from GitHub first if needed).
3. **Runtime → Change runtime type → T4 GPU** (needed from Cell 15 onward; CPU cells work either way).
4. Run cells **top to bottom, one at a time** (Shift+Enter). Read each markdown cell before running its code.

## Part 3 — Cell-by-cell guide

| Cells | Title | Run? | Expected output | If it fails |
|---|---|---|---|---|
| 1 | Overview | read | — | — |
| 2 | Env check | ✅ | python/torch/CUDA/GPU/disk printed | missing deps noted for Cell 4 |
| 3 | Git clone | ✅ | `commit: a0ca7ce…`, `CLONE_OK = True` | no internet → check Colab connection; repo moved → tell developer |
| 4 | Deps install | ✅ | `sentencepiece x.y | pyarrow x.y` | pip error → retry; network issue |
| 5 | Import check | ✅ | `all core01 imports OK`, `params: 8842560` | ImportError → dep missing, re-run Cell 4 |
| 6 | Drive mount | ✅ | folder tree printed, `DRIVE_OK = True` | auth popup → approve Drive access |
| 7 | Storage check | ✅ | `STORAGE_OK = True` (needs ~6 GB) | free space / wait for new runtime |
| 8 | FineWeb verify | ✅ | `license: odc-by`, `shards: 15`, `shard0 ~2.0 GiB`, `FINEWEB_OK = True` | internet off / HF down → retry later |
| 9 | **Dataset prep gate** | ⏸ set `APPROVE_DATASET_PREPARATION=True` only after reading | download ~2 GiB + prep ~30–60 min | see Part 5 |
| 10 | Dataset audit | ✅ after Cell 9 | `train: 103,846 docs / ~99M tokens`, `overlap: 0`, `DATASET_OK = True` | counts off → STOP, send output |
| 11 | Drive backup | ✅ | `copied english_*.jsonl` → `NexusAI/data/` | Drive full → free space |
| 12 | Tokenizer | ✅ | `vocab: 8000`, decode ok | assertion → wrong tokenizer path |
| 13 | Model config | ✅ | `MODEL_CFG_OK = True` (6L/8H/256/1024/512/8000) | mismatch → STOP, architecture changed? |
| 14 | Model init+forward | ✅ | `params: 8842560`, logits shape ok | OOM on CPU → use GPU runtime |
| 15 | GPU verify | ✅ (needs T4) | `gpu: Tesla T4`, `peak VRAM ~x GB`, `GPU_OK = True` | CUDA unavailable → Runtime → T4 |
| 16 | Config review | ✅ | prints smoke command | — read-only |
| 17 | **Smoke test gate** | ⏸ `APPROVE_SMOKE_TEST=True` after review | ~200 steps, loss ↓, ckpts in Drive | OOM → bs16+accum2 |
| 18 | Smoke eval | ✅ | ckpt list + status printed | no ckpts → smoke failed |
| 19 | **Full training gate** | ⏸ `APPROVE_FULL_TRAINING=True` only after good smoke | real run, ckpts→Drive every 500 steps | session cut → Part 6 resume |
| 20 | Checkpoint verify | ✅ after training | status/step/RNG/scaler printed | — |
| 21 | Generation test | ✅ after training | English continuations | inference error → send output |
| 22 | Session report | ✅ always end | status table → paste in README log | — |

## Part 4 — The three approval gates

```python
APPROVE_DATASET_PREPARATION = False   # Cell 9  — downloads shard + builds corpus
APPROVE_SMOKE_TEST          = False   # Cell 17 — ~200-step GPU pipeline test
APPROVE_FULL_TRAINING       = False   # Cell 19 — real pretraining
```

Enable **one at a time**, only when that stage is next. Never all together.

## Part 5 — Dataset prep details (what Cell 9 does)

- Downloads **only** `sample-10BT/train/0.parquet` (~2.0 GiB) — streaming, `.part`→rename, size+SHA-256 verified
- Runs **our unmodified** `prepare_english_corpus.py`: clean → exact-dedup → count with real `sp_bpe_8k` → stop at 100M+0.5% → doc-level 98.5/1.5 split seed 42
- Historical proof: same shard produced **100,499,546 tokens** (Kaggle run) — expect ~100.5M again
- Outputs → `/content/work/.../prepared_dataset/` → backed up to Drive `NexusAI/data/`

## Part 6 — Session disconnect & resume

Colab kills sessions (~12h). Everything valuable is on Drive:

1. New session → same notebook → Runtime T4.
2. Re-run Cells 2–16 (re-verify; variables don't persist).
3. Cell 19 driver command: append `--resume checkpoint_last.pt` (file lives in `checkpoints_full/` = `--output-dir`).
4. Resume is approximate (epoch-granular) — documented limitation.

## Part 7 — Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `git clone failed` | no internet / repo moved | check Colab connection; verify repo URL |
| `ImportError` | dep missing | re-run Cell 4 |
| `PACKAGE`/`CLONE_OK` assert | files missing in clone | re-run Cell 3 |
| `MISSING dataset files` / prep exit≠0 | download/prep failed | check Cell 9 output; disk space |
| `DATASET_OK` overlap>0 | split bug | STOP — send manifest |
| tokens ≪100M | shard short (unlikely — proven) | report; approve shard 1 manually |
| `CUDA unavailable` | CPU runtime | Runtime → T4 GPU |
| OOM smoke | batch too big | `--batch-size 16 --gradient-accumulation-steps 2` |
| Session dies mid-train | Colab limit | Part 6 resume |
| `NameError`/lost vars | kernel restarted | re-run setup cells in order |

## Part 8 — Honesty notes

- FineWeb = **text data only** (ODC-By 1.0, attribution "FineWeb by Hugging Face" + CC ToS). Not an AI model.
- Corpus counts are **real SentencePiece counts**, never GPT-2 estimates.
- Smoke success ≠ trained model. Trained = `checkpoint_final.pt` + `PRETRAINING_COMPLETED`.
- 100M English-only tokens → weak Bengali/Banglish expected.
- Core-01 remains **UNTRAINED** until full training completes.
