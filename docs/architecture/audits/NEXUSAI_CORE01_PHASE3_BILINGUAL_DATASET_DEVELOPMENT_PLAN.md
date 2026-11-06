# NEXUSAI CORE-01 — PHASE 3 BILINGUAL DATASET DEVELOPMENT PLAN

**Date**: 2026-11-06
**Type**: RESEARCH & PLANNING ONLY (No collection, download, or modification performed)
**Languages**: Bengali (বাংলা) + English + Romanized Bengali (Banglish) + code-mixed
**Constraint**: ZERO BUDGET — free/open-license sources only

---

## EXECUTIVE SUMMARY

- **Previous audit figures VERIFIED**: Phase 2 measured 83,892 records / ~5.46M tokens with the actual 8K tokenizer; Bengali = ~73K tokens (1.3%), English = ~5.38M (98.6%). This is the confirmed baseline.
- **Good news**: Legitimate free Bengali resources DO exist at useful scale — B-CORE (CC BY 4.0, commercial OK), BanglaLLM datasets (~1M+ instruction examples), Samanantar (CC0 packaging), IndicTalk (native + Romanized code-mixed dialogues), csebuetnlp/dailydialogue_bn (13K dialogues).
- **Bad news**: Several attractive datasets are license-blocked for commercial use — XL-Sum (CC BY-NC-SA), Alpaca (non-commercial), Bangla-SFT-50k (synthetic, unclear license). Must be excluded or quarantined.
- **Romanized Bengali**: Rare but real sources found — IndicTalk Romanized variant, tanziro/bangla-romanized-dhaka-shortchat (18K), Ayon128/Banglish-English, plus our own 69 staging examples.
- **Recommended distribution**: Bengali needs deliberate oversampling early (it is the weaker language). Proposed: ~35% Bengali script, ~30% English, ~15% Romanized, ~20% mixed/parallel — adjusted per stage.
- **Realistic path**: Stage 2 (~10-25M tokens) is achievable entirely from free sources already identified; Stage 3 (50-100M) requires B-CORE subset download (~1-3GB compressed — feasible on free storage but heavy for GitHub; keep in dataset storage, not git).

---

## 1. CURRENT DATASET ASSESSMENT (verified against Phase 2 audit)

| Metric | Value | Source |
|---|---|---|
| Total records | 83,892 | Phase 2 audit script (actual tokenizer run) |
| Total tokens | ~5,460,193 | same |
| Bengali tokens | ~73,145 (1.3%) | same |
| English tokens | ~5,383,266 (98.6%) | same |
| Mixed | ~3,177 | same |
| Exact duplicates | 63 | same |
| UNK tokens | 7,340 (0.13%) | same — healthy |

**VERIFIED FACT**: Bengali:English ratio is ~1:73 by tokens. For a bilingual product this is inverted from the goal.

**License triage of existing data:**

| Dataset | License | Commercial? | Action |
|---|---|---|---|
| phase10 (train/val/test) | Project-generated | ✅ | Retain — primary |
| phase9_1 / phase9_2 corpora | Project-generated | ✅ | Retain after dedup vs phase9_1 overlap |
| train_v2, train_final, conversational_data, public_v1.0*, synthetic | Project-generated | ✅ | Retain (tiny) |
| love_emotion staging | Project-generated | ✅ pending review | Retain — fix double-encoded JSONL |
| GSM8K | MIT | ✅ | Retain — math reasoning |
| Dolly 15K | CC BY-SA 3.0 | ⚠️ with attribution + share-alike | Retain w/ attribution record |
| Wikipedia bn/en collected | CC BY-SA 4.0 | ⚠️ attribution | Tiny anyway |
| **Alpaca 52K** | **Non-commercial research** | ❌ | **EXCLUDE from product training** |
| training/original_dataset.jsonl | Wikipedia dump | ⚠️ low quality | Exclude (nav junk) |
| knowledge/ | User data | ❌ privacy | NEVER upload anywhere |

## 2. BENGALI DATASET SOURCE CATALOG

