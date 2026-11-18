# NEXUSAI MODEL REGISTRY GUIDE

## How it works
`packages/ai-core/ml-service/model_registry.py` → `MODEL_DEFS` dict + `ModelRegistry` class.

Each entry: model_id, architecture, checkpoint path, sha256, params, config, tokenizer, vocab, max_len, languages, ram estimate, status, training provenance, known limits, loader type.

## Status lifecycle
`available → validated → loaded → active` | `disabled | incompatible | failed`
A file on disk is NOT ready — `validate()` checks existence + SHA-256 + tokenizer; `load()` does strict state-dict.

## Verified
- nexus-core-01: validate PASS, load 1.1s, RAM ~354MB total, generates text
- nexus-medium: validate PASS (fallback only)

## Adding a new model (e.g. Core-02)
1. Add entry to MODEL_DEFS with real checkpoint path + measured sha256 + config.
2. Choose loader: "core01" (same arch) or add new loader branch.
3. `registry.validate(id)` must pass before `load()`.
4. Router picks via capability metadata — no app rewrite needed.

## Incompatible models (do NOT register)
- `checkpoints/checkpoint_epoch_*` — SimpleTokenizer ~1K vocab, different wrapper
- `checkpoints_medium/checkpoint_epoch_*` — char-level vocab 74 tokenizer
