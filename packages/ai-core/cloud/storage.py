"""Provider-independent storage: local paths, Drive mount detection."""
import os, shutil, hashlib
from dataclasses import dataclass, field

@dataclass
class StorageReport:
    roots: dict = field(default_factory=dict)   # name -> path
    writable: dict = field(default_factory=dict)
    drive_mounted: bool = False
    errors: list = field(default_factory=list)

def default_roots() -> dict:
    roots = {"workspace": os.getcwd(), "tmp": "/tmp" if os.name != "nt" else os.environ.get("TEMP", ".")}
    # Colab Drive
    drive = "/content/drive/MyDrive"
    if os.path.isdir(drive):
        roots["gdrive"] = drive
    # Kaggle
    for p in ("/kaggle/working", "/kaggle/input"):
        if os.path.isdir(os.path.dirname(p)):
            roots.setdefault("kaggle", "/kaggle")
            break
    return roots

def probe_storage() -> StorageReport:
    r = StorageReport()
    r.roots = default_roots()
    r.drive_mounted = "gdrive" in r.roots
    for name, path in r.roots.items():
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, ".nexusai_write_test")
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
            r.writable[name] = True
        except Exception as e:
            r.writable[name] = False
            r.errors.append(f"{name} ({path}) not writable: {e}")
    return r

def sha256_file(path: str, chunk: int = 1 << 22) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(chunk), b""):
            h.update(c)
    return h.hexdigest()
