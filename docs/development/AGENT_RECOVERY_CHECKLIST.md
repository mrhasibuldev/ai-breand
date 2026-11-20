# Agent Removal & Recovery Checklist

**Scenario:** removing the local coding agent (Devin/Windsurf) and reinstalling later. The NexusAI **project folder must NOT be deleted** — only the agent application.

## What GitHub already contains (verified pushed @ c4761bc+)
- All application source: `apps/web`, `apps/api`, `apps/worker`, `packages/*`
- ML service + model registry/router/safety guard (`packages/ai-core/ml-service`)
- Training/inference scripts, evaluation suites, tests
- All 5 model checkpoints: 4 via **Git LFS** + medium via git
- Tokenizer (`sp_bpe_8k`), manifests, lockfiles, configs, `.env.example`
- Full documentation tree + audit reports + eval evidence

## What exists ONLY locally (not on GitHub — by design)
| Item | Needed to recover? | Recovery path |
|---|---|---|
| `.env` (real secrets) | yes for running services | recreate from `.env.example` + your Neon credentials |
| `exports/*.zip` training bundles (~500MB total) | optional | reproducible from tracked scripts + LFS checkpoint |
| `data/raw_bangla`, `cleaned_bangla`, `data/packages` (~2.2GB) | only for retraining | re-run tracked `acquire_*.py` scripts |
| `backups/` snapshots | no | git history supersedes |

## Verdict: SAFE TO REMOVE CODING AGENT — conditionally
Safe **only if** you also keep the local project folder `C:\Users\Nusaiba\Desktop\Ai Breand` intact (it holds `.env`, datasets, ZIPs, and the running dev environment). Deleting the agent app alone loses nothing — GitHub has the full source.

If you ever lose the local folder entirely: clone repo + `git lfs pull` + recreate `.env` + re-acquire datasets = full reconstruction path (training corpora take time to re-download).
