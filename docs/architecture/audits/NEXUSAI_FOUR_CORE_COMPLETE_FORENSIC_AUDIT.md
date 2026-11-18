# NexusAI Four-Core Complete Forensic Audit

**Date:** 2026-11-18 · **HEAD:** `cb289fb` (main, ahead of origin by 1) · **Device:** CPU-only (torch 2.14.1+cpu)

## 1. Repository state (verified, not historical)

- Branch `main`, HEAD `cb289fb39c6262b12c31ac459efe2a9d7f40fffd`, remote `origin = github.com/mrhasibuldev/ai-breand`.
- 177 uncommitted entries at audit time: 7 tracked modifications (README, Colab Run4 cell, `core01/inference.py`, `core01/pretraining_driver.py`, `model_config.py`, `production/current.json`, one `.pyc`) + ~170 untracked paths (docs, datasets, model configs, eval reports, exports).
- Ownership classes: (A) user files (`.env` — gitignored, never read/committed), (B) prior approved agent work (Phase B+C fixes, four-core datasets/manifests, Colab cells, audit docs), (C) this mission's files (verification/test scripts, repair patch, new audit docs), (D) generated artifacts (`__pycache__`, `.pyc`, `exports/*.zip` bundles, `backups/`).

## 2. Model inventory (verified by load + strict state-dict)

All four cores share ONE Transformer implementation: `packages/ai-core/core01/transformer.py` (`NexusAICore01`). They differ only in config + weights — **not** four architectures.

| Core | Config | d_model/L/H/ff | max_len | vocab | Params (verified) | Active checkpoint | Status |
|---|---|---|---|---|---|---|---|
| Core-01 | `models/nexusai_core_01` | 256/6/8/1024 | 512 | 8000 | 8,842,560 | `checkpoints_core01_run3/checkpoint_final.pt` (LFS, sha256 `ad515c…7830`) | PRETRAINING_COMPLETED (base LM, not SFT'd) |
| Core-02 | `models/nexusai_core_02` | 384/8/12/1536 | 512 | 8000 | 20,347,712 | `checkpoints_core02_sft_v2/checkpoint_final.pt` (sha256 in registry) | SFT reasoning specialist |
| Core-03 | `models/nexusai_core_03` | 256/6/8/1024 | 512 | 8000 | 8,842,560 | `checkpoints_core03_sft_v2/checkpoint_final.pt` | SFT math specialist |
| Core-04 | `models/nexusai_core_04` | 512/8/8/2048 | 512 | 8000 | 33,419,072 | `checkpoints_core04_sft_v3/checkpoint_final.pt` | SFT knowledge/memorization |
| medium (legacy) | `neural/medium_transformer.py` | 128/2/2/512 | 128 | 8000 | 2,452,544 | `checkpoints_medium/final_model.pt` | fallback only |

Strict `load_state_dict(strict=True)`: **0 missing / 0 unexpected keys for all five.** Registry SHA-256 validation: PASS for all five.

Note: `nexusai_core_02/03/04/` config dirs were **untracked** until this mission (oversight from commit `d278893`); they are required at runtime by `nexus_core.get_config()`.

## 3. Checkpoint & tokenizer verification

- Tokenizer: SentencePiece BPE 8K (`data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model`), pad=0, unk=1, bos=2, eos=3 — consistent across all cores.
- `.sha256` provenance files committed for all core02/03/04 checkpoints; `*.pt` weights are gitignored by project policy (only run3 is LFS-tracked).
- Core-01 Run3 checkpoint contains numpy-serialized metadata → `torch.load(weights_only=True)` fails; `weights_only=False` required (trusted local file). Documented, not a defect.

## 4. Dataset audit (Phase 8)

| Dataset | Records | Exact-duplicate records | Split leakage |
|---|---|---|---|
| core02_reasoning | 2,386 train / 132 val / 132 test | **1,442 train dups (60%)** | 0 |
| core03_math | 1,576 / 87 / 87 | 281 train dups (18%) | 1 (val∩train) |
| core04_knowledge | 256 / 31 / 31 | 0 | 0 |
| unified_conversational v1–v4 | manifests+checksums present | — | — |

Core-02's 60% duplication is a real data-quality finding (likely template collisions); it contributes to the observed template-collapse outputs. Datasets were **not modified** (out of scope); findings recorded for the next data mission.

## 5. Generation verification (Stage-1 benchmark, CPU)

`eval_reports/stage1_four_core_generation.json` — 24-prompt × 5-model matrix, greedy, 48 tokens:

- core-01: 16/24 non-empty; English-biased word salad; 8 immediate-EOS empties.
- core-02: 24/24 text; ~5 memorized template responses regardless of prompt.
- core-03: 24/24 bare numbers; `15+27` → `22.` (wrong).
- core-04: 24/24 fluent bn/en KB sentences; prompt-insensitive recall.
- medium: 4/24; repetitive Bengali fragments.

## 6. Confirmed defects (see Stage-2 diagnosis doc)

| ID | Defect | Class | Disposition |
|---|---|---|---|
| F1 | core-01 chat prompts → immediate EOS | training limitation | documented; needs SFT (Run4/Run5) |
| F2 | `transformer.py` falsy `or` on temperature/repetition_penalty; same in `inference.py` | code defect | **FIXED** |
| F3 | `transformer.py` `.item()` EOS check — batch>1 crash | latent code defect | **FIXED** (per-row finished mask) |
| F4 | no KV cache; Python-loop repetition penalty | performance | documented (future) |
| F5 | Run3 ckpt vs `weights_only=True` | checkpoint format | documented |
| Q1–Q3 | core-02/03/04 quality = SFT data limits | training/data | documented |
| Q4 | medium `expected_params` stale (−16,384) | registry metadata | **FIXED** |

## 7. Routing/integration verification

`model_router.py` verified live (neural_only=True):
- `What is 15 plus 27?` → route `neural:nexus-core-03`, response `22.` (neural, incorrect — honest).
- `Hello! How are you?` → `neural:nexus-core-01` (gibberish but neural; no deterministic greeting in neural-only mode ✓).
- `What is artificial intelligence?` → `neural:nexus-core-04` → correct fluent answer.
- Legacy mode routes MATH→core-03 first, then deterministic calculator fallback (labeled `tool:deterministic_math`, never disguised as neural).

## 8. Files created/modified by this mission

- Modified: `core01/transformer.py` (F2+F3), `core01/inference.py` (F2), `ml-service/model_registry.py` (Q4).
- New: `evaluation/verify_four_core_generation.py`, `evaluation/four_core_test_suite.py`, `tests/four_core/test_generation_repairs.py`, `eval_reports/stage1_four_core_generation.json`, `eval_reports/four_core_test_suite.json`, this + 6 sibling audit docs.
- Pre-existing uncommitted (Phase B+C, prior missions): inference.py, pretraining_driver.py, model_config.py, current.json, COLAB_RUN4_TRAIN_CELL.py, README.md — verified, included in release.

## 9. Honest capability statement

All four cores **load strictly and generate genuine neural text from their own weights**. None is a working conversational model: core-01 is an undertrained base LM, core-02 is template-bound, core-03 emits unreliable bare numbers, core-04 is a narrow memorization model. Code correctness ≠ model intelligence; both dimensions are reported separately throughout.

## 10. Rollback

Pre-mission copies of all modified files: `backups/20261118_223409_fourcore_repair/`. Git itself is the primary rollback for tracked files.
