"""
Dataset Builder

Helper script to prepare training datasets from user data.
Usage: python prepare_dataset.py --input <path> --output <path>
"""

import argparse
import os
import json
from typing import List
from importer import DataImporter


def prepare_conversational_dataset(
    input_texts: List[str],
    output_path: str,
    train_ratio: float = 0.8
) -> None:
    """
    Prepare training dataset with train/validation split
    
    Args:
        input_texts: List of text samples
        output_path: Path to save dataset JSON
        train_ratio: Ratio for training data (default 0.8)
    """
    # Shuffle texts
    import random
    random.shuffle(input_texts)
    
    # Split
    split_idx = int(len(input_texts) * train_ratio)
    train_texts = input_texts[:split_idx]
    val_texts = input_texts[split_idx:]
    
    # Save datasets
    output_dir = os.path.dirname(output_path)
    train_path = os.path.join(output_dir, 'train.json')
    val_path = os.path.join(output_dir, 'validation.json')
    
    with open(train_path, 'w', encoding='utf-8') as f:
        json.dump(train_texts, f, ensure_ascii=False, indent=2)
    
    with open(val_path, 'w', encoding='utf-8') as f:
        json.dump(val_texts, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dataset prepared:")
    print(f"   Training samples: {len(train_texts)}")
    print(f"   Validation samples: {len(val_texts)}")
    print(f"   Train data: {train_path}")
    print(f"   Validation data: {val_path}")


def main():
    parser = argparse.ArgumentParser(description='Prepare dataset for NexusAI training')
    parser.add_argument('--input', required=True, help='Input data file or directory')
    parser.add_argument('--output', required=True, help='Output directory for prepared dataset')
    parser.add_argument('--format', choices=['json', 'csv', 'txt', 'auto'], default='auto', help='Input format')
    parser.add_argument('--train-ratio', type=float, default=0.8, help='Training data ratio (default: 0.8)')
    
    args = parser.parse_args()
    
    # Import data
    print(f"📥 Importing data from: {args.input}")
    
    if os.path.isdir(args.input):
        texts = DataImporter.import_directory(args.input)
    elif args.format == 'json' or (args.format == 'auto' and args.input.endswith('.json')):
        texts = DataImporter.import_json(args.input)
    elif args.format == 'csv' or (args.format == 'auto' and args.input.endswith('.csv')):
        texts = DataImporter.import_csv(args.input)
    elif args.format == 'txt' or (args.format == 'auto' and args.input.endswith('.txt')):
        texts = DataImporter.import_txt(args.input)
    else:
        raise ValueError(f"Unsupported format: {args.input}")
    
    print(f"✅ Imported {len(texts)} text samples")
    
    # Check minimum requirement
    if len(texts) < 10:
        print(f"⚠️  Warning: Only {len(texts)} samples. Minimum 100 recommended for meaningful training.")
    
    # Prepare dataset
    os.makedirs(args.output, exist_ok=True)
    prepare_conversational_dataset(texts, args.output, args.train_ratio)


if __name__ == '__main__':
    main()
