# NexusAI Core-01 — Complete Forensic Model Audit

**Date:** 2026-11-16 · READ-ONLY · evidence from this repo + executed local tests

## 1. Executive Summary
NexusAI owns a real Transformer (Core-01, 8.84M) with verified training
pipeline, hash-pinned Run3 checkpoint on GitHub LFS, working CPU inference
(fixed this session), and a registry/router path to the web app. Run4
reportedly completed on Colab (step 9213) — **NOT independently verified**
(Drive-only). Model is pretrained only — no SFT. Quality is weak but real.

## 2. Model Identity & Architecture — VERIFIED PASS
`core01/transformer.py::NexusAICore01` — 6 pre-norm blocks, d256, 8H,
FFN1024, vocab8000, len512, sinusoidal PE. `count_parameters()`=8,842,560.
Key family `transformer_blocks.*`. phase10 ckpt = different arch (documented).

## 3. Training History
- **Run3:** VERIFIED — ep3/step1341, sha `ad515cade…7830`, full resume state, on GitHub LFS (main), fresh-clone verified.
- **Run4:** PREVIOUSLY REPORTED — ep5/step9213, losses ~3.18/2.92, sha `761a5b14…`, Drive path `/content/drive/MyDrive/NEXUSAI_RUN4/` — **NOT INDEPENDENTLY VERIFIED IN THIS ENVIRONMENT**. Must be hash-checked in Colab/Drive.

## 4. Dataset — PARTIAL
216,193 rec, sha `5f8572ed…`, schema `{text,category,lang,source}`, 0 malformed.
~62% EN, BN mostly encyclopedic, 459 Banglish, 6,922 dup texts. Good for LM;
**insufficient for conversation/instruction** → SFT required.

## 5. Inference — VERIFIED PASS (post-fix)
`core01/inference.py` fixed this session: BOS-only prompt (no terminal EOS),
generated-token slicing (no prompt leak), EMPTY_GENERATION warning,
inference_mode. CPU test: ~40 tok/s, <1s/short gen. **Model quality still
weak** — greedy often emits EOS immediately on short prompts (undertrained,
not a code bug). Benchmark v2 (Run3): lang_match 50%, BN output 0%, kw-hit 3.8%.

## 6. Checkpoint Metadata Bug — VERIFIED
`ckpt["config"]["model_status"]`="UNTRAINED" vs top-level "PRETRAINING_COMPLETED".
Cosmetic but blocks InferenceEngine's status gate (returns empty+warning).
Fix = set config status at save time (future approved patch).

## 7. Website Integration — PARTIAL (two paths found)
- `/orchestrate` + `/inference` → `model_router.brain.respond()` →
  `model_registry` → `loader:"core01"` → `create_inference_engine` →
  **real Core-01, CPU, lazy-loaded once, provenance traced** ✅
- Legacy path: `main.py::load_model_if_needed` loads **MediumTransformer**
  (different arch, `checkpoints_medium/final_model.pt` fallback) for older
  endpoints — coexistence risk: ensure chat traffic uses /orchestrate.
- Deterministic handlers run BEFORE neural in router (labeled, honest);
  fallback exists but is explicitly marked `fallback:true` — not disguised.

## 8. External AI Dependencies — VERIFIED CLEAN
No OpenAI/Anthropic/Gemini/HF-inference in core paths (grep clean).
Only torch/sentencepiece/numpy/psutil + hand-written handlers.

## 9. CPU Performance — MEASURED (this machine)
~38-45 tok/s, ~1s per 48 tokens, CPU-only confirmed, model ~35MB FP32.
Production server untested — needs load test before claims.

## 10. Scaling Roadmap (planning only)
P0 verify Run4 → P1 SFT data+pipeline → P2 re-benchmark → P3 ~25-30M model
only if evidence justifies → P4 CPU-optimized serving. Bigger ≠ smarter;
data+SFT first.

## 11. Status Table
| Area | Status |
|---|---|
| Own model exists & trained | VERIFIED PASS |
| Run3 checkpoint | VERIFIED PASS |
| Run4 checkpoint | NOT VERIFIED (Drive-only) |
| Inference fix | VERIFIED PASS (local CPU) |
| Bengali generation | PARTIAL (weak) |
| English generation | PARTIAL (weak) |
| Banglish | PARTIAL (detects, generates poorly) |
| Instruction following | NOT DEMONSTRATED (no SFT) |
| Reasoning | NOT DEMONSTRATED |
| CPU inference | VERIFIED PASS |
| Website→Core-01 path | PARTIAL (router OK; legacy medium path coexists) |
| External AI deps | VERIFIED NONE |
| SFT readiness | READY FOR DATA PHASE (approval needed) |
| Larger model | NOT JUSTIFIED YET |

## 12. Verdicts
Own AI model? **YES** · Trained? **YES (Run3 verified; Run4 reported)** ·
Run4 verified? **NO (needs Drive check)** · Inference fix? **YES** ·
Meaningful BN/EN/Banglish? **NO (weak)** · Instructions/reasoning? **NO** ·
CPU? **YES** · Website uses own model? **YES via /orchestrate** ·
External AI? **NONE** · Ready for SFT? **YES (pending approval)** ·
Larger model? **NOT YET**

## 13. Single most important next step
**Verify Run4 checkpoint hash in Colab/Drive, then run neural_benchmark_v2
against it** — that tells us if Run4 actually improved quality before any
SFT or scaling decision.
