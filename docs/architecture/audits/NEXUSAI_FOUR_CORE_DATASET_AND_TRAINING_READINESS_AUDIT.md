# NexusAI Four-Core Dataset & Training Readiness Audit

Read-only forensic audit. No training, no file modification, no commits.
Baseline: local `cb289fb` (1 commit ahead of remote `d278893` — push pending,
not authorized this mission). Remote verified: `d2788936afd24f5a…`.

## A. Git & project safety (VERIFIED)
- Branch `main`; HEAD `cb289fb`; remote `d278893` — local ahead by 1
  (neural-only chat commit, intentionally unpushed).
- 139 uncommitted entries = pre-existing user work + mission leftovers;
  none disturbed. `*.pt`, `*.jsonl`, `.env`, `*.corrupt.bak` gitignored.

## B. Model inventory (VERIFIED — hashes recomputed this session)

| Core | Params | Checkpoint | SHA-256 (prefix) | Size | Status |
|---|---|---|---|---|---|
| 01 Run3 | 8,842,560 | checkpoints_core01_run3/checkpoint_final.pt | ad515cadea433d17 | 106.8MB | serving, poor quality |
| 01 Run4 | 8,842,560 | (preserved, not activated) | 761a5b14…(prior audit) | ~106MB | verified artifact |
| 02 v1 | 20,347,712 | checkpoints_core02_sft_v1 | e02df55fe1cd57a4 | 82.2MB | superseded (leaky split) |
| 02 v2 | 20,347,712 | checkpoints_core02_sft_v2 | 906d6024511f3e8a | 82.2MB | registered; 74.2% held-out |
| 03 v1 | 8,842,560 | checkpoints_core03_sft_v1 | b6e373bc77406033 | 35.9MB | superseded |
| 03 v2 | 8,842,560 | checkpoints_core03_sft_v2 | 1ff83fb9ecd93944 | 35.9MB | registered; 9.2% held-out |
| 04 v1 | 33,419,072 | checkpoints_core04_sft_v1 | 404b8c0f89f32e58 | 134.8MB | superseded |
| 04 v2 | 33,419,072 | checkpoints_core04_sft_v2 | 9c47fa30a1e8b65a | 134.8MB | superseded |
| 04 v3 | 33,419,072 | checkpoints_core04_sft_v3 | e46383195d328b91 | 134.8MB | registered; 73.3% seen-fact |
| medium | 2,468,928 | checkpoints_medium/final_model.pt | 4f592af9846b89… | small | excluded (dead quality) |

Tokenizer: `data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`
sha256=2fcc6a87c9ded27d…, vocab 8000, shared by all cores (VERIFIED).
Training infra: `sft_train.py` (response-only SFT, verified), `eval_core.py`,
`nexus_core.py`, `core01/sft_dataset.py` serialization (VERIFIED).

## C–F. Per-core assessment

### Core-01 (VERIFIED)
- Run3: pretraining on run4_corpus (216k records) — real weights, strict
  load OK, generates EN/BN/Banglish but incoherent/empty-prone.
- Run4: verified artifact, not activated (preserved).
- SFT suitability: YES — needs conversational SFT (new run name, e.g.
  `core01_conversational_sft_v1`); Run5/SFT path remains separately gated.
- Recommendation: primary conversational candidate AFTER conv-SFT;
  current Run3 not fit for neural-only chat quality.

### Core-02 (VERIFIED)
- 74.2% exact on question-held-out template data — slot-fill generalization,
  NOT reasoning (deduction/ordering near-memorized; multistep 25%).
- Can it become conversational? PARTIALLY — architecture supports it, but
  weights are template-specialized; conv-SFT would need to overcome strong
  prior. Recommendation: new instruction-SFT run on conversational+structured
  mix (`core02_instruction_sft_v1`); keep excluded from chat until re-eval.

### Core-03 (VERIFIED)
- 9.2% exact on clean split. Root causes (evidence-based):
  (a) 8.8M model + only 1,576 procedural examples — arithmetic is hard for
  small transformers without algorithmic scaffolding;
  (b) answers are bare numbers — tokenizer must emit multi-digit numbers
  token-by-token; BPE 8k likely fragments digits, hurting exactness;
  (c) no step-by-step supervision in most categories (answers are finals).
