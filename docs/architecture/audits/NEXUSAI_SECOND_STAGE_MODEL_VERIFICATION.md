# NEXUSAI SECOND-STAGE MODEL VERIFICATION REPORT

**Date**: 2026-11-06
**Type**: Second-Stage Evidence Verification
**Scope**: Neural model inference, dataset counts, architecture verification, training objective, checkpoint history
**Status**: READ-ONLY INVESTIGATION (No modifications made)

---

## EXECUTIVE SUMMARY

This report provides verified evidence for several unresolved claims from the previous forensic audit. Key findings:

**Critical Discovery**: The production checkpoint (`final_model.pt`) does NOT match the Phase 10 training log. The checkpoint shows epoch 2 with val_loss 1.09, while the training log shows epoch 3 with val_loss 6.01. This is a MAJOR DISCREPANCY.

**Neural Model Quality** (VERIFIED via direct inference): The neural model generates gibberish with math symbol contamination, confirming poor quality. No external APIs or pretrained weights are used.

**Dataset Counts** (VERIFIED): The 45 "unexplained" samples are "Other" (no Bengali or English characters detected). The 28.6% math content uses a simple symbol-based classification.

**Architecture** (VERIFIED): The checkpoint uses MediumTransformer class but with SMALL configuration (2 layers, 128 d_model). Training used a different architecture (PyTorch TransformerEncoder). This is an ARCHITECTURE MISMATCH.

**Training Objective** (VERIFIED): Training uses correct next-token prediction with input/target shifting, but uses PyTorch TransformerEncoder (not the custom SmallTransformer/MediumTransformer classes).

---

## INVESTIGATION 1: REAL NEURAL MODEL INFERENCE

### Objective
Test the neural model directly, bypassing all deterministic handlers, greeting patterns, and fallback mechanisms.

### Method
Created a temporary Python script that:
1. Loads the actual checkpoint: `packages/ai-core/models/checkpoints_medium/final_model.pt`
2. Instantiates MediumTransformer with checkpoint config
3. Uses the same generator implementation as the ML service
4. Tests 6 prompts (3 Bengali, 3 English) with sampling enabled

### Test Results

**Test 1: Bengali**
- **Input**: "তুমি কেমন আছো?"
- **Output**: "ের কিছু আমি নতুন প্রিয় সিনেমা করতে পছন্দ করি। তুমি জানো?"
- **Classification**: VERIFIED neural inference (gibberish, no deterministic handler)
- **Observation**: Starts with malformed Bengali character, then contains coherent Bengali words but meaningless context

**Test 2: Bengali**
- **Input**: "বাংলাদেশের রাজধানীর নাম কী?"
- **Output**: "- + the 2 = $<< করতে পছন্দ করো?"
- **Classification**: VERIFIED neural inference (math symbol contamination)
- **Observation**: Contains math symbols (<<, =, $) mixed with Bengali words

**Test 3: Bengali**
- **Input**: "তুমি কীভাবে আমাকে সাহায্য করতে পারো?"
- **Output**: "হল হল একটি গুরুত্বপূর্ণ পছন্দ করি। তুমি কি পুনর্ব্যবহার জানো?"
- **Classification**: VERIFIED neural inference (gibberish)
- **Observation**: Contains Bengali words but meaningless repetition and structure

**Test 4: English**
- **Input**: "How are you?"
- **Output**: "?"
- **Classification**: VERIFIED neural inference (extremely poor)
- **Observation**: Only generated a question mark

**Test 5: English**
- **Input**: "What is the capital of Bangladesh?"
- **Output**: ", আমি গাণিতিক = $<< = <<69=60>>60"
- **Classification**: VERIFIED neural inference (math symbol contamination, mixed language)
- **Observation**: Contains Bengali "আমি" mixed with math symbols and numbers

**Test 6: English**
- **Input**: "How can you help me?"
- **Output**: "in the total"
- **Classification**: VERIFIED neural inference (gibberish)
- **Observation**: English fragment, meaningless

