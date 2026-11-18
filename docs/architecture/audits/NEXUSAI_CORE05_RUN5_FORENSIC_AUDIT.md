# NexusAI Core-05 / Run 5 Forensic Audit
Date: 2026-11-18 | HEAD: cb289fb39c6262b12c31ac459efe2a9d7f40fffd | branch: main

## Verified repository state
- 156 uncommitted entries (modified+untracked); ALL preserved untouched.
- Remote main at d278893 (4-core release); local cb289fb ahead, unpushed.

## Checkpoint inventory (VERIFIED on disk)
models/checkpoints_core01_run3/checkpoint_final.pt (~107MB, Run3 base)
models/checkpoints_core02_sft_v1|v2/checkpoint_final.pt (~82MB each)
models/checkpoints_core03_sft_v1|v2/checkpoint_final.pt (~36MB each)
models/checkpoints_core04_sft_v1|v2|v3/checkpoint_final.pt (~135MB each)
Plus legacy checkpoints under models/checkpoints/* and
packages/ai-core/{models,data}/**/checkpoints/ (experimental/phase8/10).

## Architecture fact (VERIFIED)
All 4 cores share ONE implementation: packages/ai-core/core01/transformer.py
(datasets/configs/weights independent). Configs verified:
  core01: d256 L6 H8 ff1024 vocab8000 max_len512 (~8.8M params)
  core02: d384 L8 H12 ff1536 vocab8000 max_len512 (~20.3M params)
  core03: same as core01 (~8.8M)
  core04: d512 L8 H8 ff2048 vocab8000 max_len512 (~33.4M)
NOT four independent architectures — independent configs+weights only.

## Existing Run 5 (VERIFIED — docs only, NOT executed)
- docs/audits/NEXUSAI_RUN5_SFT_READINESS_VERDICT.md: verdict
  "READY WITH CONDITIONS" for Core-01 SFT (sft_v2 dataset).
- docs/notebooks/COLAB_NEXUSAI_CORE01_RUN5_SFT_PREPARATION.py: Colab cell
  prepared; TRAINING_ENABLED=False preflight; NEVER RUN.
- Run5 = next SFT run on EXISTING Core-01. Distinct from Core-05.

## Loader compatibility (VERIFIED)
core01/sft_dataset.py: JSONL {messages:[{role,content}]}, max_len=512,
user/padding masked -100. v1-v4 records conform.

## Dataset forensic summary (v1-v4, VERIFIED)
v1 645 | v2 1054 | v3 1947 | v4 1223 (math-curated).
v4 langs: en49/bn24/banglish15/mixed2 %. multi_turn 63, math 391.
Gaps: bn/banglish depth, multi-turn volume, reasoning/decision thin.

## Tokenizer (VERIFIED earlier, unchanged)
BPE 8k model: bn 0.27-0.37 tok/char OK; banglish 0.51-0.58 fragmented;
mixed 0.51. 2819/8000 vocab pieces contain Bengali.

## No Core-05 artifacts exist
No core05 config/weights/scripts found — clean slate confirmed.