Verified via official HF/GitHub pages (links at end). Sizes as stated by publishers; token counts are estimates.

### A. Bengali general text (pretraining)

| Dataset | Source | Size | License | Commercial | Use |
|---|---|---|---|---|---|
| **B-CORE** | huggingface.co/datasets/nahid-hub/B-CORE-bengali-corpus | 16.5M docs / 4.32B tokens / 52GB (20.8GB compressed) | **CC BY 4.0** | ✅ w/ attribution | **PRIMARY pretraining source** — subset it |
| Bengali Wikipedia dump | dumps.wikimedia.org | ~100K+ articles | CC BY-SA 4.0 | ⚠️ attribution | Pretraining supplement |
| BdNC (Bangladesh National Corpus) | corpus.bangla.gov.bd | 40GB / 3B+ words | verify | UNVERIFIED | Candidate — license check needed |
| VACASPATI literary corpus | arXiv 2307.05083 | 11M sentences | verify | UNVERIFIED | Literature — quality candidate |
| CC-100 Bangla / OSCAR Bangla | statmt.org / oscar.cs.helsinki.fi | 8-12GB | verify per-source | UNVERIFIED | Web text — noisy, needs filtering |
| Leipzig Bengali corpora | corpora.uni-leipzig.de | 1.65M sentences | verify | UNVERIFIED | News text |
| BanglaCHQ-Summ | github (via Foysal87 catalog) | 2,350 health-QA pairs | verify | UNVERIFIED | **Health-domain relevant** — check |

### B. Bengali conversation / instruction

| Dataset | Source | Size | License | Commercial | Use |
|---|---|---|---|---|---|
| **BanglaLLM/bangla-alpaca-orca** | huggingface.co/datasets/BanglaLLM/bangla-alpaca-orca | 172K examples | research-group release; license field UNVERIFIED | UNVERIFIED | Instruction tuning — verify license first |
| **BanglaLLM/bangla-alpaca** | huggingface.co/datasets/BanglaLLM/bangla-alpaca | 51,760 | same | UNVERIFIED | Instruction tuning |
| **BanglaLLM/bangla_math_by_Ashrafur** | via banglallm.github.io | 859K | UNVERIFIED | UNVERIFIED | Math reasoning — large, verify |
| **csebuetnlp/dailydialogue_bn** | huggingface.co/datasets/csebuetnlp/dailydialogue_bn | 11,118 train dialogues (multi-turn) | research dataset; check terms | UNVERIFIED | **Conversation** — verify |
| **Mahadih534/alpaca_chat_bangla** | huggingface.co/datasets/Mahadih534/alpaca_chat_bangla | 51.8K | **CC-BY-2.0** | ✅ w/ attribution | Instruction tuning — usable |
| abrarfahim/alpaca-cleaned-bn | huggingface.co/datasets/abrarfahim/alpaca-cleaned-bn | ~52K | UNVERIFIED | UNVERIFIED | Alt Bengali Alpaca |
| worldjit/bengali-sft-v1 | huggingface.co/datasets/worldjit/bengali-sft-v1 | 120 | **Apache-2.0** | ✅ | Tiny but clean |
| spitfire4794/Bangla-SFT-50k | huggingface.co/datasets/spitfire4794/Bangla-SFT-50k | 50,053 | synthetic (Gemini+DeepSeek generated), "non-commercial projects" credit | ❌ risky | **EXCLUDE** — synthetic + license unclear |
| bhasha-sft (Bengali subset) | huggingface.co/datasets/soketlabs/bhasha-sft | part of 13M multilingual | mixed cc-by-4.0/apache-2.0/mit | per-subset | Candidate after license filter |
| BanglaSafe | via BanglaLLM | 879 safety questions | research | eval only | **Evaluation/safety test set** |

### C. Romanized Bengali (Banglish)

