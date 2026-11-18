# NexusAI Four-Core Release Report

**Release:** four-core stabilization · **Date:** 2026-11-18 · **Base HEAD:** `cb289fb`

## What this release contains

1. **Verified model inventory** — all four cores + legacy medium: strict load PASS, SHA-256 PASS, param counts verified.
2. **Three minimal repairs** (see `audits/NEXUSAI_FOUR_CORE_REPAIR_REPORT.md`):
   - F2 falsy sampling-param bug in `transformer.py` + `inference.py`.
   - F3 batch-unsafe EOS exit in `transformer.py`.
   - Q4 stale `expected_params` for nexus-medium in `model_registry.py`.
3. **Missing config packages committed** — `models/nexusai_core_02|03|04/` were untracked but required at runtime.
4. **Reproducible verification assets** — `evaluation/verify_four_core_generation.py`, `evaluation/four_core_test_suite.py`, `tests/four_core/test_generation_repairs.py`, `eval_reports/*.json`.
5. **Complete audit documentation** — forensic audit, repair report, test/benchmark report, checkpoint inventory, this release report, plus Stage-1/Stage-2 diagnosis docs.
6. **Previously approved Phase B+C changes** now committed: `model_config.py` enum fix, `inference.py` prompt/EOS/inference-mode fixes, `pretraining_driver.py` zero-step guard, `COLAB_RUN4_TRAIN_CELL.py` authorization/hash/resume guards, `production/current.json` Core-01 designation, README rewrite.

## Release gates

| Gate | Status | Evidence |
|---|---|---|
| A Repository safety | PASS | selective staging; no secrets (`.env` gitignored, never read); backups in `backups/` |
| B Model integrity | PASS | strict loads 0/0 keys all cores; SHA-256 validated; params match |
| C Functional integrity | PASS | all cores independently callable via registry; neural_only routing verified live |
| D Quality/regression | PASS w/ disclosures | 6/6 repair tests; suite failures are model-quality limits, documented — no code regressions |
| E Security | PASS | no secrets committed; no DB/schema changes; no external AI dependencies |
| F Documentation | PASS | this file + 6 audit docs + README |

## Explicit non-claims

- No core is a working conversational model. Core-03 math accuracy 9.2% on held-out; core-02 template-bound; core-01 undertrained; core-04 narrow memorization.
- No training was run. No checkpoint weights were modified. Dataset V5 was not constructed.
- Checkpoint weights for core-02/03/04 remain gitignored per policy (`.sha256` committed); they are distributed out-of-band.

## Rollback

- File-level: `backups/20261118_223409_fourcore_repair/` (pre-change copies of all modified files).
- Git-level: `git revert <release-sha>` or reset to `cb289fb`.

## Next recommended missions (separate authorization required)

1. Dataset V5 completion (the documented Core-05 blocker).
2. Core-01 Run4/Run5 SFT to fix the chat-prompt EOS problem (F1).
3. Core-02/03/04 SFT data de-duplication + retraining (Q1–Q3).
