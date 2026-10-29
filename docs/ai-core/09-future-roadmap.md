# Future Roadmap

**Last Updated**: 2026-10-26  
**Verification Status**: PLANNING (not implemented)

---

## Overview

This roadmap prioritizes investigations and improvements for the NexusAI AI Core based on verified findings from the forensic audit.

## Priority Levels

- **P0 (Critical)**: Blocks all AI Core functionality
- **P1 (High)**: Major architectural issues limiting independence
- **P2 (Medium)**: Functional improvements
- **P3 (Low)**: Infrastructure and optimizations

---

## Phase 1: Data Foundation (P0)

### Objective

Fix the root cause of poor model quality by collecting sufficient training data.

### Tasks

#### 1.1 Data Collection (P0-CRITICAL)

**Status**: NOT STARTED

**Description**: Collect sufficient training data to support a 2000+ token vocabulary.

**Requirements**:
- Minimum 1000 samples (target 10,000+ samples)
- Bengali and English balanced distribution
- Diverse topics (greetings, questions, knowledge, conversations)
- Proper formatting (conversational pairs preferred)
- UTF-8 encoding for Bengali text

**Sources to Consider**:
- Public Bengali/English conversation datasets
- Existing conversations from application (if available)
- Synthetic data generation (as supplement only)
- Domain-specific knowledge (health, wellness, general knowledge)

**Acceptance Criteria**:
- Dataset contains 1000+ samples
- Vocabulary built from dataset reaches 1500+ tokens
- Dataset quality verified (no excessive duplicates, proper formatting)

**Estimated Effort**: HIGH (requires data collection effort)

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (requires user action to collect data)

---

#### 1.2 Data Quality Validation (P0-CRITICAL)

**Status**: NOT STARTED

**Description**: Validate collected dataset for quality issues.

**Checks**:
- Duplicate detection and removal
- Malformed data filtering
- Length filtering (remove too short/long samples)
- Encoding validation (UTF-8 for Bengali)
- Language distribution analysis
- Topic diversity analysis

**Acceptance Criteria**:
- Dataset passes all quality checks
- Quality report generated
- Issues documented and resolved

**Estimated Effort**: MEDIUM

**Dependencies**: 1.1

**Authorization**: NOT AUTHORIZED (dependent on 1.1)

---

#### 1.3 Dataset Preprocessing Pipeline (P0-CRITICAL)

**Status**: NOT STARTED

**Description**: Implement proper data preprocessing pipeline.

**Requirements**:
- Punctuation separation from words
- Proper tokenization (improved over current whitespace split)
- Data augmentation (if needed)
- Train/validation/test split
- Metadata preservation

**Acceptance Criteria**:
- Preprocessing pipeline implemented
- Tokenizer vocabulary reaches 1500+ tokens
- Preprocessed dataset saved

**Estimated Effort**: MEDIUM

**Dependencies**: 1.1, 1.2

**Authorization**: NOT AUTHORIZED (dependent on 1.1)

---

## Phase 2: Model Retraining (P0)

### Objective

Retrain MediumTransformer with sufficient data and proper vocabulary.

### Tasks

#### 2.1 Fix Tokenizer Consistency (P0-CRITICAL)

**Status**: COMPLETED (Phase 4)

**Description**: Fixed training/inference tokenizer mismatch.

**Problem**: Training uses train_cleaned.json (74 tokens, Bengali/English mix), inference rebuilt from train_v2.json (74 tokens, English-heavy). Token sets were different despite same size.

**Resolution Applied** (Phase 4):
- Modified `ml-service/main.py` to load tokenizer vocabulary from checkpoint
- Added check for `tokenizer_vocab` in checkpoint
- If tokenizer_vocab exists, load it directly ensuring exact compatibility
- If tokenizer_vocab missing, issue WARNING and fall back to rebuilding
- Ensures exact token-to-ID mapping compatibility

**Acceptance Criteria**:
- ✅ Training and inference use identical tokenizer vocabulary
- ✅ Bengali words consistently included in both vocabularies
- ✅ No unknown token mismatches

**Estimated Effort**: LOW

**Dependencies**: None

**Authorization**: AUTHORIZED (Phase 4)

---

#### 2.2 Retrain MediumTransformer (P0-CRITICAL)

**Status**: NOT STARTED

**Description**: Retrain MediumTransformer with new dataset AFTER tokenizer consistency is fixed.

**Configuration**:
- Use improved dataset from Phase 1
- Train for 10+ epochs (monitor validation loss)
- Implement early stopping
- Monitor training and validation loss
- Save checkpoints with full metadata
- Save tokenizer with checkpoint

**Acceptance Criteria**:
- Model trains successfully
- Validation loss improves and stabilizes
- Checkpoints saved with metadata
- Training metrics logged
- Tokenizer saved with checkpoint

**Estimated Effort**: HIGH (CPU training may be slow)

**Dependencies**: 1.1, 1.2, 1.3 (Phase 1 data foundation required, tokenizer consistency now complete)

