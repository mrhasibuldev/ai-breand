"""
Phase 10 - Dataset Preparation

Prepares training data using the Phase 9.2 BPE 8K tokenizer.
"""

import json
import sys
import unicodedata
import random
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
PHASE10_DIR = DATA_DIR / "experimental" / "phase10"
DATASETS_DIR = PHASE10_DIR / "datasets"
MANIFESTS_DIR = PHASE10_DIR / "manifests"

# Create directories
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 10 - Dataset Preparation")
print("="*60)

import sentencepiece as spm

# Load tokenizer
tokenizer_path = PHASE9_2_DIR / "tokenizers" / "bpe_8k" / "sp_bpe_8k.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()

print(f"\nTokenizer loaded: {vocab_size} tokens")

# Load corpus
corpus_path = PHASE9_2_DIR / "corpus" / "combined.txt"
with open(corpus_path, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

print(f"Corpus loaded: {len(lines)} lines")

# Filter empty lines
lines = [line for line in lines if len(line) > 3]
print(f"After filtering: {len(lines)} lines")

# Deduplicate
seen = set()
unique_lines = []
for line in lines:
    if line not in seen:
        seen.add(line)
        unique_lines.append(line)

print(f"After deduplication: {len(unique_lines)} lines")

# Normalize and tokenize
tokenized_data = []
for line in unique_lines:
    normalized = unicodedata.normalize('NFC', line)
    ids = sp.encode(normalized, out_type=int)
    if len(ids) > 0:
        tokenized_data.append({
            'text': normalized,
            'tokens': ids,
            'length': len(ids)
        })

print(f"Tokenized: {len(tokenized_data)} examples")

# Count by language
import re
bengali_count = 0
english_count = 0
mixed_count = 0

for item in tokenized_data:
    text = item['text']
    bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if bengali_chars > 0 and latin_chars > 0:
        mixed_count += 1
    elif bengali_chars > 0:
        bengali_count += 1
    elif latin_chars > 0:
        english_count += 1

print(f"\nLanguage distribution:")
print(f"  Bengali: {bengali_count}")
print(f"  English: {english_count}")
print(f"  Mixed: {mixed_count}")

# Filter by length (keep reasonable lengths)
max_length = 128
filtered_data = [item for item in tokenized_data if item['length'] <= max_length]
print(f"\nAfter length filtering (max {max_length}): {len(filtered_data)} examples")

# Create train/validation/test splits
random.seed(42)
random.shuffle(filtered_data)

total = len(filtered_data)
train_size = int(0.8 * total)
val_size = int(0.1 * total)
test_size = total - train_size - val_size

train_data = filtered_data[:train_size]
val_data = filtered_data[train_size:train_size + val_size]
test_data = filtered_data[train_size + val_size:]

print(f"\nSplit:")
print(f"  Train: {len(train_data)} ({len(train_data)/total:.1%})")
print(f"  Validation: {len(val_data)} ({len(val_data)/total:.1%})")
print(f"  Test: {len(test_data)} ({len(test_data)/total:.1%})")

# Save datasets
train_path = DATASETS_DIR / "train.json"
val_path = DATASETS_DIR / "val.json"
test_path = DATASETS_DIR / "test.json"

with open(train_path, 'w', encoding='utf-8') as f:
    json.dump(train_data, f, indent=2, ensure_ascii=False)

with open(val_path, 'w', encoding='utf-8') as f:
    json.dump(val_data, f, indent=2, ensure_ascii=False)

with open(test_path, 'w', encoding='utf-8') as f:
    json.dump(test_data, f, indent=2, ensure_ascii=False)

print(f"\nDatasets saved:")
print(f"  Train: {train_path}")
print(f"  Validation: {val_path}")
print(f"  Test: {test_path}")

# Save manifest
manifest = {
    "preparation_timestamp": datetime.now().isoformat(),
    "tokenizer": {
        "path": str(tokenizer_path),
        "vocab_size": vocab_size
    },
    "corpus": {
        "path": str(corpus_path),
        "original_lines": len(lines),
        "unique_lines": len(unique_lines),
        "tokenized_examples": len(tokenized_data),
        "filtered_examples": len(filtered_data)
    },
    "language_distribution": {
        "bengali": bengali_count,
        "english": english_count,
        "mixed": mixed_count
    },
    "splits": {
        "train": len(train_data),
        "validation": len(val_data),
        "test": len(test_data),
        "total": len(filtered_data)
    },
    "random_seed": 42,
    "max_length": max_length,
    "normalization": "NFC"
}

manifest_path = MANIFESTS_DIR / "dataset_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest saved: {manifest_path}")

print("\n" + "="*60)
print("DATASET PREPARATION COMPLETE")
print("="*60)
