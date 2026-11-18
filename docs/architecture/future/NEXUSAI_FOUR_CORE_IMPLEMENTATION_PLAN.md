# NexusAI Four-Core Implementation Plan (VALIDATED PHASE 0)
Date: 2026-11-17 · verified against repo @ a8cc48b (139 uncommitted/untracked entries)

## Verified baseline (re-checked)
- HEAD `a8cc48b`; Core-01=only real model (Run3 serving, Run4 Drive-verified)
- nexus-medium dead (all-EOS); Core-02/03/04 NOT IMPLEMENTED
- chain: ChatInterface→:4000/api/v1/ai/chat→intelligence-engine→:8000/orchestrate→core01 — VERIFIED live
- reusable: transformer.py, inference.py, tokenizer_interface.py, model_config.py,
  training.py, pretraining_driver.py, sft_dataset.py, model_registry.py,
  model_router.py, safety_guard.py, metrics/eval endpoints, eval suite

## Per-model development spec (all UNTRAINED until approved GPU runs)

### Core-02 — Reasoning/Problem-Solving
- arch: independent config, reuse transformer blocks; proposal 8L/d384/12h/d_ff1536/max512 ≈ ~22M params (own weights, NOT Core-01 copy)
- tokenizer: shared sp_bpe_8k v1 (justified: same multilingual vocab; document)
- dataset: `build_core02_reasoning.py` — deterministic logic templates:
  deduction, ordering, constraints, planning, contradiction, insufficient-info;
  en+bn+banglish; verified answer keys; target ~2-4k records, splits, provenance
- eval: `evaluation/core02_reasoning/` — exact-answer scoring (not vibes)
- quality gate (pre-registered): exact-match ≥60% on held-out logic set,
  empty-rate ≤10%, no deterministic-handler substitution
- compute: T4 ~30-90min; ckpt ~250MB fp32

### Core-03 — Mathematics
- arch: independent config 6L/d256/8h (same scale as C-01 but OWN weights);
  digit/operator-aware serialization "3 + 5 = ?"
- dataset: `build_core03_math.py` — deterministic arithmetic generator:
  +−×÷, fractions, percentages, 2-step word problems; en+bn+banglish;
  ~5-10k records (procedural → easy to verify correctness)
- eval: exact numeric match + explanation presence; deterministic calc
  allowed ONLY as labeled tool, never counted as neural score
- quality gate: arithmetic exact-match ≥90% (procedural data makes this
  reachable), word-problem ≥50%, empty ≤5%
- compute: T4 ~30-60min; ckpt ~107MB

### Core-04 — Knowledge Processing
- arch: independent config 8L/d512/8h/d_ff2048/max512 ≈ ~45M params
- dataset: hardest — needs license-clean QA/explanation corpus;
  start with self-built concept cards + existing corpus subsets;
  HONEST: knowledge quality will be limited by 8k vocab + small model
- eval: factual QA exact/contains-match, summarization rubric, uncertainty tests
- quality gate: contains-match ≥40% on curated set, hallucination flag rate measured
- compute: T4 ~1-2h; ckpt ~500MB — largest of the four

### Core-01 — quality path (NOT Run5)
- Current: Run3 serving (poor), Run4 verified (poor). Improvement requires
  training — explicitly deferred; will be presented as separate approval
  (SFT or continued pretraining) AFTER four-core scaffolding, per mission rule.

## Execution sequence (each step = separate approval)
1. Core-02 scaffold: config+class+dataset+cell(TRAINING_ENABLED=False)+eval — CODE ONLY
2. Core-03 scaffold: same pattern
3. Core-04 scaffold: same pattern
4. Registry: add entries status=UNTRAINED/SCAFFOLDED — router refuses unverified
5. Router: extend intent classes (reasoning/math/knowledge) → map to future models
6. Chat e2e: verify existing chain still works; attribution extended
7. Docs: README truth-update + per-model docs (marked UNTRAINED)
8. Release prep: LICENSE decision + triage + secret scan → approval → push
9. [SEPARATE APPROVAL] GPU training runs for C-02/03/04 (Colab T4 cells)
10. [SEPARATE APPROVAL] post-training eval + activation decision

## Approvals required from user
A1: implement Core-02 scaffold (code+data, no training)
A2: implement Core-03 scaffold
A3: implement Core-04 scaffold
A4: registry/router changes (untrained entries, no serving)
A5: docs update
A6: release prep + LICENSE choice + push approval
A7+: each model's GPU training run (later, after scaffolds verified)

## Risks
- Untrained models must NEVER serve — status gates enforce
- Core-04 data scarcity → may stay weakest; document honestly
- 3 new ~20-45M models on T4: feasible but hours total; free-tier limits
- Dataset licensing for Core-04 must be verified before use
