"""
NexusAI BPE Tokenizer Implementation (Fixed)

Implements Byte-Pair Encoding (BPE) tokenizer from scratch for Bengali and English.
No external dependencies required.
FIXED: Now preserves whitespace during encode/decode round-trip.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
import re


class BPETokenizer:
    """
    Byte-Pair Encoding tokenizer implementation.
    Supports Bengali and English with proper Unicode handling.
    FIXED: Preserves whitespace during encode/decode round-trip.
    """

    def __init__(
        self,
        vocab_size: int = 32000,
        special_tokens: Optional[Dict[str, str]] = None
    ):
        """
        Initialize BPE tokenizer.

        Args:
            vocab_size: Target vocabulary size
            special_tokens: Custom special tokens
        """
        self.vocab_size = vocab_size

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

        self.vocab = {}  # token -> id
        self.reverse_vocab = {}  # id -> token
        self.merges = []  # list of merge operations
        self.is_built = False
        self.version = "1.1.0"  # Updated version after whitespace fix

    def _initialize_vocab(self, texts: List[str]):
        """Initialize vocabulary with characters from texts"""
        # Count characters (subword units start as characters)
        char_freq = Counter()
        for text in texts:
            # Split into characters (Unicode-aware)
            chars = list(text)
            char_freq.update(chars)

        # Add special tokens first
        for i, (name, token) in enumerate(self.special_tokens.items()):
            self.vocab[token] = i
            self.reverse_vocab[i] = token

        # Add whitespace token (crucial for preservation)
        self.vocab[" "] = len(self.vocab)
        self.reverse_vocab[len(self.vocab) - 1] = " "

        # Add characters
        next_id = len(self.vocab)
        for char, freq in char_freq.most_common():
            if next_id >= self.vocab_size:
                break
            self.vocab[char] = next_id
            self.reverse_vocab[next_id] = char
            next_id += 1

    def _get_word_pairs(self, word: List[str]) -> Counter:
        """Get all pairs of adjacent symbols in a word"""
        pairs = Counter()
        prev_char = word[0]
        for char in word[1:]:
            pairs[(prev_char, char)] += 1
            prev_char = char
        return pairs

    def _get_stats(self, vocab: Dict[str, int]) -> Counter:
        """Get statistics of all pairs in vocabulary"""
        pairs = Counter()
        for word, freq in vocab.items():
            word_list = list(word)
            for i in range(len(word_list) - 1):
                pairs[(word_list[i], word_list[i + 1])] += freq
        return pairs

    def _merge_vocab(self, pair: Tuple[str, str], vocab: Dict[str, int]) -> Dict[str, int]:
        """Merge the most frequent pair in vocabulary"""
        new_vocab = {}
        bigram = re.escape(' '.join(pair))
        p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')

        for word in vocab:
            new_word = ' '.join(word)
            new_word = p.sub(''.join(pair), new_word)
            new_vocab[' '.join(new_word.split())] = vocab[word]

        return new_vocab

    def train(self, texts: List[str]) -> Dict[str, any]:
        """
        Train BPE tokenizer on texts.

        Args:
            texts: List of training texts

        Returns:
            Training statistics
        """
        print(f"[BPE Tokenizer] Training on {len(texts)} texts...")

        # Tokenize texts into words (whitespace split)
        words = []
        for text in texts:
            words.extend(text.split())

        # Count word frequencies
        word_freqs = Counter(words)

        # Initialize vocab with characters
        self._initialize_vocab(texts)

        # BPE training
        num_merges = self.vocab_size - len(self.vocab)
        for i in range(num_merges):
            pairs = self._get_stats(word_freqs)

            if not pairs:
                break

            # Get most frequent pair
            best_pair = max(pairs, key=pairs.get)
            self.merges.append(best_pair)

            # Merge pair in vocabulary
            word_freqs = self._merge_vocab(best_pair, word_freqs)

            # Add merged token to vocab
            merged_token = ''.join(best_pair)
            self.vocab[merged_token] = len(self.vocab)
            self.reverse_vocab[len(self.vocab) - 1] = merged_token

            if (i + 1) % 1000 == 0:
                print(f"[BPE Tokenizer] Trained {i + 1}/{num_merges} merges...")

        self.is_built = True

        stats = {
            "vocab_size": len(self.vocab),
            "num_merges": len(self.merges),
            "special_tokens": self.special_tokens
        }

        print(f"[BPE Tokenizer] Training complete. Vocab size: {len(self.vocab)}")
        return stats

    def _tokenize_word(self, word: str) -> List[str]:
        """Tokenize a single word using learned merges"""
        if not self.is_built:
            raise ValueError("Tokenizer not trained. Call train() first.")

        word_list = list(word)

        # Apply merges greedily
        while len(word_list) > 1:
            pairs = [(word_list[i], word_list[i + 1]) for i in range(len(word_list) - 1)]

            # Find the best pair that exists in our merges
            best_pair = None
            best_pair_index = len(self.merges)  # Higher index = learned later

            for i, pair in enumerate(pairs):
                if pair in self.merges:
                    pair_index = self.merges.index(pair)
                    if pair_index < best_pair_index:
                        best_pair = pair
                        best_pair_index = pair_index

            if best_pair is None:
                break

            # Merge the pair
            merged = ''.join(best_pair)
            new_word_list = []
            i = 0
            while i < len(word_list):
                if i < len(word_list) - 1 and word_list[i] == best_pair[0] and word_list[i + 1] == best_pair[1]:
                    new_word_list.append(merged)
                    i += 2
                else:
                    new_word_list.append(word_list[i])
                    i += 1

            word_list = new_word_list

        return word_list

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text to token IDs.
        FIXED: Preserves whitespace by encoding space token explicitly.

        Args:
            text: Input text
            add_special_tokens: Whether to add BOS and EOS tokens

        Returns:
            List of token IDs
        """
        if not self.is_built:
            raise ValueError("Tokenizer not trained. Call train() first.")

        # Preserve whitespace by encoding it explicitly
        # Split on space but preserve the space information
        words_with_space = text.split(' ')
        token_ids = []

        for i, word in enumerate(words_with_space):
            # Tokenize word
            if word:  # Non-empty word
                subwords = self._tokenize_word(word)

                # Convert to IDs
                for subword in subwords:
                    if subword in self.vocab:
                        token_ids.append(self.vocab[subword])
                    else:
                        # Fallback to character-level for unknown subwords
                        for char in subwords:
                            if char in self.vocab:
                                token_ids.append(self.vocab[char])
                            else:
                                token_ids.append(self.vocab[self.special_tokens["UNK"]])

            # Add space token after each word except the last
            if i < len(words_with_space) - 1:
                space_id = self.vocab.get(" ")
                if space_id is not None:
                    token_ids.append(space_id)

        if add_special_tokens:
            bos_id = self.vocab[self.special_tokens["BOS"]]
            eos_id = self.vocab[self.special_tokens["EOS"]]
            token_ids = [bos_id] + token_ids + [eos_id]

        return token_ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs to text.
        FIXED: Space token is decoded back to space character.

        Args:
            token_ids: List of token IDs
            skip_special_tokens: Whether to skip special tokens

        Returns:
            Decoded text
        """
        if not self.is_built:
            raise ValueError("Tokenizer not trained. Call train() first.")

        if skip_special_tokens:
            special_ids = set(self.vocab[t] for t in self.special_tokens.values())
            token_ids = [tid for tid in token_ids if tid not in special_ids]

        tokens = [self.reverse_vocab.get(tid, self.special_tokens["UNK"]) for tid in token_ids]
        text = ''.join(tokens)

        return text

    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return len(self.vocab)

    def get_special_token_ids(self) -> Dict[str, int]:
        """Get IDs of special tokens"""
        return {
            name: self.vocab[token]
            for name, token in self.special_tokens.items()
        }

    def save(self, output_dir: str):
        """
        Save tokenizer to directory.

        Args:
            output_dir: Directory to save tokenizer
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save vocab
        with open(output_dir / "vocab.json", 'w', encoding='utf-8') as f:
            json.dump(self.vocab, f, ensure_ascii=False)

        # Save merges
        with open(output_dir / "merges.json", 'w', encoding='utf-8') as f:
            json.dump(self.merges, f, ensure_ascii=False)

        # Save metadata
        metadata = {
            "version": self.version,
            "vocab_size": self.vocab_size,
            "actual_vocab_size": len(self.vocab),
            "special_tokens": self.special_tokens,
            "special_token_ids": self.get_special_token_ids(),
            "num_merges": len(self.merges),
            "fixes": ["whitespace_preservation_v1.1.0"]
        }

        with open(output_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"[BPE Tokenizer] Saved to {output_dir}")

    def load(self, input_dir: str):
        """
        Load tokenizer from directory.

        Args:
            input_dir: Directory containing tokenizer files
        """
        input_dir = Path(input_dir)

        # Load vocab
        with open(input_dir / "vocab.json", 'r', encoding='utf-8') as f:
            self.vocab = {k: int(v) for k, v in json.load(f).items()}
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}

        # Load merges
        with open(input_dir / "merges.json", 'r', encoding='utf-8') as f:
            self.merges = [tuple(pair) for pair in json.load(f)]

        # Load metadata
        with open(input_dir / "metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            self.version = metadata["version"]
            self.special_tokens = metadata["special_tokens"]

        self.is_built = True
        print(f"[BPE Tokenizer] Loaded from {input_dir}")


if __name__ == "__main__":
    print("[BPE Tokenizer] Implementation ready (v1.1.0 with whitespace fix)")
    print("[BPE Tokenizer] Run test_bpe_tokenizer.py for testing")
