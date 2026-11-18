# NEXUSAI Dataset V4 Forensic & Quality Report

## Forensic findings (verified on v3 train.jsonl, n=1755)
- Math question-template collapse: 54 unique skeletons across ~1089 math
  records (procedural but repetitive).
- Multi-turn: 58 records, ALL 4-turn (52) or 2-turn (6) — no depth.
- bn categories dominated by math (244/290) — conversational bn thin.
- Language: en 52% / bn 24% / banglish 13% / mixed 1%.
- Math share 56% of all records — category imbalance.

## Root causes
- v1-v3 builders favored procedural math generation (cheap volume).
- Multi-turn families were scenario-limited (6 families × 3 langs × 2 variants).
- bn/banglish conversational authoring was modest vs en math generation.
- v3 math carryover had no cap — imbalance compounded.

## V3 → V4 comparison (VERIFIED, actual counts)
- total: 1947 → 1223 (math curated down, quality over quantity)
- math share: 56% → 32% (391 train records)
- multi_turn: 58 → 63 (now includes 6-8 turn deep scenarios)
- reasoning: 13 → 23 | decision: 7 → 19 | uncertainty: 37 → 44
- self_correction: 4 → 11 | mixed_lang: 18 → 27
- languages: en 52→49%, bn 24→24%, banglish 13→15%, mixed 1→2%

## V4 additions
- Deep multi-turn: study journey (8t), laptop troubleshooting (8t bn),
  job-change decision (8t banglish), photography learning (6t en),
  friendship repair (6t bn) + topic-shift variants.
- bn conversational bank +12, banglish tech_support +20,
  reasoning +8, decision +6, uncertainty +8, self_correction +5,
  mixed_lang +10 (authored trilingual).
- Math+logic capped deterministically at 460/1274 v3 records.

## Validation (VERIFIED)
- All records parse; unique IDs; roles/order validated.
- Exact + prefix near-dup quarantine; foreign-script guard.
- Group-atomic splits (sha256 ordering); benchmark isolated.
- Loader-compatible schema (messages + capabilities).

## Remaining weaknesses (honest)
- en still plurality (49%); bn/banglish below targets.
- multi_turn 63 vs 500+ aspiration.
- Math still largest single category.
- Human semantic review of bn/banglish pending.
- Banglish tokenizer fragmentation persists (data can't fully fix).

## Recommendation
V4 is a modest improvement (better balance, deep multi-turn, more
reasoning) but NOT yet sufficient for flagship conversational SFT.
Recommend V5 targeting: bn→35%+, banglish→20%+, multi_turn→200+,
reasoning/decision→100+ each, BEFORE training-readiness review.
Do NOT train on v4 alone for core01.
