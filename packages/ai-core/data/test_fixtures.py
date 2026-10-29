"""
Test fixtures for dataset validation and processing.
These are clearly labeled as TEST FIXTURES and should never be used as actual training data.
"""

from dataset_schema import (
    ConversationRecord, Message, Language, Domain, SourceType,
    ReviewStatus, LicenseStatus, PrivacyStatus, Split
)
from datetime import datetime


def create_test_record_bengali() -> ConversationRecord:
    """Create a valid Bengali test record"""
    return ConversationRecord(
        record_id="TEST-REC-20261029-0001",
        dataset_version="1.0.0",
        conversation_id="TEST-CONV-20261029-0001",
        split=Split.PENDING,
        language=Language.BENGALI,
        domain=Domain.CONVERSATION,
        messages=[
            Message(
                role="user",
                content="তোমার নাম কি?",
                language=Language.BENGALI,
                turn_index=0
            ),
            Message(
                role="assistant",
                content="আমার নাম NexusAI। আমি একটি AI সহকারী।",
                language=Language.BENGALI,
                turn_index=1
            )
        ],
        source_type=SourceType.ORIGINAL_SYNTHETIC,
        source_reference="test fixture generation",
        creator="test-automation",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.APPROVED,
        reviewer="test-automation",
        review_date=datetime.utcnow().isoformat(),
        quality_score=0.95,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["test", "bengali", "greeting"],
        notes="TEST FIXTURE - DO NOT USE FOR TRAINING"
    )


def create_test_record_english() -> ConversationRecord:
    """Create a valid English test record"""
    return ConversationRecord(
        record_id="TEST-REC-20261029-0002",
        dataset_version="1.0.0",
        conversation_id="TEST-CONV-20261029-0002",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.REASONING,
        messages=[
            Message(
                role="user",
                content="If all cats are animals, and all animals need food, do all cats need food?",
                language=Language.ENGLISH,
                turn_index=0
            ),
            Message(
                role="assistant",
                content="Yes. Since all cats are animals, and all animals need food, it follows that all cats need food.",
                language=Language.ENGLISH,
                turn_index=1
            )
        ],
        source_type=SourceType.ORIGINAL_SYNTHETIC,
        source_reference="test fixture generation",
        creator="test-automation",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.APPROVED,
        reviewer="test-automation",
        review_date=datetime.utcnow().isoformat(),
        quality_score=0.90,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["test", "english", "reasoning"],
        notes="TEST FIXTURE - DO NOT USE FOR TRAINING"
    )


def create_test_record_mixed() -> ConversationRecord:
    """Create a valid mixed-language test record"""
    return ConversationRecord(
        record_id="TEST-REC-20261029-0003",
        dataset_version="1.0.0",
        conversation_id="TEST-CONV-20261029-0003",
        split=Split.PENDING,
        language=Language.MIXED,
        domain=Domain.CONVERSATION,
        messages=[
            Message(
                role="user",
                content="আমি English এবং Bengali দুই ভাষাতেই কথা বলতে পারি",
                language=Language.MIXED,
                turn_index=0
            ),
            Message(
                role="assistant",
                content="That's great! আমিও দুই ভাষাতেই কথা বলতে পারি।",
                language=Language.MIXED,
                turn_index=1
            )
        ],
        source_type=SourceType.ORIGINAL_SYNTHETIC,
        source_reference="test fixture generation",
        creator="test-automation",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.APPROVED,
        reviewer="test-automation",
        review_date=datetime.utcnow().isoformat(),
        quality_score=0.85,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["test", "mixed", "code-switching"],
        notes="TEST FIXTURE - DO NOT USE FOR TRAINING"
    )


def create_invalid_record_empty_messages() -> ConversationRecord:
    """Create an invalid record with empty messages"""
    return ConversationRecord(
        record_id="TEST-REC-INVALID-0001",
        dataset_version="1.0.0",
        conversation_id="TEST-CONV-INVALID-0001",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.CONVERSATION,
        messages=[
            Message(
                role="user",
                content="",
                language=Language.ENGLISH,
                turn_index=0
            )
        ],
        source_type=SourceType.ORIGINAL_SYNTHETIC,
        source_reference="test fixture generation",
        creator="test-automation",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        notes="TEST FIXTURE - Invalid: empty message"
    )


def create_invalid_record_unverified_license() -> ConversationRecord:
    """Create an invalid record with unverified license"""
    return ConversationRecord(
        record_id="TEST-REC-INVALID-0002",
        dataset_version="1.0.0",
        conversation_id="TEST-CONV-INVALID-0002",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.CONVERSATION,
        messages=[
            Message(
                role="user",
                content="Hello",
                language=Language.ENGLISH,
                turn_index=0
            ),
            Message(
                role="assistant",
                content="Hi there!",
                language=Language.ENGLISH,
                turn_index=1
            )
        ],
        source_type=SourceType.IMPORTED,
        source_reference="external unknown source",
        creator="test-automation",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.5,
        license_status=LicenseStatus.UNVERIFIED,
        privacy_status=PrivacyStatus.PUBLIC,
        notes="TEST FIXTURE - Invalid: unverified license"
    )


def create_invalid_record_pii() -> ConversationRecord:
    """Create an invalid record with PII"""
    return ConversationRecord(
        record_id="TEST-REC-INVALID-0003",
        dataset_version="1.0.0",
        conversation_id="TEST-CONV-INVALID-0003",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.CONVERSATION,
        messages=[
            Message(
                role="user",
                content="My email is test@example.com",
                language=Language.ENGLISH,
                turn_index=0
            ),
            Message(
                role="assistant",
                content="I received your email",
                language=Language.ENGLISH,
                turn_index=1
            )
        ],
        source_type=SourceType.ORIGINAL_SYNTHETIC,
        source_reference="test fixture generation",
        creator="test-automation",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.5,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.CONTAINS_PII,
        notes="TEST FIXTURE - Invalid: contains PII"
    )
