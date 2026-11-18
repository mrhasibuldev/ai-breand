# NexusAI Core-05 — Stage-0 Training Readiness Audit

**Status:** COMPLETE (read-only audit; no training, no modifications)
**Date:** post-V5-construction-mission
**Auditor:** Devin (evidence-labeled)

---

## 1. Executive Summary

Stage-0 audit verdict: **Core-05 training is BLOCKED**, primarily because **Dataset V5 does not exist**. The V5 construction mission was interrupted after builder scaffolding (`build_unified_conv_v5.py`, `build_unified_conv_v5_mt.py`) was written; the dataset was never built, validated, or documented. No `data/unified_conversational/v5/` directory exists.

All other components were independently audited and are documented below. The architecture math, tokenizer, and training pipeline are technically sound and reusable; the compute plan is realistic for SFT-scale work on a free T4 but **not** for broad pretraining.

## 2. Repository Safety Status — VERIFIED

- HEAD: `cb289fb` (unchanged from prior missions)
- Branch: `main`
- Uncommitted/untracked entries: **167** (was 165; +2 = the two new v5 builder files — expected, no unexpected changes)
- V1–V4 dataset directories intact; no v5 output directory exists
- torch 2.14.1+cpu locally; `torch.cuda.is_available() == False`; RAM 8.5 GB

## 3. Dataset V5 Verification — FAILED / NOT READY

| Check | Result |
|---|---|
| `data/unified_conversational/v5/` exists | **NO** |
| Builder scripts exist | YES (`build_unified_conv_v5.py` ~70 lines stub; `build_unified_conv_v5_mt.py` ~407 lines, compiles, never executed) |
| Records/splits/manifests/checksums/reports | **NONE** |
| V1–V4 modified | NO (verified intact) |

**Consequence:** Every V5-dependent readiness item (language distribution, multi-turn depth, reasoning/decision counts, benchmark isolation, loader compatibility of V5 records, reproducibility) is **NOT VERIFIED — cannot be assessed**. The most recent real dataset is **v4: 1,223 approved records** (en 604 / bn 290 / banglish 182 / mixed 27; math 32%; multi-turn 63). This is far below V5 spec targets (multi-turn 300+, reasoning 150+, decision 150+, bn 35%).

**Recommendation:** a dedicated V5 completion mission is the critical path blocker.

## 4. Tokenizer Readiness — PARTIALLY READY

Tokenizer: SentencePiece BPE, `sp_bpe_8k.model`, vocab **8001** reported by `get_piece_size()`=8000 (specials pad=0, unk=1, bos=2, eos=3). Interface `core01/tokenizer_interface.py` validates vocab==config and warns on special-ID mismatch. `sft_dataset.py` uses `bos/eos/pad` consistently.

Measured tokenization (chars→tokens, UNK count):

| Sample | chars | tokens | UNK | tok/char |
|---|---|---|---|---|
| English | 42 | 10 | 0 | 0.24 |
| Bengali | 32 | 9 | 0 | 0.28 |
| Banglish (Romanized) | 32 | 13 | 0 | 0.41 |
| Mixed + foreign script | 38 | 16 | 1 | 0.42 |

Findings:
- Bengali script tokenizes reasonably (multi-char pieces like `প্রোগ্রামিং`); **Banglish fragments heavily** (e.g. `Programming`→`Pro gr am ming`, `shikhAR`→`sh ik h ar`) — ~70% more tokens per char than English.
- Foreign scripts (Arabic in test) produce UNK — acceptable but lossy.
- 8K vocab is **adequate for English/Bengali script, marginal for Banglish**; context efficiency for Banglish conversations will be poor. A larger or retrained tokenizer is a *future* option, not a blocker for an initial SFT experiment — but it caps achievable Banglish quality.
- **VERIFIED:** tokenizer file exists, loads, IDs match config, no UNK on bn/en/bg test samples.

## 5. Core-05 Architecture Feasibility — VERIFIED (math), RECOMMENDATION (design)

Proposed: d_model=512, n_layers=12, n_heads=8, d_ff=2048, vocab=8000, max_len=1024.

Parameter calculation (matches `model_config.estimated_parameter_count` formula):
- Per layer: attn 4·d²+4d = 1,050,624; FFN 2·d·ff+ff+d = 2,099,712; LN 2·2·d = 2,048 → **3,152,384/layer**
- 12 layers = 37,828,608
- Token embedding 8000·512 = 4,096,000; output head 512·8000+8000 = 4,104,000
- **Total ≈ 45.93M parameters** — the "~45M" claim is VERIFIED.

Consistency checks:
- 512 % 8 heads = 0 ✓; head_dim=64 ✓; d_ff=2048=4×d_model ✓
- Sinusoidal PE supports max_len=1024 (buffer sized by config) ✓ — but note PE is *fixed*, quality at 1024 unverified
- Existing `transformer.py` is config-driven; Core-05 can reuse it with a new config (no code change needed) — VERIFIED by reading `NexusAICore01.__init__`

Caveats:
- No weight tying between embedding and output head → +4.1M params; fine.
- No KV cache in `generate()` → CPU inference will be slow (see §10).
- max_len 512→1024 doubles activation memory and attention cost (S²).

## 6. Training Pipeline Audit — PARTIALLY READY

Existing infrastructure (`core01/training.py`, `sft_dataset.py`, `dataset.py`, `pretraining_driver.py`, `evaluation.py`, `inference.py`):

