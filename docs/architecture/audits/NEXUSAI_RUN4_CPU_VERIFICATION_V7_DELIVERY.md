# NexusAI Run4 CPU Verification v7 — Delivery Report

**Date:** 2026-11-17 · Phase B+C authorized · cell-only changes, zero repo/model/package modifications

## Deliverable
`docs/notebooks/NEXUSAI_RUN4_CPU_VERIFICATION_v7.py` — 483 lines, self-contained,
syntax-verified, zero `.cuda()`/`weights_only=False`/`files.upload`/external APIs.

## Seven approved corrections — all implemented
| # | correction | implementation |
|---|---|---|
| 1 | Dual numpy allowlist | `numpy._core` + `numpy.core` multiarray, per-attr getattr, +np.dtype+RandomState+Generator → verified 5 types, `add_safe_globals` OK locally |
| 2 | Reports local-only | `/content/NEXUSAI_RUN4_CPU_AUDIT/` (4 files) + write-permission preflight; Drive copy optional try/except |
| 3 | Work dir | `/content/NEXUSAI_RUN4_CPU_VERIFY_WORK/` for extraction |
| 4 | Post-test re-hash | ckpt+tok re-hashed after generation, drift reported |
| 5 | Tokenizer round-trips | en/bn/banglish encode→decode + UNK counts |
| 6 | Generated IDs | engine returns `generated_ids`; decode wrapper fallback capture |
| 7 | Guarded config | `ck.get("config")` + isinstance check + `ModelStatus(root)` validated |

Preserved: hash-gated ZIP extract + traversal rejection, transformer sha gate
(`c8b25687…`), `strict=True`, `weights_only=True` only, CPU-only proof,
forward-call neural instrumentation, inference_mode, idempotent working-copy
patches (never touches ZIP/Drive originals).

## Local verification performed
- `py_compile`: PASS
- allowlist collection + `add_safe_globals`: PASS (5 types)
- forbidden-call scan: 0 hits
- Patch patterns verified against actual packaged sources (model_config
  one-liner + inference.py marker bounds)

## NOT verified (requires Colab execution)
- Actual Run4 CPU load/generation — Drive-only checkpoint
- End-to-end cell run — never executed yet

## Execution instructions
1. Colab → new notebook → **Runtime: CPU** (GPU off OK)
2. Paste **entire** `NEXUSAI_RUN4_CPU_VERIFICATION_v7.py` → Run (~4-6 min)
3. Reports auto-written to `/content/NEXUSAI_RUN4_CPU_AUDIT/`:
   - `NEXUSAI_RUN4_CPU_VERIFICATION.json`
   - `NEXUSAI_RUN4_CPU_VERIFICATION_REPORT.md`
   - `NEXUSAI_RUN4_CPU_GENERATION_OUTPUTS.json`
   - `NEXUSAI_RUN4_CPU_FORENSIC_AUDIT.md`
4. Download: files panel → `NEXUSAI_RUN4_CPU_AUDIT/` or
   `files.download('/content/NEXUSAI_RUN4_CPU_AUDIT/NEXUSAI_RUN4_CPU_VERIFICATION.json')`
5. Paste console output back for quality analysis.

## Limitations
- Heuristic scores mechanical only — semantic quality needs human review
- weights_only=True needs narrow numpy allowlist (ckpt RNG state) — justified,
  self-produced artifact; `weights_only=False` never used
- Optional Drive copy may fail on read-only mount — by design, not required

## Production-readiness assessment
Pipeline reliability: HIGH (all known failure modes addressed).
Model quality: UNVERIFIED until cell executes. Run4 promotion still gated
on eval evidence.
