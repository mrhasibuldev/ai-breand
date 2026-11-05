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

## What Makes NexusAI Independent?

### Own AI Model

✅ **Custom Neural Architecture**
- NexusAI uses its own MediumTransformer architecture
- Trained on Phase 10 dataset (1,812 samples)
- 2.47 million parameters
- SentencePiece BPE tokenizer with 8,000 vocabulary
- No external AI APIs used as primary intelligence

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

### Neural Network

**Model**: MediumTransformer (custom implementation)
- **Location**: `packages/ai-core/neural/medium_transformer.py`
- **Parameters**: 2,468,928
- **Architecture**: Decoder-only Transformer
- **Configuration**:
  - `d_model`: 128 (embedding dimension)
  - `n_layers`: 2 (transformer layers)
  - `n_heads`: 2 (attention heads)
  - `d_ff`: 512 (feed-forward dimension)
  - `max_len`: 128 (context length)
  - `vocab_size`: 8,000 (vocabulary size)

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
- **Size**: 18.76 MB
- **Status**: ✅ Loads successfully

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
Model (MediumTransformer)
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

### Current Model Status

**Model**: MediumTransformer (Phase 1)
- **Parameters**: 2,468,928
- **Vocabulary**: 8,000 (SentencePiece BPE)
- **Context Length**: 128 tokens
- **Training Dataset**: Phase 10 (1,812 samples)
- **Training Epochs**: 3
- **Perplexity**: 2.83 (reported)
- **Device**: CPU

### Model Quality

**Current Status**: ⚠️ EXPERIMENTAL

The current model is a foundation prototype with expected limitations:
- **Small Dataset**: 1,812 samples is insufficient for high-quality generation
- **Small Model**: 2.47M parameters, 128-token context window
- **Output Quality**: Incoherent, repetitive responses
- **Languages**: Bengali and English support is basic

This is an **independent AI foundation**, not a production-ready model. Future roadmap includes dataset expansion and model retraining.

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

### Model Limitations

1. **Small Dataset**: 1,812 samples insufficient for high-quality generation
2. **Small Model**: 2.47M parameters, limited capacity
3. **Small Context**: 128-token context window
4. **Poor Output Quality**: Incoherent, repetitive text
5. **CPU Only**: No GPU support for faster inference

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

### Phase C: Model Retraining
- Train larger model (10M+ parameters)
- Increase context window (512+ tokens)
- Improve output quality
- GPU training support

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
- Verify checkpoint exists at `packages/ai-core/models/checkpoints_medium/final_model.pt`
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
