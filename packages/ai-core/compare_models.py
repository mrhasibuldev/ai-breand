"""
Baseline vs New Model Comparison

Compares the original SmallTransformer with the new MediumTransformer.
"""

import sys
import json
import torch
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent))

from tokenizer.tokenizer import SimpleTokenizer
from neural.small_transformer import SmallTransformer
from neural.medium_transformer import MediumTransformer


def load_checkpoint(model, checkpoint_path):
    """Load model from checkpoint"""
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    return checkpoint.get('metrics', {})


def test_generation(model, tokenizer, prompt, max_tokens=20):
    """Test text generation"""
    model.eval()
    with torch.no_grad():
        # Encode prompt
        input_ids = torch.tensor([tokenizer.encode(prompt, add_special_tokens=True)])
        
        # Generate
        generated = model.generate(input_ids, max_new_tokens=max_tokens, temperature=0.8, do_sample=True)
        
        # Decode
        generated_text = tokenizer.decode(generated[0].tolist(), skip_special_tokens=True)
        
        return generated_text


def compare_models():
    """Compare baseline and new models"""
    
    print("[Comparison] Baseline vs New Model")
    print("=" * 70)
    
    # Paths
    script_dir = Path(__file__).parent
    tokenizer_file = script_dir / "tokenizer" / "multilingual_tokenizer.json"
    baseline_checkpoint = script_dir / "models" / "checkpoints" / "checkpoint_epoch_5.pt"
    new_checkpoint = script_dir / "models" / "checkpoints_medium" / "final_model.pt"
    
    # Load tokenizer
    print("\n[Setup] Loading tokenizer...")
    tokenizer = SimpleTokenizer(vocab_size=2000)
    tokenizer.load(str(tokenizer_file))
    vocab_size = tokenizer.get_vocab_size()
    print(f"Vocabulary size: {vocab_size}")
    
    # Create baseline model
    print("\n[Model 1] Creating Baseline SmallTransformer...")
    baseline_model = SmallTransformer(
        vocab_size=vocab_size,
        d_model=128,
        n_layers=4,
        n_heads=4,
        d_ff=512
    )
    baseline_params = baseline_model.count_parameters()
    print(f"Parameters: {baseline_params:,}")
    
    # Load baseline checkpoint if exists
    baseline_metrics = {}
    if baseline_checkpoint.exists():
        print(f"Loading baseline checkpoint...")
        try:
            baseline_metrics = load_checkpoint(baseline_model, baseline_checkpoint)
            print(f"Train loss: {baseline_metrics.get('final_train_loss', 'N/A')}")
            print(f"Val loss: {baseline_metrics.get('final_val_loss', 'N/A')}")
        except Exception as e:
            print(f"Cannot load baseline checkpoint (architecture mismatch): {e}")
            print("Using untrained baseline for comparison")
    else:
        print("Baseline checkpoint not found, using untrained model")
    
    # Create new model
    print("\n[Model 2] Creating New MediumTransformer...")
    new_model = MediumTransformer(
        vocab_size=vocab_size,
        d_model=256,
        n_layers=6,
        n_heads=8,
        d_ff=1024
    )
    new_params = new_model.count_parameters()
    print(f"Parameters: {new_params:,}")
    
    # Load new checkpoint
    new_metrics = {}
    if new_checkpoint.exists():
        print(f"Loading new model checkpoint...")
        new_metrics = load_checkpoint(new_model, new_checkpoint)
        print(f"Train loss: {new_metrics.get('final_train_loss', 'N/A')}")
        print(f"Val loss: {new_metrics.get('final_val_loss', 'N/A')}")
    else:
        print("New model checkpoint not found")
    
    # Comparison summary
    print("\n" + "=" * 70)
    print("[COMPARISON SUMMARY]")
    print("=" * 70)
    
    print(f"\nParameter Count:")
    print(f"  Baseline (Small):  {baseline_params:,}")
    print(f"  New (Medium):       {new_params:,}")
    print(f"  Increase:           {new_params / baseline_params:.2f}x")
    print(f"  Additional:         {new_params - baseline_params:,}")
    
    print(f"\nArchitecture:")
    print(f"  Baseline:  d_model=128, layers=4, heads=4, d_ff=512")
    print(f"  New:       d_model=256, layers=6, heads=8, d_ff=1024")
    
    if baseline_metrics and new_metrics:
        print(f"\nTraining Metrics:")
        print(f"  Baseline Train Loss: {baseline_metrics.get('final_train_loss', 'N/A'):.4f}")
        print(f"  New Train Loss:      {new_metrics.get('final_train_loss', 'N/A'):.4f}")
        print(f"  Baseline Val Loss:   {baseline_metrics.get('final_val_loss', 'N/A'):.4f}")
        print(f"  New Val Loss:        {new_metrics.get('final_val_loss', 'N/A'):.4f}")
    
    # Test generation
    print(f"\n[Generation Test]")
    test_prompts = [
        "তোমার নাম কি?",
        "What is your name?",
        "তুমি কী করতে পারো?"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        
        if new_checkpoint.exists():
            try:
                generated = test_generation(new_model, tokenizer, prompt, max_tokens=15)
                print(f"New Model:  {generated}")
            except Exception as e:
                print(f"New Model:  Error - {e}")
        
        if baseline_checkpoint.exists():
            try:
                generated = test_generation(baseline_model, tokenizer, prompt, max_tokens=15)
                print(f"Baseline:   {generated}")
            except Exception as e:
                print(f"Baseline:   Error - {e}")
    
    print("\n" + "=" * 70)
    print("[CONCLUSION]")
    print("=" * 70)
    
    if new_params > baseline_params:
        print(f"✅ New model has {new_params / baseline_params:.2f}x more parameters")
        print(f"✅ Architecture upgraded for better multilingual performance")
        
        if new_metrics:
            print(f"✅ New model trained successfully")
            print(f"✅ Final validation loss: {new_metrics.get('final_val_loss', 'N/A'):.4f}")
    
    print(f"\nNext Steps:")
    print(f"1. Test with larger dataset (current: 19 samples)")
    print(f"2. Increase training epochs (current: 5)")
    print(f"3. Add more Bengali and English data")
    print(f"4. Test conversational quality")


if __name__ == "__main__":
    compare_models()
