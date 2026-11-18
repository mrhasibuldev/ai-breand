# Core-05 Training Roadmap (staged, gated)

## Stage 0 — Readiness (no training)
Tokenizer eval (bn/banglish fragmentation metrics), V5 dataset build+audit,
benchmark suite authored, Colab preflight dry-run, acceptance gates defined.

## Stage 1 — Continued pretraining (optional, compute-dependent)
On curated general corpus (existing Bengali/English text corpora already
in repo + licensed data) to adapt S-scale weights. Free-T4 feasible for
S-scale only; M-scale needs paid GPU or smaller token budget.
DECISION GATE: only if SFT-only shows capability ceiling on evals.

## Stage 2 — Supervised fine-tuning (SFT)
V5 conversational corpus → trilingual dialogue capability.
S-scale first (pipeline proof), then M-scale.

## Stage 3 — Instruction + reasoning tuning
Worked-solution math/logic, multi-step reasoning, decision examples.

## Stage 4 — Uncertainty/self-correction tuning
Honesty, clarification, correction acceptance/rejection calibration.

## Stage 5 — Evaluation + iteration
Unseen benchmarks per capability; regression vs prior checkpoint;
iterate on measured weaknesses only.

## Methods NOT recommended now
Preference optimization (DPO/GRPO): needs preference data infrastructure
not yet built; defer until SFT baseline measured.
Tool use: out of scope until core chat stable.

## Compute estimates (honest)
S-scale SFT on T4: ~minutes-hours per epoch on ~2-4k records.
M-scale SFT on T4: ~hours per epoch; feasible with grad accum.
Pretraining M-scale: NOT feasible on free tier — requires paid GPU
or accept SFT-only path.
