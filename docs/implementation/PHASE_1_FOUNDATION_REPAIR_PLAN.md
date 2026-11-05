# NexusAI Phase 1 - Foundation Repair Readiness & Implementation Plan

**Date**: 2026-11-05
**Type**: Phase 1 Foundation Repair Plan
**Status**: READY FOR FOUNDER AUTHORIZATION

---

## Executive Summary

**Current State**: NexusAI has a solid software architecture but **no trained production model**. The system runs with randomly initialized weights.

**Readiness Status**: ✅ READY for foundation repair

**Key Findings**:
1. ✅ **Validated BPETokenizer exists**: Phase 9.2 BPE 8K tokenizer fully validated (0% UNK, 100% round-trip)
2. ✅ **Dataset ready**: Phase 10 dataset has 1,812 samples (train: 1,449, val: 181, test: 182)
3. ✅ **Model architecture sound**: MediumTransformer with 2.4M parameters
4. ⚠️ **Experimental training attempted**: Phase 10 training completed but checkpoint not saved to expected location
5. ❌ **No production checkpoint**: ML service still uses random weights
6. ❌ **Consent enforcement incomplete**: MemoryConsentBoundary not implemented

**Recommended Action**: Integrate validated Phase 9.2 BPE 8K tokenizer and Phase 10 dataset into production, retrain model properly, and save checkpoint to production location.

---

## A. Tokenizer Investigation

### A.1 SimpleTokenizer (Production)

**Location**: `packages/ai-core/tokenizer/tokenizer.py`

**Verified Implementation**:
- Type: Word-level tokenizer
- Tokenization: `text.lower().split()`
- Special tokens: PAD, UNK, BOS, EOS
- Configurable vocab_size (default 5000)
- Actual production vocab: **74 tokens** (confirmed from previous audit)

**Production Usage**:
```python
# packages/ai-core/ml-service/main.py line 288
tokenizer = SimpleTokenizer(vocab_size=vocab_size)
```

**Issues**:
- 74-token vocabulary causes 60-80% UNK rate
- No Bengali support
- Punctuation not preserved
- Numbers poorly represented

### A.2 BPETokenizer (Experimental)

**Location**: `packages/ai-core/tokenizer/bpe_tokenizer.py`

**Verified Implementation**:
- Type: Byte-Pair Encoding (subword)
- Special tokens: PAD, UNK, BOS, EOS, USER, ASSISTANT, SEP
- Unicode-aware for Bengali and English
- Whitespace preservation fixed in v1.1.0
- Configurable vocab_size (default 32000)

**Validation Status** (from Phase 9.3):
```json
{
  "phase9_2_bpe_8k": {
    "bengali_unk_rate": 0.0,
    "bengali_round_trip": 1.0,
    "english_unk_rate": 0.0,
    "english_round_trip": 1.0,
    "mixed_unk_rate": 0.0,
    "mixed_round_trip": 1.0,
    "validation_status": "PASS"
  }
}
```

**Location of Validated Tokenizer**:
- Path: `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`
- Vocab size: 8,000 tokens
- Status: **FULLY VALIDATED AND READY FOR EXPERIMENTAL MODEL TRAINING**

**Tokenizer Statistics**:
- Bengali UNK rate: 0%
- English UNK rate: 0%
- Mixed language UNK rate: 0%
- Round-trip accuracy: 100% (with NFC normalization)
- Test suite: 171 tests (68 Bengali, 51 English, 52 mixed)

### A.3 SentencePiece Tokenizers (Experimental)

**Location**: `packages/ai-core/data/experimental/phase7/tokenizer_models/`

**Available Models**:
- `sp_8k_bpe.model` (8,000 tokens, BPE)
- `sp_8k_unigram.model` (8,000 tokens, Unigram)
- `sp_16k_bpe.model` (16,000 tokens, BPE)
- `sp_16k_unigram.model` (16,000 tokens, Unigram)
- `sp_32k_bpe.model` (32,000 tokens, BPE)

