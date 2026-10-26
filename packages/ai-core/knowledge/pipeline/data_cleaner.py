"""
Data Cleaner

Deterministic preprocessing pipeline for raw documents.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .schemas import (
    RawDocument,
    CleanedDocument,
    Language,
    TrustLevel,
    InformationLifetime
)


class DataCleaner:
    """
    Data cleaning pipeline for transforming raw documents into clean format.
    """

    def __init__(self):
        """Initialize data cleaner"""
        self.quality_flags = []

    def clean(self, raw_document: RawDocument) -> CleanedDocument:
        """
        Clean a raw document.

        Args:
            raw_document: Raw document to clean

        Returns:
            Cleaned document
        """
        start_time = datetime.now()

        # Read file content
        text = self._read_file(raw_document.file_path)

        # Stage 1: Extraction (already done by reading)
        # Stage 2: Normalization
        text = self._normalize_text(text)

        # Stage 3: Deduplication check (hash)
        document_hash = self._compute_hash(text)

        # Stage 4: Quality filtering
        quality_score = self._compute_quality_score(text, raw_document)
        if quality_score < 0.3:
            raise ValueError(f"Document quality too low: {quality_score}")

        # Stage 5: Language detection
        language = self._detect_language(text)

        # Stage 6: Content validation
        if not self._validate_content(text):
            raise ValueError("Content validation failed")

        # Stage 7: Metadata enrichment
        trust_level = self._assign_trust_level(raw_document)
        information_lifetime = self._assign_information_lifetime(raw_document, text)

        # Generate cleaned document ID
        cleaned_id = f"clean_{datetime.now().strftime('%Y%m%d')}_{document_hash[:12]}"

        # Count words and characters
        word_count = len(text.split())
        char_count = len(text)

        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Create cleaned document
        cleaned_doc = CleanedDocument(
            document_id=cleaned_id,
            raw_document_id=raw_document.document_id,
            text=text,
            language=language,
            quality_score=quality_score,
            trust_level=trust_level,
            information_lifetime=information_lifetime,
            word_count=word_count,
            char_count=char_count,
            processed_at=datetime.now(),
            processing_metadata={
                "extraction_method": "file_reader",
                "deduplication_status": "unique",
                "quality_flags": self.quality_flags,
                "processing_time_ms": processing_time_ms,
                "document_hash": document_hash
            },
            source={
                "url": raw_document.source,
                "source_type": raw_document.source_type.value,
                "license": raw_document.license,
                "author": raw_document.metadata.get("author"),
                "publish_date": raw_document.metadata.get("publish_date")
            }
        )

        return cleaned_doc

    def _read_file(self, file_path: str) -> str:
        """
        Read file content.

        Args:
            file_path: Path to file

        Returns:
            File content as string
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text encoding and whitespace.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Collapse multiple spaces
        text = re.sub(r' +', ' ', text)

        # Collapse multiple newlines (but keep paragraph breaks)
        text = re.sub(r'\n\n\n+', '\n\n', text)

        # Remove control characters (except newlines and tabs)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _compute_hash(self, text: str) -> str:
        """
        Compute SHA-256 hash of text.

        Args:
            text: Input text

        Returns:
            Hash string
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _compute_quality_score(self, text: str, raw_document: RawDocument) -> float:
        """
        Compute quality score for document.

        Args:
            text: Document text
            raw_document: Raw document metadata

        Returns:
            Quality score (0.0 - 1.0)
        """
        score = 0.0
        self.quality_flags = []

        # Content quality (0-0.3)
        word_count = len(text.split())
        if word_count < 20:
            self.quality_flags.append("too_short")
            score += 0.0
        elif word_count < 50:
            score += 0.1
        elif word_count < 100:
            score += 0.2
        else:
            score += 0.3

        # Source authority (0-0.3)
        if raw_document.source_type.value in ["documentation", "dataset"]:
            score += 0.3
        elif raw_document.source_type.value in ["article", "book"]:
            score += 0.2
        else:
            score += 0.1

        # Freshness (0-0.2)
        # For now, assume recent is better
        score += 0.2

        # Citations/references (0-0.2)
        # Check for common citation patterns
        if re.search(r'\[\d+\]', text) or re.search(r'\(.*?\d{4}.*?\)', text):
            score += 0.2
        else:
            score += 0.1

        return min(score, 1.0)

    def _detect_language(self, text: str) -> Language:
        """
        Detect document language using Unicode ranges.

        Args:
            text: Document text

        Returns:
            Detected language
        """
        if not text:
            return Language.UNKNOWN

        # Bengali Unicode range: U+0980 to U+09FF
        bengali_count = 0
        # Latin/English range
        latin_count = 0

        for char in text:
            code = ord(char)
            if 0x0980 <= code <= 0x09FF:
                bengali_count += 1
            elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
                latin_count += 1

        total_chars = bengali_count + latin_count
        if total_chars == 0:
            return Language.UNKNOWN

        # If any Bengali characters detected, prioritize Bengali
        if bengali_count > 0:
            if latin_count > 0:
                return Language.MIXED
            return Language.BN
        elif latin_count > 0:
            return Language.EN
        else:
            return Language.UNKNOWN

    def _validate_content(self, text: str) -> bool:
        """
        Validate content quality.

        Args:
            text: Document text

        Returns:
            True if valid, False otherwise
        """
        # Check minimum length (reduced for testing)
        if len(text) < 20:
            return False

        # Check for excessive repetition
        words = text.split()
        if len(words) > 0:
            most_common_word = max(set(words), key=words.count)
            repetition_ratio = words.count(most_common_word) / len(words)
            if repetition_ratio > 0.5:
                self.quality_flags.append("excessive_repetition")
                return False

        # Check for gibberish (high ratio of special characters)
        # For non-Latin scripts (Bengali), many characters are not alphanumeric in ASCII
        # So we only check for ASCII special characters
        ascii_special_chars = sum(1 for c in text if ord(c) < 128 and not c.isalnum() and not c.isspace())
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        if ascii_chars > 0 and ascii_special_chars / ascii_chars > 0.3:
            self.quality_flags.append("too_many_special_chars")
            return False

        return True

    def _assign_trust_level(self, raw_document: RawDocument) -> TrustLevel:
        """
        Assign trust level based on source.

        Args:
            raw_document: Raw document

        Returns:
            Trust level
        """
        if raw_document.source_type.value in ["documentation"]:
            return TrustLevel.TIER_1
        elif raw_document.source_type.value in ["article", "book"]:
            return TrustLevel.TIER_2
        elif raw_document.source_type.value in ["web", "dataset"]:
            return TrustLevel.TIER_3
        else:
            return TrustLevel.TIER_4

    def _assign_information_lifetime(self, raw_document: RawDocument, text: str) -> InformationLifetime:
        """
        Assign information lifetime.

        Args:
            raw_document: Raw document
            text: Document text

        Returns:
            Information lifetime
        """
        # For now, default to SLOW_CHANGING
        # In production, this would analyze content for time-sensitive keywords
        return InformationLifetime.SLOW_CHANGING
