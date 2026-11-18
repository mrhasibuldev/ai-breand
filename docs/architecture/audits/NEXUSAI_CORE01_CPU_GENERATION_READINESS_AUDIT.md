# NexusAI Core-01 — CPU Generation Readiness Audit

**Date:** 2026-11-17 · READ-ONLY · all findings evidence-backed

## A. Executive summary
Core-01 fully forensically verified: architecture, tokenizer, checkpoint
format, inference path (logits→argmax, no fallback), package integrity
(26/26), source-manifest match (16/17; only post-package inference.py fix).
Run4 checkpoint hash-verified on Colab GPU (`761a5b14…`, strict load PASS).
CPU generation cell ready — execution itself NOT TESTED yet.
Blocker: none technical; only Drive file-path confirmation pending.

## B. Source audit — files inspected (hashes verified vs package manifest)
| file | manifest | local | notes |
|---|---|---|---|
| core01/transformer.py | ✓ match | ✓ | NexusAICore01, pre-norm, sinusoidal |
| core01/inference.py | — | differs | **expected**: post-package fix (BOS/no-EOS/decode/inference_mode) |
| core01/tokenizer_interface.py | ✓ | ✓ | SentencePiece wrapper |
| core01/training.py | ✓ | ✓ | PretrainingEngine |
| core01/pretraining_driver.py | ✓ | ✓ | Run4 entrypoint |
| models/.../model_config.py | ✓ | ✓ | NexusAICore01Config + ModelStatus |
| models/.../model.py | ✓ | ✓ | checkpoint save/load helpers |
| cloud/*.py (4) | ✓ | ✓ | provider adapters |
Manifest check: 16/17 match; 1 diff = approved inference fix only.
Security scan: no network/subprocess/exec/eval/API calls in core01 path.

## C. Architecture audit — PASS
NexusAICore01(config): tok_emb 8000×256·√256 scale + sinusoidal pos +
6×{LN→MHA(causal,8H)→res, LN→FFN 256→1024→256→res} + final LN +
head → 8000 logits. No weight tying. count_parameters()=8,842,560.
forward(input_ids, targets=None)→logits; generate() exists in model.

## D. Checkpoint audit — PASS (Run4), Run3 local-verified
- Run4: `761a5b14f81a9726f0b56307e829b7d2b4fa5702dc4fdb0ed520cdae67ad4be1`
  106,777,501 B, ep5 step9213, strict=True PASS (Colab T4).
- Run3: `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830`
  local strict load PASS.
- Fields: model_state_dict, optimizer/scheduler/scaler/rng, epoch, step,
  config, tokenizer_path, model_status.
- **Safe deserialization WARNING**: `weights_only=True` FAILS (numpy RNG
  state in ckpt). Cell uses narrow allowlist (numpy reconstruct/dtype/
  ndarray/RandomState/Generator only) — justified: self-produced artifact.
  weights_only=False NOT used.

## E. Tokenizer audit — PASS
sp_bpe_8k.model sha `2fcc6a87…` · vocab 8000 · pad0 unk1 bos2 eos3.
encode/decode verified en/bn/banglish; UNK rate ~0 on corpus sample.

## F. Inference audit — PASS (logits path proven)
`InferenceEngine.generate` → `model.generate` → `forward()` logits →
greedy argmax / temperature+top-k/p sampling. EOS respected. Prompt:
BOS-only, no terminal EOS (post-fix). Decode: generated IDs only.
NO deterministic handlers, NO fallback, NO external calls — neural-only.

## G. CPU test cell
`docs/notebooks/COLAB_CORE01_CPU_READINESS_CELL.py` — self-contained:
env/drive/package discovery → ckpt+tok hash gates → weights_only=True
(+narrow allowlist) → strict load → CPU params proof → tokenizer →
InferenceEngine → 6 prompts (bn/en/banglish, 32 tokens, greedy,
inference_mode) → JSON+MD reports to `/content/nexusai_cpu_readiness/`.
Prereq: Drive mounted, package or ZIP present, ckpt findable (glob
fallback by exact size 106777501 B). NOT yet executed.

## H. Final status
| item | status |
|---|---|
| Source/manifest integrity | PASS |
| Architecture identification | PASS |
| Checkpoint integrity (Run4) | PASS |
| Safe deserialization | WARNING (allowlist required) |
| Strict state load | PASS (Colab T4; CPU pending) |
| Tokenizer | PASS |
| Inference path neural-only | PASS |
| CPU generation execution | **NOT TESTED** |
| Answer quality | **NOT TESTED** |
| Production readiness | NOT TESTED |

## Blockers
None technical. Run cell → inspect outputs → quality verdict pending.
