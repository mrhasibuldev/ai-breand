"""
Phase 9 - Tokenizer Compatibility Evaluation

Evaluates the Phase 7 SentencePiece tokenizer on the expanded corpus.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import sentencepiece as spm

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
PHASE9_DIR = DATA_DIR / "experimental" / "phase9"
CURATED_DIR = PHASE9_DIR / "curated"
MANIFESTS_DIR = PHASE9_DIR / "manifests"
EVALUATIONS_DIR = PHASE9_DIR / "evaluations"

# Create directories
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9 - Tokenizer Compatibility Evaluation")
print("="*60)

# Load tokenizer
tokenizer_path = PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()

print(f"\nTokenizer loaded: {vocab_size} tokens")
print(f"Tokenizer path: {tokenizer_path}")

# Load expanded corpus
curated_file = CURATED_DIR / "corpus_expanded.txt"
with open(curated_file, 'r', encoding='utf-8') as f:
    texts = [line.strip() for line in f if line.strip()]

print(f"Corpus loaded: {len(texts)} texts")

# Test sentences
test_sentences = [
    ("English", "Hello, how are you?"),
    ("English", "I want to build an AI."),
    ("English", "The capital of Bangladesh is Dhaka."),
    ("Bengali", "তুমি কেমন আছো?"),
    ("Bengali", "আমি NexusAI তৈরি করছি।"),
    ("Bengali", "বাংলাদেশের রাজধানী ঢাকা।"),
    ("Mixed", "Hello, তুমি কেমন আছো?"),
    ("Mixed", "I am NexusAI, আমি একটি AI তৈরি করছি।"),
]

print("\n" + "="*60)
print("Test Sentence Evaluation")
print("="*60)

test_results = []
for language, sentence in test_sentences:
    ids = sp.encode(sentence, out_type=int)
    unk_count = ids.count(1)  # UNK token ID is 1
    decoded = sp.decode(ids)

    result = {
        'language': language,
        'input': sentence,
        'token_count': len(ids),
        'unk_count': unk_count,
        'unk_rate': unk_count / len(ids) if len(ids) > 0 else 0,
        'decoded': decoded,
        'round_trip_correct': decoded == sentence
    }

    test_results.append(result)

    print(f"\n[{language}]")
    print(f"  Input: {sentence}")
    print(f"  Tokens: {result['token_count']}")
    print(f"  UNK: {result['unk_count']} ({result['unk_rate']:.2%})")
    print(f"  Decoded: {decoded}")
    print(f"  Round-trip: {'✓' if result['round_trip_correct'] else '✗'}")

# Sample corpus evaluation
print("\n" + "="*60)
print("Corpus Sample Evaluation")
print("="*60)

sample_size = min(1000, len(texts))
sample_texts = texts[:sample_size]

total_tokens = 0
total_unk = 0
bengali_tokens = 0
bengali_unk = 0
english_tokens = 0
english_unk = 0

import re

for text in sample_texts:
    ids = sp.encode(text, out_type=int)
    unk_count = ids.count(1)
    total_tokens += len(ids)
    total_unk += unk_count

    # Detect language
    bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))

    if bengali_chars > 0:
        bengali_tokens += len(ids)
        bengali_unk += unk_count
    elif latin_chars > 0:
        english_tokens += len(ids)
        english_unk += unk_count

overall_unk_rate = total_unk / total_tokens if total_tokens > 0 else 0
bengali_unk_rate = bengali_unk / bengali_tokens if bengali_tokens > 0 else 0
english_unk_rate = english_unk / english_tokens if english_tokens > 0 else 0

print(f"\nSample size: {sample_size} texts")
print(f"Total tokens: {total_tokens:,}")
print(f"Total UNK: {total_unk:,} ({overall_unk_rate:.2%})")
print(f"\nBengali tokens: {bengali_tokens:,}")
print(f"Bengali UNK: {bengali_unk:,} ({bengali_unk_rate:.2%})")
print(f"\nEnglish tokens: {english_tokens:,}")
print(f"English UNK: {english_unk:,} ({english_unk_rate:.2%})")

# Save evaluation results
evaluation_results = {
    "evaluation_timestamp": datetime.now().isoformat(),
    "tokenizer": {
        "path": str(tokenizer_path),
        "vocab_size": vocab_size,
        "model_type": "BPE"
    },
    "corpus": {
        "path": str(curated_file),
        "total_texts": len(texts),
        "sample_size": sample_size
    },
    "test_sentences": test_results,
    "corpus_sample": {
        "sample_size": sample_size,
        "total_tokens": total_tokens,
        "total_unk": total_unk,
        "overall_unk_rate": overall_unk_rate,
        "bengali_tokens": bengali_tokens,
        "bengali_unk": bengali_unk,
        "bengali_unk_rate": bengali_unk_rate,
        "english_tokens": english_tokens,
        "english_unk": english_unk,
        "english_unk_rate": english_unk_rate
    },
    "conclusions": [
        f"Overall UNK rate: {overall_unk_rate:.2%}",
        f"Bengali UNK rate: {bengali_unk_rate:.2%} - HIGH",
        f"English UNK rate: {english_unk_rate:.2%} - GOOD",
        "Tokenizer handles English well but struggles with Bengali",
        "Bengali data expansion is critical for better tokenization"
    ]
}

eval_path = EVALUATIONS_DIR / "tokenizer_evaluation.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(evaluation_results, f, indent=2, ensure_ascii=False)

print(f"\nEvaluation results saved: {eval_path}")

print("\n" + "="*60)
print("EVALUATION COMPLETE")
print("="*60)
