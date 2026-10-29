# AI Core System Architecture

**Last Updated**: 2026-10-26  
**Verification Status**: VERIFIED from source code inspection

---

## Overview

The NexusAI AI Core is a PyTorch-based neural AI system located in `packages/ai-core/`. It is designed to be a standalone, reusable AI system that can operate independently from the NexusAI application.

## Dependency Direction

**Current Architecture**: NexusAI → AI Core

```
┌─────────────────────────────────────────────────────────────┐
│                     NexusAI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐         ┌──────────────────┐            │
│  │  Frontend       │         │  Backend API     │            │
│  │  (Next.js)      │ HTTP    │  (Fastify)       │            │
│  │  React/TS       │ ───────► │  TypeScript      │            │
│  │  Port 3000      │         │  Port 4000       │            │
│  └─────────────────┘         └────────┬─────────┘            │
│                                       │                      │
│                                       │ HTTP                 │
│                                       ▼                      │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP API
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI Core (Python/PyTorch)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────┐        │
│  │  ML Service (FastAPI)                            │        │
│  │  Port 8000                                       │        │
│  │  - /orchestrate endpoint                         │        │
│  │  - /inference endpoint                           │        │
│  │  - /health endpoint                              │        │
│  │  - /model/status endpoint                        │        │
│  └──────────────────────────────────────────────────┘        │
│                                   │                          │
│                                   ▼                          │
│  ┌──────────────────────────────────────────────────┐        │
│  │  Orchestrator                                     │        │
│  │  - Language detection                            │        │
│  │  - Intent classification                          │        │
│  │  - Deterministic handler routing                  │        │
│  │  - Retrieval (Simple/RAG)                         │        │
│  │  - Neural model routing                           │        │
│  └──────────────────────────────────────────────────┘        │
│                                   │                          │
│                    ┌──────────────┴──────────────┐           │
│                    ▼                             ▼           │
│  ┌──────────────────────┐          ┌─────────────────────┐   │
│  │  Neural Model        │          │  Retrieval Systems   │   │
│  │  MediumTransformer   │          │  - Simple Retrieval  │   │
│  │  - 4.7M parameters   │          │  - RAG System       │   │
│  │  - 74 token vocab ❌ │          │  - Filesystem data   │   │
│  └──────────────────────┘          └─────────────────────┇   │
│                                   │                          │
│                    ┌──────────────┴──────────────┐           │
│                    ▼                             ▼           │
│  ┌──────────────────────┐          ┌─────────────────────┐   │
│  │  Tokenizer           │          │  Inference Engine   │   │
│  │  SimpleTokenizer     │          │  TextGenerator      │   │
│  │  - 74 tokens ❌      │          │  - Sampling          │   │
│  │  - Word-level        │          │  - Autoregressive    │   │
│  └──────────────────────┘          └─────────────────────┇   │
│                                   │                          │
│                    ┌──────────────┴──────────────┐           │
│                    ▼                             ▼           │
│  ┌──────────────────────┐          ┌─────────────────────┐   │
│  │  Training Pipeline   │          │  Evaluation System   │   │
│  │  - TrainingPipeline  │          │  - ModelEvaluator    │   │
│  │  - 19 samples ❌     │          │  - Test suite        │   │
│  │  - CheckpointManager │          │                     │   │
│  └──────────────────────┘          └─────────────────────┇   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Neural Models

**Location**: `packages/ai-core/neural/`

**Models**:
1. **SmallTransformer** (`transformer.py`)
   - d_model: 128
   - n_layers: 4
   - n_heads: 4
   - d_ff: 512
   - max_len: 256
   - Parameters: ~100K-200K (estimated)
   - Checkpoints: `models/checkpoints/checkpoint_epoch_*.pt`

2. **MediumTransformer** (`medium_transformer.py`)
   - d_model: 256
   - n_layers: 6
   - n_heads: 8
   - d_ff: 1024
   - max_len: 512
   - Parameters: 4,776,522 (VERIFIED)
   - Checkpoints: `models/checkpoints_medium/final_model.pt`
   - **Currently Loaded**: MediumTransformer

**Shared Components**:
- `attention.py` — Multi-head attention mechanism
- `embedding.py` — Token and positional embeddings
- `ffn.py` — Feed-forward networks

### Tokenizer

**Location**: `packages/ai-core/tokenizer/tokenizer.py`

**Implementation**: SimpleTokenizer (word-level tokenizer)

**Special Tokens**:
- `<PAD>` (0)
- `<UNK>` (1)
- `<BOS>` (2)
- `<EOS>` (3)

**Current Vocabulary Size**: 74 tokens (VERIFIED from checkpoint)

**Saved Tokenizer**: `tokenizer/multilingual_tokenizer.json`

### Training Infrastructure

**Location**: `packages/ai-core/training/`

**Components**:
- `pipeline.py` — TrainingPipeline class (main training loop)
- `dataset.py` — TextDataset class (data loading)
- `checkpoint.py` — CheckpointManager class (checkpoint save/load)

**Training Script**: `train_medium_model.py` (root of ai-core package)

### Inference Engine

**Location**: `packages/ai-core/inference/generator.py`

**Implementation**: TextGenerator class

**Features**:
- Autoregressive text generation
- Temperature sampling
- Top-k filtering
- Top-p (nucleus) sampling
- Repetition penalty

### Evaluation System

**Location**: `packages/ai-core/evaluation/evaluator.py`

**Implementation**: ModelEvaluator class

**Tests**:
- Basic generation
- Unseen prompts
- Question answering
- Multi-turn conversation
- Context retention
- Repetition detection
- Unknown question handling
- Invalid input handling
- Inference latency
- CPU memory usage

### ML Service

**Location**: `packages/ai-core/ml-service/main.py`

**Implementation**: FastAPI service

**Port**: 8000 (binds to 127.0.0.1)

**Endpoints**:
- `GET /` — Root endpoint with endpoint list
- `GET /health` — Health check
- `GET /model/status` — Model status (⚠️ HARDCODED, INACCURATE)
- `POST /inference` — Direct inference
- `POST /orchestrate` — Orchestrated inference with routing
- `GET /pipeline/status` — Autonomous pipeline status
- `POST /pipeline/run` — Run autonomous pipeline

**Dependencies**: `ml-service/requirements.txt`
- torch>=2.0.0
- numpy>=1.24.0
- fastapi>=0.100.0
- uvicorn>=0.23.0
- pydantic>=2.0.0
- psutil>=5.9.0
- python-multipart>=0.0.5

### Retrieval Systems

**Location**: `packages/ai-core/knowledge/`

**Components**:
1. **Simple Retrieval** (`store/simple_retrieval.py`)
   - Keyword-based retrieval
   - Data from `knowledge/cleaned/` directory
   - No database dependency

2. **RAG System** (`data/rag_system.py`)
   - Vector-based retrieval with character embeddings
   - Data from `data/processed/` directory
   - No database dependency

### Datasets

**Location**: `packages/ai-core/data/`

**Datasets**:
- `train_v2.json` — 502 conversation samples (used for inference tokenizer rebuilding)
- `public_datasets/v1.0_cleaned/train_cleaned.json` — 19 text samples (used for training)
- `public_datasets/v1.0/train.json` — Additional dataset
- `conversational_data.json` — Conversational data
- `merged_train.json` — Merged training data

### Checkpoints

**Location**: `packages/ai-core/models/`

**Small Model Checkpoints**:
- `checkpoints/checkpoint_epoch_1.pt` through `checkpoint_epoch_5.pt`

**Medium Model Checkpoints**:
- `checkpoints_medium/checkpoint_epoch_1.pt` through `checkpoint_epoch_5.pt`
- `checkpoints_medium/final_model.pt` (currently loaded)

## Integration Points

### Backend API Integration

**File**: `apps/api/src/routes/ai.ts`

**Endpoint**: `POST /api/v1/ai/chat`

**Behavior**:
- Receives message from frontend
- Forwards to ML service at `http://127.0.0.1:8000/orchestrate`
- Extracts `response` field from ML service response
- Returns to frontend

