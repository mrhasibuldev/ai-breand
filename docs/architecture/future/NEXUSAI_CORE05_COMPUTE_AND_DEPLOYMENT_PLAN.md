# Core-05 Compute & Deployment Plan

## Available compute (verified constraints)
- Local: Windows desktop, CPU-only realistic for inference; training
  on CPU impractical (8.8M model already hours-days).
- Free GPU: Google Colab T4 (16GB) — temporary, artifacts stay NexusAI.
- No paid GPU assumed; if later available, L-scale becomes feasible.

## Deployment path
- Train on Colab → download checkpoint → register in model registry →
  route via existing ml-service → chat API → UI.
- CPU inference: S-scale interactive OK; M-scale acceptable latency
  for typical responses (measure before claiming).
- Checkpoint ownership: all artifacts NexusAI-owned; Colab is compute
  rental only, no data leaves to third-party AI services.

## Memory estimates (training, Adam, fp32 master + bf16 compute)
S-scale (~9M): ~2-4GB → T4 comfortable.
M-scale (~45M): ~10-14GB → T4 feasible w/ grad accum + bf16.
L-scale (~110M): ~25-35GB → needs A100 or multi-GPU; NOT on free tier.

## Risk: session limits
Colab sessions ~12h max; checkpoint save/resume proven in existing
training driver — use it. Save every N steps to Drive.
