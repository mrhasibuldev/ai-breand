# NEXUSAI CORE-01 RUN4 — FINAL RELEASE VERIFICATION REPORT (v2.3.0)

**Date:** 2026-11-14 · CPU/static/archive tests only · NO training · NO commit/push.
**v2.3.0 adds enforced training-authorization gate (see §G).**

## A. Executive summary
Rebuilt the single-upload release end-to-end: fixed stale preflight pin (already
fixed in prior cycle, re-verified), reconciled stale inner `BUNDLE_MANIFEST.json`
instructions, bumped manifest to v2.2.0, rebuilt inner ZIP v3 + outer ZIP,
re-embedded notebook release identity. All identities now agree.

## B. Root causes
1. Upload Cell `EXPECTED` preflight hash was stale (`fe2e851b…`) after preflight
   cell edits — manual multi-artifact pinning is error-prone → fixed by updating
   pin AND adding reproducible builder `exports/build_run4_single_upload.py`.
2. Inner `BUNDLE_MANIFEST.json` still said "corpus uploaded separately / extract
   to /content/nexusai" — contradicted single-upload workflow → rewritten.
3. Prompt's baseline (`959ac4f0…`) was one rebuild behind; current release is newer.

## C. Files changed/created
- Changed: `docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py` (pins),
  `docs/notebooks/COLAB_RUN4_PREFLIGHT_CELL.py` (pins), `exports/README_RUN4.md`,
  `exports/build_run4_single_upload.py` (v3 inner + v2.2.0),
  `docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` (re-embed)
- Created: `exports/NEXUSAI_CORE01_RUN4_BUNDLE_v3.zip`,
  `exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.sha256`, this report
- NOT modified: Run3 checkpoint, corpus, tokenizer, model code, driver (except
  prior approved epoch/guard fixes), no Git commit/push

## D. Release verification — 14/14 PASS (all executed)
outer sha/size · testzip · manifest v2.2.0/7 entries · EXPECTED↔manifest pins ·
all payload sha+size (streamed) · safe paths/no dups/no symlinks · inner testzip ·
zero-step guard present · EPOCHS=5 present · inner manifest v2.1.0 reconciled ·
preflight pins consistent · no-training assertions

## E. Artifact identities
| Artifact | Size | SHA-256 |
|---|---|---|
| **Outer ZIP** | **173,914,048** | **`8b2129649c840e1b7009ea57babacd0e3831185852a070cd4391fbcdda3849ef`** |
| Inner ZIP v4 | 300,734 | `778ded61720651951e1dc24ce02e3c36aa520c187498e9657d826af3a050110e` |
| Upload cell | 19,018 | `ad3124f1…` |
| Preflight cell | 30,708 | `62fec3a7…` |
| Gate cell (new) | ~2.5KB | `COLAB_RUN4_TRAINING_GATE_CELL.py` |
| Corpus | 385,217,021 | `5f8572ed…` |
| Run3 ckpt | 106,777,501 | `ad515cade…` |
| Evidence | 2,932 | `0cb7588d…` |

Checksum file: `exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.sha256`

## F. Checkpoint safety
Run3 sha before == after: `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` — byte-identical.

## G. Resume readiness
Driver `range(current_epoch=3, epochs=5)` → 2 real epochs; resume restores
model/opt/sched/scaler/RNG (verified bounded smoke + CPU guard tests);
zero-step guard prevents false completion. `steps_executed` reported.

## H. Test results by class
- Static/compile: PASS (all cells+driver)
- CPU driver tests: PASS (zero-step guard exit-1; positive run steps 1341→1343)
- Archive/integrity: PASS 14/14
- GPU/Colab/Drive: **NOT RUN** — requires user

## I. Remaining limitations
- Colab/Drive/GPU unverified until user runs cells
- No checkpoint rotation (~7-8.5GB Drive needed)
- Corpus quality caveats (see forensic audit) — SFT phase needed for
  conversational/identity goals

## G. Training authorization gate (v2.3.0)
- NEW `docs/notebooks/COLAB_RUN4_TRAINING_GATE_CELL.py` + notebook Cell 10:
  requires preflight report non-BLOCKED + `input()` exact phrase
  `START NEXUSAI CORE-01 TRAINING` → writes `reports/run4/TRAINING_AUTHORIZATION.json`
- Train cell now REFUSES to run without that marker (checks `authorized:true`
  + exact phrase). Wrong/missing phrase → SystemExit, no training.
- Verified statically: gate check precedes all training logic; marker is
  atomic (tmp+os.replace); preflight BLOCKED → gate exits.
- Gate cell itself never starts training. Colab runtime test: NOT RUN.

## J. Final status: **READY FOR USER UPLOAD**
(Next gates: Colab preflight → GPU smoke → explicit `START NEXUSAI CORE-01 TRAINING`)
