# NexusAI Core-01 — Run4 Final Training-Readiness Audit

**Date:** 2026-11-15 · **Mode:** READ-ONLY · **Environment:** local Windows (CPU-only) — NOT Colab

## Verified Facts (executed this session)

| Item | Evidence | Result |
|---|---|---|
| Repo | `Ai Breand` @ `64d05e9` main, 80 uncommitted paths | PASS (work uncommitted = preservation risk) |
| Python/Torch | 3.14.6 / 2.14.1+cpu, CUDA=False | PASS locally; GPU NOT VERIFIED |
| Run3 ckpt | 106,777,501 B · SHA `ad515cadea433d17…` · ep3/step1341 · losses 4.426/4.217 · full resume keys | PASS |
| Core-01 arch | 8,842,560 params, 6L/256d/8H/FFN1024/vocab8000/len512, pre-norm, `transformer_blocks.*` keys | PASS |
| Tokenizer | `sp_bpe_8k.model` 387,195 B · SHA `2fcc6a87…` · vocab 8000 · en+bn encode/decode verified | PASS |
| Run4 dataset | `corpus_train.jsonl` 385,217,021 B · SHA `5f8572ed…` · 216,193 records · 0 malformed (prior scan) | PASS w/ warnings (6,922 dup texts; thin Banglish/conversational) |
| Release ZIP | 173,914,048 B · SHA `8b212964…` · v2.3.0 · testzip clean · inner 15 entries | PASS |
| Train cell | EPOCHS=5 → range(3,5)=2 epochs · MAX_STEPS=8000 · bs8×accum4=eff32 · fp16 · auth-marker check present | PASS (static) |
| Resume | opt+sched+scaler+RNG restored; scheduler init pre-load; atomic saves; zero-step guard | PASS (bounded smoke previously) |
| GPU | torch.cuda.is_available()=False locally | **NOT VERIFIED — Colab required** |
| Disk | only ~2 GB free locally | WARNING (irrelevant on Colab; blocks local dataset ops) |
| Phase10 ckpt | different key family confirmed | WARNING — must not be routed as Core-01 |
| R1.1/R2 artifacts | benchmark v2 report, 7/7 integrity tests, 2 docs — all intact | PASS |

## GO/NO-GO Checklist

| Area | Status | Evidence | Action |
|---|---|---|---|
| Repository | PASS | git verified | commit backup recommended |
| Python/PyTorch | PASS | local env | n/a |
| GPU | NOT VERIFIED | cuda=False local | verify in Colab cell |
| Run3 checkpoint | PASS | hash+metadata verified | none |
| Architecture compat | PASS | strict load verified | none |
| Tokenizer | PASS | vocab+codec verified | none |
| Dataset integrity | PASS | hash+count verified | none |
| Dataset quality | WARNING | 6,922 dups; weak BN-conv/Banglish | SFT phase later |
| Training config | PASS | static audit of cell | none |
| Resume safety | PASS | smoke-tested previously | Colab re-verify |
| Checkpoint recovery | PASS | atomic+priority resume | none |
| Colab notebook | PASS w/ WARN | cells packaged; gate enforced | user executes |
| Resource req | WARNING | est. VRAM ~4-6GB fits T4; disk ~1-2GB | verify at runtime |
| R1.1/R2 preserved | PASS | files+tests verified | none |

## Critical Blockers
None found in artifacts. **GPU runtime is the only unverified element.**

## Warnings
1. Dataset quality limits expected gain (pretraining ≠ conversation).
2. Phase10 orphan checkpoint — registry must not select it (documented, not moved).
3. `production/current.json` metrics stale (perplexity 2.83 false; real ≈67.8) — correction proposed, not applied.
4. 80 uncommitted paths — backup advised.

## Final Decision
**READY WITH WARNINGS — for Colab execution.** All artifact-level checks PASS;
GPU/runtime checks are NOT VERIFIED locally by design and are covered by the
Combined Preflight Cell (v2.3.0) which must run first in Colab.

## Exact Next Steps (user)
1. Colab GPU notebook → upload `NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip` (SHA `8b212964…`)
2. Run Combined Preflight cell → expect READY FOR TRAINING
3. Run gate cell → type `START NEXUSAI CORE-01 TRAINING`
4. Run training cell → paste outputs back
