# TypeScript AI Architecture

## Status: Future Architecture (Not Currently Active)

The TypeScript components in this directory represent a **future AI Brain architecture** that is designed but not yet integrated into the active runtime.

## Active Runtime

The current production runtime is the **Python FastAPI ML service** (`ml-service/main.py`), which:
- Serves HTTP requests on `http://127.0.0.1:8000`
- Loads `MediumTransformer` from `models/checkpoints_medium/final_model.pt`
- Uses `SimpleTokenizer` with 74-token vocabulary
- Provides `/orchestrate` endpoint for inference
- Is called by `apps/api/src/routes/ai.ts`

## TypeScript Components (Future)

The following TypeScript components are **intended for future implementation** and should **NOT be deleted**:

### Core AI Infrastructure
- `bridge/` - TypeScript client for Python ML service communication
- `orchestrator/` - Brain orchestration logic (intent classification, routing, validation)
- `model-registry/` - Model version registry
- `model-router/` - Model routing logic
- `model-adapter/` - Model adapter layer

### AI Capabilities
- `context/` - Context management
- `memory/` - Memory interface (currently placeholder, not implemented)
- `tools/` - Tool registry and permission system
- `safety/` - Safety layer
- `versioning/` - Model versioning system
- `observability/` - AI observability

### Core Types
- `core/` - Core type definitions
- `src/` - Main exports and pipeline definitions

## Integration Strategy

When integrating TypeScript components into the active runtime:

1. **Preserve Python ML service** - It works and is production-tested
2. **Gradual migration** - Integrate TypeScript components incrementally
3. **Maintain compatibility** - Ensure API contracts remain compatible
4. **Test thoroughly** - Validate each integration step

## Current Integration Status

- **Python ML service**: ✅ ACTIVE
- **TypeScript components**: ⚠️ DESIGNED BUT NOT INTEGRATED
- **Bridge client**: ✅ IMPLEMENTED but not used by apps/api or apps/web
- **Orchestrator**: ✅ IMPLEMENTED but not used by active runtime
- **Memory**: ❌ NOT IMPLEMENTED (placeholder only)

## DO NOT DELETE

These TypeScript components represent significant architectural work and should be preserved for future use. They are not legacy code.

---

## CRITICAL DISTINCTION

### Current Production Runtime (Python)

The current production runtime is the **Python FastAPI ML service**:

```
User (Web UI)
    ↓
apps/web/lib/backend-conversation.ts
    ↓
POST /api/v1/ai/chat
    ↓
apps/api/src/routes/ai.ts
    ↓
fetch http://127.0.0.1:8000/orchestrate
    ↓
packages/ai-core/ml-service/main.py (Python FastAPI)
    ↓
Load checkpoint: models/checkpoints_medium/final_model.pt
    ↓
Load tokenizer from checkpoint (74 tokens)
    ↓
Initialize MediumTransformer (4,776,522 parameters)
    ↓
Language Detection (Unicode-based)
    ↓
Intent Classification (Pattern-based)
    ↓
Routing: Deterministic handler or Neural model
    ↓
Quality Filter
    ↓
Fallback if rejected
    ↓
Response
```

**Active Python Components**:
- `ml-service/main.py` - Python FastAPI ML service
- `neural/medium_transformer.py` - MediumTransformer model
- `neural/small_transformer.py` - SmallTransformer model (renamed from transformer.py in Phase 1C)
- `tokenizer/tokenizer.py` - SimpleTokenizer
- `inference/generator.py` - TextGenerator
- `training/` - Training pipeline
- `evaluation/` - Evaluation scripts

**Status**: ✅ ACTIVE IN PRODUCTION

### Future Architecture (TypeScript)

The TypeScript components are designed to provide:
- **Orchestration**: Intent classification, routing, response validation
- **Model Routing**: Dynamic model selection based on task complexity
- **Model Registry**: Version tracking for multiple model checkpoints
- **Model Adapters**: Interface layer for different model architectures
- **Context Management**: Multi-turn conversation context
- **Memory**: Persistent user memory (not yet implemented)
- **Tools**: Tool registry and permission system for function calling
- **Safety**: Content filtering and safety checks
- **Versioning**: Model version management and rollback
- **Observability**: Monitoring and logging for AI operations

**Status**: ⚠️ DESIGNED BUT NOT INTEGRATED INTO PRODUCTION

---

## Migration Timeline (Not Yet Scheduled)

Phase 1: Stabilize Python runtime (CURRENT - Phase 1C)
Phase 2: Collect licensed training data (Stage B4-B2)
Phase 3: Migrate tokenizer (Future Stage)
Phase 4: Retrain model (Future Stage)
Phase 5: Evaluate new model (Future Stage)
Phase 6: Integrate TypeScript orchestration (Future - NOT SCHEDULED)
Phase 7: Implement memory/tools (Future - NOT SCHEDULED)

---

**Last Updated**: Phase 1C - Architecture Stabilization (2026-10-29)
