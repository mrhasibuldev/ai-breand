"""
Phase 9.3 - Reproduce Original Evaluation

Reproduces the Phase 9.2 evaluation and identifies which Bengali sentences failed round-trip.
"""

import json
import sys
import unicodedata
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
PHASE9_3_DIR = DATA_DIR / "experimental" / "phase9_3"
EVALUATIONS_DIR = PHASE9_3_DIR / "evaluations"
MANIFESTS_DIR = PHASE9_3_DIR / "manifests"

# Create directories
PHASE9_3_DIR.mkdir(parents=True, exist_ok=True)
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.3 - Reproduce Original Evaluation")
print("="*60)

import sentencepiece as spm

# Load Phase 9.2 test sentences
phase9_2_eval = PHASE9_2_DIR / "evaluations" / "comprehensive_evaluation.json"
with open(phase9_2_eval, 'r', encoding='utf-8') as f:
    phase9_2_data = json.load(f)

test_sentences = phase9_2_data['test_sentences']

print(f"\nLoaded test sentences:")
print(f"  Bengali: {len(test_sentences['bengali'])}")
print(f"  English: {len(test_sentences['english'])}")
print(f"  Mixed: {len(test_sentences['mixed'])}")

# Load Phase 9.2 BPE 8K tokenizer
tokenizer_path = PHASE9_2_DIR / "tokenizers" / "bpe_8k" / "sp_bpe_8k.model"
print(f"\nTokenizer: {tokenizer_path}")
print(f"Exists: {tokenizer_path.exists()}")

sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()
print(f"Vocab size: {vocab_size}")

# Evaluate with detailed tracking
detailed_results = {
    "bengali": [],
    "english": [],
    "mixed": []
}

for lang, sentences in test_sentences.items():
    print(f"\n{'='*60}")
    print(f"Evaluating {lang}")
    print(f"{'='*60}")
    
    for i, sentence in enumerate(sentences):
        # Normalize with NFC (same as Phase 9.2 corpus preparation)
        normalized = unicodedata.normalize('NFC', sentence)
        
        # Encode
        ids = sp.encode(normalized, out_type=int)
        pieces = [sp.id_to_piece(id) for id in ids]
        unk_count = ids.count(1)
        
        # Decode
        decoded = sp.decode(ids)
        
        # Compare
        exact_match = (normalized == decoded)
        
        result = {
            "index": i,
            "original": sentence,
            "normalized": normalized,
            "tokens": len(ids),
            "pieces": pieces,
            "unk_count": unk_count,
            "decoded": decoded,
            "exact_match": exact_match,
            "difference": None
        }
        
        if not exact_match:
            # Calculate character-level difference
            result['difference'] = {
                "length_original": len(normalized),
                "length_decoded": len(decoded),
                "diff": decoded if decoded != normalized else None
            }
        
        detailed_results[lang].append(result)
        
        status = "[OK]" if exact_match else "[FAIL]"
        print(f"\n{status} Sentence {i+1}:")
        print(f"  Length: {len(sentence)} chars")
        print(f"  Tokens: {len(ids)}, UNK: {unk_count}")
        if not exact_match:
            print(f"  Decoded length: {len(decoded)} chars")
            print(f"  Normalized length: {len(normalized)} chars")

# Calculate statistics
for lang in detailed_results:
    total = len(detailed_results[lang])
    correct = sum(1 for r in detailed_results[lang] if r['exact_match'])
    failed = total - correct
    
    print(f"\n{lang.capitalize()} Statistics:")
    print(f"  Total: {total}")
    print(f"  Correct: {correct}")
    print(f"  Failed: {failed}")
    print(f"  Round-trip rate: {correct/total:.2%}")

# Save detailed results
results_path = EVALUATIONS_DIR / "reproduction_results.json"
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(detailed_results, f, indent=2, ensure_ascii=False)

print(f"\nDetailed results saved: {results_path}")

# Print failed Bengali sentences
print(f"\n{'='*60}")
print("FAILED BENGALI SENTENCES")
print(f"{'='*60}")
failed_bengali = [r for r in detailed_results['bengali'] if not r['exact_match']]
for result in failed_bengali:
    print(f"\nSentence {result['index']+1}:")
    print(f"  Original length: {len(result['original'])} chars")
    print(f"  Normalized length: {len(result['normalized'])} chars")
    print(f"  Decoded length: {len(result['decoded'])} chars")
    print(f"  Difference: {result['difference']}")

print(f"\n{'='*60}")
print("REPRODUCTION COMPLETE")
print(f"{'='*60}")
