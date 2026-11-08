# NexusAI Core-01 — Full Training Configuration & Execution Plan
# (prepared; execute ONLY after smoke-test PASS + owner approval)

## Recommended config (T4, pending smoke-test VRAM evidence)

| Param | Value | Reason |
|---|---|---|
| device | `cuda` | T4 |
| precision | `fp16` | sm_75, no bf16; GradScaler path verified |
| batch_size | **16** micro | conservative; adjust per smoke peak VRAM |
| gradient_accumulation | **2** | effective batch 32 |
| seq len | 512 (config-fixed) | PackedTextDataset |
| lr | 3e-4, warmup 500 | config default |
| epochs | 1–3 over ~98.5M tok | ~6–18k optimizer steps (estimate) |
| ckpt/eval interval | 500 / 500 | Drive persistence |
| ckpt dir | `Drive/NexusAI/checkpoints_full/` | separate from smoke |
| resume | `--resume checkpoint_last.pt` | verified working |

Driver cmd template (module form — REQUIRED):
```
cd /content/nexusai/packages/ai-core && python -m core01.pretraining_driver \
  --train-file <train.jsonl> --val-file <val.jsonl> \
  --output-dir /content/drive/MyDrive/NexusAI/checkpoints_full \
  --tokenizer <sp_bpe_8k.model> --device cuda --precision fp16 \
  --batch-size 16 --gradient-accumulation-steps 2 \
  --learning-rate 3e-4 --warmup-steps 500 --epochs 1 \
  --checkpoint-interval 500 --eval-interval 500 --log-interval 50
```

## Gates before this runs

1. Smoke test report: CUDA+FP16+fwd/bwd+mask+ckpt+resume+memory ALL PASS
2. Dataset audit cell: DATASET_OK-level results on Drive files
3. Owner explicit approval for FULL_TRAINING

## Honest language-coverage warning

English corpus ≈100M tokens; Bengali repo data ≈220KB (~tens of K tokens).
After English-only pretraining the model will be **English-strong,
Bengali/Banglish-weak**. Meeting the Bengali/Banglish goals requires a
separate data-acquisition phase (more Bengali text, SFT pairs) — documented,
not silently substituted.
