# NexusAI — Cost Model and Scale Roadmap

**Document type:** Phase 11 MVP cost envelopes, usage assumptions, scaling triggers and financial risk  
**Phase:** Phase 11 — Technology Stack, Implementation Architecture & Development Foundation Planning  
**Status:** Approved — Phase 11 documentation gate passed; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-30  
**Scope:** Cost and scaling planning only. No provider purchase, billing account, workload, or capacity change is created.

## 1. Cost principles

Use envelopes and measurable assumptions, not false precision. AI inference, authentication, email/notification expansion, backup retention, observability volume and data region are variable. Keep the MVP small: managed PostgreSQL, no dedicated Redis initially, PostgreSQL-backed jobs, private object storage, hosted AI through ModelGateway and first-party minimized analytics.

Founder approval is required for budget, target geography, provider contracts, usage quotas and launch scale. All monetary values below are illustrative planning ranges in USD/month, not quotes.

## 2. Cost categories

| Category | Main driver | Cost-control lever |
| --- | --- | --- |
| Web hosting/edge | Requests, bandwidth, build minutes | Static/public caching, bounded traffic, managed deployment |
| API/worker compute | Concurrent requests, AI jobs, reminders, lifecycle jobs | Autoscaling limits, async work, efficient queries |
| PostgreSQL | Instance size, storage, IOPS, backups/PITR, connections | Right-size, pool connections, index review, retention limits |
| AI inference | Input/output tokens, model class, retries, safety evaluations | Context minimization, routing, quotas, caching safe non-sensitive work |
| Object storage | Export volume, retention, downloads, backup copies | Short expiry, encrypted private objects, no raw payload duplication |
| Queue/cache | Job volume and distributed state | PostgreSQL queue first; add Redis/managed queue only at trigger |
| Observability | Log/trace/event volume and retention | Redaction, sampling, coarse metrics, bounded retention |
| Identity/security | MAU, MFA, verification, fraud controls | Managed provider tier and abuse limits; vendor review |
| Notifications | In-app baseline; future email/push/SMS delivery | Keep external channels off until separately approved |
| CI/CD | Runner minutes, artifact storage, security scans | Cache safe build layers, retain bounded evidence |
| Support/operations | On-call, security review, legal/privacy, incidents | Clear scope and automation without weakening controls |

## 3. Planning envelopes

| Stage | Illustrative workload assumptions | Planning envelope | Main uncertainty |
| --- | --- | --- | --- |
| Low-usage MVP | Hundreds of registered users, low concurrent chat, in-app reminders, one region, no vector DB, small synthetic staging | **US$150–800/month** | AI tokens, managed DB minimum tier, identity/observability pricing |
| Early beta | ~1K–10K registered users, daily active subset, moderate chat and lifecycle jobs, staging/security testing | **US$800–4,000/month** | AI model mix, backup/observability retention, provider tiers and support |
| Growth preparation | ~10K–100K registered users, multi-instance API/worker, stronger queue/cache, semantic retrieval evaluation, higher support/reliability | **US$4,000–25,000+/month** | AI volume/quality, regional redundancy, egress, people and compliance evidence |

These are budget envelopes for planning conversations, not a commitment or a provider price claim. Recalculate with actual tokens/request, active users, retention, region, quotas and vendor contracts before launch.

## 4. Unit economics to instrument

Track privacy-safe aggregates:

- cost per active account/month;
- AI cost per conversation and per successful planning operation;
- provider retry/fallback percentage;
- database/storage cost per active account;
- queue job cost and lifecycle completion cost;
- export/deletion workload cost;
- observability cost per million redacted events;
- support/security cost per thousand accounts.

Do not attach raw chat, memory, wellness text or identifiable health categories to cost dimensions.

## 5. Scale roadmap

### MVP / up to ~1K registered users

- One modular API deployment plus one worker deployment.
- Managed PostgreSQL with conservative connection pool and PITR capability.
- PostgreSQL-backed jobs; no dedicated Redis or external vector DB.
- Hosted AI provider through ModelGateway, strict quotas and context budgets.
- Single region/environment set after geography decision.
- Manual/low-volume support with audited projections.

Trigger to review: sustained queue backlog, database connection pressure, provider quota/cost alert, or missed lifecycle objectives.

### ~1K–10K registered users

- Multiple API instances and a separate worker pool.
- Managed connection pooling and read/query optimization.
- Evaluate managed Redis for distributed rate limits/hot ephemeral state.
- Evaluate managed queue if PostgreSQL job contention affects user workloads.
- Add stronger load, DAST, AI red-team and restore cadence.
- Introduce model routing and budget circuit breakers based on measured usage.

Trigger to review: independent failure domains or throughput require extraction of AI/provider or notification workers.

### ~10K–100K registered users

- Extract high-volume AI/provider and notification workers only if ownership/scaling evidence supports it.
- Partition/archive operational usage/delivery data according to approved retention.
- Consider `pgvector` inside PostgreSQL for semantic memory only after deletion/isolation testing.
- Add regional read/compute strategy only after privacy, residency and support decisions.
- Establish formal on-call, incident exercises, cost governance and security assurance.

Trigger to review: database write/connection saturation, regional availability requirement, provider concentration risk or support/SLO commitments.

### Larger than ~100K users

- Re-evaluate multi-region data boundaries, tenant/partition strategy and provider routing.
- Dedicated queue/cache/search infrastructure may be justified.
- Specialized or self-hosted model capacity can be evaluated against privacy, quality and GPU operations.
- Formal SRE, privacy/legal, security engineering, ML-ops and independent assurance capacity becomes necessary.

No scale step is automatic; each requires metrics, a cost/risk review and an ADR.

## 6. Cost safeguards

- Per-account and global AI quotas with alerting and circuit breakers.
- Maximum context, output and retry budgets.
- Feature flags for expensive model routes and future notification channels.
- Staging provider budgets and synthetic evaluation sampling.
- Storage/export expiry and backup retention review.
- Redacted telemetry with bounded retention.
- Monthly cost review with owner, forecast, anomaly threshold and rollback/disable path.

## 7. Cost risks

- AI cost can grow faster than account revenue if retries, long context or complex models are unbounded.
- Region, transfer and backup requirements may make a low-cost platform unsuitable.
- Adding Redis, external vector search or multi-region too early increases fixed cost and operational burden.
- Self-hosted inference shifts variable API cost to GPU, staffing and reliability cost.
- Privacy/security testing, incident response and support are real launch costs, not optional line items.

## 8. Phase boundary

This document defines cost envelopes and scaling triggers only. It does not select paid plans, create billing, change capacity, enable autoscaling, or start Phase 12.
