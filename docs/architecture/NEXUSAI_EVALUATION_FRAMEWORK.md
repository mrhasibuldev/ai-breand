# NEXUSAI EVALUATION FRAMEWORK

## Principle
Training loss ≠ intelligence. Held-out tests only. Same prompts/decoding for model comparisons.

## Existing assets
- `scripts/eval_core01_run3.py` — 22-prompt multilingual suite (run3 baseline: cpu_eval.json)
- `eval_reports/forensic_orchestrate.json` — 13-test routing audit
- `eval_reports/provenance_audit.json` — provenance tests
- `reasoning_test.jsonl` — 300 held-out reasoning examples (leak-free)

## Benchmark categories (target suite)
Language: BN→BN, EN→EN, Banglish, mixed, language-consistency
Knowledge: facts, self-intro, creator identity (Hasibul), architecture honesty
Math: arithmetic, word problems, multi-step (tool-assisted vs neural separated)
Reasoning: logic, ordering, contradiction, uncertainty/abstention, decision
Reliability: hallucination (fake entities), repetition/gibberish rate, consistency
Technical: load time, RAM, tok/s, offline, strict-load, SHA-256

## Scoring
- Deterministic checks where possible (math exact, language script, abstention keywords)
- Human review for open-ended
- Report per-language + per-category; never aggregate-hide failures

## Current baselines
- run3: all 22 prompts off-topic/generic (documented)
- medium: gibberish (documented)
- run4: pending
