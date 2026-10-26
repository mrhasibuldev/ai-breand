"""
Model Architecture Comparison Test
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from neural.transformer import SmallTransformer
from neural.medium_transformer import MediumTransformer


def compare_models():
    """Compare parameter counts between Small and Medium models"""
    vocab_size = 1000
    
    print("[Model Comparison] Small vs Medium Transformer")
    print("=" * 60)
    
    # Small model (original)
    small_model = SmallTransformer(vocab_size, d_model=128, n_layers=4, n_heads=4, d_ff=512)
    small_params = small_model.count_parameters()
    
    # Medium model (upgraded)
    medium_model = MediumTransformer(vocab_size, d_model=256, n_layers=6, n_heads=8, d_ff=1024)
    medium_params = medium_model.count_parameters()
    
    print(f"\nSmall Transformer (Baseline):")
    print(f"  Parameters: {small_params:,}")
    print(f"  d_model: 128")
    print(f"  n_layers: 4")
    print(f"  n_heads: 4")
    print(f"  d_ff: 512")
    
    print(f"\nMedium Transformer (Upgraded):")
    print(f"  Parameters: {medium_params:,}")
    print(f"  d_model: 256")
    print(f"  n_layers: 6")
    print(f"  n_heads: 8")
    print(f"  d_ff: 1024")
    
    print(f"\nImprovement:")
    print(f"  Parameter increase: {medium_params / small_params:.2f}x")
    print(f"  Additional parameters: {medium_params - small_params:,}")
    
    # Test forward pass
    print(f"\n[Forward Pass Test]")
    batch_size = 2
    seq_len = 32
    
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    targets = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    # Small model
    small_loss = small_model(input_ids, targets)
    print(f"Small model loss: {small_loss.item():.4f}")
    
    # Medium model
    medium_loss = medium_model(input_ids, targets)
    print(f"Medium model loss: {medium_loss.item():.4f}")
    
    print(f"\n[OK] Both models work correctly")
    
    return {
        "small": small_params,
        "medium": medium_params,
        "ratio": medium_params / small_params
    }


if __name__ == "__main__":
    compare_models()
