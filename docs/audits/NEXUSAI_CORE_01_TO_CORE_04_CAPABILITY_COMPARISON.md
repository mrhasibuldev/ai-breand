# NexusAI Core-01 → Core-04 — Capability Comparison (STAGE B)

**Date:** 2026-11-17

| | Core-01 Run3 | Core-01 Run4 | nexus-medium | Core-02 | Core-03 | Core-04 |
|---|---|---|---|---|---|---|
| exists | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| params | 8,842,560 | 8,842,560 | 2,468,928 | — | — | — |
| arch | 6L/256/8h dec-only | same | 2L/128/2h | — | — | — |
| ckpt sha | `ad515cad…` | `761a5b14…` | prefix-only | — | — | — |
| strict load | PASS | PASS | PASS | — | — | — |
| CPU gen executes | PASS | PASS | **FAIL (all EOS)** | — | — | — |
| empty rate | 7/15 (47%) | 5/11 (45%) | 3/3 (100%) | — | — | — |
| bn script output | rare | yes (noisy) | no | — | — | — |
| en quality | gibberish | poor | none | — | — | — |
| arithmetic | 0/5 | 0/2 | — | — | — | — |
| reasoning | FAIL | FAIL | — | — | — | — |
| conversational | FAIL | FAIL | FAIL | — | — | — |
| serving status | ACTIVE (ml-service) | verified, NOT activated | fallback-only | — | — | — |

## Honest summary
- **Only Core-01 is a real model.** Run3 serves production (poor quality).
- Run4 is verified-superior mechanically but quality-unproven → not activated.
- nexus-medium cannot generate → effectively dead weight as fallback.
- **Core-02/03/04 do not exist** — roadmap documents only. No weights,
  no checkpoints, no architectures. Reported NOT IMPLEMENTED.

## Multi-model routing reality
`model_router.py` + `model_registry.py` implement validated routing, but
with only ONE generative model the "multi-model" system is single-model
in practice. Target architecture (Router→Core-01..04) is PROPOSED only.
