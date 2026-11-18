# NexusAI Stage-2 — Root-Cause Diagnosis

**Basis:** Stage-1 benchmark (`eval_reports/stage1_four_core_generation.json`), source inspection of `core01/transformer.py`, `core01/inference.py`, `core01/tokenizer_interface.py`, `nexus_core.py`, `ml-service/model_registry.py`, `ml-service/model_router.py`. Read-only; no code modified.

## A. Verified code-level findings

### F1 — Core-01 EMPTY_OUTPUT on chat-style prompts (model limitation + prompt-format mismatch)
- **Evidence:** `Hello! How are you today?` → first argmax token = id 3 (EOS), logit 10.48 vs next-best 9.67. Generation stops after 1 token → decoded text empty → `EMPTY_OUTPUT` warning. 8/24 prompts affected, all ~0.02 s.
- **Root cause:** Core-01 Run3 is a *pretrained document LM* (PackedTextDataset format `[BOS] text [EOS]`). Chat prompts are not in its training distribution; the model treats them as complete documents and emits EOS. Not an inference bug — `inference.py` correctly prepends BOS without EOS (fixed in Phase B+C).
- **Classification:** model/training limitation. **Severity:** high for chat use; expected — SFT (Run4/Run5) is the planned remedy.
- **Proposed fix:** none in inference code. Optional future: SFT prompt format `user:/assistant:` (already implemented in `sft_dataset.py`/`nexus_core.chat_prompt_ids`).

### F2 — `generate()` sampling-parameter falsy bug (minor code defect)
- **File:** `core01/transformer.py:408,411` — `temperature = temperature or self.config.temperature`; `repetition_penalty = repetition_penalty or self.config.repetition_penalty`.
- **Effect:** explicit `temperature=0.0` or `repetition_penalty=1.0` silently fall back to config defaults. `do_sample=False` makes temperature harmless for argmax, but the pattern is fragile.
- **Classification:** code defect (latent). **Severity:** low. **Fix:** use `is not None` checks (same pattern already used for `top_k`/`top_p` on lines 409–410).

### F3 — Batch-EOS early-exit bug (latent)
- **File:** `core01/transformer.py:466` — `if next_token.item() == self.config.eos_id: break` uses `.item()` on a `[batch,1]` tensor; works only for batch_size=1 and stops the entire batch when any row emits EOS.
- **Classification:** code defect (latent; all current callers use batch=1). **Severity:** low now, blocking for future batching. **Fix:** per-row finished-mask tracking.

### F4 — Generation performance: no KV cache + Python-loop repetition penalty
- **File:** `core01/transformer.py:413–468`.
- **Effect:** full forward pass over the whole sequence per token (O(n²)); repetition penalty iterates `set(input_ids.tolist())` in Python every step. Measured: core-04 avg 1.18 s/gen at 48 tokens on CPU — usable for chat, poor for long outputs.
- **Classification:** infrastructure/performance limitation. **Severity:** medium. **Fix (future):** KV-cache decode path; vectorized penalty. Not required for correctness.

### F5 — Core-01 checkpoint `weights_only=True` incompatibility
- **Evidence:** `torch.load(weights_only=True)` raises `UnpicklingError` on `numpy._core.multiarray._reconstruct` (numpy arrays inside checkpoint metadata, e.g. `rng_state`). Registry's `CheckpointManager` path loads successfully.
- **Classification:** checkpoint-format limitation, not corruption (SHA-256 verified). **Severity:** low; affects only strict `weights_only` consumers. **Fix (future):** re-save checkpoints with numpy-free metadata or register safe globals.

## B. Model-quality findings (not code defects)

### Q1 — Core-02 template collapse
- 20.3M-param SFT model emits ~5 memorized response patterns (`1. Boil water. 2. Add tea leaves.`, `No, {a} studies.`, `No, Arif finished first.`) for all 24 prompts including math and Bengali.
- **Root cause:** SFT dataset (`checkpoints_core02_sft_v2`, "clean question-level split") is dominated by narrow template/slot-fill reasoning items; model memorized surface forms. Registry already warns "template-trained; held-out generalization limited".
- **Classification:** data/training limitation. **Severity:** high for general use; matches its "specialist_reasoning" label only within trained patterns. **Fix:** requires new training data — out of scope.

