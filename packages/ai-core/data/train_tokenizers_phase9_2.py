"""
Phase 9.2 - Experimental Tokenizer Training

Trains experimental SentencePiece tokenizers with different configurations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
CORPUS_DIR = PHASE9_2_DIR / "corpus"
TOKENIZERS_DIR = PHASE9_2_DIR / "tokenizers"
MANIFESTS_DIR = PHASE9_2_DIR / "manifests"
LOGS_DIR = PHASE9_2_DIR / "logs"

# Create directories
TOKENIZERS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.2 - Experimental Tokenizer Training")
print("="*60)

import sentencepiece as spm

# Corpus file
corpus_file = CORPUS_DIR / "combined.txt"
print(f"\nCorpus: {corpus_file}")
print(f"Exists: {corpus_file.exists()}")

# Configurations to train
configs = [
    {
        "name": "bpe_8k",
        "model_type": "bpe",
        "vocab_size": 8000,
        "character_coverage": 0.9999,
        "output_dir": str(TOKENIZERS_DIR / "bpe_8k"),
        "prefix": "sp_bpe_8k"
    },
    {
        "name": "unigram_8k",
        "model_type": "unigram",
        "vocab_size": 8000,
        "character_coverage": 0.9999,
        "output_dir": str(TOKENIZERS_DIR / "unigram_8k"),
        "prefix": "sp_unigram_8k"
    },
    {
        "name": "bpe_4k",
        "model_type": "bpe",
        "vocab_size": 4000,
        "character_coverage": 0.9999,
        "output_dir": str(TOKENIZERS_DIR / "bpe_4k"),
        "prefix": "sp_bpe_4k"
    }
]

training_results = []

for config in configs:
    print(f"\n{'='*60}")
    print(f"Training: {config['name']}")
    print(f"{'='*60}")
    print(f"Model type: {config['model_type']}")
    print(f"Vocab size: {config['vocab_size']}")
    print(f"Character coverage: {config['character_coverage']}")
    
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_prefix = output_dir / config['prefix']
    
    try:
        # SentencePiece training arguments
        spm.SentencePieceTrainer.train(
            input=str(corpus_file),
            model_prefix=str(model_prefix),
            model_type=config['model_type'],
            vocab_size=config['vocab_size'],
            character_coverage=config['character_coverage'],
            user_defined_symbols=['<PAD>', '<BOS>', '<EOS>'],
            unk_id=1,
            bos_id=2,
            eos_id=3,
            pad_id=0,
            split_by_unicode_script=True,
            split_by_number=True,
            split_by_whitespace=True,
            max_sentence_length=4192,
            num_threads=4
        )
        
        # Check output files
        model_file = str(model_prefix) + ".model"
        vocab_file = str(model_prefix) + ".vocab"
        
        model_path = Path(model_file)
        vocab_path = Path(vocab_file)
        
        if model_path.exists() and vocab_path.exists():
            model_size = model_path.stat().st_size
            vocab_size = vocab_path.stat().st_size
            
            print(f"[OK] Training successful")
            print(f"  Model file: {model_file}")
            print(f"  Model size: {model_size / 1024:.2f} KB")
            print(f"  Vocab file: {vocab_file}")
            print(f"  Vocab size: {vocab_size / 1024:.2f} KB")
            
            result = {
                "name": config['name'],
                "status": "SUCCESS",
                "model_type": config['model_type'],
                "vocab_size": config['vocab_size'],
                "character_coverage": config['character_coverage'],
                "model_path": model_file,
                "vocab_path": vocab_file,
                "model_size_bytes": model_size,
                "vocab_size_bytes": vocab_size
            }
            training_results.append(result)
        else:
            print(f"[ERROR] Output files not found")
            result = {
                "name": config['name'],
                "status": "FAILED",
                "error": "Output files not found"
            }
            training_results.append(result)
            
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        result = {
            "name": config['name'],
            "status": "FAILED",
            "error": str(e)
        }
        training_results.append(result)

# Save training manifest
manifest = {
    "training_timestamp": datetime.now().isoformat(),
    "corpus": str(corpus_file),
    "configurations": configs,
    "results": training_results,
    "successful": len([r for r in training_results if r.get('status') == 'SUCCESS']),
    "failed": len([r for r in training_results if r.get('status') == 'FAILED'])
}

manifest_path = MANIFESTS_DIR / "training_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("TRAINING SUMMARY")
print(f"{'='*60}")
print(f"Total configurations: {len(configs)}")
print(f"Successful: {manifest['successful']}")
print(f"Failed: {manifest['failed']}")
print(f"\nManifest saved: {manifest_path}")

print(f"\n{'='*60}")
print("TRAINING COMPLETE")
print(f"{'='*60}")
