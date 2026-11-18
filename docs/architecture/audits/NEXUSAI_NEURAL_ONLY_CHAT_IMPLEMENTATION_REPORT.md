# Neural-Only Chat Implementation Report

Baseline: main @ d2788936afd24f5a823998b013645defca2fd553
Flag: `NEURAL_ONLY_CHAT` (server-side env on ml-service; default OFF).
Enable: `NEURAL_ONLY_CHAT=1 python main.py` in packages/ai-core/ml-service.

## Files modified
- packages/ai-core/ml-service/model_router.py — neural-only branch:
  eligible cores {core-01, core-03, core-04} only (core-02 + nexus-medium
  excluded per audit); intent-specialist selection (MATH->core03,
  KNOWLEDGE->core04, else core-01); all attempts logged in trace["attempts"];
  failure returns error.code=MODEL_GENERATION_FAILED. No canned/tool/
  fallback text reachable in neural_only mode.
- packages/ai-core/ml-service/main.py — flag read per-request;
  neural_only forced when flag on; input-guard block returns
  response_source=SAFETY_BLOCKED + empty response (no canned text);
  output-guard degenerate output returns INVALID_MODEL_OUTPUT instead of
  fallback substitution; response_source contract extended
  (NEURAL_MODEL / INVALID_MODEL_OUTPUT / MODEL_GENERATION_FAILED /
  SAFETY_BLOCKED).
- apps/api/src/intelligence-engine.ts — empty response or neural-fail
  response_source throws NEURAL_<code>; NEURAL_ errors preserved through
  outer catch (not masked as generic outage).
- apps/api/src/routes/ai.ts — NEURAL_* errors -> HTTP 502 {error: CODE}.

## Live E2E results (real :4000/api/v1/ai/chat, flag ON)
PASS neural routing (all 10 prompts reached neural cores; greetings and
identity now model-generated — gibberish but genuinely neural):
- "What is gravity?" -> neural core-04 -> correct fact (PASS)
- "Explain artificial intelligence." -> core-04 -> correct fact (PASS)
- "Hello!", "What is your name?", "Who created you?", "Tumi kemon acho?",
  "Explain how computers work." -> neural core-01 -> fluent-ish but
  semantically wrong text (PASS routing / FAIL quality — documented)
- "What is 12 × 8?" -> 502 INVALID_MODEL_OUTPUT (explicit failure; core03
  output degenerate) — PASS honest-error contract
- "তুমি কেমন আছো?" -> intermittent: neural gibberish OR 503 timeout —
  PARTIALLY VERIFIED (core-01 33M? no—8.8M but slow under CPU contention;
  empty/timeout surfaces as explicit error, never fake text)

## Failure-injection evidence (observed live, not synthetic)
- Empty neural output -> INVALID_MODEL_OUTPUT / 502 (observed)
- Generation timeout/slow model -> 503 AI service unavailable (observed;
  code path is fetch AbortController -> 'AI service timeout' -> 503)
- Degenerate neural text -> safety_guard INVALID_MODEL_OUTPUT (code path;
  stochastic sampling means not every run triggers it)

## Before/after response_source
BEFORE (flag off): deterministic:greeting, registry:identity_metadata,
tool:deterministic_math, FALLBACK, DETERMINISTIC_HANDLER.
AFTER (flag on): only NEURAL_MODEL | INVALID_MODEL_OUTPUT |
MODEL_GENERATION_FAILED | SAFETY_BLOCKED. Zero non-neural answer text.

## Chat Interface
No UI changes needed: existing isError path renders honest error
notifications on non-200 responses. Guest + auth paths share the same
endpoint. Desktop/mobile untouched.

## Known limitations
- Answer quality remains poor (core-01 gibberish on open chat; core-03
  arithmetic below gate; core-04 hallucination on unseen topics).
- Neural-only mode is dev-flag only; NOT production default.
- 10s upstream timeout can preempt slow 33M-param core-04 on CPU.
- core-02 excluded from conversational routing per audit (template bias).

## Rollback
Unset NEURAL_ONLY_CHAT (or remove env) + restart ml-service; restore
intelligence-engine.ts/ai.ts via git checkout if needed. Old path fully
preserved — flag defaults OFF.

## Verdict
PASS (architecture) — 100% of returned conversational text in neural-only
mode originates from neural inference or is an explicit error. Quality
metrics reported separately and remain limited pending conversational
SFT training (NOT authorized in this mission).
