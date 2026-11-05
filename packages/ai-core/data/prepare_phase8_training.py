"""
Phase 8 - Dataset Finalization and Experimental Transformer Training

Prepares datasets and trains a small experimental Transformer.
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import sentencepiece as spm
import time

# Fix Windows encoding for UTF-8 support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
EXPERIMENTAL_DIR = DATA_DIR / "experimental" / "phase8"

# Create experimental directory
EXPERIMENTAL_DIR.mkdir(parents=True, exist_ok=True)

print(f"Experimental directory: {EXPERIMENTAL_DIR}")
print(f"AI Core directory: {AI_CORE_DIR}")

# Verify Phase 7 artifacts
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"
CORPUS_DIR = PHASE7_DIR / "tokenizer_corpus"
TOKENIZER_MODELS_DIR = PHASE7_DIR / "tokenizer_models"

print(f"\nPhase 7 directory: {PHASE7_DIR}")
print(f"Corpus directory: {CORPUS_DIR}")
print(f"Tokenizer models directory: {TOKENIZER_MODELS_DIR}")

# Verify artifacts
corpus_files = {
    'combined': CORPUS_DIR / "corpus_combined.txt",
    'english': CORPUS_DIR / "corpus_english.txt",
    'bengali': CORPUS_DIR / "corpus_bengali.txt"
}

print("\nVerifying corpus files...")
for name, path in corpus_files.items():
    if path.exists():
        size = path.stat().st_size
        print(f"  {name}: {size / 1024:.2f} KB - OK")
    else:
        print(f"  {name}: MISSING - ERROR")

# Verify tokenizer
tokenizer_path = TOKENIZER_MODELS_DIR / "sp_8k_bpe.model"
if tokenizer_path.exists():
    print(f"\nTokenizer: {tokenizer_path.stat().st_size / 1024:.2f} KB - OK")
else:
    print(f"\nTokenizer: MISSING - ERROR")

# Load SentencePiece tokenizer
print("\nLoading SentencePiece tokenizer...")
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
print(f"Vocabulary size: {sp.get_piece_size()}")
print(f"PAD ID: {sp.pad_id()}")
print(f"UNK ID: {sp.unk_id()}")
print(f"BOS ID: {sp.bos_id()}")
print(f"EOS ID: {sp.eos_id()}")

# Test tokenizer
test_sentences = [
    "Hello, how are you?",
    "তুমি কেমন আছো?",
    "I want to build an AI."
]

print("\nTesting tokenizer...")
for sentence in test_sentences:
    ids = sp.encode(sentence, out_type=int)
    pieces = sp.encode(sentence, out_type=str)
    decoded = sp.decode(ids)
    unk_count = ids.count(sp.unk_id())
    try:
        print(f"  '{sentence}'")
    except:
        print(f"  [Bengali text]")
    print(f"    Tokens: {len(ids)}, UNK: {unk_count}")
    try:
        print(f"    Decoded: {decoded}")
    except:
        print(f"    Decoded: [contains Bengali]")

print("\n" + "="*60)
print("Phase 8A - Artifact Verification Complete")
print("="*60)
