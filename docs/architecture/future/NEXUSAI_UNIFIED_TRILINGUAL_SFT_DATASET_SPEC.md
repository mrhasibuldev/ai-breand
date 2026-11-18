# Unified Trilingual SFT Dataset — Specification (as-built v1)

## Schema (VERIFIED compatible)
Records match `core01/sft_dataset.py` ChatSFTDataset expectations:
`messages:[{role,content}]` with user/assistant turns; loss supervises
assistant tokens + EOS only. Extra metadata (lang, category, provenance,
quality, split_group) is NOT fed to the model — loader reads `messages`.

## Composition rules (enforced in builder)
- `lang` ∈ en | bn | banglish | mixed — auto-detected from script
  (Bengali Unicode → bn; romanized Bengali markers → banglish).
- `category` = primary task (one per record): greeting, identity, thanks,
  farewell, smalltalk, qa, instruction, everyday_help, knowledge,
  uncertainty, refusal, social, math, multi_turn, mixed_lang.
- Multi-turn records contain full ordered message lists.
- `split_group` groups paraphrase variants + multi-turn atoms so no
  related example crosses train/val/test.

## Provenance & licensing
- All records `provenance.source="authored"` or `"procedural"` —
  self-authored seeds and deterministic math. No external datasets
  incorporated in v1 (dolly/gsm8k license review still pending; phase9_1
  unpaired texts unsuitable for SFT without pairing).
- Founder identity (Hasibul) exists ONLY as assistant answers in
  `identity` records — no runtime handler.

## Quality gates applied (rule-based)
Valid roles, non-empty content, answer≠question, exact-question dedup,
prefix near-dup (>3 collisions quarantined), group-atomic splits
(seed 42), manifests + sha256 checksums, rejected_records.jsonl kept.

## v1 honest assessment
645 records is below the 3-5k aspiration. Strengths: verified math,
uncertainty/refusal coverage, trilingual balance attempt. Gaps:
conversational categories thin (greeting 6, multi_turn 6, social 13);
paraphrase variants are surface-level; bn/banglish naturalness needs
human review. v2 should prioritize authored conversational depth over
count.
