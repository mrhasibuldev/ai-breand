# NexusAI Core-05 — CPU Inference & Deployment Plan

**Status:** PLAN ONLY. No model instantiated, no inference benchmarked.

## 1. Feasibility

45.9M params ≈ 184MB fp32 weights. On 8.5GB RAM local CPU: loads comfortably. **Inference is feasible; speed is the constraint.**

## 2. Speed estimate (honest, unmeasured)

`generate()` recomputes the **full forward pass per generated token** (no KV cache) at growing sequence length. Rough expectation on a modern CPU:
- Short prompts (<200 tokens), ~50 new tokens: seconds to low-tens-of-seconds.
- Long contexts (1024) + 100+ tokens: tens of seconds to minutes.
- Interactive chat: usable but not snappy. **KV cache is the top inference optimization** (future mission).

These are estimates, not measurements — no model exists yet to benchmark.

## 3. Precision options

| Format | Size | Speed | Notes |
|---|---|---|---|
| FP32 | ~184MB | baseline | safest |
| FP16 | ~92MB | similar/faster on CPU w/ AVX512 | minor quality risk |
| INT8 quantization | ~46MB | faster | needs `torch.quantization` work — future |

CPU inference in fp32 is fine to start; quantization is an optimization, not a requirement.

## 4. Deployment path

- Local: `core01/inference.py` + `NexusAITokenizer` already provide generate/decode loop — reusable for Core-05 via config.
- Serving: single-user/desktop use is realistic; concurrent requests limited by CPU cores (no batching benefit without a server).
- Mobile: not realistic for 45M without quantization + mobile runtime — out of scope.

## 5. Blockers

- Depends on trained checkpoint (blocked on V5 → training).
- No KV cache → latency. Acceptable for evaluation, marginal for production chat.
