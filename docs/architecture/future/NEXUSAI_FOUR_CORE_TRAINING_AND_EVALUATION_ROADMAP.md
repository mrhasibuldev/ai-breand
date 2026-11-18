# Four-Core Training & Evaluation Roadmap (proposal — nothing executed)

## Pre-registered eval gates (per core, before any training claim)
- core01: conv benchmark ≥100 prompts (bn/en/banglish/mixed, multi-turn);
  metrics: language-match, coherence(1-5 rubric), empty-rate, attribution.
- core02: ≥100 NOVEL instructions (not template skeletons); exact/partial.
- core03: ≥100 math (arithmetic/word-problem/algebra/fraction); exact +
  numeric-tolerance; bn+en subsets.
- core04: ≥100 (seen-fact, unseen-fact, unknown-refusal, ambiguity);
  hallucination rate + refusal precision/recall.
- Cross-core: language consistency, context retention, self-correction.
All benchmarks authored separately; deterministic scoring where possible;
per-category n reported with confidence limits.

## Training order & configs
See NEXUSAI_FOUR_CORE_INTELLIGENCE_DEVELOPMENT_STRATEGY.md — order:
v3 data → core01 → core04 → core03 → core02. Full fine-tune, bs8,
lr 2-3e-4, response-only loss, new versioned checkpoint dirs, sha256
manifest per run. NEVER overwrite existing checkpoints.

## Colab readiness
`docs/notebooks/COLAB_NEXUSAI_FOUR_CORE_SFT.py` exists (parameterized,
preflight checks). Needs dataset-dir args for v2/v3 + Drive export —
static prep only; DO NOT RUN without approval.

## Rollback & safety
Every run: new dir, sha256 sidecar, eval-before-register. Registry only
accepts hash-verified checkpoints. Neural-only flag stays OFF until
post-training benchmark passes.

## Known blockers
1. v3 dataset expansion (bn/banglish conversational + multi-turn).
2. Human semantic review of bn/banglish records.
3. gsm8k/dolly license verification for optional EN augmentation.
4. Core-01 capacity ceiling — SFT may plateau; Run4-scale pretraining
   is the deeper fix (separately gated).
5. Banglish tokenizer fragmentation — research problem, not quick fix.
