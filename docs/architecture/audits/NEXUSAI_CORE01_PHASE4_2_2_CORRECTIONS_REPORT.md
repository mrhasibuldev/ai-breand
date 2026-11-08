# NEXUSAI_CORE01_PHASE4_2_2_CORRECTIONS_REPORT

**Date**: 2026-11-06
**Type**: CONTROLLED CORRECTIVE PHASE — two verified issues fixed, no training/GPU/downloads

---

## 1. EXECUTIVE SUMMARY

- **Issue 1 (gradient accumulation)**: FIXED — final partial groups now divide by actual group size. Mathematically exact (`allclose`, maxdiff ~1e-9) across 7 test cases.
- **Issue 2 (tokenizer_path)**: FIXED — populated from new `config.tokenizer_path` field or explicit engine arg; warns on load when absent; old checkpoints still load.
- Param count unchanged: **8,842,560** (VERIFIED).
- Tests: **12/12 new + 23/23 Phase-4.2 + 9/9 regression = 44/44 PASS**.
- Architecture, tokenizer, legacy checkpoints untouched.

## 2. ORIGINAL ISSUES & ROOT CAUSES

| Issue | Root cause |
|---|---|
| Partial-group gradient under-scaling (measured 2/3) | `scaled_loss = loss / accum_steps` used nominal steps for every micro-batch; final group of size k<N got factor 1/N instead of 1/k |
| `tokenizer_path` always empty | `config.to_dict()` had no `tokenizer_path` field → `.get(...,"")` returned `""` always |

## 3. FILES MODIFIED

- `packages/ai-core/core01/training.py` — group-size scaling in both engines; `tokenizer_path` init arg + save/load warning
- `packages/ai-core/models/nexusai_core_01/config/model_config.py` — new `tokenizer_path: str = ""` field + `to_dict` entry
- `packages/ai-core/core01/__init__.py` — unchanged this phase (helpers already exported)

Backups in `/tmp/phase422_backup/` (outside repo).

## 4. GRADIENT ACCUMULATION CORRECTION — FIXED / TESTED

Both `PretrainingEngine.train_epoch` and `InstructionTuningEngine.train_epoch` now compute per-batch:

```python
group_start = (batch_idx // accum_steps) * accum_steps
group_end   = min(group_start + accum_steps, num_batches_total)
group_size  = group_end - group_start
scaled_loss = loss / group_size
```

Full groups unchanged (`group_size == accum_steps`). Partial final group divides by its true size → gradient = exact group mean.

**Mathematical verification** (dropout=0, SGD lr=0 frozen weights, `output_layer.weight` compared with `torch.allclose atol=1e-5`):

| batches | accum | last group | steps | result |
|---|---|---|---|---|
| 8 | 3 | 2 | 3 | allclose, maxdiff 0 |
| 7 | 3 | 1 | 3 | allclose, maxdiff 0 |
| 2 | 3 | 2 | 1 | allclose, maxdiff 0 |
| 6 | 3 | 3 (full) | 2 | allclose, ~7e-9 |
| 5 | 3 | 2 | 2 | allclose, maxdiff 0 |
| 4 | 2 | 2 | 2 | allclose, maxdiff 0 |
| 3 | 3 | 3 (full) | 1 | allclose, ~7e-9 |

Scheduler steps == optimizer steps verified (3==3). No micro-batch skipped/duplicated.

## 5. TOKENIZER PATH CORRECTION — FIXED / TESTED

- `NexusAICore01Config.tokenizer_path: str = ""` added (default empty → backward compatible).
- Engine `__init__(..., tokenizer_path=None)`: explicit arg wins, else `config.tokenizer_path`.
- `save_checkpoint` writes `self.tokenizer_path` (was hardcoded `""`).
- `load_checkpoint` prints clear warning when checkpoint lacks `tokenizer_path`.
- No tokenizer files copied/moved; vocab/special IDs unchanged.

**Tests**: config-path checkpoint round-trip PASS; explicit-arg override PASS; SFT engine path PASS; old checkpoint without field loads with warning PASS.

## 6. BACKWARD COMPATIBILITY — VERIFIED

- Old checkpoint dicts (no `rng_state`/`tokenizer_path` keys) load via dataclass defaults — TESTED.
- `from_dict` on old config dicts → new fields get defaults (`fp32`, accum 1, `tokenizer_path=""`) — TESTED earlier.
- `weights_only=False` retained with existing comment; no security weakening.
- Atomic `.tmp`→`os.replace` writes retained; `.backup` policy retained; legacy dirs untouched.

## 7. TEST COMMANDS & RESULTS

| Command | Result |
|---|---|
| `python -m py_compile core01/training.py model_config.py` | PASS |
| `python %TEMP%/test_phase422.py` | **12/12 PASS** |
| `python %TEMP%/test_phase42.py` | **23/23 PASS** |
| `python test_core01.py` | **9/9 PASS** |
| Param count re-check | **8,842,560** |

Test file: `C:\Users\Nusaiba\AppData\Local\Temp\test_phase422.py` (synthetic data, CPU, temp dirs only).

## 8. PARAMETER COUNT — VERIFIED

`NexusAICore01(NexusAICore01Config()).count_parameters()` = **8,842,560** post-change. Architecture file `transformer.py` untouched (not in diff).

## 9. GIT STATUS

**Before**: `M core01/__init__.py, core01/training.py, model_config.py, ml-service pyc`; untracked `data/`, audit docs, `docs/guides/`.
**After**: identical set (same 3 source files modified further; no new untracked project files). No commit/push. A stray `nul` file accidentally created by a shell redirect was removed.

## 10. REMAINING RISKS & LIMITATIONS

- GPU/AMP paths still code-reviewed only — **NOT TESTED on CUDA** (Phase 4.3 will verify).
- Sampler/shuffle state still not checkpointed → approximate resume (documented).
- `weights_only=False` trust assumption unchanged — never load foreign .pt files.
- `tokenizer_path` is provenance metadata only — engine does not auto-load the tokenizer.

## 11. PHASE 4.3 READINESS — READY (REQUIRES APPROVAL)

Both verified issues resolved and mathematically proven. Next: Kaggle single-GPU diagnostic (fp16+GradScaler path on T4, ~50-100 synthetic steps, checkpoint write/read on `/kaggle/working`). Requires owner approval + Kaggle account action.

**STOP — awaiting owner decision.**
