# NexusAI — Architecture Decision Records (ADR) Plan

**Document type:** Phase 11 ADR format, initial technology decisions and governance  
**Phase:** Phase 11 — Technology Stack, Implementation Architecture & Development Foundation Planning  
**Status:** Approved — Phase 11 documentation gate passed; Phase 12 Implementation Foundation/Project Initialization approved; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS  
**Canonical product:** NexusAI — Personal AI Health & Wellness Companion  
**Date:** 2026-08-30  
**Approval recorded:** 2026-08-31  
**Scope:** Decision-record format and approved Phase 11 baseline records only. No technology is installed or provisioned by this document.

## 1. ADR policy

An ADR is required for a material technology, boundary, provider, data, security, privacy, safety, cost or operational decision. An ADR records why a choice was made, what it replaces, risks and the trigger for revisiting it. A decision is not “approved” merely because an ADR is drafted; founder-sensitive and launch-blocking decisions require explicit approval.

## 2. Required ADR format

```text
# ADR-NNN — <Decision title>

Status: Proposed | Accepted | Superseded | Rejected
Date: YYYY-MM-DD
Decision owner: <role>
Reviewers: <roles>

## Context
What requirement, constraint or incident requires a decision?

## Options considered
List realistic alternatives and their cost, reliability, security/privacy,
operational and lock-in implications.

## Decision
Select one option or explicitly defer.

## Consequences and tradeoffs
Benefits, disadvantages, migration cost and new risks.

## Controls and evidence
Tests, monitoring, contracts, approvals and rollback evidence required.

## Revisit trigger
Usage, geography, provider, legal, safety, cost or reliability signal.

## Links
Source-of-truth documents and related ADRs.
```

## 3. Approved Phase 11 ADR register

| ADR | Topic | Preferred direction | Status |
| --- | --- | --- | --- |
| ADR-011 | Web framework | Next.js App Router + React + TypeScript | **Accepted — Phase 11** |
| ADR-012 | API runtime/framework | Node.js LTS + TypeScript + Fastify | **Accepted — Phase 11** |
| ADR-013 | Application topology | Modular monolith with separate worker deployment | **Accepted — Phase 11** |
| ADR-014 | Database platform | Managed PostgreSQL; provider/region deferred | **Accepted category; provider/region TBD** |
| ADR-015 | Data access | Drizzle ORM plus reviewed SQL escape hatch | **Accepted — Phase 11** |
| ADR-016 | Authentication | Managed OIDC-capable identity adapter | **Accepted baseline; vendor/MFA TBD** |
| ADR-017 | Browser session | Secure HttpOnly SameSite cookie session | **Accepted baseline; policy parameters TBD** |
| ADR-018 | Queue/cache | PostgreSQL-backed jobs; no dedicated Redis initially | **Accepted — Phase 11; scale trigger defined** |
| ADR-019 | Object storage | Private encrypted S3-compatible storage | **Accepted category; provider/region TBD** |
| ADR-020 | AI provider | Commercial hosted model behind ModelGateway | **Accepted strategy; provider/terms TBD** |
| ADR-021 | Retrieval | PostgreSQL structured retrieval; pgvector evaluation later | **Accepted — Phase 11** |
| ADR-022 | Repository | TypeScript monorepo | **Accepted — Phase 11** |
| ADR-023 | Deployment | Single-cloud managed services, AWS-light reference | **Accepted category; geography/provider TBD** |
| ADR-024 | Observability | Redacted structured telemetry with exporter abstraction | **Accepted architecture; vendor TBD** |
| ADR-025 | CI/CD | Native source-control CI with gated promotion | **Accepted foundation; host/tool TBD** |

## 4. Decision-writing rules

- Cite the approved Product/PRD/Architecture/Database/API/AI/UI/Security requirement that motivates a choice.
- Compare at least two realistic alternatives; do not use popularity as rationale.
- Separate engineering recommendation from founder/legal/business approval.
- Record a proposed change if a choice would alter an approved domain contract; never silently modify it.
- Include privacy, data-region, provider-retention, safety and incident consequences.
- Define evidence and rollback before implementation begins.
- Mark superseded decisions rather than deleting history.

## 5. Review cadence and ownership

The documentation owner maintains the register. Engineering reviews runtime/data decisions, security reviews identity/secrets, privacy/legal reviews data-provider/retention decisions, AI safety reviews model/policy decisions, and the founder/launch authority approves budget, geography, business risk and launch gates. Exact people, quorum and cadence are `TBD / Pending Decision`.

## 6. Phase boundary

This document defines ADR governance only. It does not create individual ADR files, install technology, provision providers, or start Phase 12.
