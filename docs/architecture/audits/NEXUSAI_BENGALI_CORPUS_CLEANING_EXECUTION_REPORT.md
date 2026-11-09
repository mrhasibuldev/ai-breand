# NEXUSAI — BENGALI CORPUS CLEANING EXECUTION REPORT

**Date:** 2026-11-09 · Scope: APPROVED Phase-1 cleaning only · No training, no ckpt/dataset modification

## PIPELINE
`packages/ai-core/data/clean_bangla_batch1_v2.py` — deterministic, streaming, SHA-256 dedup, HTML unescape+strip, boilerplate filter, repetition filter (>60% unique-word loss rejected), min 40 chars, Bengali-script ratio ≥0.30 or Banglish, per-record license/provenance metadata, reject logs preserved.

## RESULTS (actual sp_bpe_8k token counts)

| Source | Read | Kept | Keep% | Cleaned tokens | Rejects (top) |
|---|---|---|---|---|---|
| bangla_wikipedia_mit | 171,674 | **168,962** | 98.4% | **112,907,557** | repetitive 1,103 · short 1,585 · non_bn 20 |
| sangraha_bengali (partial) | 9,206 | **9,172** | 99.6% | **7,635,793** | repetitive 29 · non_bn 5 |
| bongchat_v1 | 150,000 | **113,446** | 75.6% | **13,363,972** | exact_dup 22,719 · short 7,739 · non_bn 5,777 |
| **TOTAL** | **330,880** | **291,580** | 88.1% | **133,907,322** | |

Language dist (kept): bn_only ~248K · mixed ~44K · en_only ~0.

## OUTPUT FILES (new, raw untouched)
- `packages/ai-core/data/cleaned_bangla/bangla_wikipedia_mit.jsonl` (844MB)
- `.../sangraha_bengali.jsonl` (53MB)
- `.../bongchat_v1.jsonl` (136MB)
- `.../*_rejects.jsonl` audit logs + `cleaning_report.json`

## VALIDATION
- Raw files unchanged (sizes identical: 1,006,893,818 / 61,948,225 / 185,371,800 B) ✅
- Samples verified: clean Bengali prose, Bangla punctuation intact, license fields present ✅
- Tokenizer: all outputs encoded during cleaning, 0 errors ✅
- Disk: 6.1GB → 5.1GB free ✅

## TOKEN DEFINITIONS
- Raw tokens (pre-clean): ~148.4M · Cleaned tokens: **133.9M** · Unique docs: 291,580 (exact-dup removed)
- **Eligible training tokens: ~133.9M** (before train/val/test split)

## UNRESOLVED
- Near-duplicate (non-exact) detection: conservative only — not implemented (MinHash deferred)
- Wikipedia content license is CC BY-SA 3.0 (packaging MIT) — attribution required in model card
- Sangraha still partial (9,206 of ~77GB corpus)
- BanglaCoRe-5000 gated — excluded

## READINESS
Cleaned corpus **ready for Run4 readiness review** (separate approval needed). Raw data preserved; no overwrites.
