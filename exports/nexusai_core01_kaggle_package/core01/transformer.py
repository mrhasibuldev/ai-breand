"""
NexusAI Core-01 Transformer Architecture

Independent decoder-only Transformer language model built from scratch for NexusAI.
This architecture is designed for long-term development and future scaling.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple
import sys
import os

# Add models directory to path for config import
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(ai_core_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from nexusai_core_01.config.model_config import NexusAICore01Config


class TokenEmbedding(nn.Module):
    """Token embedding layer with optional scaling"""
    
    def __init__(self, vocab_size: int, d_model: int, padding_idx: int = 0):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=padding_idx)
        self.d_model = d_model
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Scale embeddings by sqrt(d_model) for stability
        return self.embedding(x) * math.sqrt(self.d_model)


class SinusoidalPositionalEncoding(nn.Module):
    """
    Sinusoidal positional encoding.
    
    Uses sin and cos functions of different frequencies to encode position.
    This allows the model to learn relative positions and generalize to longer sequences.
    """
    
    def __init__(self, d_model: int, max_len: int = 512, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Register as buffer (not a parameter)
        self.register_buffer('pe', pe.unsqueeze(0))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape [batch_size, seq_len, d_model]
        
        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class MultiHeadAttention(nn.Module):
    """
    Multi-head self-attention mechanism.
    
    Implements scaled dot-product attention with multiple attention heads.
    """
    
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        
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
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Scaled dot-product attention.
        
        Args:
            q: Query tensor [batch_size, n_heads, seq_len, head_dim]
            k: Key tensor [batch_size, n_heads, seq_len, head_dim]
            v: Value tensor [batch_size, n_heads, seq_len, head_dim]
            mask: Optional attention mask [batch_size, 1, seq_len, seq_len]
        
        Returns:
            output: Attention output [batch_size, n_heads, seq_len, head_dim]
            attn_weights: Attention weights [batch_size, n_heads, seq_len, seq_len]
        """
        # Scale scores by sqrt(head_dim)
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        # Softmax over last dimension
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        output = torch.matmul(attn_weights, v)
        
        return output, attn_weights
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional attention mask [batch_size, seq_len, seq_len]
        
        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        batch_size, seq_len, _ = x.size()
        
        # Linear projections
        q = self.w_q(x)  # [batch_size, seq_len, d_model]
        k = self.w_k(x)
        v = self.w_v(x)
        
        # Reshape for multi-head attention
        q = q.view(batch_size, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        
        # Reshape mask for multi-head attention
        if mask is not None:
            mask = mask.unsqueeze(1)  # [batch_size, 1, seq_len, seq_len]
        
        # Scaled dot-product attention
        attn_output, _ = self.scaled_dot_product_attention(q, k, v, mask)
        
        # Concatenate heads
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, seq_len, self.d_model)
        
        # Output projection
        output = self.w_o(attn_output)
        
        return output


class FeedForwardNetwork(nn.Module):
    """
    Feed-forward network with GELU activation.
    
    Two linear layers with a GELU activation in between.
    """
    
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
        
        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        x = self.dropout(x)
        return x