**Status**: Available but not validated to the same level as Phase 9.2 BPE 8K.

### A.4 Recommendation

**Use Phase 9.2 BPE 8K tokenizer** because:
1. Fully validated with 0% UNK rate
2. 100% round-trip accuracy
3. Tested on Bengali, English, and mixed text
4. Ready for production integration
5. Reasonable vocabulary size (8,000 tokens)

**Vocabulary Size Justification**:
- 8,000 tokens provides good coverage without excessive model size
- Smaller than 16K/32K (faster training, less memory)
- Larger than 2K/4K (better language representation)
- Validated on actual dataset

---

## B. Dataset Investigation

### B.1 Production Dataset (v1.0)

**Location**: `packages/ai-core/data/public_datasets/v1.0/`

**Verified Statistics**:
```json
{
  "train_samples": 19,
  "val_samples": 2,
  "test_samples": 3,
  "total_samples": 24
}
```

**Sample Content**:
- Bengali: "ঢাকা কী?", "আমার নাম NexusAI।"
- English: "I can have conversations, answer questions..."
- Mixed: Conversational pairs

**Assessment**: **INSUFFICIENT for training** - 24 samples too small for meaningful training.

### B.2 Phase 9.2 Corpus

**Location**: `packages/ai-core/data/experimental/phase9_2/corpus/`

**Verified Statistics**:
```json
{
  "bengali_texts": 726,
  "english_texts": 1111,
  "mixed_texts": 14,
  "total_texts": 1851,
  "bengali_words": 10561,
  "english_words": 21105,
  "mixed_words": 127,
  "total_words": 31793
}
```

**Language Distribution**:
- Bengali: 39.2%
- English: 60.0%
- Mixed: 0.8%

**Normalization**: NFC (Unicode normalization)

**Assessment**: Good corpus for tokenizer training, but Phase 10 provides better formatted dataset.

### B.3 Phase 10 Dataset (Experimental)

**Location**: `packages/ai-core/data/experimental/phase10/datasets/`

**Verified Statistics**:
```json
{
  "tokenizer": {
    "path": "phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model",
    "vocab_size": 8000
  },
  "corpus": {
    "original_lines": 1865,
    "unique_lines": 1837,
    "tokenized_examples": 1837,
    "filtered_examples": 1812
  },
  "language_distribution": {
    "bengali": 737,
    "english": 1022,
    "mixed": 19
  },
  "splits": {
    "train": 1449,
    "validation": 181,
    "test": 182,
    "total": 1812
  }
}
```

**Data Quality**:
- Random seed: 42 (reproducible)
- Max length: 128 tokens
- Normalization: NFC
- Duplicates removed
- Filtered for quality

**Assessment**: **READY for training** - 1,812 samples with proper train/val/test split.

### B.4 Dataset Comparison

| Dataset | Total Samples | Train | Val | Test | Status |
|---------|---------------|-------|-----|-----|--------|
| Production v1.0 | 24 | 19 | 2 | 3 | ❌ Too small |
| Phase 9.2 Corpus | 1,851 | - | - | - | ⚠️ No split |
| Phase 10 Dataset | 1,812 | 1,449 | 181 | 182 | ✅ Ready |

### B.5 Recommendation

**Use Phase 10 dataset** because:
1. Proper train/validation/test split
2. Tokenized with validated BPE 8K tokenizer
3. Filtered for quality
4. Reproducible (random seed 42)
5. Sufficient size for initial training (1,812 samples)

**Future Enhancement**: After initial model works, expand dataset to 10,000+ samples for better generalization.

---

## C. Model Architecture Investigation

### C.1 SmallTransformer

**Location**: `packages/ai-core/neural/small_transformer.py`

**Verified Architecture**:
- Type: Decoder-only Transformer
- Layers: 4
- Attention heads: 4
- d_model: 128
- d_ff: 512
- max_len: 256
- Dropout: 0.1

