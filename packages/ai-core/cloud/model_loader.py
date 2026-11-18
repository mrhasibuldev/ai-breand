"""Model loading with strict compatibility verification."""
import os, sys, hashlib
from dataclasses import dataclass, field

AI_CORE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, AI_CORE)
sys.path.insert(0, os.path.join(AI_CORE, "models"))

@dataclass
class LoadReport:
    ok: bool = False
    checkpoint: str = ""
    sha256: str = ""
    params: int = 0
    epoch: int = None
    step: int = None
    status: str = ""
    missing_keys: list = field(default_factory=list)
    unexpected_keys: list = field(default_factory=list)
    errors: list = field(default_factory=list)

def load_core01(checkpoint_path: str, config_cls=None,
                model_cls=None, device: str = "cpu") -> LoadReport:
    """Strict-load a Core-01 checkpoint; verify family + metadata."""
    import torch
    from core01.transformer import NexusAICore01
    from nexusai_core_01.config.model_config import (
        NexusAICore01Config, ModelStatus)
    r = LoadReport(checkpoint=checkpoint_path)
    if not os.path.exists(checkpoint_path):
        r.errors.append("checkpoint not found"); return r
    r.sha256 = hashlib.sha256(open(checkpoint_path, "rb").read()).hexdigest()
    try:
        ck = torch.load(checkpoint_path, map_location="cpu",
                        weights_only=False)
    except Exception as e:
        r.errors.append(f"torch.load failed: {e}"); return r
    sd = ck.get("model_state_dict", {})
    keys = list(sd.keys())
    if not any(k.startswith("transformer_blocks.") for k in keys):
        r.errors.append("NOT Core-01 family (expected transformer_blocks.*)")
        return r
    if any("self_attn.in_proj_weight" in k for k in keys):
        r.errors.append("phase10-family keys detected — incompatible")
        return r
    cd = dict(ck.get("config", {}))
    if isinstance(cd.get("model_status"), str):
        try:
            cd["model_status"] = ModelStatus[cd["model_status"]]
        except KeyError:
            cd.pop("model_status", None)
    try:
        cfg = NexusAICore01Config(
            **{k: v for k, v in cd.items()
               if k in NexusAICore01Config.__dataclass_fields__})
    except Exception as e:
        r.errors.append(f"config build failed: {e}"); return r
    model = NexusAICore01(cfg)
    try:
        res = model.load_state_dict(sd, strict=False)
        r.missing_keys = list(res.missing_keys)
        r.unexpected_keys = list(res.unexpected_keys)
        if r.missing_keys or r.unexpected_keys:
            r.errors.append("state-dict mismatch")
            return r
    except Exception as e:
        r.errors.append(f"load_state_dict failed: {e}"); return r
    r.params = model.count_parameters()
    r.epoch = ck.get("epoch"); r.step = ck.get("step")
    r.status = str(ck.get("model_status", ""))
    r.ok = True
    return r
