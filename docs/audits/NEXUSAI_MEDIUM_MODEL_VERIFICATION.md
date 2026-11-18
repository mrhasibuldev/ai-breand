# NexusAI nexus-medium — Independent Verification (STAGE B)

**Date:** 2026-11-17 · local CPU · registry fallback model

## Artifact
- ckpt `models/checkpoints_medium/final_model.pt`
- config: d_model=128, layers=2, heads=2, d_ff=512, max_len=128, vocab=8000
- params: **2,468,928** · tokenizer: same sp_bpe_8k

## Tests
| check | result |
|---|---|
| weights_only=True load | PASS |
| strict state-dict | PASS (0 missing/unexpected) |
| native greedy generation ×3 prompts | **ALL EMPTY — immediate EOS** |

Prompts: "Hello! Who are you?", "What is 2+2?", "tomar naam ki?" → all `''`.

## Verdict
| capability | status |
|---|---|
| loads strictly | PASS |
| generates text | **FAIL — 0/3 non-empty** |
| usable as fallback | **FAIL for generation** — only safe as last-resort loader |

## Conclusion
nexus-medium is effectively **non-functional for generation** (always EOS).
Registry correctly labels it "very weak; emergency fallback only" — that
label is accurate. It must never be presented as a working model.
Recommendation: keep registered-but-disabled for serving; do not route to it.
