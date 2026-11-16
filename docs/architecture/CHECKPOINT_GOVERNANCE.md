# NexusAI Checkpoint Governance — Inventory, Warnings & Retention Policy

Date: 2026-11-15 · Status: DOCUMENTATION ONLY (no checkpoint moved/deleted)

## 1. Verified Checkpoint Inventory

| Path | Family | Params | Status |
|---|---|---|---|
| `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt` | Core-01 (`transformer_blocks.*`) | 8,842,560 | **AUTHORITATIVE** — epoch 3, step 1341, SHA `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` |
| `packages/ai-core/models/checkpoints_medium/*` (7 files) | Core-01 family (`transformer_blocks.*`) | ~7M est | older experimental run; resume state unverified |
| `packages/ai-core/models/checkpoints/checkpoint_epoch_*.pt` (5) | Core-01 family, vocab 597, d_model 64, 2 blocks | 185,173 | toy/experimental — NOT Core-01 production |
| `packages/ai-core/data/experimental/phase10/checkpoints/best_model.pt` | **DIFFERENT** (`transformer.layers.*.self_attn.in_proj_weight`, `embedding.weight`, `pos_embedding.weight`) | ~7M est | ⚠️ see §2 |
| `packages/ai-core/data/experimental/phase8/checkpoints/*` | unknown (uninspected) | — | UNKNOWN |

## 2. Phase10 Architecture Warning — VERIFIED FACT

`phase10/checkpoints/best_model.pt` state-dict keys use PyTorch-native
`nn.Transformer` naming (`transformer.layers.N.self_attn.in_proj_weight`,
`embedding.weight`, `pos_embedding.weight`) — a **different model class**
from Core-01's `NexusAICore01` (`token_embedding.*`, `transformer_blocks.*`,
`positional_encoding.pe`, `output_layer.*`).

- It **cannot** `load_state_dict(strict=True)` into `NexusAICore01`.
- It must never be routed/registered as Core-01.
- Correct identity: experimental phase-10 model (likely `data/model_phase10.py`).
- Action required (needs owner approval): label in registry / move to
  `experimental/` quarantine. NOT done — no files moved.

## 3. Retention Policy (proposal — nothing auto-deleted)

For every training run directory keep:
1. `checkpoint_final.pt` (or best-val checkpoint) — REQUIRED
2. Latest resume checkpoint — REQUIRED while run is active
3. Config snapshot + tokenizer path + manifest with SHA-256 — REQUIRED
4. Step checkpoints: keep last 2 + best-val only (rotation)
5. Drive budget: ~110MB per full Core-01 ckpt → ~1GB per 10 checkpoints

Never delete: Run3 `checkpoint_final.pt`, any `PRETRAINING_COMPLETED` final,
any checkpoint referenced by `models/production/current.json`.

## 4. Recovery

Restore = copy ckpt to run dir → strict load (weights_only=False for numpy
RNG state) → verify epoch/step/loss metadata → bounded 1-step smoke test.
See `exports/build_run4_single_upload.py` + Colab cells for the verified flow.
