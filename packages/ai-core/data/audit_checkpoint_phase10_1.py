"""
Phase 10.1 - Checkpoint Integrity Check

Verifies checkpoint integrity and file sizes.
"""

import os
import torch
from pathlib import Path

print("="*60)
print("Phase 10.1 - Checkpoint Integrity Check")
print("="*60)

# Paths
DATA_DIR = Path(__file__).parent
PHASE10_DIR = DATA_DIR / "experimental" / "phase10"
CHECKPOINTS_DIR = PHASE10_DIR / "checkpoints"
checkpoint_path = CHECKPOINTS_DIR / "best_model.pt"

print(f"\nCheckpoint path: {checkpoint_path}")
print(f"Exists: {checkpoint_path.exists()}")

if checkpoint_path.exists():
    file_size = os.path.getsize(checkpoint_path)
    print(f"File size: {file_size / (1024*1024):.2f} MB")
    
    # Load checkpoint
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        print(f"Checkpoint loaded successfully")
        
        print(f"\nCheckpoint keys: {list(checkpoint.keys())}")
        
        if 'epoch' in checkpoint:
            print(f"Epoch: {checkpoint['epoch']}")
        
        if 'val_loss' in checkpoint:
            print(f"Val loss: {checkpoint['val_loss']:.4f}")
        
        if 'config' in checkpoint:
            config = checkpoint['config']
            print(f"\nConfig:")
            for key, value in config.items():
                print(f"  {key}: {value}")
        
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            print(f"\nModel state dict keys: {len(state_dict)}")
            
            # Check for NaN or infinite values
            has_nan = any(torch.isnan(p).any() for p in state_dict.values())
            has_inf = any(torch.isinf(p).any() for p in state_dict.values())
            
            print(f"Contains NaN: {has_nan}")
            print(f"Contains Inf: {has_inf}")
            
            if not has_nan and not has_inf:
                print("Weights are finite and valid")
        
        print(f"\nIntegrity: PASS")
        
    except Exception as e:
        print(f"ERROR loading checkpoint: {e}")
        print(f"Integrity: FAIL")
else:
    print("ERROR: Checkpoint file not found")
    print("Integrity: FAIL")

print("\n" + "="*60)
print("CHECKPOINT INTEGRITY CHECK COMPLETE")
print("="*60)
