"""
Small Transformer Model

Decoder-only Transformer architecture for language modeling.
"""

import torch
import torch.nn as nn
from .embedding import TokenEmbedding, PositionalEncoding
from .attention import MultiHeadAttention
from .ffn import FeedForwardNetwork


class TransformerBlock(nn.Module):
    """
    Single Transformer block with self-attention and feed-forward network.
    """

    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        """
        Initialize Transformer block.

        Args:
            d_model: Model dimension
            n_heads: Number of attention heads
            d_ff: Feed-forward dimension
            dropout: Dropout rate
        """
        super().__init__()
        self.self_attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = FeedForwardNetwork(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor [batch_size, seq_len, d_model]
            mask: Optional attention mask [batch_size, seq_len, seq_len]

        Returns:
            Output tensor [batch_size, seq_len, d_model]
        """
        # Self-attention with residual connection
        attn_output = self.self_attention(x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Feed-forward with residual connection
        ffn_output = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_output))

        return x


class SmallTransformer(nn.Module):
    """
    Small decoder-only Transformer for language modeling.
    """

    def __init__(
        self,
        vocab_size: int,
        d_model: int = 128,
        n_layers: int = 4,
        n_heads: int = 4,
        d_ff: int = 512,
        max_len: int = 256,
        dropout: float = 0.1
    ):
        """
        Initialize Small Transformer.

        Args:
            vocab_size: Size of vocabulary
            d_model: Model dimension
            n_layers: Number of Transformer blocks
            n_heads: Number of attention heads
            d_ff: Feed-forward dimension
            max_len: Maximum sequence length
            dropout: Dropout rate
        """
        super().__init__()

        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.max_len = max_len

        # Embedding layers
        self.token_embedding = TokenEmbedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_len, dropout)

        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])

        # Output layer
        self.output_layer = nn.Linear(d_model, vocab_size)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def generate_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """
        Generate causal mask for autoregressive generation.

        Args:
            seq_len: Sequence length
            device: Device to create mask on

        Returns:
            Causal mask [seq_len, seq_len]
        """
        mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
        return mask

    def forward(
        self,
        input_ids: torch.Tensor,
        targets: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass.

        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            targets: Target token IDs [batch_size, seq_len] (optional, for training)

        Returns:
            Logits [batch_size, seq_len, vocab_size] or loss if targets provided
        """
        batch_size, seq_len = input_ids.size()

        # Embeddings
        x = self.token_embedding(input_ids)
        x = self.positional_encoding(x)

        # Generate causal mask for autoregressive
        mask = self.generate_causal_mask(seq_len, input_ids.device)

        # Transformer blocks
        for block in self.transformer_blocks:
            x = block(x, mask)

        # Output projection
        logits = self.output_layer(x)

        # Calculate loss if targets provided
        if targets is not None:
            # Shift targets for next-token prediction
            loss = nn.functional.cross_entropy(
                logits.view(-1, self.vocab_size),
                targets.view(-1),
                ignore_index=-100  # Ignore padding if used
            )
            return loss

        return logits

    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 100,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        repetition_penalty: float = 1.0
    ) -> torch.Tensor:
        """
        Generate text autoregressively with improved sampling.

        Args:
            input_ids: Input token IDs [batch_size, seq_len]
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature
            top_k: Top-k sampling threshold
            top_p: Top-p (nucleus) sampling threshold
            do_sample: Whether to sample or use greedy decoding
            repetition_penalty: Penalty for repeating tokens
            no_repeat_ngram_size: Prevent repeating n-grams of this size

        Returns:
            Generated token IDs [batch_size, seq_len + max_new_tokens]
        """
        self.eval()
        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Truncate to max_len if needed
                if input_ids.size(1) > self.max_len:
                    input_ids = input_ids[:, -self.max_len:]

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

        return input_ids

    def count_parameters(self) -> int:
        """Count total number of parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
