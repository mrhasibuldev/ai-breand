"""
Phase 10 - Training Script

Trains the experimental Transformer model.
"""

import json
import sys
import time
import random
import torch
import torch.nn as nn
from pathlib import Path
from datetime import datetime

# Paths
DATA_DIR = Path(__file__).parent
AI_CORE_DIR = DATA_DIR.parent
PHASE10_DIR = DATA_DIR / "experimental" / "phase10"
DATASETS_DIR = PHASE10_DIR / "datasets"
CHECKPOINTS_DIR = PHASE10_DIR / "checkpoints"
LOGS_DIR = PHASE10_DIR / "logs"
MANIFESTS_DIR = PHASE10_DIR / "manifests"

# Create directories
CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 10 - Training Script")
print("="*60)

# Simple Transformer model
class TransformerModel(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=2, num_layers=2, 
                 dim_feedforward=512, dropout=0.1, max_len=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(dropout)
        self._init_weights()
    
    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
    
    def forward(self, x, mask=None):
        batch_size, seq_len = x.shape
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        x = self.embedding(x) + self.pos_embedding(positions)
        x = self.dropout(x)
        x = self.transformer(x, mask=mask)
        x = self.fc(x)
        return x
    
    def count_parameters(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

# Configuration
config = {
    "vocab_size": 8000,
    "d_model": 128,
    "nhead": 2,
    "num_layers": 2,
    "dim_feedforward": 512,
    "dropout": 0.1,
    "max_len": 128,
    "batch_size": 4,
    "epochs": 3,
    "learning_rate": 0.0003,
    "weight_decay": 0.01,
    "grad_clip": 1.0,
    "random_seed": 42,
    "device": "cpu"
}

print(f"\nConfiguration:")
for key, value in config.items():
    print(f"  {key}: {value}")

# Set random seed
random.seed(config['random_seed'])
torch.manual_seed(config['random_seed'])

# Load datasets
print(f"\nLoading datasets...")
with open(DATASETS_DIR / "train.json", 'r', encoding='utf-8') as f:
    train_data = json.load(f)

with open(DATASETS_DIR / "val.json", 'r', encoding='utf-8') as f:
    val_data = json.load(f)

print(f"  Train: {len(train_data)}")
print(f"  Validation: {len(val_data)}")

# Create model
print(f"\nCreating model...")
model_config = {k: v for k, v in config.items() if k not in ['vocab_size', 'batch_size', 'epochs', 'learning_rate', 'weight_decay', 'grad_clip', 'random_seed', 'device']}
model = TransformerModel(config['vocab_size'], **model_config)
num_params = model.count_parameters()
print(f"  Parameters: {num_params:,}")

device = torch.device(config['device'])
model = model.to(device)
print(f"  Device: {device}")

# Loss and optimizer
criterion = nn.CrossEntropyLoss(ignore_index=0)
optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'], weight_decay=config['weight_decay'])

# Collate function
def collate_fn(batch):
    max_len = max(len(item['tokens']) for item in batch)
    max_len = min(max_len, config['max_len'])
    padded = []
    for item in batch:
        tokens = item['tokens'][:max_len]
        if len(tokens) < max_len:
            tokens = tokens + [0] * (max_len - len(tokens))
        padded.append(tokens)
    input_ids = torch.tensor([seq[:-1] for seq in padded], dtype=torch.long)
    target_ids = torch.tensor([seq[1:] for seq in padded], dtype=torch.long)
    return input_ids, target_ids

# Training
print(f"\nStarting training...")
print(f"Epochs: {config['epochs']}")
print(f"Batch size: {config['batch_size']}")

training_log = {
    "config": config,
    "num_parameters": num_params,
    "epochs": []
}

best_val_loss = float('inf')
start_time = time.time()

for epoch in range(config['epochs']):
    epoch_start = time.time()
    
    # Training
    model.train()
    train_loss = 0
    num_batches = 0
    
    random.shuffle(train_data)
    
    for i in range(0, len(train_data), config['batch_size']):
        batch = train_data[i:i + config['batch_size']]
        
        if len(batch) < config['batch_size']:
            continue
        
        input_ids, target_ids = collate_fn(batch)
        input_ids = input_ids.to(device)
        target_ids = target_ids.to(device)
        
        optimizer.zero_grad()
        outputs = model(input_ids)
        outputs = outputs.reshape(-1, config['vocab_size'])
        target_ids = target_ids.reshape(-1)
        
        loss = criterion(outputs, target_ids)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), config['grad_clip'])
        optimizer.step()
        
        train_loss += loss.item()
        num_batches += 1
    
    avg_train_loss = train_loss / num_batches if num_batches > 0 else 0
    
    # Validation
    model.eval()
    val_loss = 0
    val_batches = 0
    
    with torch.no_grad():
        for i in range(0, len(val_data), config['batch_size']):
            batch = val_data[i:i + config['batch_size']]
            
            if len(batch) < config['batch_size']:
                continue
            
            input_ids, target_ids = collate_fn(batch)
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)
            
            outputs = model(input_ids)
            outputs = outputs.reshape(-1, config['vocab_size'])
            target_ids = target_ids.reshape(-1)
            
            loss = criterion(outputs, target_ids)
            val_loss += loss.item()
            val_batches += 1
    
    avg_val_loss = val_loss / val_batches if val_batches > 0 else 0
    
    epoch_time = time.time() - epoch_start
    
    print(f"\nEpoch {epoch + 1}/{config['epochs']}:")
    print(f"  Train Loss: {avg_train_loss:.4f}")
    print(f"  Val Loss: {avg_val_loss:.4f}")
    print(f"  Time: {epoch_time:.2f}s")
    
    # Save best checkpoint
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        checkpoint_path = CHECKPOINTS_DIR / "best_model.pt"
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss': avg_val_loss,
            'config': config
        }, checkpoint_path)
        print(f"  [NEW BEST] Checkpoint saved")
    
    training_log['epochs'].append({
        'epoch': epoch + 1,
        'train_loss': avg_train_loss,
        'val_loss': avg_val_loss,
        'time': epoch_time
    })

total_time = time.time() - start_time
print(f"\nTraining complete!")
print(f"Total time: {total_time:.2f}s")
print(f"Best val loss: {best_val_loss:.4f}")

# Save log
log_path = LOGS_DIR / "training_log.json"
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(training_log, f, indent=2, ensure_ascii=False)

print(f"Training log saved: {log_path}")

print("\n" + "="*60)
print("TRAINING COMPLETE")
print("="*60)
