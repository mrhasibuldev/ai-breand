# DATA_COLLECTION_MASTER_STRATEGY

**Date**: 2026-10-31  
**Task**: Large-Scale Data Collection Master Strategy  
**Strategy Type**: DATA FOUNDATION PLAN  
**Status**: IN PROGRESS

---

## Executive Summary

This document defines the master strategy for building a large-scale, legally compliant, multilingual dataset foundation for NexusAI. The strategy addresses the need for ~95,000+ training examples across multiple languages, domains, and intelligence skills.

**Note**: This is a planning document. Actual data collection must be approved by the project owner before implementation.

---

## Storage Capacity Analysis

### Current Disk Space

**C: Drive**: 2.9 GB free (119 GB total)
**D: Drive**: 50 MB free (29.7 GB total)

**Current Data Directory Size**: 0.8 MB (867.8 KB)

**Storage Constraints**: 
- Limited free space on C: drive
- D: drive nearly full
- Cannot download large datasets without storage planning
- Need to plan for compression, incremental downloads, or external storage

---

## Phase 0: Baseline Dataset Inventory

### Existing Datasets

#### Pilot Datasets
**Location**: `packages/ai-core/data/pilots/b4-b2-p1/`

| File | Size | Conversations | Status |
|------|------|---------------|--------|
| pilot_dataset.json | 12.9 KB | 9 | Original human-authored |
| pilot_dataset_expansion_drafts.json | 95.1 KB | 71 | Original drafts |
| combined_for_review.json | 109.6 KB | 80 | Combined for review |
| pilot_dataset_pending_review.json | - | - | Pending review status |
| pilot_dataset_reviewed.json | - | - | Simulated approvals (audit only) |

**Verified Counts**:
- Pilot: 9 conversations ✅
- Expansion: 71 conversations (metadata claimed 91, actual 71) ❌
- Combined: 80 conversations ✅

**Language Distribution (Combined)**:
- Bengali: 13
- English: 50
- Mixed: 17
- Total: 80

#### Training Datasets
**Location**: `packages/ai-core/data/`

| File | Size | Records | Format | Status |
|------|------|--------|--------|--------|
| train_v2.json | 149.0 KB | 502 | List of message lists | Training data |
| conversational_data.json | 5.1 KB | - | Unknown format | Legacy |
| merged_train.json | - | - | - | Legacy |
| train_final.json | - | - | - | Legacy |

#### Public Datasets
**Location**: `packages/ai-core/data/public_datasets/`

| Path | Size | Description |
|------|------|-------------|
| v1.0/ | - | Cleaned public dataset |
| v1.0_cleaned/ | - | Further cleaned version |
| bengali_english_mixed.json | - | Mixed language dataset |

#### Synthetic Datasets
**Location**: `packages/ai-core/data/synthetic/`

| File | Description |
|------|-------------|
| train.json | Synthetic training data |
| validation.json | Synthetic validation data |

#### User Data
**Location**: `packages/ai-core/data/user_data/`

| File | Description |
|------|-------------|
| sample_dataset.json | Sample user data |

### Dataset Schema

**Schema Version**: 2.0
**Schema File**: `dataset_schema.py`

**Key Fields**:
- record_id: Unique identifier
- conversation_id: Conversation identifier
- messages: List of messages (user/assistant)
- language: Language classification (bengali, english, mixed, unknown)
- domain: Domain classification (conversation, knowledge, reasoning, mathematics, coding, writing, planning, health_wellness, other)
- source_type: Source type (original_human, original_synthetic, imported, converted)
- review_status: Review status (pending, approved, rejected)
- license_status: License status (project-owned, verified-external, unverified)
- privacy_status: Privacy status (public, private, contains_pii)
- split: Dataset split (train, validation, test, pending)

### Existing Tools

**Validation**: `dataset_validator.py`
**Processing**: `dataset_processor.py`
**Review CLI**: `human_review_cli.py`
**Quality Analysis**: `quality_analyzer.py`
**Adapters**: `training_adapter.py`, `training_adapter_compatible.py`

### Human Review Status

**Current Status**: 
- 80 conversations pending review
- 0 genuinely human-approved
- CLI review workflow implemented
- Zero records approved during implementation

---

## Phase 1: Data Requirements and Collection Strategy

### A. Language Coverage

#### Bengali (Native Script)

**Required Data**: 20,000+ conversations

**Data Types**:
- Daily conversations (greetings, casual chat)
- Question answering (what, how, why)
- Storytelling and narrative
- Cultural context
- Idioms and expressions
- Formal and informal registers

**Quality Criteria**:
- Native or highly proficient Bengali
- Proper grammar and spelling
- Natural conversation flow
- Cultural appropriateness
- No transliteration (must use Bengali script)

**Current Status**: 13 conversations (0.07% of target)

#### English

**Required Data**: 30,000+ conversations

**Data Types**:
- General conversation
- Question answering
- Instructions and explanations
- Creative writing
- Formal and informal registers

