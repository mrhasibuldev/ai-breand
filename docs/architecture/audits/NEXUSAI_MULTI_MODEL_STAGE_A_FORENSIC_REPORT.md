# NEXUSAI — MULTI-MODEL AI BRAIN · STAGE A FORENSIC REPORT

**Date:** 2026-11-10 · INVESTIGATION ONLY — zero modifications made
**Companion:** `NEXUSAI_COMPLETE_MODEL_INVENTORY.md`

## Verified findings (independent re-check)
| Claim | Verdict | Evidence |
|---|---|---|
| App uses checkpoints_medium | ✅ CONFIRMED | server log + `main.py:271` fallback path |
| ~2.47M params | ✅ CONFIRMED | state-dict = 2,468,928 |
| Core-01 run3 ~8.84M | ✅ CONFIRMED | ckpt config `estimated_parameters: 8842560`; hash `ad515cad…7830` re-verified unchanged |
| Run3 not wired | ✅ CONFIRMED | no `core01` import anywhere in `ml-service/` |
| Production JSON malformed | ✅ CONFIRMED | `models/production/current.json` has `"""` docstring prefix → `json.load` fails "Extra data line 1 col 3" |
| Intent routing bypasses neural | ✅ CONFIRMED | `main.py` ~798-869 deterministic handlers; live 13-test: 8/13 never reached neural |
| Banglish→English | ✅ CONFIRMED | BL1/BL2 detected `language=english` → FALLBACK |
| Fallback always Bengali | ✅ CONFIRMED | all fallback responses Bengali regardless of input lang |
| Neural gibberish | ✅ CONFIRMED | medium model outputs math-fragment noise |

## Compatibility matrix (for integration design)
| Model | Tokenizer | Loads into Core-01 arch? | Loads into Medium arch? | CPU | RAM |
|---|---|---|---|---|---|
| Medium final/best (2.47M) | sp_bpe_8k ✅ | ❌ arch mismatch | ✅ | ✅ | ~30MB |
| Medium epoch×5 (4.9M) | char-74 ❌ | ❌ | ⚠️ only w/ char tokenizer | ✅ | ~58MB |
| Small×5 (185K) | SimpleTokenizer ~1K | ❌ | ❌ different class | ✅ | ~2MB |
| **Core-01 run3 (8.84M)** | sp_bpe_8k ✅ | ✅ (native) | ❌ | ✅ verified | ~107MB ckpt / ~400MB RAM |

## Proposed target architecture (design only)
```
User → API → ml-service /orchestrate
  → language detect (fix: add Banglish/mixed rules)
  → intent classify (multilingual)
  → ModelRouter (new, Python): picks by verified capability metadata
      ├─ core01-run3  → general/multilingual/reasoning (PRIMARY)
      ├─ medium-final → fast fallback (same tokenizer, smaller)
      ├─ deterministic tools → math lookup ONLY (labeled, not neural)
      └─ fallback → language-aware apology (never fake neural)
  → response validation → provenance-tagged reply
```
- Lazy loading: only active model in RAM (~400MB for core01) — fits 8GB.
- No specialist models exist yet — router must NOT pretend they do.

## Files that WOULD need modification (Stage B, pending approval)
- `ml-service/main.py` — model loading, routing, fallbacks (surgical)
- NEW `ml-service/model_registry.py` + `model_router.py` — registry/router
- `models/production/current.json` — fix malformed JSON (or bypass via registry)
- Possibly `core01/inference.py` — expose generate() compatible with service
- Docs: 4 new architecture/audit files + README line

## Risks & rollback
- Risk: core01 inference slower per-token than medium? (8.8M vs 2.5M — still CPU-fine ~40tok/s)
- Risk: core01 output quality still weak (run3 eval) — honest: better than gibberish but not smart yet; Run4 pending
- Rollback: keep `checkpoints_medium` path; registry flag `active_model` switch; git-tracked file backups before edit
- RAM: core01 ~400MB — safe

## Hardware
CPU-only, 8GB — adequate for 1 active model at a time. No GPU needed for inference.

## Implementation sequence (proposed)
1. Backup main.py + current.json
2. Add `model_registry.py` (loads manifest, verifies hash+strict load)
3. Wire `core01/inference.py` into service behind registry
4. Fix language detect (Banglish) + language-aware fallbacks
5. Route neural path to registry-selected model; deterministic tools labeled
6. Re-run same 13 tests + extended suite; compare
7. Document + report

## STOP — awaiting explicit approval for Stage B.
