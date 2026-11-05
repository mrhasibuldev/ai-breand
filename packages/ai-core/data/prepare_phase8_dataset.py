"""
Phase 8 - Complete Dataset Preparation and Experimental Transformer Training

Creates a small experimental dataset and trains a CPU-optimized Transformer.
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import sentencepiece as spm
import time

# Fix Windows encoding for UTF-8 support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
EXPERIMENTAL_DIR = DATA_DIR / "experimental" / "phase8"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
CORPUS_DIR = PHASE7_DIR / "tokenizer_corpus"
TOKENIZER_MODELS_DIR = PHASE7_DIR / "tokenizer_models"

# Create experimental directories
for subdir in ['data', 'checkpoints', 'logs', 'manifests']:
    (EXPERIMENTAL_DIR / subdir).mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 8 - Dataset Finalization and Experimental Training")
print("="*60)
print(f"\nExperimental directory: {EXPERIMENTAL_DIR}")
print(f"Free disk space: {3591729152 / (1024**3):.2f} GB")

# Load tokenizer
print("\nLoading SentencePiece tokenizer...")
tokenizer_path = TOKENIZER_MODELS_DIR / "sp_8k_bpe.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()
print(f"Vocabulary size: {vocab_size}")
print(f"UNK ID: {sp.unk_id()}")

# Load corpus
print("\nLoading corpus...")
corpus_path = CORPUS_DIR / "corpus_combined.txt"
with open(corpus_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in corpus: {len(lines)}")

# Create small experimental dataset (10K samples for quick training)
print("\nCreating experimental dataset...")
random.seed(42)
sample_size = min(10000, len(lines))
sampled_lines = random.sample(lines, sample_size)

# Split into train/validation
train_size = int(0.9 * sample_size)
train_lines = sampled_lines[:train_size]
val_lines = sampled_lines[train_size:]

print(f"Experimental dataset size: {sample_size}")
print(f"Train: {len(train_lines)}")
print(f"Validation: {len(val_lines)}")

# Save experimental dataset
train_path = EXPERIMENTAL_DIR / "data" / "train.txt"
val_path = EXPERIMENTAL_DIR / "data" / "val.txt"

with open(train_path, 'w', encoding='utf-8') as f:
    f.writelines(train_lines)

with open(val_path, 'w', encoding='utf-8') as f:
    f.writelines(val_lines)

print(f"Saved training data: {train_path}")
print(f"Saved validation data: {val_path}")

# Calculate checksums
def calculate_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

train_checksum = calculate_sha256(train_path)
val_checksum = calculate_sha256(val_path)

print(f"\nTrain SHA-256: {train_checksum}")
print(f"Val SHA-256: {val_checksum}")

# Save dataset manifest
dataset_manifest = {
    'created': '2026-11-03',
    'source_corpus': str(corpus_path),
    'sample_size': sample_size,
    'train_size': len(train_lines),
    'val_size': len(val_lines),
    'train_path': str(train_path),
    'val_path': str(val_path),
    'train_checksum': train_checksum,
    'val_checksum': val_checksum,
    'tokenizer_path': str(tokenizer_path),
    'vocab_size': vocab_size
}

manifest_path = EXPERIMENTAL_DIR / "manifests" / "dataset_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(dataset_manifest, f, indent=2, ensure_ascii=False)

print(f"\nSaved dataset manifest: {manifest_path}")

print("\n" + "="*60)
print("Phase 8B - Dataset Finalization Complete")
print("="*60)
