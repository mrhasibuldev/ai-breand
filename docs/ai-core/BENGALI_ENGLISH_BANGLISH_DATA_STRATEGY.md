# BENGALI_ENGLISH_BANGLISH_DATA_STRATEGY

**Date**: 2026-10-31  
**Task**: Multilingual Data Strategy  
**Strategy Type**: LANGUAGE DATA PLAN  
**Status**: STRATEGY COMPLETE

---

## Executive Summary

This document defines the strategy for building Bengali, English, and Banglish language capabilities for NexusAI. The strategy addresses current data gaps, public dataset limitations, and the need for original data creation.

**Key Finding**: High-quality Banglish text datasets with clear licenses do not exist in public repositories. Original data creation is required.

---

## Current Status

### Bengali
- **Current Data**: 13 conversations (0.07% of 20,000 target)
- **Public Datasets**: Multiple sources exist (B-CORE: 52 GB, bnnews: 755 MB)
- **Blocker**: All have unclear licensing
- **Strategy**: License verification + original data creation

### English
- **Current Data**: 50 conversations (0.17% of 30,000 target)
- **Public Datasets**: Several with clear licenses (Gab100MFinetune, helpful_instructions)
- **Blocker**: Storage constraint for large datasets
- **Strategy**: Download verified small datasets + original data creation

### Banglish
- **Current Data**: 17 conversations (0.17% of 10,000 target)
- **Public Datasets**: Very limited (Banglish-English: 14,000, BnSentMix: 20,000)
- **Blocker**: All have unclear licensing + low quality
- **Strategy**: Original data creation (primary approach)

---

## Bengali Data Strategy

### Phase 1: License Verification (Immediate)

**Target Datasets**:
1. **B-CORE-bengali-corpus** (52 GB, 16.5M documents)
   - Publisher: nahid-hub
   - Size: Too large for current storage
   - Action: License verification + storage planning

2. **bnnews** (755 MB, 295,020 articles)
   - Publisher: thedeba
   - Size: Might fit with cleanup
   - Action: License verification + size verification

3. **bangla-llm-data** (801,645 samples)
   - Publisher: nahidstaq
   - Size: Unknown
   - Action: License verification + size verification

**Verification Process**:
1. Review dataset README and license file
2. Check if license allows commercial use
3. Check if license allows modification
4. Check attribution requirements
5. Document findings in registry

### Phase 2: Original Bengali Data Creation (Short-term)

**Target**: 5,000 Bengali conversations (Phase 1 baseline)

**Data Types**:
- Daily conversations (greetings, casual chat)
- Question answering (what, how, why)
- Storytelling and narrative
- Cultural context
- Idioms and expressions
- Formal and informal registers

**Creation Process**:
1. **Native Speakers**: Recruit native Bengali speakers
2. **Authoring**: Write original conversations
3. **Validation**: Grammar and spelling check
4. **Cultural Review**: Ensure cultural appropriateness
5. **Schema Compliance**: Follow NexusAI dataset schema
6. **Human Review**: CLI review workflow
7. **Approval**: Genuine human approval

**Quality Standards**:
- Native or highly proficient Bengali
- Proper grammar and spelling
- Natural conversation flow
- Cultural appropriateness
- No machine translation from English

**Timeline**: 1-2 months for 5,000 conversations

### Phase 3: Expansion (Long-term)

**Target**: 20,000 Bengali conversations total

**Sources**:
- Original data creation (primary)
- Public datasets (if license verified)
- User feedback collection (ongoing)

---

## English Data Strategy

### Phase 1: Download Verified Datasets (Immediate)

**Priority 1 Datasets**:
1. **helpful_instructions** (59 MB, 185,269 examples)
   - License: Apache 2.0 ✅
   - Size: Fits in current storage
   - Action: Download + review

2. **Gab100MFinetune** (831 MB, 553,427 conversations)
   - License: MIT ✅
   - Size: Might fit with cleanup
   - Action: Download + review

3. **DialoguesEN-22k-Instructional** (22,000, MIT)
   - License: MIT ✅
   - Size: Likely fits
   - Action: Download + review

**Total Estimated Size**: ~1 GB

**Review Process**:
1. Download dataset
2. Inspect schema
3. Check quality
4. Remove PII
5. Convert to NexusAI schema
6. Human review sample
7. Approve for training

### Phase 2: Original English Data Creation (Short-term)

**Target**: 5,000 English conversations

**Data Types**:
- General conversation
- Question answering
- Instructions and explanations
- Creative writing
- Formal and informal registers

**Creation Process**: Same as Bengali (native speakers, validation, review)

