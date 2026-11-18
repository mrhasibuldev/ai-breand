# Core-05 Model Architecture Design

## Implementation choice
RECOMMEND: extend the existing core01 Transformer implementation
(packages/ai-core/core01/transformer.py) into a core05 module — same
proven code path, independent config+weights. Rewriting from scratch
adds risk without evidence of benefit at this scale. New module dir:
models/nexusai_core_05/ (config + training reuse via parameterized driver).

## Scale comparison (estimates, fp32 params ≈ 12·L·d² + vocab·d)
Assumptions: vocab 8000, max_len 512-1024, standard pre-norm decoder.

| scale | d_model | L | H | d_ff | ~params | train mem (Adam,bs8,seq512) | CPU inference |
|---|---|---|---|---|---|---|---|
| S experimental | 256 | 6 | 8 | 1024 | ~9M | ~2-3GB | feasible (~2-5 tok/s) |
| M practical | 512 | 12 | 8 | 2048 | ~45M | ~8-12GB | borderline (~0.5-1 tok/s) |
| L long-term | 768 | 16 | 12 | 3072 | ~110M | ~20-30GB | impractical CPU |

## Recommendation: SCALE M (~45M), staged
- Phase A: train S-scale (~9M) as pipeline proof on Colab T4.
- Phase B: train M-scale (~45M) as candidate Core-05.
- L deferred until M proves out (data+eval gates first).

## Key design decisions
- vocab 8000 BPE (existing) initially; tokenizer research separate
  (bn ok, banglish fragmented — do NOT change tokenizer this mission;
  a v2 tokenizer is a future gated project).
- max_len 1024 target (multi-turn depth needs it; memory cost ~2x).
- Pre-norm, learned or sinusoidal pos-enc (existing impl uses sinusoidal).
- bf16/fp16 mixed precision on GPU; fp32 master weights.
- Checkpoint format: same dict structure as existing cores for
  loader/registry compatibility.
- CPU inference: M-scale feasible for short responses; S-scale for
  interactive latency. Document measured tok/s before claiming.

## GPU/compute reality
Colab free T4 (16GB): M-scale SFT feasible (bs4-8, grad accum);
pretraining M-scale from scratch NOT feasible on free tier —
continued-pretraining or SFT-only on curated corpus is realistic.
