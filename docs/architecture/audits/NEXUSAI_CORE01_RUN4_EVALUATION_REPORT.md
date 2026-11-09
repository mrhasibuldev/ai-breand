# NEXUSAI CORE-01 RUN4 EVALUATION REPORT

**Status: PENDING — requires trained run4 checkpoint**

## Plan (same suite as run3 for comparability)
- `scripts/eval_core01_run3.py` adapted → run4 path
- Categories: EN/BN/Banglish/math/reasoning/decision/abstention
- Same prompts, greedy, 48-64 tokens, CPU
- Compare run3 baseline (cpu_eval.json) vs run4 verbatim
- Metrics: language-consistency rate, on-topic rate, math accuracy, abstention correctness, tok/s, RAM

## Run3 baseline (verified)
- 22 prompts: all off-topic/generic; BN→English; math wrong; hallucination on fake entities
- CPU: 42.6 tok/s, 382MB RAM
