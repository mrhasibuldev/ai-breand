# NexusAI Core-01 Run4 — V7 Final Preflight Audit Report

**Date:** 2026-11-11 · **Checker:** `docs/notebooks/COLAB_RUN4_PREFLIGHT_CELL.py`
**Final checker SHA-256:** `e6dc139091f5661b9064973c392caa2b7fd11029c3c04f4efc3f541ab395e789` · **29,814 bytes**

## 1. V6 status → defects found → fixes

| # | Defect | Root cause | Fix |
|---|---|---|---|
| 1 | Evidence candidates: first match picked; no file identity pin | V6 hashed fields but accepted any same-named JSON with right contents | Pinned `EXPECTED_EVIDENCE_SHA`+`SIZE`; hash every candidate; >1 distinct hash → `ambiguous`→BLOCKED; identical copies → deterministic pick + WARN |
| 2 | Stage-B report failure could leave on-disk JSON/TXT/MD contradicting final `BLOCKED` verdict | Final status recomputed after stageB write but never re-persisted | Stage-C correction write triggered when stageB fails or verdict changes; failure → BLOCKED |
| 3 | (Verified OK) hardcoded success strings | — | Already replaced in V6 by validated evidence loading; now hardened further |

## 2. Evidence authenticity chain (Phase B) — `EVIDENCE_AUTHENTICITY_VERIFIED`

- `eval_reports/nexusai_run4_resume_smoke_evidence.json`: **2,932 B**, sha256 `0cb7588d7f2e7afe2e5250dd9381f3c37e1940428cb060477929bb1338523f32`
- **Byte-identical** to `smoke_result.json` written by the executed script `%TEMP%\run4_resume_smoke.py` (script preserved) — evidence was generated **programmatically from real execution**, not hand-written.
- Preserved artifacts re-verified read-only:
  - `smoke_step.pt`: 106,770,075 B, sha256 `f7236ce3…35e88` == evidence `temp_ckpt_sha` ✅; reload: `epoch=3, step=1342, PRETRAINING_IN_PROGRESS` ✅
  - `run3_copy.pt`: sha == trusted Run3 sha ✅
  - `syn.pt` synthetic ckpt present ✅
- Honest limitation: sha256 pin detects **modification**, not authorship; no signing infra exists — documented, not invented.

## 3. Colab Drive layout (Phase D)

```
/content/drive/MyDrive/NexusAI/
├── checkpoints/core01_english_run3/checkpoint_final.pt   (already required)
├── NEXUSAI_CORE01_RUN4_BUNDLE.zip                          (or under data/run4/)
├── nexusai_run4_resume_smoke_evidence.json   ← NEW: must be uploaded
├── corpus_train.jsonl                                      (or under data/run4/)
└── reports/run4/                                           (auto-created)
```

**Upload instructions (beginner):**
1. In Google Drive, open folder `MyDrive/NexusAI/` (create if missing).
2. Upload `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip` → rename not needed.
3. Upload `eval_reports/nexusai_run4_resume_smoke_evidence.json` → keep exact filename.
4. Upload `corpus_train.jsonl` (385 MB) if not already in `NexusAI/data/run4/`.
5. Verify in Drive web UI that all 3 files show correct names; sizes: ZIP=299,476 B, JSON=2,932 B.
6. If any file missing → checker prints `BLOCKED` with the exact missing item.

## 4. Protection audit (Phase E) — all preserved

ZIP (sha+size+testzip+traversal/abs/drive-letter rejection+required entries+tokenizer+cell sha+AST wiring), checkpoint (sha+size, read-only), corpus (sha+size streaming, strict UTF-8, all counters, 216,193 records), manifest (optional/warning), 3-stage→now 4-stage report persistence (collision-safe, never overwrite, reparse+status consistency, self-hash boundary documented), fail-closed `compute_status`.

## 5. Honest limitations (unchanged)

- `CUDA_FP16_EXECUTION_STATUS = NOT_TESTED` — smoke ran CPU/FP32; GradScaler CUDA path source-verified only.
- `SCHEDULER_BEHAVIOR = PARTIALLY_VERIFIED` — lr-lambda rebuilt with Run4 step budget; `last_epoch` restores correctly.
- Bounded smoke ≠ full Run4 training. `READY FOR USER REVIEW` ≠ training authorization.

## 6. Tests executed (isolated, temp dirs, no training)

