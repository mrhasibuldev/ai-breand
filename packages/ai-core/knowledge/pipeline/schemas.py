"""
Knowledge Pipeline Schemas

Data models for knowledge ingestion and processing.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SourceType(Enum):
    """Source type enumeration"""
    WEB = "web"
    BOOK = "book"
    ARTICLE = "article"
    DOCUMENTATION = "documentation"
    DATASET = "dataset"
    CONVERSATION = "conversation"
    USER_UPLOADED = "user_uploaded"


class Language(Enum):
    """Language enumeration"""
    EN = "en"
    BN = "bn"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TrustLevel(Enum):
    """Trust level enumeration"""
    TIER_1 = "TIER_1"  # Highly authoritative
    TIER_2 = "TIER_2"  # Reliable secondary sources
    TIER_3 = "TIER_3"  # General public sources
    TIER_4 = "TIER_4"  # Unverified material


class InformationLifetime(Enum):
    """Information lifetime enumeration"""
    STATIC = "STATIC"
    SLOW_CHANGING = "SLOW_CHANGING"
    TIME_SENSITIVE = "TIME_SENSITIVE"


@dataclass
class RawDocument:
    """Raw document schema"""
    document_id: str
    source: str
    source_type: SourceType
    collected_at: datetime
    collected_by: str
    file_path: str
    file_hash: str
    size_bytes: int
    language: Language
    mime_type: str
    license: Optional[str] = None
    copyright_notice: Optional[str] = None
    access_restricted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "document_id": self.document_id,
            "source": self.source,
            "source_type": self.source_type.value,
            "collected_at": self.collected_at.isoformat(),
            "collected_by": self.collected_by,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "size_bytes": self.size_bytes,
            "language": self.language.value,
            "mime_type": self.mime_type,
            "license": self.license,
            "copyright_notice": self.copyright_notice,
            "access_restricted": self.access_restricted,
            "metadata": self.metadata
        }


@dataclass
class CleanedDocument:
    """Cleaned document schema"""
    document_id: str
    raw_document_id: str
    text: str
    language: Language
    quality_score: float
    trust_level: TrustLevel
    information_lifetime: InformationLifetime
    word_count: int
    char_count: int
    processed_at: datetime
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    source: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "document_id": self.document_id,
            "raw_document_id": self.raw_document_id,
            "text": self.text,
            "language": self.language.value,
            "quality_score": self.quality_score,
            "trust_level": self.trust_level.value,
            "information_lifetime": self.information_lifetime.value,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "processed_at": self.processed_at.isoformat(),
            "processing_metadata": self.processing_metadata,
            "source": self.source
        }


@dataclass
class Chunk:
    """Document chunk schema"""
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    token_count: int
    section_title: Optional[str] = None
    section_hierarchy: List[str] = field(default_factory=list)
    position_in_document: float = 0.0
    preceding_chunk_id: Optional[str] = None
    following_chunk_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "token_count": self.token_count,
            "section_title": self.section_title,
            "section_hierarchy": self.section_hierarchy,
            "position_in_document": self.position_in_document,
            "preceding_chunk_id": self.preceding_chunk_id,
            "following_chunk_id": self.following_chunk_id
        }


@dataclass
class IngestionResult:
    """Ingestion result schema"""
    success: bool
    document_id: Optional[str] = None
    chunk_count: int = 0
    error: Optional[str] = None
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "document_id": self.document_id,
            "chunk_count": self.chunk_count,
            "error": self.error,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata
        }


@dataclass
class RetrievalOptions:
    """Retrieval options schema"""
    top_k: int = 5
    min_score: float = 0.5
    trust_levels: List[TrustLevel] = field(default_factory=lambda: [TrustLevel.TIER_1, TrustLevel.TIER_2, TrustLevel.TIER_3])
    languages: List[Language] = field(default_factory=lambda: [Language.EN, Language.BN])
    information_lifetime: List[InformationLifetime] = field(default_factory=lambda: [InformationLifetime.STATIC, InformationLifetime.SLOW_CHANGING])
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    use_hybrid_search: bool = True


@dataclass
class RetrievalResult:
    """Retrieval result schema"""
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "score": self.score,
            "metadata": self.metadata,
            "source": self.source
        }
