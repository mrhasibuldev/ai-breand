"""
Inference Verification Test

Tests that the trained checkpoint can be loaded and performs inference.
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
from training.checkpoint import CheckpointManager

def main():
    print("=== Inference Verification Test ===\n")

    CHECKPOINT_DIR = "../../models/checkpoints/verification_run"
    CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, "checkpoint_epoch_2.pt")
    MAX_LEN = 256

    # Load training summary
    summary_path = os.path.join(CHECKPOINT_DIR, "training_summary.json")
    vocab_size = 124  # Default if summary fails
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        print("Training summary loaded:")
        print(f"  Epochs: {summary['epochs']}")
        print(f"  Final train loss: {summary['final_train_loss']:.4f}")
        print(f"  Final val loss: {summary['final_val_loss']:.4f}")
        print(f"  Model parameters: {summary['model_parameters']}")
        print(f"  Vocab size: {summary['vocab_size']}")
        vocab_size = summary['vocab_size']
        print()
    except Exception as e:
        print(f"WARNING: Could not load training summary: {e}")
        print(f"Using default vocab size: {vocab_size}")

    # Initialize tokenizer
    print("Initializing tokenizer...")
    try:
        tokenizer = SimpleTokenizer(vocab_size=vocab_size)
        # Build minimal vocab for test with same vocab size
        test_texts = [
            "Machine learning is a field of artificial intelligence",
            "Neural networks are computing systems inspired by brains"
        ]
        tokenizer.build_vocab(test_texts, min_freq=1)
        print(f"[OK] Tokenizer initialized (vocab size: {tokenizer.get_vocab_size()})")
    except Exception as e:
        print(f"ERROR: Failed to initialize tokenizer: {e}")
        return 1

    # Initialize model
    print("\nInitializing model...")
    try:
        model = SmallTransformer(
            vocab_size=vocab_size,
            d_model=128,
            n_heads=4,
            n_layers=4,
            d_ff=512,
            max_len=MAX_LEN
        )
        print(f"[OK] Model initialized (parameters: {model.count_parameters()})")
    except Exception as e:
        print(f"ERROR: Failed to initialize model: {e}")
        return 1

    # Load checkpoint
    print(f"\nLoading checkpoint from {CHECKPOINT_PATH}...")
    try:
        checkpoint_manager = CheckpointManager(CHECKPOINT_DIR)
        metadata = checkpoint_manager.load(CHECKPOINT_PATH, model)
        print(f"[OK] Checkpoint loaded successfully")
        print(f"  Epoch: {metadata['epoch']}")
        print(f"  Loss: {metadata['loss']:.4f}")
    except Exception as e:
        print(f"ERROR: Failed to load checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test inference
    print("\n=== Testing Inference ===")
    test_prompts = [
        "Machine learning",
        "Artificial intelligence",
        "Neural networks"
    ]

    model.eval()
    print(f"Model set to evaluation mode")

    try:
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\nTest {i}: '{prompt}'")
            try:
                # Encode prompt
                prompt_ids = tokenizer.encode(prompt, add_special_tokens=True)
                print(f"  Encoded to {len(prompt_ids)} tokens")

                # Simple forward pass
                with torch.no_grad():
                    input_tensor = torch.tensor([prompt_ids], dtype=torch.long)
                    output = model(input_tensor)

                # Verify output shape
                print(f"  Output shape: {output.shape}")
                print(f"  [OK] Forward pass executed without error")

            except Exception as e:
                print(f"  ERROR: Inference failed: {e}")
                import traceback
                traceback.print_exc()
                return 1

        print("\n=== Inference Verification Complete ===")
        print("[OK] All inference tests passed")
        print("[OK] Checkpoint loads successfully")
        print("[OK] Model forward pass works")
        print("[OK] No runtime errors")

        return 0

    except Exception as e:
        print(f"\nERROR: Inference test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
