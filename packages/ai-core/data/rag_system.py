"""
RAG (Retrieval-Augmented Generation) System

Implements vector-based retrieval and augmented generation
for improved AI responses.
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Document representation for RAG"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class SimpleEmbedding:
    """
    Simple embedding model for demonstration
    In production, replace with actual embedding model (e.g., sentence-transformers)
    """

    def __init__(self, dimension: int = 768):
        """
        Initialize embedding model

        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        # Simple character-based embedding for demonstration
        self.char_vocab = {}
        self.vocab_size = 0

    def _build_vocab(self, texts: List[str]):
        """Build character vocabulary"""
        for text in texts:
            for char in text:
                if char not in self.char_vocab:
                    self.char_vocab[char] = len(self.char_vocab)
        self.vocab_size = len(self.char_vocab)
        logger.info(f"Built vocabulary with {self.vocab_size} characters")

    def encode(self, text: str) -> np.ndarray:
        """
        Encode text to embedding vector

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        # Simple character-based encoding
        embedding = np.zeros(self.dimension)

        for i, char in enumerate(text[:self.dimension]):
            idx = ord(char) % self.dimension
            embedding[idx] += 1.0

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts

        Args:
            texts: List of texts

        Returns:
            Matrix of embeddings
        """
        embeddings = []
        for text in texts:
            embedding = self.encode(text)
            embeddings.append(embedding)
        return np.array(embeddings)


class VectorStore:
    """
    Simple in-memory vector store for RAG
    In production, replace with dedicated vector DB (e.g., Pinecone, Chroma, Milvus)
    """

    def __init__(self, dimension: int = 768):
        """
        Initialize vector store

        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        self.documents: List[Document] = []
        self.embeddings: np.ndarray = np.zeros((0, dimension))

    def add_documents(self, documents: List[Document]):
        """
        Add documents to store

        Args:
            documents: List of documents
        """
        for doc in documents:
            if doc.embedding is None:
                logger.warning(f"Document {doc.id} has no embedding, skipping")
                continue

            self.documents.append(doc)

        # Update embeddings matrix
        if self.documents:
            self.embeddings = np.array([doc.embedding for doc in self.documents])
            logger.info(f"Added {len(documents)} documents, total: {len(self.documents)}")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of (document, score) tuples
        """
        if len(self.documents) == 0:
            return []

        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Filter by threshold and create results
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= threshold:
                results.append((self.documents[idx], float(score)))

        return results

    def delete_document(self, doc_id: str):
        """
        Delete document from store

        Args:
            doc_id: Document ID
        """
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        if self.documents:
            self.embeddings = np.array([doc.embedding for doc in self.documents])
        else:
            self.embeddings = np.zeros((0, self.dimension))
        logger.info(f"Deleted document {doc_id}, remaining: {len(self.documents)}")

    def clear(self):
        """Clear all documents"""
        self.documents = []
        self.embeddings = np.zeros((0, self.dimension))
        logger.info("Cleared vector store")


class RAGSystem:
    """
    Retrieval-Augmented Generation System
    """

    def __init__(self, embedding_dimension: int = 768):
        """
        Initialize RAG system

        Args:
            embedding_dimension: Dimension of embeddings
        """
        self.embedding_model = SimpleEmbedding(dimension=embedding_dimension)
        self.vector_store = VectorStore(dimension=embedding_dimension)
        self.loaded = False

    def load_documents(self, data_path: str):
        """
        Load documents from processed data file

        Args:
            data_path: Path to processed data file (JSON or JSONL)
        """
        logger.info(f"Loading documents from: {data_path}")

        documents = []
        path = Path(data_path)

        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    doc = Document(
                        id=item['id'],
                        text=item['text'],
                        metadata=item.get('metadata', {})
                    )
                    documents.append(doc)

        elif path.suffix == '.jsonl':
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line)
                    doc = Document(
                        id=item['id'],
                        text=item['text'],
                        metadata=item.get('metadata', {})
                    )
                    documents.append(doc)

        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents")
        texts = [doc.text for doc in documents]
        embeddings = self.embedding_model.encode_batch(texts)

        # Assign embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding

        # Add to vector store
        self.vector_store.add_documents(documents)
        self.loaded = True

        logger.info(f"Loaded {len(documents)} documents into RAG system")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for query

        Args:
            query: Query text
            top_k: Number of documents to retrieve

        Returns:
            List of retrieved documents with metadata
        """
        if not self.loaded:
            logger.warning("RAG system not loaded, no documents available")
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)

        # Format results
        retrieved = []
        for doc, score in results:
            retrieved.append({
                'id': doc.id,
                'text': doc.text,
                'metadata': doc.metadata,
                'score': score
            })

        logger.info(f"Retrieved {len(retrieved)} documents for query")
        return retrieved

    def augment_prompt(self, query: str, top_k: int = 3) -> str:
        """
        Augment query with retrieved context

        Args:
            query: Original query
            top_k: Number of documents to retrieve

        Returns:
            Augmented prompt with context
        """
        retrieved = self.retrieve(query, top_k=top_k)

        if not retrieved:
            return query

        # Build context string
        context_parts = []
        for i, doc in enumerate(retrieved, 1):
            context_parts.append(f"Context {i} (relevance: {doc['score']:.3f}):\n{doc['text']}")

        context = "\n\n".join(context_parts)

        # Augment prompt
        augmented_prompt = f"""Based on the following context, answer the query:

{context}

Query: {query}

Answer:"""

        return augmented_prompt

    def clear(self):
        """Clear RAG system"""
        self.vector_store.clear()
        self.loaded = False
        logger.info("Cleared RAG system")


if __name__ == "__main__":
    # Example usage
    rag = RAGSystem()

    # Load documents (assuming processed data exists)
    # rag.load_documents("data/processed/processed_20240101_120000.jsonl")

    # Retrieve
    # results = rag.retrieve("What is NexusAI?")
    # print(f"Retrieved {len(results)} documents")

    # Augment prompt
    # augmented = rag.augment_prompt("What is NexusAI?")
    # print(augmented)
