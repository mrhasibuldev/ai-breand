# NexusAI Core-01 — Run3 Checkpoint Compatibility Forensic Audit

**Date:** 2026-11-16 · **Mode:** READ-ONLY · **Executed locally on repo artifacts**

## Executive Summary
Run3 checkpoint is **fully compatible** with the packaged Core-01 implementation.
Strict `load_state_dict(strict=True)` executed and PASSED locally; synthetic
forward+backward+optimizer/scheduler/scaler/RNG save-load-resume executed and
PASSED. The stale `tokenizer_path` inside the checkpoint is **informational
only** — the driver resolves the tokenizer via `--tokenizer` arg / config /
package-relative default (`pretraining_driver.py:189-194`), and
`training.py:~599` explicitly documents vocab-size equality as the real check.
**Classification: A — READY FOR FINAL COLAB VALIDATION.**

## Verified Inputs
| Artifact | Value |
|---|---|
| Package | `exports/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip` 173,913,680 B · SHA `f20d38ee…86e644` |
| Checkpoint | `checkpoints/verified/core01_run3_checkpoint_final.pt` · 106,777,501 B · SHA `ad515cadea433d17…7830` |
| Ckpt metadata | epoch=3, step=1341, PRETRAINING_COMPLETED, 100 tensors |
| Tokenizer | `sp_bpe_8k.model` 387,195 B · vocab 8000 · en+bn+banglish encode verified |
| Dataset | `corpus_train.jsonl` 385,217,021 B · 216,193 rec · keys `{text,category,lang,source}` · sha `5f8572ed…` |

## A. Model Architecture (VERIFIED — `core01/transformer.py`)
`NexusAICore01`: TokenEmbedding(8000→256,√d scale,pad_idx) →
SinusoidalPE(512) → 6× pre-norm TransformerBlock(LN→MHA 8H→res, LN→FFN 256→1024→256→res)
→ Linear(256→8000). 8,842,560 params (`model.count_parameters()` measured).
State-dict family `transformer_blocks.*` — matches ckpt (100 tensors).
strict=True load: **PASS** (executed).

## B. Tokenizer (VERIFIED)
`tokenizer_interface.py` loads SentencePiece directly from a path arg;
`_validate_compatibility()` enforces vocab==config (8000) and warns on
special-ID drift. Checkpoint's stored path
`/content/nexusai/.../sp_bpe_8k.model` is a **stale Colab absolute path** —
NOT resolvable in package; safe override = pass packaged
`nexusai/tokenizer/sp_bpe_8k.model` via `--tokenizer` (driver line 134,189).
Special IDs: pad0/unk1/bos2/eos3 consistent with training.
Dataset uses `tokenizer.encode(text, add_special_tokens=True, max_length=512)`
(`dataset.py:80`) — same interface, same conventions.

## C. Authoritative Entrypoint (VERIFIED by code trace)
`core01/pretraining_driver.py` — the ONLY driver matching ckpt structure:
- `load_texts()` handles `.jsonl` + `text` field (lines 46-91) → corpus schema fits
- `--tokenizer/--resume/--epochs/--max-steps/--batch-size/--gradient-accumulation-steps/--precision/--device` args (118-160)
- `engine.load_checkpoint(args.resume)` (line 316) restores full state
- Training loop `for epoch in range(engine.current_epoch, args.epochs)` (line 324) → **TOTAL epoch semantics**
- `training.py` engines: PretrainingEngine (resume-capable), InstructionTuningEngine (SFT-gated, requires pretrained ckpt — correct separation)

## D. Optimizer/Scheduler/Resume (VERIFIED in code + executed save/load)
Run3 config: lr=3e-4, bs=8, epochs=3. Checkpoint contains optimizer/
scheduler/GradScaler/RNG states — all present. Executed test: built AdamW+
LambdaLR+GradScaler(enabled=False), ran 1 synthetic step, saved full state,
reloaded, restored opt state + torch RNG — **PASS**. Param ordering identical
(same model class, strict load) → optimizer restore safe.

## E. Dataset (VERIFIED)
`corpus_train.jsonl`: 216,193 records, `{text,category,lang,source}`, 0
malformed. Driver `--train-file` + `--text-field text` (default) matches.
Known quality caveats (6,922 dup texts, thin Banglish) — quality issue, not
compatibility issue.

## F. Final Colab Validation Plan (all NOT YET TESTED on GPU)
1. Import `core01.transformer.NexusAICore01` from package path
2. Load tokenizer via `NexusAITokenizer(pkg/nexusai/tokenizer/sp_bpe_8k.model, cfg)`
3. `load_state_dict(strict=True)` → report missing/unexpected (expect none)
4. Restore optimizer+scheduler+scaler into fresh instances (no step)
5. Restore RNG states
6. Load 1 real corpus batch via `PackedTextDataset`
7. Forward → loss finite → backward (grads only, NO optimizer.step)
8. `torch.cuda.max_memory_allocated()` on T4
9. Confirm resume epoch=3/step=1341 semantics

## G. Run3→Run4 Resume Config (recommended, not executed)
`--resume <run4-or-run3 ckpt>` · `--epochs 5` (=2 new epochs: range(3,5)) ·
`--max-steps 8000` · bs8 × accum4 · fp16 · output `checkpoints/core01_run4/`
· Run3 file untouched (read-only source). Scheduler continues from restored
state → LR schedule stays continuous. Verify continuation by comparing
ckpt step >1341 and loss trend vs Run3 val 4.217.

## Unresolved Issues
- Live GPU execution: NOT TESTED (needs Colab)
- Drive-only step ckpts: NOT VERIFIED
- Dataset quality limits expected gain (SFT phase still needed)

## Status Table
| Check | Status |
|---|---|
| Package identity | PASS |
| Checkpoint hash/metadata | PASS |
| strict=True load | PASS (executed locally) |
| Tokenizer compat | PASS |
| Dataset schema compat | PASS |
| Entrypoint identification | PASS |
| Optimizer/scheduler/scaler/RNG restore | PASS (synthetic executed) |
| Forward+backward | PASS (synthetic executed) |
| Real dataset batch fwd/loss | NOT TESTED (Colab) |
| GPU memory/VRAM | NOT TESTED (Colab) |
| Live resume run | NOT TESTED (needs authorization) |

## FINAL CLASSIFICATION: **A — READY FOR FINAL COLAB VALIDATION**
