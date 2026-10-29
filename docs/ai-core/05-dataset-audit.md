# Dataset Audit

**Last Updated**: 2026-10-26 (Phase 2 Forensic Audit)  
**Verification Status**: VERIFIED from file inspection and Python commands

---

## Overview

This document provides an inventory of all training datasets in the AI Core, including sample counts, language distribution, quality assessment, and vocabulary analysis.

## Dataset Inventory

### Dataset 1: train_cleaned.json

**Location**: `packages/ai-core/data/public_datasets/v1.0_cleaned/train_cleaned.json`

**Purpose**: Training dataset for MediumTransformer

**Format**: Array of strings (simple text)

**Sample Count**: 19 samples (VERIFIED)

**Format**: JSON array

**Sample Content**:
```json
[
  "ঢাকা কী?",
  "আমার নাম NexusAI।",
  "কেমন আছ?",
  "I can have conversations, answer questions, and assist you with various tasks.",
  "You're welcome! Is there anything else I can help you with?",
  "What is the capital of Bangladesh?",
  "বাংলাদেশ কোথায়?",
  "বাংলায় কথা বলতে পারো?",
  "আমি তোমার সঙ্গে কথোপকথন করতে পারি, প্রশ্নের উত্তর দিতে পারি এবং সাহায্য করতে পারি।",
  "ঢাকা বাংলাদেশের রাজধানী।",
  "বাংলাদেশ দক্ষিণ এশিয়ায় অবস্থিত।",
  "ধন্যবাদ",
  "My name is NexusAI.",
  "আমি সময়সূচী সম্পর্কে সাহায্য করতে পারি।",
  "তুমি কী করতে পারো?",
  "What is your name?",
  "তোমার নাম কি?",
  "হ্যাঁ, আমি বাংলায় কথা বলতে পারি।",
  "The capital of Bangladesh is Dhaka."
]
```

**Language Distribution**:
- Bengali: ~10 samples
- English: ~6 samples
- Mixed: ~3 samples

**Usage**: Configured in `train_medium_model.py` as training dataset

**Training Split** (19 samples):
- Train: 15 samples (80%)
- Validation: 2 samples (10%)
- Test: 2 samples (10%)

**Quality Assessment**: CRITICALLY SMALL — 19 samples is insufficient for training a language model

---

### Dataset 2: train_v2.json

**Location**: `packages/ai-core/data/train_v2.json`

**Purpose**: Conversation dataset used for tokenizer rebuilding in ML service

**Format**: Array of conversation objects

**Sample Count**: 502 samples (VERIFIED)

**Format**: JSON array with messages

**Sample Content**:
```json
[
  {
    "messages": [
      {
        "role": "user",
        "content": "Hello"
      },
      {
        "role": "assistant",
        "content": "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?"
      }
    ]
  },
  {
    "messages": [
      {
        "role": "user",
        "content": "Hi there"
      },
      {
        "role": "assistant",
        "content": "Hi! How can I assist you today?"
      }
    ]
  }
]
```

**Usage**: Used by ML service to rebuild tokenizer vocabulary at runtime (line 233 in `main.py`)

**Vocabulary Analysis** (VERIFIED from Python command):
- Total messages: 1004 (502 conversations × 2 messages average)
- Unique words: 3,463 words
- Potential vocabulary size: 3,463+ tokens (much larger than current 74)

**Quality Assessment** (Phase 3 Audit):
- Empty messages: 0 (VERIFIED)
- Duplicate conversations: 0 (VERIFIED)
- Malformed conversations: 0 (VERIFIED)
- Role distribution: 502 user, 502 assistant (VERIFIED)
- Bengali messages: 41/1004 (4.1%) (VERIFIED)
- Message length: Mean 62 chars, Median 34 chars (VERIFIED)
- Bengali examples: "হ্যালো", "আসসালামু আলাইকুম", "তোমার নাম কী?" (VERIFIED)
- Top 10 words (when capped at 74): is, a, what, the, of, or, and, to, in, that (VERIFIED)
- **CRITICAL**: When tokenizer is capped at 74 tokens (matching checkpoint), Bengali words are NOT included (only top English words)

