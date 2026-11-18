# NexusAI Run5 SFT Readiness Verdict
Date: 2026-11-17

| gate | status |
|---|---|
| Dataset readiness | READY WITH CONDITIONS (103 smoke-scale, balanced, clean) |
| Tokenizer readiness | READY (hash-verified, roundtrips pass) |
| Model architecture | READY (strict load proven Run3+Run4) |
| Checkpoint readiness | READY (Run4 sha 761a5b14…, Drive) |
| Training code | READY WITH CONDITIONS (driver proven; SFT cell preflight unrun) |
| SFT masking | READY (tensor-verified) |
| Validation readiness | CONDITIONAL (val=5 tiny) |
| Evaluation readiness | READY (eval_prompts.json + rubric + /eval/run) |
| CPU training feasibility | IMPRACTICAL (8.8M model CPU train = hours-days; use GPU) |
| Free-GPU feasibility | READY (T4 sufficient, est. minutes) |
| Checkpoint recovery | READY (save/resume proven in driver) |
| Reproducibility | READY (seeded, hashes, manifests) |

## FINAL VERDICT: READY WITH CONDITIONS
**Can Run5 SFT begin safely today? YES — with conditions:**
1. Upload sft_v2/ to Drive/Colab (train+val+test+manifest)
2. Run preflight cell (TRAINING_ENABLED=False) on GPU → verify all PASS
3. Explicit Phase-F approval → set TRAINING_ENABLED=True, EPOCHS=3, LR=2e-5
4. New output dir NEXUSAI_RUN5_SFT — never touch Run4
5. Post-SFT: run eval_prompts suite + /eval/run before/after comparison

Blockers (priority): (a) sft_v2 not yet on Colab, (b) preflight unrun,
(c) Phase-F approval pending, (d) dataset smoke-scale → set expectations.
