# NexusAI Core-01 — GPU Smoke Test Plan (Tesla T4)

## Configuration (conservative)

| Item | Value |
|---|---|
| GPU | 1× Tesla T4 (sm_75, ~14.56 GB) |
| Precision | FP16 autocast + GradScaler |
| Stage D probe | batch 2 × seq 256, 1 optimizer step |
| Stage D2 (optional) | batch 4 × seq 256 — only if >6 GB headroom |
| Driver run | `-m core01.pretraining_driver`, bs8, seq 512 (config), `--max-steps 2`, fp16 |
| Resume test | `--resume <ckpt>` + `--max-steps 3` |
| Checkpoints | `/content/drive/MyDrive/NexusAI/checkpoints_smoke/` |
| Report | `/content/drive/MyDrive/NexusAI/audit_reports/core01_smoke_<ts>.json` |

## Stages

- **A** env: python/torch/CUDA/GPU/VRAM/fp16 probe — fail if no CUDA
- **B** source: transformer.py sha256 + fix-marker + buggy-pattern-absent — fail if old file
- **C** model: Core-01 on cuda:0, assert 8,842,560 params, init VRAM
- **D** FP16 fwd/bwd/clip/step bs2×256 + GradScaler; optional bs4 if headroom
- **E** mask: repaired `attention_mask` path, causal isolation check
- **F** driver: synthetic 300-doc jsonl, max-steps 2, ckpt create + strict reload
- **G** resume: `--resume` last ckpt, +1 step, verify step increments
- **H** cleanup: free GPU refs, keep ckpts+reports

## Safety

- `SMOKE_TEST_ONLY=True` guard + step cap ≤3 + conservative tensor limits
- No real corpus, no dataset modification, no full-training args
- Fail-fast per stage; report written even on failure
- No CPU fallback pretense, no FP16 downgrade pretense