- Recommendations: add worked-solution format ("12 × 8 = 96" with steps),
  more data (gsm8k_cleaned 7,473 EN examples available — license check
  needed; Bengali math data absent — must generate procedurally),
  evaluate with numeric-tolerance metrics not just exact-match.
- Deterministic calculator remains the honest tool for simple arithmetic.

### Core-04 (VERIFIED)
- Memorizes 36 curated facts (73.3% seen); ~0% on unseen facts; hallucinates
  fluent wrong answers instead of refusing (only 3 uncertainty records).
- Root cause: fact-level split proved the model never learned "I don't
  know" — it learned answer-style, not knowledge boundaries.
- Recommendations: (a) scale curated fact cards 10-50x across domains;
  (b) add explicit "insufficient knowledge" training pairs for OFF-TOPIC
  questions (the correct answer IS refusal); (c) keep fact-level eval;
  (d) consider retrieval-augmented design later (not neural substitution).

## G. Dataset inventory (VERIFIED this session)

Four-core datasets (builders committed, manifests+sha256):
- core02_reasoning: 2,650 recs (train 2,386/val 132/test 132), question-level
  split, 0 exact-Q overlap. en 1,667 / bn 467 / banglish 252.
- core03_math: 1,750 recs (1,576/87/87), question-level split, 0 overlap.
  en 1,123 / bn 270 / banglish 183. Procedural generation.
- core04_knowledge: 318 recs (256/31/31) fact-level split, 0 test-answer
  overlap; core04_knowledge_full: all 318 merged for v3 training.

Candidate conversational/instruction datasets found (NOT modified):
- phase2/reasoning/reasoning_train.jsonl: 3,411 recs {instruction,answer,
  explanation,category,lang} — needs format conversion to messages schema;
  bn only 282.
- phase3/sft_v1/sft_train.jsonl: 536 recs {lang,category,messages}.
- sft_v2/{train,validation,test}.jsonl: 93/5/5 recs — too small alone.
- experimental/phase9_1/cleaned: bengali_chat_conv 590, combined 741,
  bengali_sft_v1 151 — all `text` field (need QA-pair extraction).
- collected/cleaned/dolly: 14,779 EN instruction records.
- collected/cleaned/gsm8k: 7,473 EN math word problems (+1,319 test).
- conversational_data.json 28, train_v2.json 502, train_final.json 223,
  merged_train.json 167 — small mixed sets.
- Pretraining corpora: run4_corpus 216k, cleaned_bangla ~285k records,
  raw_bongchat 150k, tinystories 60k — pretraining material, not SFT.

## H. Dataset quality (VERIFIED)
- Zero exact-duplicate records in all inspected files.
- Four-core datasets: deterministic/procedural generation — consistent
  format, but template-bound (core02) or narrow-domain (core03/04).
- Conversational coverage is THE gap: largest verified conversational
  SFT set is ~741 cleaned Bengali text records (unpaired) + 536 sft_v1 +
  93 sft_v2 — far below what's needed for fluent trilingual chat.
- dolly/gsm8k are EN-only; no verified Banglish conversational corpus found.
- Bengali SFT material must be authored/generated procedurally (allowed:
  deterministic templates + human-authored seed content; NOT external AI).

## I. Leakage audit (VERIFIED)
- core02/03: question-level hash split → 0 exact-question overlap
  (template skeletons still shared — measures slot-fill, documented).
- core04: fact-level (answer-hash) split → 0 test answers in train;
  1/11 val overlap (shared uncertainty phrasing — noted).
- Older datasets (sft_v1, phase9_1) — split integrity NOT re-verified;
  flagged for audit before reuse.

## J–S. See companion docs
Training configs → NEXUSAI_FOUR_CORE_SFT_TRAINING_STRATEGY.md
Dataset spec → NEXUSAI_UNIFIED_CONVERSATIONAL_DATASET_SPEC.md
Colab workflow → docs/notebooks/COLAB_NEXUSAI_FOUR_CORE_SFT.py (exists;
needs conv-data extension before use — prepared, not run).

## T. Readiness verdict
PARTIALLY READY. Infrastructure (training/eval/registry/router) VERIFIED.
Blocker: no sufficiently large, verified, trilingual conversational SFT
dataset exists. Building it is the critical path — everything else is
engineering already proven on the specialist cores.
