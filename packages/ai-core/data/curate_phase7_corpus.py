"""
Phase 7 Dataset Curation for SentencePiece Tokenizer Training

Collects, cleans, and prepares a Bengali-English corpus for tokenizer training.
"""

import json
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Set
from collections import Counter
import re

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
EXPERIMENTAL_DIR = DATA_DIR / "experimental" / "phase7"

# Create directories
RAW_DIR = EXPERIMENTAL_DIR / "raw"
CURATED_DIR = EXPERIMENTAL_DIR / "curated"
CORPUS_DIR = EXPERIMENTAL_DIR / "tokenizer_corpus"
MANIFESTS_DIR = EXPERIMENTAL_DIR / "manifests"

for dir_path in [RAW_DIR, CURATED_DIR, CORPUS_DIR, MANIFESTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

print(f"Working directory: {AI_CORE_DIR}")
print(f"Experimental directory: {EXPERIMENTAL_DIR}")


def detect_language(text: str) -> str:
    """
    Detect language using Unicode ranges.
    Returns: 'bengali', 'english', 'mixed', or 'unknown'
    """
    if not text:
        return 'unknown'

    bengali_count = 0
    latin_count = 0

    for char in text:
        code = ord(char)
        if 0x0980 <= code <= 0x09FF:
            bengali_count += 1
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
            latin_count += 1

    if bengali_count > 0 and latin_count > 0:
        return 'mixed'
    elif bengali_count > 0:
        return 'bengali'
    elif latin_count > 0:
        return 'english'
    else:
        return 'unknown'


def normalize_unicode(text: str) -> str:
    """Normalize Unicode text"""
    import unicodedata
    return unicodedata.normalize('NFC', text)


def is_valid_text(text: str) -> bool:
    """Check if text is valid and not empty/garbage"""
    if not text or not text.strip():
        return False
    if len(text.strip()) < 2:
        return False
    # Check for excessive repeated characters
    if len(set(text.strip())) < 3 and len(text.strip()) > 10:
        return False
    return True


def load_jsonl(filepath: Path) -> List[Dict]:
    """Load JSONL file"""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def load_json(filepath: Path) -> List:
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_text_from_record(record: Dict) -> List[str]:
    """Extract text fields from a record"""
    texts = []

    # Common field names
    text_fields = ['text', 'content', 'instruction', 'input', 'output', 'response', 'question', 'answer', 'message']

    for field in text_fields:
        if field in record and isinstance(record[field], str):
            texts.append(record[field])

    # Handle structured instruction datasets
    if 'instruction' in record and 'output' in record:
        texts.append(record['instruction'])
        texts.append(record['output'])

    if 'question' in record and 'answer' in record:
        texts.append(record['question'])
        texts.append(record['answer'])

    return texts


def collect_datasets() -> Dict[str, List[str]]:
    """Collect all available datasets"""
    corpus = {
        'bengali': [],
        'english': [],
        'mixed': [],
        'unknown': []
    }

    dataset_stats = []

    # 1. Production training data (19 samples)
    try:
        train_cleaned_path = DATA_DIR / "public_datasets" / "v1.0_cleaned" / "train_cleaned.json"
        if train_cleaned_path.exists():
            data = load_json(train_cleaned_path)
            for text in data:
                if is_valid_text(text):
                    text = normalize_unicode(text)
                    lang = detect_language(text)
                    corpus[lang].append(text)
            dataset_stats.append({
                'name': 'production_train_cleaned',
                'records': len(data),
                'type': 'JSON',
                'license': 'UNKNOWN'
            })
            print(f"Loaded production training data: {len(data)} records")
    except Exception as e:
        print(f"Error loading production data: {e}")

    # 2. Bengali-English mixed dataset
    try:
        mixed_path = DATA_DIR / "public_datasets" / "bengali_english_mixed.json"
        if mixed_path.exists():
            data = load_json(mixed_path)
            for text in data:
                if is_valid_text(text):
                    text = normalize_unicode(text)
                    lang = detect_language(text)
                    corpus[lang].append(text)
            dataset_stats.append({
                'name': 'bengali_english_mixed',
                'records': len(data),
                'type': 'JSON',
                'license': 'UNKNOWN'
            })
            print(f"Loaded Bengali-English mixed: {len(data)} records")
    except Exception as e:
        print(f"Error loading mixed dataset: {e}")

    # 3. GSM8K (English mathematical reasoning)
    try:
        gsm8k_train_path = DATA_DIR / "collected" / "raw" / "gsm8k" / "gsm8k_train.jsonl"
        gsm8k_test_path = DATA_DIR / "collected" / "raw" / "gsm8k" / "gsm8k_test.jsonl"

        for path in [gsm8k_train_path, gsm8k_test_path]:
            if path.exists():
                records = load_jsonl(path)
                for record in records:
                    texts = extract_text_from_record(record)
                    for text in texts:
                        if is_valid_text(text):
                            text = normalize_unicode(text)
                            lang = detect_language(text)
                            corpus[lang].append(text)
                dataset_stats.append({
                    'name': f'gsm8k_{path.stem}',
                    'records': len(records),
                    'type': 'JSONL',
                    'license': 'MIT'
                })
                print(f"Loaded {path.stem}: {len(records)} records")
    except Exception as e:
        print(f"Error loading GSM8K: {e}")

    # 4. Dolly (English instruction following)
    try:
        dolly_path = DATA_DIR / "collected" / "raw" / "dolly" / "dolly-15k.jsonl"
        if dolly_path.exists():
            records = load_jsonl(dolly_path)
            for record in records:
                texts = extract_text_from_record(record)
                for text in texts:
                    if is_valid_text(text):
                        text = normalize_unicode(text)
                        lang = detect_language(text)
                        corpus[lang].append(text)
            dataset_stats.append({
                'name': 'dolly_15k',
                'records': len(records),
                'type': 'JSONL',
                'license': 'CC_BY_SA_3.0'
            })
            print(f"Loaded Dolly: {len(records)} records")
    except Exception as e:
        print(f"Error loading Dolly: {e}")

    # 5. Wikipedia (Bengali and English)
    try:
        wiki_bn_dir = DATA_DIR / "collected" / "wikipedia" / "bn"
        wiki_en_dir = DATA_DIR / "collected" / "wikipedia" / "en"

        for wiki_dir, lang in [(wiki_bn_dir, 'bengali'), (wiki_en_dir, 'english')]:
            if wiki_dir.exists():
                for json_file in wiki_dir.glob("*.json"):
                    data = load_json(json_file)
                    if isinstance(data, dict) and 'text' in data:
                        text = data['text']
                    elif isinstance(data, list):
                        text = ' '.join(data)
                    else:
                        text = str(data)

                    if is_valid_text(text):
                        text = normalize_unicode(text)
                        corpus[lang].append(text)

                dataset_stats.append({
                    'name': f'wikipedia_{lang}',
                    'records': len(list(wiki_dir.glob("*.json"))),
                    'type': 'JSON',
                    'license': 'CC_BY_SA_3.0'
                })
                print(f"Loaded Wikipedia {lang}: {len(list(wiki_dir.glob('*.json')))} articles")
    except Exception as e:
        print(f"Error loading Wikipedia: {e}")

    # 6. Conversational data
    try:
        conv_path = DATA_DIR / "conversational_data.json"
        if conv_path.exists():
            data = load_json(conv_path)
            for item in data:
                if isinstance(item, dict):
                    texts = extract_text_from_record(item)
                else:
                    texts = [str(item)]

                for text in texts:
                    if is_valid_text(text):
                        text = normalize_unicode(text)
                        lang = detect_language(text)
                        corpus[lang].append(text)
            dataset_stats.append({
                'name': 'conversational_data',
                'records': len(data),
                'type': 'JSON',
                'license': 'UNKNOWN'
            })
            print(f"Loaded conversational data: {len(data)} records")
    except Exception as e:
        print(f"Error loading conversational data: {e}")

    return corpus, dataset_stats


def deduplicate_texts(texts: List[str]) -> List[str]:
    """Remove exact duplicates"""
    seen = set()
    unique_texts = []
    for text in texts:
        # Use normalized hash for comparison
        normalized = ' '.join(text.lower().split())
        if normalized not in seen:
            seen.add(normalized)
            unique_texts.append(text)
    return unique_texts


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA-256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def save_corpus(corpus: Dict[str, List[str]], dataset_stats: List[Dict]):
    """Save corpus and manifest"""
    # Deduplicate each language
    print("\nDeduplicating texts...")
    for lang in corpus:
        original_count = len(corpus[lang])
        corpus[lang] = deduplicate_texts(corpus[lang])
        removed = original_count - len(corpus[lang])
        print(f"{lang}: {original_count} -> {len(corpus[lang])} (removed {removed} duplicates)")

    # Save separate language files
    corpus_files = {}
    for lang, texts in corpus.items():
        if texts:
            filepath = CORPUS_DIR / f"corpus_{lang}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                for text in texts:
                    f.write(text + '\n')
            corpus_files[lang] = {
                'path': str(filepath),
                'records': len(texts),
                'sha256': calculate_sha256(filepath)
            }
            print(f"Saved {lang} corpus: {len(texts)} texts")

    # Save combined corpus
    all_texts = []
    for lang, texts in corpus.items():
        all_texts.extend(texts)

    combined_path = CORPUS_DIR / "corpus_combined.txt"
    with open(combined_path, 'w', encoding='utf-8') as f:
        for text in all_texts:
            f.write(text + '\n')

    corpus_files['combined'] = {
        'path': str(combined_path),
        'records': len(all_texts),
        'sha256': calculate_sha256(combined_path)
    }
    print(f"Saved combined corpus: {len(all_texts)} texts")

    # Calculate statistics
    total_chars = sum(len(text) for text in all_texts)
    total_words = sum(len(text.split()) for text in all_texts)

    language_distribution = {lang: len(texts) for lang, texts in corpus.items()}

    # Save manifest
    manifest = {
        'curated_timestamp': '2026-11-03',
        'corpus_files': corpus_files,
        'language_distribution': language_distribution,
        'total_texts': len(all_texts),
        'total_words': total_words,
        'total_chars': total_chars,
        'source_datasets': dataset_stats,
        'preprocessing_steps': [
            'Unicode normalization (NFC)',
            'Empty record removal',
            'Duplicate removal (exact)',
            'Language detection'
        ]
    }

    manifest_path = MANIFESTS_DIR / "corpus_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nSaved manifest: {manifest_path}")
    print(f"\nCorpus Statistics:")
    print(f"  Total texts: {len(all_texts):,}")
    print(f"  Total words: {total_words:,}")
    print(f"  Total chars: {total_chars:,}")
    print(f"  Language distribution:")
    for lang, count in language_distribution.items():
        percentage = (count / len(all_texts)) * 100 if all_texts else 0
        print(f"    {lang}: {count:,} ({percentage:.2f}%)")


def main():
    print("=" * 60)
    print("Phase 7 Dataset Curation for SentencePiece Tokenizer")
    print("=" * 60)

    # Collect datasets
    print("\nCollecting datasets...")
    corpus, dataset_stats = collect_datasets()

    # Save corpus
    print("\nSaving corpus...")
    save_corpus(corpus, dataset_stats)

    print("\n" + "=" * 60)
    print("Dataset curation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
