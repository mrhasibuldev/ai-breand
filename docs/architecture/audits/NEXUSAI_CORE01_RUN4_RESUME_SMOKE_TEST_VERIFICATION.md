# NexusAI Core-01 Run4 — Resume Smoke Test Verification Report

**Date:** 2026-11-11
**Scope:** Controlled one-optimizer-step resume smoke test of the real Run3
checkpoint through the actual production resume path. NOT full Run4 training.

## 1. Initial blocker

Resume flow was `RESUME_FLOW_PARTIALLY_VERIFIED`: the full chain was proven by
static AST + `CheckpointManager` synthetic tests, but the real Run3 checkpoint
had never been loaded through `PretrainingEngine.load_checkpoint`, and no
optimizer step had ever been executed from restored state.

## 2. Source files inspected (read-only)

| Stage | Path | Lines |
|---|---|---|
| Subprocess command (`--resume`, `RESUME_SRC`) | `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` | ~55–65 |
| Arg parser (`--resume`) | `packages/ai-core/core01/pretraining_driver.py` | 160–163 |
| Resume call | `pretraining_driver.py` | ~315–318 |
| `PretrainingEngine.load_checkpoint` | `packages/ai-core/core01/training.py` | 453–486 |
| `CheckpointManager.load/save` | `training.py` | 131–190 |
| `TrainingCheckpoint` fields | `training.py` | 101–115 |
| Optimizer step / `current_step += 1` | `training.py` (`train_epoch`) | ~340–356 |
| `save_checkpoint` (rng/scaler capture) | `training.py` | 406–449 |
| Model class | `core01/transformer.py` | 244 |

## 3. Run3 checkpoint compatibility audit

File: `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt`
- size `106,777,501` B — sha256 `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` ✅
- Format: `dict` → `TrainingCheckpoint(**data)` — all 12 dataclass fields present ✅
- `epoch=3`, `step=1341`, `model_status=PRETRAINING_COMPLETED`, losses 4.426/4.217 ✅
- Arch: d_model=256, n_layers=6, n_heads=8, d_ff=1024, max_len=512, vocab=8000 — matches Run4 config ✅
- model_state_dict: 100 tensors, ~8.97M elements (8,842,560 params counted by model) ✅
- optimizer_state_dict (AdamW state+param_groups) present ✅
- scheduler_state_dict present (`last_epoch=1341`) ✅
- grad_scaler_state_dict present (fp16 scale=65536) — CPU/fp32 path skips scaler by design ✅
- rng_state: python/numpy/torch_cpu/torch_cuda ✅
- tokenizer_path recorded (Colab path; local equivalent verified at `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`)

**Known limitation:** scheduler `lr_lambda` is rebuilt at engine init with Run4
`num_training_steps`; `last_epoch`/LR state restores correctly, but the warmup
decay curve endpoint differs from Run3's original schedule. Warmup is only
100 steps and step 1341 >> warmup, so practical impact is nil, but it is
documented, not hidden.

## 4. Changes made

- `docs/notebooks/COLAB_RUN4_PREFLIGHT_CELL.py` — added `external_verification`
  evidence block (corpus identity, resume flow, compatibility, smoke test,
  integrity, authorization flags). No check logic weakened.
- This report. No other repo file touched by this task.

## 5. Synthetic tests (Phase D) — via `PretrainingEngine`/`CheckpointManager`

| Test | Result |
|---|---|
| D1 synthetic save→load round-trip (epoch/step/weights) | PASS |
| D2 missing checkpoint → `FileNotFoundError` | PASS |
| D3 corrupt checkpoint → `UnpicklingError` | PASS |
| D4 incompatible model state → `RuntimeError` (strict load) | PASS |

## 6. Real Run3 resume smoke test (Phase E) — exactly ONE optimizer step

Environment: Windows CPU, `device=cpu`, `precision=fp32` (GradScaler=None —
scaler-restore branch verified in source, not exercised; documented).
Run3 ckpt **copied** to temp dir (original opened read-only, never written).

| Step | Evidence |
|---|---|
| Pre-step state | `current_step=0, current_epoch=0` |
| `engine.load_checkpoint('run3_copy.pt')` | `epoch=3, step=1341` restored (0.6 s) |
| Model params | `8,842,560` |
| Scheduler | `last_epoch=1341` restored |
| One step (mirrors `train_epoch` inner update: zero_grad→forward→backward→clip→step→scheduler→`current_step+=1`) | loss=12.4020 finite, all grads finite, **step 1341→1342**, 99 tensors changed |
| Temp checkpoint | `smoke_step.pt`, 106,770,075 B, sha256 `f7236ce35580ed33…`, `model_status=PRETRAINING_IN_PROGRESS` (finalize=False — honest) |
| Temp reload (fresh engine+model) | `step=1342, epoch=3`, all weights identical |

Optimizer-step accounting: exactly one `optimizer.step()` call, one
`current_step` increment, no epoch loop, no `--max-steps` run, no retry.

## 7. Post-test integrity (Phase F)

- Original Run3 ckpt: sha256 pre == post (`ad515cade…`) ✅
- Corpus `corpus_train.jsonl`: sha256 `5f8572ed…28376`, size 385,217,021 — unchanged ✅
- Run4 ZIP: sha256 `f91411e1…82b4a5`, size 299,476 — unchanged ✅
- Temp artifacts: `C:\Users\Nusaiba\AppData\Local\Temp\nexusai_smoke_q85un1g7\` (smoke_step.pt, run3_copy.pt, smoke_result.json) — preserved as evidence; safe to delete.
- **Machine-readable evidence persisted:** `eval_reports/nexusai_run4_resume_smoke_evidence.json` (2,932 B, sha256 `0cb7588d7f2e7afe2e5250dd9381f3c37e1940428cb060477929bb1338523f32`). The V6 preflight checker validates this file field-by-field against trusted constants; missing/malformed/inconsistent evidence → `BLOCKED`. For Colab, upload this JSON to the Drive `NexusAI/` folder alongside the ZIP.

## 8. Final verdicts

- `CORPUS_IDENTITY_VERIFIED` — direct streamed hash match.
- `RESUME_FLOW_VERIFIED_BOUNDED_SMOKE` — real checkpoint loads through the
  actual production path; exactly one optimizer step completed; temp
  checkpoint saves and reloads. **This is NOT full Run4 training verification.**
- `checkpoint_compatibility_status`: COMPATIBLE (with documented scheduler
  lambda caveat).
- Checker updated: sha256 `ec50ef277c2f520e6884246c354cbf71bce12deeb7337b70ddc644f590465ad4`, 24,578 B, compile OK.

## 9. Remaining limitations

- Smoke test ran CPU/fp32; Colab will run fp16+GradScaler+CUDA. Scaler state
  restore is implemented (`training.py:480-482`) but untested on GPU.
- Scheduler LR-lambda rebuilt with Run4 step budget (see §3).
- Full multi-epoch training, data pipeline at scale, and Colab environment
  remain unverified — that is what the preflight + training run will exercise.

## 10. Next approved action

User may run the V5 preflight cell in Colab, review the Drive report, and then
explicitly authorize Run4 training. This smoke test does not authorize it.
