"""
Public Domain Data Collector

Downloads and processes public domain datasets for NexusAI training.
Sources:
- Project Gutenberg (English public domain books)
- B-CORE Bengali Corpus (CC BY 4.0)
- ManikKatha (CC0 Bengali literary corpus)
"""

import os
import sys
import json
import random
from typing import List, Dict
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class PublicDataCollector:
    """Collect public domain data for training"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_sample_from_local_files(
        self,
        file_paths: List[str],
        max_samples: int = 1000,
        output_name: str = "public_dataset"
    ) -> Dict[str, any]:
        """
        Collect samples from local files (for testing without download)
        
        Args:
            file_paths: List of file paths to read from
            max_samples: Maximum number of samples to collect
            output_name: Name for the output dataset
        """
        all_texts = []
        
        for file_path in file_paths:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_texts.extend(data)
                        elif isinstance(data, dict) and 'text' in data:
                            all_texts.append(data['text'])
                elif file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Split by paragraphs
                        text = f.read()
                        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                        all_texts.extend(paragraphs)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        # Shuffle and limit
        random.shuffle(all_texts)
        all_texts = all_texts[:max_samples]
        
        # Save
        output_path = self.output_dir / f"{output_name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_texts, f, ensure_ascii=False, indent=2)
        
        return {
            "name": output_name,
            "samples": len(all_texts),
            "path": str(output_path),
            "sources": file_paths
        }
    
    def create_conversational_samples(
        self,
        text_samples: List[str],
        max_pairs: int = 500
    ) -> List[Dict[str, str]]:
        """
        Create conversational Q&A pairs from text samples
        This is a simple heuristic approach for training data
        """
        conversations = []
        
        # Simple pattern: take adjacent sentences as Q&A
        for i in range(0, min(len(text_samples) - 1, max_pairs)):
            # Alternate between Q and A
            if i % 2 == 0:
                conversations.append({
                    "question": text_samples[i][:200],  # Limit length
                    "answer": text_samples[i + 1][:200]
                })
        
        return conversations
    
    def split_dataset(
        self,
        samples: List[str],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1
    ) -> Dict[str, List[str]]:
        """
        Split dataset into train/validation/test
        
        Args:
            samples: List of text samples
            train_ratio: Training data ratio
            val_ratio: Validation data ratio
            test_ratio: Test data ratio
        """
        random.shuffle(samples)
        total = len(samples)
        
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        return {
            "train": samples[:train_end],
            "validation": samples[train_end:val_end],
            "test": samples[val_end:]
        }
    
    def save_versioned_dataset(
        self,
        splits: Dict[str, List[str]],
        version: str = "v1.0",
        metadata: Dict = None
    ):
        """
        Save dataset with version control
        
        Args:
            splits: Dictionary with train/validation/test splits
            version: Version string
            metadata: Additional metadata to save
        """
        version_dir = self.output_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save splits
        for split_name, split_data in splits.items():
            with open(version_dir / f"{split_name}.json", 'w', encoding='utf-8') as f:
                json.dump(split_data, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata = metadata or {}
        metadata.update({
            "version": version,
            "train_samples": len(splits["train"]),
            "val_samples": len(splits["validation"]),
            "test_samples": len(splits["test"]),
            "total_samples": len(splits["train"]) + len(splits["validation"]) + len(splits["test"])
        })
        
        with open(version_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] Saved version {version} to {version_dir}")
        print(f"   Train: {metadata['train_samples']}")
        print(f"   Validation: {metadata['val_samples']}")
        print(f"   Test: {metadata['test_samples']}")


def main():
    """Main function to collect and prepare public domain data"""
    
    # Initialize collector with absolute path
    script_dir = Path(__file__).parent
    output_dir = script_dir / "public_datasets"
    collector = PublicDataCollector(str(output_dir))
    
    # Use existing sample dataset as base
    sample_file = script_dir / "user_data" / "sample_dataset.json"
    
    # If sample file doesn't exist, create a simple one
    if not sample_file.exists():
        print(f"Sample file not found, creating one...")
        sample_file.parent.mkdir(parents=True, exist_ok=True)
        sample_data = [
            "তোমার নাম কি?",
            "আমার নাম NexusAI।",
            "তুমি কী করতে পারো?",
            "আমি তোমার সঙ্গে কথোপকথন করতে পারি।",
            "What is your name?",
            "My name is NexusAI.",
            "What can you do?",
            "I can have conversations and help you."
        ]
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    # Collect samples
    result = collector.collect_sample_from_local_files(
        file_paths=[str(sample_file)],
        max_samples=500,
        output_name="bengali_english_mixed"
    )
    
    print(f"[OK] Collected {result['samples']} samples")
    
    # Load the collected data
    with open(result['path'], 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    # Split dataset
    splits = collector.split_dataset(samples, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)
    
    # Save versioned dataset
    collector.save_versioned_dataset(
        splits,
        version="v1.0",
        metadata={
            "source": "NexusAI sample dataset",
            "languages": ["Bengali", "English", "Mixed"],
            "created": "2025",
            "license": "Internal"
        }
    )


if __name__ == "__main__":
    main()
