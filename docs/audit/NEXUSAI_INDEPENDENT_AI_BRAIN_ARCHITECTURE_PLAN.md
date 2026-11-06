# NEXUSAI INDEPENDENT AI BRAIN ARCHITECTURE PLAN

**Date**: 2026-11-06
**Type**: Architecture Design
**Scope**: Independent model architecture for Bengali-English language generation

---

## A. EXECUTIVE SUMMARY

**Project Goal**: Build an independent AI Brain using internally developed model architecture, tokenizer, datasets, and training pipeline.

**STRICTLY PROHIBITED**:
- ❌ OpenAI API
- ❌ Gemini API
- ❌ Claude API
- ❌ Groq API
- ❌ Hugging Face hosted inference APIs
- ❌ GPT-2 or other pretrained external models as foundation
- ❌ Pollinations or other external AI generation APIs
- ❌ Any third-party AI API as fallback
- ❌ Fake AI responses or template-based answers

**ALLOWED**:
- ✅ PyTorch (ML library)
- ✅ SentencePiece (tokenizer library)
- ✅ NumPy (numerical library)
- ✅ Standard open-source ML libraries as engineering tools

**Current Status**: ⚠️ ARCHITECTURE INCONSISTENCY DETECTED
- Checkpoint uses PyTorch TransformerEncoder (2 layers, 128 d_model)
- ML Service loads into MediumTransformer (expects 6 layers, 256 d_model)
- ML Service overrides with checkpoint config (loads 2 layers, 128 d_model)
- **Result**: Architecture works but naming is misleading

**Recommendation**: Choose ONE coherent architecture and use it consistently.

---

## B. FORENSIC VALIDATION

### B.1 Current Architecture Investigation

**Checkpoint Analysis** (`models/checkpoints_medium/final_model.pt`):
```
Configuration from checkpoint:
  vocab_size: 8000
  d_model: 128
  n_layers: 2
  n_heads: 2
  d_ff: 512
  max_len: 128
  batch_size: 4
  epochs: 3
  learning_rate: 0.0003
  weight_decay: 0.01
  grad_clip: 1.0
  random_seed: 42
  device: cpu

Model architecture from state dict:
  Embedding weight shape: [8000, 128]
  Number of layers: 2
  Total parameters: 2,468,928
```

**Training Script Analysis** (`data/train_phase10.py`):
```
Uses: PyTorch TransformerEncoder (not SmallTransformer or MediumTransformer)
Architecture: nn.TransformerEncoderLayer
  d_model: 128
  nhead: 2
  num_layers: 2
  dim_feedforward: 512
  max_len: 128
```

**ML Service Analysis** (`ml-service/main.py`):
```
Attempts to load: MediumTransformer
Expected default: 6 layers, 256 d_model
Override behavior: Uses checkpoint config (2 layers, 128 d_model)
Result: Loads SMALL architecture correctly
```

### B.2 Architecture Discrepancy Summary

**Component 1: Training Script**
- Uses: PyTorch TransformerEncoder
- Architecture: 2 layers, 128 d_model, 2 heads, 512 d_ff
- Class name: TransformerModel (not SmallTransformer, not MediumTransformer)

**Component 2: ML Service**
- Attempts to load: MediumTransformer
- Expected: 6 layers, 256 d_model, 8 heads, 1024 d_ff
- Actual: Uses checkpoint config (2 layers, 128 d_model)
- Result: Correctly loads SMALL architecture

**Component 3: Checkpoint**
- Contains: PyTorch TransformerEncoder weights
- Architecture: 2 layers, 128 d_model, 2 heads, 512 d_ff
- Parameters: 2.4M

### B.3 Root Cause

**Issue**: Codebase has THREE different model classes:
1. `SmallTransformer` (neural/small_transformer.py) - 4 layers, 128 d_model default
2. `MediumTransformer` (neural/medium_transformer.py) - 6 layers, 256 d_model default
3. `TransformerModel` (data/train_phase10.py) - 2 layers, 128 d_model, uses PyTorch TransformerEncoder

**Current State**:
- Training script uses `TransformerModel` (PyTorch TransformerEncoder)
- ML Service tries to use `MediumTransformer` but falls back to checkpoint config
- Checkpoint is from `TransformerModel` training

