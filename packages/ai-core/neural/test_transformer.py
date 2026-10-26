"""
Unit tests for Small Transformer
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from neural.transformer import SmallTransformer


def test_model_creation():
    """Test model initialization"""
    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    assert model.vocab_size == 1000
    assert model.d_model == 64
    assert model.n_layers == 2
    assert model.n_heads == 2

    print("[PASS] Model creation test passed")


def test_forward_pass():
    """Test forward pass"""
    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    batch_size = 4
    seq_len = 32

    input_ids = torch.randint(0, 1000, (batch_size, seq_len))
    targets = torch.randint(0, 1000, (batch_size, seq_len))

    # Test with targets (should return loss)
    loss = model(input_ids, targets)
    assert loss.dim() == 0  # Scalar
    assert not torch.isnan(loss)
    assert not torch.isinf(loss)

    # Test without targets (should return logits)
    logits = model(input_ids)
    assert logits.shape == (batch_size, seq_len, 1000)
    assert not torch.isnan(logits).any()

    print("[PASS] Forward pass test passed")


def test_parameter_count():
    """Test parameter count"""
    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    param_count = model.count_parameters()
    assert param_count > 0
    assert param_count < 1000000  # Should be small for Phase 1

    print(f"[PASS] Parameter count test passed ({param_count:,} parameters)")


def test_gradient_flow():
    """Test that gradients flow correctly"""
    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    input_ids = torch.randint(0, 1000, (2, 16))
    targets = torch.randint(0, 1000, (2, 16))

    loss = model(input_ids, targets)
    loss.backward()

    # Check that gradients exist
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"No gradient for {name}"
            assert not torch.isnan(param.grad).any(), f"NaN gradient for {name}"

    print("[PASS] Gradient flow test passed")


def test_generation():
    """Test text generation"""
    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    input_ids = torch.randint(0, 1000, (1, 10))

    # Test generation
    generated = model.generate(input_ids, max_new_tokens=5, temperature=1.0)

    assert generated.shape == (1, 15)  # 10 + 5
    assert not torch.isnan(generated).any()

    print("[PASS] Generation test passed")


def test_causal_mask():
    """Test causal mask generation"""
    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    seq_len = 10
    device = torch.device('cpu')
    mask = model.generate_causal_mask(seq_len, device)

    assert mask.shape == (seq_len, seq_len)

    # Check that mask is lower triangular
    for i in range(seq_len):
        for j in range(seq_len):
            if j > i:
                assert mask[i, j] == 0
            else:
                assert mask[i, j] == 1

    print("[PASS] Causal mask test passed")


def test_save_load():
    """Test model save and load"""
    import tempfile

    model = SmallTransformer(
        vocab_size=1000,
        d_model=64,
        n_layers=2,
        n_heads=2,
        d_ff=256,
        max_len=128
    )

    # Save
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as f:
        temp_path = f.name

    try:
        torch.save(model.state_dict(), temp_path)

        # Load into new model
        new_model = SmallTransformer(
            vocab_size=1000,
            d_model=64,
            n_layers=2,
            n_heads=2,
            d_ff=256,
            max_len=128
        )
        new_model.load_state_dict(torch.load(temp_path))

        # Test that both models produce same output
        input_ids = torch.randint(0, 1000, (2, 16))

        model.eval()
        new_model.eval()

        with torch.no_grad():
            output1 = model(input_ids)
            output2 = new_model(input_ids)

        assert torch.allclose(output1, output2, atol=1e-6)

        print("[PASS] Save/load test passed")

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def run_all_tests():
    """Run all unit tests"""
    print("Running Transformer unit tests...\n")

    test_model_creation()
    test_forward_pass()
    test_parameter_count()
    test_gradient_flow()
    test_generation()
    test_causal_mask()
    test_save_load()

    print("\n[PASS] All Transformer tests passed!")


if __name__ == "__main__":
    run_all_tests()
