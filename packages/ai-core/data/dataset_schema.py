"""
NexusAI Dataset Schema v2.0

Schema definition and validation for original NexusAI training data.
Based on Stage B4-B1: Original Dataset Framework.
"""

from typing import Literal, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import re
from dataclasses import dataclass, field, asdict


class Language(str, Enum):
    """Language classification"""
    BENGALI = "bengali"
    ENGLISH = "english"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Domain(str, Enum):
    """Domain classification"""
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    MATHEMATICS = "mathematics"
    CODING = "coding"
    WRITING = "writing"
    PLANNING = "planning"
    HEALTH_WELLNESS = "health_wellness"
    OTHER = "other"


class SourceType(str, Enum):
    """Source type classification"""
    ORIGINAL_HUMAN = "original_human"
    ORIGINAL_SYNTHETIC = "original_synthetic"
    IMPORTED = "imported"
    CONVERTED = "converted"


class ReviewStatus(str, Enum):
    """Review status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LicenseStatus(str, Enum):
    """License status"""
    PROJECT_OWNED = "project-owned"
    VERIFIED_EXTERNAL = "verified-external"
    UNVERIFIED = "unverified"


class PrivacyStatus(str, Enum):
    """Privacy status"""
    PUBLIC = "public"
    PRIVATE = "private"
    CONTAINS_PII = "contains_pii"


class Split(str, Enum):
    """Dataset split"""
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    PENDING = "pending"


@dataclass
class Message:
    """Message in a conversation"""
    role: Literal["user", "assistant"]
    content: str
    language: Language
    turn_index: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            language=Language(data["language"]),
            turn_index=data["turn_index"]
        )


@dataclass
class ConversationRecord:
    """Single conversation record with full metadata"""
    record_id: str
    dataset_version: str
    conversation_id: str
    split: Split
    language: Language
    domain: Domain
    messages: List[Message]
    source_type: SourceType
    source_reference: str
    creator: str
    created_at: str  # ISO-8601
    review_status: ReviewStatus
    reviewer: Optional[str] = None
    review_date: Optional[str] = None
    quality_score: float = 0.0
    license_status: LicenseStatus = LicenseStatus.PROJECT_OWNED
    license_reference: Optional[str] = None
    privacy_status: PrivacyStatus = PrivacyStatus.PUBLIC
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    content_hash: Optional[str] = None  # Hash of content at approval time

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["messages"] = [msg.to_dict() for msg in self.messages]
        data["split"] = self.split.value
        data["language"] = self.language.value
        data["domain"] = self.domain.value
        data["source_type"] = self.source_type.value
        data["review_status"] = self.review_status.value
        data["license_status"] = self.license_status.value
        data["privacy_status"] = self.privacy_status.value
        return data

    def compute_content_hash(self) -> str:
        """Compute hash of conversation content for approval verification"""
        import hashlib
        import json
        
        # Hash only the conversation content (messages)
        content = {
            "conversation_id": self.conversation_id,
            "messages": [msg.to_dict() for msg in self.messages]
        }
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationRecord":
        messages = [Message.from_dict(msg) for msg in data["messages"]]
        return cls(
            record_id=data["record_id"],
            dataset_version=data["dataset_version"],
            conversation_id=data["conversation_id"],
            split=Split(data["split"]),
            language=Language(data["language"]),
            domain=Domain(data["domain"]),
            messages=messages,
            source_type=SourceType(data["source_type"]),
            source_reference=data["source_reference"],
            creator=data["creator"],
            created_at=data["created_at"],
            review_status=ReviewStatus(data["review_status"]),
            reviewer=data.get("reviewer"),
            review_date=data.get("review_date"),
            quality_score=data.get("quality_score", 0.0),
            license_status=LicenseStatus(data.get("license_status", "project-owned")),
            license_reference=data.get("license_reference"),
            privacy_status=PrivacyStatus(data.get("privacy_status", "public")),
            tags=data.get("tags", []),
            notes=data.get("notes"),
            content_hash=data.get("content_hash")
        )


@dataclass
class DatasetMetadata:
    """Dataset-level metadata"""
    schema_version: str = "2.0"
    dataset_version: str = "1.0.0"
    dataset_name: str = "nexusai-original"
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    modified: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    creator: str = "NexusAI Project"
    license: str = "proprietary-project-owned"
    license_url: Optional[str] = None
    commercial_use: str = "permitted"
    redistribution: str = "restricted-to-project"
    purpose: str = "training"
    description: str = "Original NexusAI training examples with Bengali-first focus"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DatasetStatistics:
    """Dataset statistics"""
    total_conversations: int = 0
    total_messages: int = 0
    language_distribution: Dict[str, int] = field(default_factory=lambda: {
        "bengali": 0, "english": 0, "mixed": 0, "unknown": 0
    })
    domain_distribution: Dict[str, int] = field(default_factory=lambda: {
        "conversation": 0, "knowledge": 0, "reasoning": 0, "mathematics": 0,
        "coding": 0, "writing": 0, "planning": 0, "health_wellness": 0, "other": 0
    })
    split_distribution: Dict[str, int] = field(default_factory=lambda: {
        "train": 0, "validation": 0, "test": 0, "pending": 0
    })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Dataset:
    """Complete dataset with metadata, statistics, and conversations"""
    metadata: DatasetMetadata = field(default_factory=DatasetMetadata)
    statistics: DatasetStatistics = field(default_factory=DatasetStatistics)
    conversations: List[ConversationRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.metadata.schema_version,
            "dataset_version": self.metadata.dataset_version,
            "dataset_name": self.metadata.dataset_name,
            "metadata": self.metadata.to_dict(),
            "statistics": self.statistics.to_dict(),
            "conversations": [conv.to_dict() for conv in self.conversations]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dataset":
        conversations = [ConversationRecord.from_dict(conv) for conv in data.get("conversations", [])]
        return cls(
            metadata=DatasetMetadata(**data.get("metadata", {})),
            statistics=DatasetStatistics(**data.get("statistics", {})),
            conversations=conversations
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Dataset":
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_json_file(cls, filepath: str) -> "Dataset":
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def to_json_file(self, filepath: str, indent: int = 2):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent))

    def update_statistics(self):
        """Recalculate statistics from conversations"""
        self.statistics.total_conversations = len(self.conversations)
        self.statistics.total_messages = sum(len(conv.messages) for conv in self.conversations)
        
        # Reset distributions
        self.statistics.language_distribution = {lang: 0 for lang in Language}
        self.statistics.domain_distribution = {dom: 0 for dom in Domain}
        self.statistics.split_distribution = {spl: 0 for spl in Split}
        
        for conv in self.conversations:
            self.statistics.language_distribution[conv.language.value] += 1
            self.statistics.domain_distribution[conv.domain.value] += 1
            self.statistics.split_distribution[conv.split.value] += 1

    def add_conversation(self, conversation: ConversationRecord):
        """Add a conversation and update statistics"""
        self.conversations.append(conversation)
        self.update_statistics()
