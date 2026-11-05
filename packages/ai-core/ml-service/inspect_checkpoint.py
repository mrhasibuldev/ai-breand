"""
Diagnostic script to inspect the trained checkpoint and verify model architecture.
This script does not start the ML service, only inspects the checkpoint file.
"""

import torch
import json
import os

# Paths
CHECKPOINT_PATH = "models/checkpoints_medium/final_model.pt"
CONFIG_PATH = "models/production/current.json"

print("=" * 80)
print("NEXUSAI CHECKPOINT INSPECTION")
print("=" * 80)

# Load checkpoint
print(f"\nLoading checkpoint from: {CHECKPOINT_PATH}")
try:
    checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
    print("[OK] Checkpoint loaded successfully")
except Exception as e:
    print(f"[ERROR] Failed to load checkpoint: {e}")
    exit(1)

# Inspect checkpoint keys
print(f"\nCheckpoint keys: {list(checkpoint.keys())}")

# Get model config if available
if 'config' in checkpoint:
    config = checkpoint['config']
    print(f"\nModel config from checkpoint:")
    for key, value in config.items():
        print(f"  {key}: {value}")
else:
    print("\n[WARNING] No 'config' key in checkpoint")
    print("Available keys:", list(checkpoint.keys()))

# Get model state dict
if 'model_state_dict' in checkpoint:
    state_dict = checkpoint['model_state_dict']
    print(f"\nModel state dict keys: {list(state_dict.keys())[:10]}...")

    # Calculate parameters from state dict
    total_params = sum(p.numel() for p in state_dict.values())
    print(f"\nTotal parameters from state dict: {total_params:,}")
else:
    print("\n[WARNING] No 'model_state_dict' key in checkpoint")

# Try to load as a model
print("\n" + "=" * 80)
print("ATTEMPTING TO LOAD AS MODEL")
print("=" * 80)

try:
    # Import the model
    import sys
    sys.path.append("neural")
    from medium_transformer import MediumTransformer

    # Load config from checkpoint or use defaults
    if 'config' in checkpoint:
        config = checkpoint['config']
        model = MediumTransformer(
            vocab_size=config.get('vocab_size', 8000),
            d_model=config.get('d_model', 128),
            n_layers=config.get('n_layers', 2),
            n_heads=config.get('n_heads', 2),
            d_ff=config.get('d_ff', 512),
            max_len=config.get('max_len', 128)
        )
    else:
        # Use defaults that match the smaller config
        model = MediumTransformer(
            vocab_size=8000,
            d_model=128,
            n_layers=2,
            n_heads=2,
            d_ff=512,
            max_len=128
        )

    # Load state dict
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
        print("[OK] Model loaded with state dict")
    else:
        # Try loading directly
        model.load_state_dict(checkpoint)
        print("[OK] Model loaded directly")

    # Count parameters
    param_count = sum(p.numel() for p in model.parameters())
    print(f"\nModel parameters: {param_count:,}")

    # Print model architecture
    print(f"\nModel architecture:")
    print(f"  d_model: {model.d_model}")
    print(f"  n_layers: {model.n_layers}")
    print(f"  n_heads: {model.n_heads}")
    print(f"  d_ff: {model.d_ff}")
    print(f"  max_len: {model.max_len}")
    print(f"  vocab_size: {model.vocab_size}")

except Exception as e:
    print(f"[ERROR] Failed to load as model: {e}")
    import traceback
    traceback.print_exc()

# Load current.json for comparison
print("\n" + "=" * 80)
print("COMPARISON WITH current.json")
print("=" * 80)

try:
    with open(CONFIG_PATH, 'r') as f:
        current_config = json.load(f)
    print(f"\ncurrent.json parameters: {current_config.get('parameters', 'N/A')}")
    print(f"current.json dataset samples: {current_config.get('dataset_samples', 'N/A')}")
    print(f"current.json perplexity: {current_config.get('perplexity', 'N/A')}")
except Exception as e:
    print(f"[ERROR] Failed to load current.json: {e}")

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
