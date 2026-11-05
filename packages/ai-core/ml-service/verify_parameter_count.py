"""
Verify exact parameter count from checkpoint
"""

import sys
import os
import torch

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
service_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.dirname(service_dir)
sys.path.insert(0, ai_core_dir)

checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")

print("Loading checkpoint...")
checkpoint = torch.load(checkpoint_path, map_location="cpu")

print("\nCheckpoint keys:", list(checkpoint.keys()))

config = checkpoint["config"]
print("\nConfig:", config)

model_state_dict = checkpoint["model_state_dict"]

print("\nParameter breakdown:")
total_params = 0
for key, tensor in model_state_dict.items():
    param_count = tensor.numel()
    total_params += param_count
    print(f"  {key}: {tensor.shape} = {param_count:,} parameters")

print(f"\nTotal parameters from state_dict: {total_params:,}")

# Calculate expected from config
vocab_size = config["vocab_size"]
d_model = config["d_model"]
n_layers = config["n_layers"]
n_heads = config["n_heads"]
d_ff = config["d_ff"]
max_len = config["max_len"]

print("\nExpected parameter calculation:")
print(f"  vocab_size: {vocab_size}")
print(f"  d_model: {d_model}")
print(f"  n_layers: {n_layers}")
print(f"  n_heads: {n_heads}")
print(f"  d_ff: {d_ff}")
print(f"  max_len: {max_len}")

# Expected for MediumTransformer
embed_params = vocab_size * d_model
pos_embed_params = max_len * d_model
layer_params = n_layers * (
    4 * d_model * d_model +  # Q, K, V, O projections
    2 * d_model * d_ff +     # FFN up/down
    2 * d_model              # layer norms
)
output_params = d_model * vocab_size

expected_total = embed_params + pos_embed_params + layer_params + output_params

print(f"\nExpected breakdown:")
print(f"  Token embedding: {vocab_size} * {d_model} = {embed_params:,}")
print(f"  Positional embedding: {max_len} * {d_model} = {pos_embed_params:,}")
print(f"  Transformer layers: {layer_params:,}")
print(f"  Output projection: {d_model} * {vocab_size} = {output_params:,}")
print(f"  Expected total: {expected_total:,}")

print(f"\nDiscrepancy: {total_params - expected_total:,} ({((total_params - expected_total) / expected_total * 100):.2f}%)")
