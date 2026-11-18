# NexusAI Core-01 — Phase D Implementation Report

**Date:** 2026-11-17 · Phase D only · NO training performed

## Deliverables created
| file | status |
|---|---|
| `packages/ai-core/data/build_sft_v2.py` | ✅ runs, deterministic |
| `packages/ai-core/data/sft_v2/` (train/val/test.jsonl + manifests + checksums) | ✅ generated |
| `packages/ai-core/core01/sft_dataset.py` | ✅ masking verified vs tensors |
| `docs/notebooks/COLAB_NEXUSAI_CORE01_RUN5_SFT_PREPARATION.py` | ✅ syntax OK, TRAINING_ENABLED=False |
| `evaluation/core01_sft_v2/eval_prompts.json` | ✅ versioned suite + rubric |

## Dataset v2 results
- **103 records** → train 93 / val 5 / test 5 (group-aware, seed 42)
- lang: en 39 · bn 29 · banglish 25 (train) — balanced vs v1 (was 90% math)
- categories: identity, greeting, thanks, facts, explain, uncertainty, everyday, reasoning, multiturn
- **leakage: 0** question overlap across splits · 1 rejected (dup)
- provenance per record + rejected_records.jsonl + checksums.sha256
- **Honest note:** small seed set — smoke-SFT scale, not production corpus

## Response-only masking — PROVEN on real tensors
- supervised decode = `'assistant: 4.'` (content+EOS only)
- multi-turn: `'assistant: Nice! assistant: Rahim.'` — both turns correct
- user text, role-adjacent prompt, BOS, padding → all `-100`
- `F.cross_entropy(ignore_index=-100)` → finite loss 7.64; all-masked → nan (confirms active)
- **NOTE:** model's own `forward(targets=)` uses `ignore_index=pad_id` — SFT loop must call `model(x)`→logits then CE(-100) itself (cell does this)

## Colab cell
- `TRAINING_ENABLED=False` hard gate; preflight verifies env/GPU/hashes/package/masking/optimizer-construction/memory — exits before any step
- Run4 hash-gated, strict load, same numpy allowlist deserialization
- Output → `/content/NEXUSAI_RUN5_SFT/` (never Run4 dir)

## Gates
| gate | status |
|---|---|
| dataset build+splits+leakage | PASS |
| masking correctness | PASS |
| loss finite | PASS |
| Run4 strict load (code path) | PASS (verified v7 + local Run3) |
| cell syntax/preflight | PASS (syntax); Colab run NOT TESTED |
| training | NOT TESTED — gated, prohibited |
| sft_v2 upload to Colab | PENDING (user must place files) |

## Files preserved
Run4 ckpt, tokenizer, sft_v1, all source — untouched. No backward/step/save.
No external AI. No push.

## Remaining blockers
1. Upload `sft_v2/` to Drive or `/content/NEXUSAI_RUN4_CPU_VERIFY_WORK/sft_v2/`
2. Colab preflight run (GPU runtime for real estimate)
3. **Phase F approval** for actual SFT