**Quality Assessment**: BETTER than train_cleaned.json - contains conversational structure and larger vocabulary, but Bengali content is minority (4.1%)

**Training Usage**: NOT currently used for training (only for tokenizer rebuilding)

**Training Script Alternative**: `train_with_v2.py` exists to train on this dataset but has not been executed

---

### Dataset 3: public_datasets/v1.0/train.json

**Location**: `packages/ai-core/data/public_datasets/v1.0/train.json`

**Purpose**: Original training dataset (same as v1.0_cleaned)

**Sample Count**: 19 samples (VERIFIED)

**Format**: JSON array of strings

**Sample Content**: Identical to train_cleaned.json

**Usage**: Source for v1.0_cleaned dataset

**Status**: VERIFIED - Same 19 samples as train_cleaned.json

---

### Dataset 4: public_datasets/v1.0/validation.json

**Location**: `packages/ai-core/data/public_datasets/v1.0/validation.json`

**Purpose**: Validation dataset (original split)

**Sample Count**: 2 samples (VERIFIED)

**Format**: JSON array of strings

**Usage**: Not currently used by training script

**Status**: VERIFIED but UNUSED

---

### Dataset 5: public_datasets/v1.0/test.json

**Location**: `packages/ai-core/data/public_datasets/v1.0/test.json`

**Purpose**: Test dataset (original split)

**Sample Count**: 3 samples (VERIFIED)

**Format**: JSON array of strings

**Usage**: Not currently used by training script

**Status**: VERIFIED but UNUSED

---

### Dataset 6: conversational_data.json

**Location**: `packages/ai-core/data/conversational_data.json`

**Purpose**: Conversational data (usage unknown)

**Sample Count**: 28 samples (VERIFIED)

**Format**: UNKNOWN (not inspected in detail)

**Usage**: UNKNOWN (not referenced in training script)

**Status**: VERIFIED count, format not inspected

---

### Dataset 7: merged_train.json

**Location**: `packages/ai-core/data/merged_train.json`

**Purpose**: Merged training data

**Sample Count**: 167 samples (VERIFIED)

**Format**: Mixed format - strings and question/answer objects

**Sample Structure**:
- Lines 1-129: Simple strings (similar to synthetic data)
- Lines 130+: Question/answer objects

**Usage**: UNKNOWN (not referenced in training script)

**Status**: VERIFIED count, mixed format

---

### Dataset 8: train_final.json

**Location**: `packages/ai-core/data/train_final.json`

**Purpose**: Final training dataset

**Sample Count**: 223 samples (VERIFIED)

**Format**: Mixed format - strings and question/answer objects

**Sample Structure**:
- Lines 1-129: Simple strings (similar to synthetic data)
- Lines 130+: Question/answer objects

**Usage**: UNKNOWN (not referenced in training script)

**Status**: VERIFIED count, mixed format

---

### Dataset 9: synthetic/train.json

**Location**: `packages/ai-core/data/synthetic/train.json`

**Purpose**: Synthetic training data

**Sample Count**: 148 samples (VERIFIED)

**Format**: JSON array of simple English sentences

**Sample Content**: General knowledge sentences (e.g., "The sky is blue today.", "Water boils at 100 degrees Celsius.")

**Usage**: UNKNOWN (not referenced in training script)

**Status**: VERIFIED count, simple English sentences

---

### Dataset 10: public_datasets/v1.0_cleaned/conversational_pairs.json

**Location**: `packages/ai-core/data/public_datasets/v1.0_cleaned/conversational_pairs.json`

**Purpose**: Conversational pairs dataset

**Sample Count**: 17 samples (VERIFIED)

**Format**: UNKNOWN (not inspected in detail)

**Usage**: UNKNOWN (not referenced in training script)

**Status**: VERIFIED count, format not inspected

---

## Vocabulary Analysis

### train_cleaned.json Vocabulary

**Unique Words**: 70 unique words (VERIFIED)

**Total Tokens**: 74 tokens (70 unique + 4 special tokens)

