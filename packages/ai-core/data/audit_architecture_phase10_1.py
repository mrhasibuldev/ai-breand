"""
Phase 10.1 - Model Architecture Verification

Independently calculates parameter count from model implementation.
"""

import torch
import torch.nn as nn
from pathlib import Path

print("="*60)
print("Phase 10.1 - Model Architecture Verification")
print("="*60)

# Define the model as implemented
class TransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=2, num_layers=2, 
                 dim_feedforward=512, dropout=0.1, max_len=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        batch_size, seq_len = x.shape
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        x = self.embedding(x) + self.pos_embedding(positions)
        x = self.dropout(x)
        x = self.transformer(x, mask=mask)
        x = self.fc(x)
        return x

# Create model with reported configuration
config = {
    'vocab_size': 8000,
    'd_model': 128,
    'nhead': 2,
    'num_layers': 2,
    'dim_feedforward': 512,
    'dropout': 0.1,
    'max_len': 128
}

model = TransformerModel(**config)

# Calculate parameters by component
def count_parameters(model):
    total = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total

print(f"\nConfiguration:")
for key, value in config.items():
    print(f"  {key}: {value}")

print(f"\nParameter breakdown:")
print(f"  Token embedding: {model.embedding.weight.numel():,}")
print(f"  Positional embedding: {model.pos_embedding.weight.numel():,}")
print(f"  Transformer encoder: {sum(p.numel() for p in model.transformer.parameters() if p.requires_grad):,}")
print(f"  Output projection: {model.fc.weight.numel() + model.fc.bias.numel():,}")

total_params = count_parameters(model)
print(f"\nTotal trainable parameters: {total_params:,}")

# Compare with reported
reported_params = 2468928
print(f"\nReported parameters: {reported_params:,}")
print(f"Calculated parameters: {total_params:,}")
print(f"Match: {total_params == reported_params}")

if total_params != reported_params:
    difference = total_params - reported_params
    print(f"Difference: {difference:,}")

print("\n" + "="*60)
print("ARCHITECTURE VERIFICATION COMPLETE")
print("="*60)
