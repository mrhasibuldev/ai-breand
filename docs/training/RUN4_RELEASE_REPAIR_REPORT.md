# RUN4 Release Repair — Forensic Audit & Verification Report

**Date:** 2026-11-13 · No training · No commit/push.

## A. Initial defects found
| ID | Defect | Root cause | Severity |
|---|---|---|---|
| D1 | Upload Cell `EXPECTED` pinned preflight sha `fe2e851b…` but actual file was `7b76b6d7…` | Preflight cell was updated (inner-zip/train-cell pins) but upload cell's trusted hash was not re-synced → release would BLOCK at Colab | **CRITICAL** |
| D2 | Manual hash pinning across 4 artifacts (upload cell, preflight cell, manifest, notebook) — error-prone | No single build step | HIGH |

## B. Repairs
- `docs/notebooks/COLAB_RUN4_SINGLE_UPLOAD_CELL.py`: preflight pin → `7b76b6d7…` (size 30740 unchanged)
- NEW `exports/build_run4_single_upload.py`: reproducible builder — hashes all payloads, writes manifest, verifies zip before atomic promote, prints release identity
- Rebuilt outer ZIP via script; notebook re-embedded with new release identity (placeholder injection verified)

## C. Verification — all executed, evidence recorded
| Test | Result |
|---|---|
| Outer ZIP sha/size vs release identity | PASS (`8cf7d6b9…`, 173,913,186) |
| ZIP testzip / safe paths / dups / symlinks | PASS |
| Manifest v2.1.0, 7 entries, all payload sha+size re-hashed | PASS |
| Upload-cell EXPECTED (5 entries) vs manifest resolution+pins | PASS |
| Inner ZIP integrity + zero-step guard + EPOCHS=5 present | PASS |
| Preflight pins (inner zip `e0f9f465…`, train cell `bcea286d…`) | PASS |
| Notebook embedded == injected source, all cells compile | PASS |
| Run3 checkpoint byte-unchanged (sha re-verified `ad515cade…`) | PASS |
| Colab/Drive/GPU runtime | **NOT RUN** (requires user) |

## D. Final artifact identities
- `exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` — **173,913,186 B** — **`8cf7d6b9dd5f5cc4702c510bf4fb1155a58101e198b910be2e57e49fe54b29cc`**
- Inner `exports/NEXUSAI_CORE01_RUN4_BUNDLE_v2.zip` — 300,135 B — `e0f9f465…97d3a`
- Payloads: corpus `5f8572ed…`/385,217,021 · ckpt `ad515cade…`/106,777,501 · evidence `0cb7588d…`/2,932 · preflight `7b76b6d7…`/30,740 · upload cell `dcd6cae1…`/19,018

## E. Checkpoint safety
Run3 `checkpoint_final.pt` sha before == after: `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` — byte-identical, read-only throughout.

## F. Training readiness: **READY FOR COLAB UPLOAD**
(next gates: Colab preflight → GPU smoke → explicit `START NEXUSAI CORE-01 TRAINING`)

## G. User action (Bengali)
নতুন ZIP `8cf7d6b9…` (পুরনো `959ac4f0…` ও `eb693237…` — দুটোই 사용 করবেন না) Colab-এ upload করে notebook-এ Cell 2→4→6→6b→8→10→12→14→16 run করুন, output পাঠান।

## H. Git status
Baseline `64d05e9` unchanged · modified/untracked working files only · **no commit, no push**.
