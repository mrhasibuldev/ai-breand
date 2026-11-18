# Dataset V5 Specification (for Core-05 general intelligence)

## Construction status: SPECIFICATION ONLY — not authorized/built yet.
V5 must be a NEW dir data/unified_conversational/v5/; v1-v4 frozen.

## Language targets (must sum 100%)
Bengali 35% | English 30% | Banglish 20% | Mixed 10% | other 5%
(measured on approved records; unclassified counted, never dropped silently)

## Capability targets
multi_turn 300+ (6/8/10/12-turn depths, diverse scenario families)
reasoning 150+ | decision 150+ | self_correction 100+ |
clarification 100+ | uncertainty 150+ | knowledge 200+ (verified)
math/logic: keep verified procedural but cap ≤25% of corpus
social/identity/greeting/thanks/farewell: cover all languages

## Carryover policy (forensic, not blind merge)
- KEEP: all v4 non-math records (curated, deduped).
- KEEP: v4 math subsample (cap total math ≤25%).
- REVIEW: v1/v2 records superseded by v3/v4 versions of same content.
- DROP candidates: exact/near-dup, foreign-script corrupt, template-
  collapsed skeletons (>N records sharing one skeleton), unverified facts.
- Every carried record retains original provenance + v5 build lineage.

## Quality controls (inherited + new)
- group-atomic splits (sha256 ordering, 90/5/5 or justified variant)
- exact+normalized+prefix near-dup detection
- question-skeleton diversity metric (unique skeletons / records)
- answer-prefix redundancy metric
- template concentration report per category
- foreign-script corruption guard
- language-label verification (script+lexicon detection, not trust)
- math deterministic verification at build time
- benchmark isolation (unseen cases never in train/val/test)

## Multi-turn requirements
6/8/10/12-turn scenarios; context-dependent later turns; topic shifts;
corrections; constraint recall. Diverse families (study, tech support,
health, finance, learning, relationship, planning, troubleshooting).

## Provenance
All records: builder script, seed, source (authored/procedural/licensed),
license where applicable. NO external AI generation/labeling/eval.
Human review status tracked per record (bn/banglish priority).
