# unified_conversational v4

Curated v3 subset + targeted v4 expansion. v3 math capped at 460/1274
for balance; all v3 non-math kept. New: deep multi-turn scenarios
(6-8 turns: study journey, tech troubleshooting, decision journey,
photography learning, relationship advice + topic-shift variants),
bn/banglish conversational+tech banks, reasoning/decision/uncertainty/
self-correction/mixed-language expansion.

Builder: `packages/ai-core/data/build_unified_conv_v4.py` (SEED=42).
Foreign-script corruption guard retained.

## Stats v4 (train)
1223 approved / 8 rejected / train 1103 / val 60 / test 60.
Langs: en 604 (49%), bn 290 (24%), banglish 182 (15%), mixed 27 (2%).
Cats: math 391, everyday_help 132, qa 127, knowledge 104, tech_support 47,
uncertainty 44, multi_turn 63, social 29, reasoning 23, decision 19,
logic 17, smalltalk 17, instruction 14, identity 13, self_correction 11,
mixed_lang 27, greeting 6, farewell 6, thanks 4, refusal 4, clarification 5.

## v3 → v4 comparison
- math share: 56% → 32% (capped + new non-math content)
- multi_turn: 58 → 63 (incl. 6-8 turn deep scenarios)
- reasoning: 13 → 23; decision: 7 → 19; uncertainty: 37 → 44
- bn: 24%→24%, banglish: 13%→15%, en: 52%→49%, mixed: 1%→2%
- Deep multi-turn (6-8 turns) now present (was max 4 turns in v3)

## Honest gaps
- Still below bn40/en30/banglish20/mixed10 language targets.
- multi_turn 63 vs 500+ aspiration.
- en remains plurality; math still largest single category.
- Human semantic review pending for bn/banglish.
