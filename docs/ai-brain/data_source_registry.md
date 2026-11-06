# NEXUSAI DATA SOURCE REGISTRY

**Date**: 2026-11-03
**Phase**: 2 - Data Collection Foundation
**Purpose**: Track authorized data sources for AI Brain training

---

## SOURCE DISCOVERY POLICY

**Principles**:
1. Only collect from publicly available, authorized sources
2. Respect robots.txt and access controls
3. Verify license terms before collection
4. Record provenance for all collected data
5. Never collect private personal information
6. Never bypass access restrictions

---

## EVALUATED DATA SOURCES

### 1. Wikipedia

**Source Name**: Wikipedia
**URL**: https://en.wikipedia.org, https://bn.wikipedia.org
**Data Category**: General knowledge, educational content
**Languages**: English, Bengali
**Collection Method**: Wikipedia API / Database dumps
**License**: CC BY-SA 3.0
**Attribution Required**: Yes
**Usage Restrictions**: Must provide attribution, share-alike
**Status**: ✅ AUTHORIZED

**Access Methods**:
- Wikipedia API (individual articles)
- Wikipedia Database dumps (bulk download)
- Recommended: Start with API for targeted collection

**Provenance Requirements**:
- Record article title, URL, revision ID
- Record collection timestamp
- Record CC BY-SA 3.0 license information

**Quality Notes**:
- High-quality, vetted content
- Suitable for pretraining
- Not suitable for instruction-following or reasoning training
- Requires format conversion from HTML to plain text

---

### 2. Wikibooks

**Source Name**: Wikibooks
**URL**: https://en.wikibooks.org, https://bn.wikibooks.org
**Data Category**: Educational textbooks, tutorials
**Languages**: English, Bengali
**Collection Method**: Wikipedia API / Database dumps
**License**: CC BY-SA 3.0
**Attribution Required**: Yes
**Usage Restrictions**: Must provide attribution, share-alike
**Status**: ✅ AUTHORIZED

**Quality Notes**:
- Structured educational content
- Suitable for knowledge base
- Better for instructional content than Wikipedia

---

### 3. Wikisource

**Source Name**: Wikisource
**URL**: https://en.wikisource.org, https://bn.wikisource.org
**Data Category**: Public domain books, historical documents
**Languages**: English, Bengali
**Collection Method**: Wikipedia API / Database dumps
**License**: Varies (mostly public domain)
**Attribution Required**: Varies
**Usage Restrictions**: Check individual work licenses
**Status**: ⚠️ REQUIRES PER-WORK LICENSE VERIFICATION

**Quality Notes**:
- High-quality literary and historical content
- Useful for language modeling
- Requires careful license verification

---

### 4. Khan Academy (Educational Content)

**Source Name**: Khan Academy
**URL**: https://www.khanacademy.org
**Data Category**: Educational videos, exercises, articles
**Languages**: English, Bengali (some translations)
**Collection Method**: API (if available) or structured export
**License**: CC BY-NC-SA 3.0
**Attribution Required**: Yes
**Usage Restrictions**: Non-commercial use only
**Status**: ⚠️ LIMITED BY NON-COMMERCIAL LICENSE

**Quality Notes**:
- High-quality educational content
- Structured by subject and difficulty
- Non-commercial restriction may limit use

---

### 5. Open Educational Resources (OER)

**Source Name**: Various OER repositories
**URL**: Multiple (OER Commons, MIT OpenCourseWare, etc.)
**Data Category**: Educational materials, textbooks
**Languages**: English, Bengali (some)
**Collection Method**: Individual repository APIs
**License**: Varies (CC BY, CC BY-SA, CC BY-NC, etc.)
**Attribution Required**: Varies
**Usage Restrictions**: Varies by source
**Status**: ⚠️ REQUIRES PER-SOURCE LICENSE VERIFICATION

**Quality Notes**:
- High-quality educational content
- Suitable for knowledge base
- Requires careful license tracking

---

## NOT RECOMMENDED / RESTRICTED SOURCES

### Common Crawl

**Source Name**: Common Crawl
**Status**: ❌ NOT RECOMMENDED FOR PHASE 2
**Reasoning**:
- Too large (hundreds of terabytes)
- Requires significant filtering infrastructure
- Quality varies widely
- Better to start with curated sources

