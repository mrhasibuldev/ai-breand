"""
Test hardened approval workflow with content hash verification.
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
from dataset_validator import DatasetValidator
from datetime import datetime

print("HARDENED APPROVAL WORKFLOW TEST")
print("="*60)

processor = DatasetProcessor(random_seed=42)
validator = DatasetValidator()

# Create test dataset
dataset = processor.create_dataset("test-approval-harden", "0.1.0")

# Test 1: Record without reviewer cannot be approved
print("\nTest 1: Approval without reviewer")
record1 = ConversationRecord(
    record_id="TEST-NO-REVIEWER-001",
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
    review_status=ReviewStatus.APPROVED,
    reviewer=None,  # Missing reviewer
    review_date=None,
    quality_score=0.8,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.PUBLIC
)
dataset.add_conversation(record1)

result1 = validator.validate_record(record1)
if not result1.is_valid and any("missing reviewer" in err.message.lower() for err in result1.errors):
    print("PASS: Approval without reviewer rejected")
else:
    print("FAIL: Approval without reviewer not rejected")

# Test 2: Record without review date cannot be approved
print("\nTest 2: Approval without review date")
record2 = ConversationRecord(
    record_id="TEST-NO-DATE-001",
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
    review_status=ReviewStatus.APPROVED,
    reviewer="test-reviewer",
    review_date=None,  # Missing review date
    quality_score=0.8,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.PUBLIC
)
dataset.add_conversation(record2)

result2 = validator.validate_record(record2)
if not result2.is_valid and any("missing review date" in err.message.lower() for err in result2.errors):
    print("PASS: Approval without review date rejected")
else:
    print("FAIL: Approval without review date not rejected")

# Test 3: Proper approval with processor.approve_record()
print("\nTest 3: Proper approval with content hash")
record3 = ConversationRecord(
    record_id="TEST-PROPER-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-003",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="Test message", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Test response", language=Language.ENGLISH, turn_index=1)
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
approved_record = processor.approve_record(record3, "test-reviewer")

result3 = validator.validate_record(approved_record)
if result3.is_valid and approved_record.content_hash:
    print("PASS: Proper approval with content hash")
    print(f"  Content hash: {approved_record.content_hash[:16]}...")
else:
    print("FAIL: Proper approval failed")
    if not result3.is_valid:
        for err in result3.errors:
            print(f"  Error: {err.message}")

# Test 4: Content hash mismatch detection
print("\nTest 4: Content hash mismatch detection")
record4 = ConversationRecord(
    record_id="TEST-MISMATCH-001",
    dataset_version="1.0.0",
    conversation_id="TEST-CONV-004",
    split=Split.PENDING,
    language=Language.ENGLISH,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="Original message", language=Language.ENGLISH, turn_index=0),
        Message(role="assistant", content="Original response", language=Language.ENGLISH, turn_index=1)
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
approved_record4 = processor.approve_record(record4, "test-reviewer")

# Modify content after approval
approved_record4.messages[0].content = "Modified message"

result4 = validator.validate_record(approved_record4)
if not result4.is_valid and any("content hash mismatch" in err.message.lower() for err in result4.errors):
    print("PASS: Content hash mismatch detected")
else:
    print("FAIL: Content hash mismatch not detected")

print("\n" + "="*60)
print("HARDENED APPROVAL WORKFLOW TEST COMPLETE")
print("="*60)