**Sample Vocabulary** (first 20):
```
<PAD>, <UNK>, <BOS>, <EOS>, is, করতে, আমি, পারি।, ঢাকা, নাম, i, can, you, what, the, capital, of, বাংলাদেশ, বাংলায়, কথা, বলতে
```

**Characteristics**:
- Mix of English and Bengali words
- Many words include punctuation attached (e.g., "পারি।", "tasks.")
- Extremely limited for a language model

### Saved Tokenizer Vocabulary

**File**: `tokenizer/multilingual_tokenizer.json`

**Vocabulary Size**: 74 tokens (VERIFIED)

**Source**: Built from train_cleaned.json

**Matches Dataset**: YES (74 tokens matches dataset analysis)

### Expected vs Actual Vocabulary

**Training Script Configuration**: vocab_size=2000 (line 82 in `train_medium_model.py`)

**Actual Vocabulary**: 74 tokens

**Mismatch Reason**: Insufficient training data cannot support 2000 tokens

**Impact**: Model severely limited by small vocabulary

---

## Language Distribution

### train_cleaned.json

**Bengali Samples**: ~10 (52%)
- Examples: "ঢাকা কী?", "আমার নাম NexusAI।", "কেমন আছ?"

**English Samples**: ~6 (32%)
- Examples: "I can have conversations...", "What is the capital of Bangladesh?"

**Mixed Samples**: ~3 (16%)
- Examples: Bengali sentences with English words

**Assessment**: Reasonable language balance, but total count is too small

---

## Dataset Quality Assessment

### Data Quality Issues

#### Issue 1: Insufficient Sample Count

**Dataset**: train_cleaned.json

**Problem**: Only 19 samples

**Impact**: 
- Cannot support 2000-token vocabulary
- Model severely undertrained
- Output quality is incoherent

**Status**: VERIFIED CRITICAL ISSUE

#### Issue 2: Limited Diversity

**Dataset**: train_cleaned.json

**Problem**: Very limited topic diversity

**Topics Covered**:
- Greetings
- Identity
- Capabilities
- Location (Dhaka, Bangladesh)
- Thanks

**Missing Topics**:
- General knowledge
- Science
- History
- Complex reasoning
- Multi-turn conversations

**Status**: VERIFIED QUALITY ISSUE

#### Issue 3: Simple Format

**Dataset**: train_cleaned.json

**Problem**: Simple string format, not conversational

**Impact**: Model may not learn conversation structure

**Status**: VERIFIED FORMAT ISSUE

#### Issue 4: Punctuation Attached to Words

**Dataset**: train_cleaned.json

**Problem**: Words include punctuation (e.g., "পারি।", "tasks.")

**Impact**: Tokenizer treats "পারি" and "পারি।" as different tokens

**Status**: VERIFIED TOKENIZATION ISSUE

---

## Duplicate Detection

### train_cleaned.json

**Status**: NOT VERIFIED (duplicate detection not performed)

**Need**: Manual or automated duplicate analysis

**Potential Issue**: Small dataset may have duplicate entries

---

## Data Preprocessing

### Current Preprocessing

**Training Script**: `train_medium_model.py`

**Preprocessing Steps**:
1. Load JSON file
2. Extract text strings
3. Build vocabulary with min_freq=1
4. Tokenize with whitespace splitting
5. Create input/target pairs (shifted by 1)
6. Pad/truncate to max_len=128

**No Filtering**: No explicit filtering of duplicates, malformed data, or quality checks

**Status**: SOURCE-INSPECTED

---

## Training Data vs Inference Data

### Discrepancy

**Training Data**: train_cleaned.json (19 samples)

**Inference Tokenizer Data**: train_v2.json (502 samples)

**Impact**: Tokenizer at inference is rebuilt from different dataset than training

**Compatibility**: Potentially incompatible if train_v2.json contains words not in training vocabulary

**Status**: VERIFIED INCONSISTENCY

**Recommendation**: Use same dataset for training and inference tokenizer

---

## Unknowns

### Dataset Origin

❓ **Question**: Why does train_cleaned.json have only 19 samples?

**Evidence**: Insufficient data for conclusion

