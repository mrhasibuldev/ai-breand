# Run4 Single-Upload — ZIP Detection Fix Report

**Date:** 2026-11-11

## Root cause
The cell the user executed expected the 4 payloads at the ZIP **root**
(`COLAB_RUN4_PREFLIGHT_CELL.py`, `NEXUSAI_CORE01_RUN4_BUNDLE.zip`,
`corpus_train.jsonl`, `nexusai_run4_resume_smoke_evidence.json`).
The actual bundle stores them under organized subdirectories:
`preflight/`, `training/`, `dataset/`, `evidence/` — verified by listing all
6 archive entries. The ZIP itself is intact (sha `da4fe952…` matched).

The failing script was not the current repo cell — it was an older/different
single-cell script. Fixed by updating
`docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py` (v2) and re-embedding it in
the notebook.

## Fix
- Payloads now discovered by **basename** across the whole archive
  (structure-agnostic), requiring **exactly one** match per file.
- Missing → critical; duplicate/ambiguous → critical.
- Unsafe paths (`..`, absolute, `C:`, backslash traversal, empty segments)
  still rejected before any extraction.
- `manifest.json` cross-checked (declared basenames vs discovered).
- Payload SHA-256 + size still verified against trusted constants — unchanged.
- Staging still goes to canonical paths the preflight/train cells require;
  identical existing files skipped, different content → conflict critical.
- Added post-copy staged-hash re-verification.
- Run3 checkpoint full-hash check retained (not prefix-only).

## Tests: 11/11 PASS
flat root · nested dirs · deep nested · missing rejected · duplicate rejected ·
4 unsafe-path rejections · safe path accepted · real-bundle discovery (4/4).

## Files changed
- `docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py` (v2, 11,880 B)
- `docs/notebooks/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` (re-embedded cell)

## Next step for user
Re-run **Cell 3** of `NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD.ipynb` (or paste the
updated `COLAB_RUN4_SINGLE_UPLOAD_CELL.py`). The uploaded ZIP is already
verified (`da4fe952…`) — it does not need re-upload unless deleted.
