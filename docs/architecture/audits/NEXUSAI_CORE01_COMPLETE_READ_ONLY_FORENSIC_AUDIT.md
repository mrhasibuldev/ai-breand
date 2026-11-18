# NEXUSAI CORE-01 — COMPLETE READ-ONLY FORENSIC AUDIT

**Date:** 2026-11-10 · Investigation only · Nothing modified

## A. Executive summary
NexusAI's pipeline is real and verified: own Transformer (Core-01 run3, 8.84M params) actively generates responses through genuine forward passes; routing/language/history bugs fixed today; zero external AI dependency. **But the model is undertrained** — neural-only eval: 22/22 routing PASS, 22/22 quality FAIL. Run4 (multilingual corpus) is technically ready; only Colab execution + approval remain.

## B. Verified completed work
| Claim | Evidence | Status |
|---|---|---|
| Core-01 run3 active | `model_registry.py` MODEL_DEFS + live /orchestrate traces `route=neural:nexus-core-01` | VERIFIED |
| Real forward pass | forward() instrumented: 25 calls/25 tokens | VERIFIED |
| Neural-only mode | `neural_only:true` → 22/22 neural, zero canned | VERIFIED |
| History fix | `_normalize_history` accepts `history`+`conversation_history`; 13/13 unit tests | VERIFIED (unit); end-to-end context-use NOT VERIFIED |
| Backup integrity | manifest re-verified: 5 source copies hash-match; 16 artifacts hash-recorded | VERIFIED |
| No external AI | repo-wide grep: no provider calls | VERIFIED |

## C. Unresolved problems
| # | Issue | Severity | Root cause |
|---|---|---|---|
| 1 | Neural output gibberish | **P0** | undertrained (english_first only, 7.4M tok) → Run4 needed |
| 2 | Bengali/Banglish output = English | P0 | no Bengali training yet → Run4 |
| 3 | Context not exploited by model | P1 | history now reaches prompt; model too weak to use it |
| 4 | Medium fallback wrapper minimal | P2 | emergency-only path |
| 5 | Bengali-digit math → neural | P3 | tool regex EN digits only |
| 6 | No streaming generation | P3 | generate() non-streaming |

## D. Model forensic findings
- **Active:** `checkpoints_core01_run3/checkpoint_final.pt` — sha256 `ad515cad…7830`, strict load PASS, status PRETRAINING_COMPLETED, 8,842,560 params, 6L/d256/8H/ff1024/ctx512, sp_bpe_8k vocab 8000
- **Fallback:** `checkpoints_medium/final_model.pt` — sha256 `4f592af9…`, custom MediumTransformer (transformer_blocks.* keys — **NOT nn.TransformerEncoder**; earlier "TransformerEncoder" claim is WRONG), config embedded: d128/2L/2H/ff512/vocab8000/ctx128, epoch=2 (3 epochs), train_loss 1.00, val_loss 1.09
- **Provenance:** trained by `training/train_phase1_medium.py` on Phase-10 dataset (train_phase10.py does NOT exist — claim that ckpt came from phase10 script is DISPROVEN; phase1 script trained ON phase10 data)
- **Param discrepancy explained:** `medium_transformer.py` class defaults are d256/6L/8H (line 23,226) but production ckpt used d128/2L — same class, smaller config. The "~10M target" was never trained.
- **Loss figures resolved:** "val 6.01" does NOT match this ckpt (val_loss=1.09). "Perplexity ~2.83" IS consistent: e^1.09≈2.97 ≈ e^1.00≈2.72 range — medium model memorized 1,449 samples (loss ~1.0 = severe overfit → gibberish).

## E. Neural generation evaluation (independently reproduced)
- Neural-only suite: **22 executed / 0 pass / 22 fail / 0 blocked** — all `route=neural:nexus-core-01`, all gibberish/irrelevant/wrong-language
- Representative: "Why does the sky appear blue?" → "If you have a good option with a pair of watermble…"; "তুমি কে?" → English fragment (language mismatch)
- Conclusion: generation is genuine but quality gate FAILED — needs Run4+

## F. Run4 readiness: **READY WITH CONDITIONS**
- Corpus verified: 216,193 docs / 385MB / sha256 `5f8572ed…` / Bengali chars 47.1% / EN-leaning by doc count (~56%)
- Cell resume-safe, bundle built, parent=run3 verified, tokenizer compatible
- Conditions: (1) user must run Colab + upload corpus, (2) explicit training approval, (3) post-train eval vs run3 baseline

## G. Dataset findings (Phase-10, the 1,812-sample set)
- train.json 1,449 / val.json 181 / test.json 182 = **1,812 total** ✅ claim verified
- Language (train, char-ratio method): EN-dominant 797 (55%), BN-dominant 606 (42%), mixed 46 (3%), empty 0, unique 1,449 (0 dups)
- Content: pre-tokenized raw text, 654 question-marked; NOT instruction pairs — explains why medium can't converse
- Prior "math/love percentages" inconsistent across reports — NOT VERIFIED as single canonical figures

## H. Memory & retrieval
- `simple_retrieval`/`rag_system`: code exists, usage commented out → DISABLED, cannot answer
- DB tables exist: `nexus.memory_records`, `consent_records`, `conversations`, `messages` (332 msgs audited)
- Consent/account isolation: schema supports it; runtime path untested → PARTIALLY VERIFIED

## I. Multi-model architecture status
- IMPLEMENTED+VERIFIED: registry (validation/hash/strict-load), router (lang/intent/model/tool/fallback), provenance trace, lazy loading
- PARTIAL: medium fallback generator (minimal wrapper)
- PLANNING ONLY: specialists, self-correction, streaming, public API

## J. Security & repo health
- Auth: `optionalAuthMiddleware` on /ai/chat; conversation_id scoping exists
- Secrets: none exposed in reports; .env not printed
- Git: uncommitted changes present (today's work) — not committed per policy
- Risk: ml-service binds 127.0.0.1:8000 (local only) ✅

## K. Prioritized action plan
- **P0:** Run4 training (only path to quality) — needs Colab + approval
- **P1:** post-Run4 eval + promotion decision; Bengali-digit math tool
- **P2:** scale data toward ~150M tokens; SFT/instruction stage
- **P3:** memory retrieval path test; streaming generation
- **P4:** specialists only if foundation eval demands
- **P5:** public API (rate limits, keys) after capability proven

## L. Approval requirements
1. Run4 Colab execution (corpus upload + cell run)
2. Any new training run
3. Git commit/push
4. DB schema changes
5. Specialist model creation

## FINAL ANSWER
**Is Core-01 ready for next phase? YES for Run4 training** — pipeline, checkpoint, tokenizer, corpus, resume-safe cell all verified. **NO for production conversational use** — model quality fails every neural test until Run4+ produces a better checkpoint. Nothing else blocks training except user's Colab run + approval.
