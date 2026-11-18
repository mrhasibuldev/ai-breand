# NEXUSAI — BENGALI RUN4 READINESS REPORT

**Date:** 2026-11-10 · PREPARATION ONLY — training NOT authorized, NOT started

## Corpus (independently re-verified this session)
- Path: `packages/ai-core/data/phase2/run4_corpus/corpus_train.jsonl`
- Docs: **216,193** · Size: **385,217,021 bytes (~385MB)** · SHA-256: `5f8572edd816ac87…` (matches build manifest)
- Composition (actual counts):
  - english_first: 61,960
  - tinystories: 60,000
  - bangla_wikipedia_mit: 45,000
  - bongchat_v1: 30,000
  - reasoning_v1: 10,233
  - sangraha_bengali: 9,000
- Language field: en 130,753 / bn_mixed 84,000 / bn 819 / banglish 459 / mixed 162
- **Bengali character share: 47.1%** of all characters
- Est. tokens: ~53M (char-based estimate; prior report said ~60.4M — treat as approximate until tokenizer pass)

### Correction to prior claims
"60% Bengali" was sampling intent, not measured. Measured: Bengali-sourced docs ≈ 84K/216K ≈ **39%**, Bengali chars ≈ **47%**. English+TinyStories ≈ 56% of docs. Corpus is roughly balanced, slightly English-leaning by count.

## Quality/provenance
- Sources all license-verified earlier (wiki MIT, Sangraha, BongChat v1, TinyStories MIT, english_first internal, reasoning_v1 deterministic-generated)
- Dedup applied at build; reasoning held-out 300 excluded from train
- Known limitation: 6 generic held-out reasoning fragments appear in corpus context (documented)

## Training config (prepared, not run)
- Parent: run3 checkpoint (sha256 verified) → output `checkpoints_core01_run4/` (isolated, run3 untouched)
- Cell: `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` — resume-safe, fp16, bs8×accum4, 2 epochs, max 8000 steps, ckpt/100
- Tokenizer: sp_bpe_8k vocab 8000 — compatible (verified)
- Hardware: Colab T4 assumed; est. runtime hours-scale with resume across sessions
- Bundle: `exports/NEXUSAI_CORE01_RUN4_BUNDLE.zip` sha256 `75af9fa2…` (source only; corpus uploaded separately)

## Readiness checklist
| Item | Status |
|---|---|
| Corpus built+hashed | ✅ verified |
| License/provenance | ✅ documented |
| Parent ckpt integrity | ✅ sha256 verified |
| Tokenizer compat | ✅ verified |
| Training cell | ✅ resume-safe patched |
| Bundle | ✅ built |
| Eval plan | ✅ neural-only suite + run3 baseline comparison |
| GPU access | ⏳ user must run Colab |
| **Training execution** | ❌ NOT AUTHORIZED — awaiting explicit approval |

## Blockers
None technical. Only missing: user runs Colab cell + uploads 385MB corpus to Drive.

## Post-training plan (on approval)
1. Download run4 ckpt → `models/checkpoints_core01_run4/`
2. Add MODEL_DEFS entry `nexus-core-01-run4`, validate hash
3. Run same neural-only suite vs run3 baseline; compare val_loss
4. Promote via registry PRIMARY only if eval improves