**Parameter Count** (estimated):
- Embedding: vocab_size × 128
- Attention: 4 heads × 128²
- FFN: 128 × 512 × 2
- Output: 128 × vocab_size
- **Total**: ~500K parameters

**Status**: Too small for meaningful language understanding.

### C.2 MediumTransformer

**Location**: `packages/ai-core/neural/medium_transformer.py`

**Verified Architecture**:
- Type: Decoder-only Transformer
- Layers: 6
- Attention heads: 8
- d_model: 256
- d_ff: 1024
- max_len: 512
- Dropout: 0.1

**Parameter Count** (calculated):
- Token embedding: 8,000 × 256 = 2,048,000
- Positional encoding: 512 × 256 = 131,072
- 6 Transformer blocks:
  - Attention: 6 × 8 × 256² = 3,145,728
  - FFN: 6 × 256 × 1024 × 2 = 3,145,728
  - LayerNorm: 6 × 2 × 256 × 4 = 12,288
- Output layer: 256 × 8,000 = 2,048,000
- **Total**: ~10.5M parameters

**Status**: Appropriate size for initial training.

### C.3 Phase 10 Experimental Model

**Configuration** (from training log):
```json
{
  "vocab_size": 8000,
  "d_model": 128,
  "nhead": 2,
  "num_layers": 2,
  "dim_feedforward": 512,
  "max_len": 128,
  "num_parameters": 2468928
}
```

**Training Results**:
- Epoch 1: train_loss=7.79, val_loss=7.35
- Epoch 2: train_loss=6.85, val_loss=6.69
- Epoch 3: train_loss=6.04, val_loss=6.01
- Test loss: 6.16
- Perplexity: 474.4

**Generation Quality** (from evaluation):
- English: Poor ("Hello =80 = = = = = + = = = = = =.")
- Bengali: Some coherent but repetitive ("তুমি কেমন ক্ষেত্রে কাজ পছন্দ করো?")

**Assessment**: Model trained but quality poor. Checkpoint not saved to production location.

### C.4 Embedding and Output Layer Compatibility

**Current Issue**:
- SimpleTokenizer has 74 tokens
- BPETokenizer has 8,000 tokens
- Embedding layer dimension: vocab_size × d_model
- Incompatible vocab sizes require reinitialization

**Solution**:
- Reinitialize embedding layer with 8,000-token vocab size
- Reinitialize output layer with 8,000-token vocab size
- Retrain from scratch (no checkpoint transfer possible)

### C.5 Recommendation

**Use MediumTransformer** with:
- Vocab size: 8,000 (matches BPE 8K tokenizer)
- d_model: 256
- n_layers: 6
- n_heads: 8
- d_ff: 1024
- max_len: 512

**Justification**:
- 10.5M parameters appropriate for dataset size
- Larger than Phase 10 experimental model (2.4M params)
- Better capacity for Bengali-English understanding
- Reasonable training time on CPU

---

## D. Hardware and Training Feasibility

### D.1 Verified Hardware

**System Information**:
```
PyTorch version: 2.14.1+cpu
CUDA available: False
CUDA device count: 0
System: Windows
Processor: Intel64 Family 6 Model 60
CPU cores: 4
Total RAM: 7.93 GB
```

**Assessment**: CPU-only training, no GPU available.

### D.2 Memory Requirements

**MediumTransformer with 8K vocab**:
- Model parameters: ~10.5M
- Parameter memory: 10.5M × 4 bytes = ~42 MB
- Batch size 4, max_len 512: 4 × 512 × 4 bytes = ~8 MB
- Optimizer state (AdamW): ~3 × 42 MB = ~126 MB
- Gradients: ~42 MB
- Activations: ~50-100 MB
- **Total**: ~250-300 MB per batch

**RAM Required**: 2-3 GB for training overhead
**Available RAM**: 7.93 GB ✅ Sufficient

### D.3 Training Duration Estimates

