# Universal Cloud Training Architecture

Provider-independent layer in `packages/ai-core/cloud/`:

| Module | Role |
|---|---|
| `env_manager.py` | python/OS/package/torch/CUDA detection + validation |
| `hardware.py` | GPU name/VRAM, RAM, disk, fit-check vs training needs |
| `storage.py` | workspace/tmp/Drive/Kaggle roots + write tests + sha256 |
| `adapters.py` | Colab / Kaggle / Generic-Linux detection (honest: no false GPU claims) |
| `model_loader.py` | strict Core-01 load: family check, strict state-dict, param count, metadata |
| `dataset_manager.py` | JSONL integrity: size/SHA/records/malformed/empty |
| `preflight.py` | single `run_preflight()` → PASS/WARN/FAIL/BLOCKED/NOT_TESTED verdict |

Design rule: adapters expose detection+paths only; training logic stays in
existing `core01/` (untouched). No provider is claimed supported until its
adapter detects correctly — Colab/Kaggle implemented, GCP-VM = generic-linux.
