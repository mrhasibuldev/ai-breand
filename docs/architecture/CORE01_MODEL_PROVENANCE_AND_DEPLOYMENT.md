# Core-01 Provenance & Deployment — 2026-11-17

## Active model (verified live)
`nexus-core-01` → `models/checkpoints_core01_run3/checkpoint_final.pt`
sha `ad515cade…7830` · CPU · lazy-load once · resident.

## Provenance fields now emitted per neural response
model_id, checkpoint(+path+sha256), tokenizer(+sha256), vocab_size,
engine, load_s, neural_generation_executed, generation_status(ok/empty).
Implemented in `model_registry.generate()` — additive only, verified live.

## Rollback
Run3 is untouched and remains the only registered core01 checkpoint.
To revert provenance patch: `backups/20261117_provenance/model_registry.py.orig`.

## Run4 integration checklist (when Drive access available)
1. sha256 == 761a5b14… → 2. copy to `models/checkpoints_core01_run4/` →
3. verify copy hash → 4. add registry entry `nexus-core-01-run4` (new id,
keep run3) → 5. benchmark → 6. only then repoint PRIMARY (approval).
