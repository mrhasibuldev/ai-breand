"""
NexusAI Core-01 Tokenizer Interface

Provides a compatible tokenizer interface for NexusAI Core-01.
This interface wraps the existing SentencePiece BPE tokenizer.
"""

import sys
import os
from typing import List, Optional
import sentencepiece as spm

# Add models directory to path for config import
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(ai_core_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from nexusai_core_01.config.model_config import NexusAICore01Config


class NexusAITokenizer:
    """
    Tokenizer interface for NexusAI Core-01.
    
    Wraps SentencePiece BPE tokenizer with compatibility checks.
    """
    
    def __init__(self, tokenizer_path: str, config: NexusAICore01Config):
        """
        Initialize tokenizer.
        
        Args:
            tokenizer_path: Path to SentencePiece model file
            config: Model configuration for compatibility validation
        """
        self.tokenizer_path = tokenizer_path
        self.config = config
        
        # Load SentencePiece tokenizer
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(tokenizer_path)
        
        # Validate compatibility
        self._validate_compatibility()
        
        # Set special token IDs from config
        self.pad_id = config.pad_id
        self.unk_id = config.unk_id
        self.bos_id = config.bos_id
        self.eos_id = config.eos_id
    
    def _validate_compatibility(self):
        """Validate tokenizer compatibility with model configuration"""
        vocab_size = self.sp.get_piece_size()
        
        if vocab_size != self.config.vocab_size:
            raise ValueError(
                f"Tokenizer vocab size ({vocab_size}) does not match "
                f"model config vocab size ({self.config.vocab_size})"
            )
        
        # Validate special token IDs
        if self.sp.pad_id() != self.config.pad_id:
            print(f"Warning: Tokenizer pad_id ({self.sp.pad_id()}) differs from config ({self.config.pad_id})")
        
        if self.sp.unk_id() != self.config.unk_id:
            print(f"Warning: Tokenizer unk_id ({self.sp.unk_id()}) differs from config ({self.config.unk_id})")
        
        if self.sp.bos_id() != self.config.bos_id:
            print(f"Warning: Tokenizer bos_id ({self.sp.bos_id()}) differs from config ({self.config.bos_id})")
        
        if self.sp.eos_id() != self.config.eos_id:
            print(f"Warning: Tokenizer eos_id ({self.sp.eos_id()}) differs from config ({self.config.eos_id})")
    
    def encode(
        self,
        text: str,
        add_special_tokens: bool = True,
        max_length: Optional[int] = None
    ) -> List[int]:
        """
        Encode text to token IDs.
        
        Args:
            text: Input text
            add_special_tokens: Whether to add BOS and EOS tokens
            max_length: Maximum length (truncates if exceeded)
        
        Returns:
            List of token IDs
        """
        tokens = self.sp.encode(text, out_type=int)
        
        if add_special_tokens:
            tokens = [self.bos_id] + tokens + [self.eos_id]
        
        if max_length is not None and len(tokens) > max_length:
            tokens = tokens[:max_length]
        
        return tokens
    
    def decode(
        self,
        token_ids: List[int],
        skip_special_tokens: bool = True
    ) -> str:
        """
        Decode token IDs to text.
        
        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens
        
        Returns:
            Decoded text
        """
        if skip_special_tokens:
            token_ids = [
                tid for tid in token_ids
                if tid not in [self.pad_id, self.unk_id, self.bos_id, self.eos_id]
            ]
        
        return self.sp.decode(token_ids)
    
    def batch_encode(
        self,
        texts: List[str],
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        padding: bool = True,
        return_tensors: bool = False
    ) -> List[List[int]]:
        """
        Encode multiple texts.
        
        Args:
            texts: List of input texts
            add_special_tokens: Whether to add special tokens
            max_length: Maximum length
            padding: Whether to pad to max_length
            return_tensors: Whether to return as PyTorch tensor
        
        Returns:
            List of token ID lists (or tensor if return_tensors=True)
        """
        encoded = [
            self.encode(text, add_special_tokens, max_length)
            for text in texts
        ]
        
        if padding and max_length is not None:
            encoded = [
                ids + [self.pad_id] * (max_length - len(ids))
                for ids in encoded
            ]
        
        if return_tensors:
            import torch
            return torch.tensor(encoded, dtype=torch.long)
        
        return encoded
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return self.sp.get_piece_size()
    
    def get_special_tokens(self) -> dict:
        """Get special token IDs"""
        return {
            "pad_id": self.pad_id,
            "unk_id": self.unk_id,
            "bos_id": self.bos_id,
            "eos_id": self.eos_id
        }
    
    def tokenize_quality_test(self, test_texts: List[str]) -> dict:
        """
        Test tokenizer quality on sample texts.
        
        Args:
            test_texts: List of test texts
        
        Returns:
            Dictionary with test results
        """
        results = {}
        for text in test_texts:
            tokens = self.encode(text, add_special_tokens=False)
            decoded = self.decode(tokens, skip_special_tokens=False)
            unk_count = tokens.count(self.unk_id)
            
            results[text] = {
                "token_count": len(tokens),
                "unk_count": unk_count,
                "decoded": decoded,
                "perfect_reconstruction": decoded == text
            }
        
        return results


def create_default_tokenizer(config: NexusAICore01Config) -> NexusAITokenizer:
    """
    Create tokenizer with default path.
    
    Args:
        config: Model configuration
    
    Returns:
        NexusAITokenizer instance
    """
    # Use existing SentencePiece tokenizer
    ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tokenizer_path = os.path.join(
        ai_core_dir,
        "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model"
    )
    
    return NexusAITokenizer(tokenizer_path, config)


if __name__ == "__main__":
    # Test tokenizer
    config = NexusAICore01Config()
    tokenizer = create_default_tokenizer(config)
    
    print(f"Vocab size: {tokenizer.get_vocab_size()}")
    print(f"Special tokens: {tokenizer.get_special_tokens()}")
    
    test_texts = [
        "What is your name?",
        "আমার নাম কি",
        "Tumi kemon acho?",
        "2 + 2 = 4"
    ]
    
    results = tokenizer.tokenize_quality_test(test_texts)
    for text, result in results.items():
        print(f"\nText: {text}")
        print(f"  Tokens: {result['token_count']}, UNK: {result['unk_count']}")
        print(f"  Decoded: {result['decoded']}")
