# NexusAI Four-Core SFT Training Strategy (proposal — NOT authorized)

All runs use NEW versioned output dirs; no existing checkpoint is touched.
Shared infra (verified): `sft_train.py` (response-only loss, grad clip,
checkpoint+sha256), `eval_core.py`, `nexus_core.py`, tokenizer
sp_bpe_8k (vocab 8000, sha256 2fcc6a87…).

## Unified dataset schema (compatible with ChatSFTDataset)

```json
{"sample_id":"conv:bn:0001","lang":"bn","category":"greeting",
 "conversation_id":"conv-0001",
 "messages":[{"role":"user","content":"নমস্কার"},
             {"role":"assistant","content":"নমস্কার! আমি NexusAI। কীভাবে সাহায্য করব?"}],
 "provenance":{"builder":"build_conv_sft.py","seed":42,"source":"authored+template"}}
```

Multi-turn = multiple user/assistant pairs in `messages`. Loss masks to
assistant tokens + EOS only (already implemented).

## Core-01 — conversational_sft_v1 (PRIMARY)
- Data: unified conversational set (~2-4k recs target): greetings,
  identity (Hasibul founder — learned from data), thanks, farewell,
  bn/en/banglish small talk, follow-ups, multi-turn (2-4 turns),
  instruction following, honest uncertainty, math handoff examples,
  knowledge handoff examples. Mix in phase3/sft_v1 (536) + sft_v2 (93)
  after format conversion + leakage audit.
- Init: fresh SFT from random OR continue Run3 weights? DECISION NEEDED:
  continuing Run3 risks catastrophic forgetting of pretraining; fresh
  conv-only model may be too narrow. Recommended: initialize from Run4
  checkpoint (verified, more training) — requires explicit approval since
  Run4 activation was previously gated.
- Config: epochs 3-5, bs 8, lr 2e-4 (lower than specialist 3e-4 for
  stability), max_len 512, cosine-ish decay via AdamW, ckpt every epoch.
- Eval: conv benchmark (see strategy doc §eval) + bn/en/banglish subsets.

## Core-02 — instruction_sft_v1
- Purpose: convert slot-fill specialist into general instruction follower.
- Data: reasoning_train.jsonl (3,411, format-convert) + conversational
  instruction subset + extraction/QA formats. Question-level split.
- Config: epochs 2-3, bs 8, lr 3e-4.
- Eval: held-out instructions (NOT template skeletons) + conv smoke.

## Core-03 — math_sft_v1
- Data: procedural arithmetic v2 — add worked-solution format
  ("12 × 8 = 96. Steps: 12×8 = 10×8 + 2×8 = 80+16 = 96."), Bengali
  procedurally generated word problems, gsm8k_cleaned EN subset
  (license verify first; else skip), multi-step chains.
- Scale target: 5-10k records (current 1,750 too small).
- Config: epochs 6-10, bs 8, lr 3e-4; consider digit-aware eval.
- Eval: numeric-tolerance exact match + step correctness; unseen operands.

## Core-04 — knowledge_sft_v1
- Data: expand cards 36 → 300+ across science/geography/history/everyday;
  CRITICAL: add OFF-TOPIC refusal pairs ("What is the capital of France?"
  style unknowns → honest "I don't have verified knowledge of that") in
  bn+en; keep fact-level split.
- Config: epochs 6-10 on larger set, bs 8, lr 3e-4.
- Eval: seen-fact recall + unseen-fact refusal rate + hallucination audit.

## Resource estimates (CPU local / Colab T4)
- core01 conv (~3k recs, 3 epochs ≈ 1,100 steps): CPU ~40-60min;
  T4 ~3-5min.
- core02 (~4k, 2 ep ≈ 1,000 steps, 20M): CPU ~60-90min; T4 ~5min.
- core03 (~8k, 8 ep ≈ 8,000 steps, 8.8M): CPU ~4-6h; T4 ~15-25min.
- core04 (~3k recs, 8 ep ≈ 3,000 steps, 33M): CPU ~3-5h; T4 ~20-30min.
(Estimates ±50%; measured: core02 598 steps ≈ 30min CPU.)

## Training order (recommended)
1. Build unified conversational dataset (blocks everything).
2. core01 conv-SFT → enables neural-only chat quality.
3. core04 knowledge-SFT → fixes hallucination/refusal.
4. core03 math-SFT → math gate retry.
5. core02 instruction-SFT → re-evaluate conversational fitness.

## Colab readiness
`docs/notebooks/COLAB_NEXUSAI_FOUR_CORE_SFT.py` exists and is parameterized;
needs: dataset-dir args for new datasets, Drive checkpoint export,
preflight hash checks. PREPARED, not run. No external AI anywhere in path.
