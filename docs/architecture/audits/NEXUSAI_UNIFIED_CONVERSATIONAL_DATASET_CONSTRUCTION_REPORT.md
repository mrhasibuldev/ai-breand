# Unified Conversational Dataset — Construction Report

Mission: dataset engineering only. NO training, NO commits, NO pushes.

## A. Git & project safety — VERIFIED
HEAD `cb289fb` (neural-only chat commit, unpushed). 142 uncommitted
entries (pre-existing user work + mission artifacts) — all preserved.
New output isolated to `data/unified_conversational/v1/` + builder script.

## B. Existing dataset inventory — VERIFIED (re-checked)
Prior audit numbers confirmed: core02 2,650 / core03 1,750 /
core04 318(+full); conversational assets: phase3/sft_v1 536, sft_v2 103,
phase9_1 cleaned bn texts 741+590+151 (unpaired), reasoning_train 3,411,
dolly 14,779 EN, gsm8k 7,473 EN, run4_corpus 216k pretrain.

## C. Previous findings re-verification — VERIFIED
Core statuses, eval scores, leakage findings all match prior reports.

## D. Final schema — VERIFIED
`messages:[{role,content}]` + metadata; compatible with
ChatSFTDataset (core02/03/04 builders use identical shape). No loader
changes needed — VERIFIED by schema inspection.

## E. Output paths — VERIFIED
`packages/ai-core/data/unified_conversational/v1/`:
train.jsonl (581), validation.jsonl (32), test.jsonl (32),
dataset_manifest.json, split_manifest.json, quality_report.json,
rejected_records.jsonl, checksums.sha256, README.md.
Builder: `packages/ai-core/data/build_unified_conv.py` (SEED=42).

## F. Total approved — VERIFIED: 645 (27 rejected, all dup_question)
Below 3-5k target — reported honestly; conversational depth prioritized
over padding.

## G. Rejected — VERIFIED: 27 exact-question duplicates (quarantined in
rejected_records.jsonl with reasons).

## H–L. Coverage (train split, VERIFIED from manifest)
- bn 215 (37%), en 279 (48%), banglish 84 (14%), mixed 3 (<1%)
- Categories: math 287, qa 108, everyday_help 49, knowledge 33,
  instruction 15, smalltalk 17, uncertainty 17, social 13, identity 13,
  multi_turn 6, greeting 6, thanks 4, farewell 6, refusal 4, mixed_lang 3
- Single-turn dominant; multi_turn only 6 records — GAP.

## M–P. Core coverage
Core-01: all categories usable but thin conversationally — PARTIAL.
Core-02: instruction 15 + multi_turn 6 — INSUFFICIENT alone; needs
reasoning_train conversion.
Core-03: math 287 verified — USABLE supplement to core03_math.
Core-04: knowledge 33 + uncertainty 17 + refusal 4 — directionally right,
volume too small for boundary-learning; needs expansion.

## Q–S. Uncertainty/social/identity — VERIFIED present but small
(uncertainty 17, refusal 4, social 13, identity 13). Identity teaches
Hasibul via data only. Safe refusal examples included (weapons, malware,
hacking, fake reviews, secrets, live data).

## T. Provenance/licensing — VERIFIED
All records authored/procedural — self-owned, no license risk.
External datasets NOT incorporated (license review pending).

## U. Training compatibility — VERIFIED
messages schema matches ChatSFTDataset; metadata ignored by loader;
BOS/EOS/masking handled by existing pipeline. Multi-turn supported.

## V. Benchmark readiness — PARTIAL
Spec exists (prior docs); benchmark prompts must be authored separately
and kept out of training data — NOT yet built.

## W. Documentation — VERIFIED
Dataset README + 3 docs: this report,
NEXUSAI_UNIFIED_TRILINGUAL_SFT_DATASET_SPEC.md,
NEXUSAI_FOUR_CORE_DATASET_MAPPING.md.

## X. Blockers
1. Volume below target — needs v2 authored expansion (bn/banglish
   conversational depth especially).
2. Semantic quality is rule-checked only — human review recommended.
3. External datasets (dolly/gsm8k/phase9_1) unusable until license/split
   audits complete.
4. Multi-turn coverage minimal (6 records).

## Y. Reproducibility
`python build_unified_conv.py` (SEED=42) regenerates all artifacts +
checksums deterministically.

## Z. Verdict — DATASET PARTIALLY COMPLETE
Foundation is real, verified, compatible, and honest — but below the
quantity/coverage bar for flagship training. Recommend v2 expansion
before core01 conv-SFT; v1 suitable for pipeline smoke tests.

NO TRAINING WAS STARTED. NO CHECKPOINTS WERE MODIFIED.
NO GIT COMMIT OR PUSH WAS PERFORMED.
