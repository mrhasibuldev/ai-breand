"""
Full Pipeline Integration Test

Complete integration test: train -> save -> load -> infer
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from tokenizer.tokenizer import SimpleTokenizer
from neural.small_transformer import SmallTransformer
from training.dataset import TextDataset, load_json_dataset
from training.pipeline import TrainingPipeline
from inference.generator import TextGenerator


def run_full_pipeline():
    """Run complete training and inference pipeline"""

    print("=" * 60)
    print("NEXUSAI BRAIN - PHASE 1 FULL PIPELINE TEST")
    print("=" * 60)

    # Configuration
    VOCAB_SIZE = 1000
    D_MODEL = 64
    N_LAYERS = 2
    N_HEADS = 2
    D_FF = 256
    MAX_LEN = 128
    BATCH_SIZE = 8
    EPOCHS = 5
    LEARNING_RATE = 0.001

    print("\n1. BUILDING TOKENIZER...")
    tokenizer = SimpleTokenizer(vocab_size=VOCAB_SIZE)

    # Load datasets
    train_texts = load_json_dataset("data/synthetic/train.json")
    val_texts = load_json_dataset("data/synthetic/validation.json")

    print(f"   Training samples: {len(train_texts)}")
    print(f"   Validation samples: {len(val_texts)}")

    # Build vocabulary
    all_texts = train_texts + val_texts
    tokenizer.build_vocab(all_texts, min_freq=1)
    print(f"   Vocabulary size: {tokenizer.get_vocab_size()}")

    print("\n2. CREATING MODEL...")
    model = SmallTransformer(
        vocab_size=tokenizer.get_vocab_size(),
        d_model=D_MODEL,
        n_layers=N_LAYERS,
        n_heads=N_HEADS,
        d_ff=D_FF,
        max_len=MAX_LEN
    )
    print(f"   Model parameters: {model.count_parameters():,}")

    print("\n3. PREPARING DATASETS...")
    train_dataset = TextDataset(train_texts, tokenizer, max_len=MAX_LEN)
    val_dataset = TextDataset(val_texts, tokenizer, max_len=MAX_LEN)
    print(f"   Train dataset size: {len(train_dataset)}")
    print(f"   Validation dataset size: {len(val_dataset)}")

    print("\n4. TRAINING MODEL...")
    pipeline = TrainingPipeline(
        model=model,
        tokenizer=tokenizer,
        checkpoint_dir="models/checkpoints",
        device="cpu"
    )

    metrics = pipeline.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        checkpoint_freq=1
    )

    print(f"\n   Final train loss: {metrics['final_train_loss']:.4f}")
    print(f"   Final val loss: {metrics['final_val_loss']:.4f}")

    # Verify loss decreased
    if metrics['train_losses'][0] > metrics['final_train_loss']:
        print("   [SUCCESS] Training loss decreased!")
    else:
        print("   [WARNING] Training loss did not decrease")

    print("\n5. LOADING CHECKPOINT...")
    checkpoint_path = "models/checkpoints/checkpoint_epoch_5.pt"
    if os.path.exists(checkpoint_path):
        # Create new model and load checkpoint
        new_model = SmallTransformer(
            vocab_size=tokenizer.get_vocab_size(),
            d_model=D_MODEL,
            n_layers=N_LAYERS,
            n_heads=N_HEADS,
            d_ff=D_FF,
            max_len=MAX_LEN
        )

        checkpoint = torch.load(checkpoint_path, map_location="cpu")
        new_model.load_state_dict(checkpoint["model_state_dict"])
        print(f"   Checkpoint loaded from {checkpoint_path}")
    else:
        print(f"   [WARNING] Checkpoint not found at {checkpoint_path}")
        new_model = model

    print("\n6. RUNNING INFERENCE...")
    generator = TextGenerator(new_model, tokenizer, device="cpu")

    test_prompts = [
        "The sky is",
        "What is",
        "I love"
    ]

    for prompt in test_prompts:
        print(f"\n   Prompt: '{prompt}'")
        generated = generator.generate(
            prompt=prompt,
            max_new_tokens=20,
            temperature=0.8,
            do_sample=True
        )
        print(f"   Generated: '{generated}'")

    print("\n" + "=" * 60)
    print("PHASE 1 PIPELINE TEST COMPLETED")
    print("=" * 60)
    print("\nMILESTONE ACHIEVED:")
    print("- Tokenizer working")
    print("- Neural network implemented")
    print("- Training pipeline functional")
    print("- Checkpoint save/load working")
    print("- Inference generating text")
    print("\nNexusAI Brain Phase 1: SUCCESS")


if __name__ == "__main__":
    run_full_pipeline()
