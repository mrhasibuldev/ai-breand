# NexusAI Website Integration — Verification Report

**Date:** 2026-11-17 · Live-tested on localhost:8000

## Architecture (verified live)
```
Website(3000) → Fastify API(4000) → FastAPI ML(8000)
   /orchestrate → model_router → model_registry → core01 InferenceEngine
   /inference   → legacy path → NOW routed to Core-01 engine (fixed)
   /model/status→ legacy globals → NOW Core-01 (fixed)
```

## What already worked
- `/orchestrate` → `neural:nexus-core-01` → genuine generation (Run3)
- Deterministic handlers (greeting/identity/math) correctly labeled
- Registry: hash-verified Run3 ckpt, strict load, provenance fields

## Bugs found & fixed (ml-service/main.py)
1. **Path bug:** `current.json` ckpt path joined to `ai_core_dir` not `models/` → FileNotFound → silent Small-model fallback → 500. Fixed: try `models/` prefix first.
2. **Legacy model mismatch:** `/inference`+`/model/status` built MediumTransformer — Core-01 `transformer_blocks.*` keys incompatible. Fixed: detect core01 keys → delegate to `registry.load("nexus-core-01")` with adapter.
3. **weights_only:** torch 2.14 defaults `weights_only=True`; Run3 ckpt has numpy RNG state → probe loads now `weights_only=False` (trusted local artifact, same as registry medium loader).

## Live verification results
| endpoint | before | after |
|---|---|---|
| /health | ok | ok |
| /orchestrate (neural Q) | neural:nexus-core-01 gibberish | same (unchanged, correct) |
| /model/status | **500** | ✅ Core-01, 8,842,560 params, cpu, Run3 ckpt |
| /inference | would 500/fallback | ✅ real neural output (Run3 quality) |

## Honest status
- **Integration: WORKING** for Run3 on ML service layer.
- **Quality: POOR** — outputs are real neural generations but incoherent (Run3 limitation, not integration bug).
- **Run4: NOT activated** — ckpt is Drive-only; activating requires file + registry update + quality evidence.
- **API(4000)/Web(3000): not running** in this session — chain verified only through ML service.
- Provenance labels accurate: deterministic vs neural vs fallback distinguished in diagnostics.

## Files changed
- `packages/ai-core/ml-service/main.py` (path fix + core01 routing + weights_only)

## Next
Run4 promotion only after: Drive ckpt → local/registry + CPU quality PASS.
