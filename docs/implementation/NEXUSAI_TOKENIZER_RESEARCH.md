# NexusAI Tokenizer Research and Repair Plan

**Date**: 2026-11-05
**Type**: Tokenizer Foundation Repair
**Priority**: CRITICAL

---

## Executive Summary

**Current Problem**: Production SimpleTokenizer has only 74 tokens, causing 60-80% UNK rate and no Bengali support.

**Solution**: Switch to BPETokenizer with 2000-5000 token vocabulary trained on Phase9_3 corpus.

**Status**: BPETokenizer already implemented, just needs integration into production.

---

## Current Tokenizer Analysis

### SimpleTokenizer (Production)

**Location**: `packages/ai-core/tokenizer/tokenizer.py`

**Implementation Details**:
- Type: Word-level tokenizer
- Tokenization method: `text.lower().split()`
- Special tokens: PAD, UNK, BOS, EOS
- Vocabulary size: Configurable (default 5000)
- Actual production vocab: 74 tokens

**Tokenization Process**:
```python
def _tokenize_text(self, text: str) -> List[str]:
    words = text.lower().split()
    return words
```

**Issues**:
1. Whitespace-only splitting loses punctuation
2. Case folding loses proper nouns
3. No subword representation
4. Bengali characters treated as separate words
5. Numbers split incorrectly
6. Unknown words become UNK

**Example Analysis**:
```
Input: "My name is Rahim. I wake up at 7 AM."
Tokens: ["my", "name", "is", "rahim.", "i", "wake", "up", "at", "7", "am."]
Issues:
- "rahim." includes period (should be separate)
- "7" and "am." not recognized
- Many become UNK with 74-token vocab
```

### BPETokenizer (Experimental)

**Location**: `packages/ai-core/tokenizer/bpe_tokenizer.py`

**Implementation Details**:
- Type: Byte-Pair Encoding (subword)
- Tokenization method: Character-level → iterative merging
- Special tokens: PAD, UNK, BOS, EOS, USER, ASSISTANT, SEP
- Vocabulary size: Configurable (default 32000)
- Unicode-aware: Supports Bengali and English
- Whitespace preservation: Fixed in v1.1.0

**BPE Training Process**:
```python
def train(self, texts: List[str]):
    # 1. Initialize with characters
    # 2. Count word frequencies
    # 3. Iteratively merge most frequent pairs
    # 4. Build vocabulary up to target size
```

**Advantages**:
1. Subword representation handles unknown words
2. Bengali characters properly tokenized
3. Numbers and punctuation preserved
4. Smaller vocabulary needed for good coverage
5. Morphological patterns captured

**Example Tokenization**:
```
Input: "My name is Rahim. I wake up at 7 AM."
Subwords: ["My", " name", " is", " Ra", "him", ".", " I", " wake", " up", " at", " 7", " AM", "."]
Advantage: Even unseen words broken into known subwords
```

---

## Tokenizer Evaluation Plan

### Test Dataset

Create comprehensive test suite with:

**Bengali Sentences**:
- "আমার নাম রহিম।" (My name is Rahim)
- "আমি সকাল ৭টায় ঘুম থেকে জাগি।" (I wake up at 7 AM)
- "বাংলাদেশ দক্ষিণ এশিয়ায় অবস্থিত।" (Bangladesh is located in South Asia)

**English Sentences**:
- "My name is Rahim and I live in Bangladesh."
- "I prefer waking up at 7 AM every morning."
- "The capital of Bangladesh is Dhaka."

**Mixed Bengali-English**:
- "My name রহিম. I live in Dhaka."
- "আমি software engineer হিসেবে কাজ করি।"

**Names and Numbers**:
- "Rahim", "Karim", "Hasibul"
- "7", "30", "2025"
- "7:30 AM", "January 15, 2025"

**Personal Memories**:
- "I prefer waking up at 7 AM"
- "My favorite color is blue"
- "I work as a software engineer"

**Longer Paragraphs**:
- Multi-sentence text
- Memory-like content
- Conversation-like content

### Evaluation Metrics

1. **UNK Percentage**:
   - Lower is better
   - Target: < 5% for English, < 10% for Bengali

2. **Token Coverage**:
   - Percentage of test texts fully represented
   - Target: > 95%

3. **Average Sequence Length**:
   - Tokens per character ratio
   - Target: 0.5-1.5 (reasonable compression)