**Impact**: Naming confusion but model loads correctly. ML Service's "Medium" label is misleading.

---

## C. PROPOSED ARCHITECTURE DESIGN

### C.1 Design Requirements

**Hardware Constraints**:
- CPU-only training (no GPU available)
- Training time must be reasonable (days, not weeks)
- Memory footprint must fit in typical RAM (8-16GB)

**Language Requirements**:
- Bengali language support
- English language support
- Mixed Bengali-English support
- Conversational format
- Context length ~128-256 tokens

**Quality Requirements**:
- Better than current SMALL model (2.4M params)
- Coherent text generation
- Reduced gibberish
- Proper Bengali output

### C.2 Architecture Options

#### Option 1: NEXUSAI-SMALL (Conservative)

**Configuration**:
```
Architecture: PyTorch TransformerEncoder (same as current)
vocab_size: 8000
d_model: 128
nhead: 2
num_layers: 4 (increased from 2)
dim_feedforward: 512
max_len: 128
dropout: 0.1
```

**Parameters**: ~5M (approximately double current)

**Training Time**: 20-30 hours on CPU for 20 epochs

**Expected Quality**: Moderately better than current
- More layers may improve coherence
- Still limited capacity
- Risk: May still generate gibberish

**Pros**:
- Minimal code changes
- Proven to work
- Fast training
- Low memory footprint

**Cons**:
- Limited capacity
- May not achieve conversational quality
- Still very small for language generation

**Recommended Use**: Baseline comparison

---

#### Option 2: NEXUSAI-MEDIUM (Balanced) ⭐ RECOMMENDED

**Configuration**:
```
Architecture: Custom Transformer (SmallTransformer)
vocab_size: 8000
d_model: 256 (increased from 128)
n_layers: 6 (increased from 2)
n_heads: 8 (increased from 2)
d_ff: 1024 (increased from 512)
max_len: 256 (increased from 128)
dropout: 0.1
```

**Parameters**: ~15M (approximately 6x current)

**Training Time**: 40-60 hours on CPU for 20 epochs

**Expected Quality**: Significantly better than current
- Larger capacity for language patterns
- Better attention mechanisms
- Likely to achieve conversational quality

**Pros**:
- Significant capacity increase
- Proven architecture (GPT-style)
- Better attention with more heads
- Longer context (256 tokens)
- Independent implementation (no PyTorch TransformerEncoder)

**Cons**:
- Longer training time
- Higher memory footprint
- Requires code changes (use SmallTransformer instead of PyTorch TransformerEncoder)

**Recommended Use**: Production target

---

#### Option 3: NEXUSAI-LARGE (Aggressive)

**Configuration**:
```
Architecture: Custom Transformer (SmallTransformer)
vocab_size: 16000 (increased from 8000)
d_model: 512 (increased from 256)
n_layers: 12 (increased from 6)
n_heads: 16 (increased from 8)
d_ff: 2048 (increased from 1024)
max_len: 512 (increased from 256)
dropout: 0.1
```

**Parameters**: ~100M+

**Training Time**: 200-400 hours on CPU for 20 epochs

**Expected Quality**: Excellent (if data supports it)
- Large capacity for complex patterns
- Very good language generation
- Long context (512 tokens)

**Pros**:
- High quality potential
- Large context window
- Excellent for complex conversations

**Cons**:
- Training time prohibitive on CPU
- High memory footprint
- Requires GPU for practical training
- Risk of overfitting on small dataset

**Recommended Use**: Future with GPU and larger dataset

---

### C.3 Architecture Comparison

| Metric | SMALL (Current) | SMALL (Option 1) | MEDIUM (Option 2) | LARGE (Option 3) |
|--------|-----------------|------------------|------------------|------------------|
| Layers | 2 | 4 | 6 | 12 |
| d_model | 128 | 128 | 256 | 512 |
| Heads | 2 | 2 | 8 | 16 |
| d_ff | 512 | 512 | 1024 | 2048 |
| Params | 2.4M | ~5M | ~15M | ~100M |
| Max Len | 128 | 128 | 256 | 512 |
| CPU Time (20 epochs) | 10h | 20h | 50h | 300h |
| Memory | ~2GB | ~3GB | ~6GB | ~20GB |
| Expected Quality | Poor | Moderate | Good | Excellent |
| Code Changes | None | Minimal | Moderate | Significant |