| Capability | Status | Evidence |
|---|---|---|
| Causal LM objective | VERIFIED | `transformer.py` forward, cross-entropy w/ ignore_index=pad |
| Response-only SFT masking | VERIFIED | `sft_dataset.serialize_conversation` masks user/role tokens with -100 |
| Shift/labels convention | VERIFIED | shift applied in serializer (input=seq[:-1], labels=seq[1:]) |
| AdamW + warmup scheduler | VERIFIED | `training.py` PretrainingEngine |
| Grad clip, grad accumulation | VERIFIED | `train_epoch`, correct group-size averaging |
| AMP fp16/bf16 | VERIFIED | `resolve_amp_dtype`, GradScaler for fp16 |
| Checkpoint save/load/resume | VERIFIED | atomic save w/ backup, RNG state capture/restore |
| Pretrained-checkpoint gate for SFT | VERIFIED | `validate_pretrained_checkpoint` refuses UNTRAINED/random init |
| Validation loop | VERIFIED | `validate()` |
| Attention-mask padding handling | VERIFIED | causal×pad mask in forward |
| KV cache / efficient generation | **MISSING** | `generate()` recomputes full forward per token |
| `generate()` batch EOS bug | MINOR | breaks entire batch when *any* sample hits EOS (`next_token.item()`) — fine for batch=1 inference |
| Core-05 config class | **MISSING** | would need `models/nexusai_core_05/config/model_config.py` (new file, not a modification) |
| Data loader for Core-05 | PARTIAL | `ChatSFTDataset` is schema-compatible with v1–v4/v5 JSONL `{messages:[...]}` — VERIFIED by code inspection; untested on v5 (doesn't exist) |

No blocking bugs found for an SFT run at batch sizes feasible on T4. The missing KV cache affects inference speed only.

## 7. Training Strategy Recommendation — RECOMMENDATION

Options evaluated:

- **A. From scratch**: needs large pretraining corpus (billions of tokens) — infeasible on free T4 within reasonable time. REJECT for now.
- **B. Small→scale**: proven path (Core-01 run3 exists at 8.8M, PRETRAINING_COMPLETED, train_loss 4.43). RECOMMENDED as pipeline proof.
- **C. External base weights**: prohibited by NexusAI principles. REJECT.
- **D. Continue pretraining from existing checkpoint**: Core-01 run3 (d256/L6/8.8M) is the only verified NexusAI-owned pretrained checkpoint; architecture differs from proposed Core-05 (d512/L12) so weights **cannot** transfer directly. Applicable only if Core-05 adopts the Core-01 shape or a compatible subset.
- **E. Staged S→M SFT + optional continued pretrain**: **RECOMMENDED.** Stage 1: small config (e.g., d256/L6) SFT on v4/v5 to prove pipeline end-to-end on T4. Stage 2: Core-05 medium (45.9M) SFT once V5 exists. Stage 3 (optional, future): continued pretraining on a larger licensed corpus to improve fluency — requires separate data mission.

**Honest limitation:** SFT on ~1–3k conversational records teaches format and style, not broad knowledge or reasoning. V5 alone cannot produce a "general-purpose brain"; it is a necessary but insufficient component. A continued-pretraining corpus mission will be needed for real capability.

## 8. Compute & Colab Feasibility — PARTIALLY VERIFIED

Local: 8.5 GB RAM, CPU-only torch — **CPU training of even 8.8M is impractical** (verified: no CUDA). CPU *inference* of 45.9M is feasible but slow (no KV cache).

T4 (16 GB VRAM, free Colab):
- 45.9M model, fp32 weights+grads+AdamW ≈ 550 MB; activations dominate. Estimated feasible: seq 512, batch 8–16 with grad-accum; seq 1024, batch 4–8 bf16. **SFT feasible; full pretraining of meaningful token count NOT feasible** on free-tier session limits (typically ≤12h, disconnects).
- Dataset transfer: V5-sized JSONL (~tens of MB) — minutes. Checkpoint ~184 MB fp32 (or ~92 MB fp16) per save — Drive backup needed per session.

## 9. Final Readiness Gates

| Component | Verdict |
|---|---|
| Dataset V5 | **BLOCKED** — does not exist |
| Dataset v4 (fallback) | PARTIALLY READY — real but below spec targets |
| Tokenizer | PARTIALLY READY — works; Banglish fragmentation caps quality |
| Architecture design | READY (math verified); implementation = new config only |
| Training pipeline | READY WITH CONDITIONS — reusable; no KV cache; needs Core-05 config |
| Compute (SFT-scale) | READY WITH CONDITIONS — T4 sufficient for SFT, not pretraining |
| Checkpoint strategy | READY — existing CheckpointManager is solid; needs core05 dir naming |
| CPU inference | PARTIALLY READY — feasible, slow without KV cache |
| Evaluation | PARTIALLY READY — benchmark suites not yet built (depend on V5) |
| **Overall Core-05 training readiness** | **BLOCKED** — gated on V5 dataset completion |

## 10. Critical Path

1. **Complete V5 dataset mission** (finish builder, build, validate, benchmark, document) — BLOCKER
2. Create `models/nexusai_core_05/` config + reuse `core01` transformer/training (new mission)
3. Stage-0.5: small-config SFT smoke test on Colab T4
4. Core-05 medium SFT on V5 train split
5. Evaluation against independent benchmark; iterate
6. (Future, separate mission) continued-pretraining corpus for real capability gains

## 11. Operations Not Performed

No training, no Colab, no checkpoint/tokenizer/architecture/runtime/API/UI/DB changes, no dataset modification, no commits/pushes. Tokenizer diagnostics were read-only. All findings above cite verified file evidence.
