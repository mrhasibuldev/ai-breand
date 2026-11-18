# NEXUSAI MODEL TRAINING STRATEGY

## Verified history
- Runs 1–3: continue-pretrain Core-01 on english_first (7.43M tok), steps 447/894/1341, val_loss 4.85→4.22 — real but undertrained.
- Medium model: Phase-10 ~1,812 samples — overfit gibberish source.

## Recommended sequence (evidence-based)
1. **Run4 (immediate):** continue-pretrain from run3 on 60M-token multilingual corpus (60% BN) — prepared, awaiting Colab. Expected ~7.4K steps.
2. **Run5+:** scale data (Chinchilla-optimal for 8.8M ≈ 175M tokens) + instruction/reasoning SFT stage on reasoning_v1-style verified data.
3. **Specialists:** only after foundation eval proves need — math/reasoning adapters or separate small models via registry.
4. **Self-correction:** two-pass generate+verify as inference-time feature (test before claiming).

## Principles
- Continue-pretraining > scratch (preserve run3 learning).
- Data quality > volume; measure dedup/leakage.
- Checkpoint per stage; resume-safe; SHA-256 verified.
- CPU inference target: keep ≤~500MB RAM active model; quantize later if scaling.
- Colab/Kaggle T4 free tier: ~7K steps/run feasible w/ resume across sessions.
