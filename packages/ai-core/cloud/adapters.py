"""Cloud provider adapters — consistent interface, honest capability."""
import os, sys, subprocess, platform
from dataclasses import dataclass, field

@dataclass
class ProviderInfo:
    name: str
    detected: bool = False
    gpu_expected: bool = False
    persistent_storage: str = ""
    notes: list = field(default_factory=list)

class CloudAdapter:
    """Base adapter interface."""
    name = "generic"
    def detect(self) -> ProviderInfo:
        raise NotImplementedError
    def workspace(self) -> str:
        return os.getcwd()
    def persistent_dirs(self) -> list:
        return []

class ColabAdapter(CloudAdapter):
    name = "google-colab"
    def detect(self):
        p = ProviderInfo(self.name)
        # robust: linux + /content dir (avoid false positive on Windows)
        p.detected = (sys.platform.startswith("linux")
                      and os.path.isdir("/content"))
        p.gpu_expected = True   # user selects runtime; may still be CPU
        p.persistent_storage = "/content/drive/MyDrive" if os.path.isdir("/content/drive/MyDrive") else ""
        if not p.persistent_storage:
            p.notes.append("Drive not mounted — mount via Drive icon or drive.mount()")
        return p

class KaggleAdapter(CloudAdapter):
    name = "kaggle"
    def detect(self):
        p = ProviderInfo(self.name)
        p.detected = os.path.isdir("/kaggle")
        p.gpu_expected = True
        p.persistent_storage = "/kaggle/working (ephemeral per session)"
        return p
    def workspace(self):
        return "/kaggle/working" if os.path.isdir("/kaggle/working") else os.getcwd()

class GenericAdapter(CloudAdapter):
    name = "generic-linux"
    def detect(self):
        p = ProviderInfo(self.name)
        p.detected = os.name == "posix"
        p.persistent_storage = os.getcwd()
        return p

def detect_provider() -> ProviderInfo:
    for cls in (ColabAdapter, KaggleAdapter, GenericAdapter):
        a = cls()
        info = a.detect()
        if info.detected:
            info.notes.insert(0, f"adapter={cls.name}")
            return info
    return ProviderInfo("unknown", detected=False)
