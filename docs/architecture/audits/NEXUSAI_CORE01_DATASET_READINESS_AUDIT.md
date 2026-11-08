# NexusAI Core-01 — Dataset Readiness Audit

**Date:** 2026-11-08 · **Mode:** read-only · Tokenizer-level stats measured locally; corpus files live on Drive/Kaggle (not locally accessible).

## 1. Dataset inventory

| Dataset | Location | Status |
|---|---|---|
| `english_train.jsonl` (~103,846 docs / ~99M tok) | Drive `NexusAI/data/` (ex-Kaggle) | **NOT locally auditable** — use `COLAB_DATASET_AUDIT_CELL.py` |
| `english_val.jsonl` (~1,581 docs / ~1.49M tok) | same | same |
| `manifest.json` + reports | same | same |
| FineWeb `sample-10BT` shard0 (source) | Colab temp / re-downloadable | provenance ODC-By 1.0 |
| Bengali repo files (phase9_1 cleaned, phase9_2 corpus, phase7) | local repo | **~220KB total — tiny** |

## 2. Measured tokenizer stats (local, real SentencePiece)

- vocab_size = **8000** · PAD=0 UNK=1 BOS=2 EOS=3 — matches model config ✅
- Sampled ~1.0M chars across repo language files → **289,589 tokens**, **UNK rate 1.06%**
- Bengali probe sentence: **0 UNK / 20 tokens** — tokenizer covers Bengali script
- English corpus: real counts exist in manifest (100,499,546 total) — historical VERIFIED

## 3. Language coverage — HONEST VERDICT

| Language | Data available | Sufficiency |
|---|---|---|
| English | ~100M tokens (FineWeb) | ✅ good for pretraining |
| Bengali | ~220KB jsonl/txt (~tens of K tokens) | ❌ **~0.05% of corpus — insufficient** |
| Banglish | essentially none dedicated | ❌ gap |
| Mixed BN-EN | minimal | ❌ gap |

**Conclusion:** English-only pretraining will produce an English-leaning model. Bengali input→Bengali output, Banglish understanding, and identity ("Hasibul") will NOT be reliably learned from current data. A separate Bengali/Banglish acquisition + SFT phase is required — documented, not fabricated.

## 4. Quality checks (repo files, measured)

- phase9_1 cleaned jsonl: valid records, small scale
- Duplicates/empties/leakage on the 100M corpus: **NOT VERIFIED locally** — audit cell checks overlap/dup/empty on Drive
- EOS-per-doc concatenation + pad-ignore loss: code-verified

## 5. Upgraded Colab audit cell (prepared, NOT yet executed)

`docs/notebooks/COLAB_DATASET_AUDIT_CELL.py` now performs, on the real Drive corpus:

- **Real SentencePiece token counts** (not ntok-field or file-size estimates) for every doc
- Per-doc language heuristic buckets: `english / bengali / mixed_bn_en / other / bengali_latin_mix` (romanized-Bengali = UNCERTAIN, not fabricated)
- Sequence-length distribution: avg, p50, p95, max tokens
- UNK-token rate (exact, tokenizer-level)
- Duplicates (exact set), empty/malformed records, bad JSON
- **Exact train/val overlap** (set intersection)
- Manifest cross-check: manifest token total vs independent recount
- File SHA-256 (small files) + sizes + timestamps
- Outputs: `dataset_audit_<ts>.json` + `.md` → `Drive/NexusAI/audit_reports/`

**Limitations:** romanized Banglish is charset-indistinguishable from English → counted as `english` (UNCERTAIN, honestly labeled); ~100M-token recount takes tens of minutes on Colab CPU.

## 6. Readiness classification

| Scope | Status |
|---|---|
| English pretraining corpus | **READY WITH LIMITATIONS** — pending Colab audit cell execution to confirm counts/leakage on actual Drive files |
| Bengali/Banglish/mixed | **NOT READY** — dedicated data absent (~220KB repo files); separate acquisition phase required |
| Tokenizer | **READY** (vocab 8000, Bengali script covered, UNK ~1%) |
| Overall multilingual goal | **NOT READY** |

**Final: `READY WITH LIMITATIONS` for English-only pretraining; `NOT READY` for multilingual objectives.**