**Authorization**: NOT AUTHORIZED (dependent on Phase 1)

---

#### 2.3 Establish Evaluation Baseline (P0-CRITICAL)

**Status**: NOT STARTED

**Description**: Run evaluation suite on current model to establish baseline before retraining.

**Required Fix**:
- Adapt evaluation suite for MediumTransformer (COMPLETED in Phase 4 - now model-agnostic)
- Run all 10 evaluation tests
- Document baseline performance
- Save baseline results

**Acceptance Criteria**:
- Evaluation suite adapted for MediumTransformer
- Baseline evaluation completed
- Baseline results documented

**Estimated Effort**: MEDIUM

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (evaluation execution required)

---

#### 2.4 Model Evaluation (P0-CRITICAL)

**Status**: NOT STARTED

**Description**: Evaluate retrained model quality.

**Tests**:
- Basic generation quality
- Question answering capability
- Context retention
- Bengali/English language support
- Coherence and relevance

**Acceptance Criteria**:
- Model generates coherent responses
- Model can answer basic questions
- Evaluation report generated
- Quality threshold met (to be defined)

**Estimated Effort**: MEDIUM

**Dependencies**: 2.2

**Authorization**: NOT AUTHORIZED (dependent on 2.2)

---

## Phase 3: Architectural Independence (P1)

### Objective

Remove NexusAI-specific coupling from ML service to enable standalone AI Core.

### Tasks

#### 3.1 Remove Hardcoded Responses (P1-HIGH)

**Status**: NOT STARTED

**Description**: Move deterministic responses from ML service to application layer.

**Changes**:
- Remove hardcoded Bengali/English responses from `main.py`
- Define response interface contract
- Implement response provider interface
- Application provides responses via configuration or API

**Acceptance Criteria**:
- ML service has no hardcoded NexusAI responses
- Response system is pluggable
- Application can provide custom responses

**Estimated Effort**: MEDIUM

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (architectural refactoring)

---

#### 3.2 Parameterize System Prompt (P1-HIGH)

**Status**: NOT STARTED

**Description**: Make system prompt configurable instead of hardcoded.

**Changes**:
- Remove hardcoded system prompt from `main.py`
- Add system prompt configuration (config file or environment variable)
- Allow application to provide custom system prompt

**Acceptance Criteria**:
- System prompt is externalized
- ML service loads prompt from configuration
- Application can customize prompt

**Estimated Effort**: LOW

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (architectural refactoring)

---

#### 3.3 Externalize Filesystem Paths (P1-HIGH)

**Status**: NOT STARTED

**Description**: Replace hardcoded filesystem paths with configuration.

**Changes**:
- Create configuration file (YAML or JSON)
- Define all paths in configuration
- ML service loads paths from configuration
- Support environment variable overrides

**Acceptance Criteria**:
- All paths are configurable
- ML service works outside monorepo structure
- Configuration file documented

**Estimated Effort**: MEDIUM

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (architectural refactoring)

---

#### 3.4 Fix Model Status Endpoint (P1-HIGH)

**Status**: NOT STARTED

**Description**: Extract actual model information instead of hardcoded values.

**Changes**:
- Extract model name from loaded model class
- Extract checkpoint path from loaded checkpoint
- Extract sequence length from model configuration
- Remove hardcoded values from endpoint

**Acceptance Criteria**:
- Endpoint reports actual model information
- Endpoint matches runtime reality
- Information is dynamically retrieved

**Estimated Effort**: LOW

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (code fix required)

---

## Phase 4: Functional Improvements (P2)

### Objective

Improve AI Core functionality after model quality is fixed.

### Tasks

#### 4.1 Pass Context to Model (P2-MEDIUM)

**Status**: NOT STARTED

**Description**: Include conversation history in model prompt.

**Changes**:
- Modify prompt construction to include conversation context
- Implement context window management
- Handle context length limits

**Acceptance Criteria**:
- Model prompt includes conversation history
- Context window properly managed
- Model can maintain context across turns

**Estimated Effort**: MEDIUM

**Dependencies**: 2.2 (model quality must be usable first)

**Authorization**: NOT AUTHORIZED (implementation required)

---

#### 4.2 Fix Retrieval System (P2-MEDIUM)

**Status**: NOT STARTED

**Description**: Investigate and fix why simple retrieval returns no context.

**Investigation**:
- Analyze keyword matching algorithm
- Check document/chunk content
- Verify stop word list
- Test with various queries

**Changes**:
- Improve keyword matching logic
- Add more relevant documents to knowledge base
- Implement better scoring

**Acceptance Criteria**:
- Retrieval returns relevant context for general questions
- Context length > 0 for test queries
- Retrieval system documented

**Estimated Effort**: MEDIUM

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (investigation required)

---

#### 4.3 Implement RAG Data Pipeline (P2-MEDIUM)

**Status**: NOT STARTED

**Description**: Create processed data directory and pipeline for RAG system.

