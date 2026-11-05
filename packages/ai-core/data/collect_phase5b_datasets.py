"""
NexusAI Phase 5B Dataset Collector
Collects GSM8K, MATH, Dolly, and expanded Wikipedia datasets
Handles SHA-256 checksums, manifests, and proper licensing metadata
"""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import time

# Configuration
BASE_DIR = Path(__file__).parent
COLLECTED_DIR = BASE_DIR / "collected"
RAW_DIR = COLLECTED_DIR / "raw"
CLEANED_DIR = COLLECTED_DIR / "cleaned"
APPROVED_DIR = COLLECTED_DIR / "approved"
MANIFESTS_DIR = COLLECTED_DIR / "manifests"

# Create directories
for dir_path in [COLLECTED_DIR, RAW_DIR, CLEANED_DIR, APPROVED_DIR, MANIFESTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Dataset metadata
DATASETS = {
    "gsm8k": {
        "name": "GSM8K",
        "source": "https://github.com/openai/grade-school-math",
        "license": "MIT",
        "license_url": "https://github.com/openai/grade-school-math",
        "commercial_eligibility": "APPROVED",
        "attribution_required": False,
        "share_alike": False,
        "category": "reasoning",
        "language": "en",
        "files": [
            {
                "url": "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl",
                "filename": "gsm8k_train.jsonl"
            },
            {
                "url": "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl",
                "filename": "gsm8k_test.jsonl"
            }
        ]
    },
    "math": {
        "name": "MATH",
        "source": "https://huggingface.co/datasets/EleutherAI/hendrycks_math",
        "license": "MIT",
        "license_url": "https://github.com/hendrycks/math/blob/main/LICENSE",
        "commercial_eligibility": "APPROVED",
        "attribution_required": False,
        "share_alike": False,
        "category": "reasoning",
        "language": "en",
        "files": [
            {
                "url": "https://huggingface.co/datasets/EleutherAI/hendrycks_math/resolve/main/algebra/train-00000-of-00001.parquet",
                "filename": "math_algebra_train.parquet"
            },
            {
                "url": "https://huggingface.co/datasets/EleutherAI/hendrycks_math/resolve/main/algebra/test-00000-of-00001.parquet",
                "filename": "math_algebra_test.parquet"
            }
        ]
    },
    "dolly": {
        "name": "Dolly",
        "source": "https://huggingface.co/datasets/databricks/databricks-dolly-15k",
        "license": "CC BY-SA 3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "commercial_eligibility": "CONDITIONAL",
        "attribution_required": True,
        "share_alike": True,
        "category": "instruction_following",
        "language": "en",
        "files": [
            {
                "url": "https://huggingface.co/datasets/databricks/databricks-dolly-15k/resolve/main/databricks-dolly-15k.jsonl",
                "filename": "dolly-15k.jsonl"
            }
        ]
    }
}

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_file(url: str, output_path: Path, max_retries: int = 3) -> bool:
    """Download a file with retry logic using urllib"""
    for attempt in range(max_retries):
        try:
            print(f"[Collector] Downloading {url} (attempt {attempt + 1}/{max_retries})")
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'NexusAI-DataCollector/1.0')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = response.getheader('Content-Length')
                if total_size:
                    total_size = int(total_size)
                downloaded = 0

                with open(output_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"[Collector] Progress: {progress:.1f}%", end='\r')

            print(f"\n[Collector] Downloaded {output_path.name} ({downloaded / 1024 / 1024:.2f} MB)")
            return True

        except urllib.error.HTTPError as e:
            print(f"[Collector] HTTP Error {e.code}: {e.reason}")
            if output_path.exists():
                output_path.unlink()
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return False
        except Exception as e:
            print(f"[Collector] Error downloading {url}: {e}")
            if output_path.exists():
                output_path.unlink()
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return False

    return False

def count_jsonl_records(file_path: Path) -> int:
    """Count records in a JSONL file"""
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception as e:
        print(f"[Collector] Error counting records in {file_path}: {e}")
    return count

