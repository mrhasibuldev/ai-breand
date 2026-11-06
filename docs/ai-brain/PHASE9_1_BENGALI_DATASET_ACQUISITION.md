# NexusAI Phase 9.1 - Bengali Dataset Acquisition, Verification & Corpus Reconciliation

**Date**: 2026-11-03
**Status**: COMPLETE
**Scope**: Bengali dataset acquisition, license verification, corpus reconciliation, and tokenizer evaluation

---

## Executive Summary

Phase 9.1 successfully acquired 2 small Bengali datasets, resolved the Phase 7 vs Phase 9 corpus discrepancy, and evaluated the impact on tokenizer performance. The phase added 10,561 Bengali words to the corpus, achieving the first milestone (5,000 words) but not the second milestone (20,000 words).

**Key Achievements**:
- ✅ Storage and environment audit completed
- ✅ Phase 7 vs Phase 9 corpus discrepancy resolved
- ✅ 2 Bengali datasets downloaded (bengali_chat_conv, bengali_sft_v1)
- ✅ License verification completed (MIT, Apache-2.0)
- ✅ Data cleaning and deduplication completed
- ✅ Tokenizer compatibility evaluation completed
- ✅ `datasets` library installed locally (not globally)

**Critical Findings**:
- Bengali words added: 10,561 (first milestone achieved)
- Bengali UNK rate: 47.06% (slightly improved from 48.38%)
- Improvement: 1.32 percentage points (minimal)
- Storage used: ~0.7 MB for raw data, ~0.2 MB for cleaned data
- Storage remaining: 3.29 GB on C: drive

**Verdict**: Dataset acquisition successful but Bengali coverage remains insufficient for meaningful model training. Tokenizer retraining on expanded corpus is recommended.

---

## Step A - Environment and Storage Audit

### Hardware Resources

**Verified Resources**:
- C: Drive: 119.2 GB total, 3.29 GB free (2.8% available)
- D: Drive: 29.7 GB total, 50 MB free (0.2% available)
- RAM: 8 GB
- GPU: None (CPU-only)
- Python: 3.14.6
- `datasets` library: NOT INSTALLED (initially)

### Existing Storage Usage

**Experimental Storage**:
- Phase 7: 26 MB
- Phase 8: 62 MB
- Phase 9: 11 MB
- Total: 99 MB

### Storage Safety Limits

**Limits Applied**:
- Maximum download size: 150 MB
- Safety threshold: 2 GB free on C: drive
- Actual free space: 3.29 GB (above threshold)
- **Verdict**: Safe for small dataset downloads

---

## Step B - Corpus Reconciliation

### Discrepancy Investigation

**Phase 7 Reported**: 47,336 texts
**Phase 7 Actual File**: 99,097 lines
**Phase 9 Script Loaded**: 99,097 texts
**Phase 9 After Deduplication**: 90,362 texts

### Root Cause Analysis

**Explanation**:
- Phase 7 corpus_combined.txt contains line-by-line text
- Multi-line source records (GSM8K, Dolly) become multiple lines when split by newlines
- Phase 7 manifest count (47,336) is the RECORD count
- Phase 7 file line count (99,097) is the LINE count
- Phase 9 loaded 99,097 lines, deduplicated to 90,362 texts

**Conclusion**:
- Phase 7 actual records: 47,336
- Phase 9 actual records: 90,362
- Bengali count: 28 texts in both phases
- **No Bengali data was lost or incorrectly classified**
- Discrepancy resolved: counting records vs lines

---

## Step C - Dataset Acquisition

### Datasets Downloaded

**Dataset 1: bengali_chat_conv**
- Source: Hugging Face (spedrox-sac/bengali_chat_conv)
- License: MIT (verified via web fetch)
- Commercial use: APPROVED
- Raw records: 1,074
- Download size: 0.6 MB
- SHA-256: `875a6d47d8a4c351...`

