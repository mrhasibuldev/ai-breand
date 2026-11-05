"""
Phase 10 - Evaluation Script

Evaluates the trained model on test set and generates samples.
"""

import json
import sys
import math
import torch
import torch.nn as nn
import unicodedata
from pathlib import Path
from datetime import datetime

# Paths
DATA_DIR = Path(__file__).parent
PHASE9_2_DIR = DATA_DIR / "experimental" / "phase9_2"
PHASE10_DIR = DATA_DIR / "experimental" / "phase10"
DATASETS_DIR = PHASE10_DIR / "datasets"
CHECKPOINTS_DIR = PHASE10_DIR / "checkpoints"
EVALUATIONS_DIR = PHASE10_DIR / "evaluations"
SAMPLES_DIR = PHASE10_DIR / "samples"
MANIFESTS_DIR = PHASE10_DIR / "manifests"

# Create directories
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 10 - Evaluation Script")
print("="*60)

# Load tokenizer
import sentencepiece as spm
tokenizer_path = PHASE9_2_DIR / "tokenizers" / "bpe_8k" / "sp_bpe_8k.model"
sp = spm.SentencePieceProcessor()
sp.load(str(tokenizer_path))
vocab_size = sp.get_piece_size()

print(f"\nTokenizer loaded: {vocab_size} tokens")

# Load test data
with open(DATASETS_DIR / "test.json", 'r', encoding='utf-8') as f:
    test_data = json.load(f)

print(f"Test data loaded: {len(test_data)} examples")

# Load checkpoint
checkpoint_path = CHECKPOINTS_DIR / "best_model.pt"
checkpoint = torch.load(checkpoint_path, map_location='cpu')
config = checkpoint['config']

print(f"\nCheckpoint loaded: {checkpoint_path}")
print(f"  Epoch: {checkpoint['epoch'] + 1}")
print(f"  Val loss: {checkpoint['val_loss']:.4f}")

# Define model
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
    
    def forward(self, x, mask=None):
        batch_size, seq_len = x.shape
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        x = self.embedding(x) + self.pos_embedding(positions)
        x = self.dropout(x)
        x = self.transformer(x, mask=mask)
        x = self.fc(x)
        return x

# Create model
model_config = {k: v for k, v in config.items() if k not in ['vocab_size', 'batch_size', 'epochs', 'learning_rate', 'weight_decay', 'grad_clip', 'random_seed', 'device']}
model = TransformerModel(config['vocab_size'], **model_config)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

device = torch.device('cpu')
model = model.to(device)

print(f"\nModel loaded")
print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")

# Test loss evaluation
print(f"\nEvaluating test loss...")
criterion = nn.CrossEntropyLoss(ignore_index=0)

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

test_loss = 0
test_batches = 0

with torch.no_grad():
    for i in range(0, len(test_data), config['batch_size']):
        batch = test_data[i:i + config['batch_size']]
        
        if len(batch) < config['batch_size']:
            continue
        
        input_ids, target_ids = collate_fn(batch)
        input_ids = input_ids.to(device)
        target_ids = target_ids.to(device)
        
        outputs = model(input_ids)
        outputs = outputs.reshape(-1, config['vocab_size'])
        target_ids = target_ids.reshape(-1)
        
        loss = criterion(outputs, target_ids)
        test_loss += loss.item()
        test_batches += 1

avg_test_loss = test_loss / test_batches if test_batches > 0 else 0
perplexity = math.exp(avg_test_loss) if avg_test_loss < 20 else float('inf')

print(f"  Test loss: {avg_test_loss:.4f}")
print(f"  Perplexity: {perplexity:.2f}")

# Generation samples
print(f"\nGenerating samples...")

generation_prompts = [
    "Hello",
    "তুমি কেমন",
    "I want to",
    "আমি একটি",
    "The weather",
    "আজকের"
]

def generate_text(prompt, max_tokens=20, temperature=0.7):
    normalized = unicodedata.normalize('NFC', prompt)
    input_ids = sp.encode(normalized, out_type=int)
    
    if len(input_ids) == 0:
        return ""
    
    input_tensor = torch.tensor([input_ids], dtype=torch.long).to(device)
    
    generated = input_ids.copy()
    
    for _ in range(max_tokens):
        input_tensor = torch.tensor([generated[-config['max_len']:]], dtype=torch.long).to(device)
        
        with torch.no_grad():
            outputs = model(input_tensor)
            logits = outputs[0, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1).item()
        
        if next_token == 3:  # EOS
            break
        
        generated.append(next_token)
        
        if len(generated) >= config['max_len']:
            break
    
    decoded = sp.decode(generated)
    return decoded

samples = []
for prompt in generation_prompts:
    generated = generate_text(prompt, max_tokens=15, temperature=0.7)
    samples.append({
        "prompt": prompt,
        "generated": generated
    })
    print(f"\nPrompt length: {len(prompt)}")
    print(f"Generated length: {len(generated)}")

# Save evaluation results
evaluation = {
    "evaluation_timestamp": datetime.now().isoformat(),
    "checkpoint": str(checkpoint_path),
    "config": config,
    "test_loss": avg_test_loss,
    "perplexity": perplexity,
    "samples": samples
}

eval_path = EVALUATIONS_DIR / "evaluation_results.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(evaluation, f, indent=2, ensure_ascii=False)

print(f"\nEvaluation saved: {eval_path}")

print("\n" + "="*60)
print("EVALUATION COMPLETE")
print("="*60)