class TransformerBlock(nn.Module):
    """
    Transformer block with pre-norm architecture.
    
    Contains multi-head self-attention and feed-forward network
    with residual connections and layer normalization.
    """
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = FeedForwardNetwork(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional attention mask [batch_size, seq_len, seq_len]
        
        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        # Pre-norm attention with residual connection
        attn_output = self.attention(self.norm1(x), mask)
        x = x + self.dropout(attn_output)
        
        # Pre-norm FFN with residual connection
        ffn_output = self.ffn(self.norm2(x))
        x = x + self.dropout(ffn_output)
        
        return x


class NexusAICore01(nn.Module):
    """
    NexusAI Core-01: Independent Transformer Language Model
    
    This is the first officially independent neural language model for NexusAI.
    It is built from scratch with independently initialized weights.
    
    Model Status: UNTRAINED - RANDOMLY INITIALIZED
    """
    
    def __init__(self, config: NexusAICore01Config):
        super().__init__()
        
        self.config = config
        
        # Token embedding
        self.token_embedding = TokenEmbedding(
            config.vocab_size,
            config.d_model,
            padding_idx=config.pad_id
        )
        
        # Positional encoding
        if config.positional_encoding == "sinusoidal":
            self.positional_encoding = SinusoidalPositionalEncoding(
                config.d_model,
                config.max_len,
                config.dropout
            )
        else:
            raise ValueError(f"Unsupported positional encoding: {config.positional_encoding}")
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(
                config.d_model,
                config.n_heads,
                config.d_ff,
                config.dropout
            )
            for _ in range(config.n_layers)
        ])
        
        # Output layer
        self.output_layer = nn.Linear(config.d_model, config.vocab_size)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights with normal distribution"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=self.config.weight_init_std)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=self.config.weight_init_std)
    
    def generate_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """
        Generate causal (autoregressive) mask.
        
        Args:
            seq_len: Sequence length
            device: Device to create mask on
        
        Returns:
            Causal mask [seq_len, seq_len] where lower triangle is 1, upper is 0
        """
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
        return mask
    
    def forward(
        self,
        input_ids: torch.Tensor,
        targets: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            targets: Target token IDs [batch_size, seq_len] (optional, for training)
            attention_mask: Attention mask [batch_size, seq_len] (optional)
        
        Returns:
            Logits [batch_size, seq_len, vocab_size] or loss if targets provided
        """
        batch_size, seq_len = input_ids.size()
        
        # Validate sequence length
        if seq_len > self.config.max_len:
            raise ValueError(f"Sequence length {seq_len} exceeds max_len {self.config.max_len}")
        
        # Token embeddings
        x = self.token_embedding(input_ids)
        
        # Positional encoding
        x = self.positional_encoding(x)
        
        # Generate causal mask for autoregressive generation
        causal_mask = self.generate_causal_mask(seq_len, input_ids.device)
        
        # Apply attention mask if provided (for padding)
        if attention_mask is not None:
            # Convert attention mask to causal attention mask
            # attention_mask: [batch_size, seq_len] where 1 = valid, 0 = padding
            mask = attention_mask.unsqueeze(1).unsqueeze(1)  # [batch_size, 1, 1, seq_len]
            mask = mask.expand(-1, seq_len, -1, -1)  # [batch_size, seq_len, seq_len, seq_len]
            mask = mask.squeeze(-1)  # [batch_size, seq_len, seq_len]
            causal_mask = causal_mask.unsqueeze(0) * mask  # Apply both masks
        else:
            causal_mask = causal_mask.unsqueeze(0)  # [1, seq_len, seq_len]
        
        # Transformer blocks
        for block in self.transformer_blocks:
            x = block(x, causal_mask)
        
        # Output projection
        logits = self.output_layer(x)
        
        # Calculate loss if targets provided
        if targets is not None:
            # Shift targets for next-token prediction
            loss = F.cross_entropy(
                logits.view(-1, self.config.vocab_size),
                targets.view(-1),
                ignore_index=self.config.pad_id
            )
            return loss
        
        return logits
    
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = None,
        temperature: float = None,
        top_k: int = None,
        top_p: float = None,
        do_sample: bool = True,
        repetition_penalty: float = None
    ) -> torch.Tensor:
        """
        Generate text autoregressively.
        
        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
            top_k: Top-k sampling (0 = disabled)
            top_p: Top-p (nucleus) sampling
            do_sample: Whether to sample or use greedy decoding
            repetition_penalty: Penalty for repeating tokens
        
        Returns:
            Generated token IDs [batch_size, seq_len + max_new_tokens]
        """
        self.eval()
        
        # Use config defaults if not provided
        max_new_tokens = max_new_tokens or self.config.max_new_tokens
        temperature = temperature or self.config.temperature
        top_k = top_k if top_k is not None else self.config.top_k
        top_p = top_p if top_p is not None else self.config.top_p
        repetition_penalty = repetition_penalty or self.config.repetition_penalty
        
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Truncate to max_len if needed
                if input_ids.size(1) > self.config.max_len:
                    input_ids = input_ids[:, -self.config.max_len:]
                
                # Forward pass
                logits = self.forward(input_ids)
                
                # Get logits for last token
                logits = logits[:, -1, :]
                
                # Apply repetition penalty
                if repetition_penalty > 1.0:
                    for batch_idx in range(input_ids.size(0)):
                        for token_id in set(input_ids[batch_idx].tolist()):
                            logits[batch_idx, token_id] /= repetition_penalty
                
                # Temperature scaling
                logits = logits / temperature
                
                # Top-k filtering
                if top_k > 0:
                    top_k = min(top_k, logits.size(-1))
                    values, indices = torch.topk(logits, top_k)
                    logits = torch.full_like(logits, float('-inf'))
                    logits.scatter_(1, indices, values)
                
                # Top-p (nucleus) filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                    
                    # Remove tokens with cumulative probability above threshold
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = False
                    
                    for batch_idx in range(logits.size(0)):
                        indices_to_remove = sorted_indices[batch_idx][sorted_indices_to_remove[batch_idx]]
                        logits[batch_idx, indices_to_remove] = float('-inf')
                
                # Sample or greedy
                if do_sample:
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    next_token = torch.argmax(logits, dim=-1, keepdim=True)
                
                # Append to input
                input_ids = torch.cat([input_ids, next_token], dim=1)
                
                # Check for EOS
                if next_token.item() == self.config.eos_id:
                    break
        
        return input_ids
    
    def count_parameters(self) -> int:
        """Count total number of trainable parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def get_model_info(self) -> dict:
        """Get model information dictionary"""
        return {
            "model_name": self.config.model_name,
            "model_version": self.config.model_version,
            "model_status": self.config.model_status.value,
            "parameter_count": self.count_parameters(),
            "estimated_parameters": self.config.estimated_parameter_count(),
            "vocab_size": self.config.vocab_size,
            "d_model": self.config.d_model,
            "n_layers": self.config.n_layers,
            "n_heads": self.config.n_heads,
            "d_ff": self.config.d_ff,
            "max_len": self.config.max_len,
            "dropout": self.config.dropout,
            "device": next(self.parameters()).device
        }


if __name__ == "__main__":
    # Test model initialization
    config = NexusAICore01Config()
    model = NexusAICore01(config)
    
    print(f"Model: {config.model_name}")
    print(f"Parameters: {model.count_parameters():,}")
    print(f"Estimated: {config.estimated_parameter_count():,}")
    print(f"Model info: {model.get_model_info()}")
