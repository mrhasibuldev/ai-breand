"""
NexusAI Dataset Processor

Handles dataset splitting, export, and approval workflow.
Implements deterministic train/validation/test splitting without leakage.
"""

import os
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataset_schema import (
    Dataset, ConversationRecord, Split, ReviewStatus, LicenseStatus
)
from dataset_validator import DatasetValidator, ValidationResult


class DatasetProcessor:
    """Processes datasets for training preparation"""

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        random.seed(random_seed)

    def create_dataset(self, dataset_name: str = "nexusai-original", version: str = "1.0.0") -> Dataset:
        """Create a new empty dataset"""
        dataset = Dataset()
        dataset.metadata.dataset_name = dataset_name
        dataset.metadata.dataset_version = version
        dataset.metadata.created = datetime.utcnow().isoformat()
        dataset.metadata.modified = datetime.utcnow().isoformat()
        return dataset

    def add_record(self, dataset: Dataset, record: ConversationRecord) -> ValidationResult:
        """Add a record to dataset with validation"""
        validator = DatasetValidator()
        result = validator.validate_record(record)

        if result.is_valid:
            dataset.add_conversation(record)
            dataset.metadata.modified = datetime.utcnow().isoformat()

        return result

    def approve_record(self, record: ConversationRecord, reviewer: str) -> ConversationRecord:
        """Approve a record for training with content hash verification"""
        record.review_status = ReviewStatus.APPROVED
        record.reviewer = reviewer
        record.review_date = datetime.utcnow().isoformat()
        record.content_hash = record.compute_content_hash()
        return record

    def reject_record(self, record: ConversationRecord, reviewer: str, reason: str) -> ConversationRecord:
        """Reject a record"""
        record.review_status = ReviewStatus.REJECTED
        record.reviewer = reviewer
        record.review_date = datetime.utcnow().isoformat()
        if record.notes:
            record.notes += f" | Rejection: {reason}"
        else:
            record.notes = f"Rejection: {reason}"
        return record

    def generate_splits(
        self,
        dataset: Dataset,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1
    ) -> ValidationResult:
        """
        Generate deterministic train/validation/test splits at conversation level.
        Ensures no conversation appears in multiple splits.
        """
        result = ValidationResult(True)

        # Validate ratios sum to 1.0
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
            result.add_error(
                "split_ratios",
                f"Split ratios must sum to 1.0 (got {train_ratio + val_ratio + test_ratio})"
            )
            return result

        # Get only approved records
        approved_records = [
            conv for conv in dataset.conversations
            if conv.review_status == ReviewStatus.APPROVED
        ]

        if not approved_records:
            result.add_error("conversations", "No approved records to split")
            return result

        # Group by conversation_id to ensure conversation-level splitting
        conv_groups = {}
        for record in approved_records:
            if record.conversation_id not in conv_groups:
                conv_groups[record.conversation_id] = []
            conv_groups[record.conversation_id].append(record)

        # Shuffle with fixed seed for determinism
        conv_ids = list(conv_groups.keys())
        random.shuffle(conv_ids)

        # Calculate split sizes
        total = len(conv_ids)
        train_size = int(total * train_ratio)
        val_size = int(total * val_ratio)
        test_size = total - train_size - val_size

        # Assign splits
        train_ids = set(conv_ids[:train_size])
        val_ids = set(conv_ids[train_size:train_size + val_size])
        test_ids = set(conv_ids[train_size + val_size:])

        # Verify no overlap
        overlap = train_ids & val_ids & test_ids
        if overlap:
            result.add_error("splits", f"Conversation ID overlap detected: {overlap}")
            return result

        # Apply splits to records
        for record in approved_records:
            if record.conversation_id in train_ids:
                record.split = Split.TRAIN
            elif record.conversation_id in val_ids:
                record.split = Split.VALIDATION
            elif record.conversation_id in test_ids:
                record.split = Split.TEST
            else:
                record.split = Split.PENDING

        dataset.update_statistics()
        dataset.metadata.modified = datetime.utcnow().isoformat()

        result.add_error(
            "splits",
            f"Generated splits: train={train_size}, val={val_size}, test={test_size}",
            severity="info"
        )

        return result

    def validate_split_integrity(self, dataset: Dataset) -> ValidationResult:
        """Validate that no conversation appears in multiple splits"""
        result = ValidationResult(True)

        conv_to_splits = {}
        for conv in dataset.conversations:
            if conv.conversation_id not in conv_to_splits:
                conv_to_splits[conv.conversation_id] = set()
            conv_to_splits[conv.conversation_id].add(conv.split.value)

        # Check for conversations in multiple splits
        for conv_id, splits in conv_to_splits.items():
            if len(splits) > 1:
                result.add_error(
                    f"conversation_id:{conv_id}",
                    f"Conversation appears in multiple splits: {splits}",
                    severity="error"
                )

        return result

    def export_approved(
        self,
        dataset: Dataset,
        output_path: str,
        dry_run: bool = False,
        overwrite_protection: bool = True
    ) -> ValidationResult:
        """
        Export only approved records to JSON file.
        Includes dry-run mode and overwrite protection.
        """
        result = ValidationResult(True)

        # Check if file exists
        if os.path.exists(output_path):
            if overwrite_protection:
                result.add_error(
                    "output_path",
                    f"File already exists: {output_path} (use overwrite_protection=False to overwrite)",
                    severity="error"
                )
                return result
            else:
                result.add_error(
                    "output_path",
                    f"File exists and will be overwritten: {output_path}",
                    severity="warning"
                )

        # Filter approved records
        approved_dataset = Dataset()
        approved_dataset.metadata = dataset.metadata
        approved_dataset.conversations = [
            conv for conv in dataset.conversations
            if conv.review_status == ReviewStatus.APPROVED
        ]
        approved_dataset.update_statistics()

        # Validate before export
        validator = DatasetValidator()
        validation_result = validator.validate_dataset(approved_dataset)
        if not validation_result.is_valid:
            result.is_valid = False
            result.errors.extend(validation_result.errors)
            return result

        if dry_run:
            result.add_error(
                "export",
                f"DRY RUN: Would export {len(approved_dataset.conversations)} approved records to {output_path}",
                severity="info"
            )
            return result

        # Export
        try:
            approved_dataset.to_json_file(output_path)
            result.add_error(
                "export",
                f"Successfully exported {len(approved_dataset.conversations)} approved records to {output_path}",
                severity="info"
            )
        except Exception as e:
            result.add_error("export", f"Export failed: {str(e)}", severity="error")
            result.is_valid = False

        return result

    def generate_split_manifest(
        self,
        dataset: Dataset,
        output_path: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1
    ) -> ValidationResult:
        """
        Generate a split manifest with full metadata for reproducibility.
        """
        result = ValidationResult(True)

        # Verify splits exist
        approved_records = [c for c in dataset.conversations if c.review_status == ReviewStatus.APPROVED]
        if not approved_records:
            result.add_error("splits", "No approved records to generate manifest")
            return result

        # Build manifest
        manifest = {
            "schema_version": "2.0",
            "manifest_type": "split_manifest",
            "generated_at": datetime.utcnow().isoformat(),
            "dataset_version": dataset.metadata.dataset_version,
            "dataset_name": dataset.metadata.dataset_name,
            "random_seed": self.random_seed,
            "split_ratios": {
                "train": train_ratio,
                "validation": val_ratio,
                "test": test_ratio
            },
            "total_conversations": len(approved_records),
            "splits": {
                "train": [],
                "validation": [],
                "test": []
            },
            "split_counts": {},
            "language_distribution": {},
            "domain_distribution": {}
        }

        # Group by split
        for conv in approved_records:
            split_name = conv.split.value
            manifest["splits"][split_name].append({
                "record_id": conv.record_id,
                "conversation_id": conv.conversation_id,
                "language": conv.language.value,
                "domain": conv.domain.value
            })

        # Count splits
        for split_name in ["train", "validation", "test"]:
            manifest["split_counts"][split_name] = len(manifest["splits"][split_name])

        # Language distribution
        for conv in approved_records:
            lang = conv.language.value
            manifest["language_distribution"][lang] = manifest["language_distribution"].get(lang, 0) + 1

        # Domain distribution
        for conv in approved_records:
            domain = conv.domain.value
            manifest["domain_distribution"][domain] = manifest["domain_distribution"].get(domain, 0) + 1

        # Calculate checksum
        import json
        import hashlib
        manifest_str = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
        manifest_checksum = hashlib.sha256(manifest_str.encode('utf-8')).hexdigest()
        manifest["manifest_checksum"] = manifest_checksum

        # Write manifest
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            result.add_error(
                "manifest",
                f"Split manifest generated: {output_path} (checksum: {manifest_checksum[:16]}...)",
                severity="info"
            )
        except Exception as e:
            result.add_error("manifest", f"Manifest generation failed: {str(e)}", severity="error")
            result.is_valid = False

        return result

    def generate_quality_report(self, dataset: Dataset) -> Dict[str, Any]:
        """Generate a quality report for the dataset"""
        validator = DatasetValidator()
        validation_result = validator.validate_dataset(dataset)

        # Count by review status
        status_counts = {}
        for conv in dataset.conversations:
            status = conv.review_status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by license status
        license_counts = {}
        for conv in dataset.conversations:
            status = conv.license_status.value
            license_counts[status] = license_counts.get(status, 0) + 1

        # Count by privacy status
        privacy_counts = {}
        for conv in dataset.conversations:
            status = conv.privacy_status.value
            privacy_counts[status] = privacy_counts.get(status, 0) + 1

        return {
            "dataset_name": dataset.metadata.dataset_name,
            "dataset_version": dataset.metadata.dataset_version,
            "total_conversations": len(dataset.conversations),
            "total_messages": dataset.statistics.total_messages,
            "validation_passed": validation_result.is_valid,
            "validation_errors": len([e for e in validation_result.errors if e.severity == "error"]),
            "validation_warnings": len([e for e in validation_result.errors if e.severity == "warning"]),
            "review_status_distribution": status_counts,
            "license_status_distribution": license_counts,
            "privacy_status_distribution": privacy_counts,
            "language_distribution": dataset.statistics.language_distribution,
            "domain_distribution": dataset.statistics.domain_distribution,
            "split_distribution": dataset.statistics.split_distribution,
            "blocked_for_training": status_counts.get("unverified", 0) + license_counts.get("unverified", 0)
        }

    def block_unverified_records(self, dataset: Dataset) -> int:
        """
        Block records with unverified license status from being exported.
        Returns count of blocked records.
        """
        blocked_count = 0
        for conv in dataset.conversations:
            if conv.license_status == LicenseStatus.UNVERIFIED:
                if conv.review_status == ReviewStatus.APPROVED:
                    conv.review_status = ReviewStatus.PENDING
                    if conv.notes:
                        conv.notes += " | Blocked: Unverified license"
                    else:
                        conv.notes = "Blocked: Unverified license"
                    blocked_count += 1

        if blocked_count > 0:
            dataset.metadata.modified = datetime.utcnow().isoformat()

        return blocked_count
