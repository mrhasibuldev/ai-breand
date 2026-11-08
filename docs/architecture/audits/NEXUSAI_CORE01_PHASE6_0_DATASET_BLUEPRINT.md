# NexusAI Core-01 — Phase 6.0: English-First Dataset Acquisition & Preparation Blueprint

**Date:** 2026-11-07 · **Status:** PLANNING ONLY — no downloads, no code changes, no GPU, no training.
**Target:** ~100M English tokens counted by `sp_bpe_8k.model` (Core-01 tokenizer, vocab 8,000).

---

## 1. Executive Summary

- FineWeb `sample-10BT` verified via HF API: **15 Parquet shards**, each **~2.15 GB** (~32 GB total for ~10B GPT-2 tokens). **We need only a fraction of ONE shard** — download shard `0.parquet` (~2.1 GB) and stop mid-stream at 100M Core-01 tokens.
- HF resolve endpoint supports **HTTP Range (206 verified)** — partial/shard-level access is possible; full-corpus download is unnecessary.
- License: **ODC-By 1.0 + CommonCrawl ToS** — attribution required; underlying page copyrights remain with authors. NOT license-free.
- Recommended execution: **Kaggle CPU notebook** (local C: has only ~5.6 GB free — insufficient margin for 2.1 GB raw + outputs).
- All token counts MUST be measured with `sp_bpe_8k` — GPT-2 counts are not transferable.

## 2. Verified Dataset Sources

| Source | Repo / URL | Structure (verified) | License | Verdict |
|---|---|---|---|---|
| **FineWeb sample-10BT** | `huggingface.co/datasets/HuggingFaceFW/fineweb` (config `sample-10BT`) | 15 shards `train/0..14.parquet`, each ~2.147 GB (HEAD-verified shard 0) | ODC-By 1.0 + CC ToS | **PRIMARY** |
| FineWeb default | same repo, config `default` | thousands of shards under `data/CC-MAIN-*/` | same | not needed |
| C4 `en` | `allenai/c4` | parquet, 305 GB | ODC-By + CC ToS | backup/supplement |
| DCLM-baseline-1.0 | `mlfoundations/dclm-baseline-1.0` | ~780k docs parquet | CC-BY-4.0 | supplement (attribution) |
| English Wikipedia | dumps.wikimedia.org | XML dump | CC BY-SA 3.0/4.0 | supplement (share-alike) |
| Project Gutenberg | gutenberg.org | ~70k books | public domain | supplement |
| OpenWebText2 / Books3 / The Pile | — | — | UNVERIFIED/mixed | **EXCLUDED** |

FineWeb-Edu (`HuggingFaceFW/fineweb-edu`) exists (1.3T educational tokens, same ODC-By) — optional future supplement, not needed for 100M.

## 3. Licensing & Attribution Obligations

- **ODC-By 1.0**: attribution required when publicly conveying/using the database; share the dataset name + license notice.
- **CommonCrawl ToS**: applies to crawled content; users bear responsibility for downstream use; robots/opt-out signals honored upstream by FineWeb curation.
- **Honest caveat**: web corpora contain copyrighted text; ODC-By does not clear page-level copyrights. For a research/personal model this is the standard accepted risk profile (same as C4/DCLM/FineWeb used by all open LLMs). Owner should acknowledge this explicitly.
- Action: corpus manifest will record `source=HuggingFaceFW/fineweb, config=sample-10BT, license=ODC-By-1.0+CC-ToS, attribution="FineWeb by Hugging Face"`.

## 4. Exact FineWeb Subset Strategy

