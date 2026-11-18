"""Hardware discovery — GPU/CPU/RAM/disk, provider independent."""
import os, shutil
from dataclasses import dataclass, field

@dataclass
class HardwareReport:
    gpu_available: bool = False
    gpu_name: str = ""
    gpu_count: int = 0
    vram_total_gb: float = 0.0
    vram_free_gb: float = 0.0
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    disk_free_gb: float = 0.0
    cpu_count: int = 0
    warnings: list = field(default_factory=list)

def probe_hardware(path: str = ".") -> HardwareReport:
    h = HardwareReport()
    h.cpu_count = os.cpu_count() or 0
    try:
        import torch
        h.gpu_available = torch.cuda.is_available()
        if h.gpu_available:
            h.gpu_count = torch.cuda.device_count()
            p = torch.cuda.get_device_properties(0)
            h.gpu_name = p.name
            h.vram_total_gb = round(p.total_memory / 2**30, 1)
            h.vram_free_gb = round(torch.cuda.mem_get_info(0)[0] / 2**30, 1)
    except Exception as e:
        h.warnings.append(f"torch probe failed: {e}")
    try:
        import psutil
        vm = psutil.virtual_memory()
        h.ram_total_gb = round(vm.total / 2**30, 1)
        h.ram_available_gb = round(vm.available / 2**30, 1)
    except ImportError:
        try:
            h.ram_total_gb = round(
                os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
                / 2**30, 1)
        except Exception:
            pass
    try:
        h.disk_free_gb = round(shutil.disk_usage(path).free / 2**30, 1)
    except Exception:
        pass
    return h

def check_training_fit(hw: HardwareReport,
                       need_vram_gb: float = 6.0,
                       need_ram_gb: float = 8.0,
                       need_disk_gb: float = 5.0) -> list:
    """Return list of warnings (empty = fits)."""
    w = []
    if hw.gpu_available:
        if hw.vram_free_gb and hw.vram_free_gb < need_vram_gb:
            w.append(f"VRAM {hw.vram_free_gb}GB < est {need_vram_gb}GB")
    else:
        w.append("no GPU — training will be very slow; inference OK")
    if hw.ram_available_gb and hw.ram_available_gb < need_ram_gb:
        w.append(f"RAM {hw.ram_available_gb}GB < est {need_ram_gb}GB")
    if hw.disk_free_gb and hw.disk_free_gb < need_disk_gb:
        w.append(f"disk {hw.disk_free_gb}GB < est {need_disk_gb}GB")
    return w
