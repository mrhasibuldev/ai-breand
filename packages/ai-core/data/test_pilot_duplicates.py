"""
Duplicate detection test for pilot dataset.
"""

import os
os.chdir(os.path.dirname(__file__))

from dataset_schema import Dataset
from dataset_validator import DatasetValidator

# Load pilot dataset
pilot_path = os.path.join("pilots", "b4-b2-p1", "pilot_dataset_reviewed.json")
dataset = Dataset.from_json_file(pilot_path)

print("DUPLICATE DETECTION TEST")
print("="*60)

validator = DatasetValidator()
result = validator.validate_dataset(dataset)

print(f"Validation passed: {result.is_valid}")
print(f"Total errors: {len([e for e in result.errors if e.severity == 'error'])}")
print(f"Total warnings: {len([e for e in result.errors if e.severity == 'warning'])}")

# Check for duplicate errors
duplicate_errors = [e for e in result.errors if "duplicate" in e.message.lower()]
if duplicate_errors:
    print(f"\nDuplicate errors found: {len(duplicate_errors)}")
    for err in duplicate_errors:
        print(f"  - {err.field}: {err.message}")
else:
    print("\nNo duplicate conversations detected")

print("="*60)
