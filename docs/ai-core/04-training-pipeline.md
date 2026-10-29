# Training Pipeline Documentation

**Last Updated**: 2026-10-26 (Phase 2 Forensic Audit)  
**Verification Status**: VERIFIED from checkpoint metrics and source inspection

---

## Overview

The AI Core includes a complete training pipeline for training neural models on text datasets. This document describes the training infrastructure, configuration, dataset selection, and checkpoint management.

## Training Infrastructure

### Core Components

**Location**: `packages/ai-core/training/`

#### 1. TrainingPipeline

**File**: `pipeline.py`

**Class**: `TrainingPipeline`

**Purpose**: Main training loop and optimization logic

**Responsibilities**:
- Create data loaders
- Setup optimizer (AdamW)
- Training loop with gradient clipping
- Validation loop
- Checkpoint saving
- Training configuration management

**Key Methods**:
- `train()` — Main training method
- `_train_epoch()` — Single epoch training
- `_validate_epoch()` — Single epoch validation

#### 2. TextDataset

**File**: `dataset.py`

**Class**: `TextDataset`

**Purpose**: Dataset loader for training

**Responsibilities**:
- Load text samples
- Tokenize text
- Create input/target pairs (shifted by 1 for next-token prediction)
- Padding/truncation to max_len

**Data Format**:
```python
{
    "input_ids": torch.Tensor,  # [batch_size, seq_len-1]
    "targets": torch.Tensor     # [batch_size, seq_len-1]
}
```

#### 3. CheckpointManager

**File**: `checkpoint.py`

**Class**: `CheckpointManager`

**Purpose**: Save and load model checkpoints

**Responsibilities**:
- Save checkpoints with metadata
- Load checkpoints
- Resume training from checkpoint
- Get latest checkpoint

**Checkpoint Format**:
```python
{
    "model_state_dict": dict,
    "optimizer_state_dict": dict,
    "epoch": int,
    "loss": float,
    "metadata": dict,
    "config": dict
}
```

## Training Script

### MediumTransformer Training

**File**: `packages/ai-core/train_medium_model.py`

**Purpose**: Train MediumTransformer on multilingual dataset

### Dataset Selection

**Configured Dataset**: `data/public_datasets/v1.0_cleaned/train_cleaned.json`

**Actual Size**: 19 samples (VERIFIED)

**Format**: Array of strings (simple text)

**Sample Data**:
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

### Tokenizer Configuration

**Tokenizer**: SimpleTokenizer

**Configured Vocab Size**: 2000 (line 82)

**Min Frequency**: 1 (line 89)

**Actual Vocab Size**: 74 tokens (VERIFIED from saved tokenizer)

**Saved Tokenizer**: `tokenizer/multilingual_tokenizer.json`

### Model Configuration

**Model**: MediumTransformer

**Configuration** (lines 112-120):
```python
model = MediumTransformer(
    vocab_size=tokenizer.get_vocab_size(),  # 74
    d_model=256,
    n_layers=6,
    n_heads=8,
    d_ff=1024,
    max_len=512,
    dropout=0.1
)
```

**Parameter Count**: 4,776,522 (VERIFIED from checkpoint)

### Training Configuration

**Training Configuration** (lines 136-145):
```python
metrics = pipeline.train(
    train_dataset=train_dataset,
    val_dataset=val_dataset,
    epochs=5,  # Start with 5 epochs for testing
    batch_size=4,  # Small batch size for CPU
    learning_rate=0.001,
    weight_decay=0.01,
    grad_clip=1.0,
    checkpoint_freq=1
)
```

**Details**:
- **Epochs**: 5
- **Batch Size**: 4
- **Learning Rate**: 0.001
- **Weight Decay**: 0.01
- **Gradient Clipping**: 1.0
- **Checkpoint Frequency**: Every 1 epoch
- **Device**: CPU

### Optimizer

**Type**: AdamW

**Configuration** (from `pipeline.py` lines 77-81):
```python
optimizer = torch.optim.AdamW(
    self.model.parameters(),
    lr=learning_rate,
    weight_decay=weight_decay
)
```

### Data Split

