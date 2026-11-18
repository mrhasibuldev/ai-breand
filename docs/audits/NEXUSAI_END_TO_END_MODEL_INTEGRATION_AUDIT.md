# NexusAI — End-to-End Model Integration Audit (STAGE B)

**Date:** 2026-11-17 · live ml-service localhost:8000

## Request-path verification (live)
`POST /orchestrate {"message":"What is 5 + 3?","neural_only":true}` →

```
route: neural:nexus-core-01
model_used: nexus-core-01
response_source: NEURAL_MODEL
neural_ran: true · fallback: false
provenance.checkpoint_sha256: ad515cadea… (Run3)
provenance.neural_generation_executed: true
engine: core01 · load_s: 0.44
```

## Findings
| check | status |
|---|---|
| API invokes Core-01 (not medium/small) | **PASS** — route=neural:nexus-core-01 |
| neural provenance recorded (ckpt sha+tok sha) | PASS |
| deterministic handlers labeled separately | PASS (earlier: greeting→DETERMINISTIC_HANDLER) |
| silent fallback to other model | none observed — medium never invoked |
| safety guard active | PASS (injection/harm blocked earlier) |
| metrics capture route/neural/latency | PASS |

## Honest notes
- `model_loaded:false` in /health is lazy-load state, not a defect.
- neural_only bypasses deterministic handlers → true neural path verified.
- Default (non-neural_only) requests may use deterministic handlers for
  identity/greeting/math — correctly labeled, NOT neural.
- Run4 NOT routed (Drive-only, quality unproven) — correct conservative choice.

## Integration verdict
**PASS** — the service genuinely invokes Core-01's own weights through
registry→router→InferenceEngine. No external AI anywhere in path.
