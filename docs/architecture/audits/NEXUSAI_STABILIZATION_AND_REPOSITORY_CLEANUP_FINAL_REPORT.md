# NexusAI Stabilization, Repository Cleanup & GitHub Delivery — Final Report

**Date:** 2026-11-19 · **Branch:** main · **HEAD:** `2c475ad` (= origin/main at audit time)

## 1. Initial repository status
- 9 mission-modified files + 7 new files (Phase 1 work, uncommitted).
- 54 files staged for untracking (Phase 3 cleanup, awaiting commit approval).
- Untracked local assets preserved: corpora (raw_bangla 1.2G, cleaned_bangla 988M), exports zips, backups/, data/.venv.

## 2. Phase 1 G9 — root cause & resolution
**Root cause:** host RAM exhaustion (8.5GB). Next.js dev + tsx API + python ML + vitest + IDE/browsers cannot coexist; "Zone Allocation failed" was Windows commit-limit, not an app bug. Web starts cleanly in 5.1s when run without concurrent heavy jobs.
**Resolution:** no code change needed — verified all services individually and browser-verified via Playwright/system Chrome.
**Browser verification (real, headless Chrome):**
- Homepage→chat navigation, guest mode: PASS
- Identity (Bengali) → `Deterministic` badge: PASS
- `১৫টি আম…` → `15 ÷ 3 = 5` + `Deterministic tool` badge: PASS
- Candle riddle → honest fallback + `Fallback` badge: PASS
- `What is AI?` → fluent answer + `Neural · nexus-core-04` badge: PASS
- Console errors: only benign 401 guest-session probes.
- Mobile/desktop layouts, sidebar, profile, settings, theme: NOT EXERCISED (would need interactive session; no evidence of breakage — typecheck clean, no layout code touched).

## 3. Cleanup audit & actions (user-approved: tracked files only)

### Removed from git tracking (local files preserved; recoverable via history)
| Item | Count | Size | Reason |
|---|---|---|---|
| `checkpoints_medium/checkpoint_epoch_*.pt` | 5 | ~290MB | registry-documented tokenizer-incompatible legacy; excluded from serving |
| `checkpoints/checkpoint_epoch_*.pt` | 5 | ~11MB | same exclusion note |
| `__pycache__/*.pyc` | 34 | <1MB | generated artifacts (already gitignored) |
| `data/packages/` nested duplicate | 5 files | 22MB | orphaned copy of `data/collected` (verified identical/near-identical, zero references) |
| `exports/*COLAB_TRAINING_BUNDLE*.zip` | 2 | ~20MB | superseded training bundles; build scripts retained |
| `backups/core01_repair/*.bak` | 3 | <1MB | stale pre-repair backups |

**Total untracked: 54 files.** Nothing deleted from disk; all recoverable via git history + `nexusai_backup_20261118_postfix` + `nexusai_phase1_backup_20261119`.

### Retained (with reason)
- All registered checkpoints (core-01..04, medium final) — REQUIRED, hash-gated.
- `raw_bangla/` 1.2G, `cleaned_bangla/` 988M — training corpora, user decision needed before any removal.
- `exports/*.zip` untracked RUN4 bundles (3×166MB) — Colab delivery artifacts; regenerable via `build_*.py` but kept per user scope.
- `data/.venv` 271MB — regenerable but kept per user scope.
- `backups/` dirs — recovery backups.
- All exports scripts/manifests/docs — referenced by training guides.

## 4. Tests & verification (post-cleanup)
- `test_phase1_stabilization.py`: 44/44 PASS
- `test_generation_repairs.py`: 13/13 PASS
- Live `/orchestrate`: DETERMINISTIC_HANDLER identity response intact
- api+web `tsc --noEmit`: clean (earlier)
- `pnpm test`: 166 failed / 37 passed — identical pre-existing baseline (env/domain issues, unrelated)

## 5. GitHub delivery readiness
- Staged deletions: 54 (untracking only — no content lost).
- Mission files to commit: 9 modified + 7 new (Phase 1 fixes, tests, docs, eval JSONs).
- No secrets in diff; `.env` untouched/ignored; `.gitignore` already covers `*.pt`, `*.pyc`, `__pycache__/`.
- LFS: core-01 checkpoint is LFS-tracked, unchanged.
- **Awaiting explicit approval to commit + push.**

## 6. Remaining problems
- Neural quality unchanged (documented honestly — gibberish now falls back cleanly).
- vitest suite: 166 pre-existing failures need a dedicated test-infra mission.
- Authenticated chat path untested live (guest path fully verified).
- Host RAM limits concurrent dev services — recommend running `pnpm dev` subsets, not all at once, on this machine.
