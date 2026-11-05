"""
Test BPE Tokenizer with Whitespace Preservation

Separate test file to avoid Windows encoding issues.
"""

import sys
import json
from pathlib import Path

# Fix Windows encoding for UTF-8 support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
tokenizer_dir = Path(__file__).parent
sys.path.insert(0, str(tokenizer_dir))

from bpe_tokenizer import BPETokenizer

def test_bpe_tokenizer():
    """Test BPE tokenizer implementation with whitespace preservation"""
    print("[BPE Tokenizer] Testing implementation (v1.1.0)...")

    # Sample texts including required test cases
    texts = [
        "আমার নাম NexusAI",
        "My name is NexusAI.",
        "আমি একটি AI Brain তৈরি করছি।",
        "I am building an AI Brain.",
        "Hello, how are you?",
        "বাংলা এবং English mixed sentence"
    ]

    tokenizer = BPETokenizer(vocab_size=100)  # Small vocab for testing
    stats = tokenizer.train(texts)

    print(f"[BPE Tokenizer] Training stats: {stats}")

    # Test round-trip on required examples
    test_cases = [
        "আমার নাম NexusAI",
        "আমি একটি AI Brain তৈরি করছি।",
        "My name is NexusAI.",
        "I am building an AI Brain.",
        "Hello, how are you?",
        "বাংলা এবং English mixed sentence"
    ]

    print("\n[BPE Tokenizer] Round-trip Tests:")
    all_passed = True

    for test_text in test_cases:
        encoded = tokenizer.encode(test_text)
        decoded = tokenizer.decode(encoded)
        passed = test_text == decoded
        all_passed = all_passed and passed

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} '{test_text}' → '{decoded}'")

    # Test special cases
    print("\n[BPE Tokenizer] Special Cases:")

    # Multiple spaces
    test_text = "Hello  world"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)
    passed = test_text == decoded
    all_passed = all_passed and passed
    print(f"{'✅ PASS' if passed else '❌ FAIL'} Multiple spaces: '{test_text}' → '{decoded}'")

    # Leading/trailing spaces
    test_text = "  Hello world  "
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)
    passed = test_text == decoded
    all_passed = all_passed and passed
    print(f"{'✅ PASS' if passed else '❌ FAIL'} Leading/trailing spaces: '{test_text}' → '{decoded}'")

    # Empty string
    test_text = ""
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)
    passed = test_text == decoded
    all_passed = all_passed and passed
    print(f"{'✅ PASS' if passed else '❌ FAIL'} Empty string: '{test_text}' → '{decoded}'")

    # Save tokenizer
    output_dir = tokenizer_dir / "bpe_tokenizer_fixed"
    tokenizer.save(str(output_dir))

    # Test loading
    tokenizer2 = BPETokenizer()
    tokenizer2.load(str(output_dir))

    # Verify vocab size
    print(f"\n[BPE Tokenizer] Vocab size: {tokenizer2.get_vocab_size()}")
    print(f"[BPE Tokenizer] Special token IDs: {tokenizer2.get_special_token_ids()}")

    print(f"\n[BPE Tokenizer] All tests: {'✅ PASSED' if all_passed else '❌ FAILED'}")

    return all_passed

if __name__ == "__main__":
    success = test_bpe_tokenizer()
    sys.exit(0 if success else 1)
