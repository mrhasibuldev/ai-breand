"""
Phase 9.1 - Dataset Acquisition

Downloads verified Bengali datasets using the locally installed datasets library.
"""

import json
import hashlib
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

# Add local datasets library to path
LOCAL_VENV = DATA_DIR / ".venv" / "lib" / "python3.14" / "site-packages"
sys.path.insert(0, str(LOCAL_VENV))
PHASE9_1_DIR = DATA_DIR / "experimental" / "phase9_1"
RAW_DIR = PHASE9_1_DIR / "raw"
MANIFESTS_DIR = PHASE9_1_DIR / "manifests"

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.1 - Dataset Acquisition")
print("="*60)

# Try to import datasets
try:
    from datasets import load_dataset
    print("\n✓ datasets library loaded from local venv")
except ImportError as e:
    print(f"\n✗ Failed to load datasets library: {e}")
    sys.exit(1)

# Datasets to download
datasets_to_download = [
    {
        "name": "bengali_chat_conv",
        "huggingface_id": "spedrox-sac/bengali_chat_conv",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
        "language": "Bengali",
        "type": "Conversation/QA",
        "estimated_records": 1074
    },
    {
        "name": "bengali_sft_v1",
        "huggingface_id": "worldjit/bengali-sft-v1",
        "license": "Apache-2.0",
        "license_url": "https://www.apache.org/licenses/LICENSE-2.0",
        "language": "Bengali",
        "type": "Instruction-following",
        "estimated_records": 151
    }
]

acquisition_results = []

for ds_info in datasets_to_download:
    print(f"\n{'='*60}")
    print(f"Downloading: {ds_info['name']}")
    print(f"{'='*60}")
    print(f"Hugging Face ID: {ds_info['huggingface_id']}")
    print(f"License: {ds_info['license']}")
    print(f"Estimated records: {ds_info['estimated_records']}")

    try:
        # Load dataset
        dataset = load_dataset(ds_info['huggingface_id'], split='train')
        actual_records = len(dataset)
        print(f"✓ Loaded: {actual_records} records")

        # Save to JSONL
        output_file = RAW_DIR / f"{ds_info['name']}.jsonl"
        dataset.to_json(str(output_file))

        # Calculate checksum
        with open(output_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        file_size = output_file.stat().st_size
        file_size_mb = round(file_size / (1024 * 1024), 2)

        print(f"✓ Saved: {output_file}")
        print(f"✓ Size: {file_size_mb} MB")
        print(f"✓ SHA-256: {file_hash[:16]}...")

        result = {
            "name": ds_info['name'],
            "status": "SUCCESS",
            "huggingface_id": ds_info['huggingface_id'],
            "license": ds_info['license'],
            "license_url": ds_info['license_url'],
            "language": ds_info['language'],
            "type": ds_info['type'],
            "estimated_records": ds_info['estimated_records'],
            "actual_records": actual_records,
            "file_path": str(output_file),
            "file_size_bytes": file_size,
            "file_size_mb": file_size_mb,
            "sha256": file_hash,
            "download_timestamp": datetime.now().isoformat()
        }

        acquisition_results.append(result)

    except Exception as e:
        print(f"✗ FAILED: {e}")
        result = {
            "name": ds_info['name'],
            "status": "FAILED",
            "error": str(e),
            "download_timestamp": datetime.now().isoformat()
        }
        acquisition_results.append(result)

# Save acquisition manifest
manifest = {
    "acquisition_timestamp": datetime.now().isoformat(),
    "total_datasets": len(datasets_to_download),
    "successful": len([r for r in acquisition_results if r.get('status') == 'SUCCESS']),
    "failed": len([r for r in acquisition_results if r.get('status') == 'FAILED']),
    "results": acquisition_results
}

manifest_path = MANIFESTS_DIR / "acquisition_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("ACQUISITION SUMMARY")
print(f"{'='*60}")
print(f"Total datasets: {len(datasets_to_download)}")
print(f"Successful: {manifest['successful']}")
print(f"Failed: {manifest['failed']}")
print(f"\nManifest saved: {manifest_path}")

print(f"\n{'='*60}")
print("ACQUISITION COMPLETE")
print(f"{'='*60}")
