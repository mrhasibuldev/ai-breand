"""
Phase 9 - Dataset Acquisition

Downloads verified commercial-approved datasets for Bengali and English expansion.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_DIR = DATA_DIR / "experimental" / "phase9"
RAW_DIR = PHASE9_DIR / "raw"
MANIFESTS_DIR = PHASE9_DIR / "manifests"

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents_dir=True, exist_ok=True)

print("="*60)
print("Phase 9 - Dataset Acquisition")
print("="*60)

# Verified commercial-approved datasets
approved_datasets = [
    {
        "name": "bengali_chat_conv",
        "source": "Hugging Face",
        "huggingface_id": "spedrox-sac/bengali_chat_conv",
        "language": "Bengali",
        "type": "Conversation/QA",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
        "commercial_use": "APPROVED",
        "estimated_records": 1074,
        "estimated_size": "323 KB"
    },
    {
        "name": "bengali_sft_v1",
        "source": "Hugging Face",
        "huggingface_id": "worldjit/bengali-sft-v1",
        "language": "Bengali",
        "type": "Instruction-following",
        "license": "Apache-2.0",
        "license_url": "https://www.apache.org/licenses/LICENSE-2.0",
        "commercial_use": "APPROVED",
        "estimated_records": 151,
        "estimated_size": "UNKNOWN"
    },
    {
        "name": "Bangla_NLP_Dataset",
        "source": "GitHub",
        "url": "https://github.com/Foysal87/Bangla-NLP-Dataset",
        "language": "Bengali",
        "type": "NER, POS, Wiki articles",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
        "commercial_use": "APPROVED",
        "estimated_records": "UNKNOWN",
        "estimated_size": "UNKNOWN",
        "notes": "Need to clone repository to access datasets via LFS"
    },
    {
        "name": "InstructionFineTuning_smallDataset",
        "source": "Hugging Face",
        "huggingface_id": "Manas2001/InstructionFineTuning-smallDataset",
        "language": "English",
        "type": "Instruction-following",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
        "commercial_use": "APPROVED",
        "estimated_records": 1100,
        "estimated_size": "UNKNOWN"
    }
]

print(f"\nCommercial-approved datasets to download: {len(approved_datasets)}")
for ds in approved_datasets:
    print(f"\n  - {ds['name']}")
    print(f"    License: {ds['license']}")
    print(f"    Records: {ds['estimated_records']}")

# Try to download Hugging Face datasets
print("\n" + "="*60)
print("Downloading Hugging Face Datasets")
print("="*60)

try:
    from datasets import load_dataset
    datasets_available = True
except ImportError:
    print("ERROR: datasets library not available")
    print("Install with: pip install datasets")
    datasets_available = False

acquisition_results = []

if datasets_available:
    for ds in approved_datasets:
        if 'huggingface_id' in ds:
            print(f"\nDownloading: {ds['name']}")
            try:
                # Load dataset
                dataset = load_dataset(ds['huggingface_id'], split='train')

                # Save to file
                output_file = RAW_DIR / f"{ds['name']}.jsonl"
                dataset.to_json(str(output_file))

                # Calculate checksum
                with open(output_file, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()

                file_size = output_file.stat().st_size

                result = {
                    "name": ds['name'],
                    "status": "SUCCESS",
                    "source": ds['source'],
                    "license": ds['license'],
                    "language": ds['language'],
                    "type": ds['type'],
                    "records": len(dataset),
                    "file_path": str(output_file),
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "sha256": file_hash,
                    "download_timestamp": datetime.now().isoformat()
                }

                print(f"  ✓ Downloaded: {len(dataset)} records")
                print(f"  ✓ Size: {result['file_size_mb']} MB")
                print(f"  ✓ Checksum: {file_hash[:16]}...")

                acquisition_results.append(result)

            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                result = {
                    "name": ds['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "download_timestamp": datetime.now().isoformat()
                }
                acquisition_results.append(result)
else:
    print("Skipping Hugging Face downloads - datasets library not available")
    for ds in approved_datasets:
        if 'huggingface_id' in ds:
            acquisition_results.append({
                "name": ds['name'],
                "status": "SKIPPED",
                "error": "datasets library not available",
                "download_timestamp": datetime.now().isoformat()
            })

# GitHub repository handling
print("\n" + "="*60)
print("GitHub Repository Handling")
print("="*60)

for ds in approved_datasets:
    if 'url' in ds and 'github.com' in ds['url']:
        print(f"\nRepository: {ds['name']}")
        print(f"  URL: {ds['url']}")
        print(f"  Status: REQUIRES MANUAL CLONE")
        print(f"  Reason: Uses Git LFS for large datasets")
        print(f"  Action: Clone manually if storage permits")
        result = {
            "name": ds['name'],
            "status": "MANUAL_CLONE_REQUIRED",
            "url": ds['url'],
            "notes": ds.get('notes', ''),
            "download_timestamp": datetime.now().isoformat()
        }
        acquisition_results.append(result)

# Save acquisition manifest
manifest = {
    "acquisition_timestamp": datetime.now().isoformat(),
    "total_datasets": len(approved_datasets),
    "successful": len([r for r in acquisition_results if r.get('status') == 'SUCCESS']),
    "failed": len([r for r in acquisition_results if r.get('status') == 'FAILED']),
    "skipped": len([r for r in acquisition_results if r.get('status') == 'SKIPPED']),
    "manual_required": len([r for r in acquisition_results if r.get('status') == 'MANUAL_CLONE_REQUIRED']),
    "results": acquisition_results
}

manifest_path = MANIFESTS_DIR / "acquisition_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\n" + "="*60)
print("ACQUISITION SUMMARY")
print("="*60)
print(f"Total datasets: {len(approved_datasets)}")
print(f"Successful: {manifest['successful']}")
print(f"Failed: {manifest['failed']}")
print(f"Skipped: {manifest['skipped']}")
print(f"Manual clone required: {manifest['manual_required']}")
print(f"\nManifest saved: {manifest_path}")

print("\n" + "="*60)
print("ACQUISITION COMPLETE")
print("="*60)
