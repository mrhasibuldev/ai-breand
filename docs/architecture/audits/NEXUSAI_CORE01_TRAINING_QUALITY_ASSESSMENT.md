# Core-01 Training Quality Assessment — 2026-11-17 (measured)

## Corpus (corpus_train.jsonl — full scan, 216,193 records)
| lang | count | % |
|---|---|---|
| en | 130,753 | 60.5% |
| bn_mixed | 84,000 | 38.9% |
| bn | 819 | 0.4% |
| banglish | 459 | 0.2% |
| mixed | 162 | 0.07% |

Categories: english_general 61,960 · english_simple 60,000 ·
bangla_general 54,000 · bangla_instruction 30,000 · reasoning_* ~10,293.
Avg ~861 chars/record. Prior dup estimate: 6,922 exact dup texts.

## Corrections to earlier claims
- Bengali-family content is ~39% (bn_mixed 84K), NOT "mostly English only" —
  earlier estimate was wrong. BUT `bn` proper-script = only 819 records and
  banglish = 459 — the conversational/Banglish gap is real.
- `bangla_instruction` 30K exists — but neural output is still weak →
  quantity ≠ quality; likely template-ish instruction data.

## Pipeline (verified correct)
Causal mask, dataset-level shift, CE ignore pad, grad-accum scaling,
fp16+GradScaler, atomic ckpts, full resume. Loss 4.43→2.92 (reported Run4).

## Assessment
- For language modeling: ADEQUATE-BETTER than assumed.
- For conversation/instruction/Banglish: INSUFFICIENT — needs SFT phase.
- Bengali script generation weak despite 39% bn_mixed → suggests bn_mixed
  may be romanized/parallel text or low diversity; needs content sampling
  (not done — would require reading records).

## SFT readiness
NOT YET — pretraining quality unproven on Run4 (unverified ckpt) and
neural outputs are gibberish-leaning even on Run3. Sequence: verify Run4 →
benchmark → targeted pretraining fix if needed → THEN SFT.