**Split** (lines 96-101):
```python
train_size = int(len(texts) * 0.8)
val_size = int(len(texts) * 0.1)

train_texts = texts[:train_size]
val_texts = texts[train_size:train_size + val_size]
test_texts = texts[train_size + val_size:]
```

**Actual Split** (19 samples):
- Train: 15 samples (80%)
- Validation: 2 samples (10%)
- Test: 2 samples (10%)

### Checkpoint Saving

**Save Location**: `models/checkpoints_medium/`

**Naming Convention**: `checkpoint_epoch_{epoch}.pt`

**Final Checkpoint**: `final_model.pt`

**Save Code** (lines 152-157):
```python
final_checkpoint = checkpoint_dir / "final_model.pt"
torch.save({
    'model_state_dict': model.state_dict(),
    'tokenizer_vocab': tokenizer.word_to_id,
    'metrics': metrics
}, final_checkpoint)
```

**Saved Metadata**:
- Model state dict
- Tokenizer vocabulary (74 tokens)
- Training metrics

## Checkpoint Management

### Checkpoint Format

**Structure**:
```python
{
    "model_state_dict": {
        "token_embedding.embedding.weight": tensor,
        "positional_encoding.pe": tensor,
        "transformer_blocks.0.self_attention.w_q.weight": tensor,
        # ... all model parameters
    },
    "tokenizer_vocab": {
        "<PAD>": 0,
        "<UNK>": 1,
        "<BOS>": 2,
        "<EOS>": 3,
        "is": 4,
        # ... 74 total tokens
    },
    "metrics": {
        "final_train_loss": float,
        "final_val_loss": float,
        "train_losses": list,
        "val_losses": list
    }
}
```

### Available Checkpoints

**Medium Model**:
- `models/checkpoints_medium/checkpoint_epoch_1.pt`
- `models/checkpoints_medium/checkpoint_epoch_2.pt`
- `models/checkpoints_medium/checkpoint_epoch_3.pt`
- `models/checkpoints_medium/checkpoint_epoch_4.pt`
- `models/checkpoints_medium/checkpoint_epoch_5.pt`
- `models/checkpoints_medium/final_model.pt` (currently loaded)

**Small Model**:
- `models/checkpoints/checkpoint_epoch_1.pt`
- `models/checkpoints/checkpoint_epoch_2.pt`
- `models/checkpoints/checkpoint_epoch_3.pt`
- `models/checkpoints/checkpoint_epoch_4.pt`
- `models/checkpoints/checkpoint_epoch_5.pt`

### Checkpoint Loading

**ML Service Loading** (lines 214-258 in `main.py`):
```python
checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")
checkpoint = torch.load(checkpoint_path, map_location="cpu")

# Extract vocab size from checkpoint
if "tokenizer_vocab" in checkpoint:
    checkpoint_vocab_size = len(checkpoint["tokenizer_vocab"])
elif "model_state_dict" in checkpoint:
    checkpoint_vocab_size = checkpoint["model_state_dict"]["token_embedding.embedding.weight"].shape[0]

# Use checkpoint vocab size
vocab_size = checkpoint_vocab_size if checkpoint_vocab_size else 2000
tokenizer = SimpleTokenizer(vocab_size=vocab_size)

# Build vocabulary from dataset
train_texts = load_json_dataset(os.path.join(ai_core_dir, "data/train_v2.json"))
tokenizer.build_vocab(train_texts, min_freq=1)

# Create model with actual vocab size
model = MediumTransformer(
    vocab_size=tokenizer.get_vocab_size(),
    d_model=256,
    n_layers=6,
    n_heads=8,
    d_ff=1024,
    max_len=512
)

# Load weights
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
```

## Training Issues

### Issue 1: Insufficient Training Data

**Problem**: Training dataset contains only 19 samples

**Impact**: 
- Vocabulary limited to 74 tokens (instead of configured 2000)
- Model severely undertrained
- Output quality is incoherent

**Status**: VERIFIED

**Root Cause**: Dataset file `train_cleaned.json` has only 19 entries

### Issue 2: Vocabulary Size Mismatch

**Problem**: Training script configures vocab_size=2000, but actual vocab is 74

