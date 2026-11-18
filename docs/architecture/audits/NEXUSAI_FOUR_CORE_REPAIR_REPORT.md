# NexusAI Four-Core Repair Report

**Date:** 2026-11-18 · Pre-change backups: `backups/20261118_223409_fourcore_repair/`

## Repairs applied (minimal, reversible)

### R1 (F2) — sampling-parameter falsy bug — FIXED AND VERIFIED
- Files: `packages/ai-core/core01/transformer.py` `generate()`; `packages/ai-core/core01/inference.py` `generate()`.
- Root cause: `temperature = temperature or self.config.temperature` (same pattern for `repetition_penalty`, `max_new_tokens`) silently discarded explicit falsy values such as `0.0`/`1.0`.
- Fix: `x if x is not None else default`, matching the existing `top_k`/`top_p` pattern.
- Regression: `packages/ai-core/tests/four_core/test_generation_repairs.py` F2 test — PASS.

### R2 (F3) — batch-unsafe EOS exit — FIXED AND VERIFIED
- File: `transformer.py` `generate()`.
- Root cause: `if next_token.item() == self.config.eos_id: break` — `.item()` requires a single element; crashes for batch_size > 1 and stops the entire batch on the first EOS.
- Fix: per-row `finished` mask; finished rows forced to `pad_id`; loop breaks only when all rows finished. Batch=1 behavior is identical to before.
- Regression: F3 batch=2 PASS; F3 EOS-bounded PASS.

### R3 (Q4) — stale registry metadata — FIXED AND VERIFIED
- File: `packages/ai-core/ml-service/model_registry.py` — `nexus-medium.expected_params` corrected 2,468,928 -> 2,452,544 (actual `MediumTransformer` parameter count; strict load already passed with 0 missing/unexpected keys, proving only the constant was wrong).
- Regression: Q4 test PASS.

## Documented but NOT code-fixed (training/data-bound — cannot be solved by patches)
- F1: Core-01 chat prompts trigger immediate EOS (pretrained doc-LM; needs SFT — Run4/Run5, separately authorized).
- F4: no KV cache + Python-loop repetition penalty — performance limitation, future optimization.
- F5: Run3 checkpoint numpy metadata vs `torch.load(weights_only=True)` — future re-save or safe-globals.
- Q1/Q2/Q3: Core-02 template collapse, Core-03 number-collapse, Core-04 prompt-insensitive recall — all require new SFT data/training (V5/Core-05 roadmap).
- Dataset findings: core02_reasoning 60% exact-duplicate train records; core03_math 18%; 1 cross-split val/train leak — recorded for the next data mission; datasets unmodified.

## Verification after repair
- `test_generation_repairs.py`: 6/6 PASS (post-fix).
- `four_core_test_suite.py` (executed pre-patch; the patches preserve the batch=1 greedy path — confirmed by the post-fix contract test): core-01 38/56 non-empty; core-02 132/132 non-empty (mean surface-sim 0.884); core-03 87/87 non-empty, numeric oracle 8/87 = 9.2%; core-04 31/31 non-empty (sim 0.900).
- Live `model_router` check post-patch (neural_only=True): MATH -> `neural:nexus-core-03`, GREETING -> `neural:nexus-core-01`, KNOWLEDGE -> `neural:nexus-core-04`; no deterministic substitution.

## Files modified
- `packages/ai-core/core01/transformer.py`
- `packages/ai-core/core01/inference.py`
- `packages/ai-core/ml-service/model_registry.py`

No checkpoint, tokenizer, dataset, architecture, router-logic, API, database, or UI changes were made.