**Changes**:
- Implement data ingestion pipeline
- Process documents into RAG format
- Save to `data/processed/` directory
- Test RAG loading

**Acceptance Criteria**:
- RAG system loads successfully
- Processed data exists
- RAG augmentation works

**Estimated Effort**: MEDIUM

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (implementation required)

---

#### 4.4 Implement Persistent Context (P2-MEDIUM)

**Status**: NOT STARTED

**Description**: Implement persistent conversation context storage.

**Options**:
- Database-backed context (PostgreSQL)
- Redis-backed context
- File-based context

**Acceptance Criteria**:
- Context persists across service restarts
- Context can be retrieved by conversation ID
- Implementation documented

**Estimated Effort**: MEDIUM to HIGH

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (infrastructure required)

---

## Phase 5: Infrastructure (P3)

### Objective

Improve development and deployment infrastructure.

### Tasks

#### 5.1 Training Logging (P3-LOW)

**Status**: NOT STARTED

**Description**: Add comprehensive logging to training pipeline.

**Features**:
- Training loss per epoch
- Validation loss per epoch
- Learning rate schedule
- Gradient norms
- Training duration

**Acceptance Criteria**:
- Training logs saved to file
- Metrics can be visualized
- Training history preserved

**Estimated Effort**: LOW

**Dependencies**: 2.1

**Authorization**: NOT AUTHORIZED (implementation required)

---

#### 5.2 Tensorboard Integration (P3-LOW)

**Status**: NOT STARTED

**Description**: Add Tensorboard logging for training visualization.

**Acceptance Criteria**:
- Tensorboard logging implemented
- Metrics visible in Tensorboard
- Documentation provided

**Estimated Effort**: LOW

**Dependencies**: 5.1

**Authorization**: NOT AUTHORIZED (implementation required)

---

#### 5.3 GPU Support (P3-LOW)

**Status**: NOT STARTED

**Description**: Add GPU support for training and inference.

**Requirements**:
- CUDA-compatible code
- GPU device selection
- GPU memory management
- Fallback to CPU if GPU unavailable

**Acceptance Criteria**:
- Model can train on GPU if available
- Model can infer on GPU if available
- Fallback to CPU works correctly

**Estimated Effort**: MEDIUM

**Dependencies**: None

**Authorization**: NOT AUTHORIZED (implementation required)

---

## Blocked Tasks

The following tasks are BLOCKED until Phase 1 and Phase 2 are complete:

- All P2 tasks (functional improvements)
- All P3 tasks (infrastructure)
- Standalone AI Core extraction
- Production deployment

**Additional Blocker for Phase 2**:
- Task 2.2 (Retrain MediumTransformer) is BLOCKED until 2.1 (Fix Tokenizer Consistency) is complete
- Task 2.4 (Model Evaluation) is BLOCKED until 2.2 (Retrain) is complete

**Reason**: Model quality is too poor to justify architectural work. Fix the data and model first. Tokenizer consistency must be fixed before retraining to avoid introducing new mismatches.

---

## Not Authorized

The following tasks are explicitly NOT AUTHORIZED:

- Removing deterministic responses (AI-012) — keep until model quality improves
- Blindly changing tokenizer — fix data first
- Blindly changing architecture — fix data first
- Randomly installing AI libraries — no external AI providers
- Integrating external AI APIs — defeats purpose of own model
- Database schema changes — not related to AI Core

---

## Timeline Estimates

### Phase 1: Data Foundation
- **Estimated**: 2-4 weeks (user-dependent data collection)
- **Blocker**: User must collect data

### Phase 2: Model Retraining
- **Estimated**: 1-2 weeks (CPU training may be slow)
- **Blocker**: Dependent on Phase 1

### Phase 3: Architectural Independence
- **Estimated**: 1-2 weeks
- **Blocker**: None (can be done in parallel)

### Phase 4: Functional Improvements
- **Estimated**: 2-3 weeks
- **Blocker**: Should wait for Phase 2 (model quality)

### Phase 5: Infrastructure
- **Estimated**: 1-2 weeks
- **Blocker**: None (can be done anytime)

---

## Success Criteria

### Phase 1 Success
- Dataset contains 1000+ samples
- Vocabulary size >= 1500 tokens
- Dataset quality validated

### Phase 2 Success
- Model trains successfully
- Model generates coherent responses
- Model can answer basic questions

### Phase 3 Success
- ML service has no hardcoded NexusAI logic
- All paths are configurable
- System prompt is externalized

### Phase 4 Success
- Context is passed to model
- Retrieval returns relevant context
- Context is persistent

### Overall Success
- AI Core is standalone and reusable
- Model quality is acceptable for basic use
- AI Core can be used by multiple applications

---

## References

- **Known Issues**: `07-known-issues.md`
- **Audit History**: `08-audit-history.md`
- **Model Inventory**: `02-model-inventory.md`
- **Dataset Audit**: `05-dataset-audit.md`