**Quality Criteria**:
- Correct grammar and spelling
- Natural language use
- Diverse vocabulary
- Context appropriateness

**Current Status**: 50 conversations (0.17% of target)

#### Banglish

**Required Data**: 10,000+ conversations

**Data Types**:
- Code-switched conversations
- Mixed-language expressions
- Transliterated Bengali
- Casual messaging style

**Quality Criteria**:
- Natural code-switching patterns
- Authentic transliteration
- Context-appropriate mixing

**Current Status**: 17 conversations (0.17% of target)

#### Bengali-English Code-Switching

**Required Data**: 5,000+ conversations

**Data Types**:
- Natural code-switching
- Contextual language switching
- Mixed-language explanations

**Quality Criteria**:
- Natural switching patterns
- Grammatical correctness in both languages
- Appropriate mixing

**Current Status**: 0 conversations (0% of target)

### B. Knowledge Domains

#### Domain Coverage Matrix

| Domain | Required | Current | Gap | Priority |
|--------|----------|---------|-----|----------|
| General Conversation | 30,000 | 80 | 29,920 | CRITICAL |
| General Knowledge | 10,000 | 0 | 10,000 | HIGH |
| Science | 5,000 | 0 | 5,000 | HIGH |
| Mathematics | 3,000 | 0 | 3,000 | HIGH |
| Physics | 2,000 | 0 | 2,000 | MEDIUM |
| Chemistry | 2,000 | 0 | 2,000 | MEDIUM |
| Biology | 2,000 | 0 | 2,000 | MEDIUM |
| Computer Science | 3,000 | 0 | 3,000 | HIGH |
| Programming | 2,000 | 0 | 2,000 | MEDIUM |
| History | 2,000 | 0 | 2,000 | MEDIUM |
| Geography | 2,000 | 0 | 2,000 | MEDIUM |
| Education | 2,000 | 0 | 2,000 | MEDIUM |
| Language & Grammar | 2,000 | 0 | 2,000 | MEDIUM |
| Writing | 2,000 | 0 | 2,000 | MEDIUM |
| Logical Reasoning | 5,000 | 0 | 5,000 | CRITICAL |
| Critical Thinking | 3,000 | 0 | 3,000 | HIGH |
| Problem-Solving | 5,000 | 0 | 5,000 | CRITICAL |
| Planning | 2,000 | 0 | 2,000 | HIGH |
| Decision-Making | 2,000 | 0 | 2,000 | HIGH |
| Everyday Life | 3,000 | 0 | 3,000 | MEDIUM |
| Health & Wellness | 2,000 | 0 | 2,000 | MEDIUM |
| Technology | 2,000 | 0 | 2,000 | MEDIUM |
| Business & Economics | 2,000 | 0 | 2,000 | LOW |
| Creativity | 2,000 | 0 | 2,000 | LOW |
| Storytelling | 2,000 | 0 | 2,000 | LOW |
| Safety & AI Behavior | 2,000 | 0 | 2,000 | CRITICAL |
| Instructions & Tasks | 3,000 | 0 | 3,000 | HIGH |

**Total Required**: ~95,000 examples across all domains
**Current**: 80 conversations
**Gap**: ~94,920 examples (99.9% gap)

### C. Intelligence Skill Coverage

#### Skill Type Requirements

| Skill Type | Required Examples | Current | Data Format | Priority |
|------------|------------------|---------|-------------|----------|
| Conversational Understanding | 30,000 | 80 | Conversations | CRITICAL |
| Instruction Following | 10,000 | 0 | Instruction-response | CRITICAL |
| Context Retention | 5,000 | 0 | Long conversations | HIGH |
| Multi-turn Conversations | 20,000 | 80 | Conversations | CRITICAL |
| Step-by-Step Reasoning | 5,000 | 0 | Reasoning chains | CRITICAL |
| Mathematical Problem-Solving | 3,000 | 0 | Math problems | HIGH |
| Coding & Debugging | 2,000 | 0 | Code examples | MEDIUM |
| Summarization | 3,000 | 0 | Document-summary pairs | MEDIUM |
| Information Extraction | 3,000 | 0 | Text-entity pairs | MEDIUM |
| Classification | 3,000 | 0 | Text-label pairs | MEDIUM |
| Planning | 2,000 | 0 | Plan-task pairs | HIGH |
| Decision-Making | 2,000 | 0 | Scenario-decision pairs | HIGH |
| Error Correction | 2,000 | 0 | Error-fix pairs | MEDIUM |
| Explanation Generation | 5,000 | 0 | Question-explanation pairs | HIGH |
| Uncertainty & Factual Accuracy | 2,000 | 0 | Fact-checking pairs | CRITICAL |
| Safety & Refusal | 2,000 | 0 | Harmful request-refusal | CRITICAL |

**Note**: Not all data needs to be question-answer pairs. Conversations, instructions, plans, and multi-turn dialogs are equally important.

