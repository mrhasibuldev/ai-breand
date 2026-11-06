# PHASE5_GLOBAL_SOURCE_AND_LICENSE_AUDIT.md

**Date**: 2026-11-03
**Phase**: 5 - Global Source and License Audit
**Status**: ✅ COMPLETE

---

## EXECUTIVE SUMMARY

Comprehensive audit of global data sources and licenses completed. CRITICAL FINDING: Alpaca dataset is CC BY-NC 4.0 (non-commercial), incompatible with NexusAI's commercial subscription model. Identified commercially eligible alternatives: Dolly (CC BY-SA 3.0, share-alike), UltraChat (MIT), GSM8K (MIT), MATH (MIT). Hardware constraint: 3.3 GB free space on C drive limits large-scale collection.

**Commercially Eligible Sources Identified**:
- Dolly (15K samples, CC BY-SA 3.0) - Conditional (share-alike)
- UltraChat (MIT) - Commercial
- GSM8K (8.5K samples, MIT) - Commercial
- MATH (12K samples, MIT) - Commercial
- Wikipedia (CC BY-SA 3.0) - Conditional (share-alike)

**Incompatible Sources**:
- Alpaca (CC BY-NC 4.0) - Non-commercial
- OpenHermes 2.5 (license unclear, mixed sources)

---

## A. LICENSE CLASSIFICATION SYSTEM

### A.1 Category A - Commercially Eligible (No Restrictions)

**Definition**: Permissive licenses allowing commercial use without significant restrictions

**Examples**:
- Public Domain (CC0)
- MIT
- Apache 2.0
- BSD (2-clause, 3-clause)

**Requirements**:
- Attribution where specified
- License copy in redistribution

**Verified Sources**:
- ✅ UltraChat (MIT)
- ✅ GSM8K (MIT)
- ✅ MATH (MIT)
- ✅ AI4Bharat IndicCorp (CC0) - BLOCKED by disk space
- ✅ Project Gutenberg (Public Domain) - BLOCKED by disk space

### A.2 Category B - Conditional Commercial Eligibility

**Definition**: Commercial use allowed with additional obligations

**Examples**:
- CC BY (attribution required)
- CC BY-SA (attribution + share-alike)

**Requirements**:
- Attribution required
- Share-alike may require derivative works to use same license
- May impact commercial model licensing

**Verified Sources**:
- ✅ Dolly (CC BY-SA 3.0)
- ✅ Wikipedia (CC BY-SA 3.0)
- ✅ Wikidata (CC0)
- ✅ OpenStax (CC BY 4.0)
- ✅ MDN Web Docs (CC BY-SA 4.0)

**Impact**: Models trained on CC BY-SA data may need to be released under CC BY-SA, which may conflict with closed-source commercial models.

### A.3 Category C - Not Approved for Commercial Use

**Definition**: Licenses prohibiting commercial use or with unclear rights

**Examples**:
- CC BY-NC (non-commercial)
- CC BY-NC-SA (non-commercial + share-alike)
- Unknown licenses
- Unclear upstream rights

**Verified Sources**:
- ❌ Alpaca (CC BY-NC 4.0)
- ❌ MIT OpenCourseWare (CC BY-NC-SA)
- ❌ Some PubMed Central content (CC BY-NC-SA)
- ❌ OpenHermes 2.5 (license unclear, mixed sources)
- ❌ Some arXiv papers (license varies)

---

## B. INSTRUCTION-FOLLOWING DATASETS

### B.1 Alpaca (COLLECTED, INCOMPATIBLE)

**Source**: https://github.com/tatsu-lab/stanford_alpaca
**Dataset**: alpaca_data.json
**Records**: 52,002 ✅ VERIFIED
**Size**: 23 MB ✅ VERIFIED
**Claimed License**: Apache 2.0 ❌ INCORRECT
**Actual License**: CC BY-NC 4.0 ✅ VERIFIED

**Evidence**:
- DATA_LICENSE file: https://raw.githubusercontent.com/tatsu-lab/stanford_alpaca/main/DATA_LICENSE
- Datasheet: States dataset should not be used for commercial purposes
- Repository README: States dataset is CC BY NC 4.0 for research use only

**Commercial Eligibility**: ❌ NO (Category C - Non-commercial)
**Action Required**: Do not use for commercial training. Mark as research-only.

### B.2 Dolly (NOT COLLECTED, ELIGIBLE)

**Source**: https://huggingface.co/datasets/databricks/databricks-dolly-15k
**Records**: 15,014
**Size**: 12.69 MB
**License**: CC BY-SA 3.0
**Commercial Permission**: ✅ YES (with attribution and share-alike)
**Attribution Required**: Yes
**Share-Alike**: Yes

