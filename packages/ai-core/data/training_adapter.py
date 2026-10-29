"""
Schema v2.0 to Training Format Adapter

Converts approved v2.0 dataset records to the format expected by training scripts.
This adapter ensures only genuinely approved records are used for training.
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Tuple
from datetime import datetime

os.chdir(os.path.dirname(__file__))

from dataset_schema import Dataset, ReviewStatus, LicenseStatus


class TrainingAdapter:
    """Adapter to convert v2.0 dataset to training format"""

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.source_checksum = None
        self.exported_record_ids = []
        self.excluded_record_ids = []
        self.exclusion_reasons = {}

    def load_dataset(self, dataset_path: str) -> Dataset:
        """Load v2.0 dataset"""
        dataset = Dataset.from_json_file(dataset_path)
        
        # Calculate source checksum
        with open(dataset_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.source_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        return dataset

    def filter_eligible_records(self, dataset: Dataset) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter records eligible for training.
        Returns: (eligible_records, excluded_records)
        """
        eligible = []
        excluded = []

        for conv in dataset.conversations:
            # Check review status
            if conv.review_status != ReviewStatus.APPROVED:
                excluded.append(conv)
                self.excluded_record_ids.append(conv.record_id)
                self.exclusion_reasons[conv.record_id] = f"Not approved: {conv.review_status.value}"
                continue

            # Check license status
            if conv.license_status != LicenseStatus.PROJECT_OWNED:
                excluded.append(conv)
                self.excluded_record_ids.append(conv.record_id)
                self.exclusion_reasons[conv.record_id] = f"License not project-owned: {conv.license_status.value}"
                continue

            # Check for privacy issues
            if conv.privacy_status.value == "contains_pii":
                excluded.append(conv)
                self.excluded_record_ids.append(conv.record_id)
                self.exclusion_reasons[conv.record_id] = "Contains PII"
                continue

            # Record is eligible
            eligible.append(conv)
            self.exported_record_ids.append(conv.record_id)

        return eligible, excluded

    def convert_to_training_format(self, eligible_records: List[Dict]) -> List[str]:
        """
        Convert eligible conversations to training format.
        Format: Concatenated conversation as text string.
        """
        training_texts = []

        for conv in eligible_records:
            # Concatenate messages with separators
            messages = []
            for msg in conv.messages:
                role_prefix = f"{msg.role}: " if msg.role else ""
                messages.append(f"{role_prefix}{msg.content}")
            
            # Join with newlines
            conversation_text = "\n".join(messages)
            training_texts.append(conversation_text)

        return training_texts

    def export_training_data(
        self,
        training_texts: List[str],
        output_path: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Export training data with metadata.
        """
        export_data = {
            "schema_version": "2.0_to_training_adapter",
            "export_timestamp": datetime.utcnow().isoformat(),
            "source_dataset_checksum": self.source_checksum,
            "exported_record_count": len(training_texts),
            "exported_record_ids": self.exported_record_ids,
            "excluded_record_count": len(self.excluded_record_ids),
            "excluded_record_ids": self.excluded_record_ids,
            "exclusion_reasons": self.exclusion_reasons,
            "training_data": training_texts,
            "metadata": metadata or {}
        }

        # Calculate output checksum
        export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
        output_checksum = hashlib.sha256(export_json.encode('utf-8')).hexdigest()
        export_data["output_checksum"] = output_checksum

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(export_json)

        return {
            "output_path": output_path,
            "output_checksum": output_checksum,
            "exported_count": len(training_texts),
            "excluded_count": len(self.excluded_record_ids)
        }


def main():
    """Test the adapter with pending-review dataset"""
    print("TRAINING ADAPTER TEST")
    print("="*60)

    adapter = TrainingAdapter(random_seed=42)

    # Load pending-review dataset
    dataset_path = os.path.join("pilots", "b4-b2-p1", "pilot_dataset_pending_review.json")
    dataset = adapter.load_dataset(dataset_path)

    print(f"Loaded dataset: {dataset.metadata.dataset_name}")
    print(f"Total conversations: {len(dataset.conversations)}")
    print(f"Source checksum: {adapter.source_checksum}")

    # Filter eligible records
    eligible, excluded = adapter.filter_eligible_records(dataset)

    print(f"\nEligible records: {len(eligible)}")
    print(f"Excluded records: {len(excluded)}")

    if excluded:
        print("\nExclusion reasons:")
        for conv in excluded:
            reason = adapter.exclusion_reasons.get(conv.record_id, "Unknown")
            print(f"  {conv.record_id}: {reason}")

    # Convert to training format
    if eligible:
        training_texts = adapter.convert_to_training_format(eligible)
        print(f"\nTraining texts generated: {len(training_texts)}")
        print(f"Sample text: {training_texts[0][:100]}...")
    else:
        print("\nNo eligible records to convert")
        return

    # Export
    output_path = os.path.join("pilots", "b4-b2-p1", "training_data_pending.json")
    metadata = {
        "adapter_version": "1.0",
        "random_seed": 42,
        "conversion_mode": "conversation_concatenation"
    }

    result = adapter.export_training_data(training_texts, output_path, metadata)

    print(f"\nExported to: {result['output_path']}")
    print(f"Output checksum: {result['output_checksum']}")
    print(f"Exported: {result['exported_count']}")
    print(f"Excluded: {result['excluded_count']}")

    print("\n" + "="*60)
    print("ADAPTER TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