| Suite | Result |
|---|---|
| compile() | PASS |
| Evidence pin: valid / modified / two-distinct-ambiguous / identical-copies / missing | 5/5 PASS |
| Evidence field validation (epoch/step/device/precision/status/orig-sha/test-count) | PASS |
| Stage-C trigger logic | PASS |
| Prior smoke suite (15 tests) | previously 15/15 PASS (not re-run — no re-execution authorized) |
| Asset integrity (corpus/ZIP/ckpt/evidence) | all unchanged |

**Counts: 11 passed, 0 failed, 0 skipped, 0 blocked** (this session's new tests; earlier suites stand as recorded).

## 7. Changed files

1. `docs/notebooks/COLAB_RUN4_PREFLIGHT_CELL.py` → sha `e6dc1390…`, 29,814 B
2. This report (new)

No other file modified. No asset touched.

## 8. Confirmations

❌ No training/optimizer step · ❌ No Colab · ❌ No CUDA test · ❌ No upload · ❌ No DB/commit/push · ✅ All original assets hash-unchanged

## 9. Next authorized action

User uploads the 3 files per §3 to Drive, runs the checker cell in Colab, reviews the persisted report, then explicitly decides on Run4 training.

---

# Independent Verification Addendum (V7.1, 2026-11-11)

## Independently re-verified facts
- All trusted hashes recomputed from actual bytes: ZIP ✅, Run3 ckpt ✅, corpus ✅, evidence JSON ✅, training cell inside ZIP ✅, checker (pre-edit) ✅.
- Evidence JSON byte-identical AND deep-equal to preserved `smoke_result.json` (zero field diffs); generator script `%TEMP%\run4_resume_smoke.py` lines 179–180 write it via `json.dump(OUT)` — programmatic, not hand-assembled.
- `smoke_step.pt` re-hashed (`f7236ce3…` match) and reloaded read-only: epoch=3, step=1342, `PRETRAINING_IN_PROGRESS`.
- Checkpoint path consistency: preflight checks `MyDrive/NexusAI/checkpoints/core01_english_run3/checkpoint_final.pt`; train cell `SRC_CKPT` = same path ✅.

## New defect found & fixed (stage-report ambiguity)
Isolated simulation showed: if stage-B **and** stage-C writes both fail, the newest on-disk report is the stage-A "initial" file showing a pre-persistence `READY` verdict — indistinguishable by filename from a final report.
**Fix:** stage tag now embedded in filenames (`RUN4_PREFLIGHT_{stamp}_{stage}.{ext}`) + last-resort `RUN4_PREFLIGHT_BLOCKED_{stamp}.txt` marker when zero report files exist and verdict is BLOCKED.
**Checker after fix:** sha256 `fe2e851bdf257c294297a7793a197e856e973a01581ed7cc76f9b6945fd0f640`, 30,740 B, compile OK.

## Stage simulation results (isolated temp dirs, faithful logic replica)
16/16 PASS — incl. stale-report scenario now mitigated by stage-tagged filenames; in-memory verdict always correct; on-disk final files consistent whenever any write succeeds.

## Trust-boundary limitation (honest)
The evidence pin (`EXPECTED_EVIDENCE_SHA`) lives inside the checker file itself. Anyone who can modify the checker can also change the pin — the pin detects evidence-file tampering, not checker tampering. True independence would require an externally signed manifest; none exists. Documented, not hidden.

## Statuses
- `EVIDENCE_AUTHENTICITY`: VERIFIED (programmatic generation + artifact cross-checks; no cryptographic authorship)
- `CHECKER_INTEGRITY`: PASS (compile + logic audit + simulations)
- `CHECKPOINT_INTEGRITY`: PASS · `CORPUS_INTEGRITY`: PASS · `BUNDLE_INTEGRITY`: PASS
- `REPORT_PERSISTENCE`: PASS with stage-tagging fix
- `DRIVE_LAYOUT_READINESS`: READY (see §3 tree; checkpoint path verified consistent with train cell)
- `CUDA_FP16_EXECUTION`: NOT_TESTED · `SCHEDULER_BEHAVIOR`: PARTIALLY_VERIFIED · `FULL_RUN4_TRAINING`: NOT_EXECUTED

## Release decision: `READY_FOR_USER_REVIEW`
(does NOT authorize Colab execution or training)
