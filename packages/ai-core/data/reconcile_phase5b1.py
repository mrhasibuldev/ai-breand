"""
NexusAI Phase 5B.1 Dataset Reconciliation Script
Performs actual file analysis, record counting, duplicate detection, and SHA-256 verification
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "collected" / "raw"
CLEANED_DIR = BASE_DIR / "collected" / "cleaned"
APPROVED_DIR = BASE_DIR / "collected" / "approved"
EXCLUDED_DIR = BASE_DIR / "collected" / "excluded"
MANIFESTS_DIR = BASE_DIR / "collected" / "manifests"

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def count_lines(file_path: Path) -> int:
    """Count lines in a file"""
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count

def load_jsonl(file_path: Path) -> List[Dict]:
    """Load a JSONL file"""
    records = []
    line_number = 0
    errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_number += 1
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_number}: {e}")
    
    return records, errors

def analyze_record(record: Dict, dataset_name: str) -> Dict:
    """Analyze a single record"""
    analysis = {
        "empty": False,
        "missing_fields": [],
        "word_count": 0,
        "char_count": 0,
        "has_text": False
    }
    
    if not record or len(record) == 0:
        analysis["empty"] = True
        return analysis
    
    # Check required fields
    if dataset_name == "GSM8K":
        if "question" not in record:
            analysis["missing_fields"].append("question")
        if "answer" not in record:
            analysis["missing_fields"].append("answer")
        text = record.get("question", "") + " " + record.get("answer", "")
    elif dataset_name == "Dolly":
        if "instruction" not in record:
            analysis["missing_fields"].append("instruction")
        if "response" not in record:
            analysis["missing_fields"].append("response")
        text = record.get("instruction", "") + " " + record.get("response", "")
    else:
        text = str(record)
    
    analysis["word_count"] = len(text.split())
    analysis["char_count"] = len(text)
    analysis["has_text"] = len(text.strip()) > 0
    
    return analysis

def detect_language(text: str) -> str:
    """Detect language using Unicode ranges"""
    if not text:
        return "unknown"
    
    bengali_count = sum(1 for c in text if 0x0980 <= ord(c) <= 0x09FF)
    latin_count = sum(1 for c in text if (0x0041 <= ord(c) <= 0x005A) or (0x0061 <= ord(c) <= 0x007A))
    
    if bengali_count > 0 and latin_count > 0:
        return "mixed"
    elif bengali_count > 0:
        return "bengali"
    elif latin_count > 0:
        return "english"
    else:
        return "other"

def find_duplicates(records: List[Dict], dataset_name: str) -> Dict:
    """Find duplicate records"""
    seen = set()
    duplicates = []
    duplicate_indices = []
    
    for i, record in enumerate(records):
        if dataset_name == "GSM8K":
            key = record.get("question", "")
        elif dataset_name == "Dolly":
            key = record.get("instruction", "")
        else:
            continue
        
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        
        if key_hash in seen:
            duplicates.append({
                "index": i,
                "key": key[:100]
            })
            duplicate_indices.append(i)
        else:
            seen.add(key_hash)
    
    return {
        "total_duplicates": len(duplicates),
        "duplicate_indices": duplicate_indices,
        "duplicate_samples": duplicates[:10]  # First 10
    }

def analyze_dataset_file(file_path: Path, dataset_name: str) -> Dict:
    """Comprehensive analysis of a dataset file"""
    print(f"\n[Reconciliation] Analyzing {file_path.name}...")
    
    # File metadata
    file_size = file_path.stat().st_size
    sha256 = calculate_sha256(file_path)
    line_count = count_lines(file_path)
    
    # Load records
    records, json_errors = load_jsonl(file_path)
    
    # Analyze records
    total_words = 0
    total_chars = 0
    empty_records = 0
    missing_field_records = 0
    records_with_missing_fields = []
    
    language_counts = Counter()
    
    for record in records:
        analysis = analyze_record(record, dataset_name)
        
        total_words += analysis["word_count"]
        total_chars += analysis["char_count"]
        
        if analysis["empty"]:
            empty_records += 1
        
        if analysis["missing_fields"]:
            missing_field_records += 1
            records_with_missing_fields.append({
                "index": len(records_with_missing_fields),
                "missing": analysis["missing_fields"]
            })
        
        # Language detection
        if dataset_name == "GSM8K":
            text = record.get("question", "") + " " + record.get("answer", "")
        elif dataset_name == "Dolly":
            text = record.get("instruction", "") + " " + record.get("response", "")
        else:
            text = str(record)
        
        lang = detect_language(text)
        language_counts[lang] += 1
    
    # Find duplicates
    duplicates = find_duplicates(records, dataset_name)
    
    return {
        "file_name": file_path.name,
        "file_size_bytes": file_size,
        "file_size_mb": file_size / (1024 * 1024),
        "sha256": sha256,
        "line_count": line_count,
        "valid_records": len(records),
        "json_errors": len(json_errors),
        "json_error_samples": json_errors[:5],
        "empty_records": empty_records,
        "missing_field_records": missing_field_records,
        "missing_field_samples": records_with_missing_fields[:5],
        "total_words": total_words,
        "total_chars": total_chars,
        "avg_words_per_record": total_words / len(records) if records else 0,
        "language_distribution": dict(language_counts),
        "duplicates": duplicates
    }

def main():
    """Main reconciliation function"""
    print("=" * 70)
    print("NexusAI Phase 5B.1 Dataset Reconciliation")
    print("=" * 70)
    
    # Check disk space
    import shutil
    disk_usage = shutil.disk_usage(BASE_DIR)
    free_gb = disk_usage.free / (1024 ** 3)
    total_gb = disk_usage.total / (1024 ** 3)
    print(f"\n[Reconciliation] Disk Space: {free_gb:.2f} GB free / {total_gb:.2f} GB total")
    
    reconciliation_report = {
        "reconciliation_timestamp": "2026-11-03T19:00:00",
        "disk_space_gb_free": free_gb,
        "datasets": {}
    }
    
    # Analyze GSM8K
    print("\n[Reconciliation] Analyzing GSM8K...")
    gsm8k_train_path = RAW_DIR / "gsm8k" / "gsm8k_train.jsonl"
    gsm8k_test_path = RAW_DIR / "gsm8k" / "gsm8k_test.jsonl"
    
    gsm8k_train_analysis = analyze_dataset_file(gsm8k_train_path, "GSM8K")
    gsm8k_test_analysis = analyze_dataset_file(gsm8k_test_path, "GSM8K")
    
    # Calculate GSM8K combined totals
    gsm8k_combined = {
        "train": gsm8k_train_analysis,
        "test": gsm8k_test_analysis,
        "combined": {
            "total_records": gsm8k_train_analysis["valid_records"] + gsm8k_test_analysis["valid_records"],
            "total_words": gsm8k_train_analysis["total_words"] + gsm8k_test_analysis["total_words"],
            "total_chars": gsm8k_train_analysis["total_chars"] + gsm8k_test_analysis["total_chars"],
            "total_size_mb": gsm8k_train_analysis["file_size_mb"] + gsm8k_test_analysis["file_size_mb"]
        }
    }
    
    reconciliation_report["datasets"]["gsm8k"] = gsm8k_combined
    
    # Analyze Dolly
    print("\n[Reconciliation] Analyzing Dolly...")
    dolly_path = RAW_DIR / "dolly" / "dolly-15k.jsonl"
    dolly_analysis = analyze_dataset_file(dolly_path, "Dolly")
    
    reconciliation_report["datasets"]["dolly"] = dolly_analysis
    
    # Analyze MATH (if exists)
    math_path = RAW_DIR / "math" / "math.tar"
    if math_path.exists():
        print("\n[Reconciliation] MATH file exists (but failed to collect)")
        reconciliation_report["datasets"]["math"] = {
            "status": "collection_failed",
            "file_exists": True,
            "file_size_bytes": math_path.stat().st_size
        }
    else:
        print("\n[Reconciliation] MATH file does not exist")
        reconciliation_report["datasets"]["math"] = {
            "status": "not_collected",
            "file_exists": False
        }
    
    # Calculate overall totals
    total_records = gsm8k_combined["combined"]["total_records"] + dolly_analysis["valid_records"]
    total_words = gsm8k_combined["combined"]["total_words"] + dolly_analysis["total_words"]
    total_size_mb = gsm8k_combined["combined"]["total_size_mb"] + dolly_analysis["file_size_mb"]
    
    reconciliation_report["overall_totals"] = {
        "total_records": total_records,
        "total_words": total_words,
        "total_size_mb": total_size_mb
    }
    
    # Print summary
    print("\n" + "=" * 70)
    print("Reconciliation Summary")
    print("=" * 70)
    print(f"GSM8K Train: {gsm8k_train_analysis['valid_records']} records, {gsm8k_train_analysis['total_words']} words")
    print(f"GSM8K Test: {gsm8k_test_analysis['valid_records']} records, {gsm8k_test_analysis['total_words']} words")
    print(f"GSM8K Combined: {gsm8k_combined['combined']['total_records']} records, {gsm8k_combined['combined']['total_words']} words")
    print(f"Dolly: {dolly_analysis['valid_records']} records, {dolly_analysis['total_words']} words")
    print(f"Overall: {total_records} records, {total_words} words")
    print(f"\nDolly Duplicates: {dolly_analysis['duplicates']['total_duplicates']}")
    print(f"GSM8K Train Duplicates: {gsm8k_train_analysis['duplicates']['total_duplicates']}")
    print(f"GSM8K Test Duplicates: {gsm8k_test_analysis['duplicates']['total_duplicates']}")
    
    # Save reconciliation report
    reconciliation_path = MANIFESTS_DIR / "reconciliation_report.json"
    with open(reconciliation_path, 'w', encoding='utf-8') as f:
        json.dump(reconciliation_report, f, indent=2)
    
    print(f"\n[Reconciliation] Report saved to {reconciliation_path}")
    
    return reconciliation_report

if __name__ == "__main__":
    main()
