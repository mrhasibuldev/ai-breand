"""
Validate and review the pilot dataset.
"""

import os
os.chdir(os.path.dirname(__file__))

from dataset_schema import Dataset
from dataset_processor import DatasetProcessor
from dataset_validator import DatasetValidator

# Load pilot dataset
pilot_path = os.path.join(os.path.dirname(__file__), "pilots", "b4-b2-p1", "pilot_dataset.json")
dataset = Dataset.from_json_file(pilot_path)

print("PILOT DATASET VALIDATION")
print("="*60)

# Validate dataset
validator = DatasetValidator()
validation_result = validator.validate_dataset(dataset)

print(f"Validation passed: {validation_result.is_valid}")
print(f"Total errors: {len([e for e in validation_result.errors if e.severity == 'error'])}")
print(f"Total warnings: {len([e for e in validation_result.errors if e.severity == 'warning'])}")

if validation_result.errors:
    print("\nValidation errors:")
    for err in validation_result.errors:
        print(f"  [{err.severity.upper()}] {err.field}: {err.message}")

# Generate quality report
processor = DatasetProcessor()
report = processor.generate_quality_report(dataset)

print("\n" + "="*60)
print("QUALITY REPORT")
print("="*60)
print(f"Total conversations: {report['total_conversations']}")
print(f"Total messages: {report['total_messages']}")
print(f"Review status distribution: {report['review_status_distribution']}")
print(f"License status distribution: {report['license_status_distribution']}")
print(f"Privacy status distribution: {report['privacy_status_distribution']}")
print(f"Language distribution: {report['language_distribution']}")
print(f"Domain distribution: {report['domain_distribution']}")
print(f"Blocked for training: {report['blocked_for_training']}")

# Simulate human review - approve all records
print("\n" + "="*60)
print("SIMULATED HUMAN REVIEW")
print("="*60)
print("Approving all pilot records for workflow validation...")

from dataset_schema import ReviewStatus

for conv in dataset.conversations:
    conv.review_status = ReviewStatus.APPROVED
    conv.reviewer = "pilot-reviewer"
    conv.review_date = "2026-10-29"
    conv.quality_score = 0.85  # Simulated quality score
    print(f"[APPROVE] {conv.record_id}")

dataset.update_statistics()

print(f"\nApproved: {len([c for c in dataset.conversations if c.review_status == 'approved'])}")

# Save reviewed dataset
reviewed_path = os.path.join(os.path.dirname(__file__), "pilots", "b4-b2-p1", "pilot_dataset_reviewed.json")
dataset.to_json_file(reviewed_path)
print(f"\nReviewed dataset saved to: {reviewed_path}")
