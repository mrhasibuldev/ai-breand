"""
Train BPE Tokenizer on Collected Wikipedia Data

Trains and evaluates BPE tokenizer on collected Wikipedia articles.
Tests multiple vocabulary sizes.
"""

import json
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add tokenizer directory to path
tokenizer_dir = Path(__file__).parent.parent / 'tokenizer'
sys.path.insert(0, str(tokenizer_dir))

from bpe_tokenizer import BPETokenizer


def load_collected_data(data_dir: Path) -> list:
    """Load collected Wikipedia articles"""
    texts = []

    # Load English articles
    en_dir = data_dir / 'en'
    if en_dir.exists():
        for json_file in en_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                article = json.load(f)
                texts.append(article['text'])

    # Load Bengali articles
    bn_dir = data_dir / 'bn'
    if bn_dir.exists():
        for json_file in bn_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                article = json.load(f)
                texts.append(article['text'])

    return texts


def evaluate_tokenizer(tokenizer, test_texts: list) -> dict:
    """Evaluate tokenizer on test texts"""
    results = {
        'vocab_size': tokenizer.get_vocab_size(),
        'total_texts': len(test_texts),
        'total_chars': sum(len(t) for t in test_texts),
        'total_words': sum(len(t.split()) for t in test_texts),
        'round_trip_tests': []
    }

    # Round-trip tests
    for text in test_texts[:10]:  # Test first 10
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded)
        passed = text == decoded
        results['round_trip_tests'].append({
            'original': text[:50] + '...' if len(text) > 50 else text,
            'decoded': decoded[:50] + '...' if len(decoded) > 50 else decoded,
            'passed': passed
        })

    # Calculate token stats
    total_tokens = 0
    for text in test_texts:
        total_tokens += len(tokenizer.encode(text, add_special_tokens=False))

    results['total_tokens'] = total_tokens
    results['chars_per_token'] = results['total_chars'] / total_tokens if total_tokens > 0 else 0
    results['words_per_token'] = results['total_words'] / total_tokens if total_tokens > 0 else 0

    return results


def main():
    """Main training and evaluation function"""
    print("[Tokenizer Evaluation] Loading collected Wikipedia data...")

    # Load collected data
    data_dir = Path(__file__).parent / 'collected' / 'wikipedia'
    texts = load_collected_data(data_dir)

    print(f"[Tokenizer Evaluation] Loaded {len(texts)} articles")
    print(f"[Tokenizer Evaluation] Total characters: {sum(len(t) for t in texts)}")
    print(f"[Tokenizer Evaluation] Total words: {sum(len(t.split()) for t in texts)}")

    # Test vocabulary sizes
    vocab_sizes = [1000, 2000, 5000, 10000, 20000, 30000]
    all_results = {}

    for vocab_size in vocab_sizes:
        print(f"\n[Tokenizer Evaluation] Training with vocab size: {vocab_size}")

        tokenizer = BPETokenizer(vocab_size=vocab_size)
        stats = tokenizer.train(texts)

        print(f"[Tokenizer Evaluation] Trained vocab size: {stats['vocab_size']}")
        print(f"[Tokenizer Evaluation] Number of merges: {stats['num_merges']}")

        # Evaluate
        results = evaluate_tokenizer(tokenizer, texts)
        all_results[vocab_size] = results

        print(f"[Tokenizer Evaluation] Total tokens: {results['total_tokens']}")
        print(f"[Tokenizer Evaluation] Chars per token: {results['chars_per_token']:.2f}")
        print(f"[Tokenizer Evaluation] Words per token: {results['words_per_token']:.2f}")

        # Round-trip test results
        passed = sum(1 for t in results['round_trip_tests'] if t['passed'])
        print(f"[Tokenizer Evaluation] Round-trip tests: {passed}/{len(results['round_trip_tests'])} passed")

    # Save results
    output_dir = Path(__file__).parent / 'collected' / 'wikipedia'
    results_file = output_dir / 'tokenizer_evaluation_results.json'

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n[Tokenizer Evaluation] Results saved to {results_file}")

    # Print summary
    print("\n=== TOKENIZER EVALUATION SUMMARY ===")
    for vocab_size, results in all_results.items():
        print(f"\nVocab Size: {vocab_size}")
        print(f"  Actual Vocab: {results['vocab_size']}")
        print(f"  Total Tokens: {results['total_tokens']}")
        print(f"  Chars per Token: {results['chars_per_token']:.2f}")
        print(f"  Words per Token: {results['words_per_token']:.2f}")
        passed = sum(1 for t in results['round_trip_tests'] if t['passed'])
        print(f"  Round-trip: {passed}/{len(results['round_trip_tests'])} passed")


if __name__ == "__main__":
    main()
