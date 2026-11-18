# NEXUSAI MULTI-MODEL AI BRAIN — ARCHITECTURE

## What exists now (verified 2026-11-10)
```
User message
  → model_router.NexusBrain.respond()
      → detect_language_v2 (bengali/english/banglish/mixed + confidence)
      → classify_intent_v2 (greeting/thanks/bye/identity/capability/math/question/chat)
      → deterministic handlers (labeled, honest metadata only)
      → math tool (deterministic calculator, labeled TOOL)
      → neural: registry.generate("nexus-core-01") → fallback "nexus-medium"
      → output validation (_is_degenerate) → language-aware fallback
  → OrchestratorResponse with trace (language, intent, model_used, route, neural_ran, fallback)
```

## Components
- `ml-service/model_registry.py` — validated model registry (hash, strict load, vocab, status lifecycle)
- `ml-service/model_router.py` — NexusBrain: language/intent/router/fallback/math tool
- `ml-service/main.py` — brain path inserted at top of /orchestrate and /inference; legacy path preserved as fallback
- `models/production/current.json` — fixed malformed JSON, now points to Core-01 run3

## Models
| ID | Arch | Params | Status | Role |
|---|---|---|---|---|
| nexus-core-01 | core01 6L/256/8H | 8.84M | ACTIVE primary | general/multilingual neural |
| nexus-medium | medium 2L/128/2H | 2.47M | fallback | emergency only |
| (excluded) small ckpts, medium epoch ckpts | — | — | incompatible tokenizers | not registered |

## Rules
- Deterministic ≠ neural — always labeled in trace.
- Lazy loading: only requested model in RAM (~354MB observed with core01).
- No external AI APIs anywhere in path.
