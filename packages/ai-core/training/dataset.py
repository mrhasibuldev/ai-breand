"""
Dataset Module

Dataset loader and collation for training.
"""

import torch
from torch.utils.data import Dataset
from typing import List, Dict
import json


class TextDataset(Dataset):
    """
    Simple text dataset for training.
    """

    def __init__(self, texts: List[str], tokenizer, max_len: int = 256):
        """
        Initialize dataset.

        Args:
            texts: List of text samples
            tokenizer: Tokenizer instance
            max_len: Maximum sequence length
        """
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self) -> int:
        """Return dataset size"""
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single training sample.

        Args:
            idx: Sample index

        Returns:
            Dictionary with input_ids and targets
        """
        text = self.texts[idx]

        # Encode text
        token_ids = self.tokenizer.encode(text, add_special_tokens=True)

        # Truncate or pad to max_len
        if len(token_ids) > self.max_len:
            token_ids = token_ids[:self.max_len]
        else:
            # Pad with PAD token
            pad_id = self.tokenizer.word_to_id[self.tokenizer.PAD_TOKEN]
            token_ids = token_ids + [pad_id] * (self.max_len - len(token_ids))

        # For next-token prediction, targets are shifted inputs
        input_ids = torch.tensor(token_ids[:-1], dtype=torch.long)
        targets = torch.tensor(token_ids[1:], dtype=torch.long)

        return {
            "input_ids": input_ids,
            "targets": targets
        }


def load_json_dataset(path: str) -> List[str]:
    """
    Load dataset from JSON file.

    Args:
        path: Path to JSON file

    Returns:
        List of text samples
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []
    for item in data:
        if isinstance(item, str):
            texts.append(item)
        elif isinstance(item, dict):
            if "text" in item:
                texts.append(item["text"])
            elif "question" in item and "answer" in item:
                texts.append(f"{item['question']} {item['answer']}")
            elif "messages" in item:
                # Concatenate conversation
                conversation = " ".join([msg["content"] for msg in item["messages"]])
                texts.append(conversation)

    return texts
