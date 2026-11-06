# GLOBAL_DATA_SOURCE_REGISTRY.md

**Date**: 2026-11-03
**Phase**: 1-2 - Global Source Discovery & Registry
**Status**: ✅ COMPLETE (with hardware constraints documented)

---

## EXECUTIVE SUMMARY

Comprehensive global data source research completed. Critical hardware constraint identified: only 2.8 GB free disk space on C drive. This severely limits large-scale data collection. Registry focuses on small, high-quality datasets (10-100 MB range) that are commercially licensed and feasible within current constraints.

**Key Findings**:
- Large corpora (IndicCorp, Project Gutenberg, Dolma) are 15-275 GB - NOT feasible
- Small reasoning datasets (GSM8K, MATH) are 10-50 MB - FEASIBLE
- Instruction datasets (Dolly, Alpaca) are 50-200 MB - FEASIBLE
- Wikipedia API collection is ongoing and scalable - FEASIBLE

**Strategy**: Collect small, high-quality datasets now. Plan for storage expansion for large corpora later.

---

## A. HARDWARE CONSTRAINTS

### A.1 Disk Space

**C Drive**:
- Total: 119 GB
- Free: 2.8 GB
- Available for data: ~2 GB (safety margin)

**D Drive**:
- Total: 29.7 GB
- Free: 50 MB (critically low, unusable)

**Implication**: Cannot download datasets >2 GB. Must prioritize small, high-quality datasets.

---

## B. ENCYCLOPEDIAS AND KNOWLEDGE SOURCES

### B.1 Wikipedia

**Source**: Wikipedia API
**URL**: https://en.wikipedia.org, https://bn.wikipedia.org
**Category**: General Knowledge
**Languages**: English, Bengali
**Estimated Size**: Unlimited (API access)
**License**: CC BY-SA 3.0
**Commercial Permission**: ✅ YES (with attribution)
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Access Method**: REST API
**Authentication**: None
**Rate Limits**: Recommended 1 second delay
**Collection Status**: ✅ COLLECTED (19 articles, 1,380 words)
**Status**: `verified_commercial`
**Priority**: HIGH
**Notes**: Scalable, high quality, requires attribution

### B.2 Wikidata

**Source**: Wikidata
**URL**: https://wikidata.org
**Category**: Structured Knowledge
**Languages**: Multilingual
**Estimated Size**: Large (dump >10 GB)
**License**: CC0
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: API / Dumps
**Collection Status**: ❌ NOT COLLECTED (too large)
**Status**: `verified_commercial`
**Priority**: MEDIUM
**Limitation**: Dump size exceeds disk space

### B.3 Wikisource

**Source**: Wikisource
**URL**: https://en.wikisource.org, https://bn.wikisource.org
**Category**: Public Domain Literature
**Languages**: English, Bengali
**Estimated Size**: Large
**License**: Varies (mostly public domain)
**Commercial Permission**: ⚠️ REQUIRES PER-WORK VERIFICATION
**AI Training Permission**: ⚠️ DEPENDS ON INDIVIDUAL WORK
**Attribution Required**: Varies
**Collection Status**: ❌ NOT COLLECTED
**Status**: `pending_review`
**Priority**: LOW
**Limitation**: License complexity, large size

---

## C. BOOKS AND DIGITAL LIBRARIES

### C.1 Project Gutenberg

**Source**: Project Gutenberg
**URL**: https://gutenberg.org
**Category**: Public Domain Books
**Languages**: Primarily English
**Estimated Size**: 26.2 GB (71,810 documents)
**Accessible Size**: Individual books ~100 KB each
**License**: Public Domain (US)
**Commercial Permission**: ✅ YES (public domain)
**AI Training Permission**: ✅ YES
**Attribution Required**: No (public domain)
**Access Method**: API / Direct Download
**Collection Status**: ❌ NOT COLLECTED (full corpus too large)
**Status**: `verified_commercial`
**Priority**: MEDIUM
**Limitation**: Full corpus 26.2 GB exceeds disk space
**Alternative**: Could collect selected high-quality books (~100-200 books, ~20 MB)

