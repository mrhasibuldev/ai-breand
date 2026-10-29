"""
Verify Model Inference

Load the trained checkpoint and test with real prompts.
"""

import sys
import os
import torch
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer.tokenizer import SimpleTokenizer
from neural.small_transformer import SmallTransformer
from training.dataset import load_json_dataset
from inference.generator import TextGenerator


def main():
    """Test model inference with real prompts"""

    print("=" * 60)
    print("MODEL INFERENCE VERIFICATION")
    print("=" * 60)

    # Load tokenizer
    print("\n1. Loading tokenizer...")
    tokenizer = SimpleTokenizer(vocab_size=1000)
    train_texts = load_json_dataset("data/synthetic/train.json")
    val_texts = load_json_dataset("data/synthetic/validation.json")
    all_texts = train_texts + val_texts
    tokenizer.build_vocab(all_texts, min_freq=1)
    print(f"   Vocab size: {tokenizer.get_vocab_size()}")

    # Load model
    print("\n2. Loading model from checkpoint...")
    model = SmallTransformer(
        vocab_size=tokenizer.get_vocab_size(),
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    checkpoint_path = "models/checkpoints/checkpoint_epoch_5.pt"
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print(f"   Loaded from epoch {checkpoint['epoch']}")
    print(f"   Validation loss: {checkpoint['loss']:.4f}")

    # Test with real prompts
    print("\n3. Testing inference with real prompts...")
    generator = TextGenerator(model, tokenizer, device="cpu")

    test_prompts = [
        "Hello",
        "How are you?",
        "What is your name?",
        "What can you do?",
        "My name is Alex.",
        "What is my name?",
        "Tell me something about Bangladesh.",
        "What should I do today?",
        "I am feeling confused.",
        "Can you help me?"
    ]

    results = []
    for prompt in test_prompts:
        start_time = time.time()
        try:
            generated = generator.generate(
                prompt=prompt,
                max_new_tokens=20,
                temperature=0.8,
                do_sample=True
            )
            latency = (time.time() - start_time) * 1000

            results.append({
                "prompt": prompt,
                "generated": generated,
                "latency_ms": latency
            })

            print(f"\nPrompt: '{prompt}'")
            print(f"Generated: '{generated}'")
            print(f"Latency: {latency:.2f}ms")

            # Analysis
            if generated == prompt.lower():
                print("Status: PURE REPETITION")
            elif len(generated) < len(prompt):
                print("Status: SHORTER THAN INPUT")
            elif generated == "":
                print("Status: EMPTY RESPONSE")
            else:
                print("Status: SOME GENERATION")

        except Exception as e:
            print(f"\nPrompt: '{prompt}'")
            print(f"ERROR: {e}")
            results.append({
                "prompt": prompt,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("INFERENCE SUMMARY")
    print("=" * 60)

    repetition_count = sum(1 for r in results if "generated" in r and r["generated"] == r["prompt"].lower())
    empty_count = sum(1 for r in results if "generated" in r and r["generated"] == "")
    error_count = sum(1 for r in results if "error" in r)

    print(f"Total tests: {len(results)}")
    print(f"Pure repetition: {repetition_count}")
    print(f"Empty responses: {empty_count}")
    print(f"Errors: {error_count}")

    if repetition_count > len(results) / 2:
        print("\nHONEST ASSESSMENT: Model mostly repeats input")
        print("This is EXPECTED for 176K params and 186 samples")
        print("Conversational intelligence: NOT ACHIEVED")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