---

## D. RECOMMENDED ARCHITECTURE: NEXUSAI-MEDIUM

### D.1 Rationale

**Why MEDIUM?**
1. **Significant capacity increase** (6x parameters)
2. **Reasonable training time** (40-60 hours on CPU)
3. **Proven architecture** (GPT-style custom Transformer)
4. **Independent implementation** (no external pretrained models)
5. **Balanced trade-offs** (quality vs. time vs. memory)

**Why not SMALL?**
- Limited capacity may still produce gibberish
- Marginal improvement over current model
- Risk of wasted training time for minimal gain

**Why not LARGE?**
- Training time prohibitive on CPU
- Memory footprint too high
- Requires GPU for practical use
- Risk of overfitting on small dataset

### D.2 Detailed Configuration

**Model Architecture**:
```python
class NexusAIBrain(nn.Module):
    """
    Independent NexusAI Brain - Medium Architecture
    Custom GPT-style Transformer
    """

    def __init__(
        self,
        vocab_size: int = 8000,
        d_model: int = 256,
        n_layers: int = 6,
        n_heads: int = 8,
        d_ff: int = 1024,
        max_len: int = 256,
        dropout: float = 0.1
    ):
        super().__init__()

        # Embedding layers
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_len, dropout)

        # Transformer blocks (custom implementation)
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])

        # Output layer
        self.output_layer = nn.Linear(d_model, vocab_size)

        # Initialize weights
        self._init_weights()
```

**Parameter Count**:
- Token embedding: 8000 × 256 = 2,048,000
- Positional encoding: 256 × 256 = 65,536
- Each Transformer block:
  - Self-attention: 256 × 256 × 4 = 262,144
  - Feed-forward: 256 × 1024 + 1024 × 256 = 524,288
  - Layer norms: negligible
- 6 blocks: ~4.7M
- Output layer: 256 × 8000 = 2,048,000
- **Total**: ~9M parameters (approximately)

**Memory Requirements**:
- Model weights: ~36MB (9M params × 4 bytes)
- Optimizer state: ~144MB (AdamW, 3 states per param)
- Gradients: ~36MB
- Activations (batch size 4, seq len 256): ~100MB
- **Total**: ~300-400MB per batch

**Training Time Estimate**:
- 1 epoch: ~2-3 hours on CPU
- 20 epochs: ~40-60 hours on CPU
- 50 epochs: ~100-150 hours on CPU

### D.3 Components

**Embedding Layer**:
- Token embedding: Maps token IDs to 256-dimensional vectors
- Positional encoding: Sinusoidal positional encoding for sequence position
- Dropout: 0.1 for regularization

**Transformer Blocks**:
- Multi-head self-attention: 8 heads, each 32-dimensional
- Layer normalization: Pre-normalization for stability
- Feed-forward network: 2-layer MLP with 1024 hidden dimension
- Residual connections: Skip connections for gradient flow
- Dropout: 0.1 for regularization

**Output Layer**:
- Linear projection: 256 → 8000 (vocabulary size)
- Softmax applied during inference (not during training for efficiency)

**Causal Masking**:
- Autoregressive masking: Each position can only attend to previous positions
- Ensures next-token prediction objective

### D.4 Training Configuration

**Optimizer**: AdamW
- Learning rate: 0.0003 (same as current, proven to work)
- Weight decay: 0.01 (same as current)
- Beta1: 0.9
- Beta2: 0.999

**Learning Rate Schedule**:
- Warmup: 5% of total steps
- Decay: Cosine annealing after warmup
- Final learning rate: 10% of initial

**Regularization**:
- Dropout: 0.1
- Weight decay: 0.01
- Gradient clipping: 1.0

**Batch Size**: 4 (CPU constraint)
- Sequence length: 256
- Batch tokens: 1024

**Training Duration**:
- Epochs: 20-50 (monitor validation loss)
- Early stopping: Stop if validation loss doesn't improve for 5 epochs