**Possible Explanations**:
- Intentional minimal dataset for testing
- Data collection incomplete
- Data file truncated accidentally
- Placeholder dataset

❓ **Question**: What is the source of train_cleaned.json?

**Evidence**: No documentation found

**Status**: UNKNOWN

❓ **Question**: Are the other datasets (train_v2.json, etc.) higher quality?

**Evidence**: Not inspected

**Status**: UNKNOWN

❓ **Question**: Why is train_v2.json not used for training?

**Evidence**: Training script explicitly uses train_cleaned.json

**Status**: UNKNOWN

---

## Phase 3 Training Readiness Findings

### train_v2.json Split Analysis (VERIFIED)

**Split Method**: Simple sequential split (lines 109-115 in `train_with_v2.py`)

**Split Distribution**:
- Train: 401 conversations (80%)
- Validation: 50 conversations (10%)
- Test: 51 conversations (10%)

**Data Leakage**: VERIFIED NO LEAKAGE
- Train-Val overlap: 0 conversations (VERIFIED)
- Train-Test overlap: 0 conversations (VERIFIED)
- Val-Test overlap: 0 conversations (VERIFIED)

**Reproducibility**: DETERMINISTIC (sequential split, no random seed)

**Assessment**: Split is clean with no data leakage

### Critical Tokenizer Compatibility Issue (VERIFIED)

**Problem**: Inference rebuilds tokenizer from train_v2.json but uses checkpoint vocab size

**Current Inference Flow** (ml-service/main.py lines 228-234):
1. Load checkpoint → extract vocab_size = 74
2. Initialize tokenizer with vocab_size=74
3. Build vocabulary from train_v2.json (502 conversations, 3,463 words)
4. tokenizer.build_vocab() caps at 74 tokens (due to vocab_size=74)
5. Result: Only top 74 most frequent words included

**Consequence** (VERIFIED):
- Bengali words (41 messages) EXCLUDED from inference tokenizer
- Long-tail English words EXCLUDED from inference tokenizer
- Checkpoint was trained on 74-token vocabulary from train_cleaned.json (mostly Bengali/English mix)
- Inference tokenizer builds 74-token vocabulary from train_v2.json (mostly English common words)
- **Vocabularies are DIFFERENT even though both have 74 tokens**

**Impact**: UNKNOWN (requires runtime test to determine actual effect on inference)

### train_with_v2.py Compatibility (VERIFIED)

**Checkpoint Destination**: `models/checkpoints_v2/` (line 82)

**Current Checkpoints**: `models/checkpoints_medium/` (line 71 in train_medium_model.py)

**Overwrite Risk**: NO - different directories

**Tokenizer Destination**: `tokenizer/v2_tokenizer.json` (line 81)

**Current Tokenizer**: `tokenizer/multilingual_tokenizer.json`

**Overwrite Risk**: NO - different filenames

**Assessment**: Safe to execute without overwriting existing checkpoints

### train_with_v2.py Configuration Analysis

**Dataset Conversion** (lines 29-40):
- Converts conversations to "role: content" format
- Example: "user: Hello assistant: Hello! I'm NexusAI..."
- **Issue**: Flattens conversation structure, loses role information for next-token prediction

**Max Sequence Length**: 256 (line 121, 30)

**Model max_len**: 512 (line 132)

**Mismatch**: Training max_len (256) < Model max_len (512) - conservative but may truncate longer conversations

**Vocabulary Size**: 3000 (line 100)

**Expected Actual Size**: 3000 tokens (train_v2.json has 3,463 unique words, so cap at 3000)

**Assessment**: Reasonable configuration for experiment

---

## Training Script Inventory

### Script 1: train_medium_model.py

**Location**: `packages/ai-core/train_medium_model.py`

**Purpose**: Train MediumTransformer on v1.0_cleaned dataset

**Dataset Used**: `data/public_datasets/v1.0_cleaned/train_cleaned.json` (19 samples)

**Tokenizer**: Loads or builds `tokenizer/multilingual_tokenizer.json`

**Configured Vocab Size**: 2000

**Actual Vocab Size**: 74 (due to insufficient data)

