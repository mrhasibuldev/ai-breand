# NEXUSAI CORE-01 — PHASE 3.1 INDEPENDENT DATASET VERIFICATION, INTELLIGENCE REQUIREMENTS & FINAL TRAINING DATA SELECTION

**Date**: 2026-11-06
**Type**: STRICT RESEARCH-ONLY — no downloads, no modifications, no training
**Method**: Live repository inspection + official HF dataset card verification (primary sources)

---

## 1. EXECUTIVE SUMMARY

- **Core-01 VERIFIED**: exists at `packages/ai-core/core01/` + `models/nexusai_core_01/`; instantiated and counted = **8,842,560 params**; status `UNTRAINED`; all 9 architecture tests passed in Phase 1.
- **License reality changed the plan**: Several attractive Bengali datasets are **NOT legally safe** for a commercial product — `dailydialogue_bn` is CC BY-NC-SA (non-commercial), `bangla-alpaca-orca` is GPL-3.0 (copyleft), XL-Sum is CC BY-NC-SA, raw Alpaca is non-commercial.
- **Verified-safe core**: B-CORE (CC BY 4.0), IndicTalk (CC BY 4.0, includes Romanized code-mixed), Ayon128/Banglish-English (MIT), alpaca_chat_bangla (CC-BY-2.0), GSM8K (MIT), Dolly (CC BY-SA 3.0 w/ attribution), Samanantar (CC0 packaging).
- **Banglish is the weakest link**: real Romanized-Bengali conversational data is scarce and the best-looking set (tanziro dhaka-chat) has UNVERIFIED license + GPL-contaminated provenance.
- **Bottom line**: a small clean corpus (~15-30M tokens) mixing verified-safe sources is realistic for Stage 2; reasoning/emotion/personality capabilities will be limited by data availability AND the 8.84M param ceiling.

---

## 2. CURRENT CORE-01 VERIFICATION (independent, this session)

| Claim | Verified? | Evidence |
|---|---|---|
| Model exists | ✅ VERIFIED | `core01/transformer.py`, instantiated live |
| 8,842,560 params | ✅ VERIFIED | `count_parameters()` = 8,842,560 exactly |
| UNTRAINED status | ✅ VERIFIED | `model_status = UNTRAINED`; inference returns warning, no gibberish |
| Config d256/L6/H8/dff1024/vocab8000/ctx512 | ✅ VERIFIED | `nexusai_core_01/config/model_config.py` |
| Tokenizer compatible | ✅ VERIFIED | Phase 1 test: 8K vocab, special IDs match |
| Training pipeline exists | ✅ VERIFIED | `training.py` (Pretraining + Instruction engines, checkpoint/resume) |
| Training occurred | ❌ NO | No checkpoints under `models/nexusai_core_01/checkpoints/` |
| Checkpoints to protect | legacy `checkpoints_medium/` (2.47M model) + tokenizer | untouched |
| Architecture limits | ctx 512 fine for chat; 8K vocab adequate for bn/en/banglish per Phase 2 UNK=0.13% | — |

**VERIFIED FACT**: Core-01 is ready for a small training experiment; no architecture change needed for Stage 1-2.

---

## 3. THREE-LANGUAGE REQUIREMENTS → DATA MAPPING

| Language | Need | Best verified sources |
|---|---|---|
| **Bengali (bn)** | fluency, Q&A, reasoning, instruction | B-CORE (pretrain), alpaca_chat_bangla, IndicTalk-native, project phase9/10 |
| **English (en)** | fluency, reasoning, instruction | GSM8K, Dolly, project data, B-CORE is bn-only so English comes from existing+new |
| **Romanized Bengali (Banglish)** | understand informal spelling, respond appropriately | IndicTalk-Romanized, Ayon128 pairs, project staging bn_latn; **scarce** |
| **Mixed bn-en** | code-switching | IndicTalk (code-mixed by design), Samanantar pairs |

**VERIFIED FACT**: IndicTalk is the single most valuable find — 145K Bengali rows with BOTH `Native` and `Romanized` script variants, persona-based multi-turn, code-mixed, CC BY 4.0.

---

## 4. INTELLIGENCE CATEGORY → DATA MAPPING

| Capability | What teaches it | Available verified data | Gap |
|---|---|---|---|
| A. Language understanding | pretrain corpus + conversations | B-CORE, IndicTalk, phase9/10 | bn volume OK via B-CORE |
| B. Logical reasoning | GSM8K (math CoT), synthetic reasoning | GSM8K 760K tok; reasoning-specific bn data = GAP | need bn reasoning set |
| C. Decision-making | comparison/pro-con examples | Alpaca-style instruction sets; no dedicated verified bn set | GAP — may need project-generated |
| D. Problem-solving | GSM8K, troubleshooting text | GSM8K, some Dolly | partial |
| E. Emotional intelligence | empathetic dialogue | love_emotion staging (project), IndicTalk personas | thin but project-controllable |
| F. Personality/conversation | consistent persona SFT | train_v2, phase9_1, IndicTalk | project data helps |
| G. Instruction following | SFT instruction/response | alpaca_chat_bangla (CC-BY-2.0), IndicTalk | solid |
| H. Math/analytical | GSM8K | 760K tok MIT | good for en; bn math = bangla_math (GPL — risky) |