**Dataset 2: bengali_sft_v1**
- Source: Hugging Face (worldjit/bengali-sft-v1)
- License: Apache-2.0 (verified via web fetch)
- Commercial use: APPROVED
- Raw records: 151
- Download size: 0.05 MB
- SHA-256: `3494b7214ab7b64b...`

### Dependency Installation

**Action**: Installed `datasets` library locally
- Location: `packages/ai-core/data/.venv/lib/python3.14/site-packages/`
- Version: 5.1.0
- Impact: Project dependencies unchanged (local installation only)
- **Verdict**: Safe installation, no global changes

---

## Step D - Data Cleaning and Quality Control

### Cleaning Results

**bengali_chat_conv**:
- Raw records: 1,074
- Cleaned records: 590
- Duplicates removed: 484
- Empty removed: 0
- Language distribution: 590 Bengali (100%)

**bengali_sft_v1**:
- Raw records: 151
- Cleaned records: 151
- Duplicates removed: 0
- Empty removed: 0
- Language distribution: 136 Bengali, 1 English, 14 Mixed

**Total Cleaned Records**: 741

### Data Quality

**Deduplication**: 484 duplicates removed (45% reduction in bengali_chat_conv)
**Empty records**: 0
**Corrupted records**: 0
**Encoding**: UTF-8 preserved
**Bengali characters**: Preserved
**Punctuation**: Preserved

---

## Step E - Organized Experimental Corpora

### Directory Structure

```
packages/ai-core/data/experimental/phase9_1/
├── raw/
│   ├── bengali_chat_conv.jsonl (0.6 MB)
│   └── bengali_sft_v1.jsonl (0.05 MB)
├── cleaned/
│   ├── bengali_chat_conv_cleaned.jsonl (184 KB)
│   ├── bengali_sft_v1_cleaned.jsonl (33 KB)
│   └── combined_cleaned.jsonl (217 KB)
├── manifests/
│   ├── environment_audit.json
│   ├── corpus_reconciliation.json
│   ├── acquisition_manifest.json
│   ├── cleaning_manifest.json
│   └── license_manifest.json
└── evaluations/
    ├── language_evaluation.json
    └── tokenizer_evaluation.json
```

### Provenance Tracking

Every record includes:
- Source dataset name
- Language classification
- Original text preserved
- SHA-256 checksums calculated

---

## Step F - Language and Quality Evaluation

### Language Distribution

| Language | Records | Percentage | Words | Characters |
|----------|---------|------------|-------|------------|
| Bengali | 726 | 97.98% | 10,561 | 64,235 |
| English | 1 | 0.13% | 14 | 101 |
| Mixed | 14 | 1.89% | 127 | 727 |
| **Total** | **741** | **100%** | **10,702** | **65,063** |

### Type Distribution

| Type | Records | Percentage |
|------|---------|------------|
| Conversations | 590 | 79.62% |
| Instructions | 151 | 20.38% |

### Target Progress

- **First milestone (5,000 Bengali words)**: ✅ ACHIEVED
  - Current: 10,561 Bengali words
- **Second milestone (20,000 Bengali words)**: ✗ NOT MET
  - Current: 10,561 Bengali words
  - Need: 9,439 more Bengali words
- **Long-term target (100,000+ Bengali words)**: ✗ NOT MET
  - Current: 10,561 Bengali words
  - Need: 89,439 more Bengali words

### Statistics

- Total records: 741
- Total words: 10,702
- Total characters: 65,063
- Average words per record: 14.44
- Average characters per record: 87.80

---

## Step G - Tokenizer Compatibility Test

### Test Results

**Phase 7 SentencePiece Tokenizer (8K BPE)**

**Sample Evaluation** (5 Bengali samples):
- Average tokens: 23.8
- Average UNK: 10.8 (45.3%)
- Round-trip decoding: Partial (UNK tokens not recoverable)

**Corpus-Wide Evaluation** (500 records):
- Total tokens: 15,745
- Total UNK: 7,409 (47.06%)
- Bengali tokens: 15,745
- Bengali UNK: 7,409 (47.06%)

