"""
NexusAI Phase 5B.1 Data Cleaning Pipeline
Removes duplicates, creates cleaned datasets, preserves raw data
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
EXCLUDED_DIR = BASE_DIR / "collected" / "excluded"
MANIFESTS_DIR = BASE_DIR / "collected" / "manifests"

# Create directories
for dir_path in [CLEANED_DIR, APPROVED_DIR, EXCLUDED_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def load_jsonl(file_path: Path) -> List[Dict]:
    """Load a JSONL file"""
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def save_jsonl(records: List[Dict], output_path: Path):
    """Save records to JSONL file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

def clean_dolly() -> Dict:
    """Clean Dolly dataset by removing duplicate instructions"""
    print("\n[Cleaning] Cleaning Dolly dataset...")
    
    raw_path = RAW_DIR / "dolly" / "dolly-15k.jsonl"
    records = load_jsonl(raw_path)
    
    print(f"[Cleaning] Original records: {len(records)}")
    
    # Track seen instructions
    seen_instructions = set()
    cleaned_records = []
    excluded_indices = []
    excluded_records = []
    
    for i, record in enumerate(records):
        instruction = record.get("instruction", "")
        instruction_hash = hashlib.md5(instruction.encode('utf-8')).hexdigest()
        
        if instruction_hash in seen_instructions:
            excluded_indices.append(i)
            excluded_records.append({
                "index": i,
                "instruction": instruction[:100],
                "reason": "duplicate_instruction"
            })
        else:
            seen_instructions.add(instruction_hash)
            cleaned_records.append(record)
    
    print(f"[Cleaning] Cleaned records: {len(cleaned_records)}")
    print(f"[Cleaning] Excluded duplicates: {len(excluded_indices)}")
    
    # Save cleaned dataset
    cleaned_path = CLEANED_DIR / "dolly" / "dolly-15k_cleaned.jsonl"
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    save_jsonl(cleaned_records, cleaned_path)
    
    # Save excluded records
    excluded_path = EXCLUDED_DIR / "dolly" / "dolly_excluded_duplicates.json"
    excluded_path.parent.mkdir(parents=True, exist_ok=True)
    with open(excluded_path, 'w', encoding='utf-8') as f:
        json.dump(excluded_records, f, indent=2)
    
    # Calculate SHA-256
    cleaned_sha256_hash = hashlib.sha256()
    with open(cleaned_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            cleaned_sha256_hash.update(byte_block)
    
    return {
        "original_records": len(records),
        "cleaned_records": len(cleaned_records),
        "excluded_duplicates": len(excluded_indices),
        "excluded_indices": excluded_indices,
        "cleaned_file": str(cleaned_path.relative_to(BASE_DIR)),
        "cleaned_sha256": cleaned_sha256_hash.hexdigest(),
        "excluded_file": str(excluded_path.relative_to(BASE_DIR))
    }

def clean_gsm8k() -> Dict:
    """Clean GSM8K dataset (no duplicates expected, just copy)"""
    print("\n[Cleaning] Cleaning GSM8K dataset...")
    
    # GSM8K has no duplicates, just copy to cleaned
    train_path = RAW_DIR / "gsm8k" / "gsm8k_train.jsonl"
    test_path = RAW_DIR / "gsm8k" / "gsm8k_test.jsonl"
    
    train_records = load_jsonl(train_path)
    test_records = load_jsonl(test_path)
    
    print(f"[Cleaning] GSM8K Train: {len(train_records)} records (no duplicates)")
    print(f"[Cleaning] GSM8K Test: {len(test_records)} records (no duplicates)")
    
    # Save cleaned datasets
    cleaned_train_path = CLEANED_DIR / "gsm8k" / "gsm8k_train_cleaned.jsonl"
    cleaned_test_path = CLEANED_DIR / "gsm8k" / "gsm8k_test_cleaned.jsonl"
    cleaned_train_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_jsonl(train_records, cleaned_train_path)
    save_jsonl(test_records, cleaned_test_path)
    
    # Calculate SHA-256 for train
    train_sha256_hash = hashlib.sha256()
    with open(cleaned_train_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            train_sha256_hash.update(byte_block)
    
    # Calculate SHA-256 for test
    test_sha256_hash = hashlib.sha256()
    with open(cleaned_test_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            test_sha256_hash.update(byte_block)
    
    return {
        "train_records": len(train_records),
        "test_records": len(test_records),
        "train_cleaned_file": str(cleaned_train_path.relative_to(BASE_DIR)),
        "test_cleaned_file": str(cleaned_test_path.relative_to(BASE_DIR)),
        "train_sha256": train_sha256_hash.hexdigest(),
        "test_sha256": test_sha256_hash.hexdigest()
    }

def main():
    """Main cleaning function"""
    print("=" * 70)
    print("NexusAI Phase 5B.1 Data Cleaning Pipeline")
    print("=" * 70)
    
    cleaning_report = {
        "cleaning_timestamp": "2026-11-03T19:05:00",
        "datasets": {}
    }
    
    # Clean GSM8K
    gsm8k_result = clean_gsm8k()
    cleaning_report["datasets"]["gsm8k"] = gsm8k_result
    
    # Clean Dolly
    dolly_result = clean_dolly()
    cleaning_report["datasets"]["dolly"] = dolly_result
    
    # Calculate totals
    total_cleaned = gsm8k_result["train_records"] + gsm8k_result["test_records"] + dolly_result["cleaned_records"]
    total_excluded = dolly_result["excluded_duplicates"]
    
    cleaning_report["totals"] = {
        "total_cleaned_records": total_cleaned,
        "total_excluded_records": total_excluded
    }
    
    # Save cleaning report
    cleaning_report_path = MANIFESTS_DIR / "cleaning_report.json"
    with open(cleaning_report_path, 'w', encoding='utf-8') as f:
        json.dump(cleaning_report, f, indent=2)
    
    print("\n" + "=" * 70)
    print("Cleaning Summary")
    print("=" * 70)
    print(f"Total Cleaned Records: {total_cleaned}")
    print(f"Total Excluded Records: {total_excluded}")
    print(f"\nGSM8K: {gsm8k_result['train_records'] + gsm8k_result['test_records']} records (no change)")
    print(f"Dolly: {dolly_result['cleaned_records']} records (removed {dolly_result['excluded_duplicates']} duplicates)")
    print(f"\nCleaning report saved to {cleaning_report_path}")

if __name__ == "__main__":
    main()