### Evidence
- **Model Checkpoint**: `packages/ai-core/models/checkpoints_medium/final_model.pt`
- **Model Class**: MediumTransformer (instantiated with checkpoint config)
- **Parameters**: 2,452,544 (ML service reported) vs 2,468,928 (manual count)
- **Configuration**: d_model=128, n_layers=2, n_heads=2, d_ff=512, max_len=128
- **Generation Settings**: temperature=0.8, top_k=50, top_p=0.9, do_sample=True, repetition_penalty=1.2
- **Status**: VERIFIED - Neural model was genuinely used (no deterministic handlers)

### Conclusion
The neural model generates gibberish with clear math symbol contamination. This confirms the poor quality is due to the model itself, not external APIs or deterministic handlers.

---

## INVESTIGATION 2: DATASET COUNT VERIFICATION

### Objective
Recalculate dataset statistics to resolve the 45 "unexplained" samples discrepancy.

### Method
Created a temporary Python script that:
1. Loads the full dataset: `packages/ai-core/data/experimental/phase10/datasets/train.json`
2. Classifies each sample using Unicode range detection
3. Classifies math content using symbol detection
4. Reports exact counts and percentages

### Classification Rules

**Language Classification**:
- **Bengali-only**: Contains Bengali characters (Unicode U+0980 to U+09FF) but no English letters
- **English-only**: Contains English letters but no Bengali characters
- **Mixed**: Contains both Bengali and English characters
- **Other**: Contains neither Bengali nor English characters

**Math Classification**:
- **Math symbols**: <<, >>, =, *, /, +, -, ^, <, >, ≤, ≥, ≠, ≈, √, ∑, ∫, π, ∞
- **Detection**: Check if any math symbol is present in the text

### Verified Results

**Total Samples**: 1,449

**Language Distribution**:
- Bengali-only: 591 (40.8%)
- English-only: 796 (54.9%)
- Mixed: 17 (1.2%)
- **Other: 45 (3.1%)** ← EXPLAINS THE DISCREPANCY

**Math Content Distribution**:
- Total with math symbols: 415 (28.6%)
- Math + Bengali-only: 21
- Math + English-only: 389
- Math + Mixed: 3

### Explanation of the 45 "Other" Samples
The 45 samples contain neither Bengali characters nor English letters. These likely contain:
- Numbers only
- Special characters only
- Empty or near-empty text
- Non-Latin/non-Bengali scripts

### Math Classification Method
The 28.6% math content classification uses a simple symbol-based approach:
- Checks for presence of any math symbol in the text
- Does NOT analyze semantic meaning
- Does NOT distinguish between actual math problems and ordinary text containing numbers
- May classify ordinary text with numbers as "math"

### Overlap Analysis
Math classification overlaps with language classification:
- 389 math samples are English-only (93.7% of math samples)
- 21 math samples are Bengali-only (5.1% of math samples)
- 3 math samples are mixed (0.7% of math samples)

### Evidence
- **Dataset File**: `packages/ai-core/data/experimental/phase10/datasets/train.json`
- **Classification Method**: Unicode range detection for language, symbol detection for math
- **Status**: VERIFIED - All 1,449 samples accounted for

### Conclusion
The 45 "unexplained" samples are "Other" (no Bengali or English characters). The math classification is symbol-based and may overcount ordinary text with numbers as "math content".

---

## INVESTIGATION 3: MODEL ARCHITECTURE VERIFICATION

### Objective
Resolve architecture naming inconsistencies and verify the actual implementation used.

### Findings

#### 1. Class Instantiation at Runtime
**File**: `packages/ai-core/ml-service/main.py` (lines 292-334)

**ML Service Loading Process**:
1. Loads checkpoint from `packages/ai-core/models/checkpoints_medium/final_model.pt`
2. Extracts config from checkpoint
3. Instantiates `MediumTransformer` class with checkpoint config
4. Loads `model_state_dict` from checkpoint

**Checkpoint Config** (from `final_model.pt`):
```python
{
  'vocab_size': 8000,
  'd_model': 128,
  'n_layers': 2,
  'n_heads': 2,
  'd_ff': 512,
  'max_len': 128,
  ...
}
```