**MediumTransformer (10.5M params)**:
- Dataset: 1,812 samples
- Batch size: 4
- Batches per epoch: 1,812 / 4 = 453
- Epochs: 5-10
- Time per batch (CPU estimate): 0.5-1 second
- Time per epoch: 453 × 0.5-1s = 4-8 minutes
- **Total time**: 20-80 minutes (5-10 epochs)

**Phase 10 Experimental Model (2.4M params)**:
- Actual time: 62 + 58 + 57 = 177 seconds (3 epochs)
- Time per epoch: ~59 seconds
- **Total time for 10 epochs**: ~10 minutes

**Estimate**: MediumTransformer training will take **30-60 minutes** on CPU.

### D.4 Storage Requirements

**Checkpoints**:
- Model state: ~42 MB
- Optimizer state: ~126 MB
- Training metadata: ~1 MB
- Tokenizer vocab: ~1 MB
- **Total per checkpoint**: ~170 MB

**Storage Required**: 1-2 GB for multiple checkpoints
**Available**: Sufficient (no storage constraint identified)

### D.5 CPU Fallback

**Feasibility**: ✅ CPU training is feasible
- 4 CPU cores sufficient
- 8 GB RAM sufficient
- Training time acceptable (30-60 minutes)
- No GPU required for initial training

**Optimization**:
- Use smaller batch size if memory issues
- Reduce epochs if overfitting
- Consider mixed precision if CPU supports (unlikely)

### D.6 Recommendation

**Proceed with CPU training**:
- MediumTransformer will train in 30-60 minutes
- No GPU required
- RAM sufficient
- Storage sufficient

**Future Enhancement**: If GPU becomes available, training time can be reduced to 5-10 minutes.

---

## E. Memory Consent and Security

### E.1 Current Memory Pipeline

**Verified Flow**:
1. MemoryService.retrieveMemories() calls MemoryRepository.listApproved()
2. MemoryRepository queries: `WHERE account_id = $1 AND status = 'approved'`
3. No consent_records table check
4. MemoryConsentBoundary interface exists but not implemented

**Issue**: Consent boundary not enforced at runtime.

### E.2 Consent Records Table

**Location**: Database schema `COMPLETE_SCHEMA.sql`

**Verified Schema**:
```sql
CREATE TABLE nexus.consent_records (
    id uuid PRIMARY KEY,
    account_id uuid NOT NULL,
    consent_type text NOT NULL,
    policy_version varchar(80) NOT NULL,
    decision text NOT NULL, -- 'granted', 'denied', 'revoked', 'superseded'
    captured_at timestamptz NOT NULL,
    revoked_at timestamptz,
    capture_source varchar(40) NOT NULL
);
```

**Foreign Key**: memory_records.consent_record_id references consent_records.id

### E.3 Consent Enforcement Gap

**Missing Components**:
1. No ConsentRecordRepository to query consent_records
2. No implementation of MemoryConsentBoundary.isMemoryEnabled()
3. MemoryService does not check consent before retrieval
4. proposeMemory() does not check consent before saving

### E.4 Implementation Plan (Deferred to After Foundation)

**Required Changes**:
1. Create ConsentRecordRepository
2. Implement MemoryConsentBoundary class
3. Update MemoryService.retrieveMemories() to check consent
4. Update MemoryService.proposeMemory() to check consent
5. Test with different consent states

**Status**: **DEFERRED** - Not part of Phase 1 foundation repair.

---

## F. Phase 1 Proposed Repair Design

### F.1 Dependency Order

```
1. Validate BPETokenizer ✅ DONE (Phase 9.3)
2. Validate Dataset ✅ DONE (Phase 10)
3. Update ML Service to use BPETokenizer ⬅️ NEXT
4. Train MediumTransformer with BPE 8K ⬅️ NEXT
5. Save checkpoint to production location ⬅️ NEXT
6. Update production designation ⬅️ NEXT
7. Verify inference ⬅️ NEXT
8. Implement consent enforcement ⬅️ DEFERRED
```

### F.2 Step-by-Step Implementation Plan

#### Step 1: Update ML Service to Use BPETokenizer

