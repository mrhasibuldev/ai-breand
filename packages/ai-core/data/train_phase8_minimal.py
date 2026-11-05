"""
Phase 8 - Minimal Experimental Training (1 Epoch)

Trains a very small model for 1 epoch to generate an experimental checkpoint.
"""

import json
import os
import sys
import time
from pathlib import Path
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
print("Phase 8 - Minimal Experimental Training (1 Epoch)")
print("="*60)

# Load tokenizer
tokenizer_path = PHASE7_DIR / "tokenizer_models" / "sp_8k_bpe.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()
print(f"Tokenizer loaded: {vocab_size} tokens")

# Import SmallTransformer
sys.path.insert(0, str(AI_CORE_DIR))
from neural.small_transformer import SmallTransformer

# Load dataset
train_path = EXPERIMENTAL_DIR / "data" / "train.txt"
val_path = EXPERIMENTAL_DIR / "data" / "val.txt"

class TextDataset(Dataset):
    def __init__(self, filepath, tokenizer, max_length=64):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self.lines = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(self.lines)} lines")
    
    def __len__(self):
        return len(self.lines)
    
    def __getitem__(self, idx):
        text = self.lines[idx]
        ids = self.tokenizer.encode(text, out_type=int)
        
        if len(ids) > self.max_length:
            ids = ids[:self.max_length]
        
        while len(ids) < self.max_length:
            ids.append(0)
        
        input_ids = torch.tensor(ids[:-1], dtype=torch.long)
        target_ids = torch.tensor(ids[1:], dtype=torch.long)
        
        return input_ids, target_ids

print("\nLoading datasets...")
train_dataset = TextDataset(train_path, sp, max_length=64)
val_dataset = TextDataset(val_path, sp, max_length=64)

batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

print(f"Batch size: {batch_size}")
print(f"Train batches: {len(train_loader)}")
print(f"Val batches: {len(val_loader)}")

# Create very small model
print("\nCreating model...")
model = SmallTransformer(
    vocab_size=vocab_size,
    d_model=64,
    n_layers=1,
    n_heads=2,
    d_ff=256,
    max_len=64,
    dropout=0.0
)

param_count = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {param_count:,}")

device = torch.device('cpu')
model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss(ignore_index=0)

# Train for 1 epoch
print("\n" + "="*60)
print("Training - 1 Epoch")
print("="*60)

model.train()
epoch_loss = 0.0
start_time = time.time()

for batch_idx, (input_ids, target_ids) in enumerate(train_loader):
    input_ids = input_ids.to(device)
    target_ids = target_ids.to(device)
    
    optimizer.zero_grad()
    
    logits = model(input_ids)
    logits = logits.view(-1, vocab_size)
    target_ids = target_ids.view(-1)
    
    loss = criterion(logits, target_ids)
    
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    
    epoch_loss += loss.item()
    
    if batch_idx % 50 == 0:
        print(f"  Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}")

avg_train_loss = epoch_loss / len(train_loader)
train_time = time.time() - start_time

print(f"\nEpoch 1 Summary:")
print(f"  Train Loss: {avg_train_loss:.4f}")
print(f"  Time: {train_time:.2f}s")

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
print(f"  Val Loss: {avg_val_loss:.4f}")

# Save checkpoint
checkpoint_path = EXPERIMENTAL_DIR / "checkpoints" / "experimental_model.pt"
torch.save({
    'model_state_dict': model.state_dict(),
    'vocab_size': vocab_size,
    'config': {
        'd_model': 64,
        'n_layers': 1,
        'n_heads': 2,
        'd_ff': 256,
        'max_len': 64
    },
    'train_loss': avg_train_loss,
    'val_loss': avg_val_loss,
    'parameters': param_count
}, checkpoint_path)

print(f"\nCheckpoint saved: {checkpoint_path}")
print(f"File size: {checkpoint_path.stat().st_size / 1024:.2f} KB")

# Save training log
training_log = {
    'parameters': param_count,
    'train_loss': avg_train_loss,
    'val_loss': avg_val_loss,
    'train_time_seconds': train_time,
    'batch_size': batch_size,
    'epochs': 1
}

log_path = EXPERIMENTAL_DIR / "logs" / "minimal_training_log.json"
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(training_log, f, indent=2)

print(f"Training log saved: {log_path}")

print("\n" + "="*60)
print("Minimal Training Complete")
print("="*60)
