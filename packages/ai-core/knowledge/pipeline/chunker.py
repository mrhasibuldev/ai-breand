"""
Document Chunker

Semantic chunking strategy for splitting documents into manageable pieces.
"""

import re
from typing import List, Tuple
from datetime import datetime
import hashlib

from .schemas import CleanedDocument, Chunk


class DocumentChunker:
    """
    Document chunker with semantic splitting.
    """

    def __init__(
        self,
        chunk_size: int = 350,
        chunk_overlap: int = 50,
        min_chunk_size: int = 20
    ):
        """
        Initialize document chunker.

        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk(self, document: CleanedDocument) -> List[Chunk]:
        """
        Split document into chunks.

        Args:
            document: Cleaned document to chunk

        Returns:
            List of chunks
        """
        # Split by paragraphs first
        paragraphs = self._split_into_paragraphs(document.text)

        # Group paragraphs into chunks
        chunks = self._group_paragraphs_into_chunks(
            paragraphs,
            document.document_id
        )

        # Post-process chunks
        chunks = self._post_process_chunks(chunks, document.document_id)

        return chunks

    def _split_into_paragraphs(self, text: str) -> List[Tuple[str, Optional[str]]]:
        """
        Split text into paragraphs with section titles.

        Args:
            text: Input text

        Returns:
            List of (paragraph, section_title) tuples
        """
        paragraphs = []
        current_section = None

        # Split by double newlines
        raw_paragraphs = text.split('\n\n')

        for para in raw_paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if this is a heading (all caps, starts with #, etc.)
            if self._is_heading(para):
                current_section = para
                continue

            paragraphs.append((para, current_section))

        return paragraphs

    def _is_heading(self, text: str) -> bool:
        """
        Check if text is a heading.

        Args:
            text: Text to check

        Returns:
            True if heading, False otherwise
        """
        # Check for markdown-style headings
        if text.startswith('#'):
            return True

        # Check for all caps (likely a heading)
        if text.isupper() and len(text) < 100:
            return True

        # Check for numbered headings
        if re.match(r'^\d+\.\s+', text):
            return True

        return False

    def _group_paragraphs_into_chunks(
        self,
        paragraphs: List[Tuple[str, Optional[str]]],
        document_id: str
    ) -> List[Chunk]:
        """
        Group paragraphs into chunks based on token count.

        Args:
            paragraphs: List of (paragraph, section_title) tuples
            document_id: Document ID

        Returns:
            List of chunks
        """
        chunks = []
        current_chunk_text = []
        current_chunk_tokens = 0
        current_section = None
        chunk_index = 0

        for para, section_title in paragraphs:
            para_tokens = len(para.split())

            # Update current section
            if section_title:
                current_section = section_title

            # If adding this paragraph would exceed chunk size
            if current_chunk_tokens + para_tokens > self.chunk_size and current_chunk_text:
                # Create chunk
                chunk_text = ' '.join(current_chunk_text)
                chunk = self._create_chunk(
                    chunk_text,
                    document_id,
                    chunk_index,
                    current_section
                )
                chunks.append(chunk)
                chunk_index += 1

                # Start new chunk with overlap
                current_chunk_text = self._get_overlap_paragraphs(current_chunk_text)
                current_chunk_tokens = sum(len(p.split()) for p in current_chunk_text)

            # Add paragraph to current chunk
            current_chunk_text.append(para)
            current_chunk_tokens += para_tokens

        # Add final chunk if not empty
        if current_chunk_text:
            chunk_text = ' '.join(current_chunk_text)
            chunk = self._create_chunk(
                chunk_text,
                document_id,
                chunk_index,
                current_section
            )
            chunks.append(chunk)

        return chunks

    def _get_overlap_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """
        Get paragraphs for overlap.

        Args:
            paragraphs: Current chunk paragraphs

        Returns:
            Overlap paragraphs
        """
        overlap_tokens = 0
        overlap_paragraphs = []

        # Take paragraphs from the end until we reach overlap size
        for para in reversed(paragraphs):
            para_tokens = len(para.split())
            if overlap_tokens + para_tokens <= self.chunk_overlap:
                overlap_paragraphs.insert(0, para)
                overlap_tokens += para_tokens
            else:
                break

        return overlap_paragraphs

    def _create_chunk(
        self,
        text: str,
        document_id: str,
        chunk_index: int,
        section_title: Optional[str]
    ) -> Chunk:
        """
        Create a chunk object.

        Args:
            text: Chunk text
            document_id: Document ID
            chunk_index: Chunk index
            section_title: Section title

        Returns:
            Chunk object
        """
        token_count = len(text.split())
        chunk_id = f"chunk_{datetime.now().strftime('%Y%m%d')}_{hashlib.sha256(text.encode()).hexdigest()[:12]}"

        return Chunk(
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            text=text,
            token_count=token_count,
            section_title=section_title,
            section_hierarchy=[section_title] if section_title else [],
            position_in_document=0.0  # Will be set in post-processing
        )

    def _post_process_chunks(self, chunks: List[Chunk], document_id: str) -> List[Chunk]:
        """
        Post-process chunks to set metadata.

        Args:
            chunks: List of chunks
            document_id: Document ID

        Returns:
            Post-processed chunks
        """
        if not chunks:
            return chunks

        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            # Set position in document
            chunk.position_in_document = i / total_chunks if total_chunks > 0 else 0.0

            # Set preceding/following chunk IDs
            if i > 0:
                chunk.preceding_chunk_id = chunks[i - 1].chunk_id
            if i < total_chunks - 1:
                chunk.following_chunk_id = chunks[i + 1].chunk_id

            # Filter out chunks that are too small
            if chunk.token_count < self.min_chunk_size:
                chunks[i] = None

        # Remove None chunks
        chunks = [c for c in chunks if c is not None]

        return chunks
