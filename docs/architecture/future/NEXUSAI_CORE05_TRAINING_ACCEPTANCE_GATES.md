# NexusAI Core-05 — Training Acceptance Gates

**Status:** PLAN ONLY. No model trained; no performance claimed.

## 1. Evaluation principles

- **Unseen test data only** — V5 test split + independent benchmark; never train on eval items.
- **No external AI evaluator** — deterministic metrics + human rubric only.
- Separate: train loss, val loss, independent test metrics, human eval.

## 2. Proposed gates (must pass before "usable" claim)

| Gate | Capability | Proposed threshold (to be finalized) |
|---|---|---|
| G1 | English conversation | coherent, on-topic, grammatical on ≥80% of unseen cases (human-scored) |
| G2 | Bengali conversation | natural Bengali script, grammatical, relevant |
| G3 | Banglish | natural Romanized Bengali, not gibberish |
| G4 | Mixed/code-switch | maintains context across language switches |
| G5 | Multi-turn context | answers follow-ups correctly using earlier turns |
| G6 | Reasoning | correct on verifiable logic problems; shows steps |
| G7 | Decision-making | compares options with stated trade-offs |
| G8 | Mathematics | correct answers on held-out verified problems |
| G9 | Knowledge | accurate on verifiable facts; admits unknowns |
| G10 | Uncertainty/self-correction | says "I don't know" rather than hallucinating; corrects errors when shown |
| G11 | Instruction following | follows multi-constraint instructions |
| G12 | Clarification | asks when requirements are ambiguous |

## 3. Metric plan

- **Automatic:** val/test cross-entropy loss; exact-match on math/logic subsets; token-level fluency proxies.
- **Human rubric:** naturalness, relevance, correctness, language consistency — scored on a fixed sample (e.g., 50–100 cases per capability).
- **No claim of "general intelligence"** regardless of scores — gates measure specific capabilities only.

## 4. Benchmark suites needed (depend on V5)

Per-capability unseen case sets for: en, bn, banglish, mixed, multi-turn, reasoning, decision, math, knowledge, uncertainty, self-correction, clarification, instruction-following. Target ≥100 cases per major capability where feasible — must be authored/verified independently of training data.

## 5. Current status

- V5 benchmark suite: **does not exist** (blocked on V5).
- v4 has splits but no formal independent benchmark.
- No model exists to evaluate.

**Verdict: PARTIALLY READY** — framework defined; execution blocked on V5 + trained checkpoint.
