"""
Test approval gate: Verify adapter rejects ineligible records.
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

print("APPROVAL GATE TEST")
print("="*60)

processor = DatasetProcessor(random_seed=42)
adapter = TrainingAdapter(random_seed=42)

# Create test dataset with various approval states
dataset = processor.create_dataset("test-approval-gate", "0.1.0")

# Test 1: Pending record
pending_record = ConversationRecord(
    record_id="TEST-PENDING-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-001",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="Test", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Response", language=Language.ENGLISH, turn_index=1)
    ],
    source_type=SourceType.ORIGINAL_HUMAN,
    source_reference="test",
    creator="test",
    created_at=datetime.utcnow().isoformat(),
    review_status=ReviewStatus.PENDING,
    quality_score=0.0,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.PUBLIC
)
dataset.add_conversation(pending_record)

# Test 2: Rejected record
rejected_record = ConversationRecord(
    record_id="TEST-REJECTED-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-002",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="Test", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Response", language=Language.ENGLISH, turn_index=1)
    ],
    source_type=SourceType.ORIGINAL_HUMAN,
    source_reference="test",
    creator="test",
    created_at=datetime.utcnow().isoformat(),
    review_status=ReviewStatus.REJECTED,
    reviewer="test-reviewer",
    review_date="2026-10-29",
    quality_score=0.3,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.PUBLIC,
    notes="Rejected for testing"
)
dataset.add_conversation(rejected_record)

# Test 3: Unverified license
unverified_record = ConversationRecord(
    record_id="TEST-UNVERIFIED-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-003",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="Test", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Response", language=Language.ENGLISH, turn_index=1)
    ],
    source_type=SourceType.IMPORTED,
    source_reference="external unknown",
    creator="test",
    created_at=datetime.utcnow().isoformat(),
    review_status=ReviewStatus.APPROVED,
    reviewer="test-reviewer",
    review_date="2026-10-29",
    quality_score=0.7,
    license_status=LicenseStatus.UNVERIFIED,
    privacy_status=PrivacyStatus.PUBLIC
)
dataset.add_conversation(unverified_record)

# Test 4: Contains PII
pii_record = ConversationRecord(
    record_id="TEST-PII-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-004",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="My email is test@example.com", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Response", language=Language.ENGLISH, turn_index=1)
    ],
    source_type=SourceType.ORIGINAL_HUMAN,
    source_reference="test",
    creator="test",
    created_at=datetime.utcnow().isoformat(),
    review_status=ReviewStatus.APPROVED,
    reviewer="test-reviewer",
    review_date="2026-10-29",
    quality_score=0.7,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.CONTAINS_PII
)
dataset.add_conversation(pii_record)

print(f"Test dataset created with {len(dataset.conversations)} records")

# Test adapter
eligible, excluded = adapter.filter_eligible_records(dataset)

print(f"\nEligible records: {len(eligible)}")
print(f"Excluded records: {len(excluded)}")

print("\nExclusion reasons:")
for conv in excluded:
    reason = adapter.exclusion_reasons.get(conv.record_id, "Unknown")
    print(f"  {conv.record_id}: {reason}")

# Verify each test case
print("\n" + "="*60)
print("TEST CASES")
print("="*60)

print("\nTest 1: Pending record")
if any(c.record_id == "TEST-PENDING-001" for c in excluded):
    print("PASS: Pending record excluded")
else:
    print("FAIL: Pending record not excluded")

print("\nTest 2: Rejected record")
if any(c.record_id == "TEST-REJECTED-001" for c in excluded):
    print("PASS: Rejected record excluded")
else:
    print("FAIL: Rejected record not excluded")

print("\nTest 3: Unverified license")
if any(c.record_id == "TEST-UNVERIFIED-001" for c in excluded):
    print("PASS: Unverified license excluded")
else:
    print("FAIL: Unverified license not excluded")

print("\nTest 4: Contains PII")
if any(c.record_id == "TEST-PII-001" for c in excluded):
    print("PASS: PII-containing record excluded")
else:
    print("FAIL: PII-containing record not excluded")

print("\n" + "="*60)
print("APPROVAL GATE TEST COMPLETE")
print("="*60)
