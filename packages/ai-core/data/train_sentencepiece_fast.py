"""
Phase 7 SentencePiece Tokenizer Training (Fast)

Trains only 8K BPE for quick evaluation.
"""

import sentencepiece as spm
import json
from pathlib import Path
from typing import Dict, List
import time
import os

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
EXPERIMENTAL_DIR = DATA_DIR / "experimental" / "phase7"
CORPUS_DIR = EXPERIMENTAL_DIR / "tokenizer_corpus"
TOKENIZER_MODELS_DIR = EXPERIMENTAL_DIR / "tokenizer_models"
EVALUATIONS_DIR = EXPERIMENTAL_DIR / "evaluations"

# Create directories
TOKENIZER_MODELS_DIR.mkdir(parents=True, exist_ok=True)
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)

print(f"Corpus directory: {CORPUS_DIR}")
print(f"Models directory: {TOKENIZER_MODELS_DIR}")
print(f"Evaluations directory: {EVALUATIONS_DIR}")

# Load corpus manifest
manifest_path = EXPERIMENTAL_DIR / "manifests" / "corpus_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

corpus_path = CORPUS_DIR / "corpus_combined.txt"
print(f"\nUsing corpus: {corpus_path}")
print(f"Total texts: {manifest['total_texts']:,}")
print(f"Total words: {manifest['total_words']:,}")

# Test sentences for evaluation
TEST_SENTENCES = [
    "Hello, how are you?",
    "তুমি কেমন আছো?",
    "আমি NexusAI তৈরি করছি।",
    "Hello, তুমি কেমন আছো?",
    "Explain artificial intelligence বাংলায়।",
    "Solve 25 × 4.",
    "বাংলাদেশের রাজধানী ঢাকা।",
    "I want to build an advanced AI Brain."
]

# Special tokens
SPECIAL_TOKENS = ['<PAD>', '<UNK>', '<BOS>', '<EOS>']

# Train only 8K BPE
vocab_size = 8000
model_type = 'bpe'
model_name = 'sp_8k_bpe'

model_prefix = TOKENIZER_MODELS_DIR / model_name
model_path = str(model_prefix) + ".model"

print(f"\n{'='*60}")
print(f"Training: {model_name}")
print(f"Vocab size: {vocab_size}")
print(f"Model type: {model_type}")
print(f"{'='*60}")

start_time = time.time()

# SentencePiece training arguments
user_symbols = ['<PAD>', '<BOS>', '<EOS>']  # Exclude UNK
train_args = {
    'input': str(corpus_path),
    'model_prefix': str(model_prefix),
    'vocab_size': vocab_size,
    'model_type': model_type,
    'character_coverage': 0.995,
    'input_sentence_size': 1000000,
    'shuffle_input_sentence': True,
    'normalization_rule_name': 'nmt_nfkc',
    'remove_extra_whitespaces': True,
    'pad_id': 0,
    'unk_id': 1,
    'bos_id': 2,
    'eos_id': 3,
    'pad_piece': '<PAD>',
    'unk_piece': '<UNK>',
    'bos_piece': '<BOS>',
    'eos_piece': '<EOS>',
    'user_defined_symbols': ','.join(user_symbols),
    'num_threads': 4
}

# Train
spm.SentencePieceTrainer.train(**train_args)

training_time = time.time() - start_time

# Load trained model
sp = spm.SentencePieceProcessor()
sp.load(model_path)

# Get vocabulary info
vocab_size_actual = sp.get_piece_size()
unk_id = sp.unk_id()

# Evaluate on test sentences
evaluation_results = []
unk_counts = []

for sentence in TEST_SENTENCES:
    # Encode
    ids = sp.encode(sentence, out_type=int)
    pieces = sp.encode(sentence, out_type=str)

    # Count UNK tokens
    unk_count = ids.count(unk_id)
    unk_counts.append(unk_count)

    # Decode
    decoded = sp.decode(ids)

    evaluation_results.append({
        'sentence': sentence,
        'token_count': len(ids),
        'tokens': pieces,
        'unk_count': unk_count,
        'decoded': decoded,
        'decode_matches': (decoded.strip() == sentence.strip())
    })

