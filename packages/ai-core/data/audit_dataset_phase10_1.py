"""
Phase 10.1 - Dataset Count Reconciliation

Independently verifies dataset counts and language distribution.
"""

import json
import re
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent
PHASE10_DIR = DATA_DIR / "experimental" / "phase10"
DATASETS_DIR = PHASE10_DIR / "datasets"

print("="*60)
print("Phase 10.1 - Dataset Count Reconciliation")
print("="*60)

# Load datasets
with open(DATASETS_DIR / "train.json", 'r', encoding='utf-8') as f:
    train_data = json.load(f)

with open(DATASETS_DIR / "val.json", 'r', encoding='utf-8') as f:
    val_data = json.load(f)

with open(DATASETS_DIR / "test.json", 'r', encoding='utf-8') as f:
    test_data = json.load(f)

print(f"\nActual dataset sizes:")
print(f"  Train: {len(train_data)}")
print(f"  Validation: {len(val_data)}")
print(f"  Test: {len(test_data)}")
print(f"  Total: {len(train_data) + len(val_data) + len(test_data)}")

# Language classification function
def classify_language(text):
    bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if bengali_chars > 0 and latin_chars > 0:
        return 'mixed'
    elif bengali_chars > 0:
        return 'bengali'
    elif latin_chars > 0:
        return 'english'
    else:
        return 'unknown'

# Count by language
def count_languages(data):
    counts = {'bengali': 0, 'english': 0, 'mixed': 0, 'unknown': 0}
    for item in data:
        lang = classify_language(item['text'])
        counts[lang] += 1
    return counts

train_lang = count_languages(train_data)
val_lang = count_languages(val_data)
test_lang = count_languages(test_data)

print(f"\nTrain language distribution:")
for lang, count in train_lang.items():
    print(f"  {lang}: {count}")

print(f"\nValidation language distribution:")
for lang, count in val_lang.items():
    print(f"  {lang}: {count}")

print(f"\nTest language distribution:")
for lang, count in test_lang.items():
    print(f"  {lang}: {count}")

# Total language distribution
total_data = train_data + val_data + test_data
total_lang = count_languages(total_data)

print(f"\nTotal language distribution:")
for lang, count in total_lang.items():
    print(f"  {lang}: {count}")

# Duplicate check
def check_duplicates(data):
    texts = [item['text'] for item in data]
    return len(texts) - len(set(texts))

train_dups = check_duplicates(train_data)
val_dups = check_duplicates(val_data)
test_dups = check_duplicates(test_data)

print(f"\nDuplicate check:")
print(f"  Train duplicates: {train_dups}")
print(f"  Validation duplicates: {val_dups}")
print(f"  Test duplicates: {test_dups}")

# Cross-split overlap check
train_texts = set(item['text'] for item in train_data)
val_texts = set(item['text'] for item in val_data)
test_texts = set(item['text'] for item in test_data)

train_val_overlap = len(train_texts & val_texts)
train_test_overlap = len(train_texts & test_texts)
val_test_overlap = len(val_texts & test_texts)

print(f"\nCross-split overlap:")
print(f"  Train-Val overlap: {train_val_overlap}")
print(f"  Train-Test overlap: {train_test_overlap}")
print(f"  Val-Test overlap: {val_test_overlap}")

print("\n" + "="*60)
print("RECONCILIATION COMPLETE")
print("="*60)
