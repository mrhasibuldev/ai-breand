# unified_conversational v2

Superset of v1 (645 carryover records preserved) + new authored content:
multi-turn scenarios (35 records, 2-4 turns, 5 topics x3 languages +
slot variants), reasoning/decision/self_correction/clarification,
expanded uncertainty/social, procedural verified math & logic.

Builder: `packages/ai-core/data/build_unified_conv_v2.py` (SEED=42).
No external AI. Same messages-schema as v1 (ChatSFTDataset compatible),
plus optional `capabilities` metadata (ignored by loader).

## Stats v2
1054 approved / 51 rejected (dup_question + near-dup prefix).
train 950 / val 52 / test 52. Groups: sha256(split_group) atomic.
Langs (train): en 504 (53%), bn 302 (32%), banglish 141 (15%), mixed 3.
Categories: math 582, qa 108, everyday_help 49, multi_turn 35,
knowledge 33, uncertainty 27, reasoning 13, smalltalk 17, social 18,
instruction 14, identity 13, decision 7, greeting 6, farewell 6,
thanks 4, self_correction 4, clarification 5, refusal 4, logic 2,
mixed_lang 3.

## Honest limitations
- Multi-turn (35) still below the 300-500 aspiration — scenario scripts
  are authored, not template-expanded; v3 should add more scenarios.
- English-heavy (53%) vs bn40/en30/banglish20/mixed10 target — math
  procedural bias + v1 carryover. Banglish tokenizer fragmentation
  (see forensic audit) limits its near-term value anyway.
- Math is 55% of records — useful for core03, heavy for core01;
  per-core manifests recommended (see mapping doc).
- Semantic quality rule-checked only.
