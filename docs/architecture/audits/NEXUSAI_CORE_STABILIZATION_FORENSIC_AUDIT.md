# NEXUSAI CORE — STABILIZATION FORENSIC AUDIT (Gate A)

**Date:** 2026-11-10 · READ-ONLY · No source/config/checkpoint modified
**Companion evidence:** `eval_reports/nexusai_core_stabilization_audit.json`

## 1. Executive summary
The system was already partially stabilized earlier today (multi-model integration): Core-01 run3 is the active neural model behind a validated registry+router; deterministic handlers are labeled; fallbacks are language-aware. **Remaining confirmed defects:** (a) conversation-history key mismatch drops context, (b) Core-01 run3 neural quality is weak (needs Run4), (c) no neural-only test mode exists yet, (d) medium fallback wrapper is minimal.

## 2. Current architecture (verified)
```
Web :3000 → Fastify api :4000 POST /api/v1/ai/chat
  → intelligenceEngine.respond → POST ml-service :8000/orchestrate
  → model_router.NexusBrain.respond()
      detect_language_v2 → classify_intent_v2
      → deterministic (greeting/thanks/bye/identity/capability)
      → math tool → neural registry.generate(nexus-core-01 → nexus-medium)
      → degenerate check → language-aware fallback
  → OrchestratorResponse{response,intent,response_source,language,diagnostics[]}
```

## 3. Model inventory (re-verified)
| ID | Arch | Params | Ckpt | Hash | Status |
|---|---|---|---|---|---|
| nexus-core-01 | core01 6L/256/8H/1024 ctx512 | 8,842,560 | checkpoints_core01_run3/checkpoint_final.pt | ad515cad…7830 ✅ | ACTIVE, validated, strict-load PASS |
| nexus-medium | medium 2L/128/2H/512 ctx128 | 2,468,928 | checkpoints_medium/final_model.pt | 4f592af9… | fallback |
| excluded | small×5 (185K), medium-epoch×5 (4.9M vocab74) | — | — | — | tokenizer-incompatible |
| checkpoints_retrained/ | — | — | EMPTY dir | — | nothing inside |

- Run4: **NOT started** — no `checkpoints_core01_run4/` dir exists; corpus/bundle/cell prepared only.
- Tokenizer: sp_bpe_8k vocab 8000 shared, verified multilingual, UNK ~0.12%.
- No state-dict key mismatch for core01 (strict load verified in registry.load).

## 4. Neural generation evidence (verified)
- `model.forward` instrumented: exactly 25 calls per 25-token generation → real autoregressive inference.
- Checkpoint status PRETRAINING_COMPLETED; tokenizer vocab 8000 matches config.
- Outputs are genuine model generations — semantically weak (undertrained), not canned.

## 5. Response-origin classification (current)
- neural: route=`neural:nexus-core-01`, neural_ran=true, provenance{model_id,checkpoint}
- deterministic: greeting/thanks/bye/identity/capability — labeled, honest metadata
- tool: math — labeled deterministic calculator
- fallback: language-aware apology strings, only on neural failure/degenerate
- retrieval: DISABLED (commented in main.py; cannot answer)
- external AI: NONE found (repo-wide grep; only dataset-source URLs)

## 6. History bug — CONFIRMED STILL PRESENT
- `apps/api/src/intelligence-engine.ts:98` sends `history: conversationContext.messages`
- `ml-service/main.py` orchestrate reads `body_data.get('conversation_history')` → always empty → **context dropped for every chat**
- Also brain path reads `conversation_history` (model_router.respond arg) — same mismatch
- Impact: no multi-turn context reaches model; follow-ups can't work
- Fix needed: normalize in one place (accept both keys) — backward compatible

## 7. Retrieval status
`simple_retrieval`/`rag_system` imported but usage commented out; brain path bypasses legacy block entirely. Cannot produce answers. Leave disabled for milestone.

## 8. External AI dependencies
None found in scanned source. Runtime network behavior to external AI: not fully verifiable, but no code path exists to call one.

## 9. Test coverage
- Existing: eval_core01_run3.py (22 prompts), forensic/provenance audit scripts, ml-service has test_*.py files (consent/db/simple-gen — check relevance)
- Missing: neural-only mode, history-contract tests, registry unit tests

## 10. Root causes (remaining)
1. History key mismatch → context loss [code bug, HIGH]
2. Undertrained model → weak answers [data/compute, HIGH — Run4 pending]
3. No neural-only test harness [test gap, MED]
4. Medium fallback wrapper minimal [MED — emergency only]

## 11. Proposed implementation plan (Gate B — needs approval)
1. Backup `intelligence-engine.ts`, `main.py`, `model_router.py` → `backups/<ts>/`
2. Fix history contract: orchestrate accepts `history` OR `conversation_history`; normalize once; preserve order/roles; dedupe current msg; cap context; per-conversation isolation (conversation_id already passed)
3. Add neural-only mode: `/orchestrate?mode=neural` or `diagnostic_mode` extension bypassing deterministic handlers → direct registry.generate with full provenance
4. Add history unit tests (empty/1/N msgs, BN/EN/mixed, malformed, isolation)
5. Re-run neural-only suite (EN/BN/Banglish/context/generalization) + 13-test regression
6. Write implementation + evaluation reports; Run4 readiness report (already mostly prepared)

## 12. Files that would change
- `apps/api/src/intelligence-engine.ts` (history key) — or `ml-service/main.py`+`model_router.py` normalize (prefer ml-service side: accept both keys — zero api change)
- `ml-service/model_router.py` — neural_only flag
- `ml-service/main.py` — pass mode param
- NEW test file(s) under ml-service or scripts/

## 13. Risks
- Low: additive changes, try/except-guarded brain path, backups exist
- History fix could alter prompt content → re-run eval to confirm no regression

## 14. Cannot verify
- Whether frontend sends additional context fields (request.context vs history) — inspect at implementation
- Long-history truncation behavior — will test

## VERDICT: Gate A audit complete — awaiting approval for Gate B implementation.
