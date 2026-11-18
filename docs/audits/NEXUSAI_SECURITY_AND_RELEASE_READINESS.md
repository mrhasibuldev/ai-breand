# NexusAI Security & Release Readiness
Date: 2026-11-17 · READ-ONLY

## Secrets scan
- `.env`, `.env.local` → **git-ignored** (check-ignore PASS); only `.env.example` tracked
- no hardcoded keys found in scanned py/ts/mjs (grep sweep)
- `hybrid-test-cookies.txt` at root — session cookies, EXCLUDE from release
- database URLs in .env only (ignored) ✓

## Release blockers
| item | action |
|---|---|
| no LICENSE | add before publish |
| ~8 modified + 100+ untracked files | triage: include docs/audits+code, exclude junk |
| node_modules/, dist/, .venv/, __pycache__ | ensure .gitignore covers |
| checkpoints/*.pt binaries | decide: exclude or LFS (Run3 already LFS) |
| eval_reports/, logs/, backups/ | exclude or trim |
| data/.venv (huge) | MUST exclude — verify gitignore |
| private datasets (data/) | review before publish — provenance unclear for some |

## Model/data provenance
- Core-01 weights: self-trained ✓ publishable (own IP)
- tokenizer: self-trained SentencePiece ✓
- datasets: mixed sources (Wikipedia MIT, Sangraha, TinyStories…) — LICENSE REVIEW REQUIRED per-source before redistribution
- sft_v1/v2: self-generated templates ✓

## Verdict: NOT READY — needs allowlist + LICENSE + dataset license review + triage commit.
