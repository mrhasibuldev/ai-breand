# Core-05 Decision Record

## Decision: build Core-05 as NEW general-purpose model
Rationale (evidence-based):
1. Four cores share ONE transformer impl — they are specialists, not
   a general brain. General conversation needs broader capacity+data.
2. Run5 (Core-01 SFT) is ready-with-conditions but only improves the
   smallest conversational specialist; it cannot deliver general
   intelligence alone.
3. A dedicated general core with staged training is the credible path
   to the stated long-term objective.

## Alternatives considered
A. Run5 only: rejected as sole path — specialist ceiling.
B. Core-05 orchestrator over specialists: viable LATER (routing layer
   exists); but specialists individually weak → orchestrator inherits
   weakness. Core-05 should be a real model first.
C. New architecture from scratch: rejected — existing impl is proven;
   extend it (models/nexusai_core_05/) with independent config.

## Status: APPROVED FOR DESIGN ONLY
No implementation authorized. Next gate: owner approval → V5 dataset
construction mission → Stage-0 readiness → staged training.
