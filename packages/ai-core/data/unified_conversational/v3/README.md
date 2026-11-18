# unified_conversational v3

Superset of v2 (1,054 carryover) + major expansion: multi-turn scenario
engine (6 families x en/bn/banglish + greeting variants), authored
bn/banglish/en conversational+tech banks, reasoning/decision/uncertainty/
self-correction/knowledge, procedural verified math/logic (trilingual
word problems with steps).

Builder: `packages/ai-core/data/build_unified_conv_v3.py` (SEED=42).
Foreign-script corruption guard added (CJK/Arabic/Cyrillic/Thai → reject).

## Stats v3 (train split)
1947 approved / 202 rejected / train 1755 / val 96 / test 96.
Langs: en 1019 (52%), bn 456 (24%), banglish 262 (13%), mixed 18 (1%).
Cats: math 1089, knowledge 105, qa 128, everyday_help 122, logic 52,
multi_turn 58, uncertainty 37, social 29, tech_support 20, reasoning 13,
instruction 14, smalltalk 17, identity 13, decision 7, self_correction 8,
clarification 5, greeting 6, thanks 4, farewell 6, refusal 4, mixed_lang 18.

## Honest gaps vs targets
- bn 24% vs 40% target; banglish 13% vs 20%; mixed ~1% vs 10%.
- multi_turn 58 vs 500+ target.
- math 56% of records — per-core manifests required so core01 isn't
  math-skewed (see manifests/).
- en-heavy overall. Quantity below aspiration for bn/banglish/mixed.

## Files
train/validation/test.jsonl, records/{lang,category}.jsonl,
manifests/{core01..04}_manifest.json + dataset_manifest.json,
benchmarks/benchmark_manifest.json, reports/, checksums.sha256.
