# PHASE5B1_DATASET_RECONCILIATION_REPORT.md

**Date**: 2026-11-03
**Phase**: 5B.1 - Dataset Reconciliation
**Status**: ✅ COMPLETE

---

## EXECUTIVE SUMMARY

Actual dataset files inspected and reconciled. Discrepancy identified: previous report included Wikipedia (19 articles, 1,380 words) in totals. Actual Phase 5B collected datasets (GSM8K + Dolly) total 23,803 records, 1,942,256 words. SHA-256 checksums verified to match exactly. Dolly has 232 duplicate instructions (1.5%), which have been removed in cleaning phase.

---

## A. BEFORE vs AFTER

### A.1 Previous Report (Phase 5B)

**Reported Totals**:
- Total Records: 23,822
- Total Words: 1,943,636
- GSM8K: 8,792 records, 854,046 words
- Dolly: 15,011 records, 1,088,210 words
- Discrepancy: 23,822 - 23,803 = 19 records (Wikipedia not included in Phase 5B collection)

### A.2 Actual Verification (Phase 5B.1)

**Actual Collected Phase 5B Datasets**:
- GSM8K: 8,792 records, 854,046 words ✅ MATCHES
- Dolly: 15,011 records, 1,088,210 words ✅ MATCHES
- **Actual Total**: 23,803 records, 1,942,256 words ✅ CORRECTED

**After Cleaning**:
- GSM8K: 8,792 records (no duplicates removed)
- Dolly: 14,779 records (232 duplicates removed)
- **Cleaned Total**: 23,571 records

### A.3 SHA-256 Verification

**GSM8K Train**:
- Previous: `17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465`
- Actual: `17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465`
- Status: ✅ MATCHES

**GSM8K Test**:
- Previous: `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14`
- Actual: `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14`
- Status: ✅ MATCHES

**Dolly**:
- Previous: `2df9083338b4abd6bceb5635764dab5d833b393b55759dffb0959b6fcbf794ec`
- Actual: `2df9083338b4abd6bceb5635764dab5d833b393b55759dffb0959b6fcbf794ec`
- Status: ✅ MATCHES

---

## B. DATASET STATUS

### B.1 GSM8K

**Status**: ✅ VERIFIED

**File**: `packages/ai-core/data/collected/raw/gsm8k/gsm8k_train.jsonl`
- Size: 4.17 MB
- Records: 7,473
- Words: 723,419
- Avg Words/Record: 96.8
- Language: 100% English
- Duplicates: 0
- Empty Records: 0
- Missing Fields: 0
- JSON Errors: 0
- SHA-256: `17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465`

**File**: `packages/ai-core/data/collected/raw/gsm8k/gsm8k_test.jsonl`
- Size: 0.75 MB
- Records: 1,319
- Words: 130,627
- Avg Words/Record: 99.0
- Language: 100% English
- Duplicates: 0
- Empty Records: 0
- Missing Fields: 0
- JSON Errors: 0
- SHA-256: `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14`

**Combined**: 8,792 records, 854,046 words, 4.69 MB

**Cleaned**: 8,792 records (no change, no duplicates to remove)

### B.2 Dolly

**Status**: ✅ VERIFIED

**File**: `packages/ai-core/data/collected/raw/dolly/dolly-15k.jsonl`
- Size: 12.48 MB
- Records: 15,011
- Words: 1,088,210
- Avg Words/Record: 72.5
- Language: 99.99% English, 0.01% Mixed
- Duplicates: 232 (1.5%)
- Empty Records: 0
- Missing Fields: 0
- JSON Errors: 0
- SHA-256: `2df9083338b4abd6bceb5635764dab5d833b393b55759dffb0959b6fcbf794ec`

**Cleaned**: 14,779 records (232 duplicates removed)

### B.3 MATH

**Status**: ❌ NOT COLLECTED

**File**: Does not exist
**Reason**: Collection failed (Berkeley URL unavailable)
**Status**: Marked as unavailable

---

## C. DATA QUALITY

### C.1 Quality Status

**GSM8K**: ✅ HIGH QUALITY
- No empty records
- No missing fields
- No duplicates
- No JSON errors
- Valid UTF-8

**Dolly**: ✅ HIGH QUALITY (with minor duplicates)
- No empty records
- No missing fields
- 232 duplicate instructions (1.5%)
- No JSON errors
- Valid UTF-8

### C.2 Duplicate Details

**GSM8K**:
- Train Duplicates: 0
- Test Duplicates: 0
- Train/Test Overlap: Not checked (preserving official split)

**Dolly**:
- Total Duplicates: 232
- Duplicate Samples:
  - "What is the English Premier League?"
  - "Extract all of the dates mentioned in this paragraph..."
  - "Extract all of the names of people mentioned in this paragraph..."
  - "Give me a title of one of the \"Harry Potter\" novels."
  - "What is the meaning of life?"
  - "Why is the sky blue?"
  - "What are the primary colors?"
  - "Where do bears live?"
  (Plus 224 more)

**Excluded File**: `packages/ai-core/data/collected/excluded/dolly/dolly_excluded_duplicates.json`

---

## D. FILES CHANGED

### D.1 Created

**Data Collection Scripts**:
1. `packages/ai-core/data/reconcile_phase5b1.py`
2. `packages/ai-core/data/clean_phase5b1.py`

**Cleaned Datasets**:
3. `packages/ai-core/data/collected/cleaned/gsm8k/gsm8k_train_cleaned.jsonl`
4. `packages/ai-core/data/collected/cleaned/gsm8k/gsm8k_test_cleaned.jsonl`
5. `packages/ai-core/data/collected/cleaned/dolly/dolly-15k_cleaned.jsonl`

**Excluded Records**:
6. `packages/ai-core/data/collected/excluded/dolly/dolly_excluded_duplicates.json`

**Manifests**:
7. `packages/ai-core/data/collected/manifests/reconciliation_report.json`
8. `packages/ai-core/data/collected/manifests/cleaning_report.json`

**Reports**:
9. `docs/ai-brain/PHASE5B1_DATASET_RECONCILIATION_REPORT.md` (this file)

### D.2 Modified

**None** - All files created new

---

## E. SAFETY VERIFICATION

**Confirmed Unchanged**:
- ✅ Production tokenizer (SimpleTokenizer, 74 tokens)
- ✅ Production model (MediumTransformer, 4.7M parameters)
- ✅ Production checkpoint
- ✅ ML inference pipeline
- ✅ Frontend
- ✅ API
- ✅ Database
- ✅ Authentication

**Raw Datasets**: Preserved in `raw/` directory
**Cleaned Datasets**: Created in `cleaned/` directory
**Excluded Records**: Documented in `excluded/` directory

---

## F. DISK SPACE

**C Drive**: 3.21 GB free (slightly decreased from 3.22 GB)
**Total Dataset Storage**: ~34 MB (raw + cleaned)
**Status**: ✅ SUFFICIENT

---

## G. CONCLUSION

Reconciliation complete. Previous discrepancy (23,822 vs 23,803) explained by Wikipedia inclusion. SHA-256 checksums verified to match exactly. Dolly duplicates (232) removed in cleaning phase. Raw datasets preserved. Cleaned datasets created for training use.

---

**Report End**
