"""
NexusAI Core-01 Dataset Infrastructure

Provides reusable dataset loading, validation, and preprocessing for NexusAI Core-01.
"""

import torch
from torch.utils.data import Dataset, DataLoader
import json
import os
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
        pad_id: int = 0
    ):
        """
        Initialize instruction dataset.
        
        Args:
            instructions: List of instruction texts
            responses: List of response texts
            tokenizer: Tokenizer instance
            max_len: Maximum sequence length
            pad_id: Padding token ID
        """
        assert len(instructions) == len(responses), "Instructions and responses must have same length"
        
        self.instructions = instructions
        self.responses = responses
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.pad_id = pad_id
    
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
        
        # Format as: [BOS] instruction [response] [EOS]
        formatted = f"{instruction} {response}"
        
        # Tokenize
        token_ids = self.tokenizer.encode(formatted, add_special_tokens=True, max_length=self.max_len)
        
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