# Calculate statistics
total_tokens = sum(r['token_count'] for r in evaluation_results)
total_unk = sum(unk_counts)
avg_unk_rate = total_unk / total_tokens if total_tokens > 0 else 0

# Get model file size
model_file_size = os.path.getsize(model_path)

result = {
    'config': {
        'vocab_size': vocab_size,
        'model_type': model_type,
        'name': model_name
    },
    'model_path': model_path,
    'vocab_size_actual': vocab_size_actual,
    'training_time_seconds': training_time,
    'model_file_size_bytes': model_file_size,
    'evaluation': evaluation_results,
    'statistics': {
        'total_tokens': total_tokens,
        'total_unk': total_unk,
        'avg_unk_rate': avg_unk_rate,
        'max_unk_per_sentence': max(unk_counts) if unk_counts else 0
    }
}

print(f"Training complete in {training_time:.2f}s")
print(f"Actual vocab size: {vocab_size_actual}")
print(f"Model file size: {model_file_size / 1024:.2f} KB")
print(f"Average UNK rate: {avg_unk_rate:.4f}")

# Evaluate SimpleTokenizer for comparison
print("\n" + "=" * 60)
print("Evaluating SimpleTokenizer (baseline)")
print("=" * 60)
import sys
sys.path.insert(0, str(AI_CORE_DIR))

from tokenizer.tokenizer import SimpleTokenizer

tokenizer = SimpleTokenizer(vocab_size=74)
tokenizer.build_vocab(TEST_SENTENCES, min_freq=1)

simple_evaluation_results = []

for sentence in TEST_SENTENCES:
    try:
        ids = tokenizer.encode(sentence, add_special_tokens=True)
        decoded = tokenizer.decode(ids, skip_special_tokens=True)

        unk_count = ids.count(1)  # UNK token is ID 1

        simple_evaluation_results.append({
            'sentence': sentence,
            'token_count': len(ids),
            'unk_count': unk_count,
            'decoded': decoded,
            'decode_matches': (decoded.strip() == sentence.strip())
        })
    except Exception as e:
        simple_evaluation_results.append({
            'sentence': sentence,
            'error': str(e)
        })

simple_total_tokens = sum(r.get('token_count', 0) for r in simple_evaluation_results)
simple_total_unk = sum(r.get('unk_count', 0) for r in simple_evaluation_results)
simple_avg_unk_rate = simple_total_unk / simple_total_tokens if simple_total_tokens > 0 else 0

simple_result = {
    'tokenizer_type': 'SimpleTokenizer',
    'vocab_size': tokenizer.get_vocab_size(),
    'evaluation': simple_evaluation_results,
    'statistics': {
        'total_tokens': simple_total_tokens,
        'total_unk': simple_total_unk,
        'avg_unk_rate': simple_avg_unk_rate,
        'max_unk_per_sentence': max(r.get('unk_count', 0) for r in simple_evaluation_results)
    }
}

# Save results
all_results = [result, simple_result]
results_path = EVALUATIONS_DIR / "tokenizer_evaluation_results.json"
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {results_path}")

# Print summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"\n{model_name} ({model_type.upper()}, {vocab_size} tokens)")
print(f"  Vocab size: {vocab_size_actual}")
print(f"  Training time: {training_time:.2f}s")
print(f"  Model size: {model_file_size / 1024:.2f} KB")
print(f"  Avg UNK rate: {avg_unk_rate:.4f}")
print(f"  Max UNK per sentence: {max(unk_counts) if unk_counts else 0}")

print(f"\n{simple_result['tokenizer_type']}")
print(f"  Vocab size: {simple_result['vocab_size']}")
print(f"  Avg UNK rate: {simple_avg_unk_rate:.4f}")
print(f"  Max UNK per sentence: {max(r.get('unk_count', 0) for r in simple_evaluation_results)}")

print("\n" + "=" * 60)
print("Training complete!")
print("=" * 60)