### Q2 — Core-03 number-collapse
- Emits bare numbers (`15.`, `83.`, `2/8.`) for every prompt; `15 plus 27` → `22.` (wrong).
- **Root cause:** math SFT taught answer-only numeric format; model has no concept of non-math input rejection. Router is expected to gate intent (MATH intent → core-03 only).
- **Classification:** training/data limitation + missing router-side guard for out-of-domain prompts. **Severity:** medium. Note: `model_router.py` only routes `intent=="MATH"` to core-03 — direct registry calls bypass this.

### Q3 — Core-04 prompt-insensitive memorization
- Fluent Bengali/English KB sentences, but nearest-neighbor recall over 318 curated records; greetings/math elicit unrelated KB facts. Occasional script mixing (`-এর জন্য সূর্যের`).
- **Root cause:** small curated corpus + memorization training; registry label "memorization model; narrow coverage" is accurate.
- **Classification:** data/training limitation. **Severity:** medium; best current model within its domain.

### Q4 — nexus-medium registry param-count mismatch
- Actual 2,452,544 vs registry `expected_params` 2,468,928 (−16,384 = e.g., one 128×128 matrix). Strict load passes with 0 missing/unexpected keys, so the checkpoint matches the built model — the registry metadata is stale/wrong.
- **Classification:** registry metadata defect. **Severity:** low (fallback-only model). **Fix:** correct `expected_params` to 2,452,544 or recompute from `MediumTransformer` definition — requires owner approval (registry change).

### Q5 — Core-01 quality: undertrained base LM
- Output is English-biased word salad with math-corpus artifacts (`<<a+b=c>>`, `####`), regardless of prompt language. Train loss ≈4.43 after 3 epochs on english_first corpus.
- **Classification:** training limitation. Run4 (2 more epochs) is planned but unexecuted; Run5/SFT requires separate authorization.

## C. Infrastructure findings

### I1 — Router honesty: VERIFIED clean
- `model_router.py` labels deterministic routes explicitly (`deterministic:greeting`, `tool:deterministic_math`, `registry:*_metadata`, `fallback`) and never represents them as neural. `neural_only=True` mode restricts candidates to `nexus-core-01/03/04` and returns explicit `MODEL_GENERATION_FAILED` errors — no silent fallback. Provenance dict includes checkpoint path + SHA-256.
- **Note:** `_generate_neural` falls back from core-01 to `nexus-medium` in legacy mode — labeled via `prov`, acceptable but medium is gibberish-prone.

### I2 — Tokenizer
- SentencePiece BPE 8K wrapper verified: bos=2, eos=3, pad=0 consistent across all models. Banglish fragmentation and UNK on foreign scripts remain known data limitations (measured previously), not code defects.

## D. Severity summary

| ID | Type | Severity | Needs code fix? |
|---|---|---|---|
| F1 | model limitation | High (chat) | No — needs SFT/training |
| F2 | latent code defect | Low | Yes (1-line, `is not None`) |
| F3 | latent code defect | Low | Yes (batch EOS mask) |
| F4 | performance | Medium | No (KV cache = future work) |
| F5 | checkpoint format | Low | No (re-save or safe-globals) |
| Q1–Q3 | training/data | High/Medium | No — new data/training required |
| Q4 | registry metadata | Low | Yes (constant correction) |
| I1/I2 | — | Clean | No |

## E. Recommended minimal fix set (pending owner approval)

1. `transformer.py:408,411` — `is not None` guards for temperature/repetition_penalty (F2).
2. `transformer.py:466` — per-row EOS tracking for batch safety (F3) — optional, batch=1 today.
3. `model_registry.py` — correct `nexus-medium.expected_params` → 2,452,544 (Q4).
4. Add regression tests: falsy-parameter handling, batch>1 EOS, registry param-count consistency.

Everything else is training/data-dependent and must not be "fixed" in code.

## F. Not performed

No source, checkpoint, tokenizer, config, router, API, DB, or UI changes. No training. No Git commit/push.
