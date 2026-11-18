"""
NexusAI multi-core model factory.

Honest architecture note: Core-02/03/04 currently share the Core-01
pre-norm decoder-only Transformer *implementation* but have INDEPENDENT
configurations, weights, datasets, training runs and checkpoints. This is
"same architecture family, independent models" — NOT four distinct
architectures. Documented as such; distinct architectures remain future work.

Usage:
    from nexus_core import build_model, load_checkpoint_strict, chat_generate
    model, config = build_model("core02")
"""
import hashlib
import importlib
import os
import sys

AI_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(AI_CORE_DIR, "models")
if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

# core_id -> (config module path suffix, config class name)
_CORE_MAP = {
    "core01": ("nexusai_core_01.config.model_config", "NexusAICore01Config"),
    "core02": ("nexusai_core_02.config.model_config", "NexusAICore02Config"),
    "core03": ("nexusai_core_03.config.model_config", "NexusAICore03Config"),
    "core04": ("nexusai_core_04.config.model_config", "NexusAICore04Config"),
}

# default checkpoint paths (versioned, model-specific; never overwrite)
DEFAULT_CHECKPOINTS = {
    "core01": os.path.join(AI_CORE_DIR, "models", "checkpoints_core01_run3",
                           "checkpoint_final.pt"),
    "core02": os.path.join(AI_CORE_DIR, "models", "checkpoints_core02_sft_v1",
                           "checkpoint_final.pt"),
    "core03": os.path.join(AI_CORE_DIR, "models", "checkpoints_core03_sft_v1",
                           "checkpoint_final.pt"),
    "core04": os.path.join(AI_CORE_DIR, "models", "checkpoints_core04_sft_v1",
                           "checkpoint_final.pt"),
}


def get_config(core_id, **overrides):
    """Instantiate the per-core config dataclass with optional overrides."""
    core_id = core_id.lower()
    if core_id not in _CORE_MAP:
        raise ValueError(f"unknown core_id {core_id!r}; expected one of {list(_CORE_MAP)}")
    mod_name, cls_name = _CORE_MAP[core_id]
    mod = importlib.import_module(mod_name)
    cls = getattr(mod, cls_name)
    return cls(**overrides)


def build_model(core_id, config=None, device="cpu"):
    """Build the Transformer for a core. Returns (model, config)."""
    from core01.transformer import NexusAICore01
    config = config or get_config(core_id)
    model = NexusAICore01(config)
    return model.to(device), config


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def save_checkpoint(model, config, path, extra=None):
    """Save a versioned checkpoint with provenance metadata + SHA-256."""
    import torch
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "model_state_dict": model.state_dict(),
        "config": config.to_dict() if hasattr(config, "to_dict") else {},
        "core_id": getattr(config, "model_name", "unknown"),
        "format": "nexusai_sft_v1",
    }
    if extra:
        payload.update(extra)
    torch.save(payload, path)
    digest = sha256_file(path)
    meta = {"path": path, "sha256": digest, "bytes": os.path.getsize(path),
            "core_id": payload["core_id"]}
    with open(path + ".sha256", "w") as f:
        f.write(f"{digest}  {os.path.basename(path)}\n")
    return meta


def load_checkpoint_strict(model, path, map_location="cpu"):
    """Strict-load a NexusAI checkpoint. Returns (n_missing, n_unexpected)."""
    import torch
    ckpt = torch.load(path, map_location=map_location, weights_only=True)
    state = ckpt.get("model_state_dict", ckpt)
    res = model.load_state_dict(state, strict=True)
    return res


def chat_prompt_ids(tokenizer, user_text, max_len=512):
    """Build SFT-format prompt ids: [BOS] 'user: <text>' (NO trailing EOS —
    matches serialize_conversation turn format; model continues 'assistant:')."""
    ids = tokenizer.encode("user: " + user_text, add_special_tokens=False)
    # match serialize_conversation: user turn ends with EOS before assistant turn
    seq = [tokenizer.bos_id] + ids + [tokenizer.eos_id]
    if len(seq) > max_len:
        seq = [tokenizer.bos_id] + seq[1:][-(max_len - 1):]
    return seq


def chat_generate(model, tokenizer, user_text, max_new_tokens=80,
                  temperature=0.3, top_k=20, device="cpu"):
    """Greedy-ish chat generation matching SFT serialization format.
    Returns decoded assistant text (leading 'assistant:' stripped)."""
    import torch
    model.eval()
    ids = chat_prompt_ids(tokenizer, user_text)
    input_ids = torch.tensor([ids], dtype=torch.long, device=device)
    prompt_len = input_ids.shape[1]
    with torch.inference_mode():
        out = model.generate(
            input_ids, max_new_tokens=max_new_tokens,
            temperature=temperature, top_k=top_k, top_p=1.0,
            do_sample=False, repetition_penalty=1.1)
    new_ids = out[0, prompt_len:].cpu().tolist()
    text = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
    if text.startswith("assistant:"):
        text = text[len("assistant:"):].strip()
    return text


def status_of(config):
    s = getattr(config, "model_status", None)
    return s.value if hasattr(s, "value") else str(s)
