# Four-Core Intelligence Development Strategy (proposal — no training)

## Capability framework → data mapping
- Language understanding: all v2 records (lang-tagged); bn/banglish
  coverage is the bottleneck (see tokenizer finding).
- Intent understanding: category diversity (qa/instruction/decision/
  clarification/uncertainty) — v2 has all tags.
- Context: multi_turn records (35 — insufficient; needs v3 expansion).
- Reasoning: reasoning(13)+decision(7)+logic(2) — thin; core02's real
  reasoning data remains phase2/reasoning_train (3,411) pending audit.
- Decision-making: decision category — every record includes constraint
  + conclusion + explanation format.
- Uncertainty: uncertainty(27)+refusal(4) — teaches cutoff-honesty and
  safe refusal; core04-critical.
- Self-correction: self_correction(4) — tiny; expand in v3.

## Per-core recommended manifests (proposal)
- core01_conv_sft_v1: v2 ALL + phase3/sft_v1(536) + sft_v2(103) after
  audit; weight conversational categories, cap math ≤20%.
- core02_instruction_sft_v1: reasoning_train converted + v2
  instruction/decision/multi_turn + core02_reasoning (existing).
- core03_math_sft_v1: core03_math(1,750) + v2 math(582) + gsm8k
  (license pending).
- core04_knowledge_sft_v1: core04_knowledge_full(318) + v2
  knowledge/qa/uncertainty/refusal.

## Training configs (per earlier verified runs)
Full fine-tuning (architecture has no adapter support; LoRA would need
new code — NOT recommended now). bs 8, lr 2e-4–3e-4, epochs 3-8 by
dataset size, max_len 512, response-only loss (verified), ckpt+sha256
per epoch, new versioned dirs only.

## Staged order (proposal)
1. v3 dataset expansion (bn/banglish conversational + multi-turn).
2. core01 conv-SFT → unlock neural-only chat quality.
3. core04 knowledge+uncertainty SFT → fix hallucination.
4. core03 math SFT v2 → retry arithmetic gate.
5. core02 instruction SFT → re-evaluate conversational fitness.

## Resource estimates (measured CPU baseline: ~0.45-3s/step)
core01 (~3k recs, 3ep ≈1.1k steps): CPU ~40-60min / T4 ~4min.
core02 (~4k, 2ep ≈1k steps, 20M): CPU ~1-1.5h / T4 ~5min.
core03 (~8k, 8ep ≈8k steps): CPU ~4-6h / T4 ~20min.
core04 (~3k, 8ep ≈3k steps, 33M): CPU ~3-5h / T4 ~25min.
(±50% uncertainty; Colab T4 free tier assumed, not guaranteed.)

## Architecture limitation note
8.8M–33M decoder-only transformers CAN learn narrow SFT tasks (proven:
core02 74%, core04 73% seen-fact) but general trilingual conversation
likely exceeds their capacity ceiling — expect incremental gains, not
human-level chat. A larger pretraining run (Run4-scale+) is the real
lever for core01; SFT alone has limits. State this honestly in evals.