def collect_dataset(dataset_key: str) -> Dict:
    """Collect a single dataset"""
    dataset_info = DATASETS[dataset_key]
    dataset_dir = RAW_DIR / dataset_key
    dataset_dir.mkdir(exist_ok=True)

    print(f"\n[Collector] Collecting {dataset_info['name']}...")
    print(f"[Collector] License: {dataset_info['license']}")
    print(f"[Collector] Commercial Eligibility: {dataset_info['commercial_eligibility']}")

    collected_files = []
    total_records = 0
    total_size = 0

    for file_info in dataset_info["files"]:
        url = file_info["url"]
        filename = file_info["filename"]
        output_path = dataset_dir / filename

        if output_path.exists():
            print(f"[Collector] File already exists: {filename}")
            size = output_path.stat().st_size
            sha256 = calculate_sha256(output_path)
            collected_files.append({
                "filename": filename,
                "url": url,
                "size": size,
                "sha256": sha256,
                "status": "already_exists"
            })
            total_size += size

            # Count records if JSONL
            if filename.endswith('.jsonl'):
                records = count_jsonl_records(output_path)
                total_records += records
                print(f"[Collector] Records: {records}")
            continue

        success = download_file(url, output_path)
        if success:
            size = output_path.stat().st_size
            sha256 = calculate_sha256(output_path)
            collected_files.append({
                "filename": filename,
                "url": url,
                "size": size,
                "sha256": sha256,
                "status": "downloaded"
            })
            total_size += size

            # Count records if JSONL
            if filename.endswith('.jsonl'):
                records = count_jsonl_records(output_path)
                total_records += records
                print(f"[Collector] Records: {records}")
        else:
            collected_files.append({
                "filename": filename,
                "url": url,
                "size": 0,
                "sha256": None,
                "status": "failed"
            })

    # Create dataset manifest
    manifest = {
        "dataset": dataset_info["name"],
        "dataset_key": dataset_key,
        "source": dataset_info["source"],
        "license": dataset_info["license"],
        "license_url": dataset_info["license_url"],
        "commercial_eligibility": dataset_info["commercial_eligibility"],
        "attribution_required": dataset_info["attribution_required"],
        "share_alike": dataset_info["share_alike"],
        "category": dataset_info["category"],
        "language": dataset_info["language"],
        "collection_timestamp": datetime.utcnow().isoformat(),
        "total_files": len(collected_files),
        "total_size_bytes": total_size,
        "total_records": total_records,
        "files": collected_files
    }

    manifest_path = MANIFESTS_DIR / f"{dataset_key}_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"[Collector] Manifest saved to {manifest_path}")
    print(f"[Collector] Total size: {total_size / 1024 / 1024:.2f} MB")
    print(f"[Collector] Total records: {total_records}")

    return manifest

def main():
    """Main collection function"""
    print("=" * 60)
    print("NexusAI Phase 5B Dataset Collector")
    print("=" * 60)

    # Check disk space
    import shutil
    disk_usage = shutil.disk_usage(BASE_DIR)
    free_gb = disk_usage.free / (1024 ** 3)
    print(f"\n[Collector] Available disk space: {free_gb:.2f} GB")

    if free_gb < 1.0:
        print("[Collector] WARNING: Less than 1 GB free space available")
        response = input("[Collector] Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("[Collector] Aborting collection")
            return

    # Collect datasets
    all_manifests = {}
    results = {}

    for dataset_key in DATASETS.keys():
        try:
            manifest = collect_dataset(dataset_key)
            all_manifests[dataset_key] = manifest
            results[dataset_key] = "success"
        except Exception as e:
            print(f"[Collector] Error collecting {dataset_key}: {e}")
            results[dataset_key] = "failed"

    # Create summary manifest
    summary = {
        "collection_timestamp": datetime.utcnow().isoformat(),
        "total_datasets": len(DATASETS),
        "successful_collections": sum(1 for r in results.values() if r == "success"),
        "failed_collections": sum(1 for r in results.values() if r == "failed"),
        "results": results,
        "datasets": all_manifests
    }

    summary_path = MANIFESTS_DIR / "collection_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("Collection Summary")
    print("=" * 60)
    print(f"Total datasets: {len(DATASETS)}")
    print(f"Successful: {summary['successful_collections']}")
    print(f"Failed: {summary['failed_collections']}")
    print(f"\nSummary saved to {summary_path}")

if __name__ == "__main__":
    main()
