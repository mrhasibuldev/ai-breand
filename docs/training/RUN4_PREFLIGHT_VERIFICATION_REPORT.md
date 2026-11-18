# Run4 Preflight Verification Report

**Date:** 2026-11-11 · Validation-only · NO training.

## What was verified (local, evidence-backed)
- Outer ZIP identity: 173,912,644 B / `eb693237…debe` — user-confirmed PASS on Colab upload (size+sha+release identity all PASS per user report; internal payload verification pending full cell run)
- Manifest v2.0.0: 7 entries, all payload hashes verified by streaming e2e locally
- Secure extraction logic: traversal/absolute/drive-letter/backslash/`..`/empty-segment rejection, symlink rejection, duplicate-path rejection, manifest-authorized paths only, streaming writes, temp staging, no-overwrite conflicts
- Checkpoint: hash+size verified; resume fields present (epoch=3, step=1341, opt/sched/scaler/rng); bounded smoke proved load→step→save→reload
- Dataset: streamed sha match; 216,193 records; 0 malformed/empty in prior full audit; 2000-line sample clean this session
- Evidence JSON: pinned sha/size + field validation; provenance = programmatic smoke-test output (documented limitation: sha-pin ≠ authorship proof)
- Notebook↔source sync: embedded cell == canonical + documented release-identity injection only
- Report persistence: 3-stage + stage-C correction + stage-tagged filenames + BLOCKED marker fallback

## NOT TESTED (requires Colab)
- Real Drive mount/staging, GPU detection, FP16/GradScaler path, forward/backward smoke on GPU, save/reload on Drive, full preflight cell run, training, evaluation, CPU inference of Run4 output.

## Blocking issues before training
None technical remaining locally. Required user actions:
1. Run upload cell v3.1 in Colab → confirm `[CELL_VERSION] v3.1` + release sha.
2. Run preflight cell → review `reports/run4/` JSON.
3. Only then, explicit `START NEXUSAI CORE-01 TRAINING` authorization.

## Data-quality caveat (see forensic audit)
Corpus supports language modeling; conversational goals (creator=Hasibul,
BN/EN QA consistency, Banglish, affection chat) are weakly covered — plan a
small instruction-tuning phase after Run4 for those behaviors.
