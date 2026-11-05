"""
Phase 1 Foundation Repair - Training Script

Trains MediumTransformer with Phase 9.2 BPE 8K tokenizer and Phase 10 dataset.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import json
import os
import sys
import time
from pathlib import Path
import sentencepiece as spm

# Add parent directory to path
service_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.dirname(service_dir)
sys.path.insert(0, ai_core_dir)

from neural.medium_transformer import MediumTransformer


class TextDataset(Dataset):
    """Dataset for Phase 10 text data (already tokenized)"""
    
    def __init__(self, data_items, max_len=128):
        self.data_items = data_items
        self.max_len = max_len
        
    def __len__(self):
        return len(self.data_items)
    
    def __getitem__(self, idx):
        item = self.data_items[idx]
        
        # Use pre-tokenized tokens
        token_ids = item["tokens"]
        
        # Truncate or pad
        if len(token_ids) > self.max_len:
            token_ids = token_ids[:self.max_len]
        else:
            token_ids = token_ids + [0] * (self.max_len - len(token_ids))  # 0 is PAD in SentencePiece
        
        # Shift for next-token prediction
        input_ids = torch.tensor(token_ids[:-1], dtype=torch.long)
        targets = torch.tensor(token_ids[1:], dtype=torch.long)
        
        return {"input_ids": input_ids, "targets": targets}


def load_phase10_dataset(data_dir):
    """Load Phase 10 dataset (already tokenized)"""
    train_path = os.path.join(data_dir, "train.json")
    val_path = os.path.join(data_dir, "val.json")
    test_path = os.path.join(data_dir, "test.json")
    
    with open(train_path, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    with open(val_path, 'r', encoding='utf-8') as f:
        val_data = json.load(f)
    with open(test_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    return train_data, val_data, test_data


def train_model():
    """Main training function"""
    
    # Configuration (reduced for CPU training)
    config = {
        "vocab_size": 8000,
        "d_model": 128,
        "n_layers": 2,
        "n_heads": 2,
        "d_ff": 512,
        "max_len": 128,
        "batch_size": 4,
        "epochs": 3,
        "learning_rate": 0.0003,
        "weight_decay": 0.01,
        "grad_clip": 1.0,
        "random_seed": 42,
        "device": "cpu"
    }
    
    print(f"[Phase 1 Training] Configuration: {config}")
    
    # Set random seed
    torch.manual_seed(config["random_seed"])
    
    # Paths
    ai_core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tokenizer_path = os.path.join(ai_core_dir, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
    dataset_dir = os.path.join(ai_core_dir, "data/experimental/phase10/datasets")
    checkpoint_dir = os.path.join(ai_core_dir, "models/checkpoints_medium")
    
    # Create checkpoint directory
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Load tokenizer (for reference, data already tokenized)
    print(f"[Phase 1 Training] Loading tokenizer from {tokenizer_path}")
    tokenizer = spm.SentencePieceProcessor()
    tokenizer.load(tokenizer_path)
    print(f"[Phase 1 Training] Tokenizer loaded. Vocab size: {tokenizer.get_piece_size()}")
    
    # Load dataset (already tokenized)
    print(f"[Phase 1 Training] Loading dataset from {dataset_dir}")
    train_data, val_data, test_data = load_phase10_dataset(dataset_dir)
    print(f"[Phase 1 Training] Dataset loaded: Train={len(train_data)}, Val={len(val_data)}, Test={len(test_data)}")
    
    # Create datasets
    train_dataset = TextDataset(train_data, max_len=config["max_len"])
    val_dataset = TextDataset(val_data, max_len=config["max_len"])
    test_dataset = TextDataset(test_data, max_len=config["max_len"])
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config["batch_size"], shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=config["batch_size"], shuffle=False)
    
    # Initialize model
    print(f"[Phase 1 Training] Initializing MediumTransformer")
    model = MediumTransformer(
        vocab_size=config["vocab_size"],
        d_model=config["d_model"],
        n_layers=config["n_layers"],
        n_heads=config["n_heads"],
        d_ff=config["d_ff"],
        max_len=config["max_len"]
    )
    
    model = model.to(config["device"])
    param_count = model.count_parameters()
    print(f"[Phase 1 Training] Model initialized. Parameters: {param_count:,}")
    
    # Setup optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"]
    )
    
    # Training loop
    print(f"[Phase 1 Training] Starting training for {config['epochs']} epochs")
    train_losses = []
    val_losses = []
    
    best_val_loss = float('inf')
    
    for epoch in range(config["epochs"]):
        epoch_start = time.time()
        
        # Train
        model.train()
        train_loss = 0.0
        num_batches = 0
        
        for batch in train_loader:
            input_ids = batch["input_ids"].to(config["device"])
            targets = batch["targets"].to(config["device"])
            
            optimizer.zero_grad()
            loss = model(input_ids, targets)
            loss.backward()
            
            # Gradient clipping
            if config["grad_clip"] > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), config["grad_clip"])
            
            optimizer.step()
            
            train_loss += loss.item()
            num_batches += 1
        
        train_loss = train_loss / num_batches
        train_losses.append(train_loss)
        
        # Validate
        model.eval()
        val_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(config["device"])
                targets = batch["targets"].to(config["device"])
                
                loss = model(input_ids, targets)
                val_loss += loss.item()
                num_batches += 1
        
        val_loss = val_loss / num_batches
        val_losses.append(val_loss)
        
        epoch_time = time.time() - epoch_start
        
        print(f"[Phase 1 Training] Epoch {epoch+1}/{config['epochs']} - "
              f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
              f"Time: {epoch_time:.1f}s")
        
        # Save best checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint_path = os.path.join(checkpoint_dir, "best_model.pt")
            
            checkpoint = {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "epoch": epoch,
                "val_loss": val_loss,
                "train_loss": train_loss,
                "config": config,
                "tokenizer_path": tokenizer_path,
                "vocab_size": config["vocab_size"]
            }
            
            torch.save(checkpoint, checkpoint_path)
            print(f"[Phase 1 Training] Saved best checkpoint to {checkpoint_path}")
    
    # Save final checkpoint
    final_checkpoint_path = os.path.join(checkpoint_dir, "final_model.pt")
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": config["epochs"] - 1,
        "val_loss": val_losses[-1],
        "train_loss": train_losses[-1],
        "config": config,
        "tokenizer_path": tokenizer_path,
        "vocab_size": config["vocab_size"],
        "train_losses": train_losses,
        "val_losses": val_losses
    }
    
    torch.save(checkpoint, final_checkpoint_path)
    print(f"[Phase 1 Training] Saved final checkpoint to {final_checkpoint_path}")
    
    # Test evaluation
    model.eval()
    test_loss = 0.0
    num_batches = 0
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(config["device"])
            targets = batch["targets"].to(config["device"])
            
            loss = model(input_ids, targets)
            test_loss += loss.item()
            num_batches += 1
    
    test_loss = test_loss / num_batches
    perplexity = torch.exp(torch.tensor(test_loss)).item()
    
    print(f"[Phase 1 Training] Test Loss: {test_loss:.4f}, Perplexity: {perplexity:.2f}")
    
    # Training summary
    print(f"[Phase 1 Training] Training complete")
    print(f"[Phase 1 Training] Final Train Loss: {train_losses[-1]:.4f}")
    print(f"[Phase 1 Training] Final Val Loss: {val_losses[-1]:.4f}")
    print(f"[Phase 1 Training] Test Loss: {test_loss:.4f}")
    print(f"[Phase 1 Training] Perplexity: {perplexity:.2f}")
    print(f"[Phase 1 Training] Checkpoint saved to: {final_checkpoint_path}")
    
    return {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "test_loss": test_loss,
        "perplexity": perplexity,
        "checkpoint_path": final_checkpoint_path,
        "config": config
    }


if __name__ == "__main__":
    results = train_model()
    print(f"[Phase 1 Training] Results: {results}")
