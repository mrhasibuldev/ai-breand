"""
Phase 9.2 - Comprehensive Tokenizer Evaluation

Evaluates all tokenizers against the same test sentences.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
TOKENIZERS_DIR = PHASE9_2_DIR / "tokenizers"
EVALUATIONS_DIR = PHASE9_2_DIR / "evaluations"
MANIFESTS_DIR = PHASE9_2_DIR / "manifests"

# Create directories
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.2 - Comprehensive Tokenizer Evaluation")
print("="*60)

import sentencepiece as spm

# Test sentences
test_sentences = {
    "bengali": [
        "তুমি কেমন আছো?",
        "বাংলাদেশের রাজধানী ঢাকা।",
        "আমি একটি নতুন কৃত্রিম বুদ্ধিমত্তা তৈরি করছি।",
        "বাংলা ভাষার শব্দের গঠন এবং উচ্চারণ আলাদা।",
        "আজকের আবহাওয়া খুব সুন্দর।",
        "তুমি কি আমাকে একটি পরিকল্পনা তৈরি করতে সাহায্য করতে পারবে?",
        "বাংলাদেশ স্বাধীনতা দিবস ২৬ মার্চ।",
        "পানি জীবনের জন্য অত্যন্ত গুরুত্বপূর্ণ।",
        "শিক্ষা জাতির উন্নতির চাবিক।",
        "আমি বই পড়তে ভালোবাসি।"
    ],
    "english": [
        "Hello, how are you?",
        "I want to build an advanced AI Brain.",
        "The capital of Bangladesh is Dhaka.",
        "Artificial intelligence is transforming the world.",
        "Today's weather is very beautiful.",
        "Can you help me create a study plan?",
        "Bangladesh Independence Day is March 26.",
        "Water is essential for life.",
        "Education is the key to national progress.",
        "I love reading books."
    ],
    "mixed": [
        "Hello, তুমি কেমন আছো?",
        "আমি NexusAI তৈরি করছি, an AI assistant.",
        "Explain machine learning বাংলায়।",
        "আমাকে একটি study plan তৈরি করে দাও।",
        "Today is sunny, আজকের আবহাওয়া সুন্দর।"
    ]
}

# Tokenizers to evaluate
tokenizers = {
    "baseline": {
        "name": "Phase 7 Baseline (BPE 8K)",
        "path": str(PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model")
    },
    "bpe_8k": {
        "name": "Phase 9.2 BPE 8K",
        "path": str(TOKENIZERS_DIR / "bpe_8k" / "sp_bpe_8k.model")
    },
    "bpe_4k": {
        "name": "Phase 9.2 BPE 4K",
        "path": str(TOKENIZERS_DIR / "bpe_4k" / "sp_bpe_4k.model")
    }
}

evaluation_results = {}

for tokenizer_id, tokenizer_info in tokenizers.items():
    print(f"\n{'='*60}")
    print(f"Evaluating: {tokenizer_info['name']}")
    print(f"{'='*60}")
    
    model_path = Path(tokenizer_info['path'])
    
    if not model_path.exists():
        print(f"[ERROR] Model file not found: {model_path}")
        evaluation_results[tokenizer_id] = {
            "name": tokenizer_info['name'],
            "status": "FAILED",
            "error": "Model file not found"
        }
        continue
    
    # Load tokenizer
    sp = spm.SentencePieceProcessor()
    sp.load(str(model_path))
    vocab_size = sp.get_piece_size()
    
    print(f"Vocab size: {vocab_size}")
    
    # Evaluate
    tokenizer_eval = {
        "name": tokenizer_info['name'],
        "vocab_size": vocab_size,
        "status": "SUCCESS",
        "bengali": {},
        "english": {},
        "mixed": {}
    }
    
    for lang, sentences in test_sentences.items():
        total_tokens = 0
        total_unk = 0
        total_round_trip_correct = 0
        total_words = 0
        
        for sentence in sentences:
            # Encoding
            start_encode = time.time()
            ids = sp.encode(sentence, out_type=int)
            encode_time = time.time() - start_encode
            
            # Decoding
            start_decode = time.time()
            decoded = sp.decode(ids)
            decode_time = time.time() - start_decode
            
            # Metrics
            tokens = len(ids)
            unk_count = ids.count(1)  # UNK token ID is 1
            words = len(sentence.split())
            
            total_tokens += tokens
            total_unk += unk_count
            total_words += words
            
            if decoded == sentence:
                total_round_trip_correct += 1
        
        tokenizer_eval[lang] = {
            "total_sentences": len(sentences),
            "total_tokens": total_tokens,
            "total_unk": total_unk,
            "unk_rate": total_unk / total_tokens if total_tokens > 0 else 0,
            "round_trip_correct": total_round_trip_correct,
            "round_trip_rate": total_round_trip_correct / len(sentences) if sentences else 0,
            "total_words": total_words,
            "avg_tokens_per_word": total_tokens / total_words if total_words > 0 else 0
        }
        
        print(f"\n{lang.capitalize()}:")
        print(f"  Sentences: {len(sentences)}")
        print(f"  Total tokens: {total_tokens}")
        print(f"  UNK: {total_unk} ({tokenizer_eval[lang]['unk_rate']:.2%})")
        print(f"  Round-trip correct: {total_round_trip_correct}/{len(sentences)} ({tokenizer_eval[lang]['round_trip_rate']:.2%})")
        print(f"  Avg tokens/word: {tokenizer_eval[lang]['avg_tokens_per_word']:.2f}")
    
    # Get model file size
    model_size = model_path.stat().st_size
    
    tokenizer_eval["model_size_bytes"] = model_size
    tokenizer_eval["model_size_kb"] = model_size / 1024
    
    print(f"\nModel size: {model_size / 1024:.2f} KB")
    
    evaluation_results[tokenizer_id] = tokenizer_eval

# Save evaluation results
manifest = {
    "evaluation_timestamp": datetime.now().isoformat(),
    "test_sentences": test_sentences,
    "tokenizers": tokenizers,
    "results": evaluation_results
}

eval_path = EVALUATIONS_DIR / "comprehensive_evaluation.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("EVALUATION COMPLETE")
print(f"{'='*60}")
print(f"\nResults saved: {eval_path}")

# Print comparison table
print(f"\n{'='*60}")
print("COMPARISON TABLE")
print(f"{'='*60}")
print(f"{'Tokenizer':<30} {'Bengali UNK':<15} {'English UNK':<15} {'Mixed UNK':<15} {'Model Size':<15}")
print("-" * 90)

for tokenizer_id, result in evaluation_results.items():
    if result.get('status') == 'SUCCESS':
        bengali_unk = result['bengali']['unk_rate']
        english_unk = result['english']['unk_rate']
        mixed_unk = result['mixed']['unk_rate']
        model_size = result['model_size_kb']
        
        print(f"{result['name']:<30} {bengali_unk:>14.2%} {english_unk:>14.2%} {mixed_unk:>14.2%} {model_size:>14.2f} KB")
    else:
        print(f"{result['name']:<30} {'FAILED':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15}")
