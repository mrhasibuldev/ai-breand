# NexusAI Direct Neural Chat — Forensic Audit

Baseline: main @ d2788936afd24f5a823998b013645defca2fd553
Method: read-only code inspection + live `/orchestrate` diagnostic traces
(9 prompts, diagnostic_mode=true). No source modified.

## 1. Live chat execution architecture (VERIFIED)

```
ChatInterface.tsx (app/components/ChatInterface.tsx:235,380)
  -> POST http://localhost:4000/api/v1/ai/chat   (guest + auth modes)
  -> apps/api/src/routes/ai.ts -> intelligence-engine.ts:103
  -> POST http://127.0.0.1:8000/orchestrate       (10s timeout)
  -> ml-service/main.py orchestrate()
       1. safety_guard.check_input  (may return DETERMINISTIC_HANDLER)
       2. model_router.brain.respond()  (NexusBrain)
       3. safety_guard.check_output (may replace neural text w/ fallback)
       4. legacy neural path ONLY if brain import fails
  -> OrchestratorResponse {response, response_source, diagnostics}
```

`response_source` ∈ NEURAL_MODEL | TOOL | FALLBACK | DETERMINISTIC_HANDLER —
already computed honestly in main.py:~915.

## 2. Non-neural answer sources — complete inventory (VERIFIED)

### model_router.py (ml-service)
- `GREETING_ANSWER`, `THANKS`, `FAREWELL` dicts — canned replies.
- `IDENTITY_ANSWER`, `CAPABILITY_ANSWER` — canned replies (labeled
  "registry:identity_metadata" but text is hardcoded).
- `FALLBACKS` dict — language-aware apology strings returned when all
  neural paths fail (`route="fallback"`).
- `try_math_tool()` — deterministic arithmetic/percent calculator
  (`route="tool:deterministic_math"`).
- `_generate_neural` falls back to `nexus-medium` (dead-quality model)
  when primary fails — neural but effectively garbage.

### safety_guard.py
- `FALLBACKS` dict + `fallback_message()` — replaces blocked/degenerate
  neural output with canned text (`route="safety_guard:*"`).

### main.py
- Input safety block returns canned Bengali message directly.
- Output guard replaces neural text with fallback on degenerate output.
- Legacy path (only on brain import failure): old transformer `generator`
  — neural but different/older model, plus RAG retrieval context.

### apps/api intelligence-engine.ts
- On ML-service error/timeout: throws -> route returns error payload
  (no canned answer, but also no neural answer — acceptable failure mode).
- `'No response from AI'` literal if response empty.

## 3. Live trace — 9 prompts (VERIFIED, this session)

| # | Prompt | Intent | Route | Neural? | Result |
|---|--------|--------|-------|---------|--------|
| 1 | Hello! | GREETING | deterministic:greeting | NO | canned EN greeting |
| 2 | What is your name? | IDENTITY | registry:identity_metadata | NO | canned identity text |
| 3 | Who created you? | IDENTITY | registry:identity_metadata | NO | canned identity text |
| 4 | What is gravity? | KNOWLEDGE | neural:nexus-core-04 | YES | correct curated fact |
| 5 | What is 12 × 8? | MATH | neural:nexus-core-03 then fallback | PARTIAL | core03 degenerate -> Bengali fallback text (non-neural) |
| 6 | Explain artificial intelligence. | KNOWLEDGE | neural:nexus-core-04 | YES | correct curated fact |
| 7 | বাংলাদেশের রাজধানী কী? | CHAT | neural:nexus-medium | YES(bad) | gibberish "হ্যাঁ, how manyess জানি।" |
| 8 | তুমি কেমন আছো? | CHAT | neural:nexus-core-01 | YES(bad) | incoherent math-word-problem text |
| 9 | Tumi kemon acho? | GREETING | deterministic:greeting | NO | canned Banglish greeting |

Score: 4/9 fully non-neural; 2/9 neural-but-degenerate->non-neural fallback;
3/9 genuine neural (1 correct, 2 gibberish).

## 4. Four-core capability assessment (VERIFIED)

- All cores: same pre-norm decoder-only Transformer implementation
  (core01/transformer.py), independent configs+weights. SFT chat format:
  `[BOS] user: <q> [EOS] assistant: <a> [EOS]`; inference prompt must
  include user-turn EOS (bug found+fixed in nexus_core.chat_prompt_ids).
- Core-01 Run3: generates but poor quality (empty EN, incoherent BN/BNG).
- Core-02 v2: 74.2% exact on template-held-out; cannot do novel reasoning;
  syllogism test produced gibberish via core-01 (intent missed REASONING).
