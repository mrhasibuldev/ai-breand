"""
Diagnostic script to trace the neural generation failure
"""

import sys
import os
import torch
import json

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add paths
service_dir = os.path.dirname(os.path.abspath(__file__))
ai_core_dir = os.path.dirname(service_dir)
sys.path.insert(0, ai_core_dir)

import sentencepiece as spm
from neural.medium_transformer import MediumTransformer

print("=" * 80)
print("NEURAL GENERATION DIAGNOSTIC")
print("=" * 80)

# Load checkpoint
checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")
print(f"\n1. Loading checkpoint from: {checkpoint_path}")

checkpoint = torch.load(checkpoint_path, map_location="cpu")
print(f"   Checkpoint keys: {list(checkpoint.keys())}")

# Load config
if "config" in checkpoint:
    config = checkpoint["config"]
    print(f"   Config: {config}")
else:
    print("   WARNING: No config in checkpoint")
    config = {}

# Load tokenizer
tokenizer_path = os.path.join(ai_core_dir, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
print(f"\n2. Loading tokenizer from: {tokenizer_path}")

tokenizer = spm.SentencePieceProcessor()
tokenizer.load(tokenizer_path)
print(f"   Tokenizer vocab size: {tokenizer.get_piece_size()}")

# Wrapper class
class SentencePieceWrapper:
    def __init__(self, sp_tokenizer):
        self.sp = sp_tokenizer
        self.pad_id = 0
        self.unk_id = 1
        self.bos_id = 2
        self.eos_id = 3
    
    def encode(self, text, add_special_tokens=True):
        tokens = self.sp.encode(text, out_type=int)
        if add_special_tokens:
            tokens = [self.bos_id] + tokens + [self.eos_id]
        return tokens
    
    def decode(self, token_ids, skip_special_tokens=True):
        if skip_special_tokens:
            token_ids = [tid for tid in token_ids if tid not in [self.pad_id, self.unk_id, self.bos_id, self.eos_id]]
        return self.sp.decode(token_ids)

wrapper = SentencePieceWrapper(tokenizer)

# Load model
print(f"\n3. Loading model")
vocab_size = config.get("vocab_size", 8000)
d_model = config.get("d_model", 128)
n_layers = config.get("n_layers", 2)
n_heads = config.get("n_heads", 2)
d_ff = config.get("d_ff", 512)
max_len = config.get("max_len", 128)

model = MediumTransformer(
    vocab_size=vocab_size,
    d_model=d_model,
    n_layers=n_layers,
    n_heads=n_heads,
    d_ff=d_ff,
    max_len=max_len
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
print(f"   Model loaded successfully")
print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")

# Test inputs
test_inputs = [
    "Hello",
    "What is the capital of Bangladesh?",
    "আমার নাম কী?",
    "My name is Rahim."
]

print(f"\n4. Testing generation")
print("=" * 80)

for test_input in test_inputs:
    print(f"\nInput: {test_input}")
    print("-" * 40)
    
    # Encode
    tokens = wrapper.encode(test_input, add_special_tokens=True)
    print(f"Encoded tokens: {tokens[:20]}... (total {len(tokens)})")
    
    input_ids = torch.tensor([tokens], dtype=torch.long)
    print(f"Input tensor shape: {input_ids.shape}")
    
    # Forward pass
    with torch.no_grad():
        logits = model(input_ids)
        print(f"Logits shape: {logits.shape}")
        print(f"Logits finite: {torch.isfinite(logits).all()}")
        print(f"Logits min/max: {logits.min().item():.4f} / {logits.max().item():.4f}")
        
        # Get next token logits
        next_token_logits = logits[:, -1, :]
        print(f"Next token logits shape: {next_token_logits.shape}")
        
        # Top predictions
        top_probs, top_indices = torch.topk(torch.softmax(next_token_logits, dim=-1), 5)
        print(f"Top 5 predictions:")
        for i in range(5):
            token_id = top_indices[0, i].item()
            prob = top_probs[0, i].item()
            token_text = wrapper.sp.decode([token_id])
            print(f"   {i+1}. ID={token_id}, prob={prob:.4f}, text='{token_text}'")
        
        # Greedy selection
        next_token = torch.argmax(next_token_logits, dim=-1)
        next_token_id = next_token.item()
        next_token_text = wrapper.sp.decode([next_token_id])
        print(f"Greedy selection: ID={next_token_id}, text='{next_token_text}'")
        
        # Generate a few tokens
        generated_ids = tokens.copy()
        for step in range(5):
            input_ids = torch.tensor([generated_ids], dtype=torch.long)
            if input_ids.size(1) > max_len:
                input_ids = input_ids[:, -max_len:]
            
            logits = model(input_ids)
            next_token_logits = logits[:, -1, :]
            next_token = torch.argmax(next_token_logits, dim=-1)
            next_token_id = next_token.item()
            
            print(f"   Step {step+1}: generated ID={next_token_id}, text='{wrapper.sp.decode([next_token_id])}'")
            
            generated_ids.append(next_token_id)
            
            if next_token_id == wrapper.eos_id:
                print(f"   Stopped: EOS generated")
                break
        
        # Decode full sequence
        decoded = wrapper.decode(generated_ids, skip_special_tokens=True)
        print(f"Full decoded sequence: '{decoded}'")
        print(f"Length: {len(decoded)} characters")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
