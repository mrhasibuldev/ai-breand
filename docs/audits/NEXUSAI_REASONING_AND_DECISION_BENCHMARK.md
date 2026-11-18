# NexusAI — Reasoning & Decision Benchmark (STAGE B)

**Date:** 2026-11-17 · native greedy generation, max 32 tokens, CPU

## Structured reasoning tests — Run3 Core-01
| test | expected | output | result |
|---|---|---|---|
| 7+5 | 12 | EMPTY | FAIL |
| 3+2 apples | 5 | EMPTY | FAIL |
| Monday+3d | Thursday | EMPTY | FAIL |
| iron vs feathers 1kg | equal | EMPTY | FAIL |
| cats→animals (logic) | yes | gibberish | FAIL |

**Score: 0/5.** Arithmetic prompts almost always → immediate EOS.
Logical prompt → irrelevant text. No evidence of reasoning.

## Run4 (from v7 transcript)
| test | expected | output | result |
|---|---|---|---|
| 3+2 apples | 5 | EMPTY | FAIL |
| sun brightness | explanation | irrelevant story | FAIL |

**Score: 0/2.**

## What this means
- Language-model generation ≠ reasoning. Neither checkpoint demonstrates
  arithmetic, logic, planning, comparison, or constraint-solving.
- Deterministic handlers in the router DO solve arithmetic — but those are
  software utilities, NOT neural reasoning, and are labeled as such.
- **No reasoning capability claim is supportable.** Reasoning requires
  targeted SFT/RL data + verified benchmarks — future work.

## Benchmark artifact
Raw outputs preserved in this audit + `/tmp/run3_stageb.json` (session).
Recommend versioning this suite under `evaluation/` for post-SFT comparison.
