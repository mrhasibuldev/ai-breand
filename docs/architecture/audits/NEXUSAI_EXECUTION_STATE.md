# NexusAI Execution State — Four-Core Mission

Last updated: this session (continuous execution log).

## Last completed task
- Core-02/03/04 SFT v1 trainings completed on local CPU (real checkpoints, hashed).
- Core-04 dataset builder repaired + expanded 120 -> 318 records.
- Registry: nexus-core-02/03/04 registered with real checkpoint hashes
  (core02 hash pending update — see below); `nexus_sft` loader added.
- Router: intent classes REASONING/KNOWLEDGE added; specialist routing via
  `_try_specialist` (validate-gated, never substitutes silently).
- Core-03 prompt-format bug found+fixed (missing user-turn EOS); re-eval 11.5% exact.

## Verified artifacts
- packages/ai-core/nexus_core.py — model factory, strict load, chat_generate
- packages/ai-core/sft_train.py — response-only SFT trainer (verified end-to-end)
- packages/ai-core/eval_core.py — held-out evaluator
- packages/ai-core/data/build_core0{2,3,4}_*.py — dataset builders w/ manifests+sha256
- packages/ai-core/models/checkpoints_core0{2,3,4}_sft_v1/checkpoint_final.pt
- packages/ai-core/eval_reports/*.json

## Checkpoint hashes (v1)
- core02: e02df55fe1cd57a4... (598 steps, val_loss 0.034) — 20,347,712 params
- core03: b6e373bc77406033... (591 steps, val_loss 0.717) — 8,842,560 params
- core04: 404b8c0f89f32e58... (60 steps, val_loss 3.07, OLD 96-rec dataset) — 33,419,072 params

## In-flight
- core04_sft_v2: 20 epochs on expanded 318-record dataset
- core03_sft_v2: 8 epochs (accuracy improvement attempt)
- core02 held-out eval running

## Known blockers / honest status
- Core-03 v1 exact-match 11.5% — format OK, arithmetic weak (tiny model+data).
- Core-04 v1 undertrained (60 steps); v2 in progress.
- Core-01: Run3 serving, Run4 verified-not-activated; Run5/SFT NOT authorized.
- No Colab GPU used yet; all training so far local CPU.

## Remaining checklist
- [ ] core02 eval results + hash registration
- [ ] core04_v2 + core03_v2 training, eval, hash registration
- [ ] Core-01 verification pass (strict load, trilingual gen)
- [ ] Router E2E via ml-service /orchestrate
- [ ] Chat Interface E2E (desktop+mobile path)
- [ ] Docs (model cards, training report, eval report)
- [ ] Git release scope review + push

## Update 2 (split-integrity remediation)
- FOUND: core02/03/04 datasets had answer/question-level train-test leakage
  (core02: 68/95 test Qs verbatim in train; core04: 24/27 test answers in train).
- FIXED: question-level hash split (02/03), fact-level answer split (04).
  Rebuilt all three datasets; verified 0 exact overlap.
- CONSEQUENCE: all v1 evals invalidated as generalization measures.
- Retraining on clean splits:
  * core02_sft_v2 (2 epochs) — RUNNING
  * core04_sft_v2 (20 epochs, 318 recs) — RUNNING
  * core03_sft_v2 (8 epochs) — QUEUED in same shell after core04
- Router smoke test PASSED mechanically: MATH->nexus-core-03,
  KNOWLEDGE->nexus-core-04, real neural invocation + provenance trace.
  Quality still weak (v1 checkpoints) — registry will be updated to v2
  checkpoints after training+eval.
- Core-01 Run3 verified via registry path: strict-format load OK
  (weights_only=False required — NumPy RNG in ckpt, documented),
  generation works but quality poor (empty EN, incoherent BN/Banglish).
  Run4 preserved untouched. Run5/SFT NOT started (not authorized).

## Update 3 — v2/v3 training complete, E2E verified

### Final checkpoints (all strict-load verified, sha256 recorded)
- core02_sft_v2: 906d6024511f3e8ab48f36d077be391e2eae47573fa4ba29ba8e550c690cbb18
  598 steps, clean question-level split. Held-out eval: exact=0.742,
  contains=0.849, empty=0.0 (n=132). Template-generalization, NOT novel reasoning.
- core03_sft_v2: 1ff83fb9ecd93944969c4086c206e2647c844c182c420b857e2f12b558d5e956
  1576 steps, 8 epochs, clean split. Held-out eval: exact=0.092, empty=0.0 (n=87).
  BELOW quality gate — arithmetic weak; deterministic calculator covers simple ops.
- core04_sft_v3: e46383195d328b9105950939f66b0c36c6363f5b6bc5247c210efa99b5d17c48
  320 steps, 8 epochs, trained on FULL 318-rec curated KB.
  Seen-fact eval (n=30): exact=0.733, contains=0.80.
  Unseen-fact generalization (v2 clean-split proxy): ~0% — memorization model,
  hallucinates plausible wrong facts on unknown topics instead of refusing.

### Registry/router final state
- model_registry.py: nexus-core-02/03/04 -> v2/v3 checkpoints, real sha256,
  nexus_sft loader (strict load + chat format), hash-gated validation.
- model_router.py: intents GREETING/THANKS/FAREWELL/IDENTITY/CAPABILITY (deterministic,
  labeled), MATH->core03 specialist then deterministic tool, REASONING->core02,
  KNOWLEDGE->core04, else core01->nexus-medium fallback. All traces recorded.

### E2E verification (real services)
- ml-service :8000 + api :4000 + web :3000 all running.
- POST /api/v1/ai/chat works unauthenticated (guest mode).
- Direct /orchestrate diagnostic traces verified:
  * "What is gravity?" -> neural:nexus-core-04 -> CORRECT curated fact.
  * "What is 12 x 8?" -> tool:deterministic_math -> "96" (correct, labeled).
  * "Hello!" -> deterministic:greeting.
  * Syllogism -> neural:nexus-core-01 -> gibberish (core01 quality limit).
- Browser preview opened at http://localhost:3000 for UI verification.

### Honest quality summary
- Core-02: VALIDATED WITH LIMITATIONS (74% held-out on template data).
- Core-03: TRAINED, BELOW GATE (9% arithmetic; tool covers simple math).
- Core-04: VALIDATED WITH LIMITATIONS (73% seen-fact recall; ~0% unseen-fact,
  no reliable refusal — hallucination risk on unknown topics).
- Core-01 Run3: serving, poor quality (documented). Run4 preserved. Run5 NOT run.