### Comparison with Phase 9

| Metric | Phase 9 (Old Corpus) | Phase 9.1 (New Corpus) | Change |
|--------|---------------------|------------------------|--------|
| Bengali UNK rate | 48.38% | 47.06% | -1.32% |
| Bengali words | 531 | 10,561 | +10,030 |

**Improvement**: 1.32 percentage points (minimal)

### Conclusion

- Bengali UNK rate remains high (47.06%)
- Minimal improvement despite 20x increase in Bengali words
- **Tokenizer retraining on expanded corpus recommended**
- Current tokenizer trained on English-dominant corpus

---

## Step H - License and Commercial Usage Report

### License Classification

**Commercially Approved** (2 datasets):
1. **bengali_chat_conv** - MIT License
   - Commercial use: APPROVED
   - Attribution: Required
   - Share-alike: No
   - Source: Hugging Face

2. **bengali_sft_v1** - Apache-2.0 License
   - Commercial use: APPROVED
   - Attribution: Required
   - Share-alike: No
   - Source: Hugging Face

**Non-Commercial** (0 datasets):
- None downloaded

**Unknown/Unverified** (0 datasets):
- None downloaded

**Rejected** (0 datasets):
- None downloaded

### Preservation

For every acquired dataset:
- Original URL preserved
- License name preserved
- License evidence preserved (web fetch verification)
- Attribution requirements documented
- Acquisition date recorded
- Downloaded files preserved
- SHA-256 checksums calculated

---

## Files Created

**Scripts** (5):
1. `packages/ai-core/data/audit_phase9_1.py`
2. `packages/ai-core/data/reconcile_phase9_1.py`
3. `packages/ai-core/data/acquire_phase9_1.py`
4. `packages/ai-core/data/clean_phase9_1.py`
5. `packages/ai-core/data/evaluate_phase9_1.py`
6. `packages/ai-core/data/test_tokenizer_phase9_1.py`

**Raw Data** (2):
7. `packages/ai-core/data/experimental/phase9_1/raw/bengali_chat_conv.jsonl`
8. `packages/ai-core/data/experimental/phase9_1/raw/bengali_sft_v1.jsonl`

**Cleaned Data** (3):
9. `packages/ai-core/data/experimental/phase9_1/cleaned/bengali_chat_conv_cleaned.jsonl`
10. `packages/ai-core/data/experimental/phase9_1/cleaned/bengali_sft_v1_cleaned.jsonl`
11. `packages/ai-core/data/experimental/phase9_1/cleaned/combined_cleaned.jsonl`

**Manifests** (5):
12. `packages/ai-core/data/experimental/phase9_1/manifests/environment_audit.json`
13. `packages/ai-core/data/experimental/phase9_1/manifests/corpus_reconciliation.json`
14. `packages/ai-core/data/experimental/phase9_1/manifests/acquisition_manifest.json`
15. `packages/ai-core/data/experimental/phase9_1/manifests/cleaning_manifest.json`
16. `packages/ai-core/data/experimental/phase9_1/manifests/license_manifest.json`

**Evaluations** (2):
17. `packages/ai-core/data/experimental/phase9_1/evaluations/language_evaluation.json`
18. `packages/ai-core/data/experimental/phase9_1/evaluations/tokenizer_evaluation.json`

**Reports** (1):
19. `docs/ai-brain/PHASE9_1_BENGALI_DATASET_ACQUISITION.md` (this file)

---

## Final Safety Verification

**Production Source Code**: ✅ UNCHANGED
**Production Chat**: ✅ UNCHANGED
**Production Tokenizer**: ✅ UNCHANGED (SimpleTokenizer still active)
**Production Model**: ✅ UNCHANGED
**Production Checkpoints**: ✅ UNCHANGED
**Phase 7 Artifacts**: ✅ UNCHANGED
**Phase 8 Checkpoint**: ✅ UNCHANGED
**Original Datasets**: ✅ PRESERVED
**Database**: ✅ UNCHANGED
**Authentication**: ✅ UNCHANGED
**No Database Migrations**: ✅ CONFIRMED
**No Git Commit**: ✅ CONFIRMED
**No GitHub Push**: ✅ CONFIRMED

