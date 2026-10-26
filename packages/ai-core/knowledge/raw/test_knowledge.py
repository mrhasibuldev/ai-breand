"""
Test Knowledge Retrieval

This script tests the knowledge retrieval system with the ingested data.
"""

import sys
from pathlib import Path

# Add parent directories to path
current_file = Path(__file__).resolve()
knowledge_dir = current_file.parent.parent
ai_core_dir = knowledge_dir.parent
sys.path.insert(0, str(knowledge_dir))
sys.path.insert(0, str(ai_core_dir))

from store.simple_retrieval import retrieval_system


def test_retrieval():
    """Test the retrieval system with sample queries."""
    print("=== Testing Knowledge Retrieval System ===\n")

    # Load data
    print("Loading knowledge base...")
    retrieval_system.load()

    # Test queries
    test_queries = [
        "What is science?",
        "Tell me about physics",
        "Computer science definition",
        "What is mathematics?",
        "Biology and its study",
        "Chemistry basics",
        "History as a discipline",
        "Philosophy questions",
        "Economics study",
        "Geography definition"
    ]

    print(f"\nRunning {len(test_queries)} test queries...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        results = retrieval_system.retrieve(query, top_k=2)

        if results:
            print(f"  Found {len(results)} relevant chunks:")
            for j, result in enumerate(results, 1):
                print(f"    {j}. Score: {result['score']:.2f}")
                # Show first 100 chars of the chunk
                text_preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                print(f"       {text_preview}")
        else:
            print("  No results found")
        print()

    print("=== Test Complete ===")


if __name__ == "__main__":
    test_retrieval()
