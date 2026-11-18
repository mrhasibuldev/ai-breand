# NEXUSAI MODEL ROUTING GUIDE

## Pipeline (model_router.py)
1. **Language** — `detect_language_v2`: Bengali script → bengali; Latin+Bengali → mixed; Latin+romanized-BN markers → **banglish** (NEW); else english. Returns confidence.
2. **Intent** — greeting/farewell/thanks/identity/capability/math/general_question/chat.
3. **Route**:
   - greeting/thanks/farewell → deterministic (language-matched)
   - identity/capability → registry metadata (verified: creator=Hasibul)
   - math (digit patterns) → deterministic calculator, labeled TOOL
   - everything else → neural `nexus-core-01`, fallback `nexus-medium`
4. **Validation** — degenerate-output rejection → language-aware fallback (never fake neural).

## Verified routing (live tests)
- "Who created you?" → EN identity answer w/ Hasibul ✅
- "তোমাকে কে তৈরি করেছে?" → BN identity ✅
- "kemon acho?" → banglish greeting ✅
- "What is 12 plus 7?" → TOOL "19" ✅
- Open questions → NEURAL_MODEL core01 (weak output — model limitation, not routing) ✅

## Trace fields (per request)
language, lang_conf, intent, model_used, route, tool, neural_ran, fallback, provenance{model_id,checkpoint,engine}
