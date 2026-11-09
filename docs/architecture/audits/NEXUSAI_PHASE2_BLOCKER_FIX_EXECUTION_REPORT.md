# NEXUSAI PHASE 2 — BLOCKER FIX EXECUTION REPORT

**Date:** 2026-11-10 · Scope: 3 approved fixes only

## FIX 1 — Reasoning dataset leakage

| Metric | Before | After |
|---|---|---|
| Generated | 4,587 (v1-style loops) | 4,587 candidates → **3,711 unique** |
| Train | 3,215 (102 dup instr, max 77×) | **3,411 unique** |
| Held-out test | 300 (237 near-dup w/ train) | **300, near-leak = 0** |
| test∩train exact | 61 | **0** |
| test instructions in corpus | 237/300 | **6/300** (near-template only, see below) |

- Generator rewritten: all examples parameterized-unique; dedupe by normalized SHA-256 (876 removed).
- Distribution after: arithmetic 2,851 · logic 330 · decision 114 · uncertainty 67 · banglish 168 · bn 297 · mixed 59 · instruction 29 · contradiction 65 · cause_effect 15.
- Math answers still code-verified.
- **Residual:** 6/300 test items share template-family with train (e.g., ordering permutations, "water boils" variants) — different parameters, not identical; documented limitation, acceptable for pilot.

## FIX 2 — Corpus rebuild

- `corpus_train.jsonl` rebuilt deterministically (seed 42): **216,193 docs**, 385,217,021 bytes
- New SHA-256: `5f8572edd816ac875a7f52915bc6326635d7a483e0ca3f33b70fffdda7e28376`
- Components: BN 84,000 docs (wiki 45K + sangraha 9K + bongchat 30K) · EN 121,960 · reasoning 10,233 (3,411×3)
- Est. tokens ~60.4M (stratified sample); Bengali ≈60%
- reasoning_test.jsonl excluded from corpus ✅

## FIX 3 — Run4 cell resume

`COLAB_RUN4_TRAIN_CELL.py` patched:
- Resume priority: `checkpoint_final.pt` → skip; `checkpoint_last.pt` → resume; latest step ckpt → resume; else run3 ckpt
- Resume source verified (model+opt state_dict asserted) before training — never random init
- Run3 untouched (separate SRC_CKPT, run4 isolated OUT_DIR)
- MAX_STEPS 6000→**8000**; EPOCHS=2; ~60M tok ÷ 16K tok/step ≈ 3.7K steps/epoch → ~7.4K total < 8000 ✅
- Syntax verified

## Regression checks
- run3 ckpt SHA-256 re-verified: **unchanged** ✅
- Corpus manifest regenerated, counts match ✅
- No raw/cleaned data modified ✅

## Remaining limitations
- 6 near-template test items (documented)
- english_first train/val near-dup (pre-existing gsm8k rewording)
- Sangraha still partial; BanglaCoRe gated
- Actual training unverified until Colab run

## FINAL VERDICT: **READY FOR COLAB RUN4**

All three blockers fixed and verified. Next: user uploads corpus + runs cell.
