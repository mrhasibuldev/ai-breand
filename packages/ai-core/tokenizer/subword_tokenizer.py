"""
NexusAI Subword Tokenizer Implementation

Implements a subword tokenizer using SentencePiece for Bengali and English.
Supports bilingual tokenization with proper morphology handling.
"""

import sentencepiece as spm
import json
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter
import re


class SubwordTokenizer:
    """
    Subword tokenizer using SentencePiece for Bengali and English.
    Supports bilingual tokenization with proper morphology handling.
    """

    def __init__(
        self,
        vocab_size: int = 32000,
        model_type: str = "bpe",
        character_coverage: float = 0.9995,
        special_tokens: Optional[Dict[str, str]] = None
    ):
        """
        Initialize subword tokenizer.

        Args:
            vocab_size: Target vocabulary size
            model_type: SentencePiece model type ('bpe', 'unigram', 'word', 'char')
            character_coverage: Character coverage for vocab (higher for more languages)
            special_tokens: Custom special tokens
        """
        self.vocab_size = vocab_size
        self.model_type = model_type
        self.character_coverage = character_coverage

        # Default special tokens
        self.special_tokens = special_tokens or {
            "PAD": "<pad>",
            "UNK": "<unk>",
            "BOS": "<s>",
            "EOS": "</s>",
            "USER": "<user>",
            "ASSISTANT": "<assistant>",
            "SEP": "<sep>"
        }

        self.sp = None
        self.is_built = False
        self.version = "1.0.0"

    def train(
        self,
        input_files: List[str],
        model_prefix: str = "nexusai_tokenizer",
        control_symbols: Optional[List[str]] = None
    ) -> str:
        """
        Train SentencePiece model on input files.

        Args:
            input_files: List of text files for training
            model_prefix: Prefix for output model files
            control_symbols: Additional control symbols

        Returns:
            Path to trained model file
        """
        control_symbols = control_symbols or list(self.special_tokens.values())

        # Train SentencePiece model
        spm.SentencePieceTrainer.train(
            input=','.join(input_files),
            model_prefix=model_prefix,
            vocab_size=self.vocab_size,
            model_type=self.model_type,
            character_coverage=self.character_coverage,
            user_defined_symbols=control_symbols,
            split_by_whitespace=False,  # Use Unicode tokenization
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
            pad_piece=self.special_tokens["PAD"],
            unk_piece=self.special_tokens["UNK"],
            bos_piece=self.special_tokens["BOS"],
            eos_piece=self.special_tokens["EOS"],
            normalization_rule_name='nmt_nfkc',  # Unicode normalization
            remove_extra_whitespaces=False,
            max_sentence_length=512  # Match model max length
        )

        model_path = f"{model_prefix}.model"
        self.load(model_path)

        return model_path

    def load(self, model_path: str):
        """
        Load trained SentencePiece model.

        Args:
            model_path: Path to .model file
        """
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(model_path)
        self.is_built = True

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text to token IDs.

        Args:
            text: Input text
            add_special_tokens: Whether to add BOS and EOS tokens

        Returns:
            List of token IDs
        """
        if not self.is_built:
            raise ValueError("Tokenizer not loaded. Call train() or load() first.")

        tokens = self.sp.encode(text, out_type=int)

        if add_special_tokens:
            # Add BOS and EOS (SentencePiece doesn't add them by default)
            bos_id = self.sp.piece_to_id(self.special_tokens["BOS"])
            eos_id = self.sp.piece_to_id(self.special_tokens["EOS"])
            tokens = [bos_id] + tokens + [eos_id]

        return tokens

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.

        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens in output

        Returns:
            Decoded text
        """
        if not self.is_built:
            raise ValueError("Tokenizer not loaded. Call train() or load() first.")

        if skip_special_tokens:
            # Filter out special tokens
            special_ids = set(self.sp.piece_to_id(t) for t in self.special_tokens.values())
            token_ids = [tid for tid in token_ids if tid not in special_ids]

        return self.sp.decode(token_ids)

    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        if not self.is_built:
            raise ValueError("Tokenizer not loaded. Call train() or load() first.")
        return self.sp.get_piece_size()

    def get_special_token_ids(self) -> Dict[str, int]:
        """Get IDs of special tokens"""
        if not self.is_built:
            raise ValueError("Tokenizer not loaded. Call train() or load() first.")

        return {
            name: self.sp.piece_to_id(token)
            for name, token in self.special_tokens.items()
        }

    def token_count(self, text: str) -> int:
        """Count tokens in text without special tokens"""
        if not self.is_built:
            raise ValueError("Tokenizer not loaded. Call train() or load() first.")
        return self.sp.encode(text, out_type=int)

    def save_metadata(self, output_path: str):
        """
        Save tokenizer metadata for reproducibility.

        Args:
            output_path: Path to save metadata JSON
        """
        metadata = {
            "version": self.version,
            "vocab_size": self.vocab_size,
            "model_type": self.model_type,
            "character_coverage": self.character_coverage,
            "special_tokens": self.special_tokens,
            "special_token_ids": self.get_special_token_ids() if self.is_built else None,
            "actual_vocab_size": self.get_vocab_size() if self.is_built else None
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    @staticmethod
    def create_sample_text_file(texts: List[str], output_path: str):
        """
        Create a text file from a list of texts for training.

        Args:
            texts: List of text strings
            output_path: Path to output file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for text in texts:
                f.write(text + '\n')


def prepare_training_data(
    bengali_file: str,
    english_file: str,
    output_file: str
):
    """
    Combine Bengali and English texts for tokenizer training.

    Args:
        bengali_file: Path to Bengali text file
        english_file: Path to English text file
        output_file: Path to combined output file
    """
    texts = []

    # Load Bengali texts
    if Path(bengali_file).exists():
        with open(bengali_file, 'r', encoding='utf-8') as f:
            texts.extend(f.readlines())

    # Load English texts
    if Path(english_file).exists():
        with open(english_file, 'r', encoding='utf-8') as f:
            texts.extend(f.readlines())

    # Write combined
    with open(output_file, 'w', encoding='utf-8') as f:
        for text in texts:
            f.write(text.strip() + '\n')

    print(f"[Tokenizer] Combined {len(texts)} texts for training")


if __name__ == "__main__":
    # Example usage
    print("[Subword Tokenizer] Implementation ready")
    print("[Subword Tokenizer] Requires SentencePiece installation: pip install sentencepiece")
