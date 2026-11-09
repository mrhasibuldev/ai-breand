# NEXUSAI REASONING DATASET REPORT

**Path:** `packages/ai-core/data/phase2/reasoning/`
**Generator:** `packages/ai-core/data/generate_reasoning_dataset.py` (deterministic, seed 42, NO external AI)

## Stats
- Total: **3,515** | Train: 3,215 | Held-out test: 300 (no leakage)
- By category: arithmetic 755, decision_making 500, uncertainty 480, instruction_following 300, logic 330, cause_effect 200, contradiction 160, banglish 640, mixed_reasoning 150
- By lang: en 2,215 / bn 510 / banglish 640 / mixed 150

## Schema
record_id, instruction, answer, explanation, category, lang, difficulty, provenance=`nexusai-authored-deterministic-v1`, validation_status=`validated`, split

## Quality controls
- All arithmetic answers computed by code (not hand-typed)
- Logic templates have unambiguous answers
- Uncertainty/abstention examples teach honest "I don't know"
- Suspicious-string scan: 0 hits
- sha256(train)=`115b36079cec8e5a6e89…`

## Limitations
- Template-generated → limited diversity; Bengali coverage small (510)
- Not a substitute for large human-authored reasoning corpora
- Eval set is internal, not a public benchmark
