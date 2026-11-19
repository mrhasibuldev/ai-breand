# NexusAI Web Chat Mode — Forensic Audit

**Date:** 2026-11-19 · **Mode audited:** normal Web Chat (NEURAL_ONLY_CHAT unset → OFF) · **Method:** read-only code trace + live in-process reproduction of all 10 prompts through `NexusBrain.respond()` (the exact code path `/orchestrate` executes) + live HTTP verification of `/orchestrate` for 2 prompts.

---

## 1. Executive summary

Normal Web Chat is **not primarily a neural chat system**. It is a deterministic-first router: intent classification sends greetings, identity, capability, thanks, farewell, and math-shaped messages to hardcoded templates or a tiny regex calculator; only unmatched intents reach neural cores. Even then, Core-01 (the general model) produces English word-salad/math-fragment garbage for most Bengali prompts, and the language-aware fallback text is what users actually see for roughly half of realistic inputs. The correct identity answer the user observed is a **hardcoded Bengali template**, not neural output. Core-04 produced a fluent but factually wrong Bengali sentence for a contradiction question — fluent surface, zero understanding.

**Bottom line:** the pipeline plumbing is verified correct end-to-end; the failures are dominated by (a) deterministic handlers masking neural incapacity, (b) Core-01/medium model quality, (c) tokenizer fragmentation of Bengali, and (d) a provenance bug that mislabels specialist neural output. No evidence of external AI anywhere in the path.

## 2. Safety baseline

- Repo `C:\Users\Nusaiba\Desktop\Ai Breand`, branch `main`, HEAD `2c475adfefcce58b5e34a42076df76b46095641d` = `origin/main` (verified via `git ls-remote`).
- `git status`: 1 modified tracked file (`__pycache__/main.cpython-314.pyc` — runtime artifact) + known untracked dirs (backups/, exports/, corpora). No user work touched.
- This audit modified **zero** source files. Only artifacts created: this report + `eval_reports/web_chat_forensic_audit.json`. The ML service was started (read-only runtime) for HTTP verification; it was already running earlier and was restarted after it stopped — no config changed.

## 3. Actual Web Chat architecture (verified)

```
Browser ChatInterface.tsx
  POST http://localhost:4000/api/v1/ai/chat   {message, conversationId, context:[history]}
    (guest: in-memory history; auth: Supabase-persisted)
        │
        ▼
apps/api/src/routes/ai.ts  POST /api/v1/ai/chat  (optionalAuthMiddleware)
        │  builds ModelRequest{operation:'chat', context:[{message, conversation_id, user_id, history}]}
        ▼
apps/api/src/intelligence-engine.ts  NexusAIIntelligenceEngine.respond()
        │  contextBuilder (guest: extractHistoryFromContext — BUG, see §9)
        │  memoryService.retrieveMemories (Neon, consent-gated)
        │  POST {AI_SERVICE_URL||http://127.0.0.1:8000}/orchestrate  (10 s AbortController timeout)
        ▼
packages/ai-core/ml-service/main.py  POST /orchestrate
        │  UTF-8 BOM-safe parse → _normalize_history (≤12 msgs, ≤2000 chars)
        │  safety_guard.check_input  → SAFETY_BLOCK canned reply if unsafe
        │  NEURAL_ONLY_CHAT env flag (absent → OFF); per-request neural_only flag also honored
        ▼
packages/ai-core/ml-service/model_router.py  NexusBrain.respond(message, history, neural_only=False)
        │  detect_language_v2 → classify_intent_v2
        │  ├─ deterministic: GREETING/THANKS/FAREWELL/IDENTITY/CAPABILITY → hardcoded pick()
        │  ├─ MATH → specialist core-03 (greedy) → else try_math_tool regex calculator (labeled)
        │  ├─ REASONING→core-02, KNOWLEDGE→core-04 specialists (_try_specialist)
        │  ├─ neural: core-01 (temp .8, sample, 64 tok) → nexus-medium fallback (temp .8)
        │  └─ all failed/degenerate → FALLBACKS[lang] honest apology
        ▼
main.py: if trace.neural_ran → safety_guard.check_output → may substitute fallback (normal mode)
        ▼
OrchestratorResponse{response, intent, response_source, language, diagnostics:[trace], ...}
        ▼
intelligence-engine.ts: throws NEURAL_* if empty/fail-source; else returns text
        ▼
api.ts reply: {response, conversationId, messageId, latencyMs, provider:'nexusai-python-ml', contextInfo}
        │  ⚠ diagnostics/response_source/rejection_reason are DROPPED here
        ▼
ChatInterface renders data.response
```

