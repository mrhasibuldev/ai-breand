# NexusAI Run4 — Generation Failure Forensic Report

**Date:** 2026-11-17 · READ-ONLY Phase A · no code modified

## Executive summary
Generation fails at `inference.py:87` with `AttributeError: 'str' object has no attribute 'value'`.
**Root cause confirmed:** checkpoint `config.model_status` is the **string** `"UNTRAINED"`.
`NexusAICore01Config.from_dict()` passes it through raw (no Enum conversion).
The status guard at line 78-83 correctly detects UNTRAINED via `str()`, but the
early-return dict at **lines 87-88 still calls `self.config.model_status.value`**
→ crash before the warning response can be returned.
Two stacked issues: (1) type-unsafe deserialization, (2) unguarded `.value`
in the guard's own return path.

## Confirmed findings (source-verified)

### 1. ModelStatus / config (`models/nexusai_core_01/config/model_config.py`)
- `ModelStatus(Enum)` line 12; `model_status: ModelStatus = ModelStatus.UNTRAINED` line 44.
- `to_dict()` line 196 serializes `.value` → **string** in checkpoint config.
- `from_dict()` line 235: `cls(**{k:v ...})` — **no type conversion**; string passes straight into the dataclass field. CONFIRMED BUG SOURCE.
- `__post_init__`/`_validate_config` (108-135): validates dims/tokens only — does NOT coerce or validate `model_status` type.

### 2. InferenceEngine (`core01/inference.py`)
- `__init__` (30-49): stores `self.config = config` as passed — no normalization.
- `generate()` lines 78-89: `status_value` handles str-or-Enum correctly, BUT lines 87-88 build the early-return dict with `self.config.model_status.value` → **AttributeError when status is str**.
- Guard semantics: returns empty + warning for UNTRAINED/RANDOMLY_INITIALIZED — **intentional safety guard, must NOT be removed**.
- `load_checkpoint()` line ~138: `self.config.model_status = ModelStatus(checkpoint.model_status)` — converts top-level ckpt status correctly (but our cell bypasses this path).

### 3. Checkpoint metadata inconsistency
- ckpt root `model_status = "PRETRAINING_COMPLETED"` (set by training engine at completion).
- ckpt `config.model_status = "UNTRAINED"` — **stale**: config was serialized before/during early training and never updated. Root status is authoritative (written post-training); config value is a serialization artifact, NOT evidence the model is untrained.
- Evidence: step 9213, optimizer state, loss 3.18/2.92, strict load PASS — model IS trained.

### 4. Why Colab hit it but local didn't
Local tests constructed config via driver path (Enum) or bypassed status guard.
The Colab cell's `NexusAICore01Config(**cd)` received raw string (or an earlier cell version skipped conversion) → str reached `.value`.

## Generation pipeline (post-guard, verified clean)
encode(add_special_tokens=False) → prepend BOS, no EOS → max_len trim →
model.generate → logits → greedy/sampling → decode generated IDs only →
`torch.inference_mode()`. No fallback/handlers/external calls.

## Additional potential issues (hypotheses, not yet hit)
- After Enum fix, UNTRAINED status → guard returns empty+warning (by design).
  To generate, config status must reflect ckpt root `PRETRAINING_COMPLETED`
  — legitimate: it's the checkpoint's own metadata, not a relabel.
- `load_checkpoint()` uses `CheckpointManager`/`checkpoint.model_status` —
  different path than direct `ck["model_state_dict"]`; not used by cell.

## Recommended minimal fixes (AWAITING APPROVAL)
| # | file | change | necessity |
|---|---|---|---|
| 1 | `model_config.py::from_dict` | coerce `model_status` str→ModelStatus, raise on invalid | fixes deserialization at source |
| 2 | `inference.py:87-88` | use `status_value` instead of `.value` in return dict | fixes crash in guard path |
| 3 | cell/config build | set `model_status` from ckpt **root** status (authoritative) | enables generation honestly |
Weights/architecture/tokenizer/checkpoint: **NO changes needed. No retraining.**

## Decision: **READY FOR MINIMAL FIX**
3 small, source-consistent changes; checkpoint untouched (sha stays `761a5b14…`).
Awaiting explicit approval to implement Phase B.
