# Four-Core SFT Evaluation Results (honest, held-out)

Evaluator: packages/ai-core/eval_core.py — greedy chat_generate, SFT format
`[BOS] user: <q> [EOS]` → decode, strip `assistant:`. Metrics per category:
exact_match (normalized), contains (ref keywords), empty_rate.

## Prompt-format bug found & fixed
First eval returned empty_rate=1.0 / exact=0%: chat prompt omitted the
user-turn EOS that serialize_conversation emits in training. Fixed in
nexus_core.chat_prompt_ids (append eos_id after user text). Re-eval valid.

## Core-02 v1 (contaminated split — INVALID, kept for record)
- n=132, exact_match=0.9318, contains=0.9394, empty=0.0
- INVALID: 68/95 test questions verbatim in train (pre-fix split).
- Demonstrates template memorization, NOT reasoning generalization.

## Core-03 v1 (contaminated split — indicative only)
- n=87, exact_match=0.1149, contains=0.1149, empty=0.0
- Per-category: fraction|en 0.857, algebra|en 0.167, arith|en 0.087,
  arith|bn 0.0, percent|en 0.077, wordprob|en 0.0
- Model emits correct FORMAT ("x = 2.", "2/4.") but wrong values.
- 18/85 test questions duplicated in train; all 13 templates shared.

## Core-04 v1 (60 steps, old data — superseded)
- n=12, exact=0.0 — fluent but factually wrong; undertrained.

## Split-integrity fixes applied (this session)
- build_core02/03/04: sort key changed sample_id → question text (02/03)
  and → reference answer (04, fact-level). Rebuilt datasets.
- Verified: 0 exact-question overlap (02/03); 0 test-answer overlap (04).
- v2 retraining runs on clean splits; results pending — see EXECUTION_STATE.