---

## Storage Constraints and Planning

### Current Limitations

**C: Drive**: 2.9 GB free
**D: Drive**: 50 MB free (essentially full)

### Estimated Storage Requirements

**Raw Data** (uncompressed):
- 95,000 conversations at ~2 KB each = ~190 MB
- With metadata and overhead = ~250 MB

**Processed Data**:
- Normalized text = ~200 MB
- Embeddings (if pre-computed) = ~500 MB
- Total processed = ~700 MB

**Backups**:
- 1 backup = ~700 MB
- Total with backup = ~1.4 GB

**Growth Over Time**:
- Version 1.0: ~1.4 GB
- Version 2.0: +1.4 GB = ~2.8 GB
- Version 3.0: +1.4 GB = ~4.2 GB

### Storage Strategy

**Immediate (C: Drive)**:
- Keep current 0.8 MB data
- Add up to 1 GB new data
- Keep 1 backup = ~2 GB total
- **Risk**: May exceed C: drive capacity

**Recommended**:
1. **External Storage**: Add external HDD or SSD (1-2 TB)
2. **Cloud Storage**: Use cloud storage for backups (Google Drive, Dropbox, etc.)
3. **Compression**: Use compression for raw data storage
4. **Incremental**: Download in batches, process, delete raw after processing

**Critical Rule**: Do not download large datasets without confirming available storage and cleanup strategy.

---

## Collection Strategy

### Phase 1: Human-Authored Data (Immediate)

**Target**: 5,000 conversations
**Timeline**: 1-2 months
**Method**: Project owner and trusted contributors
**Focus**: Bengali, English, Banglish basics
**Cost**: Time investment only
**Storage**: ~10 MB

### Phase 2: Public Dataset Integration (Short-term)

**Target**: 20,000 conversations
**Timeline**: 2-3 months
**Method**: License-verified public datasets
**Focus**: General knowledge, basic reasoning
**Risks**: License verification required
**Storage**: ~40 MB

### Phase 3: User Feedback Integration (Long-term)

**Target**: 50,000+ conversations
**Timeline**: Ongoing
**Method**: Collect user conversations with consent
**Focus**: Real-world interactions
**Privacy**: Explicit consent, anonymization
**Storage**: ~100 MB

### Phase 4: Synthetic Generation (Supplemental)

**Target**: 10,000 conversations
**Timeline**: After model quality improves
**Method**: Generate with existing model, human review
**Focus**: Edge cases, rare scenarios
**Risks**: Quality varies, strict review required
**Storage**: ~20 MB

---

## Data Quality Standards

### Minimum Requirements

**For All Records**:
- Valid schema compliance
- Required fields present
- No PII (unless explicitly marked and handled)
- Verified license status
- Clear provenance
- Language correctly labeled
- Domain correctly labeled
- Quality score above threshold

**Bengali-Specific**:
- Native or highly proficient language
- Proper grammar and spelling
- Cultural appropriateness
- No machine translation from English

**Banglish-Specific**:
- Natural code-switching patterns
- Authentic transliteration
- Context-appropriate mixing

**Reasoning-Specific**:
- Clear logical structure
- Correct reasoning chains
- Step-by-step explanations where applicable

**Math-Specific**:
- Clear problem statements
- Correct solutions
- Step-by-step work shown

**Code-Specific**:
- Correct syntax
- Functional code
- Safe code (no vulnerabilities)
- Clear explanations

---

## Collection Priorities

### Immediate Priority (Phase 1)

1. **Approve current 80 conversations** for initial training
2. **Collect 4,920 additional conversations** (human-authored)
3. **Implement subword tokenizer**
4. **Train 50M parameter model**

### Short-Term Priority (Phase 2)

1. **Identify and verify 5-10 public datasets**
2. **License verification for each**
3. **Download and integrate 20,000 conversations**
4. **Human review all imported data**

### Long-Term Priority (Phase 3+)

1. **Implement user feedback collection**
2. **Scale to 50,000+ conversations**
3. **Continuous quality improvement**
4. **Regular dataset versioning**

---

## Next Steps

### Immediate Actions

1. **Storage Planning**: Acquire external storage or cloud storage plan
2. **Data Approval**: Approve current 80 conversations for training
3. **Human Data Collection**: Begin collecting 4,920 additional conversations
4. **Public Dataset Research**: Identify 5-10 candidate public datasets
5. **License Verification**: Verify licenses for candidate datasets

### Blockers

1. **Storage**: Limited disk space (2.9 GB on C:, 50 MB on D:)
2. **Data Volume**: Need 95,000+ examples, currently have 80
3. **Human Review Capacity**: Need systematic review workflow
4. **License Verification**: Need legal review for public datasets

---

**Strategy Status**: IN PROGRESS — STORAGE CONSTRAINTS IDENTIFIED

**Recommendation**: Address storage constraints before proceeding with large-scale data collection.
