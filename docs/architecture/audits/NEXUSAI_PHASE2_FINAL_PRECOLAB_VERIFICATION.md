# NEXUSAI PHASE 2 — FINAL PRE-COLAB VERIFICATION

**Date:** 2026-11-10 · READ-ONLY · Verdict: **CONDITIONALLY READY — FIXES REQUIRED**

## A. Bengali Corpus Accounting [VERIFIED]

| Component | Docs in corpus | Est. tokens (2K-stratified sample) |
|---|---|---|
| bangla_wikipedia_mit | 45,000 (of 168,962 cleaned) | 26.1M |
| sangraha_bengali | 9,000 (of 9,172) | 6.5M |
| bongchat_v1 | 30,000 (of 113,446) | 3.5M |
| english_first | 61,960 (all train) | 7.2M |
| tinystories | 60,000 (all) | 16.5M |
| reasoning_v1 (×3) | 9,645 | 0.6M |
| **TOTAL** | **215,605** | **~60.4M** |

- Bengali-side tokens ≈ **36.1M (60%)**, English ≈ 23.7M, reasoning ≈ 0.6M.
- Reduction 133.9M→36.1M BN tokens = **intentional even-stride sampling** (seed 42) — not loss; remainder available for future runs.
- Earlier "56.9M" estimate was low; stratified sample gives **~60.4M**.

## B. Reasoning Dataset — ⚠️ ISSUES FOUND

| Check | Result |
|---|---|
| Train/test counts | 3,215 / 300 ✅ |
| Category/lang dist | as reported ✅ |
| Math answers | code-verified at generation ✅ |
| **Exact dup instructions in train** | **102 unique dups, max 77×** ❌ (template loops) |
| **test ∩ train exact** | **61** ❌ |
| **test ∩ train near-dup (80-char)** | **237/300** ❌ |
| Test leakage into corpus | **237/300 test instructions present** ❌ |

Root cause: test examples reuse the same templates as train → held-out is not truly held out.

## C. English Expansion [VERIFIED]
- TinyStories `roneneldan/TinyStories`, HF license tag `mit`, 60K/58.9MB streamed, all 60K in corpus ✅
- Used as LM text only (category `english_simple`), not instruction data ✅
- Attribution: MIT — include in model card

## D. Leakage Summary
| Pair | Overlap | Severity |
|---|---|---|
| reasoning_test ↔ corpus_train | 237/300 | **HIGH — fix before training** |
| reasoning_test ↔ reasoning_train | 237/300 near | HIGH |
| english_val ↔ english_train | near-dup gsm8k rewording (e.g. val[0] vs train[53467] same problem different formatting) | MEDIUM — pre-existing, document |
| cleaned_bangla cross-file | 0 exact | PASS |

## E. Run4 Cell Verification — ⚠️ 2 ISSUES

| Check | Status |
|---|---|
| run3 path/hash guard | ✅ asserts step==1341, strict keys |
| Resume absolute path | ✅ works (os.path.join handles abs) |
| Overwrite protection | ✅ asserts empty run4 dir |
| Driver args | ✅ corrected |
| **Resume-after-interruption** | ❌ `assert not glob(ckpt*)` blocks rerun once ckpts exist — session resume impossible without editing |
| **Step budget** | ⚠️ corpus ~60M tok ÷ 16K tok/step ≈ 3.8K steps/epoch; EPOCHS=2 needs ~7.6K but MAX_STEPS=6000 truncates mid-epoch-2 |
| Val leakage | ✅ val-fraction holdout, reasoning_test not in corpus inputs (but see D) |

## F. Eval plan
Same prompts/decoding as run3 (`eval_core01_run3.py` pattern) — comparable. Held-out reasoning_test currently compromised → must regenerate distinct test templates.

## REQUIRED FIXES BEFORE COLAB
1. **Reasoning dataset:** dedupe train (102 dup instr); regenerate test with disjoint templates; rebuild corpus without test leakage.
2. **Cell:** allow resume (remove/soften empty-dir assert → resume from latest run4 ckpt); set MAX_STEPS≈8000 or EPOCHS=1+resume sessions.
3. Document english_first near-dup limitation (pre-existing, acceptable for pilot).

## Verdict: **CONDITIONALLY READY — FIXES REQUIRED**

Data assets are good; leakage + resume issues must be fixed first. Estimated fix time: small (generator patch + corpus rebuild ~10 min).

**STOP — awaiting owner decision: fix now or proceed as-is?**


---

## UPDATE 2026-11-10 — BLOCKERS FIXED

All 3 blockers resolved (see NEXUSAI_PHASE2_BLOCKER_FIX_EXECUTION_REPORT.md):
- Reasoning leakage: 237→6 near-template residual, 0 exact, 0 near-leak in split
- Corpus rebuilt: 216,193 docs, sha256 `5f8572ed…28376`
- Cell resume-safe, MAX_STEPS=8000

**REVISED VERDICT: READY FOR COLAB RUN4**
