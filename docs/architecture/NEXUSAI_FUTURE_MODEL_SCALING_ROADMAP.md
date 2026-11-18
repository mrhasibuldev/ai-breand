# NEXUSAI FUTURE MODEL SCALING ROADMAP

## Today (verified)
3 architectures: SmallTransformer(185K), MediumTransformer(2.47M), Core-01(8.84M). Active: Core-01 run3. RAM ~354MB.

## Safe promotion process for new checkpoints (e.g. Run4, Core-02)
1. Train on Colab → download ckpt → verify SHA-256 + strict load locally.
2. Add MODEL_DEFS entry (don't replace old — keep both).
3. Run fixed eval suite vs current primary.
4. Promote by changing `NexusBrain.PRIMARY` — one-line, reversible.
5. Old model stays registered as fallback.

## Scaling path
- Run4 (60M-token multilingual corpus — prepared, awaiting Colab)
- Larger Core variants: only after eval proves 8.8M insufficient
- Specialist models (math/reasoning/Bengali): future training + registry entries
- Quantization (INT8): for bigger models on 8GB CPU
- New tokenizers: registry already stores tokenizer path per model — versioned

## Hardware budget
CPU-only 8GB: 1 active model (~400MB) + fallback on demand. No simultaneous multi-model loading.
