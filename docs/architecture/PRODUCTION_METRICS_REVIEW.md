# Production Metrics Review — `models/production/current.json`

Date: 2026-11-15 · READ-ONLY review — **no production config modified**

## Verified mismatches

| Field | current.json | Verified evidence | Verdict |
|---|---|---|---|
| `parameters` | 8,842,560 | `model.count_parameters()` = 8,842,560 | ✅ correct |
| `checkpoint_path` | `checkpoints_core01_run3/checkpoint_final.pt` | exists, SHA `ad515cade…` | ✅ correct |
| `perplexity` | **2.83** | Run3 val_loss = **4.2169** → ppl ≈ e^4.2169 ≈ **67.8** | ❌ STALE/FABRICATED |
| `dataset_samples` | **1812** | Run3-era english_first subset; Run4 corpus = 216,193 records but **untrained** | ⚠️ MISLEADING |
| `dataset` | `english_first+run4-corpus(prepared)` | run4 corpus was *prepared*, never trained on | ⚠️ MISLEADING |
| `trained_at` | 2026-11-09 | ckpt timestamp 2026-11-08T20:50:13 | ~minor |
| neural quality | (implied good) | v1 benchmark: lang_match 0.5, incoherent outputs | ❌ OVERSTATED |

## Proposed correction (AWAITING APPROVAL — not applied)

```json
{
  "perplexity": 67.8,
  "perplexity_note": "derived from val_loss 4.2169 (e^loss); measured on Run3 val split",
  "dataset": "english_first (Run3 training set)",
  "dataset_samples": 1812,
  "dataset_note": "run4 corpus (216,193 records) prepared but NOT yet trained — see Run4 release v2.3.0",
  "quality_note": "neural_only benchmark v1 (13 prompts): lang_match 0.50, outputs weak/incoherent — undertrained, SFT pending"
}
```

## Affected files
- `packages/ai-core/models/production/current.json` (only file found declaring these metrics)
- `packages/ai-core/ml-service/model_registry.py` may surface them — verify before change
