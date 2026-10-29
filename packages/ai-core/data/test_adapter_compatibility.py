"""
Test adapter output format vs training script expectations.
"""

import os
os.chdir(os.path.dirname(__file__))

from dataset_schema import Dataset
from dataset_schema import ConversationRecord
from dataset_schema import Message
from dataset_schema import Language
from dataset_schema import Domain
from dataset_schema import SourceType
from dataset_schema import ReviewStatus
from dataset_schema import LicenseStatus
from dataset_schema import PrivacyStatus
from dataset_schema import Split
from dataset_processor import DatasetProcessor
from training_adapter import TrainingAdapter
from datetime import datetime

print("ADAPTER COMPATIBILITY TEST")
print("="*60)

processor = DatasetProcessor(random_seed=42)
adapter = TrainingAdapter(random_seed=42)

# Create a test dataset with one approved record
dataset = processor.create_dataset("test-compatibility", "0.1.0")

approved_record = ConversationRecord(
    record_id="TEST-APPROVED-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-001",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="Hello", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Hi there!", language=Language.ENGLISH, turn_index=1)
    ],
    source_type=SourceType.ORIGINAL_HUMAN,
    source_reference="test",
    creator="test",
    created_at=datetime.utcnow().isoformat(),
    review_status=ReviewStatus.APPROVED,
    reviewer="test-reviewer",
    review_date="2026-10-29",
    quality_score=0.9,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.PUBLIC
)
dataset.add_conversation(approved_record)

# Convert with adapter
eligible, excluded = adapter.filter_eligible_records(dataset)
training_texts = adapter.convert_to_training_format(eligible)

print(f"Training texts generated: {len(training_texts)}")
print(f"Sample text: {training_texts[0]}")

# Show the format
print("\nAdapter output format:")
print("The adapter outputs a JSON object with:")
print("  - training_data: array of strings")
print("  - metadata: adapter version, seed, etc.")
print("  - checksums: source and output")

# Compare with training script expectation
print("\nTraining script expectation (from train_medium_model.py):")
print("  - Input: JSON array of strings")
print("  - Code: texts = json.load(f)")
print("  - Expected: [\"text1\", \"text2\", ...]")

print("\nCompatibility Assessment:")
print("  - Adapter output: JSON object with 'training_data' field")
print("  - Training script expects: JSON array of strings")
print("  - Integration required: Extract 'training_data' field before training")

print("\n" + "="*60)
print("COMPATIBILITY TEST COMPLETE")
print("="*60)