- Core-03 v2: 9.2% arithmetic — cannot reliably do math neurally.
- Core-04 v3: 73.3% seen-fact recall; hallucinates on unseen topics;
  no reliable refusal.
- nexus-medium: effectively dead model — must not serve conversational chat.

Verdict: NO existing core currently meets "general conversational
assistant" quality. They are task specialists with narrow competence.
Direct neural-only chat is architecturally achievable TODAY (all pieces
exist); answer QUALITY is the blocker, not the plumbing.

## 5. Root causes of non-neural responses

1. Deterministic intent handlers short-circuit before any model (greeting,
   identity, capability, thanks, farewell).
2. Math intent prefers deterministic tool after specialist failure.
3. Language-aware FALLBACKS dict returns canned text on any neural failure.
4. safety_guard replaces degenerate neural output with canned text.
5. Core-01 (general chat model) is undertrained -> degenerate outputs
   trigger fallbacks or gibberish.
6. Banglish/Bengali conversational ability essentially absent in all cores.

## 6. Target architecture (design only — NOT implemented)

```
message -> safety input check (keep: security, not answer-gen)
        -> neural router (model selection ONLY — no text handlers)
        -> selected core chat_generate (SFT format)
        -> safety output check (keep degenerate detection, but on failure
           return explicit MODEL_GENERATION_FAILED, never canned text)
        -> response_source=NEURAL_MODEL always, or explicit error
```

Required changes (pending approval):
- model_router.py: remove/bypass GREETING/THANKS/FAREWELL/IDENTITY/
  CAPABILITY/FALLBACKS/tool handlers for conversational intents; keep
  intent classification solely for MODEL SELECTION.
- Router picks core by language+intent: bn/banglish chat -> best available
  (currently core-01 or core-04); knowledge -> core-04; math -> core-03;
  reasoning -> core-02; default -> core-01.
- On neural failure: return explicit error state (HTTP 200 with
  response_source=MODEL_UNAVAILABLE or 503), never template text.
- intelligence-engine.ts: propagate error state; no 'No response from AI'
  substitution for conversational path.
- Optionally retrain cores on conversational SFT data (see §8) — required
  for acceptable quality; architecture change alone yields neural-but-weak
  answers, which is still compliant (honest neural output > fake quality).

## 7. Training requirements (for quality, not plumbing)

- Conversational SFT dataset: greetings, identity (Hasibul founder —
  learned via data, not handler), thanks, farewell, bn/en/banglish chat,
  multi-turn, honest uncertainty, math, knowledge — EN/BN/Banglish balanced.
- Must NOT reuse Run5/Core-01 SFT path without separate approval.
- New clearly-named run e.g. core01_conv_sft_v1 / or extend core02-04.
- Deterministic-seed builders, question-level split integrity (learned:
  hash on question/answer, not sample_id), manifests+sha256.
- Colab free-GPU cell pattern already exists (COLAB_NEXUSAI_FOUR_CORE_SFT.py).

## 8. Benchmark design (prepared, not run)

110+ prompts: 20 bn, 20 en, 20 banglish, 20 general-knowledge, 20 math,
20 conversation, 10 multi-turn conversations, 10 unknown/unanswerable.
Per test capture: input, selected core, raw output, neural confirmation,
lang correctness, relevance, hallucination flag, latency, pass/fail.
Acceptance: 100% neural routing; 0 template answers; explicit error on
failure; attribution trace complete. Quality reported separately.

## 9. Risks

- Removing handlers makes greetings/identity neural-generated -> currently
  cores will produce poor answers until conversational SFT training done.
  Sequence: (a) implement neural-only path behind flag, (b) benchmark,
  (c) train conversational data, (d) re-benchmark, (e) cut over.
- safety_guard output-replacement must be changed to explicit-error mode
  or it remains a hidden non-neural path.
- nexus-medium must be excluded from conversational routing.
- Guest/auth/UI untouched; only ml-service router + api error propagation.

## 10. Verdict

ARCHITECTURE: direct neural-only chat is fully implementable with existing
components — VERIFIED feasible.
QUALITY: current cores cannot yet serve as a general conversational brain
— VERIFIED limitation. Neural-only routing without retraining will produce
honest-but-poor answers (compliant but weak).
RECOMMENDATION: approve phased implementation — neural-only router behind
config flag -> conversational SFT dataset+training (new run names) ->
benchmark -> cutover. No GitHub push without separate approval.