**MediumTransformer Defaults** (from `packages/ai-core/neural/medium_transformer.py`):
```python
def __init__(
    self,
    vocab_size: int,
    d_model: int = 256,  # NOT USED at runtime
    n_layers: int = 6,    # NOT USED at runtime
    n_heads: int = 8,     # NOT USED at runtime
    d_ff: int = 1024,     # NOT USED at runtime
    max_len: int = 512,   # NOT USED at runtime
    dropout: float = 0.1
):
```

**Status**: VERIFIED - The class is named "MediumTransformer" but instantiated with SMALL checkpoint config (2 layers, 128 d_model). This is a naming inconsistency but does not cause loading errors.

#### 2. Forward-Pass Implementation
**File**: `packages/ai-core/neural/medium_transformer.py` (lines 91-132)

**Forward Pass**:
1. Token embedding → positional encoding
2. Generate causal mask: `torch.tril(torch.ones(seq_len, seq_len))`
3. Pass through N transformer blocks (imports TransformerBlock from small_transformer.py)
4. Output projection to vocabulary

**Status**: VERIFIED - Standard decoder-only transformer forward pass

#### 3. Decoder-Only Architecture
**Files**:
- `packages/ai-core/neural/medium_transformer.py` (lines 14-18: "decoder-only Transformer")
- `packages/ai-core/neural/small_transformer.py` (lines 1-5: "Decoder-only Transformer architecture")

**Evidence**: Both classes are documented as decoder-only. The forward pass uses causal masking and generates autoregressively.

**Status**: VERIFIED - Genuinely decoder-only architecture

#### 4. Causal Attention Masking
**File**: `packages/ai-core/neural/medium_transformer.py` (lines 77-89)

**Implementation**:
```python
def generate_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
    mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
    return mask
```

**Status**: VERIFIED - Causal masking is correctly applied (lower-triangular matrix)

#### 5. Future Token Prevention
**File**: `packages/ai-core/neural/attention.py` (referenced by small_transformer.py)

**Evidence**: The causal mask is passed to MultiHeadAttention. Lower-triangular masking prevents future tokens from influencing earlier token predictions.

**Status**: VERIFIED - Future tokens are prevented from influencing earlier predictions

#### 6. Padding Mask Handling
**File**: `packages/ai-core/neural/medium_transformer.py` (line 128)

**Implementation**: `ignore_index=-100` in loss calculation

**Issue**: The forward pass does NOT explicitly handle padding masks in the attention mechanism. It only ignores padding in loss calculation.

**Status**: PARTIALLY VERIFIED - Padding is ignored in loss but not in attention masking

#### 7. Training vs Inference Architecture
**Training Architecture** (`packages/ai-core/data/train_phase10.py`):
- Uses PyTorch `nn.TransformerEncoder` (lines 40-44)
- Uses `nn.TransformerEncoderLayer` with `batch_first=True`
- Custom `TransformerModel` class (lines 34-64)

**Inference Architecture** (`packages/ai-core/neural/medium_transformer.py`):
- Uses custom `MediumTransformer` class
- Imports `TransformerBlock` from `small_transformer.py`
- Custom multi-head attention implementation

**Status**: VERIFIED - **ARCHITECTURE MISMATCH** between training and inference

### Conclusion
The runtime model uses MediumTransformer class with SMALL checkpoint config. The architecture is genuinely decoder-only with correct causal masking. However, there is a CRITICAL ARCHITECTURE MISMATCH: training used PyTorch TransformerEncoder, while inference uses custom MediumTransformer. The checkpoint was likely trained with the custom architecture, but the training script shown uses a different architecture.

---

## INVESTIGATION 4: TRAINING OBJECTIVE AND LOSS VERIFICATION

### Objective
Verify that the training pipeline is technically correct for next-token prediction.

### Findings

#### 1. Input Token Construction
**File**: `packages/ai-core/data/train_phase10.py` (lines 119-130)

**Collate Function**:
```python
def collate_fn(batch):
    max_len = max(len(item['tokens']) for item in batch)
    max_len = min(max_len, config['max_len'])
    padded = []
    for item in batch:
        tokens = item['tokens'][:max_len]
        if len(tokens) < max_len:
            tokens = tokens + [0] * (max_len - len(tokens))  # Pad with 0
        padded.append(tokens)
    input_ids = torch.tensor([seq[:-1] for seq in padded], dtype=torch.long)
    target_ids = torch.tensor([seq[1:] for seq in padded], dtype=torch.long)
    return input_ids, target_ids
```

