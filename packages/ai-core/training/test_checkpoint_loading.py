"""
Test script to verify Phase 1 checkpoint loading
"""

import torch
import os
import sys
import sentencepiece as spm

# Add paths
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ai_core_dir)

from neural.medium_transformer import MediumTransformer

# Paths
checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")
tokenizer_path = os.path.join(ai_core_dir, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")

print(f"[Test] Loading checkpoint from {checkpoint_path}")
print(f"[Test] Loading tokenizer from {tokenizer_path}")

# Load checkpoint
checkpoint = torch.load(checkpoint_path, map_location="cpu")
print(f"[Test] Checkpoint keys: {checkpoint.keys()}")

# Load config
config = checkpoint["config"]
print(f"[Test] Config: {config}")

# Load tokenizer
tokenizer = spm.SentencePieceProcessor()
tokenizer.load(tokenizer_path)
print(f"[Test] Tokenizer vocab size: {tokenizer.get_piece_size()}")

# Initialize model
model = MediumTransformer(
    vocab_size=config["vocab_size"],
    d_model=config["d_model"],
    n_layers=config["n_layers"],
    n_heads=config["n_heads"],
    d_ff=config["d_ff"],
    max_len=config["max_len"]
)

# Load state dict
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

print(f"[Test] Model loaded successfully. Parameters: {model.count_parameters():,}")

# Test forward pass
input_ids = torch.randint(0, config["vocab_size"], (1, 10))
logits = model(input_ids)
print(f"[Test] Forward pass successful. Logits shape: {logits.shape}")

print(f"[Test] Checkpoint loading verified")
