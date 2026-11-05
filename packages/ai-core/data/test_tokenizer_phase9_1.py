"""
Phase 9.1 - Tokenizer Compatibility Test

Tests the Phase 7 SentencePiece tokenizer on the newly acquired Bengali data.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"

# Add local datasets library to path
LOCAL_VENV = DATA_DIR / ".venv" / "lib" / "python3.14" / "site-packages"
sys.path.insert(0, str(LOCAL_VENV))

import sentencepiece as spm

# Paths
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
PHASE9_1_DIR = DATA_DIR / "experimental" / "phase9_1"
CLEANED_DIR = PHASE9_1_DIR / "cleaned"
EVALUATIONS_DIR = PHASE9_1_DIR / "evaluations"

print("="*60)
print("Phase 9.1 - Tokenizer Compatibility Test")
print("="*60)

# Load tokenizer
tokenizer_path = PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()

print(f"\nTokenizer loaded: {vocab_size} tokens")
print(f"Tokenizer path: {tokenizer_path}")

# Load cleaned data
combined_file = CLEANED_DIR / "combined_cleaned.jsonl"
with open(combined_file, 'r', encoding='utf-8') as f:
    records = [json.loads(line.strip()) for line in f]

print(f"Loaded {len(records)} records")

# Test sentences from new data
print(f"\n{'='*60}")
print("SAMPLE EVALUATION")
print(f"{'='*60}")

# Get sample Bengali records
bengali_samples = [r for r in records if r['language'] == 'bengali'][:5]
mixed_samples = [r for r in records if r['language'] == 'mixed'][:3]

print(f"\nBengali Samples:")
for i, record in enumerate(bengali_samples):
    text = record['text']
    ids = sp.encode(text, out_type=int)
    unk_count = ids.count(1)
    decoded = sp.decode(ids)
    print(f"\n  Sample {i+1}:")
    print(f"    Tokens: {len(ids)}, UNK: {unk_count} ({unk_count/len(ids)*100:.2f}%)")
    print(f"    Length: {len(text)} chars")

print(f"\nMixed Samples:")
for i, record in enumerate(mixed_samples):
    text = record['text']
    ids = sp.encode(text, out_type=int)
    unk_count = ids.count(1)
    decoded = sp.decode(ids)
    print(f"\n  Sample {i+1}:")
    print(f"    Tokens: {len(ids)}, UNK: {unk_count} ({unk_count/len(ids)*100:.2f}%)")
    print(f"    Length: {len(text)} chars")

# Corpus-wide evaluation
print(f"\n{'='*60}")
print("CORPUS-WIDE EVALUATION")
print(f"{'='*60}")

sample_size = min(500, len(records))
sample_records = records[:sample_size]

total_tokens = 0
total_unk = 0
bengali_tokens = 0
bengali_unk = 0
mixed_tokens = 0
mixed_unk = 0

import re

for record in sample_records:
    text = record['text']
    ids = sp.encode(text, out_type=int)
    unk_count = ids.count(1)
    total_tokens += len(ids)
    total_unk += unk_count

    lang = record['language']
    if lang == 'bengali':
        bengali_tokens += len(ids)
        bengali_unk += unk_count
    elif lang == 'mixed':
        mixed_tokens += len(ids)
        mixed_unk += unk_count

overall_unk_rate = total_unk / total_tokens if total_tokens > 0 else 0
bengali_unk_rate = bengali_unk / bengali_tokens if bengali_tokens > 0 else 0
mixed_unk_rate = mixed_unk / mixed_tokens if mixed_tokens > 0 else 0

print(f"\nSample size: {sample_size} records")
print(f"Total tokens: {total_tokens:,}")
print(f"Total UNK: {total_unk:,} ({overall_unk_rate:.2%})")
print(f"\nBengali tokens: {bengali_tokens:,}")
print(f"Bengali UNK: {bengali_unk:,} ({bengali_unk_rate:.2%})")
print(f"\nMixed tokens: {mixed_tokens:,}")
print(f"Mixed UNK: {mixed_unk:,} ({mixed_unk_rate:.2%})")

# Compare with Phase 9 evaluation
print(f"\n{'='*60}")
print("COMPARISON WITH PHASE 9 (OLD CORPUS)")
print(f"{'='*60}")
print(f"Phase 9 Bengali UNK rate: 48.38%")
print(f"Phase 9.1 Bengali UNK rate: {bengali_unk_rate:.2%}")
print(f"Improvement: {48.38 - bengali_unk_rate:.2f} percentage points")

# Save evaluation results
evaluation = {
    "evaluation_timestamp": datetime.now().isoformat(),
    "tokenizer": {
        "path": str(tokenizer_path),
        "vocab_size": vocab_size,
        "model_type": "BPE"
    },
    "corpus": {
        "path": str(combined_file),
        "total_records": len(records),
        "sample_size": sample_size
    },
    "corpus_sample": {
        "sample_size": sample_size,
        "total_tokens": total_tokens,
        "total_unk": total_unk,
        "overall_unk_rate": overall_unk_rate,
        "bengali_tokens": bengali_tokens,
        "bengali_unk": bengali_unk,
        "bengali_unk_rate": bengali_unk_rate,
        "mixed_tokens": mixed_tokens,
        "mixed_unk": mixed_unk,
        "mixed_unk_rate": mixed_unk_rate
    },
    "comparison": {
        "phase9_bengali_unk_rate": 0.4838,
        "phase9_1_bengali_unk_rate": bengali_unk_rate,
        "improvement_percentage_points": 0.4838 - bengali_unk_rate
    },
    "conclusions": [
        f"New Bengali UNK rate: {bengali_unk_rate:.2%}",
        f"Improvement over Phase 9: {0.4838 - bengali_unk_rate:.2f} percentage points",
        "UNK rate remains high - tokenizer retraining recommended",
        "More Bengali data would further improve tokenization"
    ]
}

eval_path = EVALUATIONS_DIR / "tokenizer_evaluation.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(evaluation, f, indent=2, ensure_ascii=False)

print(f"\nEvaluation saved: {eval_path}")

print(f"\n{'='*60}")
print("TOKENIZER EVALUATION COMPLETE")
print(f"{'='*60}")
