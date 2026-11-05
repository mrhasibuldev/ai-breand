"""
NexusAI Phase 5B Data Quality Checker
Performs quality checks, duplicate detection, and language analysis
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "collected" / "raw"
CLEANED_DIR = BASE_DIR / "collected" / "cleaned"
APPROVED_DIR = BASE_DIR / "collected" / "approved"
MANIFESTS_DIR = BASE_DIR / "collected" / "manifests"

def load_jsonl(file_path: Path) -> List[Dict]:
    """Load a JSONL file"""
    records = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except Exception as e:
        print(f"[Quality] Error loading {file_path}: {e}")
    return records

def check_quality(records: List[Dict], dataset_name: str) -> Dict:
    """Perform quality checks on records"""
    stats = {
        "total_records": len(records),
        "empty_records": 0,
        "missing_fields": 0,
        "invalid_json": 0,
        "short_records": 0,
        "duplicate_content": 0,
        "utf8_errors": 0
    }

    content_hashes = set()

    for i, record in enumerate(records):
        # Check for empty records
        if not record or len(record) == 0:
            stats["empty_records"] += 1
            continue

        # Check for missing required fields (depends on dataset)
        if dataset_name == "GSM8K":
            if "question" not in record or "answer" not in record:
                stats["missing_fields"] += 1
        elif dataset_name == "Dolly":
            if "instruction" not in record or "response" not in record:
                stats["missing_fields"] += 1

        # Check for very short content
        content = str(record)
        if len(content) < 10:
            stats["short_records"] += 1

        # Check for duplicate content
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if content_hash in content_hashes:
            stats["duplicate_content"] += 1
        else:
            content_hashes.add(content_hash)

    return stats

def detect_duplicates(records: List[Dict], dataset_name: str) -> Dict:
    """Detect duplicate records"""
    seen_questions = set()
    duplicates = []

    for i, record in enumerate(records):
        if dataset_name == "GSM8K":
            question = record.get("question", "")
        elif dataset_name == "Dolly":
            question = record.get("instruction", "")
        else:
            continue

        question_hash = hashlib.md5(question.encode('utf-8')).hexdigest()
        if question_hash in seen_questions:
            duplicates.append({
                "index": i,
                "question": question[:100]  # First 100 chars
            })
        else:
            seen_questions.add(question_hash)

    return {
        "total_duplicates": len(duplicates),
        "duplicate_indices": [d["index"] for d in duplicates[:10]]  # First 10
    }

def analyze_language(records: List[Dict], dataset_name: str) -> Dict:
    """Analyze language distribution"""
    bengali_count = 0
    english_count = 0
    mixed_count = 0
    other_count = 0

    for record in records:
        if dataset_name == "GSM8K":
            text = record.get("question", "") + " " + record.get("answer", "")
        elif dataset_name == "Dolly":
            text = record.get("instruction", "") + " " + record.get("response", "")
        else:
            continue

        # Simple language detection using Unicode ranges
        bengali_chars = sum(1 for c in text if 0x0980 <= ord(c) <= 0x09FF)
        latin_chars = sum(1 for c in text if (0x0041 <= ord(c) <= 0x005A) or (0x0061 <= ord(c) <= 0x007A))

        if bengali_chars > 0 and latin_chars > 0:
            mixed_count += 1
        elif bengali_chars > 0:
            bengali_count += 1
        elif latin_chars > 0:
            english_count += 1
        else:
            other_count += 1

    return {
        "bengali": bengali_count,
        "english": english_count,
        "mixed": mixed_count,
        "other": other_count
    }

def count_words(records: List[Dict], dataset_name: str) -> Dict:
    """Count words in records"""
    total_words = 0
    total_chars = 0

    for record in records:
        if dataset_name == "GSM8K":
            text = record.get("question", "") + " " + record.get("answer", "")
        elif dataset_name == "Dolly":
            text = record.get("instruction", "") + " " + record.get("response", "")
        else:
            continue

        words = text.split()
        total_words += len(words)
        total_chars += len(text)

    return {
        "total_words": total_words,
        "total_chars": total_chars,
        "avg_words_per_record": total_words / len(records) if records else 0
    }

def main():
    """Main quality check function"""
    print("=" * 60)
    print("NexusAI Phase 5B Data Quality Checker")
    print("=" * 60)

    quality_report = {
        "check_timestamp": "2026-11-03T18:45:00",
        "datasets": {}
    }

    # Check GSM8K
    print("\n[Quality] Checking GSM8K...")
    gsm8k_train = load_jsonl(RAW_DIR / "gsm8k" / "gsm8k_train.jsonl")
    gsm8k_test = load_jsonl(RAW_DIR / "gsm8k" / "gsm8k_test.jsonl")
    gsm8k_all = gsm8k_train + gsm8k_test

    print(f"[Quality] GSM8K Train: {len(gsm8k_train)} records")
    print(f"[Quality] GSM8K Test: {len(gsm8k_test)} records")
    print(f"[Quality] GSM8K Total: {len(gsm8k_all)} records")

    gsm8k_quality = check_quality(gsm8k_all, "GSM8K")
    gsm8k_duplicates = detect_duplicates(gsm8k_all, "GSM8K")
    gsm8k_language = analyze_language(gsm8k_all, "GSM8K")
    gsm8k_words = count_words(gsm8k_all, "GSM8K")

    quality_report["datasets"]["gsm8k"] = {
        "quality": gsm8k_quality,
        "duplicates": gsm8k_duplicates,
        "language": gsm8k_language,
        "word_count": gsm8k_words
    }

    print(f"[Quality] GSM8K Quality: {gsm8k_quality}")
    print(f"[Quality] GSM8K Duplicates: {gsm8k_duplicates['total_duplicates']}")
    print(f"[Quality] GSM8K Language: {gsm8k_language}")
    print(f"[Quality] GSM8K Words: {gsm8k_words}")

    # Check Dolly
    print("\n[Quality] Checking Dolly...")
    dolly_records = load_jsonl(RAW_DIR / "dolly" / "dolly-15k.jsonl")

    print(f"[Quality] Dolly: {len(dolly_records)} records")

    dolly_quality = check_quality(dolly_records, "Dolly")
    dolly_duplicates = detect_duplicates(dolly_records, "Dolly")
    dolly_language = analyze_language(dolly_records, "Dolly")
    dolly_words = count_words(dolly_records, "Dolly")

    quality_report["datasets"]["dolly"] = {
        "quality": dolly_quality,
        "duplicates": dolly_duplicates,
        "language": dolly_language,
        "word_count": dolly_words
    }

    print(f"[Quality] Dolly Quality: {dolly_quality}")
    print(f"[Quality] Dolly Duplicates: {dolly_duplicates['total_duplicates']}")
    print(f"[Quality] Dolly Language: {dolly_language}")
    print(f"[Quality] Dolly Words: {dolly_words}")

    # Save quality report
    quality_report_path = MANIFESTS_DIR / "quality_report.json"
    with open(quality_report_path, 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, indent=2)

    print(f"\n[Quality] Quality report saved to {quality_report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Quality Summary")
    print("=" * 60)
    print(f"GSM8K:")
    print(f"  Total records: {len(gsm8k_all)}")
    print(f"  Empty records: {gsm8k_quality['empty_records']}")
    print(f"  Missing fields: {gsm8k_quality['missing_fields']}")
    print(f"  Duplicates: {gsm8k_duplicates['total_duplicates']}")
    print(f"  Total words: {gsm8k_words['total_words']}")
    print(f"\nDolly:")
    print(f"  Total records: {len(dolly_records)}")
    print(f"  Empty records: {dolly_quality['empty_records']}")
    print(f"  Missing fields: {dolly_quality['missing_fields']}")
    print(f"  Duplicates: {dolly_duplicates['total_duplicates']}")
    print(f"  Total words: {dolly_words['total_words']}")

if __name__ == "__main__":
    main()
