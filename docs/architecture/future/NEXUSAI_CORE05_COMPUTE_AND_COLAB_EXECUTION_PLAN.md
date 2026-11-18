# NexusAI Core-05 — Compute & Colab Execution Plan

**Status:** PLAN ONLY. No Colab launched, nothing executed.

## 1. Available resources (verified)

| Resource | Status |
|---|---|
| Local CPU | torch 2.14.1+cpu, CUDA unavailable, 8.5GB RAM — training impractical even at 8.8M; inference feasible |
| Free Colab T4 | 16GB VRAM, ~12h max session, disconnect risk — primary training target |
| Paid GPU (A100/L4) | not currently available; optional future upgrade |

## 2. Memory estimates (45.9M model, AdamW, bf16 on T4)

| Component | FP32 | BF16 |
|---|---|---|
| Weights | ~184 MB | ~92 MB |
| Gradients | ~184 MB | ~92 MB |
| AdamW states (m+v) | ~368 MB | ~184–368 MB |
| Activations (dominant) | seq512·b8: ~2–4GB | ~1–2GB |
| **Total typical** | ~3–5GB | ~1.5–3GB |

Headroom exists for seq1024 with batch 4–8 + grad-accum.

## 3. What T4 can and cannot do — honest assessment

- **SFT (V5-scale, ~1–4k records):** YES — under ~2h, well within session limits.
- **Continued pretraining (millions of tokens):** NO on free tier — session limits + token throughput make meaningful pretraining a multi-session, manually-chained effort. Possible but painful; needs checkpoint chaining across sessions.
- **Full pretraining to general intelligence:** NOT feasible on free T4. Would need paid GPU or many chained sessions — out of scope now.

Do NOT assume "can run SFT" = "can pretrain a brain." They are different compute regimes by orders of magnitude.

## 4. Recommended workflow

1. Upload repo subset + V5 JSONL + tokenizer to Colab/Drive once.
2. Run SFT cell: bf16, seq512 b8 accum8 (or seq1024 b4 accum16), 3 epochs.
3. Save checkpoint every 250 steps to Drive (atomic save already implemented).
4. Before session ends: ensure latest checkpoint + metrics downloaded.
5. Evaluate locally on CPU (inference only) or on Colab.
6. For any multi-session work: resume via `resume_checkpoint` + RNG restore (VERIFIED in code).

## 5. Dataset transfer

V5 JSONL estimated tens of MB → minutes over Drive/Colab. Tokenizer `.model` ~MBs. Checkpoint ~92–184MB per save. All well within Colab disk (usually ~100GB+ ephemeral; use Drive for persistence).

## 6. Risks

- Free-tier session cutoff mid-epoch → mitigated by frequent checkpoints + resume.
- Colab ToS/resource variability → keep runs short, checkpoint often.
- No persistent GPU → cannot hold model resident; reload per session (~seconds for 45M).