**Timeout**: 10 seconds (configurable)

### Frontend Integration

**File**: `apps/web/app/components/ChatInterface.tsx`

**Behavior**:
- User submits message via chat interface
- Sends to backend at `http://localhost:4000/api/v1/ai/chat`
- Receives response and displays in chat
- Guest mode uses in-memory conversation storage
- Authenticated mode uses conversation manager

## Current Coupling Points

### Technical Coupling (Legitimate)
- HTTP API contract between backend and ML service
- Service URL configuration via `AI_SERVICE_URL` environment variable
- JSON request/response format

### Problematic Coupling (Needs Removal)
1. **Hardcoded NexusAI responses** in ML service (lines 540-611 in main.py)
   - Bengali/English deterministic greetings
   - NexusAI identity responses
   - Application-specific prompts

2. **Hardcoded system prompt** (lines 8-26 in main.py)
   - "You are an AI assistant created by Mr. Hasibul"
   - NexusAI branding
   - Islam-specific knowledge

3. **Hardcoded filesystem paths** (lines 213-234 in main.py)
   - Assumes monorepo structure
   - Relative paths to `packages/ai-core/`

## Independence Assessment

### What is Independent
- ✅ Neural model code (no React/Next.js imports)
- ✅ Tokenizer (no application dependencies)
- ✅ Training pipeline (no application dependencies)
- ✅ Inference engine (no application dependencies)
- ✅ Evaluation system (no application dependencies)
- ✅ Retrieval systems (no database dependencies)
- ✅ Checkpoint loading (no application dependencies)

### What is Coupled
- ❌ ML service has hardcoded NexusAI-specific logic
- ❌ ML service has hardcoded filesystem paths
- ❌ ML service has hardcoded system prompt
- ❌ Deterministic responses are application-specific

### Standalone Capability
**Verdict**: PARTIALLY

The neural model, tokenizer, training, and inference can run standalone. The ML service needs cleanup to remove application-specific logic and paths.

## Target Architecture

### Proposed Standalone AI Core

```
ai-core/
├── model/                      # Neural models
├── tokenizer/                  # Tokenizer system
├── inference/                 # Inference engine
├── training/                  # Training infrastructure
├── evaluation/                # Evaluation system
├── retrieval/                 # Optional retrieval
├── checkpoints/               # Model checkpoints
├── datasets/                  # Training datasets
├── configs/                   # Configuration files
├── runtime/                   # Cleaned ML service
└── safety/                    # Optional safety layer
```

### Key Principles
1. Configuration-driven (no hardcoded values)
2. Interface-based (pluggable components)
3. Application-agnostic (no NexusAI branding)
4. Standalone installable (pip package)
5. API-first (clean REST API)
6. Versioned (multiple model/checkpoint versions)

## References

- **Main Service**: `packages/ai-core/ml-service/main.py`
- **Models**: `packages/ai-core/neural/`
- **Tokenizer**: `packages/ai-core/tokenizer/tokenizer.py`
- **Training**: `packages/ai-core/training/`
- **Backend Integration**: `apps/api/src/routes/ai.ts`
- **Frontend Integration**: `apps/web/app/components/ChatInterface.tsx`
