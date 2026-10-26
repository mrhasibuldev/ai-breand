"""
Test Knowledge Ingestion Pipeline

Test the pipeline with a small dataset of 10 documents.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge.pipeline import (
    KnowledgeIngestionPipeline,
    SourceType
)


async def test_ingestion_pipeline():
    """
    Test the ingestion pipeline with sample documents.
    """
    print("=" * 60)
    print("TESTING KNOWLEDGE INGESTION PIPELINE")
    print("=" * 60)

    # Initialize pipeline
    pipeline = KnowledgeIngestionPipeline(
        raw_data_dir="knowledge/raw",
        cleaned_data_dir="knowledge/cleaned"
    )

    # Test documents (small dataset of 10)
    test_documents = [
        {
            "text": """NexusAI is a personal AI health and wellness companion. It helps users track their wellness goals, provide health information, and offer personalized recommendations based on user preferences and health data.""",
            "source": "https://nexusai.example.com/about",
            "source_type": "documentation",
            "metadata": {
                "author": "NexusAI Team",
                "publish_date": "2024-01-01"
            }
        },
        {
            "text": """বাংলাদেশ দক্ষিণ এশিয়ার একটি স্বাধীন রাষ্ট্র। এর রাজধানী ঢাকা এবং এটি বিশ্বের অন্যতম জনবহুল শহর। বাংলাদেশের সরকারি ভাষা বাংলা।""",
            "source": "https://example.com/bangladesh",
            "source_type": "article",
            "metadata": {
                "author": "Wikipedia",
                "publish_date": "2024-01-10"
            }
        },
        {
            "text": """Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction.""",
            "source": "https://example.com/ai-definition",
            "source_type": "article",
            "metadata": {
                "author": "Tech Encyclopedia",
                "publish_date": "2024-01-05"
            }
        },
        {
            "text": """The transformer is a deep learning architecture introduced in 2017. It uses self-attention mechanisms to process sequential data and has become the foundation for modern language models like GPT and BERT.""",
            "source": "https://example.com/transformer-architecture",
            "source_type": "documentation",
            "metadata": {
                "author": "AI Research",
                "publish_date": "2024-01-08"
            }
        },
        {
            "text": """স্বাস্থ্য সুরক্ষা মানুষের জীবনের অন্যতম গুরুত্বপূর্ণ দিক। নিয়মিত ব্যায়াম, সুষম খাদ্যাভ্যাস এবং পর্যাপ্ত ঘুম স্বাস্থ্য ভালো রাখতে সাহায্য করে।""",
            "source": "https://example.com/health-bangla",
            "source_type": "article",
            "metadata": {
                "author": "Health Guide",
                "publish_date": "2024-01-12"
            }
        },
        {
            "text": """Python is a high-level, interpreted programming language known for its simplicity and readability. It is widely used for web development, data science, artificial intelligence, and automation.""",
            "source": "https://example.com/python",
            "source_type": "documentation",
            "metadata": {
                "author": "Python Foundation",
                "publish_date": "2024-01-03"
            }
        },
        {
            "text": """Machine Learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and learn from it.""",
            "source": "https://example.com/machine-learning",
            "source_type": "article",
            "metadata": {
                "author": "ML Guide",
                "publish_date": "2024-01-07"
            }
        },
        {
            "text": """ঢাকা বাংলাদেশের রাজধানী এবং বৃহত্তম শহর। এটি বুড়িগঙ্গা নদীর তীরে অবস্থিত এবং একটি প্রধান সাংস্কৃতিক ও অর্থনৈতিক কেন্দ্র।""",
            "source": "https://example.com/dhaka",
            "source_type": "article",
            "metadata": {
                "author": "City Guide",
                "publish_date": "2024-01-11"
            }
        },
        {
            "text": """A neural network is a computational model inspired by the biological neural networks in the human brain. It consists of interconnected nodes (neurons) organized in layers that process information using connectionist approaches.""",
            "source": "https://example.com/neural-networks",
            "source_type": "documentation",
            "metadata": {
                "author": "Neural Science",
                "publish_date": "2024-01-09"
            }
        },
        {
            "text": """Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language. It enables applications like translation, sentiment analysis, and chatbots.""",
            "source": "https://example.com/nlp",
            "source_type": "article",
            "metadata": {
                "author": "NLP Research",
                "publish_date": "2024-01-06"
            }
        }
    ]

    print(f"\nTesting with {len(test_documents)} documents...\n")

    # Ingest documents
    results = await pipeline.ingest_batch(test_documents)

    # Report results
    success_count = sum(1 for r in results if r.success)
    failure_count = sum(1 for r in results if not r.success)

    print(f"\nResults:")
    print(f"  Success: {success_count}")
    print(f"  Failed: {failure_count}")
    print(f"  Total: {len(results)}")

    # Show details for each result
    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        if result.success:
            print(f"  {i}. [OK] Document: {result.document_id}")
            print(f"     Chunks: {result.chunk_count}")
            print(f"     Time: {result.processing_time_ms:.2f}ms")
            print(f"     Quality: {result.metadata.get('quality_score', 'N/A')}")
            print(f"     Trust: {result.metadata.get('trust_level', 'N/A')}")
            print(f"     Language: {result.metadata.get('language', 'N/A')}")
        else:
            print(f"  {i}. [FAIL] Error: {result.error}")

    # List all cleaned documents
    print("\nCleaned Documents:")
    document_ids = pipeline.list_cleaned_documents()
    for doc_id in document_ids:
        print(f"  - {doc_id}")

    # Test retrieval of a document
    if document_ids:
        print(f"\nRetrieving document: {document_ids[0]}")
        doc = pipeline.get_cleaned_document(document_ids[0])
        if doc:
            print(f"  Text length: {len(doc.text)}")
            print(f"  Word count: {doc.word_count}")
            print(f"  Language: {doc.language.value}")
            print(f"  Quality score: {doc.quality_score}")
            print(f"  Trust level: {doc.trust_level.value}")
            print(f"  Preview: {doc.text[:100]}...")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

    return results


if __name__ == "__main__":
    asyncio.run(test_ingestion_pipeline())
