# NexusAI Model Checkpoints

This directory contains trained model checkpoints for the NexusAI AI Brain.

## Directory Structure

```
models/
├── checkpoints/          # Small Transformer checkpoints (legacy)
├── checkpoints_medium/    # Medium Transformer checkpoints (active)
└── checkpoints_retrained/ # Retrained checkpoints (experimental)
```

## Active Model

**Current Production Model**: MediumTransformer  
**Checkpoint**: `checkpoints_medium/final_model.pt`  
**Architecture**: 6-layer Transformer decoder  
**Parameters**: 4,776,522  
**Vocabulary Size**: 74 tokens  
**Max Sequence Length**: 512  
**Training Epochs**: 5  
**Training Samples**: 19 (from data/public_datasets/v1.0_cleaned/train_cleaned.json)

### Checkpoint Details

**File**: `checkpoints_medium/final_model.pt`  
**Size**: 18.76 MB  
**Contents**:
- `model_state_dict`: PyTorch model weights
- `tokenizer_vocab`: 74-token vocabulary mapping
- `metrics`: Training and validation loss values

**Checkpoint Keys**:
```python
{
  'model_state_dict': dict,      # Model weights
  'tokenizer_vocab': dict,        # Vocabulary mapping
  'metrics': dict                 # Training metrics
}
```

## Legacy Checkpoints

### Small Transformer (checkpoints/)

**Architecture**: SmallTransformer  
**Parameters**: ~200,000  
**Vocabulary Size**: 1,000  
**Training Samples**: Unknown  

**Files**:
- `checkpoint_epoch_1.pt` through `checkpoint_epoch_5.pt` (2.10 MB each)

**Status**: Legacy, not actively used by the application.

### Medium Transformer Training History (checkpoints_medium/)

**Files**:
- `checkpoint_epoch_1.pt` through `checkpoint_epoch_5.pt` (55.28 MB each)
- `final_model.pt` (18.76 MB) - Active production checkpoint

**Note**: Training checkpoints are significantly larger than the final model because they include optimizer state and other training artifacts.

## Model Loading

The active ML service loads the model from:
```python
packages/ai-core/models/checkpoints_medium/final_model.pt
```

Loading logic is implemented in:
- `packages/ai-core/ml-service/main.py` (lines 215-321)

### Loading Verification

To verify checkpoint loading:
```python
import torch
checkpoint = torch.load('models/checkpoints_medium/final_model.pt', map_location='cpu')
print(f'Keys: {list(checkpoint.keys())}')
print(f'Vocab size: {len(checkpoint["tokenizer_vocab"])}')
```

Expected output:
```
Keys: ['model_state_dict', 'tokenizer_vocab', 'metrics']
Vocab size: 74
```

## Tokenizer Compatibility

**Tokenizer Implementation**: `packages/ai-core/tokenizer/tokenizer.py`  
**Tokenizer Class**: SimpleTokenizer  
**Type**: Word-level (whitespace-based)  
**Special Tokens**: PAD (0), UNK (1), BOS (2), EOS (3)

**Current Limitations**:
- 74-token vocabulary is critically small for bilingual use
- Word-level tokenization is inadequate for Bengali morphology
- Subword tokenization required for better quality

## Checkpoint Migration

**Important**: The current checkpoint is tied to the 74-token SimpleTokenizer. To migrate to a larger vocabulary or subword tokenizer:

1. Train new tokenizer on larger dataset
2. Retrain model with new tokenizer
3. Save new checkpoint to new directory (e.g., `checkpoints_v2.0.0/`)
4. Update `ml-service/main.py` to load new checkpoint
5. Verify compatibility before switching production

**Do Not**:
- Replace the active checkpoint without verification
- Modify checkpoint contents directly
- Use a checkpoint with incompatible tokenizer

## Current Limitations

1. **Small Vocabulary**: 74 tokens cannot represent meaningful Bengali or English vocabulary
2. **Limited Training Data**: Trained on only 19 samples
3. **Poor Generation Quality**: Model produces incoherent, repetitive output
4. **Word-Level Tokenization**: Inadequate for Bengali and mixed-language text
5. **No EOS Handling**: Generation does not check for EOS token

For detailed architecture and runtime information, see:
- `../RUNTIME_ARCHITECTURE.md`
- `../CHECKPOINT_COMPATIBILITY.md`

## Safe Replacement Rules

When replacing the production checkpoint:

1. Verify new checkpoint structure (must contain model_state_dict)
2. Verify tokenizer compatibility (vocab_size must match embedding dimensions)
3. Keep old checkpoint as backup (rename with version suffix)
4. Update checkpoint path in `ml-service/main.py`
5. Test loading before deploying
6. Document the change in this README

## Known Issues

- Training checkpoints (55.28 MB each) are much larger than final model (18.76 MB)
- No version metadata in checkpoint files
- No dataset provenance tracking in checkpoint
- No Git LFS configured (all checkpoints tracked directly in Git)

## License

Model checkpoints are part of the NexusAI project. Verify licensing before redistribution or commercial use.
