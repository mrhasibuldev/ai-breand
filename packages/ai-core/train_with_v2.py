"""
Training Script for Medium Transformer with v2 Dataset

Trains the Medium model with the new high-quality conversational dataset.
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
from torch.utils.data import Dataset, DataLoader
from tokenizer.tokenizer import SimpleTokenizer
from neural.medium_transformer import MediumTransformer
from training.dataset import TextDataset
from training.pipeline import TrainingPipeline


class ConversationDataset(Dataset):
    """Dataset for conversational message pairs"""
    
    def __init__(self, conversations, tokenizer, max_len=256):
        self.texts = []
        for conv in conversations:
            if "messages" in conv:
                # Convert conversation to training text
                messages = conv["messages"]
                conversation_text = ""
                for msg in messages:
                    role = msg["role"]
                    content = msg["content"]
                    conversation_text += f"{role}: {content} "
                self.texts.append(conversation_text.strip())
        
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # Encode text
        token_ids = self.tokenizer.encode(text, add_special_tokens=True)
        
        # Truncate or pad
        if len(token_ids) > self.max_len:
            token_ids = token_ids[:self.max_len]
        else:
            # Pad with PAD token
            pad_id = self.tokenizer.word_to_id["<PAD>"]
            token_ids = token_ids + [pad_id] * (self.max_len - len(token_ids))
        
        # Input and target (shifted by 1 for next-token prediction)
        input_ids = torch.tensor(token_ids[:-1], dtype=torch.long)
        targets = torch.tensor(token_ids[1:], dtype=torch.long)
        
        return {
            "input_ids": input_ids,
            "targets": targets
        }


def train_with_v2():
    """Train Medium Transformer with v2 dataset"""
    
    print("[Training] Starting Medium Transformer Training with v2 Dataset")
    print("=" * 60)
    
    # Paths
    script_dir = Path(__file__).parent
    data_file = script_dir / "data" / "train_v2.json"
    tokenizer_file = script_dir / "tokenizer" / "v2_tokenizer.json"
    checkpoint_dir = script_dir / "models" / "checkpoints_v2"
    
    # Load v2 dataset
    print(f"\n[Step 1] Loading data from {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Build tokenizer
    print(f"\n[Step 2] Building tokenizer")
    # Extract all text for vocabulary building
    all_texts = []
    for conv in conversations:
        if "messages" in conv:
            for msg in conv["messages"]:
                all_texts.append(msg["content"])
    
    tokenizer = SimpleTokenizer(vocab_size=3000)
    tokenizer.build_vocab(all_texts, min_freq=1)
    
    print(f"Vocabulary size: {tokenizer.get_vocab_size()}")
    
    # Save tokenizer
    tokenizer.save(str(tokenizer_file))
    
    # Split data
    print(f"\n[Step 3] Splitting data")
    train_size = int(len(conversations) * 0.8)
    val_size = int(len(conversations) * 0.1)
    
    train_convs = conversations[:train_size]
    val_convs = conversations[train_size:train_size + val_size]
    test_convs = conversations[train_size + val_size:]
    
    print(f"Train: {len(train_convs)}, Val: {len(val_convs)}, Test: {len(test_convs)}")
    
    # Create datasets
    print(f"\n[Step 4] Creating datasets")
    train_dataset = ConversationDataset(train_convs, tokenizer, max_len=256)
    val_dataset = ConversationDataset(val_convs, tokenizer, max_len=256)
    
    # Create model
    print(f"\n[Step 5] Creating Medium Transformer")
    model = MediumTransformer(
        vocab_size=tokenizer.get_vocab_size(),
        d_model=256,
        n_layers=6,
        n_heads=8,
        d_ff=1024,
        max_len=512,
        dropout=0.1
    )
    
    print(f"Model parameters: {model.count_parameters():,}")
    
    # Training pipeline
    print(f"\n[Step 6] Starting training")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    pipeline = TrainingPipeline(
        model=model,
        tokenizer=tokenizer,
        checkpoint_dir=str(checkpoint_dir),
        device="cpu"
    )
    
    # Train with conservative settings for CPU
    metrics = pipeline.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=3,  # Start with 3 epochs for CPU training
        batch_size=2,  # Very small batch size for CPU
        learning_rate=0.001,
        weight_decay=0.01,
        grad_clip=1.0,
        checkpoint_freq=1
    )
    
    print(f"\n[Training Complete]")
    print(f"Final train loss: {metrics['final_train_loss']:.4f}")
    print(f"Final val loss: {metrics['final_val_loss']:.4f}")
    
    # Save final model
    final_checkpoint = checkpoint_dir / "final_model.pt"
    torch.save({
        'model_state_dict': model.state_dict(),
        'tokenizer_vocab': tokenizer.word_to_id,
        'metrics': metrics
    }, final_checkpoint)
    
    print(f"[OK] Model saved to {final_checkpoint}")
    
    return metrics


if __name__ == "__main__":
    train_with_v2()
