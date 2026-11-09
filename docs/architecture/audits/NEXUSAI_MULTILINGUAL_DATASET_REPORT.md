# NEXUSAI MULTILINGUAL DATASET REPORT

**Output:** `packages/ai-core/data/phase2/run4_corpus/corpus_train.jsonl` (386MB, 215,605 docs, ~56.9M tokens est)
**Manifest:** `corpus_manifest.json` | sha256 `bc7a9091f7b4a78f53fe…`

## Composition
| Source | Docs | Lang | Category |
|---|---|---|---|
| bangla_wikipedia_mit (sampled) | 45,000 | bn | bangla_general |
| sangraha_bengali (all) | 9,000 | bn | bangla_general |
| bongchat_v1 (sampled) | 30,000 | bn/mixed | bangla_instruction |
| english_first | 61,960 | en | english_general |
| tinystories | 60,000 | en | english_simple |
| reasoning_v1 ×3 | 9,645 | en/bn/banglish/mixed | reasoning_* |

## Method
- Deterministic even-stride sampling (seed 42), no raw data modified
- Reasoning repeated ×3 for weight (9,645 emitted from 3,215)
- Driver holds out 2% val internally; reasoning_test.jsonl kept separate for eval
- Token estimate: 2K-doc sample → avg 264 tok/doc, UNK 0.12%

## Language balance
Bengali-side ≈ 75% docs / ~80% tokens; English ≈ 25%. Bengali-heavy by design (model is English-biased from run1-3).
