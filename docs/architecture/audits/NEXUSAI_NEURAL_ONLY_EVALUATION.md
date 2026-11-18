# NEXUSAI — NEURAL-ONLY EVALUATION (Gate B)

**Date:** 2026-11-10 · Mode: `neural_only:true` → all deterministic handlers bypassed
**Model:** nexus-core-01 · ckpt `checkpoints_core01_run3/checkpoint_final.pt` · sha256 `ad515cad…7830` · tokenizer sp_bpe_8k vocab 8000
**Data:** `eval_reports/nexusai_neural_only_evaluation.json` (22 tests, all executed)

## Result summary
- **Routing/provenance: 22/22 PASS** — every response `route=neural:nexus-core-01`, `neural_ran=true`, checkpoint+tokenizer recorded
- **Output quality: 0 PASS / 0 PARTIAL / 22 FAIL** — honest classification. Outputs are disfluent English-ish fragments regardless of input language; Bengali/Banglish prompts produce English text; context not exploited; math wrong.

## Per-category (all FAIL quality)
| Cat | Tests | Result |
|---|---|---|
| English (7) | hello/who/creator/AI/sky/computer/ML | coherent-sounding fragments, wrong content |
| Bengali (5) | তুমি কে? etc | English output — language mismatch |
| Banglish (4) | Tumi ke? etc | English output — language mismatch |
| Context (3) | physics topic + follow-ups | context concatenated into prompt; model ignores it |
| Generalization (1) | zorblax… | template-like non-answer |
| Reasoning (2) | 17+25, cat→animal | wrong arithmetic/logic |

## What this proves
1. Neural-only mode works: no canned/fallback/tool can masquerade as neural.
2. Core-01 run3 generates real tokens via forward passes — but is **undertrained**; quality gate for "useful conversational AI" is **FAILED** until Run4+.
3. Deterministic handlers remain the only source of clean answers today — by design, labeled.

## Context proof status
History normalization verified (13/13 unit tests) and `history` key now reaches `_normalize_history` → prompt context join (last 3 msgs). Whether the weak model *uses* context: NOT VERIFIED — outputs show no evidence of it.
