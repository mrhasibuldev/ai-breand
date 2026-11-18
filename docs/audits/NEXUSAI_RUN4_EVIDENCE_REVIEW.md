# NexusAI Run4 — Evidence Review (independent)

**Date:** 2026-11-17 · source: Colab v7 cell console output (user-provided)
Reports live at Colab `/content/NEXUSAI_RUN4_CPU_AUDIT/` (not local).

## Independently cross-checked claims
| claim | evidence | verdict |
|---|---|---|
| ckpt sha `761a5b14f81a…` size 106,777,501 | console `[PASS] ckpt_sha256` | VERIFIED (transcript) |
| tokenizer sha `2fcc6a87…` | console `[PASS]` | VERIFIED |
| weights_only=True + allowlist(30) | console `[PASS] deser` | VERIFIED |
| strict load 0/0, 8,842,560 params | console `[PASS]` | VERIFIED |
| CPU-only, cuda_init=False | console `[PASS] cpu_only` | VERIFIED |
| 11/11 prompts, fwd proof | console `[PASS] generation` | VERIFIED |
| post-test hashes unchanged | `[PASS] post_hash` | VERIFIED |
| empty=5/11, quality NEEDS IMPROVEMENT | console + per-lang table | VERIFIED |

## Actual outputs (from transcript)
- bn_name: `'Answer: আমি জানি না। Explanation: ছোট কাজ আগে করলে বড় কাজের জন্য সময়'` — Bengali script, template noise
- bn_how: Bengali-ish fragment; bn_ai: EMPTY
- en_name: song-lyrics; en_how: EMPTY; en_ai: repetition loop
- bg_do/bg_ai: EMPTY; bg_name: irrelevant English story
- rs_apple: EMPTY; rs_sun: irrelevant story

## Independent assessment
- **Pipeline: fully verified** — every integrity gate PASS with hash evidence.
- **Quality: poor** — Bengali script appears (improvement over Run3) but
  answers are template/story noise; 5/11 empty; reasoning fails.
- vs Run3: fewer empties (5/11 vs 7/15), Bengali script present — modest gain.
- **Cannot claim conversational ability.** SFT required.

## Evidence gaps
- JSON reports not downloaded locally — analysis based on console transcript
  only. Recommend downloading `NEXUSAI_RUN4_CPU_VERIFICATION.json` for
  token-level audit.