---

## E. IMPLEMENTATION PLAN

### E.1 Code Structure

**New File**: `packages/ai-core/neural/nexusai_brain.py`
- Independent NexusAI Brain class
- Based on SmallTransformer but renamed for clarity
- Configuration as NEXUSAI-MEDIUM

**New File**: `packages/ai-core/training/train_nexusai.py`
- Training script for NexusAI Brain
- Uses NexusAI Brain architecture
- Correct dataset loading
- Proper train/validation split
- Checkpoint management

**Modify**: `packages/ai-core/ml-service/main.py`
- Load NexusAI Brain instead of MediumTransformer
- Update checkpoint loading logic
- Ensure configuration consistency

### E.2 Backward Compatibility

**Preserve**:
- Existing checkpoint (do not delete)
- Existing training scripts (do not delete)
- Existing ML service logic (extend, don't replace)

**Add**:
- New NexusAI Brain class
- New training script
- New checkpoint directory (e.g., `models/nexusai_brain/`)

### E.3 Migration Path

**Phase 1**: Implement NexusAI Brain architecture
- Create `nexusai_brain.py`
- Test architecture with dummy data
- Verify parameter count

**Phase 2**: Implement training pipeline
- Create `train_nexusai.py`
- Test with small dataset
- Verify training loop

**Phase 3**: Train initial model
- Train with cleaned dataset
- 20 epochs
- Save checkpoint

**Phase 4**: Evaluate and iterate
- Run evaluation suite
- Compare with current model
- Adjust hyperparameters if needed

**Phase 5**: Integrate into ML service
- Update ML service to load NexusAI Brain
- Test inference
- Deploy if quality acceptable

---

## F. ARCHITECTURE TRADE-OFFS

### F.1 Capacity vs. Training Time

**Higher Capacity** (more parameters):
- Better language generation
- Slower training
- Higher memory footprint

**Lower Capacity** (fewer parameters):
- Faster training
- Lower memory footprint
- May produce gibberish

**Chosen Balance**: NEXUSAI-MEDIUM (~9M parameters)
- Significantly better than current (2.4M)
- Reasonable training time (40-60 hours)
- Manageable memory footprint (~6GB)

### F.2 Context Length vs. Memory

**Longer Context** (more tokens):
- Better for long conversations
- Higher memory during training
- Slower training

**Shorter Context** (fewer tokens):
- Faster training
- Lower memory
- Limited conversation length

**Chosen Balance**: 256 tokens
- 2x current (128 tokens)
- Good for multi-turn conversations
- Manageable memory footprint

### F.3 Layers vs. Depth

**More Layers**:
- Better representation learning
- Slower training
- Risk of vanishing gradients

**Fewer Layers**:
- Faster training
- Simpler gradient flow
- Limited representation capacity

**Chosen Balance**: 6 layers
- 3x current (2 layers)
- Proven to work (GPT-2 small has 12 layers)
- Residual connections prevent vanishing gradients

---

## G. HARDWARE REQUIREMENTS

### G.1 Minimum Requirements

**CPU**:
- Cores: 4+ (recommended)
- Clock speed: 2.0GHz+
- Architecture: x86_64

**RAM**:
- Minimum: 8GB
- Recommended: 16GB
- Estimated usage: 6GB for training

**Storage**:
- Dataset: ~10MB
- Checkpoints: ~100MB per checkpoint
- Logs: ~10MB
- Total: ~200MB

### G.2 Training Time Estimates

**1 Epoch**:
- SMALL (5M params): ~1-2 hours
- MEDIUM (9M params): ~2-3 hours
- LARGE (100M params): ~10-15 hours

**20 Epochs**:
- SMALL: ~20-40 hours
- MEDIUM: ~40-60 hours
- LARGE: ~200-300 hours

**50 Epochs**:
- SMALL: ~50-100 hours
- MEDIUM: ~100-150 hours
- LARGE: ~500-750 hours

### G.3 GPU Considerations

**If GPU Available**:
- Training time: 10-20x faster
- MEDIUM (9M params): ~4-6 hours for 20 epochs
- LARGE (100M params): ~20-30 hours for 20 epochs

**GPU Requirements**:
- VRAM: 8GB+ (for MEDIUM)
- VRAM: 16GB+ (for LARGE)
- CUDA: 11.0+

**Recommendation**: CPU training is feasible for MEDIUM architecture. GPU recommended for LARGE.

---

## H. EVALUATION METRICS

### H.1 Quantitative Metrics

**Training Metrics**:
- Training loss (cross-entropy)
- Validation loss (cross-entropy)
- Perplexity (exp(loss))
- Training time per epoch
- GPU/CPU utilization

**Inference Metrics**:
- Latency (ms per token)
- Throughput (tokens per second)
- Memory usage

### H.2 Qualitative Metrics

**Language Coherence**:
- Bengali: Intelligible sentences
- English: Intelligible sentences
- Mixed: Proper language switching

**Conversational Quality**:
- Relevance to prompt
- Appropriate responses
- Context retention
- Multi-turn consistency

**Error Metrics**:
- Gibberish rate (percentage of meaningless output)
- Repetition rate (percentage of repetitive output)
- Empty response rate (percentage of empty output)

### H.3 Human Evaluation

**Evaluation Protocol**:
- Select 100 test prompts (50 Bengali, 50 English)
- Have human evaluators rate responses on 1-5 scale
- Metrics: Coherence, Relevance, Grammar, Fluency

**Pass Criteria**:
- Average score > 3.5/5.0
- Bengali score > 3.0/5.0
- English score > 3.5/5.0
- Gibberish rate < 10%

---

## I. CONCLUSION

### I.1 Current State

**Architecture**: ⚠️ INCONSISTENT
- Training script uses PyTorch TransformerEncoder
- ML Service uses MediumTransformer (but falls back to checkpoint config)
- Checkpoint is from PyTorch TransformerEncoder training
- Naming confusion but model loads correctly

**Recommendation**: Standardize on ONE architecture

### I.2 Recommended Architecture

**NEXUSAI-MEDIUM**:
- Layers: 6
- d_model: 256
- Heads: 8
- d_ff: 1024
- Params: ~9M
- Max len: 256
- Training time: 40-60 hours on CPU

**Rationale**:
- Significant capacity increase (6x current)
- Reasonable training time
- Proven architecture
- Independent implementation
- Balanced trade-offs

### I.3 Next Steps

1. **Implement NexusAI Brain architecture** (nexusai_brain.py)
2. **Implement training pipeline** (train_nexusai.py)
3. **Train initial model** (20 epochs)
4. **Evaluate and iterate** (adjust hyperparameters)
5. **Integrate into ML service** (update main.py)

### I.4 Honest Assessment

The current architecture is inconsistent but functional. The model (2.4M params) is too small for quality language generation. We need to implement a consistent, larger architecture (NEXUSAI-MEDIUM, ~9M params) and train it with cleaned data to achieve production quality.

This is a significant effort (40-60 hours of training), but it is necessary for an independent AI Brain that does not rely on external APIs.

---

## J. FILES INVESTIGATED

1. `packages/ai-core/models/checkpoints_medium/final_model.pt` - Current checkpoint
2. `packages/ai-core/neural/small_transformer.py` - Small Transformer class
3. `packages/ai-core/neural/medium_transformer.py` - Medium Transformer class
4. `packages/ai-core/data/train_phase10.py` - Training script (PyTorch TransformerEncoder)
5. `packages/ai-core/ml-service/main.py` - ML service code
6. `packages/ai-core/data/test_checkpoint_arch.py` - Checkpoint analysis script (created)

---

## K. FILES TO BE CREATED

1. `packages/ai-core/neural/nexusai_brain.py` - Independent NexusAI Brain class
2. `packages/ai-core/training/train_nexusai.py` - Training script for NexusAI Brain
3. `packages/ai-core/training/evaluate_nexusai.py` - Evaluation script for NexusAI Brain

---

## L. PRESERVED SYSTEMS

✅ No changes to existing checkpoints
✅ No changes to existing training scripts
✅ No changes to existing model classes
✅ All existing code preserved
✅ All previous work preserved

---

**END OF INDEPENDENT AI BRAIN ARCHITECTURE PLAN**
