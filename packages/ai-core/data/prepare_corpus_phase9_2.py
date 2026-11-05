"""
Phase 9.2 - Corpus Preparation

Builds reproducible tokenizer training corpora from Phase 9.1 and Phase 7 data.
"""

import json
import unicodedata
import sys
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
PHASE9_1_DIR = DATA_DIR / "experimental" / "phase9_1"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
CORPUS_DIR = PHASE9_2_DIR / "corpus"
MANIFESTS_DIR = PHASE9_2_DIR / "manifests"

# Create directories
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.2 - Corpus Preparation")
print("="*60)

# Unicode normalization
def normalize_text(text):
    return unicodedata.normalize('NFC', text)

# Load Phase 9.1 cleaned data
phase9_1_combined = PHASE9_1_DIR / "cleaned" / "combined_cleaned.jsonl"
with open(phase9_1_combined, 'r', encoding='utf-8') as f:
    phase9_1_records = [json.loads(line.strip()) for line in f]

print(f"\nLoaded Phase 9.1: {len(phase9_1_records)} records")

# Load Phase 7 corpus (for English balance)
phase7_combined = PHASE7_DIR / "tokenizer_corpus" / "corpus_combined.txt"
with open(phase7_combined, 'r', encoding='utf-8') as f:
    phase7_lines = [line.strip() for line in f if line.strip()]

print(f"Loaded Phase 7: {len(phase7_lines)} lines")

# Separate Phase 9.1 by language
bengali_texts = []
english_texts = []
mixed_texts = []

for record in phase9_1_records:
    text = normalize_text(record['text'])
    lang = record['language']
    
    if lang == 'bengali':
        bengali_texts.append(text)
    elif lang == 'english':
        english_texts.append(text)
    elif lang == 'mixed':
        mixed_texts.append(text)

print(f"\nPhase 9.1 Language Distribution:")
print(f"  Bengali: {len(bengali_texts)}")
print(f"  English: {len(english_texts)}")
print(f"  Mixed: {len(mixed_texts)}")

# Sample English from Phase 7 to balance corpus
# We want Bengali to have ~30-40% of the corpus for multilingual tokenizer
import random
random.seed(42)  # Deterministic seed

target_total = len(bengali_texts) + len(mixed_texts) + len(english_texts)
target_english_ratio = 0.6  # English should be ~60% of total
target_english_count = int((len(bengali_texts) + len(mixed_texts)) * target_english_ratio / (1 - target_english_ratio))

# Sample English from Phase 7
phase7_english_sample = random.sample(phase7_lines, min(target_english_count, len(phase7_lines)))
phase7_english_sample = [normalize_text(text) for text in phase7_english_sample]

print(f"\nSampled English from Phase 7: {len(phase7_english_sample)} lines")

# Combine
all_bengali = bengali_texts
all_english = english_texts + phase7_english_sample
all_mixed = mixed_texts

print(f"\nFinal Corpus Distribution:")
print(f"  Bengali: {len(all_bengali)} texts")
print(f"  English: {len(all_english)} texts")
print(f"  Mixed: {len(all_mixed)} texts")
print(f"  Total: {len(all_bengali) + len(all_english) + len(all_mixed)} texts")

# Save separate corpora
bengali_file = CORPUS_DIR / "bengali.txt"
with open(bengali_file, 'w', encoding='utf-8') as f:
    for text in all_bengali:
        f.write(text + '\n')

english_file = CORPUS_DIR / "english.txt"
with open(english_file, 'w', encoding='utf-8') as f:
    for text in all_english:
        f.write(text + '\n')

mixed_file = CORPUS_DIR / "mixed.txt"
with open(mixed_file, 'w', encoding='utf-8') as f:
    for text in all_mixed:
        f.write(text + '\n')

# Save combined corpus for SentencePiece training
combined_file = CORPUS_DIR / "combined.txt"
with open(combined_file, 'w', encoding='utf-8') as f:
    # Mix Bengali, English, and Mixed
    combined_texts = all_bengali + all_english + all_mixed
    random.shuffle(combined_texts)  # Shuffle for better training
    for text in combined_texts:
        f.write(text + '\n')

print(f"\nCorpus files saved:")
print(f"  Bengali: {bengali_file}")
print(f"  English: {english_file}")
print(f"  Mixed: {mixed_file}")
print(f"  Combined: {combined_file}")

# Calculate statistics
bengali_words = sum(len(text.split()) for text in all_bengali)
english_words = sum(len(text.split()) for text in all_english)
mixed_words = sum(len(text.split()) for text in all_mixed)
total_words = bengali_words + english_words + mixed_words

print(f"\nCorpus Statistics:")
print(f"  Bengali words: {bengali_words:,}")
print(f"  English words: {english_words:,}")
print(f"  Mixed words: {mixed_words:,}")
print(f"  Total words: {total_words:,}")

# Save manifest
manifest = {
    "preparation_timestamp": datetime.now().isoformat(),
    "normalization": "NFC",
    "random_seed": 42,
    "sources": {
        "phase9_1": {
            "records": len(phase9_1_records),
            "bengali": len(bengali_texts),
            "english": len(english_texts),
            "mixed": len(mixed_texts)
        },
        "phase7": {
            "total_lines": len(phase7_lines),
            "sampled_english": len(phase7_english_sample)
        }
    },
    "final_corpus": {
        "bengali_texts": len(all_bengali),
        "english_texts": len(all_english),
        "mixed_texts": len(all_mixed),
        "total_texts": len(all_bengali) + len(all_english) + len(all_mixed),
        "bengali_words": bengali_words,
        "english_words": english_words,
        "mixed_words": mixed_words,
        "total_words": total_words
    },
    "files": {
        "bengali": str(bengali_file),
        "english": str(english_file),
        "mixed": str(mixed_file),
        "combined": str(combined_file)
    }
}

manifest_path = MANIFESTS_DIR / "corpus_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest saved: {manifest_path}")

print("\n" + "="*60)
print("CORPUS PREPARATION COMPLETE")
print("="*60)
