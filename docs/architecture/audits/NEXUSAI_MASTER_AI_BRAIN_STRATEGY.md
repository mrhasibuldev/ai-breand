# NEXUSAI — MASTER AI BRAIN DEVELOPMENT & TRAINING STRATEGY

**Type:** READ-ONLY forensic audit + roadmap. No code/dataset/checkpoint changes.
**Evidence labels:** [VERIFIED] repo/Drive-verified · [ESTIMATED] derived · [REC] recommendation · [UNKNOWN] needs testing

---

## PHASE A — DATASET INVENTORY [VERIFIED]

| Dataset | Path | Size | Records | Tokens | Used in training? | License |
|---|---|---|---|---|---|---|
| english_first train | data/english_first/english_train.json | 26MB | 61,960 docs | 7.21M | ✅ runs 1–3 | mixed (see below) |
| english_first val/test | same dir | ~0.8MB | 958+958 | 215K | eval only | same |
| dolly-15k cleaned | collected/cleaned/dolly/ | 12.8MB | ~14K | (in english_first) | ✅ | Apache-2.0 |
| gsm8k cleaned | collected/cleaned/gsm8k/ | 5MB | 8,792 | (in english_first) | ✅ | MIT |
| corpus_english/expanded | experimental/phase7,9,9_2 | ~22MB | ~82K lines | (in english_first) | ✅ | internal |
| **alpaca_data.json** | collected/small_datasets/ | 23MB | **52,002** | ~8–10M est | ❌ **NOT trained** | Apache-2.0 |
| Bengali phase9_1 cleaned | experimental/phase9_1/cleaned/ | 222KB | 590+151 | <100K | ❌ | internal |
| Bengali phase9_2 corpus | corpus/bengali.txt | 172KB | 742 lines | ~50K | ❌ | internal |
| love_emotion_* | data/staging/love_emotion/ | ~60KB | 9+20×3 | tiny | ❌ (11 en docs in english_first) | internal |
| Bengali Wikipedia etc. | — | — | — | — | ❌ not yet collected | see Bangla report |

**english_first composition [VERIFIED]:** 223,521 read → 5,129 empty → 114,021 short-filtered → 12 non-English → 45,623 dedup-removed → **63,876 docs / 7,428,739 tokens**. Seed 42, zero overlap verified.

**Critical finding:** alpaca (52K instruction pairs, Apache-2.0) sits unused — largest ready instruction dataset we own.

## PHASE B — LANGUAGE STRATEGY

- **Tokenizer:** sp_bpe_8k trained primarily on English+mixed corpus. Bengali script coverage UNKNOWN [UNKNOWN — test needed: encode Bengali text, measure UNK rate]. If UNK-heavy → retrain tokenizer on multilingual corpus (own tokenizer, allowed).
- **Banglish:** zero dedicated data [VERIFIED]. Must self-create (romanized BN patterns) — no quality public dataset found.
- **Strategy [REC]:** keep 8K vocab for now; measure Bengali UNK rate first; retrain tokenizer only if evidence demands.

## PHASE C — REASONING & DECISION-MAKING

Required dataset types per capability:

| Capability | Dataset type | Example structure | Training objective |
|---|---|---|---|
| Logic | rule-based QA (synthetic, own-generated rules OK — not AI-generated) | premise→conclusion | LM on structured text |
| Math | gsm8k (have) + more math corpora | problem→step-by-step→answer | LM; CoT-style formatting helps |
| Decision | Situation→Info→Constraints→Alternatives→Reasoning→Decision→Explanation | structured JSONL→text | LM on formatted examples |
| Uncertainty | "I don't know"/abstention examples | unanswerable Q→honest response | LM |
| Emotion | love_emotion + respectful-dialogue corpus | context→empathetic reply | LM/SFT |

**Phases distinction [REC]:** pretraining (raw text LM) ≠ instruction tuning (prompt→response) ≠ reasoning training (structured CoT). Our driver does LM only — instruction format must be embedded as plain text patterns.