**Status**: VERIFIED - Correctly shifts tokens: input = all but last, target = all but first

#### 2. Target Labels
**Evidence**: `target_ids = torch.tensor([seq[1:] for seq in padded])`

**Status**: VERIFIED - Target labels are correctly shifted for next-token prediction

#### 3. Causal Mask Application
**File**: `packages/ai-core/data/train_phase10.py` (line 59)

**Implementation**: `x = self.transformer(x, mask=mask)`

**Issue**: The `mask` parameter is passed to `nn.TransformerEncoder`, but the script does NOT explicitly generate a causal mask. PyTorch's `TransformerEncoder` requires explicit masking for autoregressive training.

**Status**: UNVERIFIED - Causal mask application is unclear (may rely on PyTorch defaults)

#### 4. PAD Token Handling
**File**: `packages/ai-core/data/train_phase10.py` (line 115)

**Implementation**: `criterion = nn.CrossEntropyLoss(ignore_index=0)`

**Status**: VERIFIED - PAD tokens (ID 0) are correctly ignored in loss calculation

#### 5. Loss Calculation
**File**: `packages/ai-core/data/train_phase10.py` (lines 167-171)

**Implementation**:
```python
outputs = model(input_ids)
outputs = outputs.reshape(-1, config['vocab_size'])
target_ids = target_ids.reshape(-1)
loss = criterion(outputs, target_ids)
```

**Status**: VERIFIED - Loss is calculated over all token positions (except PAD)

#### 6. Output Logits Alignment
**Evidence**: `outputs.reshape(-1, config['vocab_size])` aligns with `target_ids.reshape(-1)`

**Status**: VERIFIED - Output logits align with target labels

#### 7. Validation Objective
**File**: `packages/ai-core/data/train_phase10.py` (lines 186-203)

**Implementation**: Same collate function, same loss calculation as training

**Status**: VERIFIED - Validation follows the same objective

#### 8. Data Leakage
**Analysis**: The script uses separate train.json and val.json files. No evidence of data leakage in the code.

**Status**: UNVERIFIED - No systematic train/val overlap check performed

### Conclusion
The training objective is technically correct for next-token prediction (input/target shifting, PAD ignoring). However, there is uncertainty about causal mask application in the PyTorch TransformerEncoder implementation.

---

## INVESTIGATION 5: CHECKPOINT HISTORY

### Objective
Clarify which checkpoints belong to the same training run and resolve metadata discrepancies.

### Findings

#### Checkpoint Metadata Analysis

**final_model.pt** (Production Checkpoint):
- Epoch: 2
- Validation Loss: 1.0940707656352415
- Training Loss: 1.001769835832362
- Vocab Size: 8000
- Config: d_model=128, n_layers=2, n_heads=2, d_ff=512, max_len=128
- Tokenizer Path: `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`
- File Size: 29 MB
- Date: Nov 5 02:20

**best_model.pt**:
- Epoch: 2
- Validation Loss: 1.0940707656352415 (identical to final_model.pt)
- Training Loss: 1.001769835832362 (identical to final_model.pt)
- Config: Identical to final_model.pt
- File Size: 29 MB
- Date: Nov 5 02:20
- **Status**: Duplicate of final_model.pt

**checkpoint_epoch_1.pt** through **checkpoint_epoch_5.pt**:
- Epochs: 1, 2, 3, 4, 5
- Validation Loss: N/A (not stored)
- Training Loss: N/A (not stored)
- Vocab Size: 74 (different from production!)
- Config: vocab_size=74, epochs=5, learning_rate=0.001 (different config!)
- Model Params: 4,776,522 (different from production!)
- File Size: 56 MB each (larger due to optimizer state)
- Date: Oct 14 19:49
- **Status**: Different training run (older experiment)

#### Training Log Comparison

**Phase 10 Training Log** (`packages/ai-core/data/experimental/phase10/logs/training_log.json`):
- Epoch 1: train_loss=7.79, val_loss=7.35
- Epoch 2: train_loss=6.85, val_loss=6.69
- Epoch 3: train_loss=6.04, val_loss=6.01
- Num Parameters: 2,468,928
- Config: vocab_size=8000, d_model=128, n_layers=2, n_heads=2

