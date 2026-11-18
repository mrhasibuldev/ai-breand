# NexusAI — Personal AI Health & Wellness Companion

NexusAI is an independent AI-powered application designed to assist users with health and wellness goals through conversational AI interactions. What makes NexusAI unique is that it uses its own trained AI model — not external AI services like OpenAI or Claude.

---

## Table of Contents

- [What is NexusAI?](#what-is-nexusai)
- [What Makes NexusAI Independent?](#what-makes-nexusai-independent)
- [Current Implementation Status](#current-implementation-status)
- [AI Brain Architecture](#ai-brain-architecture)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [AI Model Details](#ai-model-details)
- [Current Limitations](#current-limitations)
- [Future Roadmap](#future-roadmap)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Core-01 Kaggle Pretraining Guide](#core-01-kaggle-pretraining-guide)
- [License](#license)

---

## What is NexusAI?

NexusAI is a full-stack AI application built from the ground up with its own:

- **Neural Architecture**: Custom Transformer model
- **Tokenizer**: SentencePiece BPE with 8,000-token vocabulary
- **Training Pipeline**: End-to-end training infrastructure
- **Inference Engine**: Python FastAPI ML service
- **Memory System**: Consent-aware memory retrieval
- **Database**: PostgreSQL (Neon) with comprehensive schema

Unlike many AI applications that rely on external APIs (OpenAI, Claude, Gemini), NexusAI trains and runs its own model. This gives you complete control over your data and AI behavior.

---

## 🧠 AI Brain (Core-01) — Verified Status

NexusAI's next-generation independent model, **Core-01**, is a custom 6-layer Transformer (8,842,560 parameters, 8K SentencePiece tokenizer) trained on our own English-first corpus. It runs locally on CPU — no GPU or external AI needed for inference.

| Capability | Status | Evidence |
|---|---|---|
| Own Transformer model | ✅ Implemented | `packages/ai-core/core01/transformer.py` |
| Own tokenizer | ✅ Implemented | sp_bpe_8k, multilingual (EN/BN/Banglish) |
| GPU training (Colab) | ✅ Implemented | Runs 1–3 completed, Run4 prepared |
| Run3 checkpoint | ✅ Verified | sha256 `ad515c…7830`, strict load PASS |
| CPU inference | ✅ Verified | ~382MB RAM, ~42 tok/s, offline |
| Run4 training | ⏳ Prepared | single-upload bundle ready; preflight pending |
| Multi-model brain | ✅ Implemented | registry + router; Core-01 run3 is active neural model |
| English generation | ⚠️ Partial | fluent but undertrained |
| Bengali generation | ⚠️ Partial | neural path works; quality limited pre-Run4 |
| Banglish | ⚠️ Partial | language detection works; generation unproven |
| Reliable reasoning / decision-making | ❌ Not demonstrated | eval report |
| Memory / Agent Mode / Voice / Public API | 📋 Planned | roadmap docs |

**Honest status:** the pipeline works end-to-end; the model is still early-stage and improving with each training run.

📖 **Full guide:** [`docs/architecture/NEXUSAI_AI_BRAIN_COMPLETE_GUIDE.md`](docs/architecture/NEXUSAI_AI_BRAIN_COMPLETE_GUIDE.md)

---

## What Makes NexusAI Independent?

### Own AI Model

✅ **Four-Core Model Family** (shared Transformer implementation, independent weights)
- `packages/ai-core/core01/transformer.py` — one decoder-only Transformer used by all cores
- Core-01: 8.84M params — general/base LM (`checkpoints_core01_run3`, PRETRAINING_COMPLETED)
- Core-02: 20.35M params — reasoning specialist (`checkpoints_core02_sft_v2`)
- Core-03: 8.84M params — mathematics specialist (`checkpoints_core03_sft_v2`)
- Core-04: 33.42M params — knowledge specialist (`checkpoints_core04_sft_v3`)
- Legacy MediumTransformer: 2.45M params — emergency fallback only
- SentencePiece BPE tokenizer with 8,000 vocabulary (shared)
- No external AI APIs used as primary intelligence

> **Honest status:** all four cores strict-load and generate genuine neural text, but none is a working conversational model yet — see [Model Inventory](#model-inventory-four-cores) and `docs/architecture/audits/NEXUSAI_FOUR_CORE_TEST_AND_BENCHMARK_REPORT.md`.

✅ **Training Infrastructure**
- Complete training pipeline in `packages/ai-core/training/`
- Dataset acquisition and cleaning scripts
- Checkpoint management and versioning
- Evaluation and metrics tracking

✅ **Inference Service**
- Python FastAPI ML service
- Loads trained checkpoint from local storage
- Processes Bengali and English inputs
- No dependency on external inference providers

### Data Privacy

✅ **Consent-First Design**
- Memory system requires explicit user consent
- Guest conversations isolated from persistent storage
- User data remains in your database
- No data sent to external AI providers

---

## Current Implementation Status

### ✅ Fully Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| Frontend (Next.js) | ✅ Complete | React 19, TypeScript, responsive design |
| Backend API (Fastify) | ✅ Complete | REST API, authentication, conversation management |
| ML Service (FastAPI) | ✅ Complete | Python inference service with trained model |
| Database (PostgreSQL) | ✅ Complete | Neon PostgreSQL with comprehensive schema |
| Authentication | ✅ Complete | Self-managed with bcrypt, HTTP-only cookies |
| AI Orchestration | ✅ Complete | Intelligence engine, context builder, memory service |
| Consent System | ✅ Complete | Consent records, memory approval workflow |
| Trained Model | ✅ Complete | 2.47M parameters, BPE 8K tokenizer |
| Tokenizer | ✅ Complete | SentencePiece BPE with 8,000 vocabulary |
| Training Pipeline | ✅ Complete | Scripts, datasets, checkpoint management |

### ⚠️ Partially Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| Profile Image Upload | ⚠️ Partial | localStorage only (not cross-device) |
| Memory Runtime Testing | ⚠️ Blocked | No isolated PostgreSQL test environment |

### ❌ Not Implemented (Future Roadmap)

| Component | Status | Description |
|-----------|--------|-------------|
| Public Model API | ❌ Planned | Developer-facing API for model access |
| Developer Platform | ❌ Planned | Dashboard, analytics, API key management |
| Email Verification | ❌ Planned | Email verification during registration |
| Password Reset | ❌ Planned | Password reset flow |
| Model Expansion | ❌ Planned | Larger model (10M+ params) |
| Dataset Expansion | ❌ Planned | Larger dataset (10,000+ samples) |
| Cloud Storage | ❌ Planned | S3/R2/Cloudflare for profile images |
| Knowledge Engine | ❌ Planned | RAG with vector embeddings |

---

## AI Brain Architecture

### Neural Network — Four-Core Family

All cores share one implementation: `packages/ai-core/core01/transformer.py` (`NexusAICore01`), a decoder-only Transformer with token embeddings, sinusoidal positional encoding, pre-norm blocks, multi-head self-attention, GELU feed-forward networks, residual connections, and a final output projection. They differ only in configuration and weights — **not** in architecture code.

| Core | d_model | Layers | Heads | d_ff | max_len | Params | Checkpoint | Verified role |
|---|---|---|---|---|---|---|---|---|
| Core-01 | 256 | 6 | 8 | 1024 | 512 | 8,842,560 | `checkpoints_core01_run3/checkpoint_final.pt` (LFS) | base/general LM — PRETRAINING_COMPLETED, not SFT'd |
| Core-02 | 384 | 8 | 12 | 1536 | 512 | 20,347,712 | `checkpoints_core02_sft_v2/checkpoint_final.pt` | reasoning specialist — template-bound |
| Core-03 | 256 | 6 | 8 | 1024 | 512 | 8,842,560 | `checkpoints_core03_sft_v2/checkpoint_final.pt` | math specialist — 9.2% held-out numeric accuracy |
| Core-04 | 512 | 8 | 8 | 2048 | 512 | 33,419,072 | `checkpoints_core04_sft_v3/checkpoint_final.pt` | knowledge/memorization — narrow curated KB |
| Medium (legacy) | 128 | 2 | 2 | 512 | 128 | 2,452,544 | `checkpoints_medium/final_model.pt` | fallback only — gibberish-prone |

Model selection is handled by `packages/ai-core/ml-service/model_registry.py` (hash-validated registry) and `model_router.py` (language → intent → model). `neural_only=True` mode routes exclusively through neural cores with explicit failure errors — no silent deterministic fallback.

### Tokenizer

**Type**: SentencePiece BPE (Byte Pair Encoding)
- **Location**: `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`
- **Vocabulary Size**: 8,000 tokens
- **Special Tokens**: PAD=0, UNK=1, BOS=2, EOS=3
- **Languages**: Bengali and English

### Training

**Dataset**: Phase 10
- **Samples**: 1,812
- **Languages**: Bengali and English
- **Training Epochs**: 3
- **Perplexity**: 2.83 (reported)
- **Device**: CPU

**Checkpoint**: `packages/ai-core/models/checkpoints_medium/final_model.pt`
- **Size**: ~29.5 MB
- **Status**: ✅ Loads successfully (fallback only — see four-core table above)

### Inference Pipeline

```
User Message
    ↓
Frontend (Next.js)
    ↓
Backend API (Fastify)
    ↓
Intelligence Engine
    ↓
Context Builder (load history)
    ↓
Memory Service (check consent, retrieve memory)
    ↓
ML Service (FastAPI)
    ↓
Model Registry + Router (model_registry.py / model_router.py)
    ↓
Core-01 / Core-02 / Core-03 / Core-04 (or labeled deterministic handler)
    ↓
Tokenizer (SentencePiece BPE)
    ↓
Neural Inference
    ↓
Response
```

---

## How It Works

### Conversation Flow

1. **User enters message** in chat interface
2. **Frontend** sends message to backend API at `/api/v1/chat`
3. **Backend** validates request and calls Intelligence Engine
4. **Intelligence Engine**:
   - Calls Context Builder to load conversation history (last 10 messages, 2000 tokens)
   - Calls Memory Service to retrieve relevant memory (if consent granted)
   - Sends request to ML Service with context
5. **ML Service**:
   - Loads trained model checkpoint
   - Tokenizes input with SentencePiece BPE
   - Runs neural inference
   - Decodes output tokens
   - Returns response
6. **Backend** stores conversation and messages in database
7. **Frontend** displays response to user

### Authentication Flow

1. **User registers** with email and password
2. **Backend** hashes password with bcrypt
3. **Backend** creates account in database
4. **Backend** creates session and sets HTTP-only cookie
5. **Subsequent requests** include cookie for authentication
6. **Session validation** checks cookie against database

### Memory and Consent

1. **User grants consent** for memory storage
2. **Memory Service** checks consent before retrieval
3. **If consent granted**, relevant memory is retrieved and included in context
4. **If consent denied**, memory is not retrieved
5. **Guest mode** conversations remain in-memory only (not persistent)

---

## Technology Stack

### Frontend
- **Framework**: Next.js 15.5.24
- **UI Library**: React 19
- **Language**: TypeScript
- **Icons**: lucide-react
- **Styling**: CSS with CSS variables

### Backend
- **Framework**: Fastify 5.12.5
- **Language**: TypeScript
- **Authentication**: bcrypt, HTTP-only cookies
- **CORS**: @fastify/cors

### ML Service
- **Framework**: FastAPI (Python)
- **ML Library**: PyTorch
- **Tokenizer**: SentencePiece
- **Model**: Custom MediumTransformer

### Database
- **Provider**: PostgreSQL via Neon
- **Schema**: nexus (custom schema)
- **Access Layer**: Custom PostgreSQL client

### Development Tools
- **Package Manager**: pnpm 11.19.0
- **Node Version**: >=22 <25
- **Type Checking**: TypeScript
- **Testing**: Vitest (infrastructure exists, no test files yet)

---

## Project Structure

```
ai-breand/
├── apps/
│   ├── web/              # Next.js frontend
│   │   ├── app/          # React components and pages
│   │   └── lib/          # API clients and services
│   ├── api/              # Fastify backend
│   │   ├── src/
│   │   │   ├── routes/   # API endpoints
│   │   │   ├── middleware/ # Auth middleware
│   │   │   ├── intelligence-engine.ts
│   │   │   ├── context-builder.ts
│   │   │   └── memory-service.ts
│   │   └── server.ts
│   └── worker/           # Background worker (not actively used)
├── packages/
│   ├── ai-core/          # AI Brain implementation
│   │   ├── ml-service/   # Python FastAPI ML service
│   │   ├── neural/       # Neural network architectures
│   │   ├── training/     # Training scripts
│   │   ├── models/       # Model checkpoints
│   │   └── data/         # Datasets and tokenizers
│   ├── database-core/    # PostgreSQL client and migrations
│   ├── auth-core/        # Authentication utilities
│   ├── repositories/     # Data access layer
│   ├── storage-core/     # Storage abstraction
│   └── config/           # Configuration utilities
├── docs/                 # Documentation
├── .env.example          # Environment variable template
└── README.md             # This file
```

---

## Installation

### Prerequisites

- Node.js >=22 <25
- pnpm 11.19.0
- Python 3.14 (for ML service)
- PostgreSQL database (Neon recommended)
- PyTorch (for ML service)

### Step 1: Clone Repository

```bash
git clone https://github.com/mrhasibuldev/ai-breand.git
cd ai-breand
```

### Step 2: Install Dependencies

```bash
pnpm install
```

### Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration:
- `DATABASE_URL`: PostgreSQL connection string from Neon
- `COOKIE_SECRET`: Random string for cookie signing
- `AI_SERVICE_URL`: http://127.0.0.1:8000 (ML service URL)

### Step 4: Install Python Dependencies

```bash
cd packages/ai-core
pip install torch fastapi uvicorn pydantic sentencepiece
```

### Step 5: Set Up Database

- Get PostgreSQL connection string from Neon: https://neon.tech
- Add `DATABASE_URL` to `.env`
- Migrations will run automatically on first backend startup

---

## Running the Project

### Start All Services (Recommended)

```bash
pnpm dev
```

This starts:
- Frontend: http://localhost:3000
- Backend: http://localhost:4000
- ML Service: http://127.0.0.1:8000

### Start Services Individually

**Backend API** (Terminal 1):
```bash
cd apps/api
pnpm run dev
```

**Frontend Web** (Terminal 2):
```bash
cd apps/web
pnpm run dev
```

**ML Service** (Terminal 3):
```bash
cd packages/ai-core/ml-service
python main.py
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:4000
- **ML Service**: http://127.0.0.1:8000

---

## Environment Variables

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| NODE_ENV | Yes | Environment mode | development |
| WEB_PORT | Yes | Frontend port | 3000 |
| API_PORT | Yes | Backend port | 4000 |
| API_ORIGIN | Yes | Backend origin | http://localhost:4000 |
| WEB_ORIGIN | Yes | Frontend origin | http://localhost:3000 |
| NEXT_PUBLIC_API_ORIGIN | Yes | API origin for frontend | http://localhost:4000 |
| DATABASE_PROVIDER | Yes | Database provider | postgresql |
| DATABASE_URL | Yes | PostgreSQL connection string | postgresql://... |
| COOKIE_SECRET | Yes | Cookie signing secret | generate-random-string |
| AI_SERVICE_URL | Yes | ML service URL | http://127.0.0.1:8000 |

---

## Database Setup

### Database Technology

- **Provider**: PostgreSQL via Neon
- **Schema**: nexus (custom schema)
- **Connection**: PostgreSQL connection string via DATABASE_URL

### Key Tables

- `accounts` - User accounts
- `auth_sessions` - Session management
- `user_profiles` - User profile data
- `conversations` - Chat conversations
- `messages` - Chat messages
- `memory_records` - AI memory with consent
- `consent_records` - User consent tracking
- `knowledge_documents` - Knowledge base documents
- `knowledge_chunks` - Document chunks for RAG

### Migrations

Migrations are located in `packages/database-core/migrations/`:
- 001_bootstrap.sql through 017_add_memory_consent_fk.sql
- Migrations run automatically on backend startup

---

## AI Model Details

### Current Model Status — Four-Core Family

**Active production designation**: Core-01 `1.0.0-run3` (`models/production/current.json`)

| Core | Params | Training | Verified generation | Honest quality |
|---|---|---|---|---|
| Core-01 | 8.84M | pretraining 3 epochs, loss ≈4.43 | PARTIALLY VERIFIED (38/56 non-empty) | undertrained base LM; English-biased word salad; immediate-EOS on many chat prompts |
| Core-02 | 20.35M | SFT v2 | VERIFIED mechanical / FAILED semantic | template collapse — ~5 memorized responses for all prompts |
| Core-03 | 8.84M | SFT v2, 8 epochs | VERIFIED mechanical / FAILED semantic | bare numbers only; 9.2% numeric accuracy on held-out test |
| Core-04 | 33.42M | SFT v3, 318 curated records | VERIFIED mechanical / PARTIALLY VERIFIED semantic | fluent bn/en KB sentences; prompt-insensitive memorization |
| Medium | 2.45M | Phase 10 (1,812 samples) | PARTIALLY VERIFIED | gibberish-prone; emergency fallback only |

### Model Quality

**Current Status**: ⚠️ EXPERIMENTAL — pipeline verified, intelligence not yet

The models are independently owned and technically functional (strict checkpoint loading, genuine neural generation, honest routing), but conversational quality is early-stage:
- **Core-01** needs SFT (Run4/Run5) to fix chat-prompt handling.
- **Core-02/03/04** need deduplicated, broader SFT data (Dataset V5 roadmap).
- **Tokenizer** fragments Banglish and emits UNK on unseen foreign scripts.
- **No KV cache** — CPU inference is correct but slow for long contexts.

Full evidence: `docs/architecture/audits/NEXUSAI_FOUR_CORE_TEST_AND_BENCHMARK_REPORT.md` and `eval_reports/`.

### Deterministic Handlers

The system uses deterministic handlers for better UX on common inputs:
- Greetings (Hello, Hi)
- Farewells (Goodbye, Bye)
- Thanks (Thank you)
- Help requests

These bypass neural model and return pre-defined responses. This is intentional.

### Fallback Behavior

The system has fallback mechanisms for:
- Unknown intents
- Language detection failures
- Model output validation failures

Fallbacks return hardcoded Bengali text. This is intentional error handling.

---

## Current Limitations

### Model Limitations (verified 2026-11-18)

1. **Core-01**: undertrained base LM — English-biased word salad, immediate EOS on many prompts (needs SFT).
2. **Core-02**: template/slot-fill collapse — does not generalize beyond memorized patterns.
3. **Core-03**: emits bare numbers for any input; 9.2% held-out arithmetic accuracy.
4. **Core-04**: prompt-insensitive memorized KB recall; narrow 318-record coverage.
5. **Tokenizer**: Banglish fragmentation, UNK on unseen scripts.
6. **Inference**: no KV cache; CPU-only; repetition penalty is a slow Python loop.
7. **Datasets**: core02 60% exact-duplicate train records; core03 18%; V5 not yet constructed.
8. **Multi-turn**: single-turn inference path only.

### Architecture Limitations

1. **No Public API**: Developer-facing API not implemented
2. **No Developer Platform**: Dashboard, analytics, API key management missing
3. **Memory Runtime Testing**: Blocked (no isolated PostgreSQL test environment)
4. **No Automated Tests**: Test infrastructure exists but no test files
5. **Manual Testing Required**: End-to-end testing requires browser interaction

### Feature Limitations

1. **Profile Images**: localStorage only (not cross-device)
2. **No Email Verification**: Email addresses not verified
3. **No Password Reset**: Users cannot reset forgotten passwords
4. **No Cloud Storage**: Profile images not stored in cloud
5. **No Content Filtering**: AI responses not filtered for harmful content

### Infrastructure Limitations

1. **Rate Limiting**: In-memory only (not database-backed)
2. **No Session Cleanup**: Expired sessions not automatically cleaned
3. **No Retry Logic**: Failed AI requests not retried
4. **No Monitoring**: No centralized logging or observability

---

## Future Roadmap

### Phase A: Foundation (Current)
- ✅ Architecture documentation
- ✅ AI Brain foundation
- ✅ Consent system
- ✅ Basic inference

### Phase B: Dataset Expansion
- Expand dataset to 10,000+ samples
- Improve Bengali coverage
- Improve English coverage
- Data quality validation

### Phase C: Model Improvement (current focus)
- Dataset V5 construction (next approved mission — the Core-05 blocker)
- Core-01 Run4/Run5 SFT for chat-capable generation
- Core-02/03/04 SFT retraining on deduplicated data
- Core-05 general-purpose model (architecture audited, not implemented)
- GPU training support (temporary Colab, separately authorized)

### Phase D: Knowledge Engine
- Implement RAG with vector embeddings
- Document chunking and retrieval
- Knowledge base management
- Vector database integration

### Phase E: Storage Migration
- Migrate profile images to cloud storage (S3/R2)
- Implement signed URLs
- Add image compression
- Implement CDN

### Phase F: Public API Platform
- Developer-facing API
- API key management
- Usage tracking
- Rate limiting per API key

### Phase G: Developer Platform
- Developer dashboard
- Analytics and metrics
- API documentation
- Developer accounts

### Phase H: Model Registry
- Model version management
- A/B testing
- Model deployment pipeline
- Model rollback

### Phase I: Observability
- Centralized logging
- Metrics collection
- Error tracking
- Performance monitoring

### Phase J: Security Hardening
- Email verification
- Password reset flow
- Two-factor authentication
- Content filtering

### Phase K: Production Deployment
- Infrastructure automation
- CI/CD pipeline
- Load testing
- Disaster recovery

---

## Troubleshooting

### ML Service Won't Start

**Problem**: ModuleNotFoundError for torch or fastapi

**Solution**:
```bash
cd packages/ai-core
pip install torch fastapi uvicorn pydantic sentencepiece
```

### Backend Won't Connect to Database

**Problem**: Connection refused or invalid DATABASE_URL

**Solution**:
- Verify DATABASE_URL in `.env` is correct
- Check Neon database is active
- Ensure database user has correct permissions

### Frontend Can't Reach Backend

**Problem**: CORS errors or connection refused

**Solution**:
- Verify API_ORIGIN and NEXT_PUBLIC_API_ORIGIN in `.env`
- Ensure backend is running on port 4000
- Check CORS configuration in backend

### Model Loading Fails

**Problem**: Checkpoint file not found or incompatible

**Solution**:
- Verify the active checkpoint exists (e.g. `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt` for Core-01; see the four-core table above for others)
- Verify `.sha256` provenance matches `packages/ai-core/ml-service/model_registry.py`
- Verify tokenizer exists at `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`
- Check ML service logs for specific error

### AI Responses are Poor Quality

**Problem**: Incoherent or repetitive text

**Solution**:
- This is expected with current small dataset (1,812 samples)
- Model quality will improve with dataset expansion (Phase B)
- Current model is experimental foundation

---

## Contributing

Contributions are welcome! This is an independent AI project with significant room for improvement.

### Areas for Contribution

1. **Dataset Expansion**: Add more Bengali and English training samples
2. **Model Architecture**: Experiment with larger architectures
3. **Testing**: Add unit tests, integration tests, E2E tests
4. **Documentation**: Improve documentation and examples
5. **Features**: Implement roadmap features

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## Core-01 Kaggle Pretraining Guide

> **Purpose:** Permanent setup, recovery, and training manual for **NexusAI Core-01** — our independently initialized decoder-only Transformer — on Kaggle. Written so a beginner can reproduce everything from a fresh account.
>
> **Honesty rule:** ✅ = real verified output exists. ⏳ = pending/unverified. ❌ = failed. Never assume a step succeeded — check the printed output.

### What is Core-01?

Our own language model — **not** GPT, Llama, Mistral, or any pretrained model. It learns only from data we prepare.

| Property | Value |
|---|---|
| Architecture | Decoder-only Transformer, causal attention |
| Parameters | **8,842,560** |
| Vocabulary | 8,000 SentencePiece BPE (pad=0, unk=1, bos=2, eos=3) |
| Tokenizer | `sp_bpe_8k.model` |
| d_model / layers / heads | 256 / 6 / 8 |
| Feed-forward / activation | 1,024 / GELU · Pre-LayerNorm · sinusoidal positions |
| Context length | 512 tokens |
| Status | **UNTRAINED** — full pretraining NOT completed |

### Why our own model?

External models are someone else's brain. Core-01 gives us control over weights, data, privacy, and behavior — the foundation of the NexusAI "own AI brain" goal.

### Verified artifacts

| Item | Location | Details |
|---|---|---|
| Package ZIP | `exports/nexusai_core01_kaggle_package.zip` (Desktop copy: `C:\Users\Nusaiba\Desktop\nexusai_core01_kaggle_package.zip`) | 306,348 B · 15 files · SHA-256 `1b0c66f03457eb764b08dacde5594e4093581b2b3f116ad9e3176a97d33be970` |
| Notebook | `docs/notebooks/nexusai_core01_fineweb_pretraining.ipynb` | 23 physical cells = logical Cells 1–12 |
| Prep script | `packages/ai-core/data/prepare_english_corpus.py` (also inside ZIP at `data/`) | local-Parquet only, never downloads |
| Driver | `packages/ai-core/core01/pretraining_driver.py` (inside ZIP at `core01/`) | CLI entry point |
| Tokenizer | `data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model` + `.vocab` | Kaggle sha256 `2fcc6a87c9ded27d1f8ad6c2dc0ff747ca4dc52db68ffde9a6e229b2cd3d8052` |

### Kaggle account details (verified)

- Notebook: `NexusAI-Core-Training`
- Dataset owner: `atoplay` · Dataset: `nexusai-core01-package`
- Input path: `/kaggle/input/datasets/atoplay/nexusai-core01-package/nexusai_core01_kaggle_package/`

### Cell-by-cell progress (historical evidence)

| Cell | Stage | Status | Evidence |
|---|---|---|---|
| 2 | Environment check | ✅ VERIFIED SUCCESS (CPU session) | Python 3.13.18/16 · torch 2.11.0 (cpu build seen once, cu130 in recovery) · sentencepiece 0.2.2 · pyarrow 23.0.1 · ~20.9 GB disk · ~33.7 GB RAM. **CPU env ≠ GPU ready** |
| 3 | Package setup | ✅ VERIFIED SUCCESS | Package found as **extracted dir** (ZIP candidate absent → sha check skipped); `PACKAGE_OK=True`; extracted to `/kaggle/working/nexusai_core01/pkg/` |
| 4 | Tokenizer | ✅ VERIFIED SUCCESS | vocab 8,000 · IDs 0/1/2/3 · encode/decode round-trip True |
| 5 | FineWeb verify | ✅ VERIFIED SUCCESS | `FINEWEB_VERIFIED=True` (license `odc-by`, lang `en`, shard-0 size verified) |
| 6 | FineWeb download | ✅ PREVIOUSLY VERIFIED | `APPROVE_FINEWEB_DOWNLOAD=True` → shard 0 (~2.0 GiB) downloaded in earlier session |
| 7 | Corpus preparation | ✅ PREVIOUSLY VERIFIED | See "Verified corpus results" below — 100,499,546 tokens, exit 0 |
| 8 | Dataset audit | ✅ PREVIOUSLY VERIFIED | `DATASET_OK=True`, overlap 0, driver loaded 103,846 docs |
| 9 | GPU verification | ✅ PREVIOUSLY VERIFIED | Tesla T4 · CUDA True · sm_75 · fp16 path · `GPU_OK=True` |
| 10 | GPU smoke test | ❌ **FAILED — NOT VERIFIED** | `NameError: PACKAGE_OK is not defined` after runtime restart; driver never launched; 200-step smoke **never ran** |
| 11 | Full training approval | ⏳ PENDING | gate exists, not enabled |
| 12 | Full pretraining | ❌ **NOT STARTED** | no evidence of any completed training |

> ⚠️ Cells 6–9 results are **historical** — they were verified in an earlier Kaggle session. `/kaggle/working/` contents may not persist; always re-verify before relying on them (see Recovery section).

### Verified corpus results (historical, Cell 7/8)

| Metric | Value |
|---|---|
| Source | FineWeb `sample-10BT`, shard 0, license ODC-By-1.0 |
| Target / buffer / val / seed | 100,000,000 / 0.005 / 0.015 / 42 |
| Inspected docs | 105,475 |
| Accepted docs | 105,427 (48 duplicates rejected) |
| **Total tokens (Core-01 tokenizer)** | **100,499,546** |
| Train | 103,846 docs / 99,011,035 tokens |
| Val | 1,581 docs / 1,488,511 tokens |
| Audit | overlap=0, empty=0, dup-in-output=0, `DATASET_OK=True`, driver loaded all docs |
| Outputs | `english_train.jsonl`, `english_val.jsonl`, `manifest.json`, `preparation_report.md`, `deduplication_report.json` |

### Kaggle Runtime Restart & Recovery Incident

**What happened:** During the earlier workflow, Cell 10 (GPU smoke test) was authorized and executed — but failed immediately with:

```
NameError: name 'PACKAGE_OK' is not defined
```

A recovery diagnostic was then run (read-only; no downloads, prep, or training). Verified findings:

- Python 3.13.16 · torch 2.11.0+cu130 · **CUDA True** · GPU **Tesla T4** · VRAM **14.56 GB**
- **Missing from `/kaggle/working/`:** package working dir, tokenizer, FineWeb shard, prepared dataset, train/val files, smoke checkpoint dir
- **Missing variables:** `PACKAGE_OK`, `TOKENIZER_OK`, `DATASET_OK`, `DOWNLOAD_OK`, `PREP_DONE`, `PACKAGE_ROOT`, `TOKENIZER_PATH`, `train_path`, `val_path`, `PREPARED_DIR`
- `GPU_OK` remained set (it was re-created by Cell 9 in that session)
- The attached package dataset was still accessible at `/kaggle/input/datasets/atoplay/nexusai-core01-package/nexusai_core01_kaggle_package/`

**Explanation (beginner terms):**
- `/kaggle/input/` = attached datasets (persistent, survives restarts)
- `/kaggle/working/` = notebook working storage (can be wiped on runtime restart/crash/timeout)
- Python variables live only in the running kernel — a restart erases them all
- The earlier prepared corpus therefore **must be regenerated** if `/kaggle/working` was cleared

**Cause:** not independently established — described as a **suspected Kaggle runtime reset/restart** (consistent with status-code-56-style session drops seen previously). Do not claim a definitive root cause.

### Kaggle Runtime Recovery Procedure

When variables/files are missing after a restart, recover in this order — **never skip verification, never auto-repeat expensive steps:**

1. **Env check** — re-run Cell 2; confirm torch/CUDA/GPU.
2. **Input check** — confirm `/kaggle/input/datasets/atoplay/nexusai-core01-package/` still exists.
3. **Restore package** — re-run Cell 3 → recreates `PACKAGE_OK`, `PACKAGE_ROOT`, paths.
4. **Tokenizer** — re-run Cell 4 → `TOKENIZER_OK`.
5. **FineWeb verify** — re-run Cell 5 (read-only).
6. **Shard** — Cell 6 checks `SHARD_PATH` size before downloading; if `.part`/full file exists it skips re-download. Only set `APPROVE_FINEWEB_DOWNLOAD=True` if the shard is actually missing.
7. **Corpus** — Cell 7 prep script is resume-safe (row-group checkpoints in `prep_state.json`); re-run only if outputs are missing/incomplete.
8. **Audit** — re-run Cell 8 → `DATASET_OK`.
9. **GPU** — re-run Cell 9 → `GPU_OK`.
10. **Smoke test** — re-run Cell 10 **only after re-reading its code and getting explicit owner approval.**

> ⚠️ **Runtime Recovery ≠ Training Resume.** Recovery rebuilds environment+data. Training resume continues a checkpointed run (next section).

### Checkpoint Management & Training Resume

- A **checkpoint** = saved snapshot of model weights + optimizer + scheduler + GradScaler + RNG + step/epoch + status. It is the "save game" of training.
- Checkpoints are written **atomically** (`.tmp` → `os.replace`) with `.backup` copies — a crash cannot leave a half-written file.
- Files in `--output-dir`: `checkpoint_step{N}.pt` (periodic), `checkpoint_last.pt` (epoch end — primary resume point), `checkpoint_final.pt` (only on genuine completion → `PRETRAINING_COMPLETED`), `checkpoint_interrupted.pt` (Ctrl+C, stays `PRETRAINING_IN_PROGRESS`), `checkpoint_error.pt` (exception forensics), `checkpoint_maxsteps.pt`.
- Checkpoint interval is configured by `--checkpoint-interval` (driver arg, verified in `pretraining_driver.py`).
- **Resume:** the driver supports `--resume <checkpoint filename inside --output-dir>` — verified in code (`args.resume` → `engine.load_checkpoint`). Exact procedure for cross-session resume on Kaggle: download `checkpoints_full/` output before session end → attach as Kaggle Dataset → re-run driver with `--resume checkpoint_last.pt`.
- Resume restores model/optimizer/scheduler/RNG/epoch/step but **not** DataLoader sampler/batch position → **approximate, epoch-granular** — documented limitation.
- Before session end, download `/kaggle/working/nexusai_core01/checkpoints_full/` (Kaggle Output → download, or save as Dataset) — working storage may not persist.

### The 12 notebook cells — plain-language guide

| Cell | CPU/GPU | Downloads? | Changes files? | Approval? | Success looks like | If it fails |
|---|---|---|---|---|---|---|
| 1 Overview | — | no | no | no | read markdown | — |
| 2 Env check | CPU | no | no | no | versions + disk printed | missing pkg → `!pip install -q sentencepiece pyarrow` |
| 3 Package | CPU | no | extracts to `/kaggle/working/.../pkg` only | no | `PACKAGE_OK = True` | see Troubleshooting |
| 4 Tokenizer | CPU | no | no | no | `vocab_size: 8000`, round-trip True | wrong path → check Cell 3 |
| 5 FineWeb verify | CPU | metadata only (HEAD/API) | no | no | `FINEWEB_VERIFIED: True` | internet off → Settings → Internet ON |
| 6 Download | CPU | **YES — shard 0 ~2.0 GiB** | writes `raw/…shard0.parquet` | **`APPROVE_FINEWEB_DOWNLOAD`** | `DOWNLOAD_OK: True` + sha256 | disk short → free space; never auto-fetches more shards |
| 7 Corpus prep | CPU | no | writes `prepared_dataset/` | **`APPROVE_CORPUS_PREPARATION`** | `PREP_DONE` + 5 output files | see Troubleshooting |
| 8 Dataset audit | CPU | no | no | no | `DATASET_OK: True` | token shortfall → report, don't train |
| 9 GPU check | GPU probe | no | no | no | `GPU_OK: True`, T4 + 14.56 GB | CUDA unavailable → Accelerator → GPU T4 x2 |
| 10 Smoke test | **GPU** | no | writes `checkpoints_smoke/` | **`APPROVE_GPU_SMOKE_TEST`** | ~200 steps, finite loss, ckpt saved | OOM → lower batch / raise accum |
| 11 Full training | **GPU** | no | writes `checkpoints_full/` | **`APPROVE_FULL_TRAINING`** | `checkpoint_final.pt` = COMPLETED | session end → resume |
| 12 Status | — | no | no | no | status board | — |

> ⚠️ Enable `APPROVE_*` flags **one at a time**, only after reading that cell's plan. Never enable all four together.

### FineWeb dataset facts (verified)

- Repo `HuggingFaceFW/fineweb` · config `sample-10BT` · English · **ODC-By 1.0** (attribution: *"FineWeb by Hugging Face"*) + Common Crawl ToS.
- `sample-10BT` = 15 shards; shard 0 = **2,147,292,183 bytes (~2.0 GiB)**; Range requests supported.
- Only shard 0 downloaded; prep stops at ~100M **real SentencePiece tokens** (never GPT-2 estimates), 0.5% buffer, 1.5% val, seed 42.
- The older ~3.47M-token corpus is too small — FineWeb replaces it for pretraining. Bengali needs a separate approved data strategy later.

### Beginner glossary

| Term | Plain meaning |
|---|---|
| Runtime | The live Python process inside the notebook. Restart = all variables + `/kaggle/working` files may be lost. |
| CUDA | NVIDIA's GPU computing platform — lets PyTorch use the GPU. |
| GPU / VRAM | Graphics card / its memory (T4 = 14.56 GB). Model+batches must fit in VRAM. |
| Tokenizer | Tool that splits text into tokens the model understands (ours: SentencePiece, 8,000 vocab). |
| Training dataset | Text the model learns from (train split). |
| Validation dataset | Held-out text used to measure progress honestly (val split). |
| Pretraining | First stage: model learns language patterns from raw text (next-token prediction). |
| Training step | One optimizer update after processing a batch. |
| Loss | Error score — lower = better. We watch it go down. |
| Checkpoint | Saved model+optimizer snapshot for resume/safety. |
| Runtime recovery | Rebuilding notebook state after a restart (Cells 2–9). |
| Training resume | Continuing from a checkpoint in a later session (`--resume`). |

### Rebuilding the NexusAI Core-01 Kaggle Environment from Scratch

1. Kaggle account → verify phone if prompted.
2. **Dataset:** Datasets → New Dataset → upload `nexusai_core01_kaggle_package.zip` → Create.
3. **Notebook:** `NexusAI-Core-Training` → File → Import `nexusai_core01_fineweb_pretraining.ipynb`.
4. Right panel → **Input → Add Input → Your Work → nexusai-core01-package**.
5. **Settings:** Internet ON · Add-ons `sentencepiece`, `pyarrow` if Cell 2 reports missing · Accelerator CPU for Cells 2–8, GPU T4 x2 for Cells 9–11.
6. Run cells in order; enable each `APPROVE_*` flag only when that stage is next.
7. If the runtime restarts → follow **Kaggle Runtime Recovery Procedure** above.

### NexusAI Core-01 — Run4 Single-Upload Bundle (NEW)

Run4 distribution is consolidated into **one ZIP**:
`exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` (~81 MB).
It contains the preflight cell, original training bundle, corpus, and resume
evidence plus a `manifest.json` of SHA-256 hashes. Upload that ONE file to
Colab (or Drive) and run `docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py`,
which validates, extracts, and stages everything safely — then run the
preflight cell. Full guide:
`docs/training/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_GUIDE.md`.
The Run3 checkpoint stays on Drive and is never modified.

### NexusAI Core-01 — Google Colab Training Guide (Kaggle-free)

Training moved fully to **Google Colab** — no Kaggle, no manual uploads. The notebook clones our public GitHub repo, downloads FineWeb `sample-10BT` shard 0 (~2 GiB), prepares the 100M-token corpus with our own `prepare_english_corpus.py`, then trains on 1× Tesla T4 (verified env: Python 3.13.16, torch 2.14.1+cu130, CUDA True).

**One-time setup**

1. Open **https://colab.research.google.com** → sign in.
2. **File → Upload notebook** → `docs/notebooks/NexusAI_Core01_Google_Colab_Training.ipynb`.
3. **Runtime → Change runtime type → T4 GPU**.
4. Run cells top-to-bottom. Everything else is automatic.

**The 3 approval gates (all `False` by default — enable one at a time)**

| Cell | Flag | What it authorizes |
|---|---|---|
| 9 | `APPROVE_DATASET_PREPARATION` | FineWeb shard-0 download (~2 GiB) + 100M-token corpus prep (~30–60 min) |
| 17 | `APPROVE_SMOKE_TEST` | ~200-step GPU pipeline test on real data |
| 19 | `APPROVE_FULL_TRAINING` | real pretraining; checkpoints→Drive every 500 steps |

**Drive layout (auto-created):** `MyDrive/NexusAI/{source_data,data,package,tokenizer,checkpoints,logs,reports}`

**Resume after disconnect:** new session → re-run Cells 2–16 → Cell 19 with `--resume checkpoint_last.pt`.

**Links:** full guide `docs/notebooks/NEXUSAI_CORE01_COLAB_SETUP.md` · audit `docs/architecture/audits/NEXUSAI_CORE01_COLAB_MIGRATION_AUDIT.md` · Kaggle guide above kept for history.

### Training Session Log

| Session ID | Date/time | Notebook | Runtime | GPU | VRAM | Python | Torch | Package | Tokenizer | Dataset | Tokens | Config (bs/lr/prec) | Steps | Train loss | Val loss | Checkpoints | Errors | Fixes | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 2026-11-07 | NexusAI-Core-Training | CPU then GPU T4 | Tesla T4 | 14.56 GB | 3.13.x | 2.11.0 | ✅ dir-found (sha skipped) | ✅ | ✅ 100.5M tok | 100,499,546 | smoke bs32/lr3e-4/fp16 (planned) | 0 | — | — | none saved | Cell10 NameError (runtime restart) | recovery diagnostic only | **UNTRAINED** |

> Fill one row per real session using **actual outputs only**. Update this table when new stages complete.

### Troubleshooting

| Symptom | Meaning | Safe fix |
|---|---|---|
| `PACKAGE_OK is not defined` | kernel restarted; variables lost | Re-run Cells 2–9 in order (Recovery Procedure) |
| `zip candidates: []` but dir found | dataset attached as folder | Normal — sha check skipped; re-upload ZIP if hash verify wanted |
| `PACKAGE INIT FAILED` | required file missing | verify dataset contents; re-upload ZIP |
| `sha256 match: False` | old package version | upload current ZIP as new dataset version |
| `sentencepiece/pyarrow MISSING` | deps absent | `!pip install -q sentencepiece` / `pyarrow` |
| Download fails / disk error | shard ~2 GiB + margin | check Cell 2 disk; free `/kaggle/working` |
| `CUDA unavailable` Cell 9 | accelerator still CPU | Settings → Accelerator → GPU T4 x2 → restart |
| OOM in smoke | batch too big | lower `--batch-size`, raise `--gradient-accumulation-steps` |
| Session dies mid-training | Kaggle ~9–12 h limit | resume `checkpoint_last.pt` next session |
| `DATASET_OK` overlap>0 | split bug | STOP — send manifest, do not train |
| tokens ≪ 100M | shard exhausted | report shortfall; approve shard 1 manually |

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

NexusAI is an independent AI project with its own trained model, tokenizer, and training pipeline. It does not use external AI APIs as primary intelligence.

The goal is to demonstrate that independent AI development is possible with modern tools and techniques.

---

## Support

For issues, questions, or contributions, please visit the GitHub repository:
https://github.com/mrhasibuldev/ai-breand

### Run3 Checkpoint — GitHub LFS Storage (NEW)

The authoritative Core-01 Run3 checkpoint is now stored in the repo via
**Git LFS** at `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt`
(106,777,501 B, SHA-256 `ad515cade…7830`). Fresh Colab sessions can clone the
repo and `git lfs pull` the checkpoint — no ZIP upload needed.
See `docs/training/NEXUSAI_CORE01_CHECKPOINT_RECOVERY.md` and
`docs/notebooks/COLAB_CLONE_RECOVERY_CELL.py`.

### Universal Cloud Training System (NEW — verified 2026-11-16)

Provider-independent training layer in `packages/ai-core/cloud/`:
`env_manager` (deps/CUDA detect), `hardware` (GPU/RAM/disk), `storage`
(local/Drive/Kaggle + write tests), `adapters` (Colab/Kaggle/Generic-Linux),
`model_loader` (strict checkpoint compat), `dataset_manager` (JSONL integrity),
`preflight` (single readiness verdict).

**Package:** `exports/NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip`
(173,913,680 B · SHA-256 `f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644`)
— self-contained: core01 code, cloud modules, tokenizer, Run3 checkpoint,
Run4 dataset, preflight cell, manifest+checksums. 26/26 payload hashes verified.

**Quick start (any Linux GPU cloud):**
1. Extract ZIP → run `nexusai/docs/notebooks/UNIVERSAL_CLOUD_PREFLIGHT_CELL.py`
2. Expect `READY` verdict (READY ≠ training authorization)
3. Train via `core01/pretraining_driver.py` — see `docs/training/universal/NEXUSAI_TRAINING_GUIDE.md`

**Verified locally:** 11 PASS / 0 FAIL / 2 NOT TESTED
(`tests/universal/test_universal_system.py`) — env, hardware, adapters,
dataset, tokenizer, strict model load, forward pass, synthetic train step,
checkpoint save/load + resume restore, storage, package integrity, preflight.
GPU + live Colab/Kaggle runs: NOT TESTED (need real cloud session).

Docs: `docs/training/universal/` (audit, architecture, migration, training
guide, test report, package manifest).

### Training NexusAI on Google Colab (primary environment)

**A. Prerequisites** — Google account, Colab access (free T4 OK), the
universal package ZIP, ~2GB Drive space.

**B. Drive prep** — create `MyDrive/NexusAI/` folder.

**C. Upload ZIP** — upload `NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip`
(173,913,680 bytes · SHA-256 `f20d38eee9148367068624f51b56575bac6bd719114c14d8d9bc52fffe86e644`)
to Drive. Verify size+hash before proceeding.

**D. Notebook** — new Colab notebook.

**E. GPU runtime** — `Runtime → Change runtime type → T4 GPU`. A notebook
cannot grant itself a GPU; CPU runtime = preflight will report FAIL on cuda.

**F. Mount Drive** — the setup cell does `drive.mount("/content/drive")`
automatically (browser auth prompt once per session).

**G. ZIP location** — cell auto-finds the ZIP under MyDrive or /content;
it filters candidates by exact expected size.

**H. SHA verify** — cell recomputes SHA-256 and compares to the pinned value.

**I. Extract** — safe extraction to `/content/nexusai_pkg` with
traversal/absolute-path rejection; re-runs are idempotent.

**J. Deps** — verifies torch/sentencepiece/numpy/psutil; reports missing
packages (Colab base image already has them).

**K. Preflight** — run `docs/notebooks/COLAB_UNIVERSAL_SETUP_CELL.py` as ONE cell.

**L. GPU/CUDA** — cell checks `torch.cuda.is_available()`, GPU name, VRAM,
and runs a real CUDA matmul. `cuda=FAIL` → switch runtime to T4 and re-run.

**M. Dataset/tokenizer** — verifies `corpus_train.jsonl` (385,217,021 B) and
`sp_bpe_8k.model` presence inside the package.

**N. Run3 checkpoint** — strict-loads `core01_run3_checkpoint_final.pt`,
verifies SHA `ad515cade…7830`, params 8,842,560.

**O. Resume readiness** — confirms optimizer/scheduler/GradScaler/RNG state
present; epoch=3, step=1341. Driver uses TOTAL epochs: `EPOCHS=5` →
`range(3,5)` = exactly 2 additional epochs, final epoch 5.

**P. Synthetic dry-run** — 2×16-token forward+backward on random IDs;
proves the model trains mechanically without touching real data.

**Q. Report** — JSON saved to `/content/nexusai_reports/`; verdict
READY / BLOCKED. READY ≠ authorized.

**R. Troubleshooting** — see `docs/training/universal/` guides;
common fixes: remount Drive, re-select T4, re-upload ZIP if hash fails.

**S. Checkpoint backup** — copy run4 checkpoints to
`MyDrive/NexusAI/checkpoints/core01_run4/` during/after training;
never overwrite Run3.

**T. Training start** — ONLY after explicit approval. See
`docs/training/universal/NEXUSAI_TRAINING_GUIDE.md` for the driver command.

**Live Colab/GPU status: NOT TESTED** — cell is syntax-verified and all
logic paths tested locally; first real run happens in your Colab session.
