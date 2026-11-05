"""
Phase 8 - Model Evaluation

Evaluates the experimental model on Bengali, English, and mixed-language examples.
"""

import json
import sys
from pathlib import Path
import torch
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
print("Phase 8 - Model Evaluation")
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

# Load checkpoint
checkpoint_path = EXPERIMENTAL_DIR / "checkpoints" / "experimental_model.pt"
checkpoint = torch.load(checkpoint_path, map_location='cpu')
print(f"Checkpoint loaded: {checkpoint_path.stat().st_size / 1024:.2f} KB")

# Reconstruct model
config = checkpoint['config']
model = SmallTransformer(
    vocab_size=checkpoint['vocab_size'],
    d_model=config['d_model'],
    n_layers=config['n_layers'],
    n_heads=config['n_heads'],
    d_ff=config['d_ff'],
    max_len=config['max_len'],
    dropout=0.0
)

model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

device = torch.device('cpu')
model = model.to(device)

print(f"Model loaded: {sum(p.numel() for p in model.parameters()):,} parameters")
print(f"Train loss: {checkpoint['train_loss']:.4f}")
print(f"Val loss: {checkpoint['val_loss']:.4f}")

# Test sentences
test_sentences = [
    ("English", "Hello, how are you?"),
    ("English", "I want to build an AI."),
    ("English", "The capital of Bangladesh is Dhaka."),
    ("Bengali", "তুমি কেমন আছো?"),
    ("Bengali", "আমি NexusAI তৈরি করছি।"),
    ("Bengali", "বাংলাদেশের রাজধানী ঢাকা।"),
    ("Mixed", "Hello, তুমি কেমন আছো?"),
    ("Mixed", "I am NexusAI, আমি একটি AI তৈরি করছি।"),
]

print("\nGenerating text...")
print("-" * 60)

results = []

for language, sentence in test_sentences:
    try:
        # Encode
        ids = sp.encode(sentence, out_type=int)
        max_len = 32
        
        if len(ids) > max_len:
            ids = ids[:max_len]
        
        input_tensor = torch.tensor([ids], dtype=torch.long).to(device)
        
        # Generate
        with torch.no_grad():
            for _ in range(20):  # Generate 20 tokens
                logits = model(input_tensor)
                logits = logits[:, -1, :]
                next_token = torch.argmax(logits, dim=-1, keepdim=True)
                input_tensor = torch.cat([input_tensor, next_token], dim=1)
                
                if input_tensor.shape[1] >= max_len:
                    break
        
        # Decode
        generated_ids = input_tensor[0].cpu().tolist()
        generated_text = sp.decode(generated_ids)
        
        print(f"\n[{language}]")
        print(f"  Input: {sentence}")
        print(f"  Output: {generated_text}")
        
        results.append({
            'language': language,
            'input': sentence,
            'output': generated_text,
            'status': 'success'
        })
    except Exception as e:
        print(f"\n[{language}]")
        print(f"  Input: {sentence}")
        print(f"  Error: {e}")
        results.append({
            'language': language,
            'input': sentence,
            'output': str(e),
            'status': 'error'
        })

# Save evaluation results
eval_path = EXPERIMENTAL_DIR / "logs" / "evaluation_results.json"
with open(eval_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n" + "="*60)
print("Evaluation Complete")
print("="*60)
print(f"Results saved: {eval_path}")
