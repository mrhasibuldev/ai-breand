"""Unified preflight — one call, full environment verdict."""
from dataclasses import dataclass, field
from .env_manager import detect_environment, validate_for_training
from .hardware import probe_hardware, check_training_fit
from .storage import probe_storage
from .adapters import detect_provider
from .model_loader import load_core01
from .dataset_manager import inspect_jsonl
import os

@dataclass
class Check:
    name: str
    status: str          # PASS/WARN/FAIL/BLOCKED/NOT_TESTED
    detail: str = ""

@dataclass
class PreflightReport:
    provider: str = ""
    checks: list = field(default_factory=list)
    ready_for_training: bool = False
    notes: list = field(default_factory=list)

    def add(self, name, status, detail=""):
        self.checks.append(Check(name, status, str(detail)[:250]))
        print(f"[{status:>10}] {name} — {str(detail)[:120]}")

def run_preflight(repo_root: str, checkpoint: str = None,
                  dataset: str = None, require_gpu: bool = False,
                  dataset_sha: str = None, dataset_records: int = None
                  ) -> PreflightReport:
    rep = PreflightReport()

    # provider
    prov = detect_provider()
    rep.provider = prov.name
    rep.add("provider", "PASS" if prov.detected else "WARN", prov.name)

    # environment
    env = detect_environment()
    rep.add("python", "PASS" if env.ok() else "FAIL",
            f"{env.python} torch={env.torch_version}")
    for e in env.errors:
        rep.add("env_error", "FAIL", e)
    for w in env.warnings:
        rep.add("env_warn", "WARN", w)

    # hardware
    hw = probe_hardware(repo_root)
    if hw.gpu_available:
        rep.add("gpu", "PASS", f"{hw.gpu_name} {hw.vram_total_gb}GB")
    elif require_gpu:
        rep.add("gpu", "FAIL", "required but unavailable")
    else:
        rep.add("gpu", "WARN", "no GPU — CPU mode")
    for w in check_training_fit(hw):
        rep.add("resources", "WARN", w)

    # storage
    st = probe_storage()
    rep.add("storage", "PASS" if any(st.writable.values()) else "FAIL",
            ", ".join(f"{k}:{'w' if v else 'ro'}" for k, v in st.writable.items()))
    rep.add("drive", "PASS" if st.drive_mounted else "WARN",
            "mounted" if st.drive_mounted else "not mounted")

    # model
    if checkpoint:
        lr = load_core01(checkpoint)
        if lr.ok:
            rep.add("checkpoint", "PASS",
                    f"ep{lr.epoch}/step{lr.step} params={lr.params:,} "
                    f"sha={lr.sha256[:12]}")
        else:
            rep.add("checkpoint", "FAIL", "; ".join(lr.errors))
    else:
        rep.add("checkpoint", "NOT_TESTED", "no path given")

    # dataset (optional — hash only if provided; full scan optional)
    if dataset:
        dr = inspect_jsonl(dataset, expected_sha=dataset_sha,
                           expected_records=dataset_records)
        rep.add("dataset", "PASS" if not dr.errors else "FAIL",
                f"{dr.records} rec, {dr.size/2**20:.0f}MB" if dr.exists else "missing")
        for e in dr.errors[:3]:
            rep.add("dataset_err", "WARN", e)
    else:
        rep.add("dataset", "NOT_TESTED", "no path given")

    rep.ready_for_training = not any(c.status == "FAIL" for c in rep.checks)
    rep.add("verdict",
            "PASS" if rep.ready_for_training else "FAIL",
            "READY FOR TRAINING (still requires human authorization)"
            if rep.ready_for_training else "BLOCKED — see failures")
    return rep
