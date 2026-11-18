# NEXUSAI — INTELLIGENCE REQUIREMENTS (target spec)

## Required capabilities & honest current status
| Capability | Status | Evidence needed to claim |
|---|---|---|
| Language understanding (EN/BN/Banglish) | PARTIAL | run4 multilingual eval |
| Original generation | PARTIAL | provenance audit: real forward passes, weak semantics |
| Multi-step problem solving | NOT DEMONSTRATED | held-out reasoning benchmark |
| Error/contradiction detection | NOT IMPLEMENTED | dedicated eval + self-check pass |
| Self-correction | PLANNED | generate→verify→revise loop test |
| Conversation continuity | PARTIAL | history-key bug found; fix + eval |
| Context/memory | PARTIAL infra | consent system exists; retrieval untested |
| Tool use | PARTIAL | math tool only; agent framework planned |
| Scientific/academic reasoning | NOT DEMONSTRATED | domain eval set |
| Uncertainty honesty | PARTIAL | abstention examples in reasoning_v1 |

## Non-negotiables
- No external AI as core intelligence.
- Fluency ≠ intelligence; correctness measured on held-out sets.
- Reasoning claims require reproducible benchmark evidence.
