# NexusAI Core-01 Run3 — Independent Verification (STAGE B)

**Date:** 2026-11-17 · verification-only · local CPU

## Artifact identity
- ckpt `models/checkpoints_core01_run3/checkpoint_final.pt`
  sha256 `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` UNCHANGED
- tokenizer `sp_bpe_8k.model` sha `2fcc6a87…` UNCHANGED
- weights_only=True + narrow numpy allowlist (RNG state) — no weights_only=False
- strict load: missing=0 unexpected=0 · params 8,842,560 · CPU

## Generation benchmark — 15 prompts, native InferenceEngine, greedy
| prompt | result |
|---|---|
| bn_id/bn_greet/bn_fact | **EMPTY** (immediate EOS) ×3 |
| bn_explain | Bengali-script-ish fragment, incoherent |
| en_id/en_fact/en_explain/en_uncertain | English gibberish stories ×4 |
| bg_id/bg_fact | gibberish ×2 |
| rs_add/rs_apple/rs_day/rs_compare | **EMPTY** ×4 (all arithmetic!) |
| rs_logic | gibberish |

**Totals: 15 prompts → 7 EMPTY (47%), 8 non-empty ALL low-quality,
0 repetition loops, 0 prompt-echo.**

## Verdicts
| check | status |
|---|---|
| checkpoint integrity | PASS |
| safe+strict load | PASS |
| native neural generation executes | PASS (fwd_calls>0 all non-empty) |
| Bengali output | FAIL (empty or script-noise) |
| English output | FAIL (semantically irrelevant) |
| Banglish | FAIL |
| arithmetic/reasoning | **FAIL — 0/5 correct** (4 empty + 1 gibberish) |
| multi-turn/context | NOT VERIFIED (engine is single-turn) |
| conversational ability | **FAIL** |

## Conclusion
Run3 = technically functional pipeline, **conversationally non-viable**.
Serving it is honest only because provenance labels it neural; quality must
not be claimed. SFT (Run5) is the required next step.
