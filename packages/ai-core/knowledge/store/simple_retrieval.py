"""
Simple Retrieval System

Quick implementation using keyword matching for immediate functionality.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class SimpleRetrievalSystem:
    """
    Simple keyword-based retrieval system for immediate use.
    """

    def __init__(self, cleaned_data_dir: str = None):
        """
        Initialize retrieval system.

        Args:
            cleaned_data_dir: Directory containing cleaned documents
        """
        if cleaned_data_dir is None:
            # Use absolute path from knowledge directory
            current_dir = Path(__file__).parent.parent
            cleaned_data_dir = current_dir / "cleaned"
        self.cleaned_data_dir = Path(cleaned_data_dir)
        self.documents: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        self.loaded = False

    def load(self):
        """Load documents and chunks from disk."""
        print("[SimpleRetrieval] Loading documents...")

        # Load cleaned documents
        for file_path in self.cleaned_data_dir.glob("clean_*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                self.documents.append(doc)

        # Load chunks
        chunks_file = self.cleaned_data_dir / "chunks.jsonl"
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunk = json.loads(line)
                        self.chunks.append(chunk)

        self.loaded = True
        print(f"[SimpleRetrieval] Loaded {len(self.documents)} documents and {len(self.chunks)} chunks")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for query using keyword matching.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of relevant chunks with scores
        """
        if not self.loaded:
            self.load()

        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Remove common words for better matching
        stop_words = {'is', 'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'what', 'how', 'why', 'when', 'where', 'who', 'tell', 'me', 'about', 'explain', 'define', 'describe'}
        query_keywords = query_words - stop_words

        results = []

        for chunk in self.chunks:
            chunk_text = chunk.get("text", "").lower()
            chunk_words = set(chunk_text.split())

            # Calculate overlap score with keywords
            overlap = len(query_keywords & chunk_words)
            if overlap > 0:
                # Score based on keyword overlap
                score = overlap / len(query_keywords) if query_keywords else 0

                # Bonus for exact phrase match
                if query_lower in chunk_text:
                    score += 0.5

                results.append({
                    "chunk_id": chunk.get("chunk_id"),
                    "document_id": chunk.get("document_id"),
                    "text": chunk.get("text"),
                    "score": score,
                    "metadata": chunk
                })

        # Sort by score and return top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Get formatted context for query.

        Args:
            query: Query text
            top_k: Number of chunks to retrieve

        Returns:
            Formatted context string
        """
        retrieved = self.retrieve(query, top_k)

        if not retrieved:
            return ""

        context_parts = []
        for i, result in enumerate(retrieved, 1):
            context_parts.append(f"Context {i} (relevance: {result['score']:.2f}):\n{result['text']}")

        return "\n\n".join(context_parts)

    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search documents by keyword.

        Args:
            query: Query text

        Returns:
            List of matching documents
        """
        if not self.loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for doc in self.documents:
            doc_text = doc.get("text", "").lower()
            if query_lower in doc_text:
                results.append(doc)

        return results


# Singleton instance
retrieval_system = SimpleRetrievalSystem()