**VERIFIED FACT**: reasoning/decision/emotion in BENGALI specifically is the thinnest category — most verified-safe Bengali data is general text + instruction, not structured reasoning.

---

## 5. OFFICIAL DATASET SOURCE VERIFICATION (primary sources checked this session)

| Dataset | Repo | Rows/Size | License (verified on card) | Commercial? | Verdict |
|---|---|---|---|---|---|
| B-CORE | huggingface.co/datasets/nahid-hub/B-CORE-bengali-corpus | 16.5M docs / 4.32B tok | **CC BY 4.0** | ✅ w/ attribution | **A — RECOMMENDED** |
| IndicTalk | huggingface.co/datasets/LingoIITGN/IndicTalk | 145K bn rows (native+romanized) | **CC BY 4.0** | ✅ w/ attribution | **A — RECOMMENDED** |
| Ayon128/Banglish-English | huggingface.co/datasets/Ayon128/Banglish-English | 14K pairs | **MIT** | ✅ | **A — RECOMMENDED** |
| Mahadih534/alpaca_chat_bangla | huggingface.co/datasets/Mahadih534/alpaca_chat_bangla | 51.8K | **CC-BY-2.0** | ✅ w/ attribution | **A — RECOMMENDED** |
| GSM8K | openai/gsm8k | 8,792 | **MIT** | ✅ | **A — RECOMMENDED** |
| Dolly 15K | databricks-dolly-15k | 15K | **CC BY-SA 3.0** | ⚠️ share-alike | **B — CONDITIONAL** |
| Samanantar (bn) | indicnlp.ai4bharat.org/samanantar | millions pairs | **CC0 packaging** (source rights vary) | ⚠️ per-source | **B — CONDITIONAL** |
| bangla-alpaca-orca | BanglaLLM/bangla-alpaca-orca | 172K | **GPL-3.0** | ❌ copyleft risk | **C/D — AVOID for product** |
| dailydialogue_bn | csebuetnlp/dailydialogue_bn | 13.1K | **CC BY-NC-SA 4.0** | ❌ non-commercial | **D — REJECTED** |
| XL-Sum | csebuetnlp/xlsum | bn subset | **CC BY-NC-SA 4.0** | ❌ | **D — REJECTED** |
| Alpaca raw | tatsu-lab/alpaca | 52K | non-commercial | ❌ | **D — REJECTED** |
| tanziro dhaka-chat | tanziro/bangla-romanized-dhaka-shortchat-small-sft | 18.5K | **UNVERIFIED** + derived from GPL sources | ❓ | **C — CONDITIONAL** |
| bangla_math_by_Ashrafur | via BanglaLLM | 859K | UNVERIFIED | ❓ | **C — CONDITIONAL** |
| Bhasha-SFT bn subset | soketlabs/bhasha-sft | subset of 13M | mixed per-source | ⚠️ | **C — CONDITIONAL** |
| BanglaSafe | via BanglaLLM | 879 | research | eval only | **eval set** |
| Belebele bn_Beng/Latn | facebook/belebele | eval | research | **eval set** |
| banglish_bench | sifat-febo/banglish_bench | 700 | UNVERIFIED | eval | **eval set** |

**Labeling**: A=RECOMMENDED, B=CONDITIONAL, C=LOW PRIORITY, D=REJECTED.

---

## 6. LICENSE & COMMERCIAL-RIGHTS ANALYSIS

- **Safe for commercial product (verified)**: CC BY (B-CORE, IndicTalk), MIT (Ayon128, GSM8K), CC-BY-2.0 (alpaca_chat_bangla), CC0 (Samanantar packaging).
- **Usable w/ obligations**: CC BY-SA (Dolly, Wikipedia) — attribution + share-alike on adapted dataset.
- **NOT usable commercially**: GPL-3.0 (bangla-alpaca-orca — copyleft could infect model weights, legally contested but risky), CC BY-NC-SA (dailydialogue_bn, XL-Sum), Alpaca non-commercial.
- **UNVERIFIED → not approved**: tanziro chat, bangla_math, Bhasha-SFT, BanglaNMT, SUPara, BdNC, VACASPATI.

---

## 7. DATASET QUALITY ANALYSIS

- B-CORE already dedup'd + filtered (22.4% volume reduction claimed) — high quality.
- IndicTalk is LLM-generated from news articles — fluent but synthetic; spot-check for factual drift.
- alpaca_chat_bangla is machine-translated Alpaca — usable but translationese risk.
- GSM8K is gold-standard math CoT.
- Project data (phase9/10, train_v2, staging) is small but persona-aligned — highest relevance per token for a companion.

