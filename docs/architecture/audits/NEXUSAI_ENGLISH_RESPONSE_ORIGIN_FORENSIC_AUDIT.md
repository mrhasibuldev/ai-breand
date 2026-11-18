# NEXUSAI — ENGLISH RESPONSE ORIGIN FORENSIC AUDIT

**Date:** 2026-11-10 · READ-ONLY · DB evidence: `nexus.messages` (332 rows) + `eval_reports/db_messages_recent.json`

## A. Executive summary (simple language)
The "good English responses" were **NOT** produced by a smart neural model. Forensic DB evidence shows every stored assistant reply falls into exactly three buckets: (1) clean **deterministic canned English** (greetings/identity — these look good because they're pre-written), (2) **Bengali fallback apologies**, or (3) **neural gibberish** from the weak 2.47M medium model. No external AI API exists in the codebase. No retrieval answered anything (disabled). The independent neural model (Core-01) genuinely generates text — but its output is currently poor.

## B. Conversation timeline (verified from `nexus.messages`)
Latest conversation: **2026-11-09 19:26–21:08 UTC** (before today's multi-model integration). Selected exchanges:

| Time (UTC) | User | Assistant response | Origin |
|---|---|---|---|
| 19:26:34 | hello | "Hello! I'm NexusAI, your personal AI assistant…" | DETERMINISTIC greeting |
| 19:27:06 | বাংলা: কৃত্রিম বুদ্ধিমত্তা… | "আমার নাম NexusAI। আমি একটি কাস্টম AI সহকারী…" | DETERMINISTIC (wrong intent — 'নাম'/'কি' keyword bug) |
| 19:27:30 | English: How does AI learn? | "দুঃখিত, এই বিষয়টি…" | NEURAL→fallback (empty/degenerate) |
| 19:28:59 | বাংলা: সমস্যার সমাধান… | same identity canned | DETERMINISTIC (same bug) |
| 19:29:27 | বাংলা: ২৫০ টাকার ২০ শতাংশ | "= $<<" | NEURAL gibberish |
| 19:30:27 | What is your actual model architecture? | "…, the total of the remaining = $<<…" | NEURAL gibberish (medium model) |
| 20:11:37 | What is artificial intelligence? | "Suly, Romano is the most famous formergment of Greece…" | NEURAL gibberish |
| 20:12:55 | Tumi ki? Tomar kaj ki?… | echo + gibberish | NEURAL (echo not caught) |
| 20:14:56 | 2+2 | "There are 30 days in the sale…" | NEURAL gibberish |

Historical messages (Oct 26–Nov 8): same pattern — deterministic greetings + neural gibberish + fallbacks. **No evidence of any genuinely good/coherent answer in the entire message store.**

## C. Execution trace (verified in code)
```
Web chat → POST /api/v1/ai/chat (apps/api/src/routes/ai.ts:34)
  → intelligenceEngine.respond (apps/api/src/intelligence-engine.ts:88)
      NOTE: sends keys `history`, `memory` — but /orchestrate expects
      `conversation_history` → history was DROPPED (key mismatch bug)
  → POST http://127.0.0.1:8000/orchestrate (ml-service/main.py)
      → detect_language → intent classify → deterministic handlers OR
        generator.generate (medium model) → validation → fallback
```

## D. Which model produced the Nov-9 responses?
At that time (before today's change): **checkpoints_medium/final_model.pt** — MediumTransformer, 2,468,928 params, trained on Phase-10 (1,812 samples). Its English-flavored outputs are the "English-looking" gibberish (gsm8k-style number fragments). NOT Core-01 (disconnected then).

## E. Dataset investigation
- english_first (Core-01): 63,876 docs / 7.43M tokens — trained runs 1–3, losses verified — but checkpoint was NOT serving the app during those chats.
- Phase-10 (medium model): ~1,812 samples — the actual serving model; explains gibberish.
- No dataset is queried at inference time (retrieval disabled).

## F. External AI APIs — DISPROVEN
Repo-wide grep: only dataset-source URLs mentioning `openai/grade-school-math` (GSM8K data, not API). Zero OpenAI/Anthropic/Gemini/Groq/OpenRouter calls in apps/ or packages/. No external inference dependency.

## G. Deterministic handlers
- Greeting/farewell/thanks/help/identity/capability: canned strings (clean English — likely what looked "good")
- Bengali intent bug: `['নাম','কী','কি','তোমার']` substring match → most Bengali questions misrouted to identity answer
- Fallback: fixed Bengali apology regardless of language
- Math: none deterministic (that's why "2+2" → gibberish)

## H. Reasoning verification
Nothing in the logs demonstrates reasoning: no multi-step processing, no context use (history key mismatch dropped it), no consistent paraphrase answers. Neural outputs are next-token predictions from an undertrained 2.5M model.

## I. English vs Bengali difference — explained
English "looked better" because: (a) deterministic English handlers produce clean text; (b) medium model emits English-flavored fragments (trained mostly on English-ish Phase-10 data); (c) Bengali questions hit the intent bug → canned Bengali identity or Bengali fallback. It is a **routing/data artifact, not superior intelligence.**

## J. Evidence registry
| Evidence | Source | Confidence |
|---|---|---|
| 332 stored messages, all gibberish/canned/fallback | `nexus.messages` query | PROVEN |
| API→orchestrate path | `intelligence-engine.ts:88-119` | PROVEN |
| history key mismatch (`history` vs `conversation_history`) | `intelligence-engine.ts:98` vs `main.py:633` | PROVEN |
| Medium ckpt serving pre-integration | ml-service logs + `main.py:271` | PROVEN |
| No external AI calls | repo grep | PROVEN (absence) |
| Retrieval disabled | `main.py` commented block | PROVEN |
| Core-01 real generation | forward-call instrumentation (prev audit) | PROVEN |

## K. Final verdict
**OWN_NEURAL_MODEL_WITH_DETERMINISTIC_SUPPORT** — but with a critical honest qualifier: the neural model involved in those chats was the **weak legacy medium model**, and the "good-looking" English was mostly **deterministic canned text + English-flavored gibberish**. Core-01 run3 (the better model) genuinely generates but was not connected at that time. No external AI, no retrieval, no dataset lookup produced the answers.

## L. Recommended next steps (not implemented)
1. Run4 training (prepared) to actually improve neural quality.
2. Fix `history`→`conversation_history` key mismatch in intelligence-engine.ts.
3. Already-fixed (today): core01 active, multilingual routing, language-aware fallbacks — re-run the same conversation to compare.
4. Canned handlers: keep only greetings; route knowledge questions to neural.

---
## বাংলা সারসংক্ষেপ (Owner-এর জন্য)
আপনার দেখা "ভালো English উত্তর" আসলে ভালো ছিল না — database-এ সেভ করা সব উত্তর তিন রকম:
(১) আগে থেকে লেখা canned English greeting/identity, (২) Bengali fallback ক্ষমা, (৩) দুর্বল 2.47M মডেলের engrish/mixed টেক্সটের এলোমেলো উত্তর।
কোনো external AI বা retrieval ব্যবহার হয়নি — codebase সৎ আছে, কিন্তু মডেল undertrained। Run4 training করলেই neural improve হবে।