**Stage status:** UI VERIFIED (code) · API route VERIFIED · intelligence-engine VERIFIED · orchestrate VERIFIED (live HTTP) · brain/router VERIFIED (live, all 10 prompts) · transformer VERIFIED (prior audits) · provenance-to-UI **FAILED** (dropped at api.ts).

## 4. Normal Chat vs Neural-Only (verified from code)

| Behavior | Normal Chat | Neural-Only |
|---|---|---|
| Routing | intent → deterministic / specialist / core-01→medium | eligible cores only: core-01, core-03, core-04 (core-02 & medium excluded) |
| Deterministic handlers | YES — greeting/thanks/farewell/identity/capability/math-tool | NO — bypassed entirely |
| Neural generation | only for CHAT/GENERAL_QUESTION/unmatched intents | every message |
| Fallback | language-aware apology text; safety_guard output substitution | explicit error codes only, never text substitution |
| Error handling | NEURAL_* → HTTP 502 → UI Bengali error message | same, with structured rejection_reason |
| Provenance | `trace` exists in diagnostics but **api.ts drops it**; UI cannot distinguish | same drop; diagnostic_mode exposes raw_neural_output only at ML layer |

Activation: env `NEURAL_ONLY_CHAT` (absent in `.env`/`.env.example` → OFF) **or** per-request `neural_only:true` — the API never sends it, so the UI can only ever reach normal mode. No UI toggle exists.

## 5. Ten regression tests — reproduced results

All run through `brain.respond(..., neural_only=False)` = production path. Full data: `eval_reports/web_chat_forensic_audit.json`.

