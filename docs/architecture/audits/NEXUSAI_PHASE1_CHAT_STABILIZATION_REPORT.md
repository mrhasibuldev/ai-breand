# NexusAI Phase 1 — Chat System Stabilization: Implementation Report

**Date:** 2026-11-19 · **Scope:** the five authorized areas only · **Boundary:** no training, no checkpoint/tokenizer/dataset changes, no commit/push.

## Changed files

| File | Change |
|---|---|
| `apps/api/src/intelligence-engine.ts` | Guest-history bug fix; capture + return ML provenance fields (`responseSource`, `rejectionReason`, `intent`, `modelUsed`, `neuralRan`) on `ModelResponse` |
| `apps/api/src/routes/ai.ts` | Forward the five provenance fields in `POST /api/v1/ai/chat` reply |
| `packages/ai-core/ml-service/model_registry.py` | `neural_generation_executed` now true for `nexus_sft` kind |
| `packages/ai-core/ml-service/safety_guard.py` | `check_output` gains `calc_markup_leak` (`<<`/`>>`/`####`), `language_mismatch` (all-Latin >40 chars for `expected_lang=bengali`), new fallback messages |
| `packages/ai-core/ml-service/model_router.py` | Bengali digit normalization (০-৯→0-9); `BENGALI_MATH_RE` + digit-gated MATH intent; `try_math_tool` Bengali operators + equal-share division + give-away subtraction; **MATH branch reordered: deterministic tool before specialist** |
| `packages/ai-core/ml-service/main.py` | Pass `expected_lang` from trace language into `check_output` |
| `packages/ai-core/tests/four_core/test_phase1_stabilization.py` | NEW — 16 regression tests |

## What was implemented

1. **Provenance propagation** — ML `diagnostics[0]` trace fields now flow ML → intelligence-engine → API reply. Verified live: `{"responseSource":"DETERMINISTIC_HANDLER","intent":"IDENTITY","modelUsed":null,"neuralRan":false}` and `{"responseSource":"TOOL","modelUsed":"none(tool)"}`.
2. **Guest history bug** — `'role' in item` → `'role' in msg` in `extractHistoryFromContext`. Guest conversations now send real history to `/orchestrate`.
3. **Registry provenance** — `neural_generation_executed` includes `"nexus_sft"`; core-02/03/04 neural output no longer mislabeled.
4. **Output guard** — conservative additions only; deterministic/fallback sources unaffected; short answers unaffected.
5. **Bengali math routing** — `১৫টি আম ৩ জনের মধ্যে সমান ভাগ` and `১০টি কলা…৩টি বিক্রি…২টি দিল` now classify MATH and return labeled deterministic answers; ASCII math unchanged.

## Verification evidence

- `test_phase1_stabilization.py`: **16/16 PASS**
- `test_generation_repairs.py`: **13/13 PASS** (no regression)
- `tsc --noEmit -p apps/api`: clean
- Live `/orchestrate` (restarted ML service):
  - `১৫টি আম…` → `TOOL` `15 ÷ 3 = 5 (নির্ণায়ক ক্যালকুলেটর)`
  - `১০টি কলা…` → `TOOL` `10 - 5 = 5 (নির্ণায়ক ক্যালকুলেটর)`
  - `What is 15 + 27?` → `TOOL` `42` (previously core-03 returned wrong `22.`)
  - empathy prompt → `FALLBACK` honest Bengali (was English gibberish as NEURAL_MODEL)
- Live `POST /api/v1/ai/chat` (real API): provenance fields present and correct for IDENTITY and MATH cases.

## Honest limitations (unchanged)

- Core-01/medium neural quality unchanged — Bengali open-ended CHAT still mostly falls back honestly now instead of showing gibberish.
- core-03 specialist is bypassed whenever the deterministic tool parses the math — intentional (tool is exact + labeled); specialist still serves unparseable MATH prompts.
- T7-style short English fragments (<40 chars) can still pass the language guard — conservative threshold by design.
- UI does not yet *display* the new provenance fields (API returns them; rendering is a future UI task).
- Not committed/pushed per boundary.
