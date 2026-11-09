# NEXUSAI AI BRAIN — DEVELOPMENT ROADMAP

## Phase A — CORE STABILITY (current)
Stabilize arch/config, reproducible training, eval harness, preserve checkpoints. **Status: mostly done** — remaining: eval harness standardization.

## Phase B — RUN4 MULTILINGUAL TRAINING
Use prepared 60M-token corpus (60% BN), resume run3→run4, verify sampling, safe ckpts, eval vs run3. **Status: PREPARED — awaiting Colab.**
Deliverable: run4 checkpoint + comparison report. Success: Bengali output ≥80%, val_loss <4.0, no English regression.

## Phase C — DATA QUALITY & SCALE
Expand BN+EN high-quality data, dedicated Banglish corpus, more reasoning/decision/planning examples, better dedup (MinHash), license tracking. Do NOT grow volume without quality metrics.

## Phase D — MODEL CAPABILITY
Evaluate if 8.8M/ctx512 is sufficient; controlled experiments on size/context; architecture changes only with migration plan + evidence.

## Phase E — REASONING & DECISION-MAKING
Math reasoning, multi-step logic, planning, uncertainty, evidence-based answers, tool-use training, independent benchmarks. Memorization ≠ generalization — measure held-out only.

## Phase F — CONTEXT & MEMORY
Session context, user-controlled memory, consent boundaries, account isolation, privacy/deletion, retrieval eval.

## Phase G — AGENT MODE
Tool registry, permission system, task planning, multi-step execution, error recovery, user approval for sensitive actions, execution logs, sandboxing.

## Phase H — LOCAL INFERENCE
Download ckpts, SHA-256 verify, CPU inference, memory optimization, quantization research (INT8/INT4 — not yet implemented), offline operation, hardware compat, perf measurement.

## Phase I — PUBLIC NEXUSAI API
Stable API, auth, rate limits, usage monitoring, model versioning, privacy/security, NO external AI keys required from users.

## Phase J — DIRECT VOICE CONVERSATION
See `NEXUSAI_REALTIME_VOICE_CONVERSATION_ROADMAP.md`. STT + TTS as interface layers feeding OUR model — never a third-party chatbot.

## Phase K — LONG-TERM RESEARCH
Advanced reasoning, continual learning w/ safeguards, multimodal, long context, autonomous research w/ approval, efficient training, low-cost compute, responsible deployment.

## Guiding rule
No dates promised; every phase gated by measurable evaluation, not hype.
