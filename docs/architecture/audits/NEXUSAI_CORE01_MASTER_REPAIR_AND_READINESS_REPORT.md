# NexusAI Core-01 — Master Repair & Training-Readiness Report

**Date:** 2026-11-08 · **Commit base:** `a0ca7ce` (main) · **Mode:** forensic review + minimal repair + consolidated CPU verification.
**Training: NOT started. No push. Core-01 status: UNTRAINED (random init).**

---

## A. Original findings

| # | Issue | Root cause | Location | Severity |
|---|---|---|---|---|
| 1 | **Attention-mask path crashes** (`RuntimeError: size mismatch`) and had wrong semantics | `expand`/`squeeze` produced `[B,S,S,S]`; mask indexed QUERY positions instead of KEY positions | `transformer.py` forward, old lines 350–358 | **HIGH** (latent — training never passes `attention_mask`, but any padded-batch/inference use crashes) |
| 2 | **Notebook cells would crash**: `out["loss"]`/`out["logits"]` on scalar/tensor returns | `forward()` returns scalar loss tensor (targets) or logits tensor (no targets) — not a dict | Colab notebook Cells 14–15 | **HIGH** (would fail on first GPU verify) |
| 3 | **Driver invocation wrong in notebook**: `python pretraining_driver.py` fails (`relative import`) | driver uses `from .transformer import`; must run as module `python -m core01.pretraining_driver` with cwd=`packages/ai-core` | Colab notebook SMOKE_CMD/FULL_CMD | **HIGH** (smoke/full would fail instantly) |
| 4 | Misleading comment "Shift targets" in forward | targets are pre-shifted by dataset (`block[1:]`); forward does NOT shift — comment only, code correct | `transformer.py` ~line 369 | LOW (doc) |

**Verified NON-issues:** causal mask correct; packed dataset shift/alignment correct; loss `ignore_index=pad_id` correct; EOS-per-doc + doc concatenation correct; grad-accum group-size math correct; GradScaler/AMP correct; checkpoint atomic+backup+scaler+RNG correct; `build_config` override mapping correct (all CLI args verified reaching config); resume works.

## B. Repairs (2 files changed)

| File | Change | Reason |
|---|---|---|
| `packages/ai-core/core01/transformer.py` | Replaced mask block: `pad = attention_mask[:,None,:]`; `causal_mask = causal_mask.unsqueeze(0) * pad` → `[B,S,S]`, key-position semantics | Fix crash + correct padding masking |
| `docs/notebooks/NexusAI_Core01_Google_Colab_Training.ipynb` | Cells 14/15: scalar-loss/logits handling fixed; SMOKE_CMD/FULL_CMD → `-m core01.pretraining_driver`, cwd→`packages/ai-core` | Fix would-be runtime failures |

**Backups:** `backups/core01_repair/transformer.py.bak`, `Colab_Training.ipynb.bak`, `verify_results.json`
**Diff summary:** transformer.py ±10 lines (mask block only); ipynb cell-source patches only. `git diff` available.

## C. Verification — 28/28 PASS + 2 integration runs

| Area | Result |
|---|---|
| Syntax (5 core files) | PASS |
| Imports + config (6L/8H/256/1024/512/vocab8000) | PASS |
| Tokenizer (vocab 8000, IDs 0/1/2/3, roundtrip, range) | PASS |
| Param count **8,842,560** (live instantiation) | PASS |
| Forward → finite loss (9.08 init), logits `[B,512,8000]` | PASS |
| Backward → all grads finite; AdamW step updates weights | PASS |
| Causal mask lower-triangular | PASS |
| **attention_mask path** (previously crashed) | PASS — now `[B,S,S]`, key-masking verified |
| Packed dataset: keys/shapes/shift-alignment/pad-ignore | PASS |
| Checkpoint save → fields (model/opt/scheduler/RNG/scaler/status/tokenizer) → strict reload | PASS |
| Driver `parse_args`→`build_config` override mapping (8 args verified) | PASS |
| **Driver e2e CPU run** (`-m`, 300 docs, 3 steps): seed→load→pack+cache→train→val_loss→`checkpoint_step2.pt`+`checkpoint_maxsteps.pt` | PASS (rc=0) |
| **Resume**: `--resume checkpoint_step2.pt` → continued step 2→4, new ckpts | PASS (VERIFIED) |

NOT TESTED: GPU/VRAM on T4 (Colab-only), FP16 AMP on CUDA, 100M-token corpus prep, convergence/quality, multi-hour stability.

## D. Effective configuration (verified)

6 layers · 8 heads · d_model 256 · d_ff 1024 · max_len 512 · vocab 8000 · dropout 0.1 · sinusoidal PE · pre-norm · params **8,842,560** · AdamW lr 3e-4 · warmup-only schedule · grad clip 1.0 · fp16+GradScaler on CUDA.

## E. Training recommendation (T4 14.56 GB)

| Setting | Value | Basis |
|---|---|---|
| device/precision | `cuda` / `fp16` | T4 sm_75 (no bf16); GradScaler path verified |
| batch_size | **16** micro × accum 2 (=32 eff) | conservative start; probe showed headroom at bs2 — bs16×512 est. ~4–6 GB |
| lr / warmup | 3e-4 / 500 | config defaults |
| ckpt/eval interval | 500 / 500 | Drive persistence |
| est. VRAM | ~4–6 GB of 14.56 | estimate — smoke measures actual |
| est. steps | ~6,000 optimizer steps (98.5M tok / 16k tok-per-step) | estimate |

Command (module form — required):
```
cd packages/ai-core && python -m core01.pretraining_driver \
  --train-file <train.jsonl> --val-file <val.jsonl> \
  --output-dir <ckpt_dir> --device cuda --precision fp16 \
  --batch-size 16 --gradient-accumulation-steps 2 \
  --learning-rate 3e-4 --warmup-steps 500 --epochs 1 \
  --checkpoint-interval 500 --eval-interval 500 --log-interval 50
```

## F. Remaining limitations

- GPU memory/throughput on T4: NOT TESTED (needs Colab)
- FP16 GradScaler on CUDA: code-verified, not device-tested
- attention_mask path now fixed but only exercised on CPU synthetic input
- Corpus prep on Colab: not yet run (gated)
- Convergence/output quality: unknown until training
- Resume is epoch-granular approximate (documented)

## FINAL GATE

**`READY FOR TRAINING APPROVAL`** — all required CPU integration checks pass (28/28 + e2e + resume); the one real defect found is repaired and re-verified; notebook invocation bugs fixed. GPU-side items remain for the gated smoke test.
