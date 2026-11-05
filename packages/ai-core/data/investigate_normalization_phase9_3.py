"""
Phase 9.3 - Investigate Normalization Effect

Tests round-trip with and without NFC normalization.
"""

import json
import sys
import unicodedata
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
PHASE9_3_DIR = DATA_DIR / "experimental" / "phase9_3"
EVALUATIONS_DIR = PHASE9_3_DIR / "evaluations"

print("="*60)
print("Phase 9.3 - Investigate Normalization Effect")
print("="*60)

import sentencepiece as spm

# Load Phase 9.2 test sentences
phase9_2_eval = PHASE9_2_DIR / "evaluations" / "comprehensive_evaluation.json"
with open(phase9_2_eval, 'r', encoding='utf-8') as f:
    phase9_2_data = json.load(f)

test_sentences = phase9_2_data['test_sentences']['bengali']

# Load Phase 9.2 BPE 8K tokenizer
tokenizer_path = PHASE9_2_DIR / "tokenizers" / "bpe_8k" / "sp_bpe_8k.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))

print(f"\nTesting Bengali sentences with and without NFC normalization\n")

results = []

for i, sentence in enumerate(test_sentences):
    # Test WITHOUT normalization (original Phase 9.2 method)
    ids_no_norm = sp.encode(sentence, out_type=int)
    decoded_no_norm = sp.decode(ids_no_norm)
    match_no_norm = (sentence == decoded_no_norm)
    
    # Test WITH normalization
    normalized = unicodedata.normalize('NFC', sentence)
    ids_norm = sp.encode(normalized, out_type=int)
    decoded_norm = sp.decode(ids_norm)
    match_norm = (normalized == decoded_norm)
    
    result = {
        "index": i,
        "original": sentence,
        "normalized": normalized,
        "without_normalization": {
            "decoded": decoded_no_norm,
            "match": match_no_norm
        },
        "with_normalization": {
            "decoded": decoded_norm,
            "match": match_norm
        },
        "normalization_needed": (not match_no_norm and match_norm)
    }
    
    results.append(result)
    
    print(f"Sentence {i+1}:")
    print(f"  Without NFC: {'OK' if match_no_norm else 'FAIL'}")
    print(f"  With NFC: {'OK' if match_norm else 'FAIL'}")
    if not match_no_norm and match_norm:
        print(f"  -> Normalization fixes the issue")
    print()

# Summary
no_norm_correct = sum(1 for r in results if r['without_normalization']['match'])
norm_correct = sum(1 for r in results if r['with_normalization']['match'])
normalization_needed = sum(1 for r in results if r['normalization_needed'])

print("="*60)
print("SUMMARY")
print("="*60)
print(f"Without NFC normalization: {no_norm_correct}/10 ({no_norm_correct/10:.0%})")
print(f"With NFC normalization: {norm_correct}/10 ({norm_correct/10:.0%})")
print(f"Sentences needing normalization: {normalization_needed}/10")

# Save results
results_path = EVALUATIONS_DIR / "normalization_investigation.json"
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResults saved: {results_path}")
