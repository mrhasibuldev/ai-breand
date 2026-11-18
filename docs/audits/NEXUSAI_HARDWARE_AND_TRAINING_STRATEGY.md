# NexusAI Hardware & Training Strategy
Date: 2026-11-17

## Constraints (verified)
- Local: CPU-only, ~8GB RAM → inference OK (~1GB), training impractical
- Colab: CPU 12.67GB (verified), GPU T4 16GB when available (free tier)
- Model: 8.84M params → static ~140MB fp32 + AdamW ~70MB; activations small

## Strategy
| phase | hardware | cost |
|---|---|---|
| inference/deploy | local CPU | $0 |
| SFT smoke (Run5) | Colab T4 | $0 (free tier, ~10-30min) |
| SFT scale (1-3k samples) | Colab T4/Kaggle | $0-$0 |
| future Core-02/03 | Colab Pro GPU or Kaggle 30h/wk | low |

## Rules
- temporary GPU only; weights export to local CPU inference
- checkpoint to Drive after each run; hash-recorded
- interrupted-run resume via training_state.pt (driver supports)
- never depend on paid GPU permanently
- free-tier availability NOT guaranteed → keep cells resumable
