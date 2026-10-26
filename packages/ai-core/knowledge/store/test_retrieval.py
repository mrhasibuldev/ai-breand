"""
Test Simple Retrieval System
"""

import sys
from pathlib import Path

# Add knowledge directory to path
knowledge_dir = Path(__file__).parent.parent
sys.path.insert(0, str(knowledge_dir))

from store.simple_retrieval import SimpleRetrievalSystem


def test_retrieval():
    """Test the retrieval system."""
    print("=" * 60)
    print("TESTING SIMPLE RETRIEVAL SYSTEM")
    print("=" * 60)

    retrieval = SimpleRetrievalSystem()
    retrieval.load()

    # Test queries
    queries = [
        "What is NexusAI?",
        "AI",
        "Python",
        "Machine Learning",
        "Bangladesh",
        "health"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        results = retrieval.retrieve(query, top_k=2)

        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['score']:.2f}")
                print(f"     Text: {result['text'][:100]}...")
        else:
            print("  No results found")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_retrieval()
