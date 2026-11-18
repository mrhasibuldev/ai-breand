# NexusAI Four-Core Test & Benchmark Report

**Date:** 2026-11-18 · CPU-only · Evidence: `eval_reports/stage1_four_core_generation.json`, `eval_reports/four_core_test_suite.json`

## Suites executed

| Suite | Command | Cases | Result |
|---|---|---|---|
| Stage-1 generation matrix | `python packages/ai-core/evaluation/verify_four_core_generation.py --models nexus-core-01,nexus-core-02,nexus-core-03,nexus-core-04,nexus-medium --max-new-tokens 48` | 24 prompts x 5 models | all strict loads PASS; see JSON |
| Four-core test suite | `python packages/ai-core/evaluation/four_core_test_suite.py` | core-01: 56 authored; core-02: 132 held-out; core-03: 87 held-out; core-04: 31 held-out | see below |
| Repair regression | `python packages/ai-core/tests/four_core/test_generation_repairs.py` | 6 tests | 6 PASS, 0 FAIL |

## Held-out results (deterministic scoring only — no external AI evaluator)

| Core | Non-empty | Empty rate | Metric | Value | Interpretation |
|---|---|---|---|---|---|
| core-01 | 38/56 | 32.1% | mechanical flags | 18 EMPTY (immediate EOS) | undertrained base LM; PARTIALLY VERIFIED |
| core-02 | 132/132 | 0% | mean surface-sim vs reference | 0.884 | high sim = template memorization, NOT reasoning; PARTIALLY VERIFIED |
| core-03 | 87/87 | 0% | numeric oracle (exact match) | 8/87 = 9.2% | FAILED quality gate (consistent with prior 9% arith eval); format correct, math unreliable |
| core-04 | 31/31 | 0% | mean surface-sim vs reference | 0.900 | strong memorized-KB recall on its 318-record corpus; PARTIALLY VERIFIED (narrow domain) |

Core-01 authored-set detail: outputs are English-biased document-continuation text with math-corpus artifacts (`<<a+b=c>>`, `####`); Bengali/Banglish prompts mostly produce English text or immediate EOS. Language consistency: poor.

## Language coverage

Prompts covered en / bn / banglish / mixed across greeting, conversation, knowledge, reasoning, mathematics, follow-up. Bengali script generation verified mechanically (UTF-8 preserved in JSON); semantic Bengali quality is NOT VERIFIED for any core except core-04's memorized Bengali KB sentences.

## Multi-turn

Single-turn only in the current inference path (`chat_generate`, `InferenceEngine.generate`). Five context probes per core embedded prior-turn text inline; no dedicated multi-turn state was tested — marked PARTIALLY VERIFIED / NOT VERIFIED for true multi-turn.

## Error handling

- Strict-load failures: none (all 0 missing / 0 unexpected keys).
- Generation exceptions: 0 across 306 suite generations + 120 matrix generations.
- EMPTY_OUTPUT correctly surfaced as warning/status, never disguised as success.

## Performance (CPU, per generation)

core-01 ~0.44 s, core-02 ~0.51 s, core-03 ~0.13 s, core-04 ~1.18 s average (48 tokens, greedy). Process RSS after model load: ~270–775 MB depending on model size.

## Honesty notes

- `surface_sim` measures token overlap with reference answers; for core-02 it is inflated by template duplication — it is NOT a correctness metric.
- No model demonstrated reasoning, understanding, or general knowledge. Claims are limited to: strict load VERIFIED, neural generation VERIFIED (mechanical), semantic quality PARTIALLY VERIFIED / FAILED per the table above.
