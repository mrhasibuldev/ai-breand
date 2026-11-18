# NEXUSAI RUN4 — START_EPOCH BUGFIX REPORT

**Date:** 2026-11-10 · Scope: ONLY the START_EPOCH fix · No training authorized/started

## Root cause
`COLAB_RUN4_TRAIN_CELL.py` line 68 built the post-training `rep` dict referencing `START_EPOCH`, which was never assigned → `NameError` after `subprocess.run` completed (training + checkpoints unaffected; only the JSON report failed).

## Actual variable inspection
- Checkpoint dict variable: **`ck`** (line 45: `ck = torch.load(SRC_CKPT, ...)`)
- `ck` is **deleted at line 51** (`del ck`) → START_EPOCH had to be captured BEFORE the delete
- First-use site: line 68 (`"start_epoch": START_EPOCH`)

## Exact change
File: `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` (only file modified)

```diff
-START_STEP = ck["step"]; print("resume ckpt: step=%s epoch=%s status=%s tl=%s vl=%s" % (
+START_STEP = ck["step"]; START_EPOCH = ck.get("epoch", 0)
+print("resume ckpt: step=%s epoch=%s status=%s tl=%s vl=%s" % (
     ck.get("step"), ck.get("epoch"), ck.get("model_status"),
     ck.get("train_loss"), ck.get("val_loss")))
 del ck
```
`START_EPOCH = ck.get("epoch", 0)` inserted at line 48 — after `ck` load (45), before `del ck` (52), before first use (69). Uses the actual loaded dict; no duplicate checkpoint load; no training-logic change.

## Verification
- Python `ast.parse`: **syntax OK**
- Static assignment check: START_STEP, START_EPOCH, RESUME_SRC, OUT_DIR, TRAIN, EPOCHS, MAX_STEPS, rep all assigned ✅
- Order verified: define(48) → del ck(52) → use(69) ✅
- `git diff --stat`: 1 file, +2/-1 ✅

## Files confirmed unchanged
Run3 ckpt, corpus_train.jsonl, tokenizer, model config, hyperparams, resume/save logic, all other project files — untouched. No training started, no GPU loop run, no checkpoint written, no commit/push.

## Remaining limitations
- Cell not executed end-to-end (would start training — not authorized). Runtime verification pending owner's Colab run.
- Run4 still NOT training-ready by itself — awaits corpus upload + Colab execution + separate approval.

## Verdict: **FIXED AND VERIFIED** (static/safe checks only)