**Shard-0 bounded extraction:**
1. Download ONLY `sample-10BT/train/0.parquet` (~2.15 GB) — HF API URL verified resolving (HTTP 200, `application/octet-stream`, Range supported).
2. Read with `pyarrow.parquet.ParquetFile` → iterate **row groups** (or record batches); FineWeb rows have `text`, `id`, `dump`, `url`, `date`, `file_path`, `language` fields (language already `en`-filtered upstream).
3. For each document: clean → exact-dedup check → tokenize-count with `sp_bpe_8k` → accumulate; **stop when cumulative tokens ≥ 100,000,000** (plus small overshoot buffer, e.g. +0.5%, to allow val split rounding).
4. Expected yield: shard 0 holds ~650–700M GPT-2 tokens; at our ~0.29 tok/char ratio vs GPT-2's ~0.25–0.3, **100M Core-01 tokens ≈ 15–25% of shard 0** → download stays ~2.1 GB, processing reads only the needed prefix (can even abort parquet iteration early — no need to read remaining row groups).
5. **Reproducibility**: fixed shard list `[0]`, fixed row-group order, seeded doc-level split (seed=42), manifest records shard filename + sha256 + rows consumed + token count.

Alternative considered — **HTTP streaming without full download**: Range requests work, but Parquet needs footer+metadata; pyarrow can do partial reads but row-group-level random access over HTTP is fragile on HF CDN. **Selected-shard download is more practical** for Kaggle CPU (2.1 GB is trivial there).

## 5. 100M Token Counting Method (Core-01 tokenizer)

```
total_tokens = 0
for doc in parquet_row_groups(shard0):
    text = clean(doc.text)
    if not acceptable(text): continue
    n = len(tokenizer.sp.encode(text, out_type=int))   # raw sp count, no BOS/EOS
    total_tokens += n
    emit(text)  # to cleaned corpus file
    if total_tokens >= TARGET + BUFFER: break
```

- Count **raw SentencePiece pieces** (no BOS/EOS) for the target; PackedTextDataset adds BOS/EOS later (~2 tokens/doc overhead, negligible at ~1M docs).
- Final verification pass re-counts emitted corpus with the same tokenizer and asserts `0.98 ≤ actual/target ≤ 1.05`.
- Cross-check: also record GPT-2-style char/token ratio for the manifest (informational only).

## 6. Data Quality Plan

FineWeb is already heavily filtered upstream (language ID, heuristic filters, MinHash dedup). Our prep adds a **light verification layer** — do NOT re-do what upstream did expensively:

