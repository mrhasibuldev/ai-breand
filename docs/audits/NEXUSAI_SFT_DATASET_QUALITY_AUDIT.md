# NexusAI SFT Dataset Quality Audit — sft_v2
Date: 2026-11-17 · READ-ONLY · `packages/ai-core/data/sft_v2/`

## Inventory
- train.jsonl 93 · validation.jsonl 5 · test.jsonl 5 · total 103
- formats: {sample_id, lang, category, conversation_id, version, messages[], provenance}
- rejected: 1 (duplicate question) in rejected_records.jsonl
- checksums.sha256: all 5 files VERIFIED

## Language distribution (measured, all splits)
en 43 (41.7%) · bn 33 (32.0%) · banglish 27 (26.2%)
Train only: en39 bn29 bg25. No "other" language. Mixed = multiturn bn/bg samples.

## Conversation structure
- single-turn 100, multi-turn 4 (conversation-atomic in splits)
- roles valid: all start user, end assistant (0 violations)
- assistant len min11/avg55.8/max96 chars — SHORT answers
- provenance 103/103 · dedup 0 exact dups · 0 cross-split leakage (all user turns)

## Topic coverage (train categories)
facts25 identity13 greeting13 explain10 everyday8 reasoning8 thanks7
uncertainty6 multiturn3
**MISSING/weak:** love/affection (0 dedicated beyond everyday), math beyond
arithmetic templates absent in v2 (good — v1's 90% math skew removed),
planning/decision-making (0), Bengali cultural depth (thin), long-form
explanations (max 96 chars).

## Quality verdict
- VERIFIED: schema, splits, leakage, provenance, checksums, dedup
- PARTIAL: language balance OK for smoke; answer depth shallow
- RISK: 103 samples is smoke-scale — high overfitting/template-memorization
  risk; val=5 too small for reliable selection
- No fabricated data; all deterministic templates

## Recommendation
READY WITH CONDITIONS for smoke-SFT only. Expand to 1-3k diverse samples
(human-reviewed) before any production claim.
