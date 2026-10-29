# Checkpoint and Tokenizer Compatibility

## Active Production Checkpoint

**Path**: `models/checkpoints_medium/final_model.pt`

**Model**: MediumTransformer

**Parameters**: 4,776,522

**Architecture Config**:
- d_model: 256
- n_layers: 6
- n_heads: 8
- d_ff: 1024
- max_len: 512

**Tokenizer**: SimpleTokenizer (word-level, whitespace splitting)

**Vocabulary Size**: 74 tokens

**Vocabulary Source**: Embedded in checkpoint (`tokenizer_vocab` field)

**Special Tokens**: PAD (ID 0), UNK (ID 1), BOS (ID 2), EOS (ID 3)

## Compatibility Verification

### Model Architecture ✅ COMPATIBLE

The `MediumTransformer` class in `neural/medium_transformer.py` matches the checkpoint:
- Embedding layer shape: torch.Size([74, 256]) - matches vocab_size=74, d_model=256
- All layer dimensions match the checkpoint's model_state_dict

### Tokenizer ✅ COMPATIBLE

The ML service loads the tokenizer from the checkpoint:
```python
if "tokenizer_vocab" in checkpoint:
    tokenizer.word_to_id = checkpoint["tokenizer_vocab"]
    tokenizer.id_to_word = {int(k): v for k, v in zip(...)}
    tokenizer.is_built = True
```

This ensures the tokenizer used at inference matches the tokenizer used during training.

### Current Loading Path

**File**: `ml-service/main.py` (lines 215-288)

**Process**:
1. Load checkpoint from `models/checkpoints_medium/final_model.pt`
2. Extract vocabulary size from checkpoint (74 tokens)
3. Load tokenizer from checkpoint's `tokenizer_vocab` field
4. Initialize MediumTransformer with vocab_size=74
5. Load model weights from checkpoint's `model_state_dict`
6. Create TextGenerator with model and tokenizer

## Checkpoint Metadata

**Current Metadata** (in final_model.pt):
- model_state_dict: ✅ Present
- tokenizer_vocab: ✅ Present (74 tokens)
- metrics: ✅ Present (train_loss, val_loss, epoch history)

**Missing Metadata**:
- model_version: ❌ Missing
- architecture_config: ❌ Missing
- dataset_version: ❌ Missing
- training_run_id: ❌ Missing
- git_commit: ❌ Missing

## Known Limitations

### 74-Token Vocabulary

The 74-token vocabulary is **critically small** for bilingual English-Bengali use:
- Cannot represent meaningful Bengali vocabulary
- Cannot represent meaningful English vocabulary
- Most words map to UNK token
- This is a primary cause of poor generation quality

### Tokenizer Type

The SimpleTokenizer uses word-level whitespace splitting:
- Bengali Unicode is preserved but not handled specially
- Punctuation is not separated from words
- No subword tokenization
- Poor morphological handling for Bengali

## Legacy Checkpoints

**SmallTransformer Checkpoints** (`models/checkpoints/`):
- checkpoint_epoch_1.pt through checkpoint_epoch_5.pt
- 597-token vocabulary
- 1,050,088 parameters
- Used only as fallback if MediumTransformer fails
- Status: LEGACY (not active)

## Migration Path

When expanding vocabulary or changing tokenizer:

1. **Backup current checkpoint** - Copy final_model.pt to backup location
2. **Train new tokenizer** - Build larger vocabulary from cleaned dataset
3. **Retrain model** - Train with new tokenizer
4. **Save with metadata** - Include full metadata in new checkpoint
5. **Update production** - Point ML service to new checkpoint
6. **Keep old checkpoint** - Preserve for rollback capability

## Checkpoint Validation

To validate checkpoint compatibility:

```python
import torch

checkpoint = torch.load('models/checkpoints_medium/final_model.pt', map_location='cpu')

# Check vocabulary size
vocab_size = len(checkpoint['tokenizer_vocab'])
print(f"Vocabulary size: {vocab_size}")

# Check embedding layer
embedding_shape = checkpoint['model_state_dict']['token_embedding.embedding.weight'].shape
print(f"Embedding shape: {embedding_shape}")

# Verify architecture compatibility
assert embedding_shape[0] == vocab_size, "Vocabulary size mismatch"
```

---

**Last Updated**: Phase 1C - Architecture Stabilization
