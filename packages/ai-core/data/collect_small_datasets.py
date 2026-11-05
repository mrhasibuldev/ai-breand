"""
NexusAI Small Dataset Collector

Collects small, high-quality datasets feasible within 2.8 GB disk space.
Focuses on reasoning and instruction-following datasets.
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class SmallDatasetCollector:
    """Collects small datasets from GitHub and Hugging Face"""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_github_raw(self, url: str, filename: str) -> bool:
        """Download file from GitHub raw URL"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'NexusAI-DatasetCollector/1.0'
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8')
                    output_path = self.output_dir / filename
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"[Collector] Downloaded: {filename}")
                    return True
                else:
                    print(f"[Collector] Failed to download {filename}: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"[Collector] Error downloading {filename}: {e}")
            return False

    def collect_gsm8k(self):
        """Collect GSM8K dataset from GitHub"""
        print("[Collector] Collecting GSM8K...")

        base_url = "https://raw.githubusercontent.com/openai/grade-school-math/main/grade_school_math/data"

        # Download train and test
        train_success = self.download_github_raw(
            f"{base_url}/train.jsonl",
            "gsm8k_train.jsonl"
        )

        test_success = self.download_github_raw(
            f"{base_url}/test.jsonl",
            "gsm8k_test.jsonl"
        )

        # Save metadata
        metadata = {
            "dataset": "GSM8K",
            "source": "https://github.com/openai/grade-school-math",
            "license": "MIT",
            "category": "mathematical_reasoning",
            "language": "en",
            "train_samples": 7473,
            "test_samples": 1319,
            "total_samples": 8792,
            "collected_at": datetime.utcnow().isoformat(),
            "files": {
                "train": "gsm8k_train.jsonl",
                "test": "gsm8k_test.jsonl"
            }
        }

        with open(self.output_dir / "gsm8k_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return train_success and test_success

    def collect_alpaca(self):
        """Collect Alpaca dataset from GitHub"""
        print("[Collector] Collecting Alpaca...")

        url = "https://raw.githubusercontent.com/tatsu-lab/stanford_alpaca/main/alpaca_data.json"

        success = self.download_github_raw(url, "alpaca_data.json")

        if success:
            # Load and count samples
            with open(self.output_dir / "alpaca_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                num_samples = len(data)

            metadata = {
                "dataset": "Alpaca",
                "source": "https://github.com/tatsu-lab/stanford_alpaca",
                "license": "Apache 2.0",
                "category": "instruction_following",
                "language": "en",
                "total_samples": num_samples,
                "collected_at": datetime.utcnow().isoformat(),
                "files": {
                    "data": "alpaca_data.json"
                }
            }

            with open(self.output_dir / "alpaca_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

        return success


def main():
    """Main collection function"""
    print("[Small Dataset Collector] Starting collection...")

    # Use absolute path from script location
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'collected' / 'small_datasets'
    collector = SmallDatasetCollector(str(output_dir))

    # Collect GSM8K
    gsm8k_success = collector.collect_gsm8k()

    # Collect Alpaca
    alpaca_success = collector.collect_alpaca()

    # Summary
    print("\n=== COLLECTION SUMMARY ===")
    print(f"GSM8K: {'✅ SUCCESS' if gsm8k_success else '❌ FAILED'}")
    print(f"Alpaca: {'✅ SUCCESS' if alpaca_success else '❌ FAILED'}")

    # Save collection manifest
    manifest = {
        "collection_timestamp": datetime.utcnow().isoformat(),
        "datasets": {
            "gsm8k": {
                "collected": gsm8k_success,
                "category": "mathematical_reasoning",
                "license": "MIT"
            },
            "alpaca": {
                "collected": alpaca_success,
                "category": "instruction_following",
                "license": "Apache 2.0"
            }
        }
    }

    with open(collector.output_dir / "collection_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[Collector] Manifest saved to {collector.output_dir / 'collection_manifest.json'}")


if __name__ == "__main__":
    main()