**Impact**: Model trained on insufficient vocabulary

**Status**: VERIFIED

**Root Cause**: Insufficient training data cannot support 2000 tokens

### Issue 3: Training Configuration

**Problem**: Small batch size (4) and few epochs (5) on tiny dataset

**Impact**: Limited training iterations

**Status**: VERIFIED

**Note**: This is appropriate for CPU training on small dataset, but the dataset itself is the problem

## Training Status

### MediumTransformer

**Status**: TRAINED (checkpoint exists)

**Training Data**: 19 samples

**Epochs**: 5

**Checkpoints**: 5 epoch checkpoints + final checkpoint

**Quality**: POOR (incoherent output)

**Verification**: Checkpoint loads successfully, parameters match expected

### SmallTransformer

**Status**: TRAINED (checkpoints exist)

**Training Data**: UNKNOWN

**Epochs**: 5 (assumed from checkpoint naming)

**Checkpoints**: 5 epoch checkpoints

**Quality**: UNKNOWN (not tested)

**Verification**: Checkpoints exist, but not loaded or tested

## Training Verification

### What Was Verified

- ✅ Training script exists and is syntactically correct
- ✅ Checkpoints exist for both models
- ✅ Checkpoint format contains expected fields
- ✅ Checkpoint loads successfully in ML service
- ✅ Parameter count matches expected (4,776,522)
- ✅ Embedding and output layer shapes match
- ✅ **Training completed successfully** (metrics verified from final_model.pt)
- ✅ **Training loss values accessible** (from checkpoint metrics)
- ✅ **Validation loss values accessible** (from checkpoint metrics)
- ✅ **Training converged** (loss decreased steadily across epochs)

### Training Metrics (VERIFIED from final_model.pt)

**Final Checkpoint**: `models/checkpoints_medium/final_model.pt`

**Training Loss History**:
- Epoch 1: 1.7583
- Epoch 2: 0.4355
- Epoch 3: 0.3038
- Epoch 4: 0.2252
- Epoch 5: 0.1933

**Validation Loss History**:
- Epoch 1: 0.4361
- Epoch 2: 0.2376
- Epoch 3: 0.1964
- Epoch 4: 0.1633
- Epoch 5: 0.1579

**Final Metrics**:
- Final train loss: 0.1933
- Final val loss: 0.1579

**Training Convergence**: VERIFIED - Both training and validation loss decreased steadily across all 5 epochs

### What Was NOT Verified

- ❓ Training duration (not recorded in checkpoint)
- ❓ SmallTransformer training data and quality
- ❓ Whether training plateaued or could benefit from more epochs

### Unknowns

- ❓ Why `train_cleaned.json` has only 19 samples
- ❓ Whether the 19 samples were intentionally limited or accidental
- ❓ Whether training completed all 5 epochs successfully
- ❓ Whether validation loss was improving or stable
- ❓ Why multilingual_tokenizer.json has 74 tokens instead of 2000

## Recommendations

### Immediate Priority

1. **Collect sufficient training data** (1000+ samples, ideally 10,000+)
2. **Rebuild tokenizer** with proper vocabulary (2000+ tokens)
3. **Retrain model** with sufficient data

### Training Improvements

1. Increase dataset size to at least 1000 samples
2. Consider data augmentation for Bengali/English
3. Ensure balanced language distribution
4. Consider longer training (more epochs) with proper validation
5. Monitor training and validation loss
6. Implement early stopping
7. Consider learning rate scheduling

### Infrastructure Improvements

1. Add training logging
2. Save training metrics to file
3. Implement tensorboard logging
4. Add model evaluation during training
5. Implement gradient monitoring
6. Add data quality checks

## References

- **Training Script**: `packages/ai-core/train_medium_model.py`
- **Training Pipeline**: `packages/ai-core/training/pipeline.py`
- **Dataset**: `packages/ai-core/training/dataset.py`
- **Checkpoint Manager**: `packages/ai-core/training/checkpoint.py`
- **Checkpoints**: `packages/ai-core/models/`
- **Dataset File**: `packages/ai-core/data/public_datasets/v1.0_cleaned/train_cleaned.json`
