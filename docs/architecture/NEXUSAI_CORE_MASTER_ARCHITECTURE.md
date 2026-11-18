# NEXUSAI CORE — MASTER ARCHITECTURE

## Verified current state (2026-11-10)
- **3 architectures:** SmallTransformer(185K), MediumTransformer(2.47M), Core-01(8.84M)
- **Active model:** `nexus-core-01` = run3 ckpt (sha256 ad515cad…7830) via model_registry+router
- **Fallback:** nexus-medium (2.47M) — emergency only
- **Excluded:** small ckpts + medium epoch ckpts (tokenizer-incompatible: vocab 1K/char-74)
- **Pipeline:** web → api /ai/chat → ml-service /orchestrate → model_router.NexusBrain → registry → core01 inference → validated response
- **Offline CPU inference:** verified ~354MB RAM, ~40tok/s

## Target architecture (roadmap, not yet built)
```
NEXUSAI CORE
├── Model Orchestrator (exists: model_router.py — needs extension)
├── Context Manager (partial: conversation_history; history-key bug found)
├── Model Router (exists: language/intent/model/tool/fallback)
├── Inference Controller (exists: core01/inference.py)
├── Response Evaluation (planned: eval framework doc)
├── LANGUAGE MODEL → nexus-core-01 (run3 now, run4 next)
├── REASONING/MATH/CODING/BENGALI specialists → FUTURE (do not fake)
└── Unified Response + provenance trace (exists)
```

## Design rules
- One reliable foundation first (Core-01) before specialists.
- Shared tokenizer sp_bpe_8k across compatible models.
- Registry-driven: new checkpoint = new MODEL_DEFS entry, no app rewrite.
- Deterministic tools labeled, never disguised as neural.
- Consent-based memory separate from model weights.
