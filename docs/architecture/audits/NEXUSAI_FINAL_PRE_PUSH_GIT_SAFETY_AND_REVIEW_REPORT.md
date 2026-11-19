# NexusAI — Final Pre-Push Forensic Review & Git Safety Report

**Date:** 2026-11-19 · **Audit-only mission — zero modifications made.**

## 1. Executive summary
Code is verified and safe to commit. **However, two asset-level issues need your decision before push:** (a) three SFT checkpoints (core-02/03/04, ~253MB) are git-ignored and untracked — a clean clone would lose 3 of 5 registered models; (b) three ~166–174MB training ZIPs are untracked and would hard-fail a GitHub push if accidentally added.

## 2. Baseline Git state
- Branch `main` @ `2c475ad` = origin/main · **0 commits ahead/behind**
- 54 staged index-only deletions (approved cleanup) · 20 modified · 36 untracked
- No commit/push/reset performed during any mission

## 3. English semantic-wrongness guard — INVESTIGATED, CONFIRMED LIMITATION
**What:** `safety_guard.validate_neural_output` runs `language_mismatch` only when `expected_lang ∈ {bengali, banglish, mixed}`. For **English input there is no output-language/content validation** beyond markup/repetition/length — fluent-but-wrong English neural output passes as `NEURAL_MODEL`.
**Evidence (live):** eval prompt C1 ("Explain why learning from mistakes is important") → core-04 output `'কৃত্রিক বুদ্ধিমত্তা হলো মেশিন, a medical.'` (mixed gibberish) labeled `NEURAL_MODEL`; G1/G2 → off-topic English fragments labeled `NEURAL_MODEL`.
**Impact:** quality/provenance-honesty issue — `NEURAL_MODEL` is technically true (neural ran) but content can be wrong/irrelevant. Not a safety breach, not Bengali/Banglish affected (those are guarded). **Status: NEEDS USER DECISION** — proposed fix would require semantic relevance scoring (embedding similarity or self-consistency), a design change beyond safe scope. Documented, not implemented per instructions.

## 4. Changed-file classification (20 modified)
All 20 are **required source/test/config**: api (`app.ts`, `intelligence-engine.ts`, `routes/ai.ts`), web (`AuthContext.tsx`, `ChatInterface.tsx`, `MainContent.tsx`, `conversation-types.ts`, `globals.css`, `page.tsx`, `dev.mjs`), ml-service (`main.py`, `model_router.py`, `safety_guard.py`, `production_inference.py`), root configs (`package.json`, `vitest.config.ts`, `.env.example`, `.gitignore`), and test files. **No secrets, no generated artifacts, no unrelated user work mixed in.**

## 5. Secrets & security — VERIFIED SAFE
- `.env` present locally, untracked, unstaged — contains Neon URL + cookie secret; never printed.
- Diff scan: only test placeholders (`postgresql://*.invalid`, `shared-key`, `test-only` comments). No keys/tokens/passwords.
- `.env.example` has placeholders only.

## 6. ⚠ Asset-tracking findings (the two decision items)

| Asset | State | Consequence on clean clone |
|---|---|---|
| core-01 ckpt (107MB) | tracked via **Git LFS** (`.gitattributes`) | ✅ preserved |
| nexus-medium ckpt (30MB) | tracked | ✅ preserved |
| **core-02 ckpt (82MB)** | `*.pt` ignored, untracked | ❌ MISSING → registry marks unavailable |
| **core-03 ckpt (36MB)** | ignored, untracked | ❌ MISSING |
| **core-04 ckpt (135MB)** | ignored, untracked | ❌ MISSING — and >100MB so plain git can't take it anyway |
| tokenizer `sp_bpe_8k` | tracked | ✅ preserved |
| `corpus_train.jsonl` (~1.9GB) | `*.jsonl` ignored | training asset — not needed for inference; delivery ZIPs contain it |
| 3 export ZIPs ~166–174MB | untracked, **not ignored** | ⚠️ `git add .` would attempt push → **GitHub rejects >100MB files** |
| other export ZIPs | 3 tracked (small) | ✅ |

**Recommendation (needs approval):** add LFS patterns for `checkpoints_core0*_sft_*/checkpoint_final.pt` + `git add` them (mirrors core-01 approach) so all 5 cores survive cloning; keep large training ZIPs untracked or LFS them separately. Do NOT `git add .` blindly.

## 7. AI Brain integrity — VERIFIED (unchanged)
5 cores registered, all `available`, hash+tokenizer strict-load, params measured (8.8M/20.3M/8.8M/33.4M/2.5M), core-04 live-generate proven with SHA256 provenance, no external AI anywhere (VERIFIED last audit, no new deps since).

## 8. Regression (this session, actually executed)
- vitest **203/203** · python stabilization **44/44** · generation **13/13** · api+web tsc clean
- RAM available ~1.07GB — no build run (would OOM); typechecks sufficient

## 9. Environment limits
Host RAM ~1GB free → Next dev OOMs intermittently (environmental, retried OK); Neon write-path auth lifecycle remains BLOCKED (no isolated test DB).

## 10. Status summary
| Item | Status |
|---|---|
| Code changes safe to commit | VERIFIED SAFE |
| Secrets | VERIFIED SAFE |
| Tests | VERIFIED SAFE (all green) |
| SFT checkpoints on GitHub | **NEEDS USER DECISION** (untracked → clone loses core-02/03/04) |
| Large training ZIPs | **NEEDS USER DECISION** (push-blocker if added) |
| English guard gap | NEEDS USER DECISION (documented, not fixed) |
| Neon auth lifecycle | BLOCKED (infra) |

## Final verdict: **A. READY FOR USER COMMIT/PUSH APPROVAL** — with two explicit cautions:
1. Commit selectively — do NOT `git add .` (166MB+ ZIPs will fail push).
2. Decide whether core-02/03/04 checkpoints go to Git LFS before or after this push; without them a fresh clone runs degraded (core-01+medium only).
