# NexusAI Four-Core Operations & Inference

**Verified commands (CPU, repo root, Python env with torch+sentencepiece):**

## Load & generate a core directly

```python
import sys
sys.path.insert(0, "packages/ai-core")
sys.path.insert(0, "packages/ai-core/models")
sys.path.insert(0, "packages/ai-core/ml-service")
import model_registry as mr

# validate (hash+tokenizer) then load+generate
txt, prov = mr.registry.generate("nexus-core-04", "What is artificial intelligence?",
                                max_new_tokens=64, do_sample=False)
print(txt); print(prov["checkpoint"], prov["checkpoint_sha256"][:16])
```

Model IDs: `nexus-core-01`, `nexus-core-02`, `nexus-core-03`, `nexus-core-04`, `nexus-medium`.

## Router path (what the app uses)

```python
from model_router import brain
r = brain.respond("What is 15 plus 27?", neural_only=True)
# r["trace"]["route"] == "neural:nexus-core-03"; r["response"] is neural text
```

`neural_only=True` = no deterministic handlers; failures return `error.code == "MODEL_GENERATION_FAILED"`.

## Verification suites

```bash
# strict load + 24-prompt x 5-model generation matrix
python packages/ai-core/evaluation/verify_four_core_generation.py \
    --models nexus-core-01,nexus-core-02,nexus-core-03,nexus-core-04,nexus-medium \
    --max-new-tokens 48 --out eval_reports/stage1_four_core_generation.json

# held-out per-core test suite (core-02/03/04 test.jsonl + core-01 authored set)
python packages/ai-core/evaluation/four_core_test_suite.py \
    --out eval_reports/four_core_test_suite.json

# repair regression tests
python packages/ai-core/tests/four_core/test_generation_repairs.py
```

## Checkpoint handling

- Weights `*.pt` are gitignored by policy; `.sha256` sidecars are committed. Verify integrity:
  `python -c "import hashlib;print(hashlib.sha256(open('packages/ai-core/models/checkpoints_core01_run3/checkpoint_final.pt','rb').read()).hexdigest())"` — compare with registry constants in `model_registry.py`.
- Core-01 Run3 needs `torch.load(..., weights_only=False)` (numpy metadata); other checkpoints work with `weights_only=True`.
- Never overwrite checkpoints; save new runs to new versioned dirs (`checkpoints_core0X_<run>/`).

## Training (existing pipeline, CPU-verified structure; GPU runs are Colab cells)

- SFT: `core01/sft_dataset.py` serialization + `core01/training.py` loop; per-core builders `data/build_core0X_*.py` produce `data/core0X_*/{train,validation,test}.jsonl`.
- Pretraining: `core01/pretraining_driver.py` (zero-step guard prevents false completion).
- Colab: `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` (authorization-gated, hash-verified resume).

## Known runtime limits

- No KV cache → generation cost grows quadratically with context; CPU only.
- Repetition penalty implemented as a Python loop — slow on long sequences.
- `max_len` 512 for all cores (core-01/03/04), medium 128.