**Timeline**: 1-2 months

### Phase 3: Expansion (Long-term)

**Target**: 30,000 English conversations total

**Sources**:
- Public datasets (verified licenses)
- Original data creation
- User feedback collection

---

## Banglish Data Strategy

### Critical Finding

**No high-quality Banglish text datasets with clear licenses exist in public repositories.**

Available sources:
- **Banglish-English** (14,000) — license unclear
- **BnSentMix** (20,000) — license unclear
- **Code-mixed Chaos** (10,234) — license unclear, toxicity-focused
- **Banglish (CSVC-Net)** — audio format, not suitable

**Conclusion**: Original Banglish data creation is the primary strategy.

### Phase 1: Original Banglish Data Creation (Primary Strategy)

**Target**: 10,000 Banglish conversations

**Data Types**:
- Code-switched conversations
- Mixed-language expressions
- Transliterated Bengali
- Casual messaging style
- Natural Banglish expressions

**Creation Process**:
1. **Banglish Speakers**: Recruit native Banglish speakers
2. **Authoring**: Write original Banglish conversations
3. **Validation**: Natural code-switching patterns
4. **Quality Check**: Authentic transliteration
5. **Schema Compliance**: Follow NexusAI schema
6. **Human Review**: CLI review workflow
7. **Approval**: Genuine human approval

**Quality Standards**:
- Natural code-switching patterns
- Authentic transliteration
- Context-appropriate mixing
- No machine translation

**Timeline**: 2-3 months for 10,000 conversations

### Phase 2: Code-Switching Research (Long-term)

**Research Focus**:
- Study natural Banglish code-switching patterns
- Analyze social media Banglish (with consent)
- Develop Banglish-specific guidelines
- Create Banglish style guide

---

## Language Distribution Targets

### Phase 1 (Immediate)
- Bengali: 5,000 (original creation)
- English: 10,000 (5,000 original + 5,000 from datasets)
- Banglish: 2,000 (original creation)
- **Total**: 17,000

### Phase 2 (Short-term)
- Bengali: 10,000
- English: 20,000
- Banglish: 5,000
- **Total**: 35,000

### Phase 3 (Long-term)
- Bengali: 20,000
- English: 30,000
- Banglish: 10,000
- **Total**: 60,000

---

## Data Quality Standards

### Bengali
- Native or highly proficient language
- Proper grammar and spelling
- Cultural appropriateness
- No machine translation
- Bengali script (not transliterated)

### English
- Correct grammar and spelling
- Natural language use
- Diverse vocabulary
- Context appropriateness

### Banglish
- Natural code-switching patterns
- Authentic transliteration
- Context-appropriate mixing
- No machine translation

---

## Integration Strategy

### Schema Alignment
All datasets must be converted to NexusAI dataset schema (v2.0):
- record_id
- conversation_id
- messages (with role, content, language, turn_index)
- language (bengali, english, mixed)
- domain
- source_type
- review_status
- license_status
- privacy_status

### Language Detection
Implement language detection for mixed-language conversations:
- Unicode range detection
- Bengali script detection
- English detection
- Mixed classification

### Metadata Tracking
Track for each conversation:
- Source (original_human, imported, etc.)
- License
- Reviewer
- Review timestamp
- Content hash

---

## Storage Requirements

### Bengali
- Original creation (5,000): ~10 MB
- Public datasets (if used): 52 GB - 755 MB (need storage)

### English
- Verified datasets (priority 1): ~1 GB
- Original creation (5,000): ~10 MB

### Banglish
- Original creation (10,000): ~20 MB

**Total (Phase 1 without large public datasets)**: ~40 MB ✅ fits

**Total (with large Bengali datasets)**: 52 GB - 1 GB ❌ requires external storage

---

## Risks and Mitigation

### Risk 1: License Verification Fails
**Mitigation**: Primary reliance on original data creation

### Risk 2: Insufficient Native Speakers
**Mitigation**: Gradual collection, prioritize quality over quantity

### Risk 3: Banglish Quality Variability
**Mitigation**: Strict quality guidelines, human review

### Risk 4: Storage Constraint
**Mitigation**: Focus on original creation (smaller footprint), defer large datasets

---

## Next Steps

1. **Immediate**: Verify licenses for priority English datasets
2. **Immediate**: Begin original Bengali data creation (5,000)
3. **Immediate**: Begin original Banglish data creation (2,000)
4. **Short-term**: Download verified English datasets
5. **Long-term**: Address storage for large Bengali datasets

---

**Strategy Created**: 2026-10-31  
**Status**: STRATEGY COMPLETE
