# =============================================================================
# NEXUSAI CORE-01 — COLAB GPU SETUP & VERIFICATION CELL
# Run this FIRST in a Google Colab notebook.
# Safe: installs nothing unless required, never starts training.
# =============================================================================
import subprocess, sys, os, json, platform

R = {"checks": [], "gpu_ready": False}
def rec(name, ok, detail=""):
    R["checks"].append({"check": name, "status": "PASS" if ok else "FAIL",
                        "detail": str(detail)[:300]})
    print(("PASS " if ok else "FAIL ") + name + (" — " + str(detail)[:120] if detail else ""))

print("=== NEXUSAI GPU SETUP ===")
print("python:", sys.version.split()[0], "| os:", platform.system())

# 1. PyTorch + CUDA state
try:
    import torch
    rec("torch import", True, torch.__version__)
    cuda_avail = torch.cuda.is_available()
    rec("torch.cuda.is_available", cuda_avail,
        "False => CPU runtime OR cpu-only torch build")
    if cuda_avail:
        rec("gpu name", True, torch.cuda.get_device_name(0))
        rec("cuda version", True, torch.version.cuda)
        rec("vram GB", True, round(torch.cuda.get_device_properties(0).total_memory/2**30, 1))
        x = torch.randn(512, 512, device="cuda")
        y = (x @ x).sum().item()
        torch.cuda.synchronize(); torch.cuda.empty_cache()
        rec("cuda matmul", y == y, "tensor compute OK")
        R["gpu_ready"] = True
    else:
        print("\n>>> NO GPU DETECTED. If you expected a GPU:")
        print(">>> In Colab: Runtime -> Change runtime type -> T4 GPU -> Save.")
        print(">>> Then RE-RUN this cell. A notebook cannot grant itself a GPU.")
        if "+cpu" in torch.__version__:
            print(">>> torch is a CPU-only build. On a GPU runtime, run:")
            print('>>> !pip uninstall -y torch torchvision && pip install torch --index-url https://download.pytorch.org/whl/cu121')
except Exception as e:
    rec("torch import", False, e)

# 2. Resources
try:
    import psutil
    vm = psutil.virtual_memory()
    rec("RAM GB", True, round(vm.total/2**30, 1))
    du = psutil.disk_usage("/content" if os.path.exists("/content") else ".")
    rec("disk free GB", True, round(du.free/2**30, 1))
except Exception as e:
    rec("resources", False, e)

# 3. VRAM fit estimate for Core-01 Run4 (model 8.8M, bs8 x accum4, seq512, fp16)
#    params fp32 master ~35MB + AdamW ~70MB + activations ~1-2GB => T4 16GB ample
if R["gpu_ready"]:
    free = torch.cuda.mem_get_info(0)[0]/2**30
    rec("VRAM free GB >= 6", free >= 6, f"{free:.1f} GB free")
    R["vram_free_gb"] = round(free, 1)

R["status"] = "GPU_READY" if R["gpu_ready"] else "GPU_NOT_AVAILABLE"
print("\n==== GPU PREFLIGHT:", R["status"], "====")
print(json.dumps(R, indent=1)[:800])
# DO NOT proceed to training unless status == GPU_READY
