"""
Text Generator

Autoregressive text generation with sampling strategies.
"""

import torch
import torch.nn as nn
from typing import List, Optional


class TextGenerator:
    """
    Text generator for autoregressive text generation.
    """

    def __init__(self, model: nn.Module, tokenizer, device: str = "cpu"):
        """
        Initialize text generator.

        Args:
            model: Trained model
            tokenizer: Tokenizer instance
            device: Device to run on
        """
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.model.eval()

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        repetition_penalty: float = 1.2
    ) -> str:
        """
        Generate text from prompt with improved diversity.

        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            top_k: Top-k sampling (0 = disabled)
            top_p: Top-p (nucleus) sampling
            do_sample: Whether to sample or use greedy decoding
            repetition_penalty: Penalty for repeating tokens (>1 reduces repetition)

        Returns:
            Generated text
        """
        # Encode prompt
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)

        # Generate with improved sampling
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty
            )

        # Decode
        generated_ids = generated_ids[0].cpu().tolist()
        generated_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # Remove prompt from response if it's repeated
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()

        return generated_text

    def load_checkpoint(self, checkpoint_path: str):
        """
        Load model from checkpoint.

        Args:
            checkpoint_path: Path to checkpoint
        """
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        print(f"Model loaded from {checkpoint_path}")
