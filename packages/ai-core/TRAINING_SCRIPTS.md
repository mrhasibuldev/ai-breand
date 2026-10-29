# NexusAI Training Scripts

This document describes the training scripts in the NexusAI ai-core package.

## Active Training Script

### train_medium_model.py

**Status**: CANONICAL - This script produced the current production checkpoint  
**Purpose**: Trains the MediumTransformer model  
**Checkpoint Produced**: `models/checkpoints_medium/final_model.pt`  
**Training Data**: `data/public_datasets/v1.0_cleaned/train_cleaned.json` (19 samples)  
**Model Architecture**: MediumTransformer (d_model=256, n_layers=6, n_heads=8, d_ff=1024, max_len=512)  
**Vocabulary Size**: 74 tokens (SimpleTokenizer)  
**Training Epochs**: 5  
**Output**: Training checkpoints in `models/checkpoints_medium/`

**Usage**:
```bash
cd packages/ai-core
python train_medium_model.py
```

**Note**: This is the script that produced the current production model (final_model.pt).

## Experimental Training Scripts

### train_with_v2.py

**Status**: EXPERIMENTAL - Not used for production  
**Purpose**: Trains MediumTransformer with conversational dataset (train_v2.json)  
**Training Data**: `data/train_v2.json` (502 conversations)  
**Note**: This script uses a larger dataset but has not been verified for license compliance. DO NOT use for production until license is verified.

### retrain_model.py

**Status**: LEGACY - For SmallTransformer only  
**Purpose**: Retrains SmallTransformer with expanded dataset  
**Model Architecture**: SmallTransformer (d_model=64, n_layers=2, n_heads=2, d_ff=256, max_len=128)  
**Training Data**: `data/train_final.json`  
**Checkpoint Produced**: `models/checkpoints/`  
**Note**: This script is for the legacy SmallTransformer model, not the current production MediumTransformer.

## Training Infrastructure

### training/ Module

**Location**: `packages/ai-core/training/`  
**Contents**:
- `__init__.py` - Module initialization
- `checkpoint.py` - Checkpoint saving/loading utilities
- `dataset.py` - Dataset classes (TextDataset, load_json_dataset)
- `pipeline.py` - TrainingPipeline class
- `validator.py` - Training validation utilities

**Status**: STABLE - Used by training scripts

## Canonical vs Experimental vs Legacy

**Canonical**: `train_medium_model.py` - Use this for training the production MediumTransformer

**Experimental**: `train_with_v2.py` - For research only, not for production until license verified

**Legacy**: `retrain_model.py` - For SmallTransformer (legacy model), not for current production

## Important Notes

1. **Do NOT train** on datasets with unverified licenses
2. **Do NOT use** `train_with_v2.py` for production until `train_v2.json` license is verified
3. **Do NOT delete** training scripts - they may be useful for future research
4. **Current production checkpoint** was produced by `train_medium_model.py` with 19 samples
5. **Future training** should use licensed datasets following the framework in Stage B4-B1

## Training Guidelines

Before running any training script:

1. Verify dataset license permits commercial use
2. Verify dataset license permits redistribution
3. Document dataset provenance
4. Use the canonical script unless there is a specific reason to use experimental scripts
5. Backup existing checkpoints before training
6. Monitor disk space (training checkpoints can be large)

## Training Script Inventory

| Script | Model | Status | Data | Checkpoint |
|--------|-------|--------|------|------------|
| train_medium_model.py | MediumTransformer | CANONICAL | v1.0_cleaned (19 samples) | checkpoints_medium/final_model.pt |
| train_with_v2.py | MediumTransformer | EXPERIMENTAL | train_v2.json (502 conv) | Not verified |
| retrain_model.py | SmallTransformer | LEGACY | train_final.json | checkpoints/ |

---

**Last Updated**: Phase 1C - Architecture Stabilization
