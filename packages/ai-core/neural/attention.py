"""
Multi-Head Attention Mechanism

Scaled dot-product attention with multiple heads.
"""

import torch
import torch.nn as nn
import math


class MultiHeadAttention(nn.Module):
    """
    Multi-head self-attention mechanism.
    """

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        """
        Initialize multi-head attention.

        Args:
            d_model: Model dimension
            n_heads: Number of attention heads
            dropout: Dropout rate
        """
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads  # Dimension of each head

        # Linear projections for Q, K, V
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)

        # Output projection
        self.w_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def scaled_dot_product_attention(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
        mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Scaled dot-product attention.

        Args:
            q: Query tensor [batch_size, n_heads, seq_len, d_k]
            k: Key tensor [batch_size, n_heads, seq_len, d_k]
            v: Value tensor [batch_size, n_heads, seq_len, d_k]
            mask: Optional attention mask [batch_size, 1, seq_len, seq_len]

        Returns:
            Attention output [batch_size, n_heads, seq_len, d_k]
        """
        # Calculate attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)

        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Softmax to get attention weights
        attention_weights = torch.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention weights to values
        output = torch.matmul(attention_weights, v)

        return output

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional attention mask [seq_len, seq_len] or [batch_size, seq_len, seq_len]

        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        batch_size, seq_len, _ = x.size()

        # Linear projections and reshape for multi-head
        q = self.w_q(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        k = self.w_k(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        v = self.w_v(x).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)

        # Scaled dot-product attention
        # Handle mask: if 2D, expand to 4D for multi-head
        if mask is not None:
            if mask.dim() == 2:
                # [seq_len, seq_len] -> [1, 1, seq_len, seq_len]
                mask = mask.unsqueeze(0).unsqueeze(0)
            elif mask.dim() == 3:
                # [batch_size, seq_len, seq_len] -> [batch_size, 1, seq_len, seq_len]
                mask = mask.unsqueeze(1)

        attention_output = self.scaled_dot_product_attention(q, k, v, mask)

        # Concatenate heads
        attention_output = attention_output.transpose(1, 2).contiguous()
        attention_output = attention_output.view(batch_size, seq_len, self.d_model)

        # Final linear projection
        output = self.w_o(attention_output)

        return output