| Dataset | Source | Size | License | Use |
|---|---|---|---|---|
| **LingoIITGN/IndicTalk (bengali, Romanized variant)** | huggingface.co/datasets/LingoIITGN/IndicTalk | multi-turn persona dialogues, Native+Romanized | verify | **BEST Romanized source** — real conversational Banglish |
| tanziro/bangla-romanized-dhaka-shortchat-small-sft | huggingface.co/datasets/tanziro/... | 18K rows | verify | Romanized Dhaka chat SFT |
| Ayon128/Banglish-English | huggingface.co/datasets/Ayon128/Banglish-English | pairs | verify | Banglish↔English parallel |
| sifat-febo/banglish_bench | huggingface.co/datasets/sifat-febo/banglish_bench | 700 prompts | eval | **Evaluation benchmark** for Banglish |
| Our staging love_emotion_bn_latn | local `data/staging/` | 20 | project | Keep — fix JSON encoding |

### D. Bengali-English bilingual / parallel

| Dataset | Source | Size | License | Use |
|---|---|---|---|---|
| **AI4Bharat Samanantar (bn subset)** | indicnlp.ai4bharat.org/samanantar | millions of pairs (49.6M across Indic) | **CC0 packaging** (source text rights vary — mostly Wikipedia/news CC BY-SA) | Translation pairs, mixed-language training |
| csebuetnlp/BanglaNMT | via Foysal87 catalog | 2.38M pairs / 133MB | verify | Parallel corpus |
| SUPara0.8M | IEEE DataPort | 0.8M balanced En-Bn | verify | Parallel |
| BanglaSTEM | arXiv 2511.03498 | 5K STEM pairs | verify | Niche |

## 3. ENGLISH DATASET REVIEW (existing)

