"""
Phase 9.3 - Comprehensive Final Evaluation

Evaluates all tokenizers with NFC normalization on expanded test suite.
"""

import json
import sys
import unicodedata
import time
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
PHASE9_3_DIR = DATA_DIR / "experimental" / "phase9_3"
TESTS_DIR = PHASE9_3_DIR / "tests"
EVALUATIONS_DIR = PHASE9_3_DIR / "evaluations"
MANIFESTS_DIR = PHASE9_3_DIR / "manifests"

print("="*60)
print("Phase 9.3 - Comprehensive Final Evaluation")
print("="*60)

import sentencepiece as spm

# Load expanded test suite
test_suite_path = TESTS_DIR / "expanded_test_suite.json"
with open(test_suite_path, 'r', encoding='utf-8') as f:
    test_suite = json.load(f)

print(f"\nLoaded test suite:")
print(f"  Bengali: {len(test_suite['bengali_tests'])}")
print(f"  English: {len(test_suite['english_tests'])}")
print(f"  Mixed: {len(test_suite['mixed_tests'])}")

# Tokenizers to evaluate
tokenizers = {
    "baseline": {
        "name": "Phase 7 Baseline (BPE 8K)",
        "path": str(PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model")
    },
    "bpe_8k": {
        "name": "Phase 9.2 BPE 8K",
        "path": str(PHASE9_2_DIR / "tokenizers" / "bpe_8k" / "sp_bpe_8k.model")
    },
    "bpe_4k": {
        "name": "Phase 9.2 BPE 4K",
        "path": str(PHASE9_2_DIR / "tokenizers" / "bpe_4k" / "sp_bpe_4k.model")
    }
}

all_results = {}

for tokenizer_id, tokenizer_info in tokenizers.items():
    print(f"\n{'='*60}")
    print(f"Evaluating: {tokenizer_info['name']}")
    print(f"{'='*60}")
    
    model_path = Path(tokenizer_info['path'])
    
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        all_results[tokenizer_id] = {
            "name": tokenizer_info['name'],
            "status": "FAILED",
            "error": "Model file not found"
        }
        continue
    
    # Load tokenizer
    sp = spm.SentencePieceProcessor()
    sp.load(str(model_path))
    vocab_size = sp.get_piece_size()
    model_size = model_path.stat().st_size
    
    print(f"Vocab size: {vocab_size}")
    print(f"Model size: {model_size / 1024:.2f} KB")
    
    # Evaluate
    tokenizer_result = {
        "name": tokenizer_info['name'],
        "vocab_size": vocab_size,
        "model_size_bytes": model_size,
        "status": "SUCCESS",
        "bengali": {},
        "english": {},
        "mixed": {}
    }
    
    for lang in ['bengali', 'english', 'mixed']:
        sentences = test_suite[f'{lang}_tests']
        
        total_tokens = 0
        total_unk = 0
        total_round_trip_correct = 0
        total_words = 0
        total_encode_time = 0
        total_decode_time = 0
        
        for sentence in sentences:
            # Normalize with NFC
            normalized = unicodedata.normalize('NFC', sentence)
            
            # Encoding
            start_encode = time.time()
            ids = sp.encode(normalized, out_type=int)
            encode_time = time.time() - start_encode
            
            # Decoding
            start_decode = time.time()
            decoded = sp.decode(ids)
            decode_time = time.time() - start_decode
            
            # Metrics
            tokens = len(ids)
            unk_count = ids.count(1)
            words = len(sentence.split())
            
            total_tokens += tokens
            total_unk += unk_count
            total_words += words
            total_encode_time += encode_time
            total_decode_time += decode_time
            
            if decoded == normalized:
                total_round_trip_correct += 1
        
        tokenizer_result[lang] = {
            "total_sentences": len(sentences),
            "total_tokens": total_tokens,
            "total_unk": total_unk,
            "unk_rate": total_unk / total_tokens if total_tokens > 0 else 0,
            "round_trip_correct": total_round_trip_correct,
            "round_trip_rate": total_round_trip_correct / len(sentences) if sentences else 0,
            "total_words": total_words,
            "avg_tokens_per_word": total_tokens / total_words if total_words > 0 else 0,
            "avg_encode_time": total_encode_time / len(sentences) if sentences else 0,
            "avg_decode_time": total_decode_time / len(sentences) if sentences else 0
        }
        
        print(f"\n{lang.capitalize()}:")
        print(f"  Sentences: {len(sentences)}")
        print(f"  Total tokens: {total_tokens}")
        print(f"  UNK: {total_unk} ({tokenizer_result[lang]['unk_rate']:.2%})")
        print(f"  Round-trip: {total_round_trip_correct}/{len(sentences)} ({tokenizer_result[lang]['round_trip_rate']:.2%})")
        print(f"  Avg tokens/word: {tokenizer_result[lang]['avg_tokens_per_word']:.2f}")
    
    all_results[tokenizer_id] = tokenizer_result

# Save comprehensive results
manifest = {
    "evaluation_timestamp": datetime.now().isoformat(),
    "normalization": "NFC",
    "test_suite_size": {
        "bengali": len(test_suite['bengali_tests']),
        "english": len(test_suite['english_tests']),
        "mixed": len(test_suite['mixed_tests'])
    },
    "tokenizers": tokenizers,
    "results": all_results
}

eval_path = EVALUATIONS_DIR / "final_comprehensive_evaluation.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("EVALUATION COMPLETE")
print(f"{'='*60}")
print(f"\nResults saved: {eval_path}")

# Print comparison table
print(f"\n{'='*60}")
print("COMPARISON TABLE (Expanded Test Suite)")
print(f"{'='*60}")
print(f"{'Tokenizer':<30} {'Bengali UNK':<15} {'English UNK':<15} {'Mixed UNK':<15} {'Bengali RT':<15}")
print("-" * 90)

for tokenizer_id, result in all_results.items():
    if result.get('status') == 'SUCCESS':
        bengali_unk = result['bengali']['unk_rate']
        english_unk = result['english']['unk_rate']
        mixed_unk = result['mixed']['unk_rate']
        bengali_rt = result['bengali']['round_trip_rate']
        
        print(f"{result['name']:<30} {bengali_unk:>14.2%} {english_unk:>14.2%} {mixed_unk:>14.2%} {bengali_rt:>14.2%}")
    else:
        print(f"{result['name']:<30} {'FAILED':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15}")

print(f"\n{'='*60}")
print("ROUND-TRIP ACCURACY TABLE")
print(f"{'='*60}")
print(f"{'Tokenizer':<30} {'Bengali RT':<15} {'English RT':<15} {'Mixed RT':<15}")
print("-" * 75)

for tokenizer_id, result in all_results.items():
    if result.get('status') == 'SUCCESS':
        bengali_rt = result['bengali']['round_trip_rate']
        english_rt = result['english']['round_trip_rate']
        mixed_rt = result['mixed']['round_trip_rate']
        
        print(f"{result['name']:<30} {bengali_rt:>14.2%} {english_rt:>14.2%} {mixed_rt:>14.2%}")
