"""
Retrain Small Transformer with Expanded Dataset
"""

import sys
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tokenizer.tokenizer import SimpleTokenizer
from neural.transformer import SmallTransformer
from training.dataset import TextDataset, load_json_dataset
from training.pipeline import TrainingPipeline


def main():
    print("Starting model retraining with expanded dataset...")
    
    # Load expanded dataset
    print("Loading expanded dataset...")
    train_texts = load_json_dataset("data/train_final.json")
    val_texts = load_json_dataset("data/synthetic/validation.json")
    
    print(f"Training samples: {len(train_texts)}")
    print(f"Validation samples: {len(val_texts)}")
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = SimpleTokenizer()
    
    # Build vocabulary from training data
    print("Building vocabulary...")
    tokenizer.build_vocab(train_texts)
    
    # Create datasets
    print("Creating datasets...")
    train_dataset = TextDataset(train_texts, tokenizer, max_len=128)
    val_dataset = TextDataset(val_texts, tokenizer, max_len=128)
    
    # Create model
    print("Creating model...")
    model = SmallTransformer(
        vocab_size=len(tokenizer.word_to_id),
        d_model=64,
        n_heads=2,
        n_layers=2,
        max_len=128,
        dropout=0.1
    )
    
    # Training pipeline
    print("Initializing training pipeline...")
    pipeline = TrainingPipeline(
        model=model,
        tokenizer=tokenizer,
        checkpoint_dir="models/checkpoints_retrained",
        device="cpu"
    )
    
    # Train
    print("Starting training...")
    history = pipeline.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=10,
        batch_size=8,
        learning_rate=0.001,
        weight_decay=0.01,
        grad_clip=1.0,
        checkpoint_freq=1
    )
    
    print("Training completed!")
    print(f"Final training loss: {history['train_loss'][-1]:.4f}")
    print(f"Final validation loss: {history['val_loss'][-1]:.4f}")
    
    # Save final model
    print("Saving final model...")
    torch.save({
        'model_state_dict': model.state_dict(),
        'tokenizer_vocab': tokenizer.word_to_id,
        'config': {
            'vocab_size': len(tokenizer.word_to_id),
            'd_model': 64,
            'n_heads': 2,
            'n_layers': 2,
            'max_len': 128
        }
    }, 'models/checkpoints_retrained/checkpoint_final.pt')
    
    print("Model saved successfully!")


if __name__ == "__main__":
    main()
