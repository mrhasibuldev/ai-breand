"""
Unit tests for SimpleTokenizer
"""

import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer.tokenizer import SimpleTokenizer


def test_special_tokens():
    """Test special tokens initialization"""
    tokenizer = SimpleTokenizer()

    assert tokenizer.PAD_TOKEN == "<PAD>"
    assert tokenizer.UNK_TOKEN == "<UNK>"
    assert tokenizer.BOS_TOKEN == "<BOS>"
    assert tokenizer.EOS_TOKEN == "<EOS>"

    # Check special tokens are in vocabulary
    assert tokenizer.PAD_TOKEN in tokenizer.word_to_id
    assert tokenizer.UNK_TOKEN in tokenizer.word_to_id
    assert tokenizer.BOS_TOKEN in tokenizer.word_to_id
    assert tokenizer.EOS_TOKEN in tokenizer.word_to_id

    print("[PASS] Special tokens test passed")


def test_vocab_building():
    """Test vocabulary building"""
    tokenizer = SimpleTokenizer(vocab_size=100)

    texts = [
        "hello world",
        "hello there",
        "world of ai",
        "ai is amazing"
    ]

    tokenizer.build_vocab(texts, min_freq=1)

    assert tokenizer.is_built
    assert len(tokenizer.word_to_id) > 4  # At least special tokens

    # Check common words are in vocab
    assert "hello" in tokenizer.word_to_id
    assert "world" in tokenizer.word_to_id
    assert "ai" in tokenizer.word_to_id

    print("[PASS] Vocabulary building test passed")


def test_encode_decode():
    """Test encode/decode roundtrip"""
    tokenizer = SimpleTokenizer(vocab_size=100)

    texts = [
        "hello world",
        "this is a test",
        "nexusai brain"
    ]

    tokenizer.build_vocab(texts, min_freq=1)

    # Test encoding
    original_text = "hello world"
    token_ids = tokenizer.encode(original_text, add_special_tokens=True)

    assert len(token_ids) > 0
    assert token_ids[0] == tokenizer.word_to_id[tokenizer.BOS_TOKEN]
    assert token_ids[-1] == tokenizer.word_to_id[tokenizer.EOS_TOKEN]

    # Test decoding
    decoded_text = tokenizer.decode(token_ids, skip_special_tokens=True)
    assert decoded_text == original_text

    print("[PASS] Encode/decode roundtrip test passed")


def test_unknown_token():
    """Test unknown token handling"""
    tokenizer = SimpleTokenizer(vocab_size=100)

    texts = ["hello world"]
    tokenizer.build_vocab(texts, min_freq=1)

    # Encode text with unknown word
    token_ids = tokenizer.encode("hello unknownword world", add_special_tokens=False)

    # Check that unknown word maps to UNK token
    unk_id = tokenizer.word_to_id[tokenizer.UNK_TOKEN]
    assert unk_id in token_ids

    print("[PASS] Unknown token test passed")


def test_save_load():
    """Test save and load functionality"""
    tokenizer = SimpleTokenizer(vocab_size=100)
    texts = ["hello world", "test example"]
    tokenizer.build_vocab(texts, min_freq=1)

    # Save
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        tokenizer.save(temp_path)

        # Load into new tokenizer
        new_tokenizer = SimpleTokenizer(vocab_size=100)
        new_tokenizer.load(temp_path)

        # Verify they're the same
        assert new_tokenizer.word_to_id == tokenizer.word_to_id
        assert new_tokenizer.id_to_word == tokenizer.id_to_word
        assert new_tokenizer.is_built == tokenizer.is_built

        # Test encoding with loaded tokenizer
        original_ids = tokenizer.encode("hello world", add_special_tokens=False)
        loaded_ids = new_tokenizer.encode("hello world", add_special_tokens=False)
        assert original_ids == loaded_ids

        print("[PASS] Save/load test passed")

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def run_all_tests():
    """Run all unit tests"""
    print("Running tokenizer unit tests...\n")

    test_special_tokens()
    test_vocab_building()
    test_encode_decode()
    test_unknown_token()
    test_save_load()

    print("\n[PASS] All tokenizer tests passed!")


if __name__ == "__main__":
    run_all_tests()
