# NEXUSAI CORE-01 — RUN4 FINAL GPU PREFLIGHT REPORT

**Date:** 2026-11-10 · READ-ONLY · No training executed · No files modified

## Verdicts
| Check | Verdict |
|---|---|
| Run3 checkpoint compatibility | **READY** — strict-load architecture identical, verified live |
| Tokenizer compatibility | **READY** — same sp_bpe_8k, no regeneration in pipeline |
| Dataset integrity | **READY WITH CONDITIONS** — valid format; token total approximate; 6-fragment leakage noted |
| Training script correctness | **READY WITH CONDITIONS** — one NameError bug in cell report section (post-training only) |
| Colab/GPU readiness | **NOT VERIFIED** — requires live Colab session; T4 assumed, model tiny (8.8M) so memory is non-issue |
| Checkpoint & resume safety | **READY** — atomic saves, full state (opt/sched/rng/scaler), isolated OUT_DIR |
| Evaluation readiness | **READY WITH CONDITIONS** — neural-only suite exists; held-out = corpus val-fraction 0.02 |
| **Overall** | **READY WITH CONDITIONS** |

## Verified facts
- Run3 ckpt: `checkpoints_core01_run3/checkpoint_final.pt`, 106,777,501 B, sha256 `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` ✅
- Contents: 100 tensors, epoch=3, step=1341, train_loss 4.426, val_loss 4.217, status PRETRAINING_COMPLETED, includes optimizer+scheduler+rng+grad_scaler states → faithful resume possible
- Config embedded: d256/6L/8H/ff1024/ctx512/vocab8000/fp16/bs8/accum4/lr3e-4/warmup100 — matches core01 transformer exactly (strict load proven via registry earlier)
- Corpus: `corpus_train.jsonl` 216,193 docs / 385,217,021 B / sha256 `5f8572ed…` / field `text` ✅ / Bengali chars 47.1%
- Cell: asserts run3 step==1341 ✅ (matches), resume priority run4-last→run4-final→run3, OUT_DIR isolated `checkpoints/core01_run4`
- Driver: `load_state_dict` strict (training.py:469), atomic `os.replace` checkpoint saves (training.py:163), resume restores model+optimizer+scheduler+RNG+scaler
- `--resume` absolute path works: `os.path.join(dir, "/abs")` → "/abs" on POSIX ✅

## Conditions (must resolve before/at run)
1. **CELL BUG:** `COLAB_RUN4_TRAIN_CELL.py:68` references `START_EPOCH` — never defined → `NameError` AFTER subprocess finishes. Training+checkpoints unaffected; only the JSON report fails. **Fix: add `START_EPOCH = ck.get("epoch",0)` — needs owner approval to edit cell.**
2. GPU type/RAM unverified until Colab session (expected T4; 8.8M model fp16 ≈ trivial memory).
3. Corpus token count is char-estimated (~53M); exact tokenizer count pending.
4. Val split = 2% of corpus (~4.3K docs) held out by driver; reasoning_test 300 held-out known to have 6 generic-fragment overlaps (documented).

## Risks
- Colab disconnect → resume-safe (checkpoint_last.pt every epoch-end + step ckpts every 100)
- Bengali-heavy corpus → possible mild EN regression (mitigated: ~56% EN-dominant docs)
- Template reasoning data → limited reasoning gain expected

## Recommended next action
Owner approves 1-line cell fix (`START_EPOCH`) → upload corpus to Drive → run cell → download `checkpoint_final.pt` → I run neural-only eval vs run3.
