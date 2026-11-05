# NexusAI - System Overview

**Version**: 1.0.0
**Date**: 2026-11-05
**Status**: STAGE 1 - FORENSIC AUDIT AND ARCHITECTURE BLUEPRINT

---

## Executive Summary

NexusAI is designed to become an independent AI technology platform with its own neural network architecture, AI model parameters, tokenizer, training datasets, inference engine, and public Model API platform. The platform aims to serve both end users through a web application and external developers through a public API.

**Current Status**: Phase 1 Foundation Repair - PARTIAL ACCEPTED (Memory Consent runtime verification BLOCKED)

**Target Vision**: A complete AI platform with:
- Independent AI Core (own architecture, tokenizer, datasets, parameters)
- Knowledge Engine (curated facts, documents, retrieval)
- Memory Engine (user-specific memory with consent enforcement)
- Reasoning and Execution Framework (multi-step planning, tool execution)
- Model Serving Layer (dedicated serving infrastructure)
- Public Model API Platform (developer-facing API)
- Developer Platform (dashboard, analytics, documentation)

---

## System Architecture Overview

### Current Architecture (As-Is)

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interactions                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Layer A: Client Applications                 │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  NexusAI Web App │  │  (Future Mobile) │                    │
│  │  (Next.js, React)│  │                  │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer B: Application Backend                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Fastify API Server (apps/api)                │  │
│  │  - Authentication (HTTP-only cookies)                      │  │
│  │  - Authorization (session-based)                           │  │
│  │  - Route Controllers (auth, conversations, ai, etc.)       │  │
│  │  - AI Orchestration (intelligence-engine.ts)               │  │
│  │  - Memory Service (memory-service.ts)                      │  │
│  │  - Context Builder (context-builder.ts)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer C: AI Orchestration                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Intelligence Engine                           │  │
│  │  - Request normalization                                  │  │
│  │  - Context construction (history + memory)               │  │
│  │  - Model selection                                         │  │
│  │  - Python ML service integration                          │  │
│  │  - Response processing                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer D: Independent AI Core                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Python ML Service (FastAPI)                  │  │
│  │  - Tokenizer (SentencePiece BPE 8K)                        │  │
│  │  - Neural Model (MediumTransformer, 2.47M params)         │  │
│  │  - Inference Engine (SimpleTextGenerator)                │  │
│  │  - Checkpoint Loading                                      │  │
│  │  - Generation Parameters (top_k, top_p, etc.)             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer E: Knowledge and Memory                 │
│  ┌────────────────────────┐  ┌──────────────────────────────┐  │
│  │  Memory Engine         │  │  Knowledge Engine (Partial)  │  │
│  │  - Consent enforcement  │  │  - Knowledge tables         │  │
│  │  - User isolation       │  │  - Knowledge ingestion      │  │
│  │  - Memory CRUD          │  │  - Knowledge sources        │  │
│  └────────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer F: Database Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Neon PostgreSQL                              │  │
│  │  - accounts, auth_sessions                               │  │
│  │  - conversations, messages                              │  │
│  │  - memory_records, consent_records                       │  │
│  │  - knowledge_* tables                                    │  │
│  │  - dataset_registry                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Target Architecture (To-Be)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Layer A: Client Applications                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐│
│  │  NexusAI Web App │  │  Developer       │  │  Public API ││
│  │  (Next.js, React)│  │  Dashboard       │  │  Consumers  ││
│  └──────────────────┘  └──────────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer B: Application Backend                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Fastify API Server                           │  │
│  │  - Authentication (HTTP-only cookies + API keys)        │  │
│  │  - Authorization (session-based + key-based)             │  │
│  │  - Route Controllers (web, public API, developer)         │  │
│  │  - AI Orchestration                                       │  │
│  │  - Memory Service                                         │  │
│  │  - Knowledge Service                                      │  │
│  │  - Reasoning Service                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer C: AI Orchestration                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              AI Orchestration Service                       │  │
│  │  - Request normalization                                  │  │
│  │  - Context construction (history + memory + knowledge)    │  │
│  │  - Memory consent enforcement                             │  │
│  │  - Model selection (registry-based)                      │  │
│  │  - Inference execution (model serving)                     │  │
│  │  - Response processing                                     │  │
│  │  - Safety enforcement                                      │  │
│  │  - Source attribution                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer D: Independent AI Core                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Model Serving Layer                           │  │
│  │  - Model Registry (version management)                    │  │
│  │  - Model Loading (approved versions only)                 │  │
│  │  - Inference Execution                                     │  │
│  │  - Generation Parameters                                  │  │
│  │  - Resource Management                                     │  │
│  │  - Health Checks                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Neural Models (Trained)                       │  │
│  │  - MediumTransformer (2.47M params, 128 context)           │  │
│  │  - Future: Larger models (10M+ params, 512+ context)     │  │
│  │  - Future: Specialized models (wellness, etc.)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Tokenizer (SentencePiece BPE 8K)            │  │
│  │  - Vocabulary management                                  │  │
│  │  - Bengali support                                        │  │
│  │  - English support                                        │  │
│  │  - Mixed-language support                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer E: Knowledge and Memory                 │
│  ┌────────────────────────┐  ┌──────────────────────────────┐  │
│  │  Memory Engine         │  │  Knowledge Engine            │  │
│  │  - Consent enforcement  │  │  - Document ingestion       │  │
│  │  - User isolation       │  │  - Chunking and embedding    │  │
│  │  - Memory CRUD          │  │  - Retrieval (keyword,       │  │
│  │  - Memory approval      │  │    semantic)                │  │
│  │  - Consent state mgmt   │  │  - Source metadata           │  │
│  └────────────────────────┘  │  - Versioning                │  │
│                              └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer F: Reasoning and Execution               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Reasoning Framework                           │  │
│  │  - Multi-step task planning                               │  │
│  │  - Context management                                     │  │
│  │  - Structured reasoning workflows                         │  │
│  │  - Tool selection                                         │  │
│  │  - Permission checks                                      │  │
│  │  - Tool execution                                         │  │
│  │  - Execution history                                      │  │
│  │  - Error recovery                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer G: Public Model API Platform             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Public API Gateway                           │  │
│  │  - Versioned API routes (/api/v1/*)                      │  │
│  │  - API key validation                                    │  │
│  │  - Permission checks                                     │  │
│  │  - Rate limiting                                         │  │
│  │  - Usage tracking                                        │  │
│  │  - Quota enforcement                                     │  │
│  │  - Request ID generation                                 │  │
│  │  - Standard error responses                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer H: Developer Platform                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Developer Dashboard                           │  │
│  │  - Developer registration                                 │  │
│  │  - API key management                                     │  │
│  │  - Usage analytics                                        │  │
│  │  - Model catalog                                          │  │
│  │  - API documentation                                      │  │
│  │  - Integration examples                                   │  │
│  │  - Error logs                                             │  │
│  │  - Request history                                        │  │
│  │  - Quota visibility                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer I: Database Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Neon PostgreSQL                              │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  User Domain:                                      │  │  │
│  │  │  - accounts, auth_sessions                         │  │  │
│  │  │  - user_profiles                                   │  │  │
│  │  │  - notification_preferences                        │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │  Conversation Domain:                              │  │  │
│  │  │  - conversations, messages                         │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │  Memory Domain:                                    │  │  │
│  │  │  - memory_records, consent_records                 │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │  Knowledge Domain:                                 │  │  │
│  │  │  - knowledge_documents, knowledge_chunks          │  │  │
│  │  │  - knowledge_sources                              │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │  Model Domain:                                     │  │  │
│  │  │  - model_registry, model_versions                 │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │  Developer Domain:                                 │  │  │
│  │  │  - developer_accounts, api_keys                    │  │  │
│  │  │  - api_key_permissions, usage_records             │  │  │
│  │  ├──────────────────────────────────────────────────┤  │  │
│  │  │  Operational Domain:                               │  │  │
│  │  │  - request_logs, audit_logs, rate_limit_state      │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Layer J: Infrastructure                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐  │
│  │  Neon DB       │  │  Object Storage│  │  Background Jobs  │  │
│  │  (PostgreSQL)  │  │  (Neon S3, AWS)│  │  (Future)         │  │
│  └────────────────┘  └────────────────┘  └────────────────────┘  │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐                         │
│  │  Logging       │  │  Monitoring    │                         │
│  │  (Structured)  │  │  (Metrics)     │                         │
│  └────────────────┘  └────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Independent AI Core
- **Requirement**: The core AI system must NOT depend on external AI providers (OpenAI, Gemini, Claude, Groq, etc.)
- **Implementation**: Own neural architecture, tokenizer, datasets, training pipeline, model parameters
- **Status**: ✅ IMPLEMENTED AND VERIFIED (MediumTransformer, SentencePiece BPE 8K, trained checkpoint)

### 2. Memory Consent Enforcement
- **Requirement**: Memory access must require explicit user consent, enforce isolation, and fail closed
- **Implementation**: ConsentRecordRepository, consent check before memory retrieval
- **Status**: ⚠️ IMPLEMENTED BUT NOT VERIFIED (Code correct, runtime testing BLOCKED by environment constraints)

### 3. Security First
- **Requirement**: Authentication, authorization, input validation, SQL injection protection, rate limiting
- **Implementation**: HTTP-only cookies, bcrypt, session management, CSRF protection, security headers
- **Status**: ✅ IMPLEMENTED AND VERIFIED

### 4. Modular Architecture
- **Requirement**: Clear separation of concerns, dependency direction, typed interfaces
- **Implementation**: Monorepo with apps/* and packages/*, domain-driven boundaries
- **Status**: ✅ IMPLEMENTED AND VERIFIED

### 5. Evidence-Driven Development
- **Requirement**: All claims must be backed by actual code, tests, or measurements
- **Implementation**: Phase 1 verification reports, checkpoint inspection, runtime tests
- **Status**: ✅ IMPLEMENTED AND VERIFIED

---

## Technology Stack

### Current Stack

**Frontend**:
- Next.js 15
- React 19
- TypeScript
- lucide-react (icons)

**Backend**:
- Fastify 5.12.5
- TypeScript
- bcrypt (password hashing)

**Database**:
- Neon PostgreSQL
- pgvector (vector embeddings, if needed)

**AI/ML**:
- Python 3
- PyTorch
- FastAPI
- SentencePiece (BPE tokenizer)

**Infrastructure**:
- pnpm (package manager)
- Neon Object Storage (S3-compatible)
- HTTP-only cookies (session management)

### Target Stack (Additions)

**Public API Platform**:
- API key management (cryptographic hashing)
- Rate limiting (database-backed)
- Usage tracking (PostgreSQL)

**Developer Platform**:
- Developer dashboard (Next.js)
- API documentation (OpenAPI/Swagger)

**Model Serving**:
- Model registry (PostgreSQL)
- Dedicated serving infrastructure

**Background Jobs**:
- Job queue (if justified by workload)
- Worker nodes (if needed)

---

## Current Limitations

### Critical

1. **Memory Consent Runtime Verification**: ❌ BLOCKED
   - Code implementation correct
   - Runtime testing blocked by environment constraints
   - Requires isolated PostgreSQL test environment

2. **Poor Model Output Quality**: ❌ POOR
   - Model generates incoherent text
   - Cause: Small dataset (1,812 samples)
   - Impact: Cannot answer questions meaningfully

3. **Limited Model Capacity**: ❌ REDUCED
   - Current: 2.47M parameters
   - Originally planned: 10.5M parameters
   - Cause: CPU training constraints

4. **Limited Context Window**: ❌ SMALL
   - Current: 128 tokens
   - Impact: Long conversations truncated

### High

5. **No Public API Platform**: ❌ MISSING
   - No developer-facing API
   - No API key management
   - No usage tracking

6. **No Developer Platform**: ❌ MISSING
   - No developer dashboard
   - No analytics
   - No integration examples

7. **No Model Registry**: ❌ MISSING
   - No version management
   - No approval workflow
   - No deployment eligibility tracking

8. **No Reasoning Framework**: ❌ MISSING
   - No multi-step planning
   - No tool execution
   - No structured reasoning workflows

### Medium

9. **Knowledge Engine Partial**: ⚠️ PARTIAL
   - Tables exist but ingestion incomplete
   - No chunking and embedding
   - No semantic retrieval

10. **No Production Storage Adapter**: ❌ MISSING
    - Profile images use localStorage
    - Not cross-device compatible

---

## System Flows

### NexusAI Chat Flow (Current)

```
User Input
  ↓
Frontend (ChatInterface)
  ↓
API Request (with session cookie)
  ↓
Fastify API (auth middleware)
  ↓
Intelligence Engine
  ↓
Context Builder (load history + memory with consent)
  ↓
Python ML Service (model inference)
  ↓
Response
  ↓
Frontend Display
```

### Public Developer API Flow (Target)

```
External Developer
  ↓
Public API Request (with API key)
  ↓
API Gateway (api/v1/*)
  ↓
API Key Validation
  ↓
Permission Check
  ↓
Rate Limit
  ↓
Usage Tracking
  ↓
AI Orchestration
  ↓
Model Serving (via registry)
  ↓
Neural Model Inference
  ↓
Response (with attribution)
  ↓
Developer Application
```

### Model Training Flow (Target)

```
Dataset Sources
  ↓
Validation & Cleaning
  ↓
Tokenization
  ↓
Dataset Split (train/val/test)
  ↓
Training (with configuration)
  ↓
Checkpoint Saving
  ↓
Evaluation (metrics)
  ↓
Model Registry (metadata)
  ↓
Approval Workflow
  ↓
Model Serving (deployment)
```

---

## Next Steps

This document provides the high-level system overview. Detailed architecture documentation for each layer is available in:

- `docs/architecture/TARGET_ARCHITECTURE.md` - Complete target architecture
- `docs/architecture/AI_CORE_ARCHITECTURE.md` - AI core architecture
- `docs/architecture/PUBLIC_API_PLATFORM.md` - Public API platform
- `docs/architecture/DATABASE_ARCHITECTURE.md` - Database architecture
- `docs/architecture/SECURITY_ARCHITECTURE.md` - Security architecture

For the current state versus target state comparison, see:
- `docs/implementation/ARCHITECTURE_GAP_ANALYSIS.md`

For the phased implementation plan, see:
- `docs/implementation/IMPLEMENTATION_ROADMAP.md`