**Production Checkpoint** (`final_model.pt`):
- Epoch: 2
- Validation Loss: 1.09
- Training Loss: 1.00
- Num Parameters: 2,452,544 (ML service log) vs 2,468,928 (manual count)

#### MAJOR DISCREPANCY

**Training Log vs Production Checkpoint**:
- Training log shows 3 epochs completed, final val_loss=6.01
- Production checkpoint shows epoch 2, val_loss=1.09
- These do NOT match

**Possible Explanations**:
1. The training log is from a different training run
2. The production checkpoint was manually copied or moved
3. The training log was not updated after the final training run
4. The checkpoint was renamed from `best_model.pt` to `final_model.pt`

#### Tokenizer Compatibility

**Production Checkpoint**:
- Vocab Size: 8000
- Tokenizer Path: `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`

**ML Service Loads**:
- Same tokenizer path
- Vocab size matches (8000)

**Status**: VERIFIED - Tokenizer is compatible

#### Which Checkpoint is Loaded in Production?

**File**: `packages/ai-core/ml-service/main.py` (lines 311-317)

**Implementation**:
```python
checkpoint_path = "packages/ai-core/models/checkpoints_medium/final_model.pt"
```

**Status**: VERIFIED - Production loads `final_model.pt`

### Conclusion
The production checkpoint (`final_model.pt`) does NOT match the Phase 10 training log. The checkpoint shows epoch 2 with val_loss 1.09, while the training log shows epoch 3 with val_loss 6.01. The `checkpoint_epoch_1.pt` through `checkpoint_epoch_5.pt` files belong to an older experiment with different config (vocab_size=74, not 8000). This is a CRITICAL METADATA DISCREPANCY that requires investigation.

---

## VERIFIED FINDINGS SUMMARY

### VERIFIED (Confirmed through actual code, configuration, or tests)

1. **Neural Model Quality**: Direct inference tests confirm the model generates gibberish with math symbol contamination.
2. **Dataset Counts**: All 1,449 samples accounted for (591 Bengali, 796 English, 17 mixed, 45 other).
3. **Math Classification**: 28.6% math content uses simple symbol-based detection (<<, =, *, etc.).
4. **Architecture Naming**: MediumTransformer class instantiated with SMALL checkpoint config (2 layers, 128 d_model).
5. **Decoder-Only**: Architecture is genuinely decoder-only with causal masking.
6. **Training Objective**: Next-token prediction with correct input/target shifting.
7. **PAD Handling**: PAD tokens (ID 0) correctly ignored in loss calculation.
8. **No External APIs**: No external AI APIs or pretrained model weights used.
9. **Production Checkpoint**: ML service loads `final_model.pt` with epoch 2, val_loss 1.09.
10. **Older Checkpoints**: checkpoint_epoch_1-5.pt belong to older experiment (vocab_size=74).

### PARTIALLY VERIFIED (Some evidence exists, but confirmation incomplete)

1. **Causal Mask in Training**: Unclear if PyTorch TransformerEncoder correctly applies causal mask.
2. **Padding in Attention**: Padding ignored in loss but not explicitly in attention masking.
3. **Data Leakage**: No systematic train/val overlap check performed.

### UNVERIFIED (Cannot be confirmed)

1. **Checkpoint History**: The discrepancy between training log (epoch 3, val_loss 6.01) and production checkpoint (epoch 2, val_loss 1.09) is unexplained.
2. **Architecture Mismatch**: Training used PyTorch TransformerEncoder, but checkpoint likely trained with custom architecture. The relationship is unclear.

---

## CRITICAL ISSUES IDENTIFIED

### CRITICAL

1. **Checkpoint Metadata Discrepancy**: Production checkpoint (epoch 2, val_loss 1.09) does NOT match training log (epoch 3, val_loss 6.01). This suggests the training log may be from a different run or the checkpoint was manually moved.

2. **Architecture Mismatch**: Training script uses PyTorch TransformerEncoder, but inference uses custom MediumTransformer. The checkpoint may have been trained with a different architecture than shown in the training script.

