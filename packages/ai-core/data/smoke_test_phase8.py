"""
Phase 8 - Smoke Test for Experimental Training

Quick verification that the model can run a forward/backward pass.
"""

import json
import os
import sys
import time
from pathlib import Path
import torch
import torch.nn as nn
import sentencepiece as spm

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
EXPERIMENTAL_DIR = DATA_DIR / "experimental" / "phase8"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"

print("="*60)
print("Phase 8 - Smoke Test")
print("="*60)

# Load tokenizer
tokenizer_path = PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()
print(f"Tokenizer loaded: {vocab_size} tokens")

# Import SmallTransformer
sys.path.insert(0, str(AI_CORE_DIR))
from neural.small_transformer import SmallTransformer

# Create very small model
print("\nCreating small model...")
model = SmallTransformer(
    vocab_size=vocab_size,
    d_model=64,  # Very small
    n_layers=1,  # Just 1 layer
    n_heads=2,
    d_ff=256,
    max_len=64,
    dropout=0.0
)

param_count = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {param_count:,}")

# Device
device = torch.device('cpu')
model = model.to(device)
print(f"Device: {device}")

# Create dummy data
print("\nCreating dummy data...")
batch_size = 4
seq_len = 32
dummy_input = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)
dummy_target = torch.randint(0, vocab_size, (batch_size, seq_len)).to(device)

print(f"Dummy input shape: {dummy_input.shape}")
print(f"Dummy target shape: {dummy_target.shape}")

# Forward pass
print("\nTesting forward pass...")
model.eval()
with torch.no_grad():
    logits = model(dummy_input)
print(f"Logits shape: {logits.shape}")

# Test backward pass
print("\nTesting backward pass...")
model.train()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

optimizer.zero_grad()
logits = model(dummy_input)
logits = logits.view(-1, vocab_size)
dummy_target = dummy_target.view(-1)
loss = criterion(logits, dummy_target)
print(f"Loss: {loss.item():.4f}")

loss.backward()
optimizer.step()
print("Backward pass successful!")

# Memory check
print(f"\nMemory usage:")
print(f"  Allocated: {torch.cuda.memory_allocated() if torch.cuda.is_available() else 'N/A (CPU)'}")
print(f"  Reserved: {torch.cuda.memory_reserved() if torch.cuda.is_available() else 'N/A (CPU)'}")

print("\n" + "="*60)
print("Smoke Test Complete - Training Pipeline Functional")
print("="*60)
