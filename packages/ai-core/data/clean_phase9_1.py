"""
Phase 9.1 - Dataset Cleaning and Quality Control

Cleans and evaluates the acquired Bengali datasets.
"""

import json
import hashlib
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
RAW_DIR = PHASE9_1_DIR / "raw"
CLEANED_DIR = PHASE9_1_DIR / "cleaned"
MANIFESTS_DIR = PHASE9_1_DIR / "manifests"
EVALUATIONS_DIR = PHASE9_1_DIR / "evaluations"

# Create directories
CLEANED_DIR.mkdir(parents=True, exist_ok=True)
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.1 - Dataset Cleaning and Quality Control")
print("="*60)

# Language detection
def detect_language(text):
    bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(text)

    if total_chars == 0:
        return 'unknown'

    bengali_ratio = bengali_chars / total_chars
    latin_ratio = latin_chars / total_chars

    if bengali_ratio > 0.3 and latin_ratio > 0.1:
        return 'mixed'
    elif bengali_ratio > 0.3:
        return 'bengali'
    elif latin_ratio > 0.3:
        return 'english'
    else:
        return 'unknown'

# Process datasets
datasets = [
    "bengali_chat_conv",
    "bengali_sft_v1"
]

cleaning_results = {}
total_stats = {
    'bengali': 0,
    'english': 0,
    'mixed': 0,
    'unknown': 0,
    'total_records': 0,
    'total_words': 0,
    'total_chars': 0
}

for dataset_name in datasets:
    print(f"\n{'='*60}")
    print(f"Processing: {dataset_name}")
    print(f"{'='*60}")

    raw_file = RAW_DIR / f"{dataset_name}.jsonl"

    if not raw_file.exists():
        print(f"ERROR: File not found: {raw_file}")
        continue

    # Load raw data
    with open(raw_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Raw records: {len(lines)}")

    # Parse and clean
    cleaned_records = []
    language_counts = {'bengali': 0, 'english': 0, 'mixed': 0, 'unknown': 0}
    duplicates_removed = 0
    empty_removed = 0
    seen_texts = set()

    for line in lines:
        try:
            record = json.loads(line.strip())

            # Extract text based on dataset structure
            if dataset_name == "bengali_chat_conv":
                # Structure: {"Question": "...", "Answer": "..."}
                question = record.get('Question', '').strip()
                answer = record.get('Answer', '').strip()
                text = f"{question} {answer}".strip()
            elif dataset_name == "bengali_sft_v1":
                # Structure: {"instruction": "...", "output": "..."}
                instruction = record.get('instruction', '').strip()
                output = record.get('output', '').strip()
                text = f"{instruction} {output}".strip()
            else:
                text = str(record).strip()

            # Skip empty
            if not text or len(text) < 3:
                empty_removed += 1
                continue

            # Skip duplicates
            if text in seen_texts:
                duplicates_removed += 1
                continue
            seen_texts.add(text)

            # Detect language
            lang = detect_language(text)
            language_counts[lang] += 1

            # Add to cleaned records
            cleaned_records.append({
                'text': text,
                'language': lang,
                'source': dataset_name
            })

        except Exception as e:
            print(f"Error parsing line: {e}")
            continue

    print(f"Cleaned records: {len(cleaned_records)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Empty removed: {empty_removed}")
    print(f"Language distribution: {language_counts}")

    # Save cleaned data
    cleaned_file = CLEANED_DIR / f"{dataset_name}_cleaned.jsonl"
    with open(cleaned_file, 'w', encoding='utf-8') as f:
        for record in cleaned_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    # Calculate checksum
    with open(cleaned_file, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    file_size = cleaned_file.stat().st_size

    print(f"Saved: {cleaned_file}")
    print(f"Size: {file_size / 1024:.2f} KB")
    print(f"SHA-256: {file_hash[:16]}...")

    # Update total stats
    for record in cleaned_records:
        lang = record['language']
        text = record['text']
        total_stats[lang] += 1
        total_stats['total_records'] += 1
        total_stats['total_words'] += len(text.split())
        total_stats['total_chars'] += len(text)

    cleaning_results[dataset_name] = {
        'raw_records': len(lines),
        'cleaned_records': len(cleaned_records),
        'duplicates_removed': duplicates_removed,
        'empty_removed': empty_removed,
        'language_distribution': language_counts,
        'file_path': str(cleaned_file),
        'file_size_bytes': file_size,
        'sha256': file_hash
    }

# Create combined cleaned corpus
print(f"\n{'='*60}")
print("Creating Combined Cleaned Corpus")
print(f"{'='*60}")

all_cleaned = []
for dataset_name in datasets:
    cleaned_file = CLEANED_DIR / f"{dataset_name}_cleaned.jsonl"
    if cleaned_file.exists():
        with open(cleaned_file, 'r', encoding='utf-8') as f:
            for line in f:
                all_cleaned.append(json.loads(line.strip()))

combined_file = CLEANED_DIR / "combined_cleaned.jsonl"
with open(combined_file, 'w', encoding='utf-8') as f:
    for record in all_cleaned:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

print(f"Combined records: {len(all_cleaned)}")
print(f"Saved: {combined_file}")

# Save cleaning manifest
manifest = {
    "cleaning_timestamp": datetime.now().isoformat(),
    "datasets_processed": datasets,
    "cleaning_results": cleaning_results,
    "total_statistics": total_stats,
    "combined_corpus": {
        "file_path": str(combined_file),
        "total_records": len(all_cleaned)
    }
}

manifest_path = MANIFESTS_DIR / "cleaning_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest saved: {manifest_path}")

print(f"\n{'='*60}")
print("CLEANING COMPLETE")
print(f"{'='*60}")
print(f"\nTotal Bengali records: {total_stats['bengali']}")
print(f"Total English records: {total_stats['english']}")
print(f"Total Mixed records: {total_stats['mixed']}")
print(f"Total words: {total_stats['total_words']:,}")
