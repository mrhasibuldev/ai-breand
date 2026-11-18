# NexusAI Run5 SFT Training Pipeline Audit
Date: 2026-11-17 · READ-ONLY · no training executed

## Components verified
- `core01/pretraining_driver.py`: resume, AdamW, LambdaLR, grad-accum,
  AMP/bf16, checkpoint save, best-val selection, interruption recovery — VERIFIED (Run4 used it)
- `core01/training.py`: micro-batch loop, grad scaling, clip — VERIFIED
- `core01/sft_dataset.py`: ChatSFTDataset + serialize + collate +
  batch_has_supervision — VERIFIED on tensors (Run3 ckpt, CPU)
- `docs/notebooks/COLAB_NEXUSAI_CORE01_RUN5_SFT_PREPARATION.py`:
  TRAINING_ENABLED=False gate, hash-gated Run4 load, embedded dataset code,
  masking+loss+NaN-guard preflight — syntax PASS, Colab run NOT VERIFIED

## SFT correctness findings
- serialization `[BOS]user:…[EOS]assistant:…[EOS]` deterministic ✓
- response-only masking: prompt/user/BOS/pad → -100; assistant content+EOS supervised ✓
- multi-turn: both assistant turns supervised ✓
- last supervised token = EOS(3) ✓
- attention_mask produced by collate; model.forward accepts it ✓
- loss path: logits=model(x,attention_mask) → CE(ignore_index=-100) — correct;
  NOTE model's own forward(targets=) uses pad_id NOT -100 → SFT must use
  external CE (cell does) ✓
- NaN guard: batch_has_supervision — all-masked batches skipped ✓

## Risks identified
- catastrofic forgetting: low LR 2e-5 + 3 epochs on 93 samples — moderate
- immediate-EOS persistence: SFT data has explicit assistant turns → should fix
- overfitting: 93 train samples tiny → keep epochs ≤3, monitor val
- Bengali degradation: bn=29 train — watch bn val loss

## Not verified
- Colab GPU preflight run (pending user)
- actual training step (prohibited)
- GPU memory measured (estimated only)