### C.2 Internet Archive

**Source**: Internet Archive
**URL**: https://archive.org
**Category**: Digital Library
**Languages**: Multilingual
**Estimated Size**: Very Large (petabytes)
**Accessible Size**: Varies by collection
**License**: Varies
**Commercial Permission**: ⚠️ REQUIRES INDIVIDUAL VERIFICATION
**AI Training Permission**: ⚠️ DEPENDS ON INDIVIDUAL WORK
**Attribution Required**: Varies
**Collection Status**: ❌ NOT COLLECTED
**Status**: `permission_required`
**Priority**: LOW
**Limitation**: License complexity, large size

---

## D. SCIENTIFIC RESEARCH

### D.1 arXiv

**Source**: arXiv
**URL**: https://arxiv.org
**Category**: Scientific Preprints
**Languages**: Primarily English
**Estimated Size**: Very Large (millions of papers)
**Accessible Size**: Individual papers ~100 KB
**License**: arXiv license (varies)
**Commercial Permission**: ⚠️ COMPLEX
**AI Training Permission**: ⚠️ COMPLEX
**Attribution Required**: Yes
**Access Method**: API / OAI-PMH
**Collection Status**: ❌ NOT COLLECTED
**Status**: `permission_required`
**Priority**: LOW
**Limitation**: License complexity for commercial use

### D.2 PubMed Central

**Source**: PubMed Central Open Access
**URL**: https://www.ncbi.nlm.nih.gov/pmc
**Category**: Biomedical Research
**Languages**: Primarily English
**Estimated Size**: Large
**License**: CC BY or CC BY-NC-SA
**Commercial Permission**: ⚠️ MIXED (some non-commercial)
**AI Training Permission**: ⚠️ MIXED
**Attribution Required**: Yes
**Collection Status**: ❌ NOT COLLECTED
**Status**: `permission_required`
**Priority**: LOW
**Limitation**: Non-commercial restrictions on some content

---

## E. PROGRAMMING AND TECHNICAL KNOWLEDGE

### E.1 Python Documentation

**Source**: Python Docs
**URL**: https://docs.python.org
**Category**: Programming Documentation
**Languages**: English
**Estimated Size**: ~50 MB
**License**: PSF License (compatible)
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: Web scraping / Download
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: MEDIUM
**Notes**: High quality, small size

### E.2 MDN Web Docs

**Source**: MDN Web Docs
**URL**: https://developer.mozilla.org
**Category**: Web Development Documentation
**Languages**: Multiple
**Estimated Size**: ~100 MB
**License**: CC BY-SA 4.0
**Commercial Permission**: ✅ YES (with attribution)
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Access Method**: API / Download
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: MEDIUM
**Notes**: High quality, attribution required

---

## F. EDUCATIONAL KNOWLEDGE

### F.1 OpenStax

**Source**: OpenStax
**URL**: https://openstax.org
**Category**: Open Educational Textbooks
**Languages**: English
**Estimated Size**: ~500 MB (full catalog)
**Accessible Size**: Individual books ~20 MB
**License**: CC BY 4.0
**Commercial Permission**: ✅ YES (with attribution)
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Access Method**: Direct Download
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: MEDIUM
**Limitation**: Full catalog ~500 MB, could select 2-3 books (~60 MB)

### F.2 MIT OpenCourseWare

