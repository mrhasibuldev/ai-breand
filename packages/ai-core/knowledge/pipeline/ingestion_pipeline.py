"""
Knowledge Ingestion Pipeline

Main pipeline for ingesting documents into the knowledge system.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from .schemas import (
    RawDocument,
    CleanedDocument,
    Chunk,
    IngestionResult,
    SourceType,
    Language,
    TrustLevel,
    InformationLifetime
)
from .data_cleaner import DataCleaner
from .chunker import DocumentChunker


class KnowledgeIngestionPipeline:
    """
    Main knowledge ingestion pipeline.
    """

    def __init__(
        self,
        raw_data_dir: str = "knowledge/raw",
        cleaned_data_dir: str = "knowledge/cleaned"
    ):
        """
        Initialize ingestion pipeline.

        Args:
            raw_data_dir: Directory for raw data
            cleaned_data_dir: Directory for cleaned data
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.cleaned_data_dir = Path(cleaned_data_dir)
        self.cleaner = DataCleaner()
        self.chunker = DocumentChunker()

        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.cleaned_data_dir.mkdir(parents=True, exist_ok=True)

    async def ingest_from_text(
        self,
        text: str,
        source: str,
        source_type: SourceType = SourceType.DATASET,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestionResult:
        """
        Ingest document from text.

        Args:
            text: Document text
            source: Source URL or identifier
            source_type: Type of source
            metadata: Additional metadata

        Returns:
            Ingestion result
        """
        start_time = datetime.now()

        try:
            # Generate document ID
            document_id = f"raw_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:12]}"

            # Create temporary file for raw document
            temp_file = self.raw_data_dir / f"{document_id}.txt"
            temp_file.write_text(text, encoding='utf-8')

            # Compute file hash
            file_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

            # Create raw document
            raw_doc = RawDocument(
                document_id=document_id,
                source=source,
                source_type=source_type,
                collected_at=datetime.now(),
                collected_by="pipeline",
                file_path=str(temp_file),
                file_hash=file_hash,
                size_bytes=len(text.encode('utf-8')),
                language=Language.UNKNOWN,  # Will be detected in cleaning
                mime_type="text/plain",
                license=metadata.get("license") if metadata else None,
                copyright_notice=metadata.get("copyright_notice") if metadata else None,
                access_restricted=False,
                metadata=metadata or {}
            )

            # Clean document
            cleaned_doc = self.cleaner.clean(raw_doc)

            # Chunk document
            chunks = self.chunker.chunk(cleaned_doc)

            # Save cleaned document
            self._save_cleaned_document(cleaned_doc)

            # Save chunks
            self._save_chunks(chunks)

            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            return IngestionResult(
                success=True,
                document_id=cleaned_doc.document_id,
                chunk_count=len(chunks),
                processing_time_ms=processing_time_ms,
                metadata={
                    "raw_document_id": raw_doc.document_id,
                    "quality_score": cleaned_doc.quality_score,
                    "trust_level": cleaned_doc.trust_level.value,
                    "language": cleaned_doc.language.value
                }
            )

        except Exception as e:
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            return IngestionResult(
                success=False,
                error=str(e),
                processing_time_ms=processing_time_ms
            )

    async def ingest_from_file(
        self,
        file_path: str,
        source: str,
        source_type: SourceType = SourceType.USER_UPLOADED,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestionResult:
        """
        Ingest document from file.

        Args:
            file_path: Path to file
            source: Source URL or identifier
            source_type: Type of source
            metadata: Additional metadata

        Returns:
            Ingestion result
        """
        start_time = datetime.now()

        try:
            # Read file
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            text = file_path_obj.read_text(encoding='utf-8', errors='ignore')

            # Use text ingestion
            return await self.ingest_from_text(text, source, source_type, metadata)

        except Exception as e:
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            return IngestionResult(
                success=False,
                error=str(e),
                processing_time_ms=processing_time_ms
            )

    async def ingest_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[IngestionResult]:
        """
        Ingest multiple documents.

        Args:
            documents: List of document dictionaries with 'text' and 'source' keys

        Returns:
            List of ingestion results
        """
        results = []
        for doc in documents:
            text = doc.get("text")
            source = doc.get("source")
            source_type = SourceType(doc.get("source_type", "dataset"))
            metadata = doc.get("metadata")

            if not text or not source:
                results.append(IngestionResult(
                    success=False,
                    error="Missing 'text' or 'source' field"
                ))
                continue

            result = await self.ingest_from_text(text, source, source_type, metadata)
            results.append(result)

        return results

    def _save_cleaned_document(self, document: CleanedDocument):
        """
        Save cleaned document to disk.

        Args:
            document: Cleaned document to save
        """
        output_file = self.cleaned_data_dir / f"{document.document_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)

    def _save_chunks(self, chunks: List[Chunk]):
        """
        Save chunks to disk.

        Args:
            chunks: List of chunks to save
        """
        # Save all chunks to a single JSONL file
        chunks_file = self.cleaned_data_dir / "chunks.jsonl"
        with open(chunks_file, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + '\n')

    def get_cleaned_document(self, document_id: str) -> Optional[CleanedDocument]:
        """
        Retrieve cleaned document by ID.

        Args:
            document_id: Document ID

        Returns:
            Cleaned document or None if not found
        """
        file_path = self.cleaned_data_dir / f"{document_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert string enum values back to enums
        language = data["language"]
        if isinstance(language, str):
            language = Language(language)

        trust_level = data["trust_level"]
        if isinstance(trust_level, str):
            trust_level = TrustLevel(trust_level)

        information_lifetime = data["information_lifetime"]
        if isinstance(information_lifetime, str):
            information_lifetime = InformationLifetime(information_lifetime)

        return CleanedDocument(
            document_id=data["document_id"],
            raw_document_id=data["raw_document_id"],
            text=data["text"],
            language=language,
            quality_score=data["quality_score"],
            trust_level=trust_level,
            information_lifetime=information_lifetime,
            word_count=data["word_count"],
            char_count=data["char_count"],
            processed_at=datetime.fromisoformat(data["processed_at"]),
            processing_metadata=data["processing_metadata"],
            source=data["source"]
        )

    def list_cleaned_documents(self) -> List[str]:
        """
        List all cleaned document IDs.

        Returns:
            List of document IDs
        """
        documents = []
        for file_path in self.cleaned_data_dir.glob("clean_*.json"):
            document_id = file_path.stem
            documents.append(document_id)

        return documents
