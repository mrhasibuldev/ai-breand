# NEXUSAI RUN4 LOCAL CPU READINESS

## Verified (run3, same arch as run4)
- Load: strict state_dict OK, 8,842,560 params
- RAM: ~382MB peak during eval (8GB machine OK)
- Speed: 42.6 tok/s CPU → 100 tokens ≈ 2.3s
- Offline: torch+sentencepiece only, no external AI
- Disk: ckpt ~107MB

## Run4 expectation
Same architecture → same footprint. No quantization needed at 8.8M params.
Multi-turn chat memory: app-layer concern, not model.