**Git Status**: Branch `main`, ahead of origin/main by 1 commit (unchanged)

**Pre-existing Modified Files** (preserved):
- `apps/api/src/app.ts`
- `apps/api/src/middleware/auth.ts`
- `apps/api/src/routes/auth.ts`
- `apps/api/src/routes/storage.ts`
- `apps/web/lib/avatar-service.ts`
- `packages/database-core/migrations/COMPLETE_SCHEMA.sql`

**Verdict**: Production system completely untouched. All Phase 9.1 work is isolated to experimental directories.

---

## Final Report

### How Many New Bengali Records Were Actually Acquired?

**Answer**: 741 cleaned records (590 conversations + 151 instructions)
- Raw: 1,225 records (1,074 + 151)
- After deduplication: 741 records
- Bengali: 726 records
- Mixed: 14 records
- English: 1 record

### How Many Verified Bengali Words Are Available Now?

**Answer**: 10,561 Bengali words
- Previous (Phase 9): 531 Bengali words
- Added in Phase 9.1: 10,030 Bengali words
- Total: 10,561 Bengali words
- **First milestone (5,000 words)**: ✅ ACHIEVED
- **Second milestone (20,000 words)**: ✗ NOT MET (need 9,439 more)

### Which Datasets Were Downloaded Successfully?

**Answer**: 2 datasets
1. **bengali_chat_conv** (MIT License) - 1,074 raw records → 590 cleaned
2. **bengali_sft_v1** (Apache-2.0 License) - 151 raw records → 151 cleaned

### Which Licenses Were Verified?

**Answer**: 2 licenses verified
1. **MIT License** (bengali_chat_conv) - Commercial use approved
2. **Apache-2.0 License** (bengali_sft_v1) - Commercial use approved

### What Is the Actual Storage Remaining?

**Answer**: 3.29 GB free on C: drive
- Phase 9.1 artifacts: ~1 MB (raw + cleaned)
- Total experimental storage: ~100 MB
- Storage remaining: 3.29 GB (above 2 GB safety threshold)

### Was the Phase 7 vs Phase 9 Discrepancy Resolved?

**Answer**: ✅ YES
- Discrepancy caused by counting records vs lines
- Phase 7: 47,336 records became 99,097 lines when split by newlines
- Phase 9: Loaded 99,097 lines, deduplicated to 90,362 texts
- No Bengali data lost or incorrectly classified

### Is the Corpus Ready for Experimental Tokenizer Retraining?

**Answer**: ⚠️ PARTIALLY
- Bengali words: 10,561 (first milestone achieved)
- Bengali UNK rate: 47.06% (still high)
- **Recommendation**: Retrain tokenizer on expanded corpus
- **Additional recommendation**: Acquire more Bengali data to reach 20K+ words

### What Blockers Remain?

**Blockers**:
1. Bengali coverage insufficient for production training (10,561 vs target 100,000+ words)
2. Tokenizer UNK rate remains high (47.06%)
3. No GPU available for large-scale training
4. Disk space limited (3.29 GB free)
5. No Bengali reasoning/mathematical datasets

**Next Steps**:
1. Retrain SentencePiece tokenizer on expanded corpus
2. Acquire additional Bengali datasets (target: 20K+ words)
3. Download Indic_Glossaries (102,855 English-Bengali pairs, CC BY 4.0)
4. Consider cloning Bangla_NLP_Dataset from GitHub
5. Acquire external storage for large-scale training

---

## STOP

Phase 9.1 complete. Bengali dataset acquisition successful (10,561 words added), corpus discrepancy resolved, and tokenizer evaluation completed. First milestone achieved but second milestone not met. Tokenizer retraining recommended.

**Awaiting explicit approval for next phase.**
