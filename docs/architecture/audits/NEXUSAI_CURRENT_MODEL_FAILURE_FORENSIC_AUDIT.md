# NEXUSAI — CURRENT MODEL FAILURE FORENSIC AUDIT

**Date:** 2026-11-10 · READ-ONLY · No code/checkpoint/data modified
**Live test artifact:** `eval_reports/forensic_orchestrate.json`

## 1. Executive summary
NexusAI's chat failures have **multiple confirmed root causes**, the primary being: **the application loads the legacy weak model (`checkpoints_medium`, 2.47M params, trained on ~1,812 samples), NOT Core-01 Run3 (8.84M)**. On top of that, an intent router sends many questions to canned deterministic handlers or Bengali fallback messages before the neural model ever runs, and the neural model itself produces incoherent text.

## 2. Active model identity [VERIFIED — HIGH]
- Server log: `Using default checkpoint path: .../models/checkpoints_medium/final_model.pt`
- File: 29,539,569 bytes · SHA-256 `4f592af9846b89652eb7…` (prefix)
- State-dict params: **2,468,928** (service log reports 2,452,544 via `count_parameters` — minor counting difference, same model)
- Checkpoint meta: epoch 2, train_loss 1.0018, val_loss 1.0941 — **suspiciously low** → classic overfit on tiny Phase-10 dataset
- Config in ckpt: d_model=128, n_layers=2, n_heads=2, d_ff=512, max_len=128 — the legacy SmallTransformer/Medium, **NOT Core-01**
- Production designation JSON is malformed (`Extra data: line 1 column 3`) → silent fallback to this ckpt (`main.py` ~line 500)

## 3. Inference pipeline (traced)
```
Web → Fastify API → FastAPI ml-service :8000
  POST /orchestrate (main.py ~617)
    → language detect (regex heuristics)
    → intent classify (English-centric keyword lists, ~780-790)
    → DETERMINISTIC_HANDLER canned replies for GREETING/IDENTITY/CAPABILITY/THANKS/HELP/FAREWELL (~798-869)
    → NEURAL_MODEL only for GENERAL_QUESTION/unknown (~928 generator.generate, temp 0.8, top_k 50, top_p 0.9, rep_penalty 1.2, max 100 tok)
    → output validation → Bengali fallback string on empty/short/echo (~945-960)
```
**The neural model is bypassed for most structured intents.** Retrieval fallback is commented out (disabled for "neural testing").

## 4. The 13 tests — actual results (verbatim in forensic_orchestrate.json)

| # | Input | Lang→Intent | Source | Output (verbatim, truncated) | Verdict |
|---|---|---|---|---|---|
| BN1 | কৃত্রিম বুদ্ধিমত্তা শিখে শিখে কীভাবে? | bn→IDENTITY_QUESTION | DETERMINISTIC | "আমার নাম NexusAI। আমি একটি কাস্টম AI সহকারী…" | WRONG — canned, irrelevant |
| BN2 | একটি সমস্যার সমাধান… | bn→IDENTITY_QUESTION | DETERMINISTIC | same canned | WRONG |
| BN3 | তোমাকে কে তৈরি করেছে? | bn→UNKNOWN | FALLBACK | Bengali apology | WRONG — neural never ran properly |
| BN4 | ২৫০ টাকার ২০% ছাড়… | bn→UNKNOWN | NEURAL_MODEL | "- 4 = $<<1 in a third." | GIBBERISH |
| EN1 | How does AI learn? | en→GENERAL_QUESTION | NEURAL_MODEL | "এবং খাবার করতে পছন্দ করি।" | GIBBERISH (Bengali fragment!) |
| EN2 | What is your actual model architecture? | en→GENERAL | NEURAL | "tos = <<1 = $<< + the cost of a month…" | GIBBERISH |
| EN3 | Who created you? | en→GENERAL | NEURAL | ", and a total of the following." | GIBBERISH |
| EN4 | 20% off 250 taka? | en→GENERAL | FALLBACK | Bengali apology | WRONG |
| BL1 | Artificial intelligence kivabe shikhe? | en→UNKNOWN | FALLBACK | Bengali apology | WRONG — Banglish undetected |
| BL2 | Ekta problem solve korar age… | en→UNKNOWN | FALLBACK | Bengali apology | WRONG |
| RS1 | 12 apples… | en→UNKNOWN | NEURAL | "to the other she a total of hes…" | GIBBERISH |
| RS2 | roses/flowers logic | en→GENERAL | NEURAL | "of the same are the total…" | GIBBERISH |
| RS3 | three tasks two slots | en→UNKNOWN | FALLBACK | Bengali apology | WRONG |

**Score: 0/13 correct.** Only 5/13 reached neural inference; all neural outputs incoherent.

## 5. Tokenizer [VERIFIED earlier — PASS]
sp_bpe_8k (vocab 8000) is shared between training/inference; 0% UNK on multilingual battery. Not the failure cause.

## 6. Confirmed root causes (severity-ranked)

| # | Cause | Class | Evidence | Confidence |
|---|---|---|---|---|
| 1 | **Wrong model loaded** — legacy 2.47M overfit ckpt instead of Core-01 run3 | Checkpoint mismatch / config | server log line "Using default checkpoint path: checkpoints_medium"; malformed production designation JSON | HIGH |
| 2 | **Intent router bypasses neural net** — Bengali questions → IDENTITY canned; many → FALLBACK | Fallback handler problem / API bug | BN1/BN2/BN3, BL1/BL2/RS3, EN4 results | HIGH |
| 3 | **Intent classifier English-only** — Banglish detected as 'english' UNKNOWN | Prompt/routing bug | BL1/BL2 language='english' | HIGH |
| 4 | **Neural model itself incoherent** — 2L/128d model on 1,812 samples | Insufficient training / poor dataset | EN1-3, RS1-2 gibberish; val_loss 1.09 overfit | HIGH |
| 5 | **Fallback always Bengali** regardless of input language | Post-processing bug | BL/EN fallbacks return Bengali apology | HIGH |
| 6 | Core-01 run3 NOT wired into app at all | Integration gap | ml-service has no core01 loader; run3 ckpt sits unused locally/Drive | HIGH |

## 7. Unconfirmed hypotheses
- Whether /inference endpoint (non-orchestrated) is used anywhere in web app (likely /orchestrate only) — MEDIUM
- Whether history/memory augmentation harms prompts — not tested — LOW

## 8. What must NOT change
Run3/run4 ckpts, tokenizer, datasets, architecture, production routing without approval.

## 9. Repair sequence (proposal only — NOT executed)
1. **Stage 1:** Fix checkpoint selection — point production designation to verified Core-01 run3 (or add explicit model-path config) after compatibility test.
2. **Stage 2:** Fix routing — remove/limit deterministic handlers to true greetings only; make intent classifier multilingual; language-appropriate fallbacks.
3. **Stage 3:** Fixed multilingual eval benchmark on Core-01 (run3 baseline already exists).
4. **Stage 4:** Run4 training (prepared) then re-evaluate.
5. **Stage 5:** Implementation plan only after approval.

## 10. Final verdict
**MULTIPLE ROOT CAUSES** — primary: wrong checkpoint loaded (legacy 2.47M model) + fallback/routing bypassing neural inference + weak underlying model. Core-01 run3 exists and works but is not connected to the app.
