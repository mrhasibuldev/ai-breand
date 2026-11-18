# Reasoning / Decision / Uncertainty Data Spec (v2 as-built + v3 needs)

## As-built in v2 (VERIFIED counts)
- reasoning 13: syllogisms, ordering, odd-one-out, conditional rules —
  en/bn/banglish, verified deterministic answers.
- decision 7: budget/time/priority decisions with constraint+conclusion.
- self_correction 4: detect-error→correct→explain pattern.
- clarification 5: ambiguous referent → ask for specification.
- uncertainty 27: live-data cutoff, personal info, dangerous requests,
  future prediction, philosophical openness.
- refusal 4: weapons, malware, hacking, fake reviews.

## Format conventions
- Reasoning answers state the rule then the conclusion.
- Decision answers name the constraint, compare options, conclude,
  explain briefly; ask for missing info when insufficient.
- Uncertainty answers distinguish known/cutoff/unknown explicitly.
- Self-correction: acknowledge error → state correct fact → thanks.

## v3 expansion needs (priority order)
1. Multi-turn scenarios: 35 → 300+ (5 more topics × languages × slots).
2. Bengali+Banglish conversational depth (bn 32%→40%, banglish 15%→20%).
3. Self-correction 4 → 40+; clarification 5 → 40+.
4. Reasoning/decision 20 → 150+ with unseen-combination eval split.
5. Math worked-solutions (steps format) for core03.
6. Uncertainty: ambiguous-question and insufficient-evidence classes.

## Evaluation isolation rule
Benchmark prompts authored SEPARATELY from training seeds; group-hash
splits keep paraphrase clusters atomic; benchmark never enters training.
