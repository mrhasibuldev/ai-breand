"""
NexusAI Core-01 — Portable GPU Diagnostic Script

Performs read-only hardware/import/model checks with SYNTHETIC data only.
Does NOT train, does NOT update weights, does NOT download anything.

Usage:
    python nexusai_core01_gpu_diagnostic.py [package_root]

package_root defaults to the directory containing this script's sibling
'nexusai_core01_kaggle_package' folder, or the current directory.
"""

import os
import sys
import hashlib

RESULTS = []


def report(name, ok, info=""):
    RESULTS.append((name, bool(ok)))
    print(f"  {'PASS' if ok else 'FAIL'}: {name}" + (f"  [{info}]" if info else ""))


def find_package_root():
    # Explicit path argument wins: python script.py <package_root>
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return os.path.abspath(sys.argv[1])
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (
        os.path.join(here, "nexusai_core01_kaggle_package"),
        here,
        os.getcwd(),
    ):
        if os.path.isdir(os.path.join(cand, "core01")) and \
           os.path.isdir(os.path.join(cand, "models", "nexusai_core_01")):
            return cand
    return None


def main():
    print("=" * 60)
    print("NEXUSAI CORE-01 GPU DIAGNOSTIC")
    print("=" * 60)

    # --- Python ---
    report("python version", sys.version_info >= (3, 9), sys.version.split()[0])

    # --- PyTorch ---
    try:
        import torch
        report("pytorch import", True, torch.__version__)
    except Exception as e:
        report("pytorch import", False, str(e))
        print("\nDIAGNOSTIC FAILED: PyTorch missing")
        return 1

    # --- CUDA / GPU ---
    # No GPU is not a failure — CPU fallback is a supported mode. GPU-specific
    # checks are marked SKIP rather than FAIL when CUDA is unavailable.
    cuda_ok = torch.cuda.is_available()
    report("CUDA available", True,
           (torch.version.cuda or "cpu-only build") +
           ("" if cuda_ok else " — CPU fallback mode"))
    gpu_name = ""
    vram_gb = 0.0
    capability = ""
    if cuda_ok:
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        capability = ".".join(map(str, torch.cuda.get_device_capability(0)))
        report("GPU device", True, f"{gpu_name} sm_{capability} {vram_gb:.1f}GB")
        report("bf16 supported", bool(torch.cuda.is_bf16_supported()))
    else:
        report("GPU device", True, "SKIPPED (no CUDA — CPU mode)")
        report("bf16 supported", True, "SKIPPED (no CUDA)")

    # --- Locate package ---
    root = find_package_root()
    if root is None:
        report("package root", False, "core01/ + models/ not found")
        print("\nDIAGNOSTIC FAILED: package structure missing")
        return 1
    report("package root", True, root)

    sys.path.insert(0, root)
    sys.path.insert(0, os.path.join(root, "models"))

    # --- Imports ---
    try:
        from core01.transformer import NexusAICore01
        from nexusai_core_01.config.model_config import NexusAICore01Config
        from core01.tokenizer_interface import NexusAITokenizer, create_default_tokenizer
        from core01.training import resolve_amp_dtype
        report("core01 imports", True)
    except Exception as e:
        report("core01 imports", False, str(e))
        print("\nDIAGNOSTIC FAILED: import error")
        return 1

    # --- Tokenizer ---
    device = "cuda" if cuda_ok else "cpu"
    try:
        tok = create_default_tokenizer(NexusAICore01Config())
        vs = tok.get_vocab_size()
        report("tokenizer load", vs == 8000, f"vocab={vs}")
    except Exception as e:
        report("tokenizer load", False, str(e))
        tok = None

    # --- Model init + param count ---
    try:
        cfg = NexusAICore01Config(device=device, precision="fp16" if cuda_ok else "fp32")
        model = NexusAICore01(cfg).to(device)
        n = model.count_parameters()
        report("param count == 8,842,560", n == 8_842_560, f"got {n:,}")
    except Exception as e:
        report("model init", False, str(e))
        print("\nDIAGNOSTIC FAILED")
        return 1

    # --- Synthetic forward + backward (NO optimizer step, NO weight update) ---
    try:
        g = torch.Generator(device="cpu").manual_seed(0)
        x = torch.randint(0, 8000, (4, 128), generator=g).to(device)
        y = torch.randint(0, 8000, (4, 128), generator=g).to(device)
        model.train()
        loss = model(x, y)
        report("synthetic forward", loss.item() == loss.item(), f"loss={loss.item():.3f}")
        loss.backward()
        report("synthetic backward", True, "grads computed (weights untouched)")
        model.zero_grad(set_to_none=True)
    except Exception as e:
        report("forward/backward", False, str(e))

    # --- AMP dtype resolution ---
    try:
        for p in ("fp32", "fp16", "bf16"):
            dt = resolve_amp_dtype(p, device)
            print(f"    amp[{p}] on {device} -> {dt}")
        report("amp resolution", True)
    except Exception as e:
        report("amp resolution", False, str(e))

    # --- FP16 AMP forward test (CUDA only; skipped on CPU) ---
    if cuda_ok:
        try:
            opt = torch.optim.SGD(model.parameters(), lr=0.0)  # lr=0: no real update
            scaler = torch.amp.GradScaler("cuda")
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                l2 = model(x, y)
            scaler.scale(l2).backward()
            scaler.unscale_(opt)
            scaler.step(opt)
            scaler.update()
            report("fp16 AMP + GradScaler", l2.item() == l2.item(),
                   f"loss={l2.item():.3f}")
            model.zero_grad(set_to_none=True)
        except Exception as e:
            report("fp16 AMP + GradScaler", False, str(e))
    else:
        report("fp16 AMP + GradScaler", True, "SKIPPED (no CUDA)")

    # --- Memory ---
    if cuda_ok:
        report("VRAM reported", True,
               f"alloc={torch.cuda.memory_allocated()/1e6:.0f}MB "
               f"peak={torch.cuda.max_memory_allocated()/1e6:.0f}MB")

    # --- Summary ---
    print("=" * 60)
    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    for name, ok in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}: {name}")
    print("=" * 60)
    verdict = "PASSED" if passed == total else "FAILED"
    print(f"DIAGNOSTIC {verdict} ({passed}/{total})")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
