# NEXUSAI — RUN4 BENGALI CORPUS & TRAINING READINESS REPORT

**Date:** 2026-11-09 · READ-ONLY planning · Labels: VERIFIED / ESTIMATED / HOLD / BLOCKED

## EXECUTIVE SUMMARY

Run3 verified working but weak (LM-only, English style, no semantics). Bengali data downloaded and token-audited (~148M tokens) but **not cleaned**. Verdict: **CONDITIONALLY READY — BLOCKERS REMAIN** (cleaning, disk for outputs, BanglaCoRe gated, English expansion needed).

## 1. VERIFIED DATASET INVENTORY

### Bengali (raw_bangla — actual token counts, sp_bpe_8k)

| File | Records | Tokens | Duplicates | Malformed | Script mix |
|---|---|---|---|---|---|
| `raw_bangla/bangla_wikipedia_mit/` | 171,674 | **115.3M** | 0 | 0 | 80% bn / 20% mixed |
| `raw_bangla/sangraha_bengali/` (PARTIAL) | 9,206 | **7.7M** | 0 | 0 | 78% bn / 22% mixed |
| `raw_bangla/bongchat_v1/` | 150,000 | **25.4M** | 1 | 0 | ~100% mixed (BN+EN instructions) |
| `raw_bangla/bangla_core_5000/` | 0 | — | — | — | **GATED 401** |

### English (existing)
- `english_first/`: 63,876 docs / **7.43M tokens** (train 61,960) [VERIFIED]
- Unused: `collected/small_datasets/alpaca_data.json` 52,002 pairs — **EXCLUDED** (GPT-3.5-generated, independence violation)
- `collected/cleaned/dolly` + `gsm8k` — already inside english_first

### Local Bengali (provenance-verified, NOT yet in corpus)
- `phase9_1/cleaned/bengali_chat_conv` (590) MIT + `bengali_sft_v1` (151) Apache-2.0
- `data/staging/love_emotion/` (69 self-authored, license "nexusai")
- `phase9_2/corpus/bengali.txt` — **HOLD** (provenance unclear)

## 2. LICENSE AUDIT

| Source | License | Commercial | Status |
|---|---|---|---|
| bangla-wikipedia | HF tag `mit`; content = Wikipedia CC BY-SA 3.0 | ⚠️ attribution+SA | APPROVED w/ attribution |
| sangraha | `cc-by-4.0` | ✅ | APPROVED |
| bongchat_v1 | `mit` | ✅ | APPROVED |
| bangla_core_5000 | gated | — | **BLOCKED — needs HF login** |
| alpaca | "Apache-2.0" metadata but GPT-generated | — | **EXCLUDED** |
| BanglaRQA/PROSHNO/bengalichat | CC BY-NC | ❌ | EXCLUDED |

## 3. TOKENIZER ASSESSMENT [VERIFIED]
8K vocab already multilingual: 2,819 BN pieces, 0% UNK on EN/BN/Banglish samples, ~1 tok/BN word. Numbers/punctuation fine. **Sufficient for Run4 — no retrain needed.**

## 4. DISK & COMPUTE
- C: free **6.1GB** (improved) — enough for cleaned corpus (~500MB est) + bundle (~10MB) + ckpts
- GPU: Colab T4 proven (3 runs). Run4 on ~150M tokens ≈ 4-5× Run3 cost → multi-session resume required

## 5. PROPOSED RUN4 DATA MIXTURE (targets, not verified contents)

| Component | Tokens | Source | Eligibility |
|---|---|---|---|
| Bengali general | ~50M | wikipedia+saangraha cleaned | ✅ |
| Banglish/instruction | ~20M | bongchat cleaned + local chat_conv | ✅ |
| English foundation | ~30M | english_first + dolly/gsm8k re-upweight | ✅ |
| Math | ~5M | gsm8k + own arithmetic templates | ⚠️ templates=self-authored OK |
| Reasoning/decision | ~1M | **GAP — no approved dataset** | needs creation |
| Love/emotion | ~0.1M | local love_emotion (69) | ✅ tiny |

**Honest gaps:** reasoning/decision/abstention data ≈ 0 — must be human-authored or rule-generated (allowed: not AI-generated). Math beyond gsm8k thin.

## 6. CLEANING PLAN (proposed, not implemented)
Deterministic pipeline `clean_bangla_batch1.py` exists: SHA256 dedup, min-length, BN-script ratio ≥0.30 or Banglish, JSONL out with license metadata. Needed additions: HTML strip, nav-boilerplate filter, near-dedup (MinHash), repeated-paragraph detection, split seed-42.

## 7. RUN4 CONFIG (proposal)
- Continue from run3 ckpt, same arch (8.8M), ctx 512
- Corpus: ~100M tokens mixed (BN-heavy ~60%)
- batch 32, accum 4, lr 3e-4 w/ warmup, ~3-4 epochs → est. 8-12k steps → multiple Colab sessions w/ resume
- Save ckpt every 100 steps + epoch ends; Drive backup each session

## 8. ACCEPTANCE CRITERIA (proposed targets)
- Bengali prompt → Bengali output ≥80% of tests
- English val_loss < 4.0; Bengali held-out ppl measurable
- Arithmetic: ≥50% on 2-digit ops
- Repetition/gibberish rate <10%
- CPU: load <2s, ≥30 tok/s, <500MB RAM
- No regression vs run3 on English eval

## 9. RISKS
- Sangraha only partial (9K docs) — may resume stream later
- BanglaCoRe gated → reasoning data gap remains
- Wiki SA license attribution tracking needed
- 100M-token run exceeds single Colab session → resume discipline critical

## FINAL VERDICT: **CONDITIONALLY READY — BLOCKERS REMAIN**

Blockers: (1) cleaning not run, (2) reasoning/decision dataset absent, (3) BanglaCoRe gated, (4) English corpus needs expansion beyond 7.4M.

## NEXT STEPS NEEDING APPROVAL
1. Run `clean_bangla_batch1.py` (+ upgrades) → produce cleaned_bangla
2. Author small reasoning/decision/abstention dataset (human-written, ~1-2K examples)
3. Approve Run4 corpus build + Colab training plan
4. Optional: HF login for BanglaCoRe; resume sangraha stream
