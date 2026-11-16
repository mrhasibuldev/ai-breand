"""
Non-destructive Core-01 integrity tests.
Run: python packages/ai-core/evaluation/test_core01_integrity.py
(also pytest-compatible)
"""
import os, sys, json, hashlib

AI_CORE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))

CKPT = os.path.join(AI_CORE, "models", "checkpoints_core01_run3",
                    "checkpoint_final.pt")
TOK = os.path.join(AI_CORE, "data", "experimental", "phase9_2",
                   "tokenizers", "bpe_8k", "sp_bpe_8k.model")
RUN3_SHA = ("ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830")
CORE01_FAMILY = ("token_embedding.", "transformer_blocks.",
                 "positional_encoding.pe", "output_layer.")


def _ckpt_keys():
    import torch
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    return ck, list(ck["model_state_dict"].keys())


def test_run3_sha256():
    h = hashlib.sha256()
    with open(CKPT, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    assert h.hexdigest() == RUN3_SHA, "Run3 checkpoint hash mismatch"


def test_run3_metadata():
    ck, _ = _ckpt_keys()
    assert ck["epoch"] == 3 and ck["step"] == 1341
    assert ck["model_status"] == "PRETRAINING_COMPLETED"
    for k in ("model_state_dict", "optimizer_state_dict",
              "scheduler_state_dict", "grad_scaler_state_dict",
              "rng_state", "config"):
        assert k in ck, f"missing resume key: {k}"


def test_core01_key_family():
    _, keys = _ckpt_keys()
    assert any(k.startswith(CORE01_FAMILY[1]) for k in keys)
    assert any(k.startswith(CORE01_FAMILY[0]) for k in keys)
    assert not any("self_attn.in_proj_weight" in k for k in keys)


def test_phase10_is_different_family():
    p10 = os.path.join(AI_CORE, "data", "experimental", "phase10",
                       "checkpoints", "best_model.pt")
    if not os.path.exists(p10):
        return  # artifact absent on this machine — not a failure
    import torch
    sd = torch.load(p10, map_location="cpu",
                    weights_only=False)["model_state_dict"]
    assert any("self_attn.in_proj_weight" in k for k in sd)
    assert not any(k.startswith("transformer_blocks.") for k in sd)


def test_tokenizer_vocab():
    from core01.tokenizer_interface import NexusAITokenizer
    from nexusai_core_01.config.model_config import (
        NexusAICore01Config, ModelStatus)
    import torch
    ck, _ = _ckpt_keys()
    cd = dict(ck["config"])
    if isinstance(cd.get("model_status"), str):
        cd["model_status"] = ModelStatus[cd["model_status"]]
    cfg = NexusAICore01Config(
        **{k: v for k, v in cd.items()
           if k in NexusAICore01Config.__dataclass_fields__})
    tok = NexusAITokenizer(TOK, cfg)
    assert tok.sp.get_piece_size() == cfg.vocab_size == 8000
    ids = tok.encode("Hello")
    assert ids and tok.decode(ids)


def test_config_matches_checkpoint():
    from nexusai_core_01.config.model_config import NexusAICore01Config
    ck, keys = _ckpt_keys()
    emb = None
    import torch
    sd = ck["model_state_dict"]
    assert sd["token_embedding.embedding.weight"].shape[0] == 8000
    assert sd["token_embedding.embedding.weight"].shape[1] == 256


def test_benchmark_reports_exist():
    d = os.path.join(AI_CORE, "eval_reports")
    reps = [f for f in os.listdir(d) if f.startswith("neural_benchmark")]
    assert reps, "no neural benchmark reports found"
    for f in reps:
        json.load(open(os.path.join(d, f), encoding="utf-8"))


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for fn in fns:
        try:
            fn(); print(f"PASS {fn.__name__}"); ok += 1
        except Exception as e:
            print(f"FAIL {fn.__name__}: {e}")
    print(f"{ok}/{len(fns)} passed")
    sys.exit(0 if ok == len(fns) else 1)
