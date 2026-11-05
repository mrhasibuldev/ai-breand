"""
Simple test of generation without the orchestration layer
"""

import sys
import os
import torch

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

# Load checkpoint
checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")
checkpoint = torch.load(checkpoint_path, map_location="cpu")
config = checkpoint["config"]

# Load tokenizer
tokenizer_path = os.path.join(ai_core_dir, "data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model")
tokenizer = spm.SentencePieceProcessor()
tokenizer.load(tokenizer_path)

# Wrapper
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
model = MediumTransformer(
    vocab_size=config["vocab_size"],
    d_model=config["d_model"],
    n_layers=config["n_layers"],
    n_heads=config["n_heads"],
    d_ff=config["d_ff"],
    max_len=config["max_len"]
)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Test with simple prompt (no "User:" prefix)
prompt = "What is the capital of Bangladesh?"
print(f"Prompt: {prompt}")

tokens = wrapper.encode(prompt, add_special_tokens=True)
print(f"Tokens: {tokens}")

input_ids = torch.tensor([tokens], dtype=torch.long)

# Generate
with torch.no_grad():
    for i in range(10):
        logits = model(input_ids)
        next_token_logits = logits[:, -1, :]
        next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
        next_token_id = next_token.item()
        
        print(f"Step {i+1}: ID={next_token_id}, text='{wrapper.sp.decode([next_token_id])}'")
        
        input_ids = torch.cat([input_ids, next_token], dim=1)
        
        if next_token_id == wrapper.eos_id:
            break

# Decode
generated_ids = input_ids[0].tolist()
generated_text = wrapper.decode(generated_ids, skip_special_tokens=True)
print(f"Full output: {generated_text}")

# Remove prompt
prompt_tokens = wrapper.encode(prompt, add_special_tokens=True)
if len(generated_ids) > len(prompt_tokens):
    new_tokens = generated_ids[len(prompt_tokens):]
    new_text = wrapper.decode(new_tokens, skip_special_tokens=True)
    print(f"New tokens only: {new_text}")
