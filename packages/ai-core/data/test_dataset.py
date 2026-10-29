"""
Tests for dataset schema, validation, and processing.
Run with: python -m pytest data/test_dataset.py -v
Or directly: python data/test_dataset.py
"""

import os
import sys
import json
import tempfile
from dataset_schema import (
    Dataset, ConversationRecord, Message, Language, Domain, SourceType,
    ReviewStatus, LicenseStatus, PrivacyStatus, Split
)
from dataset_validator import DatasetValidator
from dataset_processor import DatasetProcessor
from test_fixtures import (
    create_test_record_bengali,
    create_test_record_english,
    create_test_record_mixed,
    create_invalid_record_empty_messages,
    create_invalid_record_unverified_license,
    create_invalid_record_pii
)


def test_schema_valid_record():
    """Test that valid records can be created and serialized"""
    record = create_test_record_bengali()
    assert record.record_id == "TEST-REC-20261029-0001"
    assert record.language == Language.BENGALI
    assert len(record.messages) == 2
    assert record.review_status == ReviewStatus.APPROVED

    # Test serialization
    data = record.to_dict()
    assert "record_id" in data
    assert "messages" in data
    assert len(data["messages"]) == 2

    # Test deserialization
    restored = ConversationRecord.from_dict(data)
    assert restored.record_id == record.record_id
    assert len(restored.messages) == len(record.messages)

    print("[PASS] test_schema_valid_record")


def test_schema_dataset():
    """Test dataset creation and serialization"""
    dataset = Dataset()
    dataset.metadata.dataset_name = "test-dataset"
    dataset.metadata.dataset_version = "0.1.0"

    # Add records
    dataset.add_conversation(create_test_record_bengali())
    dataset.add_conversation(create_test_record_english())
    dataset.add_conversation(create_test_record_mixed())

    # Update statistics
    dataset.update_statistics()

    assert dataset.statistics.total_conversations == 3
    assert dataset.statistics.total_messages == 6
    assert dataset.statistics.language_distribution["bengali"] == 1
    assert dataset.statistics.language_distribution["english"] == 1
    assert dataset.statistics.language_distribution["mixed"] == 1

    # Test serialization
    data = dataset.to_dict()
    assert data["dataset_name"] == "test-dataset"
    assert len(data["conversations"]) == 3

    # Test deserialization
    restored = Dataset.from_dict(data)
    assert restored.metadata.dataset_name == "test-dataset"
    assert len(restored.conversations) == 3

    print("[PASS] test_schema_dataset")


def test_validator_valid_record():
    """Test validator accepts valid records"""
    validator = DatasetValidator()
    record = create_test_record_bengali()
    result = validator.validate_record(record)

    assert result.is_valid, f"Valid record failed validation: {result.to_dict()}"
    assert len([e for e in result.errors if e.severity == "error"]) == 0

    print("[PASS] test_validator_valid_record passed")


def test_validator_empty_messages():
    """Test validator rejects empty messages"""
    validator = DatasetValidator()
    record = create_invalid_record_empty_messages()
    result = validator.validate_record(record)

    assert not result.is_valid, "Invalid record with empty messages should fail validation"
    assert any("empty" in err.message.lower() for err in result.errors)

    print("[PASS] test_validator_empty_messages passed")


def test_validator_unverified_license():
    """Test validator blocks unverified license"""
    validator = DatasetValidator()
    record = create_invalid_record_unverified_license()
    result = validator.validate_record(record)

    assert not result.is_valid, "Unverified license should fail validation"
    assert any("unverified" in err.message.lower() for err in result.errors)

    print("[PASS] test_validator_unverified_license passed")


def test_validator_pii_detection():
    """Test validator detects PII"""
    validator = DatasetValidator()
    record = create_invalid_record_pii()
    result = validator.validate_record(record)

    # Should have warnings or errors about PII
    assert any("pii" in err.message.lower() or "email" in err.message.lower() for err in result.errors)

    print("[PASS] test_validator_pii_detection passed")


def test_validator_duplicate_detection():
    """Test validator detects duplicate conversations"""
    validator = DatasetValidator()
    dataset = Dataset()

    # Add same record twice
    record1 = create_test_record_bengali()
    record2 = create_test_record_bengali()
    record2.record_id = "TEST-REC-20261029-0002"  # Different ID but same content

    dataset.add_conversation(record1)
    dataset.add_conversation(record2)

    result = validator.validate_dataset(dataset)
    assert not result.is_valid, "Duplicate conversations should fail validation"
    assert any("duplicate" in err.message.lower() for err in result.errors)

    print("[PASS] test_validator_duplicate_detection passed")


def test_processor_add_record():
    """Test processor adds valid records"""
    processor = DatasetProcessor()
    dataset = processor.create_dataset("test-dataset")

    record = create_test_record_bengali()
    result = processor.add_record(dataset, record)

    assert result.is_valid, f"Failed to add valid record: {result.to_dict()}"
    assert len(dataset.conversations) == 1

    print("[PASS] test_processor_add_record passed")


def test_processor_reject_invalid_record():
    """Test processor rejects invalid records"""
    processor = DatasetProcessor()
    dataset = processor.create_dataset("test-dataset")

    record = create_invalid_record_empty_messages()
    result = processor.add_record(dataset, record)

    assert not result.is_valid, "Invalid record should be rejected"
    assert len(dataset.conversations) == 0  # Should not be added

    print("[PASS] test_processor_reject_invalid_record passed")


