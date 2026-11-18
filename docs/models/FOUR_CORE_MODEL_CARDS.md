# NexusAI Four-Core Model Cards (SFT v1/v2 — local CPU runs)

Honest status: all three specialists share the Core-01 pre-norm decoder-only
Transformer *implementation* with independent configs/weights/data/checkpoints.
They are task-specialist SFT models trained from random init on curated datasets.
NOT distinct architectures. NOT production-ready without quality gates.

## Core-02 — Reasoning specialist
- Config: d_model=384, layers=8, heads=12, d_ff=1536, max_len=512, vocab=8000
- Params: 20,347,712
- Dataset: data/core02_reasoning — 2,650 recs (ordering/comparison/deduction/
  constraint/multistep/contradiction/uncertainty/planning), EN/BN/Banglish,
  deterministic template generation, question-level hash split (0 exact-Q overlap)
- v1 ckpt: models/checkpoints_core02_sft_v1/checkpoint_final.pt
  sha256=e02df55fe1cd57a4f907dceff93a67cd0749828c65a014c47a16c2a6b29899a6
  598 steps, val_loss 0.034 — TRAINED on pre-fix split; eval INVALID (leakage)
- v2 ckpt: checkpoints_core02_sft_v2 — retraining on clean split (in progress)
- Known limit: template-generated data → measures slot-fill generalization,
  not novel reasoning. multistep category was 0% even in contaminated eval.

## Core-03 — Mathematics specialist
- Config: d_model=256, layers=6, heads=8, d_ff=1024, max_len=512, vocab=8000
- Params: 8,842,560
- Dataset: data/core03_math — 1,750 recs (arith/algebra/percent/fraction/
  wordprob), procedural generation + validation, question-level hash split
- v1 ckpt: models/checkpoints_core03_sft_v1/checkpoint_final.pt
  sha256=b6e373bc774060334bf15c3a4f9010b3f33a5d8957a0208de3d0dc59fb3f68fe
  591 steps, val_loss 0.717
- v1 held-out eval (contaminated split): exact_match 11.5%, empty 0%
  — format learned ("x = 2."), arithmetic mostly wrong. Honest: WEAK.
- v2 ckpt: checkpoints_core03_sft_v2 — 8 epochs on clean split (queued)
- Deterministic calculator remains for simple arithmetic (labeled, not neural).

## Core-04 — Knowledge specialist
- Config: d_model=512, layers=8, heads=8, d_ff=2048, max_len=512, vocab=8000
- Params: 33,419,072
- Dataset: data/core04_knowledge — 318 recs from 36 curated static-fact cards
  (qa/explain/classify/summarize/uncertainty), EN/BN, FACT-LEVEL hash split
  (0 test answers in train). NO live/current knowledge — uncertainty trained.
- v1 ckpt: models/checkpoints_core04_sft_v1/checkpoint_final.pt
  sha256=404b8c0f89f32e58fb4f656e7869f8089aabb4cebcf67e98a34b56636a36e97f
  60 steps on old 96-rec split — UNDERTRAINED, superseded by v2
- v2 ckpt: checkpoints_core04_sft_v2 — 20 epochs on 318-rec clean split
- Known limit: narrow curated coverage (~36 topics); not a knowledge engine.

## Shared infra
- packages/ai-core/nexus_core.py — factory, strict load, chat_generate
- packages/ai-core/sft_train.py — response-only SFT (assistant tokens + EOS only)
- packages/ai-core/eval_core.py — held-out evaluator (exact/contains/empty)
- ml-service/model_registry.py — validated registry (hash+strict load gates)
- ml-service/model_router.py — intent→specialist routing, honest fallbacks
- docs/notebooks/COLAB_NEXUSAI_FOUR_CORE_SFT.py — free-GPU reproduction cell
