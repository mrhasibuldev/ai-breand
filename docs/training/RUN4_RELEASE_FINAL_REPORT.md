# Run4 Release — Final Forensic & Verification Report

**Date:** 2026-11-11 · Cell `v3.1` · Bundle `v2.0.0`

## ROOT CAUSE (of repeated Colab failures)
1. Old cells expected payloads at ZIP root / flat filenames — bundle uses
   organized subdirs (`preflight/ training/ dataset/ evidence/ checkpoint/`).
2. Colab renames duplicate uploads to `…BUNDLE (1).zip` — old exact-match
   checks rejected them.
3. Cell source and notebook drifted (stale pasted cells ran old validation).
4. Checkpoint was Drive-dependent; now bundled + staged safely.

## CHANGES MADE
- Rebuilt bundle: added `checkpoint/checkpoint_final.pt` (verified Run3),
  `cells/` reference copy, manifest v2.0.0 (7 entries).
- Cell v3.1: manifest-driven exact-path extraction, streaming SHA-256,
  symlink+duplicate-path rejection, report-dir write probe, release-identity
  pin (placeholder in zip copy; real sha injected into notebook copy —
  self-reference impossible, documented).
- Notebook: embedded cell = canonical source + injected release identity.

## FILES
| File | Size | SHA-256 |
|---|---|---|
| `exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` | 173,912,644 | `eb693237bfa3ed9d11f33f4fb07f9db8212fbe4addae9a14aefe09a55ce3debe` |
| `docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py` | ~17.5KB | canonical (placeholder release fields) |
| `docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` | — | embedded == source + injected `eb693237…`/`173912644` |

Payload trusted identities (unchanged): preflight `fe2e851b…`/30740 ·
trainzip `f91411e1…`/299476 · corpus `5f8572ed…`/385217021 ·
evidence `0cb7588d…`/2932 · checkpoint `ad515cade…`/106777501.

## VERIFICATION RESULTS
- CHECKPOINT: hash+size verified in bundle; resume state fields present
  (epoch=3, step=1341, opt/sched/scaler/rng) — repo-side FULL_RESUME_VERIFIED
  (bounded smoke); Drive-side staging pending Colab.
- DATASET: streamed hash match; 2000-line JSONL sample clean.
- EVIDENCE: pinned sha/size + field validation logic intact.
- NOTEBOOK/SOURCE: sync verified (injection-aware compare).
- AUTOMATED TESTS: **18/18 PASS** this session + prior suites (filename
  variants, unsafe paths, payload hashes, manifest, trusted ids, release-pin
  logic, no-training).

## STATUS
- LOCAL END-TO-END: **PASS** (real bundle, streaming verify)
- GOOGLE COLAB: **NOT_TESTED** · GOOGLE DRIVE: **NOT_TESTED**
- TRAINING STATUS: **NO-GO** · TRAINING AUTHORIZATION: **FALSE**

## EXACT NEXT USER ACTION
1. Upload `NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` (the NEW 174MB file)
   to Colab or `MyDrive/NexusAI/`.
2. Open `docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` fresh in Colab.
3. Run the upload cell — confirm `[CELL_VERSION] v3.1` and release sha
   `eb693237…` in output.
4. Send me the printed `STATUS:` + report path.