def test_processor_approve_reject():
    """Test approval and rejection workflow"""
    processor = DatasetProcessor()

    record = create_test_record_bengali()
    record.review_status = ReviewStatus.PENDING

    # Approve
    approved = processor.approve_record(record, "test-reviewer")
    assert approved.review_status == ReviewStatus.APPROVED
    assert approved.reviewer == "test-reviewer"

    # Reject
    rejected = processor.reject_record(record, "test-reviewer", "Quality too low")
    assert rejected.review_status == ReviewStatus.REJECTED
    assert "Rejection" in rejected.notes

    print("[PASS] test_processor_approve_reject passed")


def test_processor_generate_splits():
    """Test deterministic split generation"""
    processor = DatasetProcessor(random_seed=42)
    dataset = processor.create_dataset("test-dataset")

    # Add approved records
    for i in range(10):
        record = create_test_record_bengali()
        record.record_id = f"TEST-REC-{i:04d}"
        record.conversation_id = f"TEST-CONV-{i:04d}"
        record.review_status = ReviewStatus.APPROVED
        dataset.add_conversation(record)

    # Generate splits
    result = processor.generate_splits(dataset, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)

    assert result.is_valid, f"Split generation failed: {result.to_dict()}"

    # Check split distribution
    train_count = sum(1 for c in dataset.conversations if c.split == Split.TRAIN)
    val_count = sum(1 for c in dataset.conversations if c.split == Split.VALIDATION)
    test_count = sum(1 for c in dataset.conversations if c.split == Split.TEST)

    assert train_count + val_count + test_count == 10
    assert train_count == 7  # 70% of 10
    assert val_count == 1 or val_count == 2  # 15% of 10 (rounding)
    assert test_count == 1 or test_count == 2  # 15% of 10 (rounding)

    # Verify no conversation in multiple splits
    split_result = processor.validate_split_integrity(dataset)
    assert split_result.is_valid, "Split integrity check failed"

    print("[PASS] test_processor_generate_splits passed")


def test_processor_export_approved_only():
    """Test export only includes approved records"""
    processor = DatasetProcessor(random_seed=42)
    dataset = processor.create_dataset("test-dataset")

    # Add mix of approved and pending records
    approved = create_test_record_bengali()
    approved.review_status = ReviewStatus.APPROVED

    pending = create_test_record_english()
    pending.review_status = ReviewStatus.PENDING

    dataset.add_conversation(approved)
    dataset.add_conversation(pending)

    # Export to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        result = processor.export_approved(dataset, temp_path, dry_run=False, overwrite_protection=False)

        assert result.is_valid, f"Export failed: {result.to_dict()}"

        # Load exported file
        with open(temp_path, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)

        # Should only have approved record
        assert len(exported_data["conversations"]) == 1
        assert exported_data["conversations"][0]["record_id"] == approved.record_id

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    print("[PASS] test_processor_export_approved_only passed")


def test_processor_export_dry_run():
    """Test dry-run mode does not create file"""
    processor = DatasetProcessor()
    dataset = processor.create_dataset("test-dataset")

    dataset.add_conversation(create_test_record_bengali())

    temp_path = tempfile.mktemp(suffix='.json')

    try:
        result = processor.export_approved(dataset, temp_path, dry_run=True, overwrite_protection=False)

        assert result.is_valid
        assert not os.path.exists(temp_path), "Dry run should not create file"

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    print("[PASS] test_processor_export_dry_run passed")


def test_processor_export_overwrite_protection():
    """Test overwrite protection prevents overwriting existing files"""
    processor = DatasetProcessor()
    dataset = processor.create_dataset("test-dataset")

    dataset.add_conversation(create_test_record_bengali())

    # Create a file first
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
        f.write('{"test": "existing"}')

    try:
        result = processor.export_approved(dataset, temp_path, dry_run=False, overwrite_protection=True)

        assert not result.is_valid, "Should fail with overwrite protection"
        assert any("already exists" in err.message.lower() for err in result.errors)

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    print("[PASS] test_processor_export_overwrite_protection passed")


def test_processor_block_unverified():
    """Test blocking unverified records"""
    processor = DatasetProcessor()
    dataset = processor.create_dataset("test-dataset")

    # Add an approved record with unverified license
    record = create_invalid_record_unverified_license()
    record.review_status = ReviewStatus.APPROVED  # Approved but unverified license

    dataset.add_conversation(record)

    # Block unverified
    blocked_count = processor.block_unverified_records(dataset)

    assert blocked_count == 1
    assert record.review_status == ReviewStatus.PENDING
    assert "Blocked" in record.notes

    print("[PASS] test_processor_block_unverified passed")


def test_processor_quality_report():
    """Test quality report generation"""
    processor = DatasetProcessor()
    dataset = processor.create_dataset("test-dataset")

    dataset.add_conversation(create_test_record_bengali())
    dataset.add_conversation(create_test_record_english())

    # Add pending record
    pending = create_test_record_mixed()
    pending.review_status = ReviewStatus.PENDING
    dataset.add_conversation(pending)

    report = processor.generate_quality_report(dataset)

    assert report["total_conversations"] == 3
    assert report["review_status_distribution"]["approved"] == 2
    assert report["review_status_distribution"]["pending"] == 1
    assert report["language_distribution"]["bengali"] == 1
    assert report["language_distribution"]["english"] == 1
    assert report["language_distribution"]["mixed"] == 1

    print("[PASS] test_processor_quality_report passed")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_schema_valid_record,
        test_schema_dataset,
        test_validator_valid_record,
        test_validator_empty_messages,
        test_validator_unverified_license,
        test_validator_pii_detection,
        test_validator_duplicate_detection,
        test_processor_add_record,
        test_processor_reject_invalid_record,
        test_processor_approve_reject,
        test_processor_generate_splits,
        test_processor_export_approved_only,
        test_processor_export_dry_run,
        test_processor_export_overwrite_protection,
        test_processor_block_unverified,
        test_processor_quality_report,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'='*60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