## PHASE D — TRAINING COMPLETENESS [VERIFIED + ANALYSIS]

- Token exposure: 7.43M tokens × 3 epochs ≈ **22.3M tokens seen**; model 8.8M params → ~2.5 tokens/param — **severely undertrained** [ESTIMATED: Chinchilla-optimal ≈ 20 tokens/param → need ~175M tokens for this size]
- Val loss 4.217 still high → underfitting, not overfitting (train≈val gap small)
- Effective batch 32, lr 3e-4, warmup 100, AdamW — config reasonable
n- Context 512, packed sequences — efficient
- **Conclusion:** loss is high because **data quantity is the binding constraint**, not architecture or hyperparameters. More epochs on same 7.4M tokens → diminishing returns/overfit risk.

## PHASE E — DATASET EXPANSION [REC]

| Target | Source | Est. tokens |
|---|---|---|
| English →100M | FineWeb sample (verified earlier), alpaca (unused!), more cleaned corpora | ~100M |
| Bengali →10M+ | Bangla Wikipedia MIT dump (~995MB→~80M tokens potential), Sangraha CC-BY | 10–80M |
| Banglish | self-created corpus (~50–200K sentences target) | ~5M |
| Reasoning/decision | BanglaCoRe-5000, PROSHNO (NC?), self-authored structured sets | ~1M |
| Instruction | alpaca + BongChat MIT | ~15M |

For 8.8M model: **~175M tokens Chinchilla-optimal** — reachable with English 100M + Bengali 30M + instruction 15M ≈ 145M (close enough for pilot).

## PHASE F — CURRICULUM [REC]

1. **S1 English foundation** — continue english_first + expanded English (target 50M+) — *can merge with S2*
2. **S2 Multilingual** — add Bengali corpus, measure UNK
3. **S3 Knowledge/math** — gsm8k upweight + math corpus
4. **S4 Instruction tuning** — alpaca/BongChat formatted as text
5. **S5 Reasoning/decision** — structured datasets
6. **S6 Eval gates** — decision eval + per-language suites

Combine S1+S2 (single multilingual corpus, simpler); keep S4/S5 as separate runs for clean attribution.

## PHASE G — HARDWARE [VERIFIED + ESTIMATED]

| Option | Cost | Notes |
|---|---|---|
| Colab T4 free | $0 | working now; ~15GB VRAM; session limits |
| Kaggle P100 | $0 | 30h/week GPU quota |
| Colab Pro | ~$10/mo | more T4/A100 time |
| Local CPU | $0 | inference only (8.8M model OK) |

**Ownership preserved regardless of platform** — checkpoints stay ours on Drive.

## PHASE H — EVALUATION FRAMEWORK [REC]

Per-language suites: perplexity on held-out split + 20-prompt generation rubric (already built: decision eval cell, local eval script). Acceptance: val loss <3.5, Bengali UNK<5%, decision-eval >70%, math gsm8k-subset >40%.

## PHASE I — ROADMAP

1. ⬜ Download run3 ckpt → local eval (Phase 3 quality baseline)
2. ⬜ Measure Bengali tokenizer UNK rate
3. ⬜ Approve Bangla Batch-1 (Wikipedia MIT + Sangraha + BanglaCoRe + BongChat)
4. ⬜ Build multilingual corpus v2 (EN+BN+Banglish+instruction)
5. ⬜ Run 4: continued pretraining on expanded corpus (Colab T4)
6. ⬜ Eval gates → iterate

## RISKS
- NC-license datasets → pending commercial decision
- Banglish scarcity → self-creation effort
- Colab quota → Kaggle fallback
- Tokenizer Bengali coverage → measure first

**STATUS: read-only audit complete. Awaiting approval for: ckpt download, Bangla batch-1 collection, tokenizer measurement.**
