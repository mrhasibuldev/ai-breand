import torch
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

checkpoint_path = "models/checkpoints_medium/final_model.pt"
checkpoint = torch.load(checkpoint_path, map_location='cpu')

print(f"Checkpoint keys: {list(checkpoint.keys())}")

if "config" in checkpoint:
    print(f"\nCheckpoint config:")
    config = checkpoint["config"]
    for key, value in config.items():
        print(f"  {key}: {value}")

if "model_state_dict" in checkpoint:
    state_dict = checkpoint["model_state_dict"]
    print(f"\nModel state dict keys (first 10): {list(state_dict.keys())[:10]}")

    # Check architecture from state dict
    embedding_weight = state_dict["token_embedding.embedding.weight"]
    print(f"\nEmbedding weight shape: {embedding_weight.shape}")
    vocab_size, d_model = embedding_weight.shape
    print(f"  Vocab size: {vocab_size}")
    print(f"  d_model: {d_model}")

    # Count transformer blocks
    layer_keys = [k for k in state_dict.keys() if k.startswith("transformer_blocks")]
    if layer_keys:
        layer_indices = set()
        for k in layer_keys:
            parts = k.split('.')
            if len(parts) > 1:
                try:
                    layer_indices.add(int(parts[1]))
                except:
                    pass
        n_layers = len(layer_indices)
        print(f"  Number of layers: {n_layers}")

    # Check attention heads (from first layer's attention)
    q_weight = state_dict.get("transformer_blocks.0.attention.wq.weight")
    if q_weight is not None:
        q_shape = q_weight.shape
        print(f"  Q weight shape: {q_shape}")
        # d_model -> (n_heads * d_k)
        d_model_from_q = q_shape[0]
        n_heads_times_dk = q_shape[1]
        print(f"  d_model from Q: {d_model_from_q}")
        print(f"  n_heads * d_k: {n_heads_times_dk}")

# Calculate total parameters
if "model_state_dict" in checkpoint:
    total_params = sum(p.numel() for p in checkpoint["model_state_dict"].values())
    print(f"\nTotal parameters: {total_params:,}")
