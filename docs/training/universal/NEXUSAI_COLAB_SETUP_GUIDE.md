# Google Colab Setup Guide (primary training environment)

## One-cell workflow
Run `docs/notebooks/COLAB_UNIVERSAL_SETUP_CELL.py` as a single Colab cell.
It performs, in order:
1. Drive mount (browser auth once)
2. ZIP locate under MyDrive//content (exact-size filter)
3. SHA-256 verify vs pinned `f20d38ee…`
4. testzip + path-safety + extract to `/content/nexusai_pkg`
5. MANIFEST.json + payload hash verification
6. Full checkpoint SHA-256 (`ad515cade…`)
7. Dependency check (torch/sentencepiece/numpy/psutil)
8. CUDA/GPU detection + real matmul
9. Model strict-load + resume-state inspection
10. Synthetic forward+backward dry-run
11. Dataset + tokenizer presence checks
12. JSON report → `/content/nexusai_reports/`

## Verdicts
- `READY` — all critical checks pass (still needs human authorization)
- `BLOCKED` — one or more FAIL; fix and re-run (idempotent)

## Epoch semantics (verified in driver)
`--epochs` is TOTAL target. Run3 ended at epoch 3. `EPOCHS=5` →
`range(3,5)` = 2 additional epochs. Scheduler/optimizer/RNG all resume.

## If GPU missing
Runtime → Change runtime type → T4 GPU → re-run cell.
Never proceed on CPU runtime for real training.

## Status
Local logic: TESTED (syntax + all branches reviewed).
Live Colab/GPU: NOT TESTED — requires your session.
