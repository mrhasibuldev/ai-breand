# Unified Conversational Dataset v2 — Construction Report

## Method
`build_unified_conv_v2.py` (SEED=42): v1 carryover (645, re-grouped) +
authored scenario scripts (5 topics × en/bn/banglish + slot variants) +
authored reasoning/decision/self-correction/clarification/uncertainty/
social seeds + procedural verified math/logic/fractions/percent.

## Results (VERIFIED from manifests)
- 1054 approved / 51 rejected (dup_question 46, near_dup_prefix 5)
- train 950 / validation 52 / test 52; group-atomic splits (sha256 ordering)
- New vs v1: +409 records; new categories reasoning, decision,
  self_correction, clarification, logic now present; multi_turn 6→35.

## Language distribution (train)
en 504 (53%) | bn 302 (32%) | banglish 141 (15%) | mixed 3 (<1%)
Target was bn40/en30/banglish20/mixed10 — NOT achieved; English-heavy
due to math procedural bias + v1 carryover. PARTIALLY VERIFIED.

## Category distribution (train)
math 582 | qa 108 | everyday_help 49 | multi_turn 35 | knowledge 33 |
uncertainty 27 | smalltalk 17 | social 18 | reasoning 13 |
instruction 14 | identity 13 | decision 7 | greeting 6 | farewell 6 |
clarification 5 | thanks 4 | self_correction 4 | refusal 4 | logic 2 |
mixed_lang 3

## Quality checks executed
Valid roles/ordering, non-empty, answer≠question, exact-question dedup,
prefix near-dup (>3 → quarantine), group-atomic splits, math answers
verified by recomputation at generation time, manifests+sha256.
Semantic naturalness: rule-checked only — human review still pending.

## Limitations (honest)
- Multi-turn 35 ≪ 300-500 target — authored scenarios don't scale
  mechanically without quality loss; needs more scenario authoring.
- Language balance off-target (en-heavy).
- Math dominance (55%) — per-core manifests needed so core01 isn't
  math-skewed.
- Banglish limited by tokenizer fragmentation (see forensic audit).

## Reproducibility
`python build_unified_conv_v2.py` regenerates everything deterministically.
v1 files untouched (frozen historical version).
