# NexusAI Core-05 General Intelligence Blueprint

## What Core-05 is
A NEW independently configured+trained decoder-only Transformer intended
as NexusAI's general-purpose conversational brain — NOT a renamed
checkpoint, NOT a wrapper, NOT Run5.

## Run5 vs Core-05 (decision basis)
- Run5 = next SFT run on existing Core-01 (8.8M, conv-focused).
  Readiness verdict exists; pending approval; improves specialist.
- Core-05 = new model: larger capacity + generalist training corpus.
  Justified because: (a) 4 specialists share one small impl and each is
  narrow; (b) general conversation needs broader data+capacity than any
  single specialist; (c) long-term goal is a general brain with
  specialists as needed components.
- RECOMMENDATION: pursue Core-05 as the general brain; Run5 remains an
  optional Core-01 improvement track. They are complementary, not
  interchangeable.

## Capability spec (measurable, staged)
1. Trilingual conversation (bn/en/banglish/mixed) — language-consistent.
2. Multi-turn context retention (6-12 turn conversations).
3. Instruction following (single+multi-requirement).
4. Reasoning with verifiable steps (math/logic/causal).
5. Honest uncertainty + self-correction + clarification.
6. General knowledge with hallucination resistance.
7. Social conversation within safety boundaries.
Each capability gated by unseen benchmarks (see eval doc).

## What success is NOT
Not: loss decrease, checkpoint save, memorized answers, demo fluency.
Success = sustained unseen-benchmark performance + CPU inference +
reproducible evals (thresholds in acceptance-gates doc).
