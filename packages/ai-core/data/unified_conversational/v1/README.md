# unified_conversational v1

Trilingual (en/bn/banglish/mixed) conversational SFT dataset for NexusAI
four-core training. Built by `packages/ai-core/data/build_unified_conv.py`
(SEED=42). Authored seeds + deterministic procedural math + documented
paraphrase variants. NO external AI used anywhere.

## Files
- train.jsonl / validation.jsonl / test.jsonl — approved records
- dataset_manifest.json — counts, distributions, schema note
- split_manifest.json — conversation-group-atomic split method
- quality_report.json — approved/rejected + reasons
- rejected_records.jsonl — quarantined records with reject_reason
- checksums.sha256 — SHA-256 of all artifacts

## Schema (compatible with core01/sft_dataset.py ChatSFTDataset)
{"sample_id","id","lang","category","task","conversation_id",
 "messages":[{"role":"user"|"assistant","content"}],
 "split_group","provenance","quality"}

## Stats (v1)
645 approved / 27 rejected (all dup_question). train 581 / val 32 / test 32.
Langs (train): en 279, bn 215, banglish 84, mixed 3.
Categories: math 287, qa 108, everyday_help 49, knowledge 33,
instruction 15, social 13, smalltalk 17, identity 13, uncertainty 17,
multi_turn 6, greeting 6, thanks 4, farewell 6, refusal 4, mixed_lang 3.

## Known limitations
- Below the 3-5k aspirational target — honest smaller set; math is
  ~50% of records (procedural). Conversational categories need a v2
  expansion with more authored trilingual content.
- Paraphrase variants share answers (documented, group-atomic splits).
- Semantic quality is rule-checked only; human review still recommended
  for bn/banglish naturalness before flagship training.
