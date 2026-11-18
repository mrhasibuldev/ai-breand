"""Environment detection & validation — provider independent."""
import sys, os, platform, importlib
from dataclasses import dataclass, field

REQUIRED = {"torch": None, "sentencepiece": None}
OPTIONAL = {"numpy": None, "psutil": None}

@dataclass
class EnvReport:
    python: str = ""
    os_name: str = ""
    packages: dict = field(default_factory=dict)
    torch_version: str = ""
    torch_cuda_build: str = ""
    cuda_available: bool = False
    cuda_version: str = ""
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def ok(self):
        return not self.errors

def detect_environment() -> EnvReport:
    r = EnvReport()
    r.python = sys.version.split()[0]
    r.os_name = f"{platform.system()} {platform.release()}"
    v = tuple(int(x) for x in r.python.split(".")[:2])
    if v < (3, 9):
        r.errors.append(f"python {r.python} < 3.9 required")
    for pkg in list(REQUIRED) + list(OPTIONAL):
        try:
            m = importlib.import_module(pkg)
            r.packages[pkg] = getattr(m, "__version__", "?")
        except ImportError:
            if pkg in REQUIRED:
                r.errors.append(f"missing required package: {pkg}")
            else:
                r.warnings.append(f"optional package missing: {pkg}")
    try:
        import torch
        r.torch_version = torch.__version__
        r.torch_cuda_build = torch.version.cuda or "cpu-only"
        r.cuda_available = torch.cuda.is_available()
        if r.cuda_available:
            r.cuda_version = torch.version.cuda
        elif "+cpu" in r.torch_version:
            r.warnings.append("cpu-only torch build — GPU training needs CUDA build")
    except Exception as e:
        r.errors.append(f"torch import failed: {e}")
    return r

def validate_for_training(require_gpu: bool = False) -> EnvReport:
    r = detect_environment()
    if require_gpu and not r.cuda_available:
        r.errors.append("GPU required but CUDA unavailable")
    return r