**File**: `packages/ai-core/ml-service/main.py`

**Changes Required**:
```python
# OLD (line 51)
from tokenizer.tokenizer import SimpleTokenizer

# NEW
from tokenizer.bpe_tokenizer import BPETokenizer

# OLD (lines 287-300)
tokenizer = SimpleTokenizer(vocab_size=vocab_size)
tokenizer.word_to_id = {...}
tokenizer.is_built = True

# NEW
tokenizer = BPETokenizer(vocab_size=8000)
tokenizer.load("packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k")
```

**Risk**: Medium - Breaking change for tokenizer compatibility
**Mitigation**: Backup existing code, test with BPETokenizer first

#### Step 2: Create Training Script

**File**: `packages/ai-core/training/train_phase1_medium.py` (new)

**Requirements**:
- Load BPETokenizer from Phase 9.2
- Load Phase 10 dataset
- Initialize MediumTransformer with 8K vocab
- Train for 5-10 epochs
- Save checkpoint with tokenizer_vocab
- Save to production location: `models/checkpoints_medium/final_model.pt`

**Configuration**:
```python
model = MediumTransformer(
    vocab_size=8000,
    d_model=256,
    n_layers=6,
    n_heads=8,
    d_ff=1024,
    max_len=512
)
```

#### Step 3: Train Model

**Script**: `train_phase1_medium.py`

**Expected Duration**: 30-60 minutes on CPU

**Validation Criteria**:
- Training loss decreases
- Validation loss decreases
- No overfitting (val loss not much higher than train loss)
- Perplexity improves
- Generation quality better than random

#### Step 4: Save Checkpoint to Production Location

**Create Directory**: `packages/ai-core/models/checkpoints_medium/`

**Save Checkpoint**:
```python
checkpoint = {
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "epoch": epoch,
    "val_loss": val_loss,
    "tokenizer_vocab": tokenizer.vocab,
    "config": training_config
}
torch.save(checkpoint, "models/checkpoints_medium/final_model.pt")
```

#### Step 5: Update Production Designation

**File**: `packages/ai-core/models/production/current.json` (new)

**Content**:
```json
{
  "model_name": "MediumTransformer",
  "model_version": "1.0.0",
  "tokenizer_name": "BPETokenizer",
  "tokenizer_version": "1.1.0",
  "tokenizer_path": "data/experimental/phase9_2/tokenizers/bpe_8k",
  "vocab_size": 8000,
  "checkpoint_path": "checkpoints_medium/final_model.pt",
  "trained_at": "2026-11-05",
  "dataset": "Phase 10",
  "dataset_samples": 1812
}
```

#### Step 6: Verify ML Service Loads Checkpoint

**Test**: Start ML service and verify:
- Checkpoint loads successfully
- BPETokenizer loads successfully
- Inference produces coherent text
- Bengali tokenization works
- Memory formatting works

#### Step 7: Runtime Verification

**Test Scenarios**:
1. Bengali input → Bengali response
2. English input → English response
3. Memory retrieval → Memory in prompt
4. Conversation history → History in prompt
5. Context awareness → Follow-up questions

---

## G. Risk Analysis

### G.1 High Risk

**Risk 1: Training Failure**
- Model may not converge
- Loss may not decrease
- Generation may be poor

**Mitigation**:
- Start with 5 epochs
- Monitor loss closely
- Try different learning rates if needed
- Reduce model size if needed

**Risk 2: Checkpoint Incompatibility**
- Old code may expect 74-token vocab
- ML service may fail to load checkpoint

**Mitigation**:
- Update ML service before training
- Test checkpoint loading
- Have rollback procedure

### G.2 Medium Risk

**Risk 3: Data Quality Issues**
- Phase 10 dataset may have noise
- Bengali text may have encoding issues

**Mitigation**:
- Validate dataset before training
- Use NFC normalization
- Monitor training for anomalies

**Risk 4: Training Time Exceeded**
- CPU training may take longer than estimated

