# NEXUSAI — COMPLETE MODEL INVENTORY

**Date:** 2026-11-10 · All hashes/sizes measured locally · READ-ONLY

## Summary counts
- **Distinct neural architectures: 3** (SmallTransformer, MediumTransformer, Core-01)
- **Trained checkpoint files: 17** (5 small + 7 medium-family + 5 core01-run + run3 final — see table)
- **Model versions/runs: 4** (small-v1, medium-phase10, core01-run1/2/3 [run4 not trained])
- **Untrained initializations: several** (config-only, no ckpt)
- **Deterministic handlers: 1 system** (intent-based canned replies in ml-service)
- **External AI dependencies: 0** for inference
- **Tokenizers: 6+** (sp_bpe_8k active; sp_bpe_4k, phase7 8k/16k/32k bpe+unigram, SimpleTokenizer char-level, multilingual_tokenizer.json)

## Checkpoint inventory (verified by torch.load)

| File | Arch | Params | Vocab | Ckpt config | SHA-256 (prefix) | Status |
|---|---|---|---|---|---|---|
| `models/checkpoints/checkpoint_epoch_{1-5}.pt` | SmallTransformer | 185,173 | ~1000 SimpleTokenizer | 2L/64d/2H | b828be60… | trained, disconnected, fallback-only |
| `models/checkpoints_medium/checkpoint_epoch_{1-5}.pt` | MediumTransformer | 4,907,594 | **74 (char-level)** | old exp | 3b775bd8… | trained, DIFFERENT tokenizer — incompatible w/ sp_bpe_8k |
| `models/checkpoints_medium/best_model.pt` | MediumTransformer | 2,468,928 | 8000 sp_bpe_8k | 2L/128d/2H/512ffn, len128 | b9c2dd94… | trained, duplicate of final |
| `models/checkpoints_medium/final_model.pt` ⭐ACTIVE | MediumTransformer | 2,468,928 | 8000 sp_bpe_8k | same | **4f592af9…** | **ACTIVE — serving users** |
| `models/checkpoints_core01_run3/checkpoint_final.pt` | Core-01 | 8,842,560 (config) / 8,973,632 (state-dict incl. buffers) | 8000 sp_bpe_8k | 6L/256d/8H/1024ffn, len512 | **ad515cad…7830** ✅ | trained run3, **NOT connected** |

Note: run3 ckpt `config.model_status` still says "UNTRAINED" — stale metadata field, weights ARE trained (loss 4.43/4.22, step 1341).

## Architecture comparison
| | SmallTransformer | MediumTransformer | Core-01 |
|---|---|---|---|
| Code | `neural/small_transformer.py` | `neural/medium_transformer.py` | `core01/transformer.py` |
| Params | 185K | 2.47M | 8.84M |
| Config (active ckpt) | 2L/64/2H | 2L/128/2H/512 | 6L/256/8H/1024 |
| Context | 128 | 128 | 512 |
| Tokenizer | SimpleTokenizer ~1K | sp_bpe_8k (final/best) or char-74 (epoch ckpts) | sp_bpe_8k |
| Trained on | Phase-10 small set | Phase 10 (1,812 samples) | english_first 7.43M tokens, 3 epochs |
| CPU inference | yes | yes (active) | yes (verified 42 tok/s) |
| In app? | fallback only | **YES — active** | **NO** |

## Inference implementations
- `ml-service/main.py` — production path (orchestrate → intent → deterministic/neural → fallback)
- `core01/inference.py` — Core-01 engine (used by eval scripts only)
- `inference/generator.py` — legacy TextGenerator
- TS stubs: `model-router/index.ts`, `model-registry/index.ts` — **not wired to Python service**

## Deterministic handlers
- Intent router in `main.py` (~lines 760-870): GREETING/IDENTITY/CAPABILITY/THANKS/HELP/FAREWELL → canned replies; GENERAL_QUESTION/unknown → neural; failures → Bengali fallback.

## Answers to key questions
- **How many architectures?** 3
- **How many trained checkpoints?** 17 files / 4 training runs
- **Which serves users?** `checkpoints_medium/final_model.pt` (MediumTransformer 2.47M)
- **Disconnected but available?** Core-01 run3 (best quality potential), small ckpts (fallback), medium epoch ckpts (wrong tokenizer — incompatible)
