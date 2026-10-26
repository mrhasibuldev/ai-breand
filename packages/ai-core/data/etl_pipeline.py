"""
ETL Pipeline for Automated Data Ingestion

Extracts, Transforms, and Loads data from multiple sources
for AI model training and RAG system.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    ETL Pipeline for automated data ingestion
    """

    def __init__(self, data_dir: str = "data/raw", output_dir: str = "data/processed"):
        """
        Initialize ETL pipeline

        Args:
            data_dir: Directory containing raw data sources
            output_dir: Directory for processed data
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract(self, sources: List[str]) -> Dict[str, List[str]]:
        """
        Extract data from multiple sources

        Args:
            sources: List of source identifiers (file paths, URLs, etc.)

        Returns:
            Dictionary mapping source to extracted data
        """
        extracted = {}

        for source in sources:
            logger.info(f"Extracting from: {source}")

            # Local file extraction
            if os.path.exists(source):
                data = self._extract_from_file(source)
                extracted[source] = data
            # URL extraction (placeholder for future)
            elif source.startswith(('http://', 'https://')):
                data = self._extract_from_url(source)
                extracted[source] = data
            else:
                logger.warning(f"Unknown source type: {source}")

        return extracted

    def _extract_from_file(self, file_path: str) -> List[str]:
        """Extract data from local file"""
        from importer import DataImporter

        if file_path.endswith('.json'):
            return DataImporter.import_json(file_path)
        elif file_path.endswith('.csv'):
            return DataImporter.import_csv(file_path)
        elif file_path.endswith('.txt'):
            return DataImporter.import_txt(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return []

    def _extract_from_url(self, url: str) -> List[str]:
        """Extract data from URL (placeholder)"""
        logger.info(f"URL extraction not yet implemented: {url}")
        return []

    def transform(self, extracted_data: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Transform and clean extracted data

        Args:
            extracted_data: Dictionary of extracted data from sources

        Returns:
            List of transformed data records
        """
        from data_cleaner import DataCleaner

        cleaner = DataCleaner()
        transformed = []

        for source, data in extracted_data.items():
            logger.info(f"Transforming data from: {source}")

            for idx, text in enumerate(data):
                # Clean the text
                cleaned = cleaner.clean_text(text)

                # Skip empty or too short texts
                if len(cleaned) < 3:
                    continue

                # Create record
                record = {
                    'id': f"{source}_{idx}",
                    'source': source,
                    'text': cleaned,
                    'metadata': {
                        'length': len(cleaned),
                        'word_count': len(cleaned.split()),
                        'processed_at': datetime.now().isoformat()
                    }
                }

                transformed.append(record)

        logger.info(f"Transformed {len(transformed)} records")
        return transformed

    def load(self, transformed_data: List[Dict[str, Any]], format: str = 'json') -> str:
        """
        Load transformed data to storage

        Args:
            transformed_data: List of transformed records
            format: Output format ('json', 'jsonl')

        Returns:
            Path to output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"processed_{timestamp}.{format}"

        logger.info(f"Loading data to: {output_file}")

        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(transformed_data, f, ensure_ascii=False, indent=2)
        elif format == 'jsonl':
            with open(output_file, 'w', encoding='utf-8') as f:
                for record in transformed_data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Loaded {len(transformed_data)} records to {output_file}")
        return str(output_file)

    def run(self, sources: List[str], format: str = 'json') -> str:
        """
        Run complete ETL pipeline

        Args:
            sources: List of data sources
            format: Output format

        Returns:
            Path to output file
        """
        logger.info("Starting ETL pipeline")

        # Extract
        extracted = self.extract(sources)

        # Transform
        transformed = self.transform(extracted)

        # Load
        output_path = self.load(transformed, format)

        logger.info("ETL pipeline completed")
        return output_path


class VectorETLPipeline(ETLPipeline):
    """
    Extended ETL pipeline for vector database integration
    """

    def __init__(self, data_dir: str = "data/raw", output_dir: str = "data/processed"):
        super().__init__(data_dir, output_dir)
        self.vector_db_config = {
            'dimension': 768,  # Will be updated based on embedding model
            'index_type': 'hnsw',
            'metric': 'cosine'
        }

    def transform_for_vectors(self, extracted_data: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Transform data specifically for vector indexing

        Args:
            extracted_data: Dictionary of extracted data

        Returns:
            List of records ready for vectorization
        """
        from data_cleaner import DataCleaner

        cleaner = DataCleaner()
        transformed = []

        for source, data in extracted_data.items():
            logger.info(f"Transforming for vectors from: {source}")

            for idx, text in enumerate(data):
                # Clean the text
                cleaned = cleaner.clean_text(text)

                # Skip empty or too short texts
                if len(cleaned) < 10:
                    continue

                # Split into chunks for better vector search
                chunks = self._chunk_text(cleaned, chunk_size=512, overlap=50)

                for chunk_idx, chunk in enumerate(chunks):
                    record = {
                        'id': f"{source}_{idx}_{chunk_idx}",
                        'source': source,
                        'text': chunk,
                        'metadata': {
                            'original_id': f"{source}_{idx}",
                            'chunk_index': chunk_idx,
                            'total_chunks': len(chunks),
                            'length': len(chunk),
                            'processed_at': datetime.now().isoformat()
                        }
                    }

                    transformed.append(record)

        logger.info(f"Transformed {len(transformed)} chunks for vectorization")
        return transformed

    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at word boundary
            if end < len(text) and not text[end].isspace():
                last_space = chunk.rfind(' ')
                if last_space > 0:
                    chunk = chunk[:last_space]
                    end = start + last_space

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def run_for_rag(self, sources: List[str]) -> str:
        """
        Run ETL pipeline specifically for RAG system

        Args:
            sources: List of data sources

        Returns:
            Path to output file
        """
        logger.info("Starting RAG ETL pipeline")

        # Extract
        extracted = self.extract(sources)

        # Transform for vectors
        transformed = self.transform_for_vectors(extracted)

        # Load
        output_path = self.load(transformed, 'jsonl')

        logger.info("RAG ETL pipeline completed")
        return output_path


if __name__ == "__main__":
    # Example usage
    pipeline = ETLPipeline()

    # Run with sample sources
    sources = [
        "data/synthetic/train.json",
        "data/synthetic/validation.json"
    ]

    output = pipeline.run(sources)
    print(f"ETL pipeline completed. Output: {output}")
