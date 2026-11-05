"""
Phase 10 - Minimal Transformer Model

Small Transformer architecture for CPU-only training.
"""

import torch
import torch.nn as nn
import math
from pathlib import Path

class TransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=2, num_layers=2, 
                 dim_feedforward=512, dropout=0.1, max_len=128):
        super().__init__()
        
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.dim_feedforward = dim_feedforward
        self.max_len = max_len
        
        # Embedding
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        
        # Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output layer
        self.fc = nn.Linear(d_model, vocab_size)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, x, mask=None):
        """
        x: (batch_size, seq_len)
        """
        batch_size, seq_len = x.shape
        
        # Create position indices
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        
        # Embedding
        x = self.embedding(x) + self.pos_embedding(positions)
        x = self.dropout(x)
        
        # Transformer
        x = self.transformer(x, mask=mask)
        
        # Output
        x = self.fc(x)
        
        return x
    
    def count_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

def create_model(vocab_size, config=None):
    """Create model with configuration"""
    if config is None:
        config = {
            'd_model': 128,
            'nhead': 2,
            'num_layers': 2,
            'dim_feedforward': 512,
            'dropout': 0.1,
            'max_len': 128
        }
    
    model = TransformerModel(vocab_size, **config)
    return model, config

if __name__ == "__main__":
    # Test model creation
    vocab_size = 8000
    model, config = create_model(vocab_size)
    
    print("Model Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print(f"\nTotal parameters: {model.count_parameters():,}")
    
    # Test forward pass
    batch_size = 4
    seq_len = 32
    x = torch.randint(0, vocab_size, (batch_size, seq_len))
    
    output = model(x)
    print(f"\nInput shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    
    print("\nModel test successful!")
