"""
Phase 9.1 - Language and Quality Evaluation

Evaluates the cleaned datasets and calculates detailed statistics.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_1_DIR = DATA_DIR / "experimental" / "phase9_1"
CLEANED_DIR = PHASE9_1_DIR / "cleaned"
MANIFESTS_DIR = PHASE9_1_DIR / "manifests"
EVALUATIONS_DIR = PHASE9_1_DIR / "evaluations"

print("="*60)
print("Phase 9.1 - Language and Quality Evaluation")
print("="*60)

# Load combined cleaned corpus
combined_file = CLEANED_DIR / "combined_cleaned.jsonl"

with open(combined_file, 'r', encoding='utf-8') as f:
    records = [json.loads(line.strip()) for line in f]

print(f"\nTotal records: {len(records)}")

# Categorize by type
conversations = []
instructions = []
qa_pairs = []

for record in records:
    source = record['source']
    if source == 'bengali_chat_conv':
        conversations.append(record)
    elif source == 'bengali_sft_v1':
        instructions.append(record)

print(f"\nConversations (bengali_chat_conv): {len(conversations)}")
print(f"Instructions (bengali_sft_v1): {len(instructions)}")

# Calculate detailed statistics
stats = {
    'total_records': len(records),
    'by_language': {
        'bengali': 0,
        'english': 0,
        'mixed': 0,
        'unknown': 0
    },
    'by_type': {
        'conversations': len(conversations),
        'instructions': len(instructions)
    },
    'word_counts': {
        'bengali': 0,
        'english': 0,
        'mixed': 0,
        'total': 0
    },
    'char_counts': {
        'bengali': 0,
        'english': 0,
        'mixed': 0,
        'total': 0
    }
}

for record in records:
    lang = record['language']
    text = record['text']
    words = len(text.split())
    chars = len(text)

    stats['by_language'][lang] += 1
    stats['word_counts'][lang] += words
    stats['char_counts'][lang] += chars
    stats['word_counts']['total'] += words
    stats['char_counts']['total'] += chars

print(f"\n{'='*60}")
print("LANGUAGE DISTRIBUTION")
print(f"{'='*60}")
for lang, count in stats['by_language'].items():
    if count > 0:
        words = stats['word_counts'][lang]
        chars = stats['char_counts'][lang]
        percentage = (count / stats['total_records']) * 100
        print(f"{lang}: {count} records ({percentage:.2f}%), {words:,} words, {chars:,} chars")

print(f"\n{'='*60}")
print("TYPE DISTRIBUTION")
print(f"{'='*60}")
for dtype, count in stats['by_type'].items():
    if count > 0:
        percentage = (count / stats['total_records']) * 100
        print(f"{dtype}: {count} records ({percentage:.2f}%)")

print(f"\n{'='*60}")
print("TOTAL STATISTICS")
print(f"{'='*60}")
print(f"Total records: {stats['total_records']}")
print(f"Total words: {stats['word_counts']['total']:,}")
print(f"Total characters: {stats['char_counts']['total']:,}")
print(f"Average words per record: {stats['word_counts']['total'] / stats['total_records']:.2f}")
print(f"Average chars per record: {stats['char_counts']['total'] / stats['total_records']:.2f}")

# Check against targets
print(f"\n{'='*60}")
print("TARGET PROGRESS")
print(f"{'='*60}")
print(f"First milestone (5,000 Bengali words): {'✓ ACHIEVED' if stats['word_counts']['bengali'] >= 5000 else '✗ NOT MET'}")
print(f"  Current: {stats['word_counts']['bengali']:,} Bengali words")
print(f"Second milestone (20,000 Bengali words): {'✓ ACHIEVED' if stats['word_counts']['bengali'] >= 20000 else '✗ NOT MET'}")
print(f"  Current: {stats['word_counts']['bengali']:,} Bengali words")
print(f"Long-term target (100,000+ Bengali words): {'✓ ACHIEVED' if stats['word_counts']['bengali'] >= 100000 else '✗ NOT MET'}")
print(f"  Current: {stats['word_counts']['bengali']:,} Bengali words")

# Save evaluation results
evaluation = {
    "evaluation_timestamp": datetime.now().isoformat(),
    "statistics": stats,
    "target_progress": {
        "first_milestone_5000_words": {
            "target": 5000,
            "current": stats['word_counts']['bengali'],
            "achieved": stats['word_counts']['bengali'] >= 5000
        },
        "second_milestone_20000_words": {
            "target": 20000,
            "current": stats['word_counts']['bengali'],
            "achieved": stats['word_counts']['bengali'] >= 20000
        },
        "long_term_100000_words": {
            "target": 100000,
            "current": stats['word_counts']['bengali'],
            "achieved": stats['word_counts']['bengali'] >= 100000
        }
    },
    "conclusions": [
        f"First milestone achieved: {stats['word_counts']['bengali']:,} Bengali words",
        f"Second milestone NOT achieved: need {20000 - stats['word_counts']['bengali']:,} more Bengali words",
        f"Long-term target NOT achieved: need {100000 - stats['word_counts']['bengali']:,} more Bengali words",
        "Conversations provide everyday Bengali language",
        "Instructions provide task-oriented Bengali language",
        "Recommendation: Acquire more Bengali datasets to reach 20K+ words"
    ]
}

eval_path = EVALUATIONS_DIR / "language_evaluation.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(evaluation, f, indent=2, ensure_ascii=False)

print(f"\nEvaluation saved: {eval_path}")

print(f"\n{'='*60}")
print("EVALUATION COMPLETE")
print(f"{'='*60}")
