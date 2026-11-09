# NEXUSAI GPU TRAINING → LOCAL CPU INFERENCE ARCHITECTURE

**Status doc for future developers.** Labels: ✅ VERIFIED IMPLEMENTED · 🧪 VERIFIED TESTED · 📋 PLANNED · ❌ NOT IMPLEMENTED · ⛔ BLOCKED

## 1. Why this architecture

- **Temporary GPU for training:** our own model needs GPU for feasible training time; Colab T4 / Kaggle P100 are free tiers. Ownership unaffected — code+data+checkpoints are ours.
- **Local CPU for inference:** an 8.8M-param model fits in ~270MB RAM and runs ~40 tok/s on a normal CPU 🧪 — no permanent GPU or cloud needed for chat.

## 2. Pipeline (target vs actual)

```
LOCAL REPO (code+data) → ZIP BUNDLE → COLAB/KAGGLE GPU → TRAIN
   → checkpoint_*.pt on Drive → DOWNLOAD → local ckpt dir
   → core01 InferenceEngine (CPU) → CHAT (EN/BN/Banglish)
```

| Stage | Status | Evidence |
|---|---|---|
| Bundle export | ✅ | `exports/NEXUSAI_CORE01_COLAB_TRAINING_BUNDLE.zip` |
| GPU train (Colab T4) | 🧪 | runs 1–3 completed (steps 447/894/1341) |
| Checkpoint save/resume | ✅ | driver `--resume`, ckpt every 100 steps |
| Checkpoint download | 📋 manual step | Drive → local path |
| CPU model load | 🧪 | 8.8M model builds in 0.3s, 252MB RAM |
| CPU generation | 🧪 | ~40 tok/s, 32 tokens in 0.81s (random weights — speed only) |
| Offline inference | 📋 | needs ckpt local + no API calls in path |
| Bengali conversation | ⛔ | model never trained on BN data yet |

## 3. Verified file paths

- Model: `packages/ai-core/core01/transformer.py` (`NexusAICore01`, 8,842,560 params)
- Config: `packages/ai-core/models/nexusai_core_01/config/model_config.py`
- Tokenizer: `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model` (vocab 8000; 2,819 BN pieces — multilingual)
- Driver: `packages/ai-core/core01/pretraining_driver.py` (`python -m core01.pretraining_driver`)
- Inference: `packages/ai-core/core01/inference.py` (`InferenceEngine`, device="cpu" default)
- Eval: `scripts/eval_core01_run3.py`, `docs/notebooks/COLAB_RUN3_DECISION_EVAL_CELL.py`

## 4. CPU inference requirements (measured)

- RAM: ~252MB model + ~15MB overhead ≈ **<300MB** 🧪 (8GB machine fine)
- Speed: ~40 tok/s → 100 tokens ≈ 2.5s 🧪
- Context 512: attention memory modest at this size; single-user fine, multi-user needs queueing
- Quantization (INT8/INT4): NOT implemented; PyTorch dynamic quantization compatible with nn.Linear — future option, unverified

## 5. Checkpoint safety rules (established)

- Never overwrite: each run gets own dir (`core01_english_runN/`)
- Resume: exact-path `--resume`, never glob-select
- Verify before use: `torch.load` + `load_state_dict(strict=True)` + param count
- Keep Drive copy + local copy; SHA-256 recorded in manifests

## 6. Hidden-dependency detection

- ml-service (`packages/ai-core/ml-service/main.py`) routes through deterministic handlers + fallback strings — neural output can be masked. For honest eval use `core01.inference.InferenceEngine` directly.
- API layer (`apps/api`) needs Postgres (Neon) for memory/context — optional infra, not core intelligence.
- No external AI API exists in core01 path ✅ (verified: only torch/sentencepiece/numpy).

## 7. Interrupted training recovery

Driver saves `checkpoint_last.pt` per epoch + `checkpoint_stepN.pt` every 100 steps; `--resume <path>` restores model+optimizer+scheduler+scaler+RNG 🧪 (verified run1→2→3 chain).

## 8. Known limitations / NOT IMPLEMENTED

- Run3 ckpt not local → CPU quality eval BLOCKED
- Bengali/Banglish: tokenizer ready, training data downloaded (148M tokens), cleaning pending, training not started
- Instruction/reasoning/decision stages: not implemented
- Quantized CPU inference: not implemented
- Multi-turn chat memory in core01 inference: not implemented