| # | Prompt (abbr.) | Intent | Route / Model | Response (excerpt) | Score 0–5 |
|---|---|---|---|---|---|
| 1 | নাম কী, কে তৈরি | IDENTITY | `registry:identity_metadata` (deterministic) | Correct Bengali identity template — **exact match to user's observed output** | n/a neural; deterministic 5 |
| 2 | মোমবাতি riddle | CHAT | core-01 → degenerate → `fallback` | "দুঃখিত, এই প্রশ্নের সঠিক উত্তর দিতে…" (user's run got "The Greekms…" — same core-01 failure, sampling variance) | 0–1 |
| 3 | tallest/shortest logic | CHAT | neural:core-01 | "In the United States, Rafael Niko island and Africa's name former…" | 0 |
| 4 | ১৫টি আম ভাগ | CHAT | neural:core-01 | ":348697 million - 1.2 = <<21=22>>27 #### 9" (user saw fallback apology) | 0 |
| 5 | উত্তর না জানলে | CHAT | neural:core-01 (HTTP-verified `NEURAL_MODEL`) | "First find the number of people can cry. Then subtract… <<3*12=5>>5" | 0 |
| 6 | কলা word problem | CHAT | neural:core-01 | "+ 40% = <<40+10=320>>3500 pounds. #### 100" | 0 |
| 7 | বাংলায় কথা বলতে পারো? | GENERAL_QUESTION (lang=mixed) | core-01 degenerate → **nexus-medium** | "তুমি কোন ভূমিকা পালন করেছিলেন। তুমি?" — Bengali but incoherent | 1 |
| 8 | লাল/নীল contradiction | KNOWLEDGE | neural:**core-04** (5.3 s) | "DNA হলো একটি সুসংগাদি।" — fluent Bengali, wrong fact | 1 |
| 9 | empathetic help | CHAT | neural:core-01 | "First find the total number of object by multiplying: 3 = <<3*3=18>>18…" | 0 |
| 10 | Honesty about not knowing | CHAT | neural:core-01 | "Bydamer is a bomburn in a tarmer cubble…" | 0 |

**Score summary:** neural-path responses averaged ~0.3/5. The only good answers came from deterministic templates (T1) or the fallback apology (T2 this run) — neither is intelligence.

## 6. Per-test trace (key evidence)

- **T1:** `classify_intent_v2` IDENTITY regex (`তোমার নাম|তোমাকে কে`) → `pick(IDENTITY_ANSWER,'bn')` → the observed sentence verbatim. `neural_ran=false`. HTTP `/orchestrate` confirmed `response_source: DETERMINISTIC_HANDLER`.
- **T2/T3/T4/T6/T9/T10:** intent=CHAT (Bengali text matches no keyword class; Bengali numerals ৫/২/১৫ are not `\d` so MATH_PATTERNS never fire) → `_generate_neural` → core-01 @ temp 0.8 sampling → degenerate or English math-corpus fragments (`<<…>>` calculator-style markup is literally Core-01's pretraining format) → `_is_degenerate` rejects some → `FALLBACKS['bengali']`.
- **T5:** HTTP-verified `NEURAL_MODEL` / `nexus-core-01` — safety_guard `check_output` did NOT catch the English math gibberish (it passes "has linguistic content" heuristics).
- **T7:** GENERAL_QUESTION has **no specialist** → core-01 failed → **nexus-medium** produced weak Bengali. Medium is excluded from neural-only precisely because of this.
- **T8:** KNOWLEDGE → `_try_specialist` → core-04 greedy → fluent memorized fact unrelated to the contradiction question (prompt-insensitivity already documented).

## 7. Model & checkpoint mapping (verified vs `model_registry.py`)

| Model | Checkpoint | Params | Role in normal chat | Neural-only eligible |
|---|---|---|---|---|
| nexus-core-01 | `checkpoints_core01_run3/checkpoint_final.pt` sha256 `ad515c…7830` | 8,842,560 | PRIMARY for CHAT/GENERAL_QUESTION | YES |
| nexus-core-02 | `checkpoints_core02_sft_v2/` sha256 `906d60…` | 20,347,712 | REASONING specialist | NO (excluded) |
| nexus-core-03 | `checkpoints_core03_sft_v2/` sha256 `1ff83f…` | 8,842,560 | MATH specialist | YES |
| nexus-core-04 | `checkpoints_core04_sft_v3/` sha256 `e46383…` | 33,419,072 | KNOWLEDGE specialist | YES |
| nexus-medium | `checkpoints_medium/final_model.pt` | 2,452,544 | fallback after core-01 | NO |
| core-05 | **does not exist** — proposal only | — | — | — |

Registry is hash-gated + strict state-dict; no checkpoint/config/tokenizer mismatch path found. All cores share `core01/transformer.py` + `sp_bpe_8k` (vocab 8000, bos2/eos3/pad0/unk1) — consistent with prior audits.

**Provenance bug (confirmed):** `model_registry.generate()` sets `neural_generation_executed = eng["kind"] in ("core01","medium")` → for `nexus_sft` (core-02/03/04) it reports **False even though `chat_generate` runs genuine transformer generation**. `trace.neural_ran` is set manually by the brain so `response_source` stays correct, but the provenance dict is wrong.

## 8. Tokenizer investigation (live `sp_bpe_8k`)

| Input | chars | tokens | tok/char | UNK |
|---|---|---|---|---|
| Bengali sentence | 38 | 10 | 0.26 | 0 |
| Bengali math word problem | 59 | 21 | 0.36 | 0 |
| Bengali candle text | 50 | 24 | **0.48** | 0 |
| English sentence | 32 | 10 | 0.31 | 0 |
| Banglish | 46 | 27 | **0.59** | 0 |
| Mixed BN/EN | 31 | 12 | 0.39 | 0 |

- Zero UNKs, but Bengali splits mid-word constantly: `মো ম বা তি`, `প্র ত্য ে কে`, `জ নের`; Banglish degenerates to near-char level (`t um i`, `k em on`).
- Bengali numerals (৫, ১৫) tokenize as single pieces; ASCII `15+27` splits oddly (`+2 7`).
- **Confirmed contributing factor:** the 8K BPE vocab was not built for Bengali morphology; a 8.8M-param model must compose meaning from single-char pieces it rarely saw coherently in training. This plausibly explains why Core-01 answers Bengali prompts with English corpus fragments — Bengali conditioning is weak.

## 9. Generation & decoding (code-verified, fixes intact)

- F2 (`is not None`), F3 (per-row `finished` mask), temp clamp `max(t,1e-8)` — all present in `transformer.py` (lines ~407–416). `test_generation_repairs.py` 13/13 PASS (prior mission).
- Core-01 chat path: `temperature=0.8, do_sample=True, max_new_tokens=64, top_k=50, top_p=0.9, rep_penalty=1.2` — **high-temperature sampling on a weak model maximally produces word salad**. Specialists use greedy (`do_sample=False`, temp 0.3).
- Specialists format prompt as `[BOS] user: <text> [EOS]` expecting `assistant:` continuation (`nexus_core.chat_prompt_ids`) — correct SFT format.
- **Confirmed bug:** `intelligence-engine.ts:179` `extractHistoryFromContext` checks `'role' in item && 'content' in item` on the **wrapper** object instead of each `msg` → guest conversation history is **always empty**. Authenticated users get history via `contextBuilder.buildContext` (DB), so only guests lose context. P2.
- `check_output` safety guard passes English math-fragment gibberish (T5) — heuristic too weak for cross-language degenerate output. P2.

## 10. Dataset evidence (manifests, unmodified)

- core02_reasoning_v1: 2,386 train (60% exact duplicates per prior audit), "deterministic logic templates" self-declared; held-out test same generators → limited generalization.
- core03_math_v1: 1,576 train, procedural verified arithmetic; Bengali only 270/1,576.
- core04_knowledge_v1: **256 train total** — extremely small; Bengali 111.
- Conversational V1–V4 exist under `data/` phases; Bengali/Banglish conversational coverage remains thin. Core-01's English math-corpus output on Bengali prompts is consistent with English-dominant pretraining.

## 11. Root causes

| # | Issue | Class | Confidence | Layer |
|---|---|---|---|---|
| RC1 | Intent router sends most real questions to deterministic templates or Core-01; correct-feeling answers are canned | CONFIRMED | certain | model_router.py |
| RC2 | Core-01 (primary CHAT model) produces English math-corpus fragments for Bengali prompts | CONFIRMED (model quality + weak BN conditioning) | certain | weights/data, not code |
| RC3 | Bengali tokenizer fragmentation (0.36–0.59 tok/char, mid-word splits) | CONFIRMED contributing factor | high | tokenizer/data |
| RC4 | Guest history extraction bug → zero context for all guest chats | CONFIRMED BUG | certain | intelligence-engine.ts:179 |
| RC5 | Provenance mislabel: `neural_generation_executed=False` for core-02/03/04 | CONFIRMED BUG | certain | model_registry.py |
| RC6 | api.ts drops diagnostics/response_source → user cannot distinguish neural vs deterministic | CONFIRMED | certain | apps/api/src/routes/ai.ts |
| RC7 | `check_output` misses cross-language degenerate neural output | CONFIRMED (weak heuristic) | high | safety_guard |
| RC8 | Specialist datasets tiny/template-bound; core-04 prompt-insensitive | NOT A BUG — model quality | certain | data/training |
| RC9 | 10 s API→ML timeout vs core-04 ~5.3 s/gen — headroom thin under load | POSSIBLE CONTRIBUTING | medium | intelligence-engine.ts |

**Direct answer:** normal Chat Mode is *substantially* deterministic+fallback, not neural. Of 10 tests: 1 deterministic-correct, 2 neural-but-degenerate→fallback/medium, 6 neural garbage, 1 neural fluent-but-wrong. Genuine neural generation executes and is correctly routed — it is simply not yet capable.

## 12. Remediation plan (no implementation)

1. **P0 — surface provenance to UI** (api.ts forward `response_source`/`diagnostics`; UI badge). Files: `apps/api/src/routes/ai.ts`, ChatInterface. No checkpoint/dataset change. Makes RC1/RC6 visible instead of hidden.
2. **P1 — fix guest history bug** (`'role' in msg`). One-line fix + test. Restores context for guests.
3. **P1 — fix `neural_generation_executed` for nexus_sft** (set True for kind `nexus_sft`). One-line + test.
4. **P1 — strengthen `check_output`** for cross-language degenerate/`<<…>>` markup detection so gibberish routes to honest fallback instead of NEURAL_MODEL. File: `safety_guard.py`.
5. **P2 — reconsider sampling for weak models**: core-01 at temp 0.8 produces maximal garbage; consider lower temp/greedy for CHAT until quality improves (config/flag change — needs approval, affects behavior).
6. **P2 — Bengali tokenizer**: the 8K BPE is the hardest ceiling; a larger/morphology-aware vocab is a *future approved* retrain decision — document, don't act.
7. **P3 — datasets**: core-04 256 examples and core-02 template duplicates cap specialist quality; any expansion requires the V5 dataset mission.
8. Do **not** recommend architecture change or external AI — evidence points to data/tokenizer/training-volume, not the Transformer implementation.

## 13. Verdicts

- **Pipeline integrity:** VERIFIED — request reaches the correct registered checkpoint with correct tokenizer; no external AI; hashes enforced.
- **Chat Mode intelligence:** FAILED for open-ended conversation — deterministic handlers + fallbacks carry the UX; neural cores produce mostly incoherent output on Bengali prompts.
- **Neural-only mode:** mechanically VERIFIED previously; would currently return mostly garbage or explicit errors — honest but not useful.
- **Suitable for reliable general conversation:** NO.

## 14. Unverified / limitations

- Authenticated-user path (DB history/memory) not exercised — code-read only.
- Web build not run; UI rendering of responses assumed from code.
- `safety_guard.check_output` internals not fully audited line-by-line.
- Exact per-prompt token IDs not captured (would need instrumentation — out of scope).
