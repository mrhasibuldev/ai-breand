# NexusAI Agent ↔ Core-01 Run4 Integration Verification

**Date:** 2026-11-16 · LIVE local stack (web:3000, api:4000, ml:8000)

## Executive Summary
**Agent ↔ Core-01 connection: VERIFIED PASS** — genuine neural inference
through the real production path with full provenance. **Run4 usage:
NOT VERIFIED — registry points to Run3.** Response quality: real neural
output but weak (gibberish-leaning, ~0% Bengali script, no instruction
following) — consistent with pretraining-only model.

## Execution Path (verified live)
User → Next.js :3000 → Fastify :4000 → `POST /orchestrate` :8000 →
`model_router.brain.respond()` → intent/language classify →
deterministic handlers (LABELED in trace) → else `registry.generate(
"nexus-core-01")` → `create_inference_engine` → Core-01 CPU → response.

## Provenance (captured live)
```json
"model_used":"nexus-core-01",
"route":"neural:nexus-core-01","neural_ran":true,"fallback":false,
"response_source":"NEURAL_MODEL",
"checkpoint_path":".../checkpoints_core01_run3/checkpoint_final.pt",
"checkpoint_sha256":"ad515cadea433d17…7830",
"engine":"core01","load_s":0.49,"latency_ms":1521
```

## CRITICAL FINDING — Run4 NOT connected
`model_registry.py` MODEL_DEFS["nexus-core-01"].checkpoint =
`checkpoints_core01_run3/checkpoint_final.pt` (Run3). Run4 lives only on
Drive; **no registry entry or pointer references it**. All "neural"
responses currently come from Run3 weights.

## Test Results (12 prompts × normal+neural_only, live)
- Deterministic handlers (greeting/identity/math/thanks/farewell):
  correct labeled Bengali/English answers — honest, not disguised.
- Neural path: all outputs genuine Core-01 text — mostly fluent-sounding
  but semantically wrong English; Bengali prompts → English gibberish;
  2 empty generations; math/reasoning prompts → math-word-problem-style
  gibberish (dataset artifact).
- No external AI anywhere in path. Fallback handler exists but is
  explicitly labeled `route:"fallback"`.

## Status Matrix
| Check | Status | Evidence |
|---|---|---|
| Agent initializes | PASS | server up, brain singleton loaded |
| Agent→ML service | PASS | /orchestrate 200s in logs |
| Router selects Core-01 | PASS | route=neural:nexus-core-01 |
| Run4 checkpoint used | **FAIL** | registry→Run3 path+sha |
| Strict model loading | PASS | load_state_dict strict in engine |
| Correct tokenizer | PASS | sp_bpe_8k, vocab 8000 |
| Direct Core-01 inference | PASS | neural_only outputs are neural text |
| Agent response = neural | PASS (when neural route) | provenance block |
| Bengali neural quality | FAIL | English gibberish on BN prompts |
| English neural quality | PARTIAL | fluent but wrong |
| Banglish | PARTIAL | detected, poor generation |
| Reasoning | FAIL | no evidence |
| Instruction following | FAIL | none |
| No external AI fallback | PASS | grep clean + provenance |
| CPU inference | PASS | this CPU, 0.5s load, ~1.5s/gen |
| Website E2E | PARTIAL | API→ML verified via logs; UI render not pixel-tested |
| Error handling | PARTIAL | neural_failed→"" honest; fallback labeled |

## The honest answer
When a user messages NexusAI: deterministic handlers answer greetings/
identity/math (labeled software logic); everything else goes to **Run3
Core-01 neural net** — genuine own-model generation, but quality is weak.
**Run4 is not yet connected.** No third-party AI involved anywhere.

## Recommended next single action
After Run4 hash verification (`761a5b14…`) + benchmark cell shows
improvement: update `model_registry.py` checkpoint path to Run4 (one-line,
approved change) → re-verify provenance → then SFT phase for quality.
