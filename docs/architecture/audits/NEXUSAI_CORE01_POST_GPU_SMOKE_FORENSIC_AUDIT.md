# NexusAI Core-01 — Post-GPU-Smoke Forensic Audit

**Date:** 2026-11-08 · **Base:** `a0ca7ce` + uncommitted repairs · **Mode:** READ-ONLY (reports only, no code changes).

## 1. Executive summary

GPU smoke test **genuinely PASSED** on Colab T4 (user-executed, reported). During it a real device-placement bug surfaced and was patched in Colab (`model.to(device)`). **That fix is NOT in the local repo** — local `pretraining_driver.py` still constructs the model on CPU. This is the single blocking defect for real GPU training.

## 2. Verified facts

| Fact | Evidence |
|---|---|
| Smoke test PASSED (all stages A–H) | user-reported Colab output |
| Model params 8,842,560 on CUDA | smoke Stage C |
| FP16 fwd/bwd/step works, peak ~0.30 GB (bs2×256 probe) | smoke Stage D — NOTE: probe batch, NOT training-config prediction |
| Driver rc=0, ckpts created, strict reload, resume works | smoke Stage F/G |
| Mask fix verified on Colab (sha match) | smoke Stage B |
| Local driver **lacks `model.to(device)`** | `pretraining_driver.py:266` — `model = NexusAICore01(config)` then straight to engine; engine never moves model (`training.py` __init__ has no `.to()`) |
| Engine moves only batch tensors `.to(device)` | `training.py:296-297, 388-389` |
| Optimizer built on `model.parameters()` inside engine | `training.py:221-226` — created AFTER model exists; if model moved before engine construction, params are same objects → safe |
| Checkpoint load uses `map_location="cpu"` + `load_state_dict` | `training.py:185,469` — copies into whatever device params live on → resume safe once model on CUDA |
| GradScaler/AMP correct | `training.py:236-243` |
| Grad accumulation group-size math correct | `training.py:303-311` (Phase 4.2.2 fix) |
| Loss `ignore_index=pad_id`, pre-shifted targets | `transformer.py:370-374`, `dataset.py:452-458` |
| Resume restores model+opt+scheduler+RNG+scaler | `training.py:469-483` |

## 3. Device-mismatch root cause

- Driver resolves `device` (line 174) but never applies it to the model.
- Engine's train loop sends `input_ids`/`targets` to CUDA while model weights stay CPU → `Expected all tensors to be on same device` at embedding.
- **Colab patch** `model = model.to(device)` after constructor is the **correct minimal fix**.
- Ordering is safe: driver constructs model → `.to(device)` → `PretrainingEngine(model,...)` creates AdamW on `model.parameters()` (same param objects, already on CUDA). No re-creation needed.
- Resume: `load_checkpoint` → `model.load_state_dict` on already-CUDA model; optimizer state loads fine. **No additional device handling needed.**

## 4. Colab vs local reconciliation

| Item | Local repo | Colab |
|---|---|---|
| transformer.py mask fix | ✅ present (uncommitted) | ✅ uploaded manually |
| driver `-m` invocation | n/a (docs fixed) | ✅ used |
| **driver `model.to(device)`** | ❌ **MISSING** | ✅ patched by user |
| smoke checkpoint | none | `checkpoints_smoke_retry_20261108_174537` (Drive) |

**Reconciliation needed:** apply the one-line driver fix locally (proposed, NOT applied), commit later with approval. Colab-patched file not in workspace → cannot byte-compare, but user's described patch (`model.to(device)` after constructor) is exactly the minimal correct fix.

## 5. REPAIR APPLIED (owner-approved, 2026-11-08)

**File:** `packages/ai-core/core01/pretraining_driver.py` line 266
```diff
-    model = NexusAICore01(config)
+    model = NexusAICore01(config).to(device)
```
**Backup:** `backups/core01_repair/pretraining_driver.py.<timestamp>.bak`

**Verification executed:**
- `ast.parse` syntax: PASS
- Device-consistency: param device == input device (cpu test): PASS
- Optimizer param-group references model params (same objects): PASS
- CPU driver e2e (`-m`, 300 docs, `--max-steps 2`, fp32): rc=0, loss 9.02→9.02, `checkpoint_step2.pt`+`checkpoint_maxsteps.pt` written: **PASS**
- CUDA device placement: **NOT VERIFIED locally** (no GPU) — verified on Colab smoke (user patch identical)

**Remaining limitation:** `.to(device)` on CUDA path not locally executed; identical change was smoke-verified in Colab.

## 6. Dataset readiness (see companion audit)

- 100M English corpus: on Drive/Kaggle — **NOT locally auditable**; Colab audit cell prepared.
- Bengali/Banglish: repo files ~220KB total — **far too small** for language goals.
- Tokenizer: vocab 8000 verified; Bengali probe 0 UNK; mixed-corpus UNK ~1.06%.

## 7. Smoke-test artifact status

`checkpoints_smoke_retry_20261108_174537` = **smoke artifact, NOT pretrained model**. Preserve as diagnostic; never ship as trained weights.

## 8. Final answers

| Question | Answer |
|---|---|
| Smoke test genuinely passed? | **YES** (user-executed, all stages) |
| Verified? | GPU fwd/bwd/opt/mask/ckpt/resume mechanics |
| Colab device fix correct? | **YES** — minimal, properly ordered |
| Fix in local repo? | **NO — MISSING** |
| Dataset ready for pretraining? | English corpus pending Drive audit; **Bengali NOT sufficient** |
| Bengali/Banglish coverage? | **INSUFFICIENT** (~220KB vs 100M) |
| Tokenizer ready? | **YES** (vocab 8000, coverage verified) |
| Driver ready? | **NO — needs the 1-line device fix** |
| Checkpoint = pretrained model? | **NO — smoke artifact only** |
| Full pretraining now? | **NOT YET — apply driver fix + dataset audit + owner approval** |

## Status: `READY FOR REPAIR APPROVAL` → then dataset audit → then training approval.
