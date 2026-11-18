# NexusAI Unified Conversational Dataset — Specification (proposal)

Compatible with `core01/sft_dataset.py` ChatSFTDataset: JSONL records with
`messages: [{role,content},...]`; loss supervises assistant tokens + EOS.

## Record schema

```json
{
  "sample_id": "conv:<lang>:<seq>",
  "lang": "en|bn|banglish|mixed",
  "category": "greeting|identity|thanks|farewell|smalltalk|qa|instruction|multi_turn|uncertainty|math|knowledge|refusal",
  "conversation_id": "conv-<hash>",
  "messages": [{"role":"user","content":"..."},{"role":"assistant","content":"..."}],
  "provenance": {"builder":"build_unified_conv.py","seed":42,"source":"authored|template|converted:<origin>","license":"self-authored|verified-public"}
}
```

## Required content coverage (target ~3,000-5,000 records v1)

| Category | Target | Languages |
|---|---|---|
| greeting | 200 | en/bn/banglish/mixed |
| identity (Hasibul founder — via data only) | 100 | en/bn/banglish |
| thanks/farewell | 150 | all |
| smalltalk/how-are-you | 300 | all |
| general QA | 600 | all |
| instruction following | 400 | en/bn |
| multi-turn (2-4 turns) | 400 | all |
| uncertainty/honest-unknown | 300 | all |
| math (hand-off style) | 200 | all |
| knowledge (hand-off style) | 200 | all |
| refusal/off-topic | 200 | en/bn |

## Hard rules
- Founder identity "Hasibul" appears ONLY inside assistant answers in
  training data — never as code/handler.
- Question-level dedup + hash split (learned from core02/04 leakage bugs).
- No external AI-generated text. Sources: self-authored seeds,
  deterministic templates over authored content, converted existing
  verified datasets (phase3/sft_v1, sft_v2, reasoning_train after audit).
- Banglish = romanized Bengali function words (existing BANGLISH_MARKERS
  vocabulary as guide).
- Every record gets provenance.source; manifest + sha256 per split.

## Conversion sources (pending per-file audit)
- phase3/sft_v1/sft_train.jsonl (536, messages format already)
- sft_v2/*.jsonl (103 total — small)
- phase2/reasoning/reasoning_train.jsonl (3,411 — instruction/answer →
  messages conversion; mostly EN reasoning, limited conv value)
- phase9_1 cleaned Bengali texts (741+590+151 — need pairing; likely
  skip or use as pretraining continuation, NOT SFT)
- dolly/gsm8k: EN-only, license verify; optional augmentation, not core.

## Evaluation isolation
- test split by question hash; multi-turn groups kept atomic.
- Benchmark: ≥100 prompts/core, per-language subsets, hallucination audit.
