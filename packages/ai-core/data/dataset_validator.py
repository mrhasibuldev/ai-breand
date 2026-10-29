"""
NexusAI Dataset Validator

Validates dataset records against schema v2.0 requirements.
Implements quality checks, privacy checks, and duplicate detection.
"""

import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from dataset_schema import (
    ConversationRecord, Dataset, Language, Domain, SourceType,
    ReviewStatus, LicenseStatus, PrivacyStatus, Split
)


class ValidationError:
    """Represents a validation error"""
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error", "warning", "info"

    def to_dict(self) -> Dict[str, str]:
        return {"field": self.field, "message": self.message, "severity": self.severity}


class ValidationResult:
    """Result of validation"""
    def __init__(self, is_valid: bool, errors: List[ValidationError] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, field: str, message: str, severity: str = "error"):
        self.errors.append(ValidationError(field, message, severity))
        if severity == "error":
            self.is_valid = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": [err.to_dict() for err in self.errors]
        }


class DatasetValidator:
    """Validates dataset records"""

    # Patterns for PII detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    BANGLADESH_PHONE_PATTERN = re.compile(r'\b\+?880\d{10}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

    # Bengali Unicode range
    BENGALI_UNICODE = re.compile(r'[\u0980-\u09FF]')
    LATIN_UNICODE = re.compile(r'[a-zA-Z]')

    def __init__(self):
        self.conversation_hashes = {}  # For duplicate detection

    def validate_record(self, record: ConversationRecord) -> ValidationResult:
        """Validate a single conversation record"""
        result = ValidationResult(True)

        # Schema validation
        self._validate_required_fields(record, result)
        self._validate_field_types(record, result)
        self._validate_enum_values(record, result)

        # Quality validation
        self._validate_messages(record, result)
        self._validate_conversation_flow(record, result)
        self._validate_empty_content(record, result)

        # Provenance validation
        self._validate_provenance(record, result)

        # Privacy validation
        self._validate_privacy(record, result)

        # Language validation
        self._validate_language_label(record, result)

        # Approval validation
        self._validate_approval_evidence(record, result)

        return result

    def validate_dataset(self, dataset: Dataset) -> ValidationResult:
        """Validate entire dataset"""
        result = ValidationResult(True)

        # Validate metadata
        if not dataset.metadata.schema_version:
            result.add_error("metadata.schema_version", "Schema version is required")

        # Validate each conversation
        for i, conv in enumerate(dataset.conversations):
            conv_result = self.validate_record(conv)
            if not conv_result.is_valid:
                result.is_valid = False
                for err in conv_result.errors:
                    result.add_error(
                        f"conversations[{i}].{err.field}",
                        err.message,
                        err.severity
                    )

        # Check for duplicates
        self._check_duplicates(dataset, result)

        # Update and validate statistics
        dataset.update_statistics()
        self._validate_statistics(dataset, result)

        return result

    def _validate_required_fields(self, record: ConversationRecord, result: ValidationResult):
        """Validate required fields are present"""
        required_fields = [
            "record_id", "dataset_version", "conversation_id", "split",
            "language", "domain", "messages", "source_type", "source_reference",
            "creator", "created_at", "review_status", "quality_score",
            "license_status", "privacy_status"
        ]

        for field in required_fields:
            if getattr(record, field, None) is None:
                result.add_error(field, f"Required field '{field}' is missing")

    def _validate_field_types(self, record: ConversationRecord, result: ValidationResult):
        """Validate field types"""
        if not isinstance(record.record_id, str):
            result.add_error("record_id", "record_id must be a string")
        if not isinstance(record.quality_score, (int, float)):
            result.add_error("quality_score", "quality_score must be a number")
        if not isinstance(record.messages, list):
            result.add_error("messages", "messages must be a list")
        if record.quality_score < 0 or record.quality_score > 1.0:
            result.add_error("quality_score", "quality_score must be between 0.0 and 1.0")

    def _validate_enum_values(self, record: ConversationRecord, result: ValidationResult):
        """Validate enum values"""
        valid_languages = [lang.value for lang in Language]
        if record.language.value not in valid_languages:
            result.add_error("language", f"Invalid language: {record.language.value}")

        valid_domains = [dom.value for dom in Domain]
        if record.domain.value not in valid_domains:
            result.add_error("domain", f"Invalid domain: {record.domain.value}")

        valid_source_types = [st.value for st in SourceType]
        if record.source_type.value not in valid_source_types:
            result.add_error("source_type", f"Invalid source_type: {record.source_type.value}")

        valid_review_statuses = [rs.value for rs in ReviewStatus]
        if record.review_status.value not in valid_review_statuses:
            result.add_error("review_status", f"Invalid review_status: {record.review_status.value}")

        valid_license_statuses = [ls.value for ls in LicenseStatus]
        if record.license_status.value not in valid_license_statuses:
            result.add_error("license_status", f"Invalid license_status: {record.license_status.value}")

        valid_privacy_statuses = [ps.value for ps in PrivacyStatus]
        if record.privacy_status.value not in valid_privacy_statuses:
            result.add_error("privacy_status", f"Invalid privacy_status: {record.privacy_status.value}")

        valid_splits = [s.value for s in Split]
        if record.split.value not in valid_splits:
            result.add_error("split", f"Invalid split: {record.split.value}")

    def _validate_messages(self, record: ConversationRecord, result: ValidationResult):
        """Validate messages array"""
        if not record.messages:
            result.add_error("messages", "messages array cannot be empty")
            return

        if len(record.messages) < 2:
            result.add_error("messages", "Conversation must have at least 2 messages")

        for i, msg in enumerate(record.messages):
            if not msg.content or not msg.content.strip():
                result.add_error(f"messages[{i}].content", "Message content cannot be empty")

            if msg.role not in ["user", "assistant"]:
                result.add_error(f"messages[{i}].role", f"Invalid role: {msg.role}")

            if msg.turn_index != i:
                result.add_error(f"messages[{i}].turn_index", f"turn_index must be {i}")

    def _validate_conversation_flow(self, record: ConversationRecord, result: ValidationResult):
        """Validate conversation follows user-assistant-user flow"""
        expected_roles = ["user", "assistant"]
        for i, msg in enumerate(record.messages):
            expected = expected_roles[i % 2]
            if msg.role != expected:
                result.add_error(
                    f"messages[{i}].role",
                    f"Expected role '{expected}', got '{msg.role}'",
                    severity="warning"
                )

    def _validate_empty_content(self, record: ConversationRecord, result: ValidationResult):
        """Validate no empty content in messages"""
        for i, msg in enumerate(record.messages):
            if not msg.content.strip():
                result.add_error(f"messages[{i}].content", "Message content is empty or whitespace")

    def _validate_provenance(self, record: ConversationRecord, result: ValidationResult):
        """Validate provenance information"""
        if record.license_status == LicenseStatus.UNVERIFIED:
            result.add_error(
                "license_status",
                "Unverified license status - record blocked from training",
                severity="error"
            )

        if record.source_type == SourceType.IMPORTED and record.license_status != LicenseStatus.VERIFIED_EXTERNAL:
            result.add_error(
                "license_status",
                "Imported data must have verified-external license status",
                severity="error"
            )

    def _validate_privacy(self, record: ConversationRecord, result: ValidationResult):
        """Validate privacy - check for PII patterns"""
        all_content = " ".join(msg.content for msg in record.messages)

        # Check for email addresses
        if self.EMAIL_PATTERN.search(all_content):
            result.add_error(
                "privacy",
                "Email address detected - may contain PII",
                severity="warning"
            )

        # Check for phone numbers
        if self.PHONE_PATTERN.search(all_content) or self.BANGLADESH_PHONE_PATTERN.search(all_content):
            result.add_error(
                "privacy",
                "Phone number detected - may contain PII",
                severity="warning"
            )

        # Check for credit card numbers
        if self.CREDIT_CARD_PATTERN.search(all_content):
            result.add_error(
                "privacy",
                "Credit card number pattern detected - may contain PII",
                severity="error"
            )

        if record.privacy_status == PrivacyStatus.CONTAINS_PII:
            result.add_error(
                "privacy_status",
                "Record contains PII - must be removed before training",
                severity="error"
            )

    def _validate_language_label(self, record: ConversationRecord, result: ValidationResult):
        """Validate language label matches detected language"""
        all_content = " ".join(msg.content for msg in record.messages)
        detected = self._detect_language(all_content)

        if detected != record.language and record.language != Language.UNKNOWN:
            result.add_error(
                "language",
                f"Language label '{record.language.value}' does not match detected language '{detected.value}'",
                severity="warning"
            )

    def _detect_language(self, text: str) -> Language:
        """Detect language using Unicode ranges"""
        has_bengali = bool(self.BENGALI_UNICODE.search(text))
        has_latin = bool(self.LATIN_UNICODE.search(text))

        if has_bengali and has_latin:
            return Language.MIXED
        elif has_bengali:
            return Language.BENGALI
        elif has_latin:
            return Language.ENGLISH
        else:
            return Language.UNKNOWN

    def _validate_approval_evidence(self, record: ConversationRecord, result: ValidationResult):
        """Validate that approved records have proper approval evidence"""
        if record.review_status == ReviewStatus.APPROVED:
            # Approved records must have reviewer
            if not record.reviewer:
                result.add_error(
                    "review_status",
                    "Approved record missing reviewer - manual approval without evidence",
                    severity="error"
                )
            
            # Approved records must have review date
            if not record.review_date:
                result.add_error(
                    "review_status",
                    "Approved record missing review date - manual approval without evidence",
                    severity="error"
                )
            
            # Approved records should have content hash
            if not record.content_hash:
                result.add_error(
                    "review_status",
                    "Approved record missing content hash - manual approval without verification",
                    severity="warning"
                )
            else:
                # Verify content hash matches current content
                current_hash = record.compute_content_hash()
                if current_hash != record.content_hash:
                    result.add_error(
                        "content_hash",
                        "Content hash mismatch - record may have been modified after approval",
                        severity="error"
                    )

    def _check_duplicates(self, dataset: Dataset, result: ValidationResult):
        """Check for duplicate conversations"""
        seen_hashes = {}
        for conv in dataset.conversations:
            # Create hash from message content
            content_str = " ".join(msg.content for msg in conv.messages)
            content_hash = hashlib.md5(content_str.encode('utf-8')).hexdigest()

            if content_hash in seen_hashes:
                result.add_error(
                    f"conversations[{conv.record_id}]",
                    f"Duplicate conversation detected (similar to {seen_hashes[content_hash]})",
                    severity="error"
                )
            else:
                seen_hashes[content_hash] = conv.record_id

    def _validate_statistics(self, dataset: Dataset, result: ValidationResult):
        """Validate dataset statistics match actual data"""
        stats = dataset.statistics

        if stats.total_conversations != len(dataset.conversations):
            result.add_error(
                "statistics.total_conversations",
                f"Statistics count {stats.total_conversations} does not match actual {len(dataset.conversations)}",
                severity="warning"
            )

        actual_messages = sum(len(conv.messages) for conv in dataset.conversations)
        if stats.total_messages != actual_messages:
            result.add_error(
                "statistics.total_messages",
                f"Statistics count {stats.total_messages} does not match actual {actual_messages}",
                severity="warning"
            )
