"""
Feed-Forward Network

Position-wise feed-forward network for Transformer.
"""

import torch
import torch.nn as nn


class FeedForwardNetwork(nn.Module):
    """
    Position-wise feed-forward network.
    """

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        """
        Initialize feed-forward network.

        Args:
            d_model: Model dimension
            d_ff: Feed-forward dimension (usually 4x d_model)
            dropout: Dropout rate
        """
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor [batch_size, seq_len, d_model]

        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        # First linear + activation + dropout
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)

        # Second linear
        x = self.linear2(x)
        x = self.dropout(x)

        return x
