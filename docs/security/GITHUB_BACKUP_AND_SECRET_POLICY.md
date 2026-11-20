# NexusAI — GitHub Backup & Secret Policy

**Purpose:** define what may and may not enter the GitHub repository so the repo remains a safe, complete backup of the project.

## Never committed
- `.env`, `.env.local`, `.env.production`, `.env.development` and any file containing real credentials
- Neon `DATABASE_URL` with password, `COOKIE_SECRET` real values, API keys, tokens, private keys
- Production database dumps, private user data, session/browser data
- Local virtualenvs (`.venv/`), `node_modules/`, caches (`__pycache__`, `.next/`)
- Local agent/tool configuration containing credentials

## Committed intentionally
- `.env.example` — placeholders only
- Source code, tests, docs, audit reports, eval JSONs
- Tokenizer assets (`sp_bpe_8k.*`)
- Model checkpoints via **Git LFS** (`checkpoints_core01_run3`, `checkpoints_core02_sft_v2`, `checkpoints_core03_sft_v2`, `checkpoints_core04_sft_v3`); `checkpoints_medium/final_model.pt` as regular git
- Small tracked export ZIPs (pre-existing)

## Local-only (preserved, not pushed)
- `exports/NEXUSAI_*SINGLE_UPLOAD_BUNDLE*.zip`, `NEXUSAI_UNIVERSAL_TRAINING_PACKAGE.zip` (~166 MB each) — reproducible training exports; contents already in repo/LFS
- `packages/ai-core/data/raw_bangla/` (~1.2 GB), `cleaned_bangla/` (~1 GB), `data/packages/` — raw training corpora; regenerable via tracked acquisition scripts
- `backups/` — dated local safety snapshots (git history already preserves source)

## Verification routine (run before every push)
1. `git status` — review every staged path explicitly (never `git add .`)
2. Secret scan of staged diff (keys, tokens, `postgresql://` with password, `sk-`, private key blocks)
3. Confirm no `.env*` real files staged
4. Confirm LFS pointers (not raw binaries) for large `.pt` files
5. `git lfs ls-files` — verify all required checkpoints listed

## If a secret is ever pushed
Do NOT force-push to hide it. Report immediately; rotate the credential (Neon password, cookie secret) and then decide on history handling with explicit approval.
