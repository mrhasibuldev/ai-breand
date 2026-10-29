"""
Test split safety with approved records.
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
from datetime import datetime

print("SPLIT SAFETY VERIFICATION TEST")
print("="*60)

processor = DatasetProcessor(random_seed=42)

# Create test dataset with approved records
dataset = processor.create_dataset("test-split-safety", "0.1.0")

# Add 5 approved records for testing
for i in range(5):
    record = ConversationRecord(
        record_id=f"TEST-SPLIT-{i:03d}",
        dataset_version="1.0.0",
        conversation_id=f"TEST-CONV-{i:03d}",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.CONVERSATION,
        messages=[
            Message(role="user", content=f"Test message {i}", language=Language.ENGLISH, turn_index=0),
            Message(role="assistant", content=f"Test response {i}", language=Language.ENGLISH, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="test",
        creator="test",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.APPROVED,
        reviewer="test-reviewer",
        review_date="2026-10-29",
        quality_score=0.8,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC
    )
    dataset.add_conversation(record)

print(f"Test dataset created with {len(dataset.conversations)} approved records")

# Test 1: Generate splits
print("\nTest 1: Generate deterministic splits")
split_result = processor.generate_splits(dataset, train_ratio=0.6, val_ratio=0.2, test_ratio=0.2)
print(f"Split generation: {split_result.is_valid}")
print(f"Split details: {split_result.to_dict()}")

# Test 2: Verify split integrity
print("\nTest 2: Verify split integrity")
integrity_result = processor.validate_split_integrity(dataset)
print(f"Split integrity: {integrity_result.is_valid}")
print(f"Integrity details: {integrity_result.to_dict()}")

# Test 3: Verify conversation-level splitting
print("\nTest 3: Verify conversation-level splitting")
conv_to_splits = {}
for conv in dataset.conversations:
    if conv.conversation_id not in conv_to_splits:
        conv_to_splits[conv.conversation_id] = set()
    conv_to_splits[conv.conversation_id].add(conv.split.value)

# Check if any conversation has multiple splits
multi_split = {cid: splits for cid, splits in conv_to_splits.items() if len(splits) > 1}
if multi_split:
    print("FAIL: Conversations in multiple splits:")
    for cid, splits in multi_split.items():
        print(f"  {cid}: {splits}")
else:
    print("PASS: No conversation in multiple splits")

# Test 4: Verify insufficient data handling
print("\nTest 4: Verify insufficient data handling")
empty_dataset = processor.create_dataset("test-empty", "0.1.0")
empty_split_result = processor.generate_splits(empty_dataset)
print(f"Empty dataset split result: {empty_split_result.is_valid}")
if not empty_split_result.is_valid:
    print("PASS: Empty dataset correctly rejected")
else:
    print("FAIL: Empty dataset not rejected")

print("\n" + "="*60)
print("SPLIT SAFETY VERIFICATION COMPLETE")
print("="*60)