4. **Text Reconstruction**:
   - Encode → decode round-trip accuracy
   - Target: > 99% character-level accuracy

5. **Truncation Rate**:
   - Percentage of texts exceeding max_len
   - Target: < 10% at max_len=512

---

## Proposed Tokenizer Experiments

### Experiment 1: Vocabulary Size Comparison

**Hypothesis**: Larger vocabulary reduces UNK rate but increases memory.

**Variants**:
- BPETokenizer with 1000 tokens
- BPETokenizer with 2000 tokens
- BPETokenizer with 5000 tokens
- BPETokenizer with 10000 tokens

**Dataset**: Phase9_3 curated corpus

**Metrics**: UNK rate, token coverage, average sequence length

**Expected Result**: 2000-5000 tokens optimal for current dataset size

### Experiment 2: Special Token Analysis

**Hypothesis**: Additional special tokens improve conversation handling.

**Variants**:
- Base: PAD, UNK, BOS, EOS
- + USER, ASSISTANT
- + SEP (separator)
- + MEM (memory marker)

**Dataset**: Conversation history samples

**Metrics**: Conversation formatting quality, reconstruction accuracy

**Expected Result**: USER/ASSISTANT tokens helpful for chat context

### Experiment 3: Normalization Strategy

**Hypothesis**: Proper Unicode normalization improves Bengali handling.

**Variants**:
- No normalization
- NFC normalization
- NFD normalization
- Custom Bengali normalization

**Dataset**: Bengali text samples

**Metrics**: UNK rate for Bengali, reconstruction accuracy

**Expected Result**: NFD normalization best for Bengali

---

## Implementation Plan

### Step 1: Train BPETokenizer

**Script**: `packages/ai-core/tokenizer/train_bpe_tokenizer.py`

**Requirements**:
- Load Phase9_3 corpus
- Set vocabulary size: 2000 (start), 5000 (target)
- Train BPETokenizer
- Save with metadata
- Save special token IDs

**Output**:
- `models/tokenizers/bpe_tokenizer/vocab.json`
- `models/tokenizers/bpe_tokenizer/merges.json`
- `models/tokenizers/bpe_tokenizer/metadata.json`

### Step 2: Update ML Service

**File**: `packages/ai-core/ml-service/main.py`

**Changes**:
```python
# OLD
from tokenizer.tokenizer import SimpleTokenizer
tokenizer = SimpleTokenizer(vocab_size=vocab_size)

# NEW
from tokenizer.bpe_tokenizer import BPETokenizer
tokenizer = BPETokenizer(vocab_size=5000)
tokenizer.load("models/tokenizers/bpe_tokenizer")
```

**Checkpoint Compatibility**:
- Checkpoint embedding layer must match new vocab size
- Retrain model with new tokenizer
- Save new checkpoint with tokenizer_vocab

### Step 3: Retrain Model

**Script**: `packages/ai-core/training/run_training.py`

**Configuration**:
- Model: MediumTransformer
- Tokenizer: BPETokenizer (5000 tokens)
- Dataset: Phase9_3 corpus
- Epochs: 5-10
- Batch size: 8
- Learning rate: 0.001

**Output**:
- `models/checkpoints_medium/final_model.pt`
- Includes tokenizer_vocab in checkpoint

### Step 4: Update Production Designation

**File**: `models/production/current.json`

**Content**:
```json
{
  "model_name": "MediumTransformer",
  "model_version": "1.0.0",
  "tokenizer_name": "BPETokenizer",
  "tokenizer_version": "1.1.0",
  "vocab_size": 5000,
  "checkpoint_path": "checkpoints_medium/final_model.pt",
  "trained_at": "2026-11-05"
}
```

### Step 5: Verification

**Tests**:
1. Load checkpoint successfully
2. Tokenize Bengali text with < 10% UNK
3. Tokenize English text with < 5% UNK
4. Encode/decode round-trip accuracy > 99%
5. Inference produces coherent text

---

## Compatibility Analysis

### Embedding Layer

**Current**: SmallTransformer embedding expects vocab_size
**New**: BPETokenizer has different vocab_size

**Solution**:
- Reinitialize embedding layer with new vocab_size
- Retrain from scratch (no checkpoint transfer possible)
- Or: Map old vocab to new vocab (complex, not recommended)