| Stage | Rule | Implementation |
|---|---|---|
| Language | English-only | upstream `language='en'` + optional fastText check (skip — adds dep; sample-audit instead) |
| Empty/malformed | drop empty, non-text, binary-garbage (replacement-char ratio >2%) | regex/char checks |
| HTML/boilerplate | strip residual tags (`<[^>]+>`), collapse >2 consecutive newlines | regex |
| Whitespace | NFC normalize, collapse runs of spaces/tabs, strip | `unicodedata` + regex |
| Length | min 200 chars, max 200k chars (split longer docs at paragraph boundary, don't drop content) | char count |
| Exact dedup | sha1/sha256 of normalized text → set | streaming hash set (~1M docs → ~100MB RAM ok) |
| Near-dup | **skip** — FineWeb already MinHash-dedup'd; document this decision | n/a |
| Spam/low-quality | drop docs with >50% uppercase, >30% digits-only lines, lorem-ipsum markers | heuristics |
| Split | doc-level seeded shuffle → **1.5% val** (~1.5M tokens), rest train | `random.Random(42)` |
| Tokenize | `sp_bpe_8k` count above | SentencePiece |
| Packing compat | emit plain text lines → `PackedTextDataset` consumes directly | existing code |

No Bengali/Banglish in this corpus — English-only by design.

## 7. Train/Validation Strategy

- Document-level split BEFORE any packing → zero leakage (PackedTextDataset packs each split independently; verified design).
- Val ≈ **1.5%** (~1.5M tokens ≈ ~3k packed blocks) — enough for stable val_loss, small enough to matter little.
- Deterministic: seed 42; manifest stores the shuffle seed + split counts.

## 8. Storage Estimates (measured vs estimate)

| Item | Size | Basis |
|---|---|---|
| Raw shard 0 parquet | **2,147,292,183 B (~2.0 GiB) MEASURED** (Content-Length) | HF HEAD |
| Cleaned text corpus | ~350–450 MB | ESTIMATE: 100M tok ÷ ~0.29 tok/char ≈ 345M chars |
| Token uint16 cache (if used) | 200 MB | 100M × 2B — PackedTextDataset builds its own `.npy` anyway |
| Train/val text outputs | ~400 MB total | same as cleaned |
| Provenance manifest | <1 MB | json |
| Temp/processing | <500 MB | row-group buffers |
| **Total Kaggle working** | **~3.5 GB peak** | well under any plausible quota |

**Local C: (~5.6 GB free): NOT recommended** — raw shard alone is 2.1 GB and outputs push past safe margin. **Kaggle CPU it is.** Kaggle working-dir quota: UNVERIFIED — check `df -h /kaggle/working` in-notebook; our need ~3.5 GB is safe under the commonly cited ~20 GB.

## 9. Kaggle CPU Execution Plan

1. Notebook (CPU-only accelerator — **no GPU quota consumed**): upload `nexusai_core01_kaggle_package.zip` as Input (already built, contains tokenizer+driver+PackedTextDataset).
2. `pip install pyarrow pandas` (or use preinstalled; verify in-notebook).
3. Download shard 0 via `huggingface_hub.hf_hub_download(repo_id='HuggingFaceFW/fineweb', filename='data/...'? — NOTE: sample-10BT parquet lives under the auto-converted `refs/convert/parquet` tree; the API URL `.../parquet/sample-10BT/train/0.parquet` resolves directly — use `requests`/`urllib` on that URL or `hf_hub_download` with `repo_type='dataset'` + revision `refs/convert/parquet`)].
4. Run prep script → outputs `english_train.txt`, `english_val.txt`, `corpus_manifest.json` in `/kaggle/working/`.
5. Optionally attach outputs as Kaggle Dataset output for the later GPU run.
6. GPU session reserved ONLY for the actual pretraining run (separate notebook/session).

## 10. Proposed Script Architecture (NOT implemented)

`packages/ai-core/data/prepare_english_corpus.py` (future, needs approval):

```
--source fineweb --config sample-10BT --shards 0 \
--target-tokens 100000000 --buffer 0.005 \
--tokenizer <path>/sp_bpe_8k.model \
--output-dir <dir> --seed 42 --val-fraction 0.015 \
--min-chars 200 --max-chars 200000 --dedup exact
```

Stages: `download_shard → iterate_row_groups → clean → dedup → count_tokens → split → write_txt → verify_count → write_manifest(sha256 per file + provenance)`.
Resume-safety: checkpoint progress file (`prep_state.json` with last completed row-group + running token count) so a Kaggle session timeout doesn't restart from zero.

## 11. Remaining Risks

- FineWeb content = CommonCrawl web text — residual noise possible despite upstream filtering; light heuristics mitigate, not eliminate.
- Copyright caveat (ODC-By §2.4) — owner acknowledgment needed.
- `pyarrow` availability on Kaggle — verify in-notebook (`pip install pyarrow` fallback).
- Token-count ratio GPT-2 vs sp_bpe_8k unknown until measured — the script measures actual; shard-0 fraction needed is an estimate (~15–25%).
- Kaggle session timeout (9–12h) — prep should take <1h; resume-state file covers interruption.
- No Bengali in this corpus — future phases need separate approved sources.

## 12. Exact Owner Approvals Required

1. Approve FineWeb `sample-10BT` shard-0 download (~2.1 GB) on Kaggle CPU + ODC-By attribution acceptance.
2. Approve corpus-prep script implementation (new file, no core changes).
3. Approve running prep on Kaggle CPU (no GPU).
4. Later: approve GPU stage-0/real run separately.

## Decision

**READY FOR OWNER APPROVAL** — source verified, sizing confirmed (one shard suffices), license documented, storage plan fits Kaggle CPU, no code written yet.
