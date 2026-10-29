"""
Test export safety and split generation for pilot dataset.
"""

import os
import tempfile
import json
os.chdir(os.path.dirname(__file__))

from dataset_schema import Dataset, ReviewStatus
from dataset_processor import DatasetProcessor

# Load reviewed pilot dataset
pilot_path = os.path.join("pilots", "b4-b2-p1", "pilot_dataset_reviewed.json")
dataset = Dataset.from_json_file(pilot_path)

processor = DatasetProcessor(random_seed=42)

print("EXPORT SAFETY AND SPLIT GENERATION TEST")
print("="*60)

# Test 1: Generate splits
print("\nTest 1: Generate deterministic splits")
split_result = processor.generate_splits(dataset, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
print(f"Split generation: {split_result.is_valid}")
print(f"Split details: {split_result.to_dict()}")

# Verify split integrity
integrity_result = processor.validate_split_integrity(dataset)
print(f"Split integrity: {integrity_result.is_valid}")

# Test 2: Export approved records
print("\nTest 2: Export approved records")
temp_path = tempfile.mktemp(suffix='.json')
export_result = processor.export_approved(dataset, temp_path, dry_run=False, overwrite_protection=False)
print(f"Export result: {export_result.is_valid}")
print(f"Export details: {export_result.to_dict()}")

# Verify exported file
if os.path.exists(temp_path):
    with open(temp_path, 'r', encoding='utf-8') as f:
        exported_data = json.load(f)
    print(f"Exported conversations: {len(exported_data['conversations'])}")
    print(f"Metadata: {exported_data.get('dataset_name')}")
    os.unlink(temp_path)

# Test 3: Verify pilot only contains approved records
print("\nTest 3: Verify pilot only contains approved records")
pending_count = len([c for c in dataset.conversations if c.review_status == ReviewStatus.PENDING])
approved_count = len([c for c in dataset.conversations if c.review_status == ReviewStatus.APPROVED])
print(f"Pending in dataset: {pending_count}")
print(f"Approved in dataset: {approved_count}")
if pending_count == 0 and approved_count == 9:
    print("PASS: Pilot only contains approved records")

print("\n" + "="*60)
print("TESTS COMPLETE")
print("="*60)
