"""
Simple Tokenizer Implementation

Byte-level simple tokenizer for Phase 1.
"""

import json
from typing import List, Dict, Set
from collections import Counter


class SimpleTokenizer:
    """
    Simple word-level tokenizer with special tokens.
    """

    # Special tokens
    PAD_TOKEN = "<PAD>"
    UNK_TOKEN = "<UNK>"
    BOS_TOKEN = "<BOS>"
    EOS_TOKEN = "<EOS>"

    def __init__(self, vocab_size: int = 5000):
        """
        Initialize tokenizer.

        Args:
            vocab_size: Maximum vocabulary size
        """
        self.vocab_size = vocab_size
        self.word_to_id: Dict[str, int] = {}
        self.id_to_word: Dict[int, str] = {}
        self.word_freq: Counter = Counter()
        self.is_built = False

        # Initialize with special tokens
        self._init_special_tokens()

    def _init_special_tokens(self):
        """Initialize special tokens in vocabulary"""
        special_tokens = [self.PAD_TOKEN, self.UNK_TOKEN, self.BOS_TOKEN, self.EOS_TOKEN]
        for i, token in enumerate(special_tokens):
            self.word_to_id[token] = i
            self.id_to_word[i] = token

    def build_vocab(self, texts: List[str], min_freq: int = 2):
        """
        Build vocabulary from texts.

        Args:
            texts: List of texts to build vocabulary from
            min_freq: Minimum frequency for a word to be included
        """
        # Count word frequencies
        for text in texts:
            words = self._tokenize_text(text)
            self.word_freq.update(words)

        # Add words to vocabulary (excluding special tokens)
        # Start from index 4 (after special tokens)
        idx = 4
        for word, freq in self.word_freq.most_common():
            if freq >= min_freq and idx < self.vocab_size:
                if word not in self.word_to_id:
                    self.word_to_id[word] = idx
                    self.id_to_word[idx] = word
                    idx += 1

        self.is_built = True
        print(f"Vocabulary built: {len(self.word_to_id)} tokens")

    def _tokenize_text(self, text: str) -> List[str]:
        """
        Simple word tokenization.

        Args:
            text: Input text

        Returns:
            List of words
        """
        # Simple whitespace tokenization
        words = text.lower().split()
        return words

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
            raise ValueError("Vocabulary not built. Call build_vocab() first.")

        words = self._tokenize_text(text)
        token_ids = []

        if add_special_tokens:
            token_ids.append(self.word_to_id[self.BOS_TOKEN])

        for word in words:
            token_id = self.word_to_id.get(word, self.word_to_id[self.UNK_TOKEN])
            token_ids.append(token_id)

        if add_special_tokens:
            token_ids.append(self.word_to_id[self.EOS_TOKEN])

        return token_ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.

        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens in output

        Returns:
            Decoded text
        """
        words = []
        special_tokens = {self.PAD_TOKEN, self.UNK_TOKEN, self.BOS_TOKEN, self.EOS_TOKEN}

        for token_id in token_ids:
            word = self.id_to_word.get(token_id, self.UNK_TOKEN)
            if skip_special_tokens and word in special_tokens:
                continue
            words.append(word)

        return " ".join(words)

    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return len(self.word_to_id)

    def save(self, path: str):
        """
        Save tokenizer to file.

        Args:
            path: Path to save tokenizer
        """
        data = {
            "vocab_size": self.vocab_size,
            "word_to_id": self.word_to_id,
            "id_to_word": self.id_to_word,
            "word_freq": dict(self.word_freq),
            "is_built": self.is_built
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Tokenizer saved to {path}")

    def load(self, path: str):
        """
        Load tokenizer from file.

        Args:
            path: Path to load tokenizer from
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.vocab_size = data["vocab_size"]
        self.word_to_id = {k: int(v) for k, v in data["word_to_id"].items()}
        self.id_to_word = {int(k): v for k, v in data["id_to_word"].items()}
        self.word_freq = Counter(data["word_freq"])
        self.is_built = data["is_built"]

        print(f"Tokenizer loaded from {path}")