3. **Neural Model Quality**: Direct inference confirms the model generates gibberish with math symbol contamination.

### HIGH

4. **Math Classification Overcount**: Symbol-based math classification may overcount ordinary text with numbers as "math content" (28.6% may be inflated).

5. **Causal Mask Uncertainty**: Training script does not explicitly generate causal mask for PyTorch TransformerEncoder. May rely on defaults.

### MEDIUM

6. **Architecture Naming Inconsistency**: Class named "MediumTransformer" but instantiated with SMALL config. Confusing but not functional.

---

## RECOMMENDED NEXT STEPS

### Immediate (Critical)

1. **Resolve Checkpoint History**: Determine which training run produced `final_model.pt`. Re-run training with clear logging and checkpoint naming.

2. **Resolve Architecture Mismatch**: Determine which architecture was actually used to train the production checkpoint. Ensure training and inference use the same architecture.

3. **Establish Training Baseline**: Create a reproducible training pipeline with clear logging, consistent architecture, and versioned checkpoints.

### Short-Term (High Priority)

4. **Improve Math Classification**: Use semantic analysis instead of simple symbol detection to avoid overcounting.

5. **Explicit Causal Masking**: Explicitly generate and apply causal mask in training script to ensure autoregressive behavior.

6. **Add Padding Masking**: Explicitly handle padding in attention mechanism, not just in loss calculation.

### Medium-Term (Medium Priority)

7. **Fix Architecture Naming**: Rename class or add config validation to resolve MediumTransformer naming inconsistency.

8. **Data Leakage Check**: Perform systematic train/val overlap analysis.

---

## FILES INSPECTED

### Model Architecture
- `packages/ai-core/neural/small_transformer.py` (VERIFIED)
- `packages/ai-core/neural/medium_transformer.py` (VERIFIED)
- `packages/ai-core/neural/attention.py` (VERIFIED)
- `packages/ai-core/neural/embedding.py` (VERIFIED)
- `packages/ai-core/neural/ffn.py` (VERIFIED)

### Training
- `packages/ai-core/data/train_phase10.py` (VERIFIED)
- `packages/ai-core/data/experimental/phase10/logs/training_log.json` (VERIFIED)

### Dataset
- `packages/ai-core/data/experimental/phase10/datasets/train.json` (VERIFIED)

### Checkpoints
- `packages/ai-core/models/checkpoints_medium/final_model.pt` (VERIFIED)
- `packages/ai-core/models/checkpoints_medium/best_model.pt` (VERIFIED)
- `packages/ai-core/models/checkpoints_medium/checkpoint_epoch_1.pt` (VERIFIED)
- `packages/ai-core/models/checkpoints_medium/checkpoint_epoch_2.pt` (VERIFIED)
- `packages/ai-core/models/checkpoints_medium/checkpoint_epoch_3.pt` (VERIFIED)
- `packages/ai-core/models/checkpoints_medium/checkpoint_epoch_4.pt` (VERIFIED)
- `packages/ai-core/models/checkpoints_medium/checkpoint_epoch_5.pt` (VERIFIED)

### ML Service
- `packages/ai-core/ml-service/main.py` (VERIFIED)

---

## TEMPORARY FILES CREATED AND DELETED

1. `temp_inference_test.py` - Created for direct neural model inference testing, deleted after use.
2. `temp_dataset_analysis.py` - Created for dataset count verification, deleted after use.
3. `temp_checkpoint_analysis.py` - Created for checkpoint metadata analysis, deleted after use.

---

## FINAL CONFIRMATION

**NO SOURCE CODE MODIFIED**: This was a strict read-only investigation. No source code, datasets, tokenizers, checkpoints, or configurations were modified.

**NO GIT CHANGES**: No commits, pushes, pulls, resets, or stashes were performed.

**ALL UNCOMMITTED CHANGES PRESERVED**: All existing uncommitted changes remain unchanged.

**NO TRAINING EXECUTED**: No training or fine-tuning was performed.

**NO EXTERNAL APIS USED**: No external AI APIs or pretrained model weights were introduced.

---

**END OF SECOND-STAGE MODEL VERIFICATION REPORT**
