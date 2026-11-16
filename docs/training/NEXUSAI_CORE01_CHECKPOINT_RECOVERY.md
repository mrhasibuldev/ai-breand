# NexusAI Core-01 — Checkpoint Recovery Guide

## Authoritative checkpoint (FOUND — verified)
| Field | Value |
|---|---|
| Path (repo) | `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt` |
| Size | 106,777,501 bytes |
| SHA-256 | `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` |
| Epoch / step | 3 / 1341 |
| Status | PRETRAINING_COMPLETED |
| Storage | **Git LFS** (file exceeds GitHub's 100MB blob limit) |
| Manifest | `CHECKPOINT_MANIFEST.json` (same directory) |

## Why Git LFS
106.8MB > GitHub 100MiB per-file limit → stored as LFS object.
Pointer committed; real bytes on LFS storage.

## Retrieve on Colab (no ZIP upload needed)
```python
# run docs/notebooks/COLAB_CLONE_RECOVERY_CELL.py as one cell
```
It: installs git-lfs → clones repo (uses Colab Secret `GITHUB_TOKEN` if
private) → `git lfs pull` for the checkpoint only → verifies size+SHA-256 →
safe-loads checkpoint → checks tokenizer vocab=8000.

Manual equivalent:
```bash
git clone https://github.com/mrhasibuldev/ai-breand.git
cd ai-breand && git lfs pull --include "packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt"
sha256sum packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt
# must equal ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830
```

## Loading notes
- Use `torch.load(..., weights_only=False)` — checkpoint contains numpy RNG
  state that `weights_only=True` rejects. File is hash-verified → trusted.
- Key family `transformer_blocks.*` = Core-01. `transformer.layers.*` =
  phase10 experimental — DO NOT substitute.
- Resume restores model+optimizer+scheduler+GradScaler+RNG.
