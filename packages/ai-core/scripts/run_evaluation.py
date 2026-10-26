"""
Run Evaluation Suite

Run honest evaluation of the trained model.
"""

import sys
import os
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenizer.tokenizer import SimpleTokenizer
from neural.transformer import SmallTransformer
from training.dataset import load_json_dataset
from evaluation.evaluator import ModelEvaluator


def main():
    """Run evaluation suite"""
    print("=" * 60)
    print("NEXUSAI BRAIN - PHASE 2 EVALUATION SUITE")
    print("=" * 60)

    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = SimpleTokenizer(vocab_size=1000)
    train_texts = load_json_dataset("data/synthetic/train.json")
    val_texts = load_json_dataset("data/synthetic/validation.json")
    all_texts = train_texts + val_texts
    tokenizer.build_vocab(all_texts, min_freq=1)
    print(f"Tokenizer loaded, vocab size: {tokenizer.get_vocab_size()}")

    # Load model
    print("\nLoading model from checkpoint...")
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
    print(f"Model loaded from epoch {checkpoint['epoch']}")

    # Run evaluation
    print("\n" + "=" * 60)
    print("STARTING EVALUATION")
    print("=" * 60)

    evaluator = ModelEvaluator(model, tokenizer)
    results = evaluator.run_all_tests()

    # Save results
    results_path = "evaluation_results.json"
    evaluator.save_results(results_path)

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print("\nTest Categories:")
    for test_name in results.keys():
        print(f"  - {test_name}")

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
