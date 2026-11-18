# NEXUSAI — NEURAL GENERATION PROVENANCE AUDIT

**Date:** 2026-11-10 · READ-ONLY · No files modified · Evidence: `eval_reports/provenance_audit.json`

## FINAL VERDICT
**Core-01 Run3 IS genuinely generating responses with its trained parameters** for ordinary questions routed to the neural path. However, a meaningful subset of intents (greeting/identity/capability/thanks/math) intentionally uses deterministic handlers — by design, honestly labeled. Retrieval systems exist in code but are disabled and cannot answer.

## Runtime proof of neural generation
Direct engine test (`model_registry` → `core01.inference.InferenceEngine`):
- Checkpoint: `checkpoints_core01_run3/checkpoint_final.pt`, sha256 `ad515cad…7830`, strict `load_state_dict` PASS, status `PRETRAINING_COMPLETED`
- Tokenizer: `NexusAITokenizer` wrapping sp_bpe_8k, vocab 8000 ✅
- **Instrumented `model.forward`**: exactly **25 forward calls per 25-token generation** (autoregressive, one call per token) — proves real forward passes
- 3 different prompts → 3 different outputs → not canned

## The 5 required tests (live /orchestrate)

| Test | Input | Route | neural_ran | Response (verbatim head) | Classification |
|---|---|---|---|---|---|
| A_bn | পাহাড় কী? | neural:nexus-core-01 | ✅ true | "Rails and Jrava is an adds of the following…" | **NEURAL** (weak semantics) |
| B_en | What is a mountain? | neural:nexus-core-01 | ✅ true | "Syaiarate is an area of the magicipl…" | **NEURAL** (weak) |
| C_bl | Mountain mane ki? | neural:nexus-core-01 | ✅ true | "The number of furs are on the city…" | **NEURAL** (lang detected 'english' — minor miss) |
| D_unfamiliar | airspeed velocity of unladen swallow in Dhaka? | neural:nexus-core-01 | ✅ true | unique generated text, no canned match | **NEURAL** — proves no prepared answer exists |
| E_prev_handler | তোমার নাম কী? | registry:identity_metadata | ❌ false | "আমি NexusAI — Hasibul…" | **DETERMINISTIC** (intentional, verified metadata) |

## Complete path inventory

**Deterministic (never neural, by design):**
- `model_router.py`: GREETING/THANKS/FAREWELL answers, IDENTITY/CAPABILITY metadata, `try_math_tool` arithmetic
- These are fixed strings, labeled `route=deterministic:*` / `registry:*` / `tool:math` in trace — never disguised as neural

**Neural:**
- `model_router._generate_neural` → `registry.generate("nexus-core-01")` → `core01.inference.InferenceEngine.generate` → `NexusAICore01.generate` (forward pass per token)
- Fallback model `nexus-medium` only if core01 fails/degenerate

**Retrieval (cannot answer):**
- `main.py`: `simple_retrieval`/`rag_system` imports exist but usage is **commented out** ("DISABLED for neural testing"); brain path returns before legacy block anyway
- No document/dataset lookup in active path

**Fallback:**
- `FALLBACKS` dict = fixed apology strings per language, only when neural output empty/degenerate — never contains answers

## Per-question provenance fields (in trace)
`model_used`, `route`, `neural_ran`, `tool`, `fallback`, `provenance{model_id, checkpoint, engine}` — every response is traceable.

## Limitations (honest)
- Neural outputs are fluent-ish but **semantically weak/wrong** — undertrained model (english_first only). Provenance ≠ quality.
- Banglish detection missed "Mountain mane ki?" (detected english) — still routed neural correctly.
- Medium fallback path not deeply exercised (emergency only).
- Bengali-digit math (২৫০ টাকার ২০%) goes to neural, not tool.

## What this means
NexusAI is **NOT** primarily returning pre-written answers for open questions — Core-01 run3's trained weights genuinely generate the text. The deterministic parts are intentional, labeled, and limited to greetings/identity/capability/math. The real problem remains **model capability**, solvable only via Run4 training — not a provenance fraud.
