# NexusAI Core-01 — Config Resolution & GPU Validation Audit

**Date:** 2026-11-16 · READ-ONLY · local source inspection + prior executed tests

## Root cause of Colab constructor error
The earlier validation script tried `NexusAICore01(**dict)` or introspected
the constructor without supplying the required `config` argument — a
**script limitation, not a model defect**. The real constructor is
`NexusAICore01(config: NexusAICore01Config)` (`core01/transformer.py`).

## Exact config resolution (authoritative — `pretraining_driver.py`)
1. `build_config(args)` (lines 94-115): `NexusAICore01Config()` defaults +
   `setattr` for non-None CLI overrides (batch_size, lr, weight_decay,
   grad_clip, warmup, precision, accum, ckpt/eval interval, device, seed,
   tokenizer_path, resume_checkpoint).
2. Driver does **NOT** read `ckpt["config"]` for architecture — arch comes
   from config defaults; strict load proves compatibility.
3. `NexusAICore01Config` defaults (`model_config.py:47-143`): vocab 8000,
   d_model 256, n_heads 8, d_ff 1024, max_len 512, pad0/unk1/bos2/eos3 —
   identical to checkpoint architecture.

## Tokenizer (production path)
`NexusAITokenizer(resolved_tokenizer, config)` where resolved =
`args.tokenizer or config.tokenizer_path or package default`
(driver lines 189-194). Packaged `sp_bpe_8k.model` used; stale ckpt path
ignored. `_validate_compatibility()` enforces vocab=8000.

## Dataset + collate (production path)
`load_texts(.jsonl, field="text")` → `PackedTextDataset(texts, tokenizer,
max_len=512, pad_id=0)` — packs docs into `max_len+1` blocks;
`input_ids=block[:-1]`, `targets=block[1:]` (shift at dataset level,
dataset.py ~line 305+). DataLoader bs=8, drop_last=True.

## Authoritative loss (VERIFIED — transformer.py:367-374)
`model(input_ids, targets)` → `F.cross_entropy(logits.view(-1,8000),
targets.view(-1), ignore_index=pad_id)` — mean reduction, NO internal shift
(dataset already shifted). Grad-accum scaling: `loss/group_size`
(training.py ~line 320). FP16 via `torch.autocast` + `GradScaler("cuda")`.

## Engine (production optimizer stack — training.py:204-261)
`PretrainingEngine(model, config, checkpoint_dir, tokenizer_path)`:
AdamW(lr, weight_decay) → `setup_scheduler(steps)` LambdaLR warmup →
GradScaler for fp16. `load_checkpoint(file)` restores model+opt+sched+
scaler+RNG+epoch+step (lines 453+).

## Resume semantics (VERIFIED)
`range(engine.current_epoch=3, args.epochs=5)` → epochs index 3,4 →
prints "epoch 4/5","5/5" = **2 additional epochs**. Step continues 1341→8000.
Scheduler/optimizer/RNG restored → continuous LR schedule.

## Proposed Run4 command (PROPOSAL ONLY — not executed)
```
python packages/ai-core/core01/pretraining_driver.py \
  --train-file <pkg>/datasets/verified_data/corpus_train.jsonl \
  --tokenizer <pkg>/nexusai/tokenizer/sp_bpe_8k.model \
  --output-dir /content/nexusai_run4 \
  --resume <run3 ckpt or run4 latest> \
  --epochs 5 --max-steps 8000 --batch-size 8 \
  --gradient-accumulation-steps 4 --precision fp16 --device cuda
```

## Status table
| Check | Status |
|---|---|
| Config class/path/constructor | PASS (source-verified) |
| strict=True load | PASS (executed locally earlier) |
| Tokenizer prod interface | PASS |
| Dataset schema→loader | PASS |
| Authoritative loss identified | PASS |
| Engine resume mechanics | PASS (source + synthetic test) |
| Epoch semantics | PASS (source-verified) |
| Live Colab GPU forward/loss/VRAM | NOT TESTED — validation cell ready |
| optimizer.step / training | NOT RUN (prohibited) |

## FINAL CLASSIFICATION: **B→A pending live cell**
Config issue RESOLVED (was script bug). All source-level checks PASS.
Remaining gate: run `CORE01_FINAL_COLAB_VALIDATION_CELL.py` on Colab T4 —
if it prints PASS, classification becomes **A — READY FOR RUN4 TRAINING
AUTHORIZATION** (still requires your explicit approval to train).