**Mitigation**:
- Use smaller batch size
- Reduce epochs
- Consider subset of data for testing

### G.3 Low Risk

**Risk 5: Storage Issues**
- Checkpoint may be larger than expected

**Mitigation**:
- Monitor storage usage
- Clean old artifacts if needed

---

## H. Migration Strategy

### H.1 Backup Plan

**Before Changes**:
1. Archive `packages/ai-core/ml-service/main.py`
2. Archive `packages/ai-core/tokenizer/tokenizer.py`
3. Archive production dataset v1.0
4. Document current configuration

### H.2 Rollback Procedure

**If training fails**:
1. Restore archived ML service code
2. Restore SimpleTokenizer usage
3. Continue with current system (random weights)

**If ML service fails to load**:
1. Use old checkpoint (if exists)
2. Fallback to random initialization
3. Debug BPETokenizer loading

### H.3 Rollout Strategy

**Phased Rollout**:
1. Update ML service code only (no training yet)
2. Test BPETokenizer loading
3. Train model in experimental directory
4. Test inference with new model
5. Only then move to production location
6. Update production designation

---

## I. Acceptance Criteria

### I.1 Tokenizer Criteria

- ✅ BPETokenizer loads successfully
- ✅ Bengali text tokenizes with 0% UNK
- ✅ English text tokenizes with 0% UNK
- ✅ Round-trip accuracy 100%
- ✅ No crash on mixed language

### I.2 Model Training Criteria

- ✅ Training loss decreases
- ✅ Validation loss decreases
- ✅ No overfitting (val loss within 20% of train loss)
- ✅ Perplexity < 100 (target)
- ✅ Checkpoint saves successfully
- ✅ Checkpoint loads successfully

### I.3 Inference Criteria

- ✅ Bengali input produces Bengali response
- ✅ English input produces English response
- ✅ Response is coherent (not random)
- ✅ Response is relevant to input
- ✅ No crash on any input

### I.4 Integration Criteria

- ✅ ML service starts without errors
- ✅ API continues to work
- ✅ Frontend continues to work
- ✅ Memory retrieval works
- ✅ Conversation history works
- ✅ No regression in existing features

---

## J. Resource Requirements

### J.1 Compute

- **CPU**: 4 cores (available)
- **RAM**: 2-3 GB required (8 GB available)
- **GPU**: Not required (none available)
- **Time**: 30-60 minutes for training

### J.2 Storage

- **Checkpoint**: ~170 MB
- **Tokenizer**: ~1 MB
- **Dataset**: ~10 MB
- **Logs**: ~5 MB
- **Total**: ~200 MB

### J.3 Human

- **Implementation**: 2-3 hours (coding, testing)
- **Training**: 30-60 minutes (automated)
- **Verification**: 1-2 hours (testing, documentation)
- **Total**: 4-6 hours

---

## K. Estimated Timeline

### Phase 1.1: Preparation (30 minutes)
- Backup existing code
- Create training script
- Set up directories

### Phase 1.2: Code Updates (1 hour)
- Update ML service to use BPETokenizer
- Test BPETokenizer loading
- Verify dataset loading

### Phase 1.3: Training (30-60 minutes)
- Run training script
- Monitor loss
- Save checkpoint

### Phase 1.4: Integration (30 minutes)
- Move checkpoint to production location
- Update production designation
- Test ML service loading

### Phase 1.5: Verification (1-2 hours)
- Test inference
- Test Bengali and English
- Test memory and context
- Document results

**Total Time**: 4-6 hours

---

## L. Unresolved Questions

### L.1 Model Quality

**Question**: Will MediumTransformer (10.5M params) on 1,812 samples produce coherent text?

**Uncertainty**: Moderate
- Phase 10 model (2.4M params) on same dataset produced poor results
- Larger model may help but dataset is still small
- May need more data for good quality

**Investigation**: Train and evaluate actual generation quality.

### L.2 Dataset Size

**Question**: Is 1,812 samples sufficient for meaningful training?

