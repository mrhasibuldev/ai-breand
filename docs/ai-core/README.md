# NexusAI AI Core Documentation

**Last Updated**: 2026-10-26  
**Documentation Status**: Active  
**AI Core Version**: 0.1.0

---

## Overview

This directory contains comprehensive technical documentation for the NexusAI AI Core — the standalone neural AI system that can operate independently from the NexusAI application.

## Documentation Index

### Core Architecture
1. **[01-system-architecture.md](./01-system-architecture.md)** — Overall architecture, component relationships, and dependency direction
2. **[02-model-inventory.md](./02-model-inventory.md)** — Neural models (SmallTransformer, MediumTransformer), checkpoints, tokenizer, and model-loading behavior
3. **[03-chat-pipeline.md](./03-chat-pipeline.md)** — Complete frontend-to-backend-to-model request flow
4. **[04-training-pipeline.md](./04-training-pipeline.md)** — Training scripts, dataset selection, preprocessing, configuration, and checkpoints
5. **[05-dataset-audit.md](./05-dataset-audit.md)** — Dataset inventory, sample counts, language distribution, duplicates, quality, and vocabulary analysis
6. **[06-memory-and-retrieval.md](./06-memory-and-retrieval.md)** — Conversation context, persistent memory, retrieval, RAG, and database integration

### Issues and Investigations
7. **[07-known-issues.md](./07-known-issues.md)** — Consolidated issue register with evidence and severity
8. **[08-audit-history.md](./08-audit-history.md)** — Chronological record of completed audits and their findings

### Planning and Guidance
9. **[09-future-roadmap.md](./09-future-roadmap.md)** — Prioritized investigation and improvement plan
10. **[10-agent-operating-guide.md](./10-agent-operating-guide.md)** — Instructions for future AI coding agents

## Quick Start

### For New Developers
1. Read [01-system-architecture.md](./01-system-architecture.md) to understand the architecture
2. Read [02-model-inventory.md](./02-model-inventory.md) to understand the neural models
3. Read [07-known-issues.md](./07-known-issues.md) to understand current problems

### For AI Coding Agents
1. **MANDATORY**: Read [10-agent-operating-guide.md](./10-agent-operating-guide.md) before making any changes
2. Review [08-audit-history.md](./08-audit-history.md) to understand previous investigations
3. Check [07-known-issues.md](./07-known-issues.md) for issue IDs and authorization status

### For Troubleshooting
1. Check [07-known-issues.md](./07-known-issues.md) for known problems
2. Review [08-audit-history.md](./08-audit-history.md) for previous diagnostic findings
3. Refer to [03-chat-pipeline.md](./03-chat-pipeline.md) for request flow debugging

## Current AI Core Status

### What Exists
- ✅ PyTorch neural model implementations (SmallTransformer, MediumTransformer)
- ✅ Word-level tokenizer (SimpleTokenizer)
- ✅ Training pipeline (TrainingPipeline, CheckpointManager)
- ✅ Inference engine (TextGenerator)
- ✅ Evaluation system (ModelEvaluator)
- ✅ Python FastAPI ML service (port 8000)
- ✅ Checkpoints for both models (5 epochs + final)
- ✅ Retrieval systems (keyword-based and RAG)

### Current Limitations
- ❌ Training dataset is only 19 samples (severely insufficient)
- ❌ Vocabulary size is only 74 tokens (critically small)
- ❌ Model output is incoherent (unusable for production)
- ❌ ML service contains hardcoded NexusAI-specific logic
- ❌ Model/status endpoint reports incorrect information
- ❌ No persistent memory integration with database

### Independence Status
- ✅ Neural model code is independent from NexusAI application
- ✅ No React/Next.js dependencies in AI Core
- ✅ No database dependencies in neural model
- ⚠️ ML service has application-specific coupling (needs cleanup)
- ⚠️ Hardcoded paths and responses (needs parameterization)

## Key Locations

### AI Core Package
```
packages/ai-core/
├── neural/              # Neural model implementations
├── tokenizer/           # Tokenizer
├── training/            # Training infrastructure
├── inference/           # Inference engine
├── evaluation/         # Evaluation system
├── ml-service/          # Python FastAPI service
├── data/                # Training datasets
├── knowledge/           # Retrieval systems
└── models/              # Checkpoints
```

### ML Service Endpoints
- `GET /health` — Health check
- `GET /model/status` — Model status (currently hardcoded, inaccurate)
- `POST /inference` — Direct inference
- `POST /orchestrate` — Orchestrated inference with routing

### Integration Points
- Backend API: `apps/api/src/routes/ai.ts` → calls ML service at `http://127.0.0.1:8000/orchestrate`
- Frontend: `apps/web/app/components/ChatInterface.tsx` → calls Backend API at `http://localhost:4000/api/v1/ai/chat`

## Documentation Standards

- All information is evidence-based with file/line references
- Verified facts are marked with ✅ VERIFIED
- Unverified claims are marked with ❓ UNKNOWN or ⚠️ SUSPECTED
- Historical audit findings are distinguished from current verification
- No secrets, passwords, or tokens are included
- File paths are absolute and verified to exist

## Related Documentation

### Main Repository Documentation
- [../README.md](../README.md) — Project README
- [../08_AI_BRAIN_ARCHITECTURE.md](../08_AI_BRAIN_ARCHITECTURE.md) — Original AI architecture documentation (may be outdated)
- [../AI-ARCHITECTURE-AUDIT.md](../AI-ARCHITECTURE-AUDIT.md) — Previous architecture audit (outdated, claims no implementation exists)

### Root-Level Reports
- [../../NEXUSAI_FULL_REPAIR_REPORT.md](../../NEXUSAI_FULL_REPAIR_REPORT.md) — Full repair report
- [../../FORENSIC_AUDIT_REPORT_COMPLETE.md](../../FORENSIC_AUDIT_REPORT_COMPLETE.md) — Forensic audit report

## Important Notes

### Documentation vs Implementation
- This documentation reflects the **actual current state** of the AI Core
- Some older documentation may claim "no AI implementation exists" — this is **incorrect**
- The AI Core has PyTorch implementations, but they are **poorly trained** (not missing)
- Always verify actual code before trusting historical reports

### Critical Finding
The AI Core exists and is technically functional, but:
- Training data is insufficient (19 samples)
- Vocabulary is too small (74 tokens)
- Model output is incoherent
- **This is a data quality problem, not a missing implementation problem**

## Maintenance

When making changes to the AI Core:
1. Update the relevant documentation files
2. Add entries to [08-audit-history.md](./08-audit-history.md)
3. Update [07-known-issues.md](./07-known-issues.md) if issues are resolved or discovered
4. Maintain evidence-based documentation with file references

## Version History

- **2026-10-26**: Initial documentation created based on comprehensive forensic audit
- **Pre-2026-10-26**: Previous audits existed but were outdated/inaccurate about implementation status
