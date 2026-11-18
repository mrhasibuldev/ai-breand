# NexusAI Four-Core Checkpoint & Model Inventory

**Verified:** 2026-11-18 against live files (SHA-256 via registry `validate()`).

## Active (registered) checkpoints

| Model ID | Checkpoint path | SHA-256 | Params | Git policy |
|---|---|---|---|---|
| nexus-core-01 | `packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt` | `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` | 8,842,560 | Git LFS (only LFS-tracked .pt) |
| nexus-core-02 | `.../checkpoints_core02_sft_v2/checkpoint_final.pt` | `906d6024511f3e8ab48f36d077be391e2eae47573fa4ba29ba8e550c690cbb18` | 20,347,712 | gitignored `*.pt`; `.sha256` sidecar committed |
| nexus-core-03 | `.../checkpoints_core03_sft_v2/checkpoint_final.pt` | `1ff83fb9ecd93944969c4086c206e2647c844c182c420b857e2f12b558d5e956` | 8,842,560 | same |
| nexus-core-04 | `.../checkpoints_core04_sft_v3/checkpoint_final.pt` | `e46383195d328b9105950939f66b0c36c6363f5b6bc5247c210efa99b5d17c48` | 33,419,072 | same |
| nexus-medium | `.../checkpoints_medium/final_model.pt` | prefix `4f592af9846b89652eb7` (full hash verified at load) | 2,452,544 | tracked historically |

## Superseded checkpoint generations (kept locally, not registered)

- `checkpoints_core02_sft_v1`, `checkpoints_core03_sft_v1`, `checkpoints_core04_sft_v1`, `checkpoints_core04_sft_v2` — earlier SFT runs; `.sha256` provenance files committed.
- `checkpoints/checkpoint_epoch_1..5.pt` — legacy SmallTransformer (tokenizer-incompatible, excluded from registry by design).
- `checkpoints_medium/checkpoint_epoch_1..5.pt` — char-level vocab variant, excluded.
- `checkpoints_retrained/` — empty.

## Tokenizer

`packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model` (+ `.vocab`), SentencePiece BPE, vocab 8000, ids pad=0 / unk=1 / bos=2 / eos=3. Shared by all registered models. Known limits: Banglish fragmentation, UNK on unseen foreign scripts.

## Config files

- `models/nexusai_core_01/config/model_config.py` (tracked)
- `models/nexusai_core_02`, `nexusai_core_03`, `nexusai_core_04` `config/model_config.py` — were untracked; committed by this mission (required at runtime by `nexus_core.get_config()`).

## Production pointer

`models/production/current.json` — designates Core-01 `1.0.0-run3` (prior approved working-tree change; verified valid JSON).

## Integrity notes

- All five registered checkpoints: strict `load_state_dict(strict=True)` PASS, 0 missing / 0 unexpected keys, parameter counts match registry `expected_params`.
- Core-01 Run3 `.pt` requires `weights_only=False` (numpy objects inside checkpoint metadata); all other checkpoints load with `weights_only=True`.
- Core-02/03/04 checkpoint weights are intentionally gitignored per project policy (`.gitignore` `*.pt`); `.sha256` provenance files ARE committed. Weight distribution is out-of-band (Drive / exports bundles). This is documented policy, not silent omission.
