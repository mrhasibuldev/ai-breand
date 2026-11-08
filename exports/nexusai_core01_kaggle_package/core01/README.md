# NexusAI Core-01

**NexusAI Core-01: Independent Transformer Language Model**

Built from scratch for NexusAI.

## Model Status

- **Model Name**: nexusai-core-01
- **Model Family**: NexusAI Core Series
- **Architecture**: Independent Transformer Language Model
- **Origin**: Built from scratch for NexusAI
- **Current Status**: UNTRAINED - RANDOMLY INITIALIZED
- **Training Status**: NOT STARTED
- **Pretraining Status**: NOT COMPLETED
- **Instruction Tuning Status**: NOT COMPLETED
- **Production Status**: NOT READY

## Architecture

- **Type**: Decoder-only Transformer
- **Parameters**: ~10M (target)
- **Embedding Dimension**: 256
- **Transformer Layers**: 6
- **Attention Heads**: 8
- **Feed-Forward Dimension**: 1024
- **Context Length**: 512 tokens
- **Vocabulary**: 8,000 (compatible with existing BPE tokenizer)

## Components

### Configuration
- `config/model_config.py` - Centralized model configuration

### Neural Network
- `transformer.py` - Core Transformer architecture

### Tokenizer
- `tokenizer_interface.py` - Tokenizer wrapper and compatibility checks

### Dataset
- `dataset.py` - Dataset loading, validation, and preprocessing

### Training
- `training.py` - Pretraining and instruction fine-tuning engines

### Inference
- `inference.py` - Text generation engine with model state warnings

### Evaluation
- `evaluation.py` - Model evaluation and testing framework

## Important Notes

1. **This model is NOT trained** - It has randomly initialized weights
2. **This model is NOT intelligent** - Intelligence will be developed through future training
3. **This model is NOT production-ready** - Training and evaluation must be completed first
4. **The legacy model is preserved** - Old checkpoints remain in `packages/ai-core/models/checkpoints_medium/`

## Usage

### Initialize Model

```python
# Add packages/ai-core and packages/ai-core/models to sys.path first
from core01 import NexusAICore01
from nexusai_core_01.config import NexusAICore01Config

config = NexusAICore01Config()
model = NexusAICore01(config)

print(f"Parameters: {model.count_parameters():,}")
print(f"Status: {config.model_status.value}")
```

### Create Inference Engine

```python
from core01 import create_inference_engine

engine = create_inference_engine(config, device="cpu")

# Generation will return warning for untrained model
result = engine.generate("What is your name?")
print(result)
```

### Run Evaluation Tests

```python
from core01 import ModelEvaluator

evaluator = ModelEvaluator(config)
results = evaluator.run_all_tests()
print(results["summary"])
```

## Training (Future)

Training infrastructure is implemented but NOT executed. Training will require:
1. Expanded dataset (50-100M tokens)
2. GPU hardware
3. Owner approval

## Checkpoint Management

Checkpoints are stored in:
- `packages/ai-core/models/nexusai_core_01/checkpoints/`

Separate from legacy model checkpoints in:
- `packages/ai-core/models/checkpoints_medium/`

## Documentation

See:
- PHASE 0 Audit: `docs/architecture/audits/NEXUSAI_PHASE0_INDEPENDENT_MODEL_CREATION_READINESS_AUDIT.md`
- Strategic Research: `docs/architecture/audits/NEXUSAI_2050_FUTURE_AI_BRAIN_STRATEGIC_RESEARCH.md`