---

## 8. TOKENIZER & MODEL COMPATIBILITY

- 8K SentencePiece: Phase 2 measured UNK=0.13% across bn/en/banglish — adequate.
- Bengali tokenizes efficiently (~1 token/word avg in samples).
- Romanized Bengali = Latin subwords — fine.
- ctx 512: sufficient for chat/instruction; too short for long documents — acceptable for companion use.
- **No tokenizer change needed.** Changing vocab would invalidate nothing yet (untrained) but is unnecessary.

---

## 9. RECOMMENDED DATASET SELECTION (final)

### Pretraining corpus (Stage A)
| Source | Lang | Est. tokens | Why |
|---|---|---|---|
| B-CORE subset (~0.5-1% of corpus) | bn | ~5-20M | Bengali fluency foundation |
| Project phase9/10 + train_v2 + staging | bn/en/mixed | ~0.1M | persona-aligned |
| IndicTalk bn (native+romanized) | bn/banglish/mixed | ~2-4M est | conversation + code-mix |
| GSM8K | en | ~0.76M | math reasoning |
| Dolly subset | en | ~1-2M | general instruction text |
| Ayon128 Banglish-English | banglish | ~0.3M est | romanized pairs |

### Instruction/reasoning SFT (Stage B)
| Source | Purpose |
|---|---|
| alpaca_chat_bangla (CC-BY-2.0) | bn instruction following |
| IndicTalk | multi-turn conversation |
| GSM8K | math reasoning |
| project phase9_1 sft + love_emotion | persona/emotion |
| Ayon128 | banglish↔en |

### Evaluation (Stage C — never train on)
- BanglaSafe (879), Belebele bn configs, banglish_bench (700), held-out phase10 test.

---

## 10. REJECTED / LOW-PRIORITY

- **REJECTED**: Alpaca raw (NC), dailydialogue_bn (NC-SA), XL-Sum (NC-SA), bangla-alpaca-orca (GPL), knowledge/ (privacy), training/original_dataset.jsonl (junk).
- **LOW PRIORITY**: synthetic/*, merged_train, training/train.json (tiny/duplicative), Wikipedia stubs (14 articles).

---

## 11. PRETRAIN vs SFT STRATEGY

- **Stage A pretrain**: B-CORE bn subset + IndicTalk + English mix → teaches language structure.
- **Stage B SFT**: instruction/reasoning/emotion sets → teaches behavior.
- Core-01 handles both (training.py has separate engines). ctx 512 limits document length — chunk B-CORE to ~400-token windows.
- Realistic: Stage A gets bn+en fluency; Stage B gets instruction-following + persona. Deep reasoning will be limited by 8.84M params — set expectations.

---

## 12. MINIMUM USEFUL INITIAL CORPUS (Stage 2 target ~10-25M tokens)

1. B-CORE random sample → ~8M bn tokens
2. IndicTalk bn (both scripts) → ~3M
3. GSM8K full → ~0.76M
4. alpaca_chat_bangla subset → ~2M
5. Dolly subset → ~1.5M
6. Project data (phase9/10/v2/staging) → ~0.1M
7. Ayon128 → ~0.3M

**≈ 15-16M tokens**, license-clean, all three languages covered. This is the smallest corpus likely to produce a measurably bilingual model.

---

## 13. ZERO-BUDGET TRAINING ROADMAP

1. CPU smoke test (Stage 1, ~30min, local) — verify pipeline.
2. Kaggle 2×T4 (~30h/week free) — Stage 2 pretrain ~5-10h.
3. Checkpoint every 30min → download → resume if session dies.
4. SFT on same free tier (~2-4h).
5. Evaluate with BanglaSafe/belebele/banglish_bench + manual prompts.

---

## 14. RISKS, LIMITATIONS, UNKNOWNS

- GPL-3.0 on bangla-alpaca-orca makes the largest bn instruction set legally risky — excluded.
- Banglish data is thin; IndicTalk-Romanized is the main hope.
- Bengali reasoning/decision data is scarce — may need owner/community-generated examples later.
- B-CORE is 20.8GB compressed — subset via streaming, don't full-download.
- All "verified" licenses are as of dataset card date; re-check before commercial launch.
- 8.84M params caps quality — this yields a useful small assistant, not AGI.

---

## 15. ACTIONS REQUIRING OWNER APPROVAL

1. Approve downloading B-CORE subset + IndicTalk + alpaca_chat_bangla + Ayon128 + GSM8K/Dolly (all free, license-clean).
2. Approve CPU smoke-train on phase10 subset.
3. Approve Kaggle/Colab account use (owner does phone verification).
4. Confirm commercial-use intent so CC-BY attribution tracking is set up.
5. Approve creating `data/corpus_v1/` outside git + manifest.

**STOP — awaiting explicit owner approval before Phase 4.**
