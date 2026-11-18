# Checkpoint Recovery Audit (2026-11-16)

## Authoritative (FOUND + VERIFIED)
`packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt`
- 106,777,501 B · SHA-256 `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830`
- ep3/step1341 · PRETRAINING_COMPLETED · full resume state · Core-01 family
- Now retrievable from GitHub main via Git LFS (fresh-clone verified)

## Other local checkpoints
- `checkpoints_medium/*` (~29MB) — Core-01 family keys, older run, resume unverified
- `checkpoints/*` epoch1-5 (~2.2MB) — toy model (vocab597/d64/2L/185K params)
- `phase10/best_model.pt` (~29.6MB) — DIFFERENT arch (`self_attn.in_proj_weight`), incompatible
- `phase8/*` — uninspected

## Drive-only (NOT VERIFIED — inaccessible from this machine)
`NexusAI/checkpoints/core01_english{,_run2,_run3}/checkpoint_step*.pt` +
`checkpoint_last.pt` + `checkpoint_final.pt` (~101.83MB each, reported).
Cannot confirm existence/identity without Drive access. If found on Drive,
verify SHA-256 + state-dict family before use; do NOT assume they equal the
canonical Run3 checkpoint (the canonical one is `ad515cade…`).

## Best verified recovery point
**Run3 `checkpoint_final.pt` via Git LFS on main** — the only fully verified
resume-capable checkpoint.
