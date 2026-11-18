# NexusAI Run4 CPU Verification Pipeline — Phase A Forensic Audit

**Date:** 2026-11-17 · READ-ONLY · no files modified

## Issues identified (root causes)

### 1. Read-only Drive error (historical cells) — RESOLVED in v6
Old cells wrote reports to `/content/drive/MyDrive/NEXUSAI_RUN4_AUDIT/` →
`OSError Errno 30` when Drive mounted read-only.
**v6 status:** reports go to `/content/nexusai_cpu_readiness/` (local) — FIXED.
**Remaining gap:** no explicit write-permission preflight; add `os.access` test.

### 2. Packaged inference.py is OLD version — HANDLED but fragile
ZIP contains pre-fix `generate()` (terminal-EOS bug, fragile decode,
no inference_mode, 3× `.value` crash sites). v6 replaces whole method via
marker-bounded patch (`def generate(` → `def load_checkpoint`).
**Risk:** if markers absent → clean STOP (verified logic). Acceptable.

### 3. NumPy allowlist path compatibility — MINOR RISK
Cell allowlists `np.core.multiarray._reconstruct`; torch 2.14 error
references `numpy._core.*`. Both resolve on numpy 2.5.4 locally, but
Colab numpy version may differ → add BOTH paths defensively.

### 4. Missing post-test hash re-verification — GAP
Spec requires ckpt/tok hashes AFTER testing; v6 hashes only before.
**Fix:** re-hash at end, compare, report drift (expect identical).

### 5. Missing tokenizer round-trip tests — GAP
Spec requires en/bn/banglish encode/decode checks; v6 only reports
vocab/special IDs. **Fix:** add 3 round-trip probes with UNK counts.

### 6. Generated token IDs not captured — GAP (minor)
Engine doesn't return IDs; v6 records `None`. **Fix:** wrap `tok.decode`
to capture last decoded ID list (read-only instrumentation).

### 7. Unguarded `ck["config"]` access — MINOR
If ckpt lacks `config` key → raw KeyError, not clean BLOCKED report.
**Fix:** `.get` + explicit stop.

### 8. `PKG_PREFERRED` staleness — LOW
`/content/NEXUSAI_RUN4_RECOVERY_WORK/...` may hold an older extract;
transformer sha-gate + idempotent patch make this safe. Acceptable.

### 9. `os.walk("/content")` package search — LOW
Could match unrelated MANIFEST dirs; transformer sha + structure checks
contain the risk. Acceptable; prefer exact preferred path first (already).

## Verified-clean items
- Syntax: v6 compiles (`py_compile` PASS)
- No `.cuda()`/`weights_only=False`/`files.upload`/external APIs
- Drive mount: conditional on `isdir` — no remount error
- ZIP extraction: hash-gated + path-traversal rejection
- Strict load `strict=True`, CPU device proof, `inference_mode`
- forward-call instrumentation proves neural path
- Local report dir already `/content/...` (no Drive write required)

## Proposed corrections (cell-only, no repo changes)
1. Write-permission preflight on `/content/NEXUSAI_RUN4_CPU_AUDIT/` (rename dir per spec)
2. Dual numpy allowlist (`np.core` + `np._core`)
3. Post-test ckpt/tok re-hash + drift check
4. Tokenizer round-trip probes (en/bn/banglish + UNK counts)
5. Generated-ID capture via decode wrapper
6. `ck.get("config")` guarded access
7. Optional Drive report copy (try/except, never required)

**All fixes are cell-internal — ZERO repository/source/checkpoint changes.**

PHASE A COMPLETE — WAITING FOR USER APPROVAL