**Recommendation**: Retrain from scratch with new tokenizer.

### Output Layer

**Current**: Output layer projects to vocab_size
**New**: Must project to new vocab_size

**Solution**: Same as embedding layer - retrain.

### Checkpoint Compatibility

**Old Checkpoints**: Incompatible with new tokenizer
**New Checkpoints**: Will include tokenizer_vocab for future compatibility

**Recommendation**: Archive old checkpoints (if any found) and start fresh.

---

## Migration Strategy

### Phase 1: Preparation (1-2 hours)

1. Backup existing tokenizer files
2. Backup existing dataset
3. Archive any experimental checkpoints
4. Prepare Phase9_3 corpus for training

### Phase 2: Tokenizer Training (10-30 minutes)

1. Train BPETokenizer on Phase9_3 corpus
2. Evaluate with test suite
3. Adjust vocabulary size if needed
4. Save final tokenizer

### Phase 3: Model Training (2-4 hours CPU, 30-60 min GPU)

1. Initialize MediumTransformer with new vocab_size
2. Train on Phase9_3 dataset
3. Monitor validation loss
4. Save final checkpoint with tokenizer_vocab

### Phase 4: Integration (30 minutes)

1. Update ML service to use BPETokenizer
2. Update production designation
3. Test checkpoint loading
4. Test inference with Bengali and English

### Phase 5: Verification (1 hour)

1. Run tokenizer evaluation suite
2. Test inference with various inputs
3. Verify memory formatting
4. Verify conversation history formatting
5. Document results

---

## Risk Assessment

### Low Risk

- BPETokenizer already implemented and tested
- Training pipeline already exists
- Dataset collection already done

### Medium Risk

- Training time may be long without GPU
- Vocabulary size may need adjustment
- Model may not converge with new tokenizer

### High Risk

- **Breaking change**: Old checkpoints incompatible
- **Retraining required**: No existing intelligence preserved
- **Uncertain quality**: New model may not perform well

**Mitigation**:
- Archive all existing artifacts before changes
- Train with careful hyperparameter tuning
- Have fallback to SimpleTokenizer if needed
- Document rollback procedure

---

## Success Criteria

### Tokenizer Metrics

- ✅ Bengali UNK rate < 10%
- ✅ English UNK rate < 5%
- ✅ Reconstruction accuracy > 99%
- ✅ No crash on Bengali text
- ✅ No crash on mixed language

### Model Metrics

- ✅ Training loss decreases
- ✅ Validation loss decreases
- ✅ No overfitting (val loss > train loss)
- ✅ Inference produces coherent text
- ✅ Model responds to Bengali input

### Integration Metrics

- ✅ ML service loads new tokenizer
- ✅ ML service loads new checkpoint
- ✅ API continues to work
- ✅ Frontend continues to work
- ✅ No regression in existing features

---

## Fallback Plan

If BPETokenizer training fails:
1. Fall back to improved SimpleTokenizer with larger vocab
2. Keep word-level but increase to 2000 tokens
3. Add Bengali-specific preprocessing
4. Train model with improved tokenizer

If model training fails:
1. Reduce model size (use SmallTransformer)
2. Reduce dataset size
3. Increase training epochs
4. Try different hyperparameters

If integration fails:
1. Keep SimpleTokenizer for production
2. Use BPETokenizer for experimental branch
3. Gradual migration
4. A/B testing

---

## Timeline Estimate

**Total Time**: 4-8 hours (with GPU), 8-16 hours (CPU only)

**Breakdown**:
- Preparation: 1-2 hours
- Tokenizer training: 10-30 minutes
- Model training: 2-4 hours (GPU) or 8-12 hours (CPU)
- Integration: 30 minutes
- Verification: 1 hour

---

## Conclusion

**Recommendation**: Switch to BPETokenizer with 5000-token vocabulary.

**Reasoning**:
- BPETokenizer already implemented
- Solves 74-token vocabulary limitation
- Enables Bengali support
- Subword representation robust to unknown words
- Training pipeline ready

**Next Steps**:
1. Train BPETokenizer on Phase9_3 corpus
2. Train MediumTransformer with new tokenizer
3. Update production ML service
4. Verify and document results

**Do Not**:
- Keep SimpleTokenizer with 74 tokens
- Train model with current tokenizer
- Add features without fixing tokenizer first

---

**END OF TOKENIZER RESEARCH**