**Evidence**:
- README: "This dataset can be used for any purpose, whether academic or commercial, under the terms of the Creative Commons Attribution-ShareAlike 3.0 Unported License"
- Databricks Blog: "Both model and dataset are available for commercial use"

**Commercial Eligibility**: ✅ YES (Category B - Conditional, share-alike)
**Status**: HIGH PRIORITY for collection
**Estimated Size**: ~13 MB (feasible within 3.3 GB space)

### B.3 UltraChat (NOT COLLECTED, ELIGIBLE)

**Source**: https://huggingface.co/datasets/openbmb/UltraChat
**Records**: ~1M samples
**Size**: Large (estimated >1 GB)
**License**: MIT ✅ VERIFIED
**Commercial Permission**: ✅ YES
**Attribution Required**: No
**Share-Alike**: No

**Evidence**:
- GitHub: MIT License
- HuggingFace: license: mit
- Discussion: License changed from CC BY-NC 4.0 to MIT in October 2023

**Commercial Eligibility**: ✅ YES (Category A - Permissive)
**Status**: HIGH PRIORITY, but may be too large for current disk space
**Estimated Size**: >1 GB (may need subset selection)

---

## C. REASONING DATASETS

### C.1 GSM8K (NOT COLLECTED, ELIGIBLE)

**Source**: https://github.com/openai/grade-school-math
**Records**: 8,792 (7,473 train + 1,319 test)
**Size**: 17.84 MB
**License**: MIT
**Commercial Permission**: ✅ YES
**Attribution Required**: No

**Evidence**:
- GitHub Repository: MIT License
- HuggingFace: license: mit
- Tensorflow Datasets: download size 10.77 MB, dataset size 17.84 MB

**Commercial Eligibility**: ✅ YES (Category A - Permissive)
**Status**: HIGH PRIORITY for collection
**Estimated Size**: ~18 MB (feasible)

### C.2 MATH (NOT COLLECTED, ELIGIBLE)

**Source**: https://github.com/hendrycks/math
**Records**: 12,500 (estimated)
**Size**: ~50 MB (estimated)
**License**: MIT
**Commercial Permission**: ✅ YES
**Attribution Required**: No

**Evidence**:
- GitHub Repository: MIT License
- Standard competition math dataset

**Commercial Eligibility**: ✅ YES (Category A - Permissive)
**Status**: HIGH PRIORITY for collection
**Estimated Size**: ~50 MB (feasible)

---

## D. GENERAL KNOWLEDGE DATASETS

### D.1 Wikipedia (COLLECTED, ELIGIBLE)

**Source**: Wikipedia API
**Records**: 19 articles (14 English, 5 Bengali)
**Words**: 1,380
**Size**: ~9 KB
**License**: CC BY-SA 3.0
**Commercial Permission**: ✅ YES (with attribution and share-alike)
**Attribution Required**: Yes
**Share-Alike**: Yes

**Commercial Eligibility**: ✅ YES (Category B - Conditional, share-alike)
**Status**: ✅ COLLECTED, can expand via API

### D.2 Wikidata (NOT COLLECTED, ELIGIBLE)

**Source**: https://wikidata.org
**License**: CC0
**Commercial Permission**: ✅ YES
**Attribution Required**: No
**Share-Alike**: No

**Commercial Eligibility**: ✅ YES (Category A - Permissive)
**Status**: HIGH PRIORITY, but dump size >10 GB (BLOCKED by disk space)

### D.3 Project Gutenberg (NOT COLLECTED, PARTIALLY ELIGIBLE)

**Source**: https://gutenberg.org
**License**: Public Domain (US)
**Commercial Permission**: ✅ YES
**Attribution Required**: No (public domain)

**Commercial Eligibility**: ✅ YES (Category A - Permissive)
**Status**: Full corpus 26.2 GB (BLOCKED by disk space)
**Alternative**: Could collect selected high-quality books (~20-50 books, ~20 MB)

---

## E. BENGALI DATASETS

### E.1 AI4Bharat IndicCorp (NOT COLLECTED, ELIGIBLE)

**Source**: https://indicnlp.ai4bharat.org/corpora/
**Bengali Size**: 15.99 GB
**License**: CC0 (Public Domain)
**Commercial Permission**: ✅ YES
**Attribution Required**: No

**Commercial Eligibility**: ✅ YES (Category A - Permissive)
**Status**: BLOCKED by disk space (15.99 GB > 3.3 GB limit)

### E.2 Bengali Wikipedia (COLLECTED, ELIGIBLE)

**Source**: https://bn.wikipedia.org
**Records**: 5 articles
**Words**: 439
**License**: CC BY-SA 3.0
**Commercial Permission**: ✅ YES (with attribution)

