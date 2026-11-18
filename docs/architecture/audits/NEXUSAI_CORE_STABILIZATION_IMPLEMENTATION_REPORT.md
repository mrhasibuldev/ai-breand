# NEXUSAI — GATE B IMPLEMENTATION REPORT

**Date:** 2026-11-10 · Gate B tasks 1–5 · No training, no checkpoint/dataset changes, no push

## A. What was wrong → what changed
| Problem | Fix |
|---|---|
| API sends `history`, orchestrator read only `conversation_history` → context silently dropped | `_normalize_history()` in `main.py` accepts BOTH keys; `conversation_history` wins on conflict (logged, never merged) |
| No way to test pure neural output (canned handlers always intercept) | `neural_only:true` request flag → `NexusBrain.respond(neural_only=True)` bypasses ALL deterministic/tool/fallback paths |
| Neural provenance lacked checkpoint hash | registry provenance now includes `checkpoint_path`, `checkpoint_sha256`, `tokenizer`, `vocab_size` |
| No automated history tests | `test_history_contract.py` — 13 cases |

## B. Files changed (all backed up first)
- `packages/ai-core/ml-service/main.py` — `_normalize_history()` + `neural_only` flag
- `packages/ai-core/ml-service/model_router.py` — `neural_only` param, neural-only branch, provenance in trace
- `packages/ai-core/ml-service/model_registry.py` — richer provenance dict
- NEW `packages/ai-core/ml-service/test_history_contract.py`
- NEW `scripts/eval_neural_only.py`
- Backups: `backups/20261110_gateb/` — manifest `eval_reports/nexusai_gate_b_backup_manifest.json` (**21 files, all hashes verified**)

## C. Backup verification
21 artifacts hashed (5 source copies verified byte-identical + 16 checkpoints/tokenizer/corpus hash-recorded). Rollback: copy `backups/20261110_gateb/ml-service/*.py` back over `packages/ai-core/ml-service/`.

## D. History fix details
- Precedence rule: `conversation_history` > `history` (documented; conflict printed to log)
- Normalization: dict or string entries, role+content preserved, max 12 msgs / 2000 chars each, trailing duplicate of current message removed, BN/EN/mixed UTF-8 safe
- Isolation: keyed by `conversation_id` upstream; normalization is per-request only

## E. Neural-only mode
- Request: `{"message": ..., "neural_only": true}` → response_source still `NEURAL_MODEL`, trace has `neural_only:true`, `route:neural:nexus-core-01`, provenance w/ sha256
- On failure: `route:"neural_failed"`, empty response + error — **no canned substitution**
- Production default unchanged (neural_only defaults false)

## F. Test results
- History contract: **13/13 PASS** (`python test_history_contract.py`)
- Neural-only eval: **22/22 executed**, all routed `nexus-core-01` — quality: **ALL FAIL** (honest — undertrained model, gibberish-level output). See `NEXUSAI_NEURAL_ONLY_EVALUATION.md` + `eval_reports/nexusai_neural_only_evaluation.json`
- Production regression: greeting→DETERMINISTIC, identity→DETERMINISTIC(Hasibul), math→TOOL(19), open Q→NEURAL ✅ unchanged

## G. Honest quality statement
Neural-only mode proves Core-01 genuinely generates every response (no canned path possible). It also proves the model is **not yet a useful conversational AI** — outputs are English-ish fragments, wrong language for BN/BL prompts, no reliable context use. This is expected pre-Run4.

## H. Remaining limitations
- Model quality: needs Run4 (prepared) then Run5+ scaling
- History reaches prompt as concatenated context (last 3 msgs) — model can't yet exploit it meaningfully
- Medium fallback wrapper minimal; neural_only correctly refuses fallback
- Bengali-digit math still not tool-covered

## I. Rollback
Restore 3 .py files from `backups/20261110_gateb/ml-service/`; delete new test/eval scripts. Registry/router additions are additive.