| Dataset | Verdict | Reason |
|---|---|---|
| GSM8K (8,792) | **RETAIN** | MIT, high-quality math CoT, directly usable |
| Dolly 15K (14,779) | **RETAIN w/ attribution** | CC BY-SA 3.0 — record attribution; human-written, good quality |
| Alpaca (52,002) | **EXCLUDE for product** | Non-commercial license; also self-instruct synthetic noise. Keep for research-only if desired |
| Wikipedia en collected | RETAIN (tiny) | CC BY-SA attribution; only 14 articles anyway |
| phase9_2 english.txt junk lines | **FILTER** | Contains ticker symbols/list fragments (~87 records) |
| synthetic/*, merged_train, train_final | RETAIN but low priority | Project-generated, tiny, some duplication |
| training/original_dataset.jsonl | **EXCLUDE** | Single Wikipedia dump w/ navigation boilerplate |
| knowledge/ | **NEVER use in training uploads** | User private data |

## 4. RECOMMENDED LANGUAGE DISTRIBUTION

Proposed target **35% Bengali script / 30% English / 15% Romanized / 20% mixed+parallel**.

Rationale vs the suggested 40/40/10/10:
- Bengali is the priority language AND currently weakest → give it the largest single share.
- Romanized raised to 15% because it's a core product requirement (Banglish users) but data is scarce — don't over-promise; cap at what sources provide.
- "Mixed/parallel" at 20% leverages Samanantar/BanglaNMT which are abundant and teach code-switching naturally.
- English at 30% is still substantial (Dolly+GSM8K alone ≈ 4.3M tokens) — prevents English collapse without letting it dominate.

**Early-training rule**: For the first run (Stage 2), Bengali effective share should be ~40%+ via oversampling, because the model starts with zero Bengali competence. As Bengali corpus grows (Stage 3+), converge to the 35/30/15/20 target.

**Preventing English dominance**: hard per-language token quotas during batch construction, not random mixing. Track running token counts per language in the training manifest.

**Romanized handling**: treat as its own bucket; do NOT rely on the model to "infer" Banglish from Bengali+English — include real Romanized conversations (IndicTalk-Romanized, Dhaka chat).

**Translation pairs**: include a modest share (~10-15% of mixed bucket) — they teach cross-lingual alignment, useful for a bilingual assistant.

**Avoiding incorrect Bengali**: prioritize human-written sources (B-CORE filtered, dailydialogue_bn, alpaca_chat_bangla CC-BY) over raw machine-translated dumps; spot-check samples; exclude synthetic-only sets (Bangla-SFT-50k).

## 5. TOKEN TARGETS ROADMAP

| Stage | Tokens | Composition | Purpose | Compute | Success looks like |
|---|---|---|---|---|---|
| 1 | 1-5M | Existing phase10 + phase9_x + small subsets | Pipeline verification | CPU/1×T4, <2h | Loss decreases, coherent short outputs, checkpoint/resume works |
| 2 | 10-25M | + GSM8K subset + alpaca_chat_bangla + IndicTalk + B-CORE sample (~5M) + dailydialogue_bn | First real bilingual experiment | 1×T4 16GB, ~5-15 GPU-h | Bengali sentences form; simple Q&A partially works; no gibberish |
| 3 | 50-100M | + larger B-CORE subset (20-40M), bangla-alpaca-orca, Samanantar bn subset, filtered Dolly | Initial capability model | 1-2×T4, ~20-40 GPU-h over multiple sessions | Conversational Bengali+English, basic instruction following, math improves |
| 4 | 100-300M | + full B-CORE Bengali share, BanglaNMT, expanded Romanized | Scale-up if Stage 3 succeeds | multi-session free tier or paid later | Noticeably better Bengali fluency; still bounded by 8.8M capacity |

**Honest note**: token counts do NOT guarantee intelligence. 8.84M params caps achievable quality regardless of data. Bengali fluency is the realistic near-term goal; general reasoning will remain limited.

## 6. DATA QUALITY CONTROL FRAMEWORK

Implement as a preprocessing pipeline (future work, not now):

1. **Exact dedup**: MD5/SHA-256 of normalized text (already prototyped in audit script).
2. **Near-dedup**: MinHash/LSH on 5-gram shingles — flag >0.8 similarity.
3. **Empty/malformed**: JSON/JSONL parse validation; strip records failing schema.
4. **Unicode/Bengali integrity**: NFC normalization; detect broken Bengali (unmatched hasanta/juktakkhor patterns, excessive U+FFFD).
5. **Spam/repetition**: reject records with >30% repeated n-grams or identical line loops.
6. **Language-label verification**: re-run script-based detection (Bengali unicode block ratio) and relabel mismatches.
7. **PII scan**: regex for phones, emails, national IDs (Bangladesh formats), addresses → quarantine.
8. **Copyright**: maintain `license` + `source` + `attribution` fields per record batch; block NC/ND licenses from product corpus.
9. **Evaluation leakage**: hold out fixed dev/test sets BEFORE any training merge; hash-check that no train record matches eval records.

**Corpus separation**:
- `pretrain/` — raw text streams (dedup'd, license-clean)
- `sft/` — instruction/response pairs
- `eval/` — fixed held-out sets per language (never trained on)
- `quarantine/` — failed checks, license-blocked, PII-flagged

## 7. TOKENIZER COMPATIBILITY ASSESSMENT (8K BPE)

**VERIFIED (Phase 2 tests)**: 0% UNK on Bengali, English, Romanized, math symbols in samples; Bengali words tokenize to ~1 token each efficiently.

**Measured fragmentation** (from audit): Bengali ~3 tokens/sample avg vs English ~4-5 — Bengali is actually token-efficient. Romanized Bengali tokenizes as English subwords (expected).

**Known limitations to document (future)**:
- 8K vocab may under-cover rare Bengali conjuncts (যুক্তাক্ষর) and English technical terms → higher fragmentation on domain text.
- Recommendation stands from Phase 1 report: keep 8K through ~10M params; evaluate 16K only if Stage 3+ shows vocab pressure (measure: avg tokens/word on held-out Bengali text > ~1.5× English rate).
- No retraining now.

## 8. STORAGE & VERSIONING STRATEGY (zero-budget)

- Store datasets OUTSIDE git: `data/corpus_v1/` with per-source subdirs; `.gitignore` already covers `data/`.
- Format: JSONL for structured, plain `.txt` (one doc per line) for pretraining streams.
- Manifest per release: `manifest.json` with source URL, license, SHA-256 per file, record/token counts, language breakdown.
- Compression: gzip/jsonl.gz for archival; B-CORE subset downloadable per-file.
- Versioning: `corpus_v1`, `corpus_v2`... immutable once used in a training run; never edit in place.
- Backup: local disk + optional free HF Dataset repo (private) as off-site copy — only license-clean public data, never `knowledge/`.
- GitHub: do NOT commit datasets; commit only manifests/scripts.

## 9. ZERO-BUDGET COLLECTION ROADMAP

All free; owner approval needed before downloading:

1. **Verify licenses** (this week, no download): BanglaLLM datasets, dailydialogue_bn, IndicTalk, alpaca_chat_bangla (CC-BY-2.0 confirmed), BanglaNMT, SUPara, B-CORE subset terms.
2. **Stage 2 corpus (~10-25M tokens)**: B-CORE sample (~5M tok), bangla-alpaca-orca subset, dailydialogue_bn, IndicTalk bn, alpaca_chat_bangla subset, existing project data, GSM8K subset.
3. **Stage 3 corpus (50-100M)**: larger B-CORE slice, Samanantar bn pairs, BanglaNMT, filtered Dolly.
4. Exclude always: Alpaca raw, XL-Sum, Bangla-SFT-50k, knowledge/, anything NC-licensed for product.

## 10. RISKS & LIMITATIONS

- **License uncertainty** on several Bengali sources (BanglaLLM, dailydialogue_bn, IndicTalk) — must verify before product use; mark UNVERIFIED until checked.
- **B-CORE is 52GB** — subset carefully; do not attempt full download on limited disk/connection.
- **Synthetic data risk**: several Bengali SFT sets are LLM-translated/Generated — quality and license both questionable; prefer human-curated.
- **Romanized Bengali scarcity**: real sources are small; may need owner/community contribution later.
- **8.84M param ceiling**: even perfect data won't make a large model; set expectations.
- **Machine translation errors** in dailydialogue_bn-type sets — spot-check before bulk use.

## 11. RECOMMENDED NEXT PHASE

**PHASE 4 — Corpus Build & License Verification** (upon approval):
1. Verify licenses for the UNVERIFIED sources above.
2. Download Stage-2 corpus to `data/corpus_v1/` (outside git).
3. Run dedup + quality pipeline; produce manifest with token counts per language.
4. CPU smoke-train Core-01 on the new corpus (Stage 1 verification).
5. Then Kaggle/Colab free GPU run for Stage 2.

---

## SOURCE LINKS (official)

- B-CORE: https://huggingface.co/datasets/nahid-hub/B-CORE-bengali-corpus
- BanglaLLM: https://banglallm.github.io/ · datasets: BanglaLLM/bangla-alpaca, bangla-alpaca-orca, bangla_math_by_Ashrafur
- Samanantar: https://indicnlp.ai4bharat.org/samanantar/
- XL-Sum (NC — excluded): https://huggingface.co/datasets/csebuetnlp/xlsum
- dailydialogue_bn: https://huggingface.co/datasets/csebuetnlp/dailydialogue_bn
- IndicTalk: https://huggingface.co/datasets/LingoIITGN/IndicTalk
- alpaca_chat_bangla (CC-BY-2.0): https://huggingface.co/datasets/Mahadih534/alpaca_chat_bangla
- Banglish Romanized chat: https://huggingface.co/datasets/tanziro/bangla-romanized-dhaka-shortchat-small-sft
- Banglish-English: https://huggingface.co/datasets/Ayon128/Banglish-English
- Banglish bench (eval): https://huggingface.co/datasets/sifat-febo/banglish_bench
- Bengali corpus catalog: https://github.com/Foysal87/Bangla-NLP-Dataset
- Belebele eval (ben_Beng/ben_Latn): https://huggingface.co/datasets/facebook/belebele
- bhasha-sft: https://huggingface.co/datasets/soketlabs/bhasha-sft

**CONFIRMATION**: Research/planning only. No datasets downloaded, no files modified, no training, no Git changes. Awaiting owner approval.
