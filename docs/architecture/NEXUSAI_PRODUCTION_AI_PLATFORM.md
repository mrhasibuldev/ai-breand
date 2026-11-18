# NEXUSAI — PRODUCTION AI PLATFORM (design)

## Current (verified)
Next.js web :3000 → Fastify api :4000 → FastAPI ml-service :8000 → core01 CPU inference. Neon Postgres (nexus schema). Auth sessions exist.

## Target production requirements
- Model serving: registry-driven, lazy load, one active model (~400MB)
- API: /orchestrate with trace; add /v1/models, /v1/chat/completions later
- Streaming generation: core01 generate() is non-streaming — add token streaming later
- Queues/rate-limit/auth: api layer has auth; add rate limits before public API
- Versioning: registry + checkpoint SHA-256 + promotion via PRIMARY switch
- Monitoring: request trace already logs language/intent/model/route
- Memory: consent_records + memory_records tables exist; retrieval path untested

## Gaps to close before public API
- history-key bug fix (intelligence-engine.ts)
- model status endpoint works now; add /models listing
- rate limiting, API keys, usage metering — not implemented
- No GPU serving yet (CPU-only inference is the design)