**Source**: MIT OCW
**URL**: https://ocw.mit.edu
**Category**: University Course Materials
**Languages**: English
**Estimated Size**: Very Large
**License**: CC BY-NC-SA 4.0
**Commercial Permission**: ❌ NON-COMMERCIAL
**AI Training Permission**: ❌ NON-COMMERCIAL
**Attribution Required**: Yes
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_noncommercial`
**Priority**: REJECTED
**Reason**: Non-commercial license incompatible with commercial AI services

---

## G. BENGALI AND SOUTH ASIAN SOURCES

### G.1 AI4Bharat IndicCorp

**Source**: AI4Bharat IndicCorp
**URL**: https://indicnlp.ai4bharat.org/corpora/
**Category**: Large Monolingual Corpora
**Languages**: 22 Indic languages including Bengali
**Estimated Size**: 275 GB (total)
**Bengali Size**: 15.99 GB
**English Size**: Large (estimated >20 GB)
**License**: CC0 (Public Domain)
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: Direct Download
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: HIGH (blocked by hardware)
**Limitation**: Bengali corpus 15.99 GB exceeds 2.8 GB disk space
**Notes**: Excellent resource, requires storage expansion

### G.2 Bengali Wikipedia

**Source**: Bengali Wikipedia
**URL**: https://bn.wikipedia.org
**Category**: General Knowledge
**Languages**: Bengali
**Estimated Size**: ~100K articles
**License**: CC BY-SA 3.0
**Commercial Permission**: ✅ YES (with attribution)
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Access Method**: API / Dumps
**Collection Status**: ✅ COLLECTED (5 articles, 439 words)
**Status**: `verified_commercial`
**Priority**: HIGH
**Notes**: More articles can be collected via API

### G.3 BanglaNLP

**Source**: BanglaNLP
**URL**: https://github.com/Rifat1493/BanglaNLP
**Category**: Bengali NLP Resources
**Languages**: Bengali
**Estimated Size**: Small
**License**: MIT
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: GitHub
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: MEDIUM
**Notes**: Small, high-quality Bengali datasets

---

## H. GENERAL LANGUAGE MODEL DATASETS

### H.1 Dolma

**Source**: Dolma
**URL**: https://huggingface.co/datasets/allenai/dolma
**Category**: Large Pretraining Corpus
**Languages**: English and others
**Estimated Size**: 3 TB
**License**: ODC-BY-1.0
**Commercial Permission**: ⚠️ ATTRIBUTION REQUIRED
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: REJECTED
**Reason**: 3 TB exceeds disk space by factor of 1000x

### H.2 C4

**Source**: C4 (Colossal Clean Crawled Corpus)
**URL**: https://huggingface.co/datasets/allenai/c4
**Category**: Large Pretraining Corpus
**Languages**: Multilingual
**Estimated Size**: 750 GB
**License**: ODC-BY-1.0
**Commercial Permission**: ⚠️ ATTRIBUTION REQUIRED
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: REJECTED
**Reason**: 750 GB exceeds disk space by factor of 250x

### H.3 RedPajama

**Source**: RedPajama
**URL**: https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T
**Category**: Large Pretraining Corpus
**Languages**: English
**Estimated Size**: 1 TB
**License**: Apache 2.0
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: REJECTED
**Reason**: 1 TB exceeds disk space by factor of 350x

---

## I. INSTRUCTION FOLLOWING AND REASONING DATASETS

### I.1 GSM8K

**Source**: Grade School Math 8K
**URL**: https://github.com/openai/grade-school-math
**Category**: Mathematical Reasoning
**Languages**: English
**Estimated Size**: 10.77 MB download, 17.84 MB dataset
**License**: MIT
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: GitHub / Hugging Face
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: HIGH
**Notes**: 8.5K math problems, multi-step reasoning, small size, feasible

### I.2 MATH

**Source**: MATH Dataset
**URL**: https://github.com/hendrycks/math
**Category**: Mathematical Reasoning
**Languages**: English
**Estimated Size**: ~50 MB
**License**: MIT
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: GitHub
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: HIGH
**Notes**: 12K competition math problems, high difficulty, feasible

### I.3 Dolly

**Source**: Dolly Dataset
**URL**: https://huggingface.co/datasets/databricks/databricks-dolly-15k
**Category**: Instruction Following
**Languages**: English
**Estimated Size**: ~50 MB
**License**: CC BY-SA 3.0
**Commercial Permission**: ✅ YES (with attribution)
**AI Training Permission**: ✅ YES
**Attribution Required**: Yes
**Access Method**: Hugging Face
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: HIGH
**Notes**: 15K instruction examples, human-generated, feasible

### I.4 Alpaca

**Source**: Alpaca Dataset
**URL**: https://github.com/tatsu-lab/stanford_alpaca
**Category**: Instruction Following
**Languages**: English
**Estimated Size**: ~5 MB
**License**: Apache 2.0
**Commercial Permission**: ✅ YES
**AI Training Permission**: ✅ YES
**Attribution Required**: No
**Access Method**: GitHub
**Collection Status**: ❌ NOT COLLECTED
**Status**: `verified_commercial`
**Priority**: HIGH
**Notes**: 52K instruction examples, derivative of GPT-3, feasible

---

## J. PRIORITY RANKING

### J.1 Immediate (Feasible within 2 GB space)

**Rank 1 - MUST COLLECT**:
1. GSM8K (17 MB) - Mathematical reasoning
2. MATH (50 MB) - Advanced mathematical reasoning
3. Dolly (50 MB) - Instruction following
4. Alpaca (5 MB) - Instruction following
5. Wikipedia API expansion (target 100-200 articles, ~50 MB)

**Total Estimated**: ~122 MB

**Rank 2 - SHOULD COLLECT**:
6. Selected Project Gutenberg books (20-50 books, ~20 MB)
7. Python Documentation (~50 MB)
8. MDN Web Docs (~100 MB)
9. BanglaNLP datasets (~10 MB)

**Total Estimated**: ~180 MB

**Combined Total**: ~302 MB (well within 2 GB limit)

### J.2 Future (Requires Storage Expansion)

**Rank 3 - EXCELLENT BUT BLOCKED**:
1. AI4Bharat IndicCorp Bengali (15.99 GB) - BLOCKED by disk space
2. AI4Bharat IndicCorp English (20+ GB) - BLOCKED by disk space
3. Project Gutenberg full corpus (26.2 GB) - BLOCKED by disk space
4. Dolma (3 TB) - BLOCKED by disk space
5. C4 (750 GB) - BLOCKED by disk space
6. RedPajama (1 TB) - BLOCKED by disk space

---

## K. LICENSE SUMMARY

### K.1 Commercially Approved (No Restrictions)

**CC0**: AI4Bharat IndicCorp
**MIT**: GSM8K, MATH, Alpaca, BanglaNLP
**Apache 2.0**: RedPajama, Alpaca
**Public Domain**: Project Gutenberg

### K.2 Commercially Approved (Attribution Required)

**CC BY**: OpenStax, Python Docs (likely)
**CC BY-SA 3.0**: Wikipedia, Wikidata, Dolly, MDN Web Docs
**ODC-BY**: Dolma, C4

### K.3 Non-Commercial Only

**CC BY-NC-SA**: MIT OpenCourseWare, some PubMed Central content
**Status**: REJECTED for commercial AI services

### K.4 Requires Verification

**arXiv**: License varies by paper
**Internet Archive**: License varies by work
**Wikisource**: License varies by work

---

## L. NEXT STEPS

### L.1 Immediate Collection (Phase 4)

**Priority 1 - Collect Now**:
1. GSM8K (17 MB)
2. MATH (50 MB)
3. Dolly (50 MB)
4. Alpaca (5 MB)
5. Expand Wikipedia collection (50 MB)

**Total**: ~172 MB

### L.2 Storage Planning

**Requirement**: To collect large corpora (IndicCorp, Project Gutenberg, Dolma), need:
- External drive (1-2 TB)
- Cloud storage (1-2 TB)
- Alternative: Stream processing without full download

**Recommendation**: Collect small datasets now, plan storage expansion for large corpora.

---

**Registry End**
