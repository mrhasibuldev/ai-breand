# NexusAI Four-Model Architecture Blueprint (PROPOSED — nothing built)
Date: 2026-11-17 · All four-model items are DESIGN ONLY.

| | Core-01 | Core-02 | Core-03 | Core-04 |
|---|---|---|---|---|
| role | general conversation | reasoning/planning | math/logic | knowledge/specialist |
| status | IMPLEMENTED (Run3 serve, Run4 verified) | NOT IMPLEMENTED | NOT IMPLEMENTED | NOT IMPLEMENTED |
| arch proposal | keep 6L/256 (scale later) | 8-12L/384-512 | 6-8L/256 + tool-use head | 8L/512 retrieval-augmented |
| tokenizer | shared sp_bpe_8k v1 | same + math tokens | same + digit/operand tokens | same + entity tokens |
| data | sft_v2→v3 dialogue | reasoning traces (self-generated+verified) | math word-problem sets | domain corpora |
| training | SFT on Run4 | continue-pretrain+SFT | curriculum math | domain-adaptive |
| eval | eval_prompts.json | logic/arithmetic suite | GSM-style subset | QA/F1 suite |
| CPU infer | ~1GB RAM proven | feasible ≤512d | feasible | needs retrieval idx |
| GPU train | T4 minutes | T4 hours | T4 hours | T4+ |
| params est | 8.8M | 20-40M | 15-30M | 30-60M |

## Principles
- Each model OWN weights/tokenizer-version/checkpoint — no shared mutable state
- Registry entries only after strict-load+eval verification
- Versioned ckpts: core02/run1/, core03/run1/ … never overwrite
- CPU inference target for all (Core-01 proves feasibility)
- No external AI anywhere in training data generation
