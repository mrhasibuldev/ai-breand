"""
Phase 9 - Corpus Curation and Expansion

Curates and expands the training corpus using existing Phase 7 data
and any manually downloadable small datasets.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys
import re

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

# Create directories
CURATED_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9 - Corpus Curation and Expansion")
print("="*60)

# Load Phase 7 corpus
phase7_corpus = PHASE7_DIR / "tokenizer_corpus" / "corpus_combined.txt"

if phase7_corpus.exists():
    with open(phase7_corpus, 'r', encoding='utf-8') as f:
        phase7_texts = [line.strip() for line in f if line.strip()]
    print(f"\nLoaded Phase 7 corpus: {len(phase7_texts)} texts")
else:
    print(f"\nERROR: Phase 7 corpus not found: {phase7_corpus}")
    phase7_texts = []

# Simple language detection (Bengali Unicode range)
def detect_language(text):
    bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(text)

    if total_chars == 0:
        return 'unknown'

    bengali_ratio = bengali_chars / total_chars
    latin_ratio = latin_chars / total_chars

    if bengali_ratio > 0.3 and latin_ratio > 0.1:
        return 'mixed'
    elif bengali_ratio > 0.3:
        return 'bengali'
    elif latin_ratio > 0.3:
        return 'english'
    else:
        return 'unknown'

# Categorize texts
corpus_by_language = {
    'bengali': [],
    'english': [],
    'mixed': [],
    'unknown': []
}

print("\nCategorizing texts...")
for text in phase7_texts:
    lang = detect_language(text)
    corpus_by_language[lang].append(text)

print(f"  Bengali: {len(corpus_by_language['bengali'])}")
print(f"  English: {len(corpus_by_language['english'])}")
print(f"  Mixed: {len(corpus_by_language['mixed'])}")
print(f"  Unknown: {len(corpus_by_language['unknown'])}")

# Deduplicate within each language
print("\nDeduplicating...")
deduplicated_corpus = {}
for lang, texts in corpus_by_language.items():
    unique_texts = list(set(texts))
    removed = len(texts) - len(unique_texts)
    deduplicated_corpus[lang] = unique_texts
    print(f"  {lang}: {len(texts)} -> {len(unique_texts)} (removed {removed})")

# Combine into expanded corpus
expanded_texts = []
for lang, texts in deduplicated_corpus.items():
    expanded_texts.extend(texts)

print(f"\nTotal expanded corpus: {len(expanded_texts)} texts")

# Save curated corpus
curated_file = CURATED_DIR / "corpus_expanded.txt"
with open(curated_file, 'w', encoding='utf-8') as f:
    for text in expanded_texts:
        f.write(text + '\n')

# Calculate checksum
with open(curated_file, 'rb') as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()

file_size = curated_file.stat().st_size

# Calculate statistics
total_chars = sum(len(text) for text in expanded_texts)
total_words = sum(len(text.split()) for text in expanded_texts)

print(f"\nCurated corpus saved: {curated_file}")
print(f"  Size: {file_size / (1024*1024):.2f} MB")
print(f"  Texts: {len(expanded_texts)}")
print(f"  Words: {total_words:,}")
print(f"  Characters: {total_chars:,}")
print(f"  SHA-256: {file_hash[:16]}...")

# Language distribution statistics
lang_stats = {}
for lang, texts in deduplicated_corpus.items():
    chars = sum(len(text) for text in texts)
    words = sum(len(text.split()) for text in texts)
    lang_stats[lang] = {
        'texts': len(texts),
        'chars': chars,
        'words': words,
        'percentage': (len(texts) / len(expanded_texts)) * 100
    }

print("\nLanguage distribution:")
for lang, stats in lang_stats.items():
    print(f"  {lang}: {stats['texts']} texts ({stats['percentage']:.2f}%), {stats['words']:,} words")

# Save manifest
manifest = {
    "curation_timestamp": datetime.now().isoformat(),
    "source": "Phase 7 corpus + deduplication",
    "total_texts": len(expanded_texts),
    "total_words": total_words,
    "total_chars": total_chars,
    "file_path": str(curated_file),
    "file_size_bytes": file_size,
    "file_size_mb": round(file_size / (1024 * 1024), 2),
    "sha256": file_hash,
    "language_distribution": lang_stats,
    "preprocessing_steps": [
        "Loaded from Phase 7 corpus",
        "Language detection (Bengali Unicode range)",
        "Deduplication (exact match)",
        "UTF-8 encoding"
    ],
    "notes": [
        "No new datasets downloaded due to missing datasets library",
        "Expanded corpus based on existing Phase 7 data",
        "Bengali coverage remains critically low",
        "Recommendation: Install datasets library or manually download small Bengali datasets"
    ]
}

manifest_path = MANIFESTS_DIR / "curated_corpus_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest saved: {manifest_path}")

print("\n" + "="*60)
print("CURATION COMPLETE")
print("="*60)
