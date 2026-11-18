# Four-Core Dataset Mapping — unified_conversational v1

How v1 records map to core training needs. `category` tags allow
per-core filtering; all records share the messages schema.

## Core-01 (conversational) — PRIMARY consumer
Use: ALL categories. Especially greeting/identity/thanks/farewell/
smalltalk/everyday_help/social/multi_turn/mixed_lang/uncertainty.
Identity records teach "Hasibul" as data, not handler.
Gap: conversational depth is thin — v2 expansion required before
flagship conv-SFT; v1 usable for smoke/pilot training.

## Core-02 (instruction following)
Use: instruction (15), multi_turn (6), qa, everyday_help.
Note: v1 instruction set is small; core02's real instruction data remains
phase2/reasoning (3,411) pending format conversion + audit.

## Core-03 (math)
Use: math (287) — procedural verified arithmetic/word-problems/algebra.
Complements (not replaces) core03_math dataset (1,750). v1 math answers
are terse "a + b = c" — core03_math has richer category coverage; merge
both for math_sft_v1.

## Core-04 (knowledge + uncertainty)
Use: knowledge (33), qa (108), uncertainty (17), refusal (4).
CRITICAL for core04: uncertainty/refusal records teach honest "I don't
know" — directly targets the v3 hallucination problem. Still thin;
core04_knowledge fact cards remain primary, v1 adds boundary behavior.

## Recommended per-core mixes (proposal)
- core01_conv_sft_v1: unified v1 (all) + phase3/sft_v1 + sft_v2 (post-audit)
- core02_instruction_sft_v1: unified instruction/multi_turn + reasoning_train
- core03_math_sft_v1: core03_math + unified math + gsm8k (license pending)
- core04_knowledge_sft_v1: core04_knowledge_full + unified knowledge/uncertainty/refusal