**Uncertainty**: High
- Most language models trained on millions of samples
- 1,812 samples may be insufficient for generalization
- May overfit to training data

**Investigation**: Monitor train/validation loss gap. If large gap, need more data.

### L.3 Bengali Understanding

**Question**: Will model understand Bengali semantics or just token patterns?

**Uncertainty**: High
- Tokenizer handles Bengali correctly
- But model may not learn Bengali semantics from 737 samples
- May produce Bengali-looking but meaningless text

**Investigation**: Evaluate Bengali generation quality carefully.

---

## M. Findings vs Previous Audit

### M.1 Corrections to Previous Audit

**Previous Claim**: "No BPETokenizer trained on actual corpus"
**Correction**: ✅ Phase 9.2 BPE 8K tokenizer fully trained and validated on Phase 9.2 corpus

**Previous Claim**: "No trained model checkpoints"
**Correction**: ⚠️ Phase 10 training completed but checkpoint not saved to production location. Experimental training logs exist showing training occurred.

**Previous Claim**: "Dataset only 24 samples"
**Correction**: ✅ Production dataset is 24 samples, but Phase 10 dataset has 1,812 samples ready for training.

### M.2 Confirmed Findings

✅ No production checkpoint in expected location
✅ SimpleTokenizer has 74 tokens (confirmed)
✅ Consent enforcement not implemented
✅ No GPU available
✅ CPU training feasible

---

## N. Final Recommendation

### N.1 Proceed with Phase 1 Foundation Repair

**Authorization Requested**:
1. Update ML service to use Phase 9.2 BPE 8K tokenizer
2. Train MediumTransformer (10.5M params) on Phase 10 dataset (1,812 samples)
3. Save checkpoint to production location
4. Update production designation
5. Verify inference quality

**Rationale**:
- BPETokenizer fully validated (0% UNK, 100% round-trip)
- Dataset ready (1,812 samples with proper split)
- Model architecture sound (MediumTransformer)
- Training feasible on CPU (30-60 minutes)
- No external dependencies required

### N.2 Deferred to Later Phase

- Memory consent enforcement (Phase 2)
- Dataset expansion to 10,000+ samples (Phase 2)
- GPU training optimization (Phase 2)
- Knowledge engine (Phase 4 - blocked until foundation fixed)
- Safety validation (Phase 5 - blocked until foundation fixed)

### N.3 Success Criteria

**Minimum Success**:
- Checkpoint saves and loads
- Inference produces coherent text (better than random)
- Bengali and English both work
- No regression in existing features

**Ideal Success**:
- Perplexity < 100
- Bengali generation meaningful
- English generation meaningful
- Memory and context utilized effectively

---

## O. Files Changed in This Plan

**No files changed** - This is a planning document only.

**Files to be changed after authorization**:
1. `packages/ai-core/ml-service/main.py` (update tokenizer)
2. `packages/ai-core/training/train_phase1_medium.py` (new)
3. `packages/ai-core/models/production/current.json` (new)
4. `packages/ai-core/models/checkpoints_medium/final_model.pt` (new, from training)

---

## P. Build/Test Results

**No builds or tests run** - This is a planning document only.

**After authorization**, will run:
- API build test
- ML service start test
- BPETokenizer loading test
- Training script test
- Inference test

---

## Q. Production Behavior Changes

**No production behavior changed** - This is a planning document only.

**After authorization**, production behavior will change:
- ML service will use BPETokenizer instead of SimpleTokenizer
- ML service will load trained checkpoint instead of random weights
- Inference quality should improve (if training successful)

---

## STOP

**Phase 1 Foundation Repair Readiness Investigation Complete.**

**Documents Created**:
1. This plan: `docs/implementation/PHASE_1_FOUNDATION_REPAIR_PLAN.md`

**Awaiting Founder Authorization** to proceed with:
- BPETokenizer integration
- MediumTransformer training
- Production checkpoint deployment

**Do Not Proceed** with implementation until explicitly authorized.