**Training Configuration**:
- Epochs: 5
- Batch size: 4
- Learning rate: 0.001
- Weight decay: 0.01
- Gradient clipping: 1.0
- Device: CPU
- Max sequence length: 128

**Status**: EXECUTED (produced current checkpoints)

**Verification**: Checkpoint metrics verify training completed successfully

---

### Script 2: train_with_v2.py

**Location**: `packages/ai-core/train_with_v2.py`

**Purpose**: Train MediumTransformer on v2 dataset

**Dataset Used**: `data/train_v2.json` (502 conversations)

**Tokenizer**: Builds and saves `tokenizer/v2_tokenizer.json`

**Configured Vocab Size**: 3000

**Expected Vocab Size**: 3,463+ (based on actual data analysis)

**Training Configuration**:
- Epochs: 3
- Batch size: 2
- Learning rate: 0.001
- Weight decay: 0.01
- Gradient clipping: 1.0
- Device: CPU
- Max sequence length: 256

**Status**: NOT EXECUTED (script exists but not run)

**Checkpoints Would Be Saved To**: `models/checkpoints_v2/`

**Verification**: Script is syntactically correct but not executed

---

## Dataset Summary Table

| Dataset | Path | Samples | Format | Used for Training | Used for Inference | Vocab Potential |
|---------|------|---------|--------|-------------------|-------------------|-----------------|
| train_cleaned.json | v1.0_cleaned/ | 19 | Strings | YES (current) | NO | 74 tokens |
| train_v2.json | data/ | 502 | Conversations | NO (alternative script) | YES (tokenizer rebuild) | 3,463+ tokens |
| v1.0/train.json | v1.0/ | 19 | Strings | NO | NO | 74 tokens |
| v1.0/validation.json | v1.0/ | 2 | Strings | NO | NO | UNKNOWN |
| v1.0/test.json | v1.0/ | 3 | Strings | NO | NO | UNKNOWN |
| conversational_data.json | data/ | 28 | UNKNOWN | NO | NO | UNKNOWN |
| merged_train.json | data/ | 167 | Mixed | NO | NO | UNKNOWN |
| train_final.json | data/ | 223 | Mixed | NO | NO | UNKNOWN |
| synthetic/train.json | synthetic/ | 148 | Strings | NO | NO | UNKNOWN |
| conversational_pairs.json | v1.0_cleaned/ | 17 | UNKNOWN | NO | NO | UNKNOWN |

## Recommendations

### Immediate Priority

1. **Use train_v2.json for training** - Execute `train_with_v2.py` to leverage 502 conversations with 3,463+ word vocabulary
2. **Ensure data quality** (diverse topics, proper formatting)
3. **Fix punctuation tokenization** (separate punctuation from words)
4. **Use same dataset for training and inference** - Currently training uses train_cleaned.json (19 samples) but inference tokenizer rebuilds from train_v2.json (502 samples)
5. **Implement data quality checks** (duplicate detection, malformed data filtering)

### Data Collection Strategy

1. **Increase Bengali samples** (currently limited)
2. **Increase English samples** (currently limited)
3. **Add diverse topics** (science, history, general knowledge)
4. **Add conversational format** (user/assistant pairs)
5. **Ensure proper encoding** (UTF-8 for Bengali)
6. **Balance language distribution** (50/50 or other target ratio)

### Data Preprocessing Improvements

1. **Punctuation separation** (strip punctuation from words)
2. **Duplicate detection and removal**
3. **Malformed data filtering**
4. **Length filtering** (remove too short/long samples)
5. **Quality scoring** (assess sample quality)
6. **Data augmentation** (for limited datasets)

---

## References

- **Training Dataset**: `packages/ai-core/data/public_datasets/v1.0_cleaned/train_cleaned.json`
- **Inference Dataset**: `packages/ai-core/data/train_v2.json`
- **Training Script**: `packages/ai-core/train_medium_model.py`
- **Tokenizer**: `packages/ai-core/tokenizer/tokenizer.py`
- **Saved Tokenizer**: `packages/ai-core/tokenizer/multilingual_tokenizer.json`
