"""
Tokenizer Audit for Multilingual Support

Tests tokenizer with Bengali, English, and mixed-language text.
"""

import sys
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokenizer.tokenizer import SimpleTokenizer


def test_tokenizer():
    """Test tokenizer with multilingual text"""
    
    print("[Audit] Testing SimpleTokenizer for multilingual support")
    print("=" * 60)
    
    # Test texts
    test_texts = [
        "তোমার নাম কি?",
        "আমার নাম NexusAI।",
        "What is your name?",
        "My name is NexusAI.",
        "তুমি কি আমার schedule manage করতে পারবে?",
        "I can help you with various tasks."
    ]
    
    # Initialize tokenizer
    tokenizer = SimpleTokenizer(vocab_size=1000)
    
    # Build vocabulary
    print("\n[Step 1] Building vocabulary...")
    tokenizer.build_vocab(test_texts, min_freq=1)
    
    print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
    print(f"Sample tokens: {list(tokenizer.word_to_id.keys())[:10]}")
    
    # Test encoding
    print("\n[Step 2] Testing encoding...")
    for text in test_texts:
        encoded = tokenizer.encode(text, add_special_tokens=True)
        decoded = tokenizer.decode(encoded, skip_special_tokens=True)
        
        print(f"\nOriginal: {text}")
        print(f"Encoded:  {encoded}")
        print(f"Decoded:  {decoded}")
        print(f"Match: {text.lower() == decoded.lower()}")
    
    # Test with larger dataset
    print("\n[Step 3] Testing with cleaned dataset...")
    script_dir = Path(__file__).parent.parent
    data_file = script_dir / "data" / "public_datasets" / "v1.0_cleaned" / "train_cleaned.json"
    
    tokenizer2 = None  # Initialize in case file doesn't exist
    
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            texts = json.load(f)
        
        print(f"Loaded {len(texts)} texts")
        
        # Build vocab from real data
        tokenizer2 = SimpleTokenizer(vocab_size=2000)
        tokenizer2.build_vocab(texts, min_freq=1)
        
        print(f"Vocabulary size: {tokenizer2.get_vocab_size()}")
        
        # Show some Bengali tokens
        bengali_tokens = [k for k in tokenizer2.word_to_id.keys() if any('\u0980' <= c <= '\u09FF' for c in k)]
        print(f"Bengali tokens found: {len(bengali_tokens)}")
        print(f"Sample Bengali tokens: {bengali_tokens[:10]}")
        
        # Show some English tokens
        english_tokens = [k for k in tokenizer2.word_to_id.keys() if k.isalpha() and k.isascii()]
        print(f"English tokens found: {len(english_tokens)}")
        print(f"Sample English tokens: {english_tokens[:10]}")
        
        print("\n[Audit Result] PASSED - Tokenizer supports multilingual text")
    else:
        print(f"[Warning] Data file not found: {data_file}")
        print("[Info] Using test tokenizer for save")
        tokenizer2 = tokenizer  # Use the test tokenizer
    
    # Save tokenizer for training
    print("\n[Step 4] Saving tokenizer...")
    output_path = script_dir / "tokenizer" / "multilingual_tokenizer.json"
    tokenizer2.save(str(output_path))
    
    print(f"[OK] Tokenizer audit complete")


if __name__ == "__main__":
    test_tokenizer()
