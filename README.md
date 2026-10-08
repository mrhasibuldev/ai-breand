# NexusAI — Personal AI Health & Wellness Companion

## Current phase

Phases 04–12: APPROVED.
Phase 13: AUTHORIZED / IN PROGRESS.
Phase 13 Part 1: APPROVED.
Phase 13 Part 2: AUTHORIZED / IN PROGRESS.

Phase 13 Part 1 is approved. Phase 13 Part 2 implements only the authorized development-only wellness Goal Management slice. Production deployment, public beta, and unresolved legal/privacy decisions remain out of scope.

## Source of truth

Read the approved documentation in `docs/00` through `docs/12` before changing architecture or implementing a feature. The Part 1 baseline is [`docs/13-core-implementation-part1.md`](docs/13-core-implementation-part1.md); the authorized goals slice and its verification status are recorded in [`docs/13-core-implementation-part2.md`](docs/13-core-implementation-part2.md).

## Boundaries

- The web app calls the versioned API; it never accesses the database or provider secrets.
- Domain services own business state, ownership, consent, lifecycle, and safety policy.
- AI traffic goes through `NexusAI IntelligenceEngine / ModelGateway`.
- Minimal Memory is off by default, consent-bound, purpose-bound, revocable, and deletable.
- Safety modes are `NORMAL`, `WELLNESS_REDIRECT`, `SAFETY_ESCALATION`, and `BLOCKED`.
