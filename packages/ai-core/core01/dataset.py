"""
NexusAI Core-01 Dataset Infrastructure

Provides reusable dataset loading, validation, and preprocessing for NexusAI Core-01.
"""

import torch
from torch.utils.data import Dataset, DataLoader
import json
import os
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import sys

# Add models directory to path for config import
ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(ai_core_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from nexusai_core_01.config.model_config import NexusAICore01Config
from .tokenizer_interface import NexusAITokenizer


@dataclass
class DatasetMetadata:
    """Metadata for dataset"""
    name: str
    version: str
    source: str
    license: str
    language: str
    size: int
    description: str


class TextDataset(Dataset):
    """
    Generic text dataset for language modeling.
    
    Supports raw text datasets that will be tokenized on-the-fly.
    """
    
    def __init__(
        self,
        texts: List[str],
        tokenizer: NexusAITokenizer,
        max_len: int = 512,
        pad_id: int = 0
    ):
        """
        Initialize dataset.
        
        Args:
            texts: List of text samples
            tokenizer: Tokenizer instance
            max_len: Maximum sequence length
            pad_id: Padding token ID
        """
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.pad_id = pad_id
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single training example.
        
        Returns:
            Dictionary with input_ids and targets
        """
        text = self.texts[idx]
        
        # Tokenize
        token_ids = self.tokenizer.encode(text, add_special_tokens=True, max_length=self.max_len)
        
        # Pad or truncate
        if len(token_ids) < self.max_len:
            token_ids = token_ids + [self.pad_id] * (self.max_len - len(token_ids))
        else:
            token_ids = token_ids[:self.max_len]
        
        # Shift for next-token prediction
        input_ids = torch.tensor(token_ids[:-1], dtype=torch.long)
        targets = torch.tensor(token_ids[1:], dtype=torch.long)
        
        return {
            "input_ids": input_ids,
            "targets": targets
        }


class TokenizedDataset(Dataset):
    """
    Dataset for pre-tokenized data.
    
    Used when data is already tokenized (e.g., from Phase 10).
    """
    
    def __init__(
        self,
        data_items: List[Dict[str, Any]],
        max_len: int = 512,
        pad_id: int = 0
    ):
        """
        Initialize dataset.
        
        Args:
            data_items: List of data items with "tokens" field
            max_len: Maximum sequence length
            pad_id: Padding token ID
        """
        self.data_items = data_items
        self.max_len = max_len
        self.pad_id = pad_id
    
    def __len__(self) -> int:
        return len(self.data_items)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single training example.
        
        Returns:
            Dictionary with input_ids and targets
        """
        item = self.data_items[idx]
        token_ids = item["tokens"]
        
        # Pad or truncate
        if len(token_ids) < self.max_len:
            token_ids = token_ids + [self.pad_id] * (self.max_len - len(token_ids))
        else:
            token_ids = token_ids[:self.max_len]
        
        # Shift for next-token prediction
        input_ids = torch.tensor(token_ids[:-1], dtype=torch.long)
        targets = torch.tensor(token_ids[1:], dtype=torch.long)
        
        return {
            "input_ids": input_ids,
            "targets": targets
        }


class DatasetLoader:
    """
    Dataset loader with validation and preprocessing.
    """
    
    def __init__(self, config: NexusAICore01Config):
        self.config = config
    
    def load_json_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load dataset from JSON file.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            List of data items
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def load_jsonl_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load dataset from JSONL file.
        
        Args:
            file_path: Path to JSONL file
        
        Returns:
            List of data items
        """
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        
        return data
    
    def split_dataset(
        self,
        dataset: List[Any],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        random_seed: int = 42
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """
        Split dataset into train/val/test.
        
        Args:
            dataset: Full dataset
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            random_seed: Random seed for reproducibility
        
        Returns:
            Tuple of (train, val, test) datasets
        """
        import random
        random.seed(random_seed)
        dataset = list(dataset)  # shuffle a copy; never mutate caller's list
        random.shuffle(dataset)
        
        n = len(dataset)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train = dataset[:train_end]
        val = dataset[train_end:val_end]
        test = dataset[val_end:]
        
        return train, val, test
    
    def create_dataloaders(
        self,
        train_dataset: Dataset,
        val_dataset: Dataset,
        test_dataset: Dataset,
        batch_size: int = 4,
        num_workers: int = 0,
        shuffle_train: bool = True
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Create PyTorch DataLoaders.
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            test_dataset: Test dataset
            batch_size: Batch size
            num_workers: Number of workers for data loading
            shuffle_train: Whether to shuffle training data
        
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=shuffle_train,
            num_workers=num_workers
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers
        )
        
        return train_loader, val_loader, test_loader
    
    def validate_dataset(self, dataset: List[Any]) -> Dict[str, Any]:
        """
        Validate dataset quality.
        
        Args:
            dataset: Dataset to validate
        
        Returns:
            Validation results
        """
        total = len(dataset)
        empty = sum(1 for item in dataset if not item)
        duplicates = total - len(set(str(item) for item in dataset))
        
        return {
            "total_samples": total,
            "empty_samples": empty,
            "duplicate_samples": duplicates,
            "valid_samples": total - empty
        }


class PackedTextDataset(Dataset):
    """
    Fixed-length packed dataset for efficient language-model pretraining.

    Instead of treating each text line as an independent example padded to
    max_len (which wastes most of the sequence on padding for short lines),
    this dataset concatenates the tokenized document stream and slices it
    into non-overlapping blocks of ``max_len + 1`` tokens. Each block yields
    ``input_ids = block[:-1]`` and ``targets = block[1:]`` (length max_len),
    matching the next-token-prediction convention used by TextDataset.

    Document boundaries: every document is encoded with BOS/EOS special
    tokens, so EOS->BOS transitions mark document boundaries inside a packed
    block. This is the standard GPT-style packing approach; tokens on one
    side of a boundary can still attend to tokens on the other side within
    the same block (accepted trade-off, same as most production LMs). Train/
    validation separation MUST therefore be performed at the document level
    BEFORE packing (see DatasetLoader.split_dataset) to prevent leakage.

    Token IDs are stored as a flat uint16 NumPy array (vocab 8,000 fits), so
    memory use is ~2 bytes/token regardless of text count.
    """

    def __init__(
        self,
        texts: List[str],
        tokenizer: NexusAITokenizer,
        max_len: int = 512,
        pad_id: int = 0,
        token_cache_path: Optional[str] = None
    ):
        """
        Args:
            texts: List of document texts (each becomes BOS..EOS in the stream)
            tokenizer: Tokenizer instance
            max_len: Sequence length for input_ids/targets
            pad_id: Padding token ID (used only for a trailing partial block)
            token_cache_path: Optional path to cache the packed uint16 token
                array as ``.npy``. If the file exists it is loaded instead of
                re-tokenizing (deterministic given the same texts+tokenizer).
        """
        self.max_len = max_len
        self.block_size = max_len + 1  # input + shifted target
        self.pad_id = pad_id
        self._num_blocks = 0

        cache_path = None
        meta_path = None
        if token_cache_path:
            cache_path = (
                token_cache_path
                if token_cache_path.endswith(".npy")
                else token_cache_path + ".npy"
            )
            meta_path = cache_path[:-4] + ".meta.json"

        fingerprint = self._compute_fingerprint(texts, tokenizer)

        if cache_path and self._cache_valid(cache_path, meta_path, fingerprint):
            try:
                self._tokens = np.load(cache_path)
                print(f"PackedTextDataset: reusing token cache "
                      f"({cache_path}) — provenance fingerprint match")
            except Exception as e:
                print(f"PackedTextDataset: cache load failed ({e}); rebuilding")
                self._tokens = self._tokenize(texts, tokenizer, cache_path, meta_path, fingerprint)
        else:
            reason = "no cache" if not (cache_path and os.path.exists(cache_path)) else "stale or missing provenance"
            if cache_path and os.path.exists(cache_path):
                print(f"PackedTextDataset: {reason} for {cache_path}; rebuilding tokens")
            self._tokens = self._tokenize(texts, tokenizer, cache_path, meta_path, fingerprint)

        n_tokens = len(self._tokens)
        n_full = n_tokens // self.block_size
        remainder = n_tokens % self.block_size
        # Keep a trailing partial block (padded) so no tokens are silently
        # dropped; pad targets are ignored by the loss (ignore_index=pad_id).
        self._num_blocks = n_full + (1 if remainder > 1 else 0)

    @staticmethod
    def _hash_texts(texts: List[str]) -> str:
        """Stable SHA-256 over the document list (order-sensitive)."""
        h = hashlib.sha256()
        for t in texts:
            b = (t or "").encode("utf-8")
            h.update(len(b).to_bytes(8, "little"))
            h.update(b)
        return h.hexdigest()

    @staticmethod
    def _hash_file(path: str) -> str:
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest()
        except OSError:
            return ""

    def _compute_fingerprint(
        self, texts: List[str], tokenizer: "NexusAITokenizer"
    ) -> Dict[str, Any]:
        """Provenance fingerprint: corpus + tokenizer + packing config."""
        tok_path = getattr(tokenizer, "tokenizer_path", "") or ""
        return {
            "version": 1,
            "texts_sha256": self._hash_texts(texts),
            "n_texts": len(texts),
            "tokenizer_path": tok_path,
            "tokenizer_sha256": self._hash_file(tok_path) if tok_path else "",
            "max_len": self.max_len,
            "pad_id": self.pad_id,
            "add_special_tokens": True,
        }

    @staticmethod
    def _cache_valid(cache_path: str, meta_path: str, fingerprint: Dict[str, Any]) -> bool:
        """True only if BOTH the .npy and its provenance metadata exist and match."""
        if not (os.path.exists(cache_path) and os.path.exists(meta_path)):
            return False
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            return meta.get("fingerprint") == fingerprint
        except Exception:
            return False

    def _tokenize(
        self,
        texts: List[str],
        tokenizer: "NexusAITokenizer",
        cache_path: Optional[str],
        meta_path: Optional[str],
        fingerprint: Dict[str, Any]
    ) -> np.ndarray:
        chunks = []
        for text in texts:
            if not text or not text.strip():
                continue  # skip empty/whitespace-only documents
            ids = tokenizer.encode(text, add_special_tokens=True)
            if ids:
                chunks.append(np.asarray(ids, dtype=np.uint16))
        if chunks:
            tokens = np.concatenate(chunks)
        else:
            tokens = np.zeros(0, dtype=np.uint16)
        if cache_path:
            os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
            np.save(cache_path, tokens)
            if meta_path:
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump({"fingerprint": fingerprint}, f, indent=1)
        return tokens

    def __len__(self) -> int:
        return self._num_blocks

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        start = idx * self.block_size
        block = self._tokens[start:start + self.block_size]
        if len(block) < self.block_size:
            block = np.concatenate(
                [block, np.full(self.block_size - len(block), self.pad_id, dtype=np.uint16)]
            )
        block = block.astype(np.int64)
        return {
            "input_ids": torch.from_numpy(block[:-1].copy()),
            "targets": torch.from_numpy(block[1:].copy())
        }

    @property
    def num_tokens(self) -> int:
        return int(len(self._tokens))

    @property
    def padding_token_count(self) -> int:
        """Number of pad tokens introduced by the single trailing partial block."""
        if self._num_blocks == 0:
            return 0
        used = self.num_tokens % self.block_size
        if used <= 1:
            return 0
        return self.block_size - used


class InstructionDataset(Dataset):
    """
    Dataset for instruction fine-tuning.
    
    Supports instruction-response pairs with proper formatting.
    """
    
    def __init__(
        self,
        instructions: List[str],
        responses: List[str],
        tokenizer: NexusAITokenizer,
        max_len: int = 512,
        pad_id: int = 0,
        mask_prompt: bool = False
    ):
        """
        Initialize instruction dataset.
        
        Args:
            instructions: List of instruction texts
            responses: List of response texts
            tokenizer: Tokenizer instance
            max_len: Maximum sequence length
            pad_id: Padding token ID
            mask_prompt: If True, compute loss only on response tokens
                (prompt/instruction positions are masked with pad_id, which
                the model's cross-entropy ignores via ignore_index).
                If False, trains on the full instruction+response sequence.
        """
        assert len(instructions) == len(responses), "Instructions and responses must have same length"
        
        self.instructions = instructions
        self.responses = responses
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.pad_id = pad_id
        self.mask_prompt = mask_prompt
    
    def __len__(self) -> int:
        return len(self.instructions)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single training example.
        
        Returns:
            Dictionary with input_ids and targets
        """
        instruction = self.instructions[idx]
        response = self.responses[idx]

        prompt_len = 0  # number of leading target positions to mask

        if self.mask_prompt:
            # Encode instruction and response separately so the prompt boundary
            # is exact. Sequence: [BOS] instr_tokens resp_tokens [EOS]
            instr_ids = self.tokenizer.encode(
                instruction, add_special_tokens=False
            )
            resp_ids = self.tokenizer.encode(
                response, add_special_tokens=False
            )
            token_ids = (
                [self.tokenizer.bos_id]
                + instr_ids
                + resp_ids
                + [self.tokenizer.eos_id]
            )
            # targets[t] = token_ids[t+1]; response tokens start at index
            # len(instr_ids)+1, so targets indices 0..len(instr_ids)-1 predict
            # instruction tokens and are masked. Always keep >=1 real target.
            prompt_len = len(instr_ids)
        else:
            # Format as: [BOS] instruction response [EOS]
            formatted = f"{instruction} {response}"
            token_ids = self.tokenizer.encode(
                formatted, add_special_tokens=True, max_length=self.max_len
            )
        
        # Pad or truncate
        if len(token_ids) < self.max_len:
            token_ids = token_ids + [self.pad_id] * (self.max_len - len(token_ids))
        else:
            token_ids = token_ids[:self.max_len]
        
        # Shift for next-token prediction
        input_ids = torch.tensor(token_ids[:-1], dtype=torch.long)
        targets = torch.tensor(token_ids[1:], dtype=torch.long)

        if self.mask_prompt and prompt_len > 0:
            # Mask prompt-prediction positions with pad_id (ignored by loss).
            # Clamp so at least the final target (usually EOS) stays real.
            k = min(prompt_len, max(0, targets.numel() - 1))
            if k > 0:
                targets[:k] = self.pad_id
        
        return {
            "input_ids": input_ids,
            "targets": targets
        }


if __name__ == "__main__":
    # Test dataset loading
    config = NexusAICore01Config()
    loader = DatasetLoader(config)
    
    # Create synthetic dataset for testing
    texts = [
        "Hello, how are you?",
        "What is your name?",
        "I am doing well.",
        "Tell me about yourself."
    ]
    
    dataset = TextDataset(texts, None, max_len=128, pad_id=config.pad_id)
    print(f"Dataset size: {len(dataset)}")
    print(f"Sample: {dataset[0]}")
