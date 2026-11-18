# NexusAI Core-01 — Phase D Independent Verification Report

**Date:** 2026-11-17 · verification-only · NO training/backward/step

## 1. "Missing 10 records" — RESOLVED
Earlier print showed only train lang dist (93). Full audit: **103 total
all classified** — en 43 / bn 33 / banglish 27 across all splits.
No unaccounted records.

## 2. Full dataset audit — PASS
- 103 records · schema violations: **0** (all start user, end assistant)
- user turns: 107, unique 107, **0 duplicates**
- leakage (ALL user turns, not just first): train-val 0, test-train 0,
  test-val 0 · **0 conversations split across sets** (atomic ✓)
- multiturn: train 3 / test 1 / val 0 — atomic per conversation_id
- provenance: 103/103 present · rejected_records: 1 (dup)
- checksums.sha256: all 5 files verify OK

## 3. Split adequacy — REVIEW (honest)
93/5/5 is **minimal** — enough for smoke-SFT sanity check, NOT robust
statistical validation. val=5 too small for reliable best-ckpt selection.
Recommendation: acceptable for first SFT run; expand dataset before
production claims. No samples fabricated.

## 4. Masking/shifting/EOS/PAD — tensor-verified (Run3 ckpt, CPU)
- supervised decode: `'assistant: 4.'` — content+EOS only ✓
- multi-turn: both assistant turns supervised ✓
- last supervised token = **EOS(3)** ✓ assistant EOS supervised
- prompt/BOS/pad → all `-100` ✓
- `attention_mask` added to collate (pad keys masked in attention) ✓
- causal mask built inside model.forward ✓ compatible
- `model(x, attention_mask=am)` + `CE(ignore_index=-100)` → loss 7.64 finite ✓

## 5. NaN guard — ADDED & TESTED
`batch_has_supervision(labels)` in `sft_dataset.py` + embedded in cell.
All-masked batch → detected False → must be skipped (never NaN/step).
Tested: real batch True, all-masked False. ✓

## 6. Logits+CE compatibility — VERIFIED
Model forward returns logits with internal causal mask; external
`F.cross_entropy(ignore_index=-100)` on pre-shifted labels is mathematically
identical to standard causal-LM SFT. No architecture conflict.

## 7. Cell review
- TRAINING_ENABLED=False hard gate ✓ · self-contained (embedded dataset code) ✓
- Run4+tok hash gates, strict load, numpy allowlist, OUTDIR isolation ✓
- attention_mask + NaN guard now in preflight test path ✓
- syntax PASS after fix

## 8. Eval suite review — 19 prompts
bn×5, en×6, banglish×4, reasoning×2, multiturn×1, repetition×1, empty×1.
Rubric covers relevance/correctness/lang/grammar/repetition/completeness/
uncertainty/multiturn. **Note:** `mt_name` prompt embeds literal
"assistant:/user:" context lines — valid context-prompt format, flagged.
`empty_test` expects guard behavior, not neural output.

## 9. Preservation — VERIFIED
Run3 ckpt hash UNCHANGED · tokenizer UNCHANGED · sft_v1 intact (86KB) ·
sft_v2 immutable outputs only.

## Gates
| item | status |
|---|---|
| dataset audit/leakage/checksums | PASS |
| masking+shifting+EOS+PAD tensors | PASS |
| NaN guard | PASS |
| logits+CE compat | PASS |
| cell syntax+self-containment | PASS |
| eval suite | PASS (with mt_name note) |
| **Colab GPU preflight** | **NOT VERIFIED — requires Colab run** |
| SFT training | NOT TESTED — prohibited |

## Remaining blockers
1. Upload `sft_v2/` → Drive `NEXUSAI_SFT_V2/` or `/content/.../sft_v2/`
2. Run `COLAB_NEXUSAI_CORE01_RUN5_SFT_PREPARATION.py` on GPU runtime
   (TRAINING_ENABLED=False) → preflight report
3. Phase F approval for training

## STOP — awaiting Phase-F authorization