**Commercial Eligibility**: ✅ YES (Category B - Conditional)
**Status**: ✅ COLLECTED, can expand via API

---

## F. LARGE CORPORA STATUS

### F.1 BLOCKED by Disk Space (3.3 GB limit)

| Dataset | Size | License | Status |
|---------|------|---------|--------|
| AI4Bharat IndicCorp (Bengali) | 15.99 GB | CC0 | ❌ BLOCKED |
| AI4Bharat IndicCorp (English) | 20+ GB | CC0 | ❌ BLOCKED |
| Project Gutenberg | 26.2 GB | Public Domain | ❌ BLOCKED |
| Wikidata | >10 GB | CC0 | ❌ BLOCKED |
| Dolma | 3 TB | ODC-BY | ❌ BLOCKED |
| C4 | 750 GB | ODC-BY | ❌ BLOCKED |
| RedPajama | 1 TB | Apache 2.0 | ❌ BLOCKED |

---

## G. PRIORITY COLLECTION PLAN

### G.1 Immediate (Feasible within 3.3 GB)

**High Priority**:
1. Dolly (15K samples, ~13 MB, CC BY-SA 3.0) - Commercial with share-alike
2. GSM8K (8.8K samples, ~18 MB, MIT) - Commercial
3. MATH (12.5K samples, ~50 MB, MIT) - Commercial
4. Expand Wikipedia (target 200 articles, ~50 MB, CC BY-SA 3.0) - Commercial with share-alike

**Total Estimated**: ~131 MB

**Medium Priority**:
5. Selected Project Gutenberg books (20-50 books, ~20 MB, Public Domain)
6. Python Documentation (~50 MB, license to verify)
7. BanglaNLP datasets (~10 MB, MIT)

**Total Estimated**: ~80 MB

**Combined Total**: ~211 MB (well within 3.3 GB limit)

### G.2 Future (Requires Storage Expansion)

**BLOCKED by 3.3 GB constraint**:
1. AI4Bharat IndicCorp Bengali (15.99 GB)
2. AI4Bharat IndicCorp English (20+ GB)
3. Project Gutenberg full corpus (26.2 GB)
4. UltraChat (estimated >1 GB, but could use subset)
5. Dolma (3 TB)
6. C4 (750 GB)
7. RedPajama (1 TB)

**Requirement**: External drive (1-2 TB) or cloud storage subscription.

---

## H. LICENSE SUMMARY TABLE

| Dataset | License | Commercial | Attribution | Share-Alike | Status |
|---------|---------|------------|-------------|-------------|--------|
| Alpaca | CC BY-NC 4.0 | ❌ NO | Yes | N/A | Incompatible |
| Dolly | CC BY-SA 3.0 | ✅ YES | Yes | Yes | Conditional |
| UltraChat | MIT | ✅ YES | No | No | Permissive |
| GSM8K | MIT | ✅ YES | No | No | Permissive |
| MATH | MIT | ✅ YES | No | No | Permissive |
| Wikipedia | CC BY-SA 3.0 | ✅ YES | Yes | Yes | Conditional |
| IndicCorp | CC0 | ✅ YES | No | No | Permissive |
| Project Gutenberg | Public Domain | ✅ YES | No | No | Permissive |

---

## I. RECOMMENDATION

### I.1 Immediate Action

**Replace Alpaca**: Alpaca is non-commercial and incompatible with NexusAI's commercial subscription model.

**Alternative**: Collect Dolly (CC BY-SA 3.0) which is explicitly commercially licensed by Databricks.

**Note**: CC BY-SA 3.0 requires share-alike, which may impact model licensing. This is acceptable for open-source model but requires legal review for closed-source commercial model.

### I.2 Priority Order

1. Collect Dolly (15K samples, CC BY-SA 3.0)
2. Collect GSM8K (8.8K samples, MIT)
3. Collect MATH (12.5K samples, MIT)
4. Expand Wikipedia (CC BY-SA 3.0)
5. Collect UltraChat subset (MIT, if space permits)

---

## J. FILES CHANGED

**Created**:
1. `docs/ai-brain/PHASE5_EXISTING_DATA_VERIFICATION.md`
2. `docs/ai-brain/PHASE5_GLOBAL_SOURCE_AND_LICENSE_AUDIT.md` (this file)

**Modified**: None

**Deleted**: None

---

## K. PRODUCTION SAFETY

**Confirmed Unchanged**:
- ✅ Production tokenizer, model, checkpoint
- ✅ ML inference pipeline
- ✅ Frontend, API, database
- ✅ Authentication system

**Experimental Artifacts**:
- Alpaca dataset (isolated, marked as non-commercial)
- Wikipedia data (isolated)
- BPE tokenizer v1.1.0 (isolated)

---

**Report End**