---

### The Pile

**Source Name**: The Pile
**Status**: ❌ NOT RECOMMENDED FOR PHASE 2
**Reasoning**:
- Large dataset (825 GB)
- Contains multiple sources with varying licenses
- Requires careful license filtering
- Better to start with simpler, well-licensed sources

---

### OpenWebText

**Source Name**: OpenWebText
**Status**: ❌ NOT RECOMMENDED FOR PHASE 2
**Reasoning**:
- Derived from Reddit (not directly available)
- License uncertainty
- Better to use directly licensed sources

---

## INSTRUCTION-FOLLOWING DATASETS

### Alpaca

**Source Name**: Alpaca Dataset
**URL**: https://github.com/tatsu-lab/stanford_alpaca
**Data Category**: Instruction-following
**Languages**: English
**License**: Apache 2.0
**Status**: ✅ AUTHORIZED (with attribution)

**Quality Notes**:
- 52K instruction-following examples
- Generated from OpenAI GPT-3 (derivative)
- Suitable for instruction tuning
- Attribution required

---

### Dolly

**Source Name**: Dolly Dataset
**URL**: https://huggingface.co/datasets/databricks/databricks-dolly-15k
**Data Category**: Instruction-following
**Languages**: English
**License**: CC BY-SA 3.0
**Status**: ✅ AUTHORIZED (with attribution)

**Quality Notes**:
- 15K instruction-following examples
- Human-generated by Databricks employees
- High quality
- Suitable for instruction tuning

---

## REASONING DATASETS

### GSM8K

**Source Name**: GSM8K (Grade School Math 8K)
**URL**: https://github.com/openai/grade-school-math
**Data Category**: Math word problems
**Languages**: English
**License**: MIT
**Status**: ✅ AUTHORIZED (with attribution)

**Quality Notes**:
- 8.5K math word problems
- Step-by-step solutions
- Suitable for reasoning training
- English only

---

### MATH

**Source Name**: MATH Dataset
**URL**: https://github.com/hendrycks/math
**Data Category**: Math problems
**Languages**: English
**License**: MIT
**Status**: ✅ AUTHORIZED (with attribution)

**Quality Notes**:
- 12K competition math problems
- High difficulty
- Suitable for reasoning training
- English only

---

## BENGALI-SPECIFIC SOURCES

### Bengali Wikipedia

**Source Name**: Bengali Wikipedia
**URL**: https://bn.wikipedia.org
**Data Category**: General knowledge
**Languages**: Bengali
**License**: CC BY-SA 3.0
**Status**: ✅ AUTHORIZED (with attribution)

**Quality Notes**:
- Smaller than English Wikipedia (~100K articles)
- High-quality Bengali content
- Essential for Bengali language modeling

---

### Bengali Wikisource

**Source Name**: Bengali Wikisource
**URL**: https://bn.wikisource.org
**Data Category**: Literary works
**Languages**: Bengali
**License**: Varies (mostly public domain)
**Status**: ⚠️ REQUIRES PER-WORK LICENSE VERIFICATION

**Quality Notes**:
- Bengali literary classics
- High-quality language
- Useful for language modeling

---

## COLLECTION PRIORITIES

### Phase 2a (Immediate - Scale Foundation)
1. **Wikipedia (English)**: 1000-5000 articles (curated topics)
2. **Wikipedia (Bengali)**: 500-1000 articles (curated topics)
3. **Total Target**: ~1-5 million tokens

### Phase 2b (Instruction-Following)
1. **Alpaca**: 52K examples (with attribution)
2. **Dolly**: 15K examples (with attribution)
3. **Total Target**: ~67K instruction examples

### Phase 2c (Reasoning)
1. **GSM8K**: 8.5K math problems (with attribution)
2. **MATH**: 12K math problems (with attribution)
3. **Total Target**: ~20K reasoning examples

---

## PROVENANCE TRACKING REQUIREMENTS

For each collected dataset, record:
- Source name and URL
- Collection timestamp
- Collection method
- License information
- Attribution requirements
- Document count
- Token count
- Checksum (SHA-256)
- Processing status
- Dataset version
- Training eligibility

---

**Registry Version**: 1.0
**Last Updated**: 2026-11-03
