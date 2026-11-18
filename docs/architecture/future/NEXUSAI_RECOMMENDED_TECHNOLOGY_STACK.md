# NexusAI Recommended Technology Stack

**Purpose:** evidence-based recommendations for strengthening NexusAI as an independently owned AI Brain. Distinguishes *currently used* vs *recommended* vs *optional/future*. No external AI inference APIs anywhere in the stack — that constraint overrides all other considerations.

## A. Core AI model development

| Technology | Status | Role | Verdict |
|---|---|---|---|
| Python 3.11–3.14 | **Used** | All model/training/inference code | Keep — ecosystem standard |
| PyTorch ≥2.x | **Used** (2.14.1+cpu local) | Model definition, autograd, inference | Keep — required |
| NumPy | **Used** | Data/tensor utilities | Keep |
| SentencePiece | **Used** | BPE tokenizer (sp_bpe_8k) | Keep — tokenizer is trained asset, retraining is a separate authorized task |
| Hugging Face `datasets`/`datasketch` (local only) | Optional | JSONL validation, near-dup detection (MinHash/LSH) | **Recommended for dataset engineering** — data tooling only, never inference |
| C++ / CUDA C++ | Future | Custom CUDA kernels for attention/generation if profiling justifies | Optional — only after KV-cache exists and profiling shows bottleneck |
| Triton | Future | Fused kernels (RoPE, RMSNorm, sampling) | Optional, same prerequisite |
| ONNX Runtime | Optional | Export for edge/CPU serving | Defer — our transformer is config-driven PyTorch; export adds a second source of truth. Revisit for mobile |
| llama.cpp-style engines | **Rejected for core** | Would couple us to an external model format/ecosystem | Incompatible with independent-weights principle unless we own the runtime; our own `transformer.py` + `inference.py` is the engine |

**Why:** the moat is ownership of weights+code. Every recommended addition is a conventional tool, not an AI service.

## B. Training & fine-tuning

| Capability | Status | Notes |
|---|---|---|
| PyTorch training loop | **Used** (`core01/training.py`) | AdamW + warmup, grad-accum, AMP bf16/fp16, RNG-capture resume, atomic checkpoints |
| Mixed precision | **Used** | bf16 on GPU, fp32 CPU |
| Gradient checkpointing | Not implemented | Recommend for Core-05 45M+ on T4 — trades ~30% speed for ~50% activation memory |
| Pretraining vs SFT vs IT | Documented distinction | Pretraining = next-token on corpus; SFT = response-only loss on conversations (`sft_dataset.py`); instruction tuning = SFT with instruction-format data; reasoning training = needs verified reasoning dataset (V5) |
| Evaluation during training | Partial | val loss tracked; no downstream benchmark gate yet — recommend adding the `four_core_test_suite.py` pattern as a training-time eval hook |

## C. Dataset engineering

| Need | Recommended tool | Status |
|---|---|---|
| JSONL validation/schema | `jsonschema` or hand-rolled (current) | Used |
| Exact dedup | hash of normalized text (used in audit) | Used ad-hoc; recommend `datasets` + `datasketch` MinHash for near-dups |
| Language ID | `lingua` or `langdetect` | Router has own `detect_language_v2`; add independent verification |
| bn/bg validation | Native-speaker review + script-ratio checks | Human step — cannot be automated honestly |
| Split/leakage | content-hash split (already used) + dedup-before-split | Recommend formalizing in builders |
| Versioning | manifest + checksums.sha256 (already convention) | Keep |

## D. Model evaluation

Current: `verify_four_core_generation.py` (matrix), `four_core_test_suite.py` (held-out + numeric oracle), `eval_core.py`. Recommended additions:
- Per-language benchmark suites with fixed seeds → reproducible JSON diffs across checkpoints.
- Bengali/Banglish human-eval rubric (documented, not auto-scored).
- Uncertainty/hallucination probes: ask out-of-corpus facts, measure whether model abstains or fabricates (currently it fabricates — known).
- Store every eval report under `eval_reports/` with git SHA + checkpoint SHA-256 (already the convention).

## E. Inference & performance

| Item | Status | Priority |
|---|---|---|
| KV caching | **Not implemented** | P1 for usable chat latency — biggest single win; implement in `transformer.py` generate path |
| Batched generation | Fixed this mission (F3) but callers are batch=1 | P2 |
| Quantization (int8/int4) | Not implemented | P2 for CPU speed; validate quality delta first |
| torch.compile / CUDA graphs | N/A CPU | GPU-only future |
| Profiling | `torch.profiler` ad-hoc | Do before optimizing |
| C++/CUDA kernels | See A | Only if profiling demands |

## F. Development & infrastructure

| Area | Current | Recommendation |
|---|---|---|
| VCS | git + GitHub, LFS for large .pt | Keep; add `.gitattributes` entries if more LFS weights needed |
| Monorepo | pnpm 11 + workspaces (apps/web, apps/api, apps/worker, packages/*) | Keep |
| Node | v24.15.0 (repo wants >=22 <25) | Compatible |
| Python env | system Python 3.14 + per-dir `.venv` | Recommend single `requirements.txt`-driven venv per service; pin versions |
| ML deps | `ml-service/requirements.txt` missing `sentencepiece` (imported but undeclared!) | **Fix: add `sentencepiece` to requirements** — real defect found during this audit |
| Docker | Not present | Optional — useful for reproducible API+ML deploy; not required for dev |
| Colab | cells in `docs/notebooks/` | Keep for authorized GPU training only |
| CI | none | Recommend GitHub Actions: lint+vitest+pytest-equivalent script runs |
| Secrets | `.env` gitignored | Keep; consider `upload-secrets` flow for CI |

## G. Long-term architecture (all PLANNED, not implemented)

Independent Core → specialized instances (02/03/04 pattern proven) → router (exists) → own inference engine (exists, needs KV cache) → public API (planned) → context/memory with consent (schema exists, runtime untested) → reasoning/self-correction (needs V5+training) → agents → voice → developer platform.

## Prioritized roadmap

- **Immediate:** add `sentencepiece` to ml-service requirements; KV-cache implementation; CI smoke job.
- **Short-term:** Dataset V5 (authorized next mission); Core-01 SFT (Run4/Run5); dedup core02/03 datasets.
- **Medium-term:** Core-05 45M model; quantized CPU serving; multi-turn state in router.
- **Long-term:** agent capabilities, voice, public developer API, consent-based memory runtime.

*Prerequisite note: every training-dependent item requires its own authorization and verified dataset first.*
