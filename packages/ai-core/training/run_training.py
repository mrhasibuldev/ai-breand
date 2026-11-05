"""
Real Data Training Run - Production Architecture Aligned

This script runs training using the actual collected data
from the approved dataset stored in Neon/Object Storage.
Aligned with canonical production MediumTransformer architecture.
"""

import torch
import json
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer.tokenizer import SimpleTokenizer
from neural.medium_transformer import MediumTransformer
from training.pipeline import TrainingPipeline
from training.dataset import TextDataset

def main():
    print("=== Real Data Training Run (Production Architecture) ===\n")

    # Configuration - Aligned with canonical production architecture
    ORIGINAL_DATASET_PATH = "../../../training/original_dataset.jsonl"
    CHECKPOINT_DIR = "../../../models/checkpoints/real_data_run_medium"
    EPOCHS = 2
    BATCH_SIZE = 4
    LEARNING_RATE = 0.001
    WEIGHT_DECAY = 0.01
    GRAD_CLIP = 1.0
    MAX_LEN = 512  # Production standard
    TRAIN_SPLIT = 0.8

    # Canonical production architecture configuration
    PRODUCTION_CONFIG = {
        "d_model": 256,
        "n_layers": 6,
        "n_heads": 8,
        "d_ff": 1024,
        "max_len": 512,
        "dropout": 0.1
    }

    # Check if original dataset exists
    abs_dataset_path = os.path.abspath(ORIGINAL_DATASET_PATH)
    print(f"Looking for dataset at: {abs_dataset_path}")
    if not os.path.exists(abs_dataset_path):
        print(f"ERROR: Original dataset not found at {abs_dataset_path}")
        print("This script requires the actual collected data.")
        print("Please ensure data was collected and extracted.")
        return 1

    print(f"Loading original dataset from {abs_dataset_path}...")
    try:
        with open(abs_dataset_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = [line for line in content.split('\n') if line.strip()]
        print(f"[OK] Dataset loaded: {len(lines)} documents")
    except Exception as e:
        print(f"ERROR: Failed to load dataset: {e}")
        return 1

    # Parse JSONL and extract texts
    print("\nParsing dataset...")
    texts = []
    for line in lines:
        try:
            doc = json.loads(line)
            if 'text' in doc:
                texts.append(doc['text'])
        except Exception as e:
            print(f"WARNING: Failed to parse line: {e}")

    print(f"[OK] Extracted {len(texts)} text samples")

    if len(texts) == 0:
        print("ERROR: No valid text samples found in dataset")
        return 1

    # Split into train/validation
    # Ensure at least 1 training sample if we have very few documents
    if len(texts) >= 2:
        split_index = int(len(texts) * TRAIN_SPLIT)
        train_texts = texts[:split_index]
        val_texts = texts[split_index:]
    else:
        # With only 1 document, use it for training and create empty validation
        train_texts = texts
        val_texts = []

    print(f"\nDataset split:")
    print(f"  Training samples: {len(train_texts)}")
    print(f"  Validation samples: {len(val_texts)}")

    # Initialize tokenizer
    print("\nInitializing tokenizer...")
    try:
        tokenizer = SimpleTokenizer()
        # Build vocabulary from all data
        print("Building vocabulary from collected data...")
        tokenizer.build_vocab(texts, min_freq=1)
        vocab_size = tokenizer.get_vocab_size()
        print(f"[OK] Tokenizer initialized (vocab size: {vocab_size})")
    except Exception as e:
        print(f"ERROR: Failed to initialize tokenizer: {e}")
        return 1

    # Initialize model with canonical production architecture
    print("\nInitializing MediumTransformer (canonical production architecture)...")
    try:
        model = MediumTransformer(
            vocab_size=vocab_size,
            d_model=PRODUCTION_CONFIG["d_model"],
            n_layers=PRODUCTION_CONFIG["n_layers"],
            n_heads=PRODUCTION_CONFIG["n_heads"],
            d_ff=PRODUCTION_CONFIG["d_ff"],
            max_len=PRODUCTION_CONFIG["max_len"],
            dropout=PRODUCTION_CONFIG["dropout"]
        )
        print(f"[OK] MediumTransformer initialized (parameters: {model.count_parameters()})")
        print(f"  Architecture: {PRODUCTION_CONFIG}")
    except Exception as e:
        print(f"ERROR: Failed to initialize model: {e}")
        return 1

    # Create datasets
    print("\nCreating datasets...")
    try:
        train_dataset = TextDataset(train_texts, tokenizer, max_len=MAX_LEN)
        print(f"[OK] Training dataset created: {len(train_dataset)} samples")

        if val_texts:
            val_dataset = TextDataset(val_texts, tokenizer, max_len=MAX_LEN)
            print(f"[OK] Validation dataset created: {len(val_dataset)} samples")
        else:
            # Use training data for validation when we have very few samples
            val_dataset = train_dataset
            print(f"[WARN] Using training data as validation (no separate validation set)")
    except Exception as e:
        print(f"ERROR: Failed to create datasets: {e}")
        return 1

    # Initialize training pipeline
    print("\nInitializing training pipeline...")
    try:
        abs_checkpoint_dir = os.path.abspath(CHECKPOINT_DIR)
        pipeline = TrainingPipeline(
            model=model,
            tokenizer=tokenizer,
            checkpoint_dir=abs_checkpoint_dir,
            device='cpu'
        )
        print(f"[OK] Training pipeline initialized")
        print(f"  Checkpoint directory: {abs_checkpoint_dir}")
    except Exception as e:
        print(f"ERROR: Failed to initialize training pipeline: {e}")
        return 1

    # Print dataset provenance
    print("\n=== Dataset Provenance ===")
    print(f"Source: Original collected dataset")
    print(f"File: {abs_dataset_path}")
    print(f"Document count: {len(texts)}")
    print(f"Vocabulary size: {vocab_size}")
    print(f"Tokenizer built from: Actual collected data")
    print(f"Model architecture: MediumTransformer (canonical production)")
    print()

    # Prepare tokenizer vocabulary for checkpoint (for reproducibility)
    tokenizer_vocab = {
        "word_to_id": tokenizer.word_to_id,
        "id_to_word": tokenizer.id_to_word,
        "vocab_size": vocab_size,
        "special_tokens": {
            "PAD": tokenizer.PAD_TOKEN,
            "UNK": tokenizer.UNK_TOKEN,
            "BOS": tokenizer.BOS_TOKEN,
            "EOS": tokenizer.EOS_TOKEN
        }
    }

    # Run training
    print(f"=== Starting Training ===")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Weight decay: {WEIGHT_DECAY}")
    print(f"Gradient clip: {GRAD_CLIP}")
    print(f"Device: cpu")
    print(f"Max sequence length: {MAX_LEN}")
    print()

    try:
        # Use custom checkpoint saving with tokenizer vocab
        metrics = pipeline.train(
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            learning_rate=LEARNING_RATE,
            weight_decay=WEIGHT_DECAY,
            grad_clip=GRAD_CLIP,
            checkpoint_freq=1
        )

        print("\n=== Training Completed Successfully ===")
        print(f"Final train loss: {metrics['final_train_loss']:.4f}")
        print(f"Final val loss: {metrics['final_val_loss']:.4f}")
        print(f"Checkpoint saved to: {abs_checkpoint_dir}")

        # Save training summary with full provenance
        summary = {
            "status": "completed",
            "data_source": "real_collected_data",
            "original_dataset": abs_dataset_path,
            "epochs": EPOCHS,
            "batch_size": BATCH_SIZE,
            "learning_rate": LEARNING_RATE,
            "weight_decay": WEIGHT_DECAY,
            "grad_clip": GRAD_CLIP,
            "max_len": MAX_LEN,
            "train_samples": len(train_dataset),
            "val_samples": len(val_dataset),
            "total_documents": len(texts),
            "final_train_loss": metrics['final_train_loss'],
            "final_val_loss": metrics['final_val_loss'],
            "train_losses": metrics['train_losses'],
            "val_losses": metrics['val_losses'],
            "model_parameters": model.count_parameters(),
            "vocab_size": vocab_size,
            "checkpoint_dir": abs_checkpoint_dir,
            "trained_on_real_data": True,
            "model_architecture": "MediumTransformer",
            "architecture_config": PRODUCTION_CONFIG,
            "tokenizer_type": "SimpleTokenizer",
            "tokenizer_vocab_saved": True,
            "software_version": "1.0.0"
        }

        summary_path = os.path.join(abs_checkpoint_dir, "training_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"Training summary saved to: {summary_path}")

        # Save tokenizer separately for easy loading
        tokenizer_path = os.path.join(abs_checkpoint_dir, "tokenizer.json")
        tokenizer.save(tokenizer_path)
        print(f"Tokenizer saved to: {tokenizer_path}")

        return 0

    except Exception as e:
        print(f"\nERROR: Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
