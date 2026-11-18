# NexusAI Multi-Model Orchestration Design (PROPOSED)
Date: 2026-11-17

## Existing (VERIFIED)
- model_registry.py: validated load, sha gates, strict state-dict, status lifecycle
- model_router.py: intent detect → deterministic handlers OR neural route,
  provenance trace, neural_only flag, fallback labeling
- ml-service: /orchestrate /inference /metrics /eval — live-verified

## Partially implemented
- multi-model registry structure exists but only 1 generative model
- deterministic handlers (identity/math/greeting) — labeled, not neural

## Proposed (NOT built)
```
NexusAI Core
 └─ Intelligent Router (intent+lang+confidence)
     ├─ Core-01 general chat (ACTIVE candidate)
     ├─ Core-02 reasoning (future)
     ├─ Core-03 math/logic (future)
     └─ Core-04 knowledge (future)
 └─ Unified Response Engine (provenance+validation+fallback)
```
- task classifier: rule-based first (current), neural later
- inter-model: shared context protocol {turn_id, lang, intent, history_ref}
- output validation: safety_guard + per-model eval gates
- confidence: empty-rate/heuristic thresholds → escalate or fallback honestly
- fallback: NEVER silent model swap; labeled deterministic or honest refusal
- observability: existing metrics jsonl extended per-model_id
