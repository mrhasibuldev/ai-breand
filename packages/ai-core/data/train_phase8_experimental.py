"""
Phase 8 - Experimental Transformer Training

Trains a small CPU-optimized Transformer for experimental purposes.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import List
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import sentencepiece as spm

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
EXPERIMENTAL_DIR = DATA_DIR / "experimental" / "phase8"
PHASE7_DIR = DATA_DIR / "experimental" / "phase7"

print("="*60)
print("Phase 8 - Experimental Transformer Training")
print("="*60)

# Load manifest
manifest_path = EXPERIMENTAL_DIR / "manifests" / "dataset_manifest.json"
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

print(f"\nDataset: {manifest['train_size']} train, {manifest['val_size']} val")
print(f"Vocabulary size: {manifest['vocab_size']}")

# Load tokenizer
tokenizer_path = PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()
unk_id = sp.unk_id()

print(f"Tokenizer loaded: {vocab_size} tokens")

# Dataset class
class TextDataset(Dataset):
    def __init__(self, filepath, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.lines = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(self.lines)} lines from {filepath}")
    
    def __len__(self):
        return len(self.lines)
    
    def __getitem__(self, idx):
        text = self.lines[idx]
        
        # Encode without special tokens (they're not properly configured)
        ids = self.tokenizer.encode(text, out_type=int)
        
        # Truncate or pad to max_length
        if len(ids) > self.max_length:
            ids = ids[:self.max_length]
        
        # Pad
        while len(ids) < self.max_length:
            ids.append(0)  # Use 0 as padding
        
        # Create input and target (shifted by 1)
        input_ids = torch.tensor(ids[:-1], dtype=torch.long)
        target_ids = torch.tensor(ids[1:], dtype=torch.long)
        
        return input_ids, target_ids

# Load datasets
train_path = EXPERIMENTAL_DIR / "data" / "train.txt"
val_path = EXPERIMENTAL_DIR / "data" / "val.txt"

print("\nLoading datasets...")
train_dataset = TextDataset(train_path, sp, max_length=128)
val_dataset = TextDataset(val_path, sp, max_length=128)

# Create dataloaders (small batch size for CPU)
batch_size = 16
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

print(f"Batch size: {batch_size}")
print(f"Train batches: {len(train_loader)}")
print(f"Val batches: {len(val_loader)}")

# Import existing SmallTransformer
sys.path.insert(0, str(AI_CORE_DIR))
from neural.small_transformer import SmallTransformer

# Create model
print("\nCreating model...")
model = SmallTransformer(
    vocab_size=vocab_size,
    d_model=128,
    n_layers=2,  # Reduced from 4 to save memory
    n_heads=4,
    d_ff=512,
    max_len=128,
    dropout=0.1
)

param_count = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {param_count:,}")

# Since SentencePiece special tokens are -1, we won't use them for now
# We'll just use the tokens as-is without BOS/EOS for simplicity

# Device
device = torch.device('cpu')
model = model.to(device)
print(f"Device: {device}")

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding (0)

# Training
print("\n" + "="*60)
print("Starting Training")
print("="*60)

num_epochs = 5
train_losses = []
val_losses = []

for epoch in range(num_epochs):
    model.train()
    epoch_loss = 0.0
    start_time = time.time()
    
    for batch_idx, (input_ids, target_ids) in enumerate(train_loader):
        input_ids = input_ids.to(device)
        target_ids = target_ids.to(device)
        
        optimizer.zero_grad()
        
        # Forward pass
        logits = model(input_ids)
        
        # Reshape for loss calculation
        logits = logits.view(-1, vocab_size)
        target_ids = target_ids.view(-1)
        
        # Calculate loss
        loss = criterion(logits, target_ids)
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        # Optimizer step
        optimizer.step()
        
        epoch_loss += loss.item()
        
        if batch_idx % 50 == 0:
            print(f"  Epoch {epoch+1}/{num_epochs}, Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}")
    
    avg_train_loss = epoch_loss / len(train_loader)
    train_losses.append(avg_train_loss)
    
    # Validation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for input_ids, target_ids in val_loader:
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)
            
            logits = model(input_ids)
            logits = logits.view(-1, vocab_size)
            target_ids = target_ids.view(-1)
            
            loss = criterion(logits, target_ids)
            val_loss += loss.item()
    
    avg_val_loss = val_loss / len(val_loader)
    val_losses.append(avg_val_loss)
    
    epoch_time = time.time() - start_time
    
    print(f"\nEpoch {epoch+1}/{num_epochs} Summary:")
    print(f"  Train Loss: {avg_train_loss:.4f}")
    print(f"  Val Loss: {avg_val_loss:.4f}")
    print(f"  Time: {epoch_time:.2f}s")
    
    # Save checkpoint
    checkpoint_path = EXPERIMENTAL_DIR / "checkpoints" / f"checkpoint_epoch_{epoch+1}.pt"
    torch.save({
        'epoch': epoch + 1,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'train_loss': avg_train_loss,
        'val_loss': avg_val_loss,
        'vocab_size': vocab_size,
        'config': {
            'd_model': 128,
            'n_layers': 2,
            'n_heads': 4,
            'd_ff': 512,
            'max_len': 128
        }
    }, checkpoint_path)
    print(f"  Checkpoint saved: {checkpoint_path.name}")

# Save final model
final_checkpoint_path = EXPERIMENTAL_DIR / "checkpoints" / "final_model.pt"
torch.save({
    'model_state_dict': model.state_dict(),
    'vocab_size': vocab_size,
    'config': {
        'd_model': 128,
        'n_layers': 2,
        'n_heads': 4,
        'd_ff': 512,
        'max_len': 128
    },
    'train_losses': train_losses,
    'val_losses': val_losses
}, final_checkpoint_path)

print(f"\nFinal model saved: {final_checkpoint_path}")
print(f"Final train loss: {train_losses[-1]:.4f}")
print(f"Final val loss: {val_losses[-1]:.4f}")

# Save training log
training_log = {
    'num_epochs': num_epochs,
    'train_losses': train_losses,
    'val_losses': val_losses,
    'parameters': param_count,
    'batch_size': batch_size,
    'device': str(device),
    'final_train_loss': train_losses[-1],
    'final_val_loss': val_losses[-1]
}

log_path = EXPERIMENTAL_DIR / "logs" / "training_log.json"
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(training_log, f, indent=2)

print(f"Training log saved: {log_path}")

print("\n" + "="*60)
print("Training Complete")
print("="*60)
