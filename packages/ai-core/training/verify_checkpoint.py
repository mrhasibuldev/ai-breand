"""
Checkpoint Verification for Real Data Training

This script verifies that the new checkpoint can be loaded.
"""

import torch
import json
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer.tokenizer import SimpleTokenizer
from neural.small_transformer import SmallTransformer

def main():
    print("=== Checkpoint Verification ===\n")

    CHECKPOINT_DIR = "../../../models/checkpoints/real_data_run"
    CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "checkpoint_epoch_2.pt")
    SUMMARY_FILE = os.path.join(CHECKPOINT_DIR, "training_summary.json")

    # Check checkpoint exists
    abs_checkpoint_file = os.path.abspath(CHECKPOINT_FILE)
    if not os.path.exists(abs_checkpoint_file):
        print(f"ERROR: Checkpoint not found at {abs_checkpoint_file}")
        return 1

    print(f"Checkpoint file: {abs_checkpoint_file}")

    # Load training summary
    abs_summary_file = os.path.abspath(SUMMARY_FILE)
    if os.path.exists(abs_summary_file):
        with open(abs_summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        print(f"\nTraining Summary:")
        print(f"  Data source: {summary.get('data_source')}")
        print(f"  Original dataset: {summary.get('original_dataset')}")
        print(f"  Trained on real data: {summary.get('trained_on_real_data')}")
        print(f"  Model parameters: {summary.get('model_parameters')}")
        print(f"  Vocabulary size: {summary.get('vocab_size')}")
        print(f"  Final train loss: {summary.get('final_train_loss'):.4f}")
        print(f"  Final val loss: {summary.get('final_val_loss'):.4f}")
    else:
        print(f"WARNING: Training summary not found at {abs_summary_file}")

    # Load checkpoint
    print(f"\nLoading checkpoint...")
    try:
        checkpoint = torch.load(abs_checkpoint_file, map_location='cpu')
        print(f"[OK] Checkpoint loaded successfully")
        print(f"  Keys in checkpoint: {list(checkpoint.keys())}")
    except Exception as e:
        print(f"ERROR: Failed to load checkpoint: {e}")
        return 1

    # Reconstruct model
    print(f"\nReconstructing model...")
    try:
        vocab_size = summary.get('vocab_size', 5000)
        model = SmallTransformer(
            vocab_size=vocab_size,
            d_model=128,
            n_heads=4,
            n_layers=4,
            d_ff=512,
            max_len=256
        )
        print(f"[OK] Model reconstructed (parameters: {model.count_parameters()})")
    except Exception as e:
        print(f"ERROR: Failed to reconstruct model: {e}")
        return 1

    # Load state dict
    print(f"\nLoading state dict...")
    try:
        model.load_state_dict(checkpoint['model_state_dict'])
        print(f"[OK] State dict loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to load state dict: {e}")
        return 1

    # Set model to eval mode
    model.eval()

    # Verify model can process input tensors
    print(f"\n=== Basic Forward Pass Test ===")
    try:
        # Create dummy input
        dummy_input = torch.randint(0, vocab_size, (1, 10))
        output = model(dummy_input)
        print(f"[OK] Forward pass successful")
        print(f"  Input shape: {dummy_input.shape}")
        print(f"  Output shape: {output.shape}")
    except Exception as e:
        print(f"ERROR: Forward pass failed: {e}")
        return 1

    print(f"\n=== Verification Complete ===")
    print(f"Checkpoint: {abs_checkpoint_file}")
    print(f"Status: PASS - Checkpoint loads and performs forward pass")
    print(f"\nNote: This is a basic verification only.")
    print(f"The checkpoint is NOT connected to production NexusAI inference.")
    print(f"Vocabulary preservation between training and inference needs separate handling.")

    return 0

if __name__ == "__main__":
    exit(main())
