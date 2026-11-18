# NexusAI Four-Core Development Baseline (PHASE 0)
Date: 2026-11-17 · READ-ONLY

## Verified model inventory
| model | impl | params | ckpt | tok | inference | quality | status |
|---|---|---|---|---|---|---|---|
| Core-01 Run3 | NexusAICore01 6L/256/8h | 8,842,560 | local sha ad515cad… | sp_bpe_8k | VERIFIED | poor (47% empty) | ACTIVE serving |
| Core-01 Run4 | same arch | 8,842,560 | Drive sha 761a5b14… | same | VERIFIED (Colab) | poor (45% empty) | verified, not activated |
| nexus-medium | MediumTransformer 2L/128/2h | 2,468,928 | local | same | loads but ALL-EOS | none | fallback (effectively dead) |
| Core-02 | none | — | — | — | — | — | NOT IMPLEMENTED |
| Core-03 | none | — | — | — | — | — | NOT IMPLEMENTED |
| Core-04 | none | — | — | — | — | — | NOT IMPLEMENTED |

## Verified chain (live)
web ChatInterface.tsx → POST :4000/api/v1/ai/chat → apps/api routes/ai.ts
→ intelligence-engine.ts → POST :8000/orchestrate → model_router →
registry(core01) → InferenceEngine → neural output.
Provenance labels verified earlier (neural:nexus-core-01, sha recorded).

## Existing reusable assets
- transformer.py / inference.py / tokenizer_interface.py / model_config.py
- training.py + pretraining_driver.py (resume/AMP/accum/checkpoint)
- sft_dataset.py (chat serialization + response-only masking, tensor-verified)
- model_registry.py + model_router.py (validated lifecycle + routing)
- safety_guard.py + metrics/eval endpoints
- eval suite evaluation/core01_sft_v2/

## Hard constraints
- Run5/SFT explicitly OUT OF SCOPE this mission
- No training without separate approval; new artifacts → versioned dirs
- CPU-only local (~8GB); Colab T4 free tier for any future training
- No external AI anywhere

## Baseline verdict
Core-01 needs quality improvement (SFT later, not now). Core-02/03/04
must be built as genuinely independent models — new configs, weights,
checkpoints, evals. Medium is dead-weight fallback.
