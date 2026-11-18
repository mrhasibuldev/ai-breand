# NexusAI Core-01 — Real Answer Capability Audit

**Date:** 2026-11-17 · READ-ONLY · Run3 evaluated live on CPU (31 prompts)
Run4 outputs: Drive-only → comparison INCONCLUSIVE pending samples file.

## Executive Summary
Run3 was tested with the full 31-prompt suite (bn/en/banglish/reasoning/
instruction/context/knowledge/open). Result: **the model cannot reliably
answer questions.** It generates fluent-looking English fragments but they
are semantically unrelated to prompts; Bengali prompts produce 100% empty
generation; reasoning prompts yield math-template gibberish.

## Model Identity (verified)
Run3 `checkpoint_final.pt` · 106,777,501 B · sha `ad515cade…7830` ·
ep3/step1341 · strict load PASS · 8,842,560 params · sp_bpe_8k vocab 8000.
Tokenizer sha `2fcc6a87…8052` (shared with Run4 — verified).

## Run3 Results — 31 prompts, greedy, CPU
| Category | n | empty | meaningful | verdict |
|---|---|---|---|---|
| Bengali | 5 | **5/5 EMPTY** | 0 | FAIL |
| English | 5 | 1 | 0 | gibberish |
| Banglish | 5 | 0 | 0 | gibberish |
| Reasoning | 4 | 3 | 0 | math-template noise |
| Instruction | 4 | 1 | 0 | ignored format |
| Context | 3 | 1 | 0 | no memory use |
| Knowledge | 2 | 0 | 0 | wrong facts |
| Open-ended | 3 | 1 | 0 | gibberish |

**Totals: 11/31 EMPTY_GENERATION (all Bengali + most reasoning),
20/31 non-empty but 0 semantically correct answers.**

Examples (verbatim, `exports/run3_answer_capability_20261117.json`):
- P:"What is the capital of Japan?" → "The city is a country that is an
  American football team…"
- P:"Why do humans need water?" → "First find the total number of fish:
  3 * 2 = <<2*2=4>>4 pairs…" (math-template artifact)
- P:"তোমার নাম কী?" → EMPTY (immediate EOS)
- P:"Reply only with the number: 7+5?" → EMPTY

## Root causes (evidence-ranked)
1. **Model undertrained for QA** — pretraining on prose; never saw
   instruction/QA format dominance. Loss ~4.4 (Run3) still high.
2. **Bengali generation absent** — greedy EOS immediately on BN prompts;
   bn_mixed corpus may not teach script generation.
3. **Math-template overfit** — outputs mimic "<<a*b=c>>" GSM8K-style
   patterns from reasoning_arithmetic data regardless of prompt.
4. **No instruction tuning** — format requests ignored entirely.

## Website integration (verified earlier)
Deterministic handlers answer greeting/identity/math-tool; everything else
→ this same weak neural net or labeled fallback. Honest but low-value.

## Run3 vs Run4
Run4 checkpoint VERIFIED (sha `761a5b14…`, ep5/step9213, strict load PASS,
0 empty/0 leak mechanical on 18-prompt suite). **Semantic comparison:
INCONCLUSIVE** — need `ACTUAL_GENERATION_SAMPLES.json` from
`NEXUSAI_RUN4_AUDIT/audit_20261116_210128/` (Drive-only, not accessible
locally). Mechanical metrics suggest Run4 may fix empty-EOS behavior
(0/18 empty vs Run3's pattern), but quality unknown.

## Verdicts
- Run3 usable for users? **NO** — cannot answer reliably (verdict C).
- Run4 better? **UNKNOWN** — needs samples review.
- Ready for real users? **NO** — needs SFT + possibly more pretraining.
- Biggest problems: (1) no instruction/conversation training, (2) Bengali
  generation absent, (3) math-template overfit + high loss.
- Fix first: Run4 semantic eval → targeted pretraining/SFT data → SFT.
- Missing evidence: Run4 raw outputs; Run4 Bengali generation test.

## FINAL VERDICT: **C — MODEL CAN GENERATE TEXT BUT CANNOT ANSWER RELIABLY**
(for Run3, fully evidenced; Run4 pending sample review → likely same class)
