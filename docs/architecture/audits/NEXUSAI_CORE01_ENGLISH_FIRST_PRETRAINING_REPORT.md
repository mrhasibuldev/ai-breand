# NexusAI Core-01 — Phase 5: Padding Optimization + English-First Pretraining Preparation

**Date:** 2026-11-07
**Scope:** padding-waste fix, packed-sequence dataset, English dataset research, training driver, CPU tests.
**Not done:** no training, no downloads, no GPU session, no commits.

---

## 1. Executive Summary

- **Padding waste CONFIRMED and FIXED.** `TextDataset` padded every line to 512 tokens → measured **95–98% padding** on real corpora. New `PackedTextDataset` concatenates the token stream into fixed 512-token blocks → **~0.008% padding** on the 3.47M-token corpus (270 pad tokens total).
- **Measured speedup:** packed DataLoader ~**12.5M slots/s** vs `TextDataset` ~**124k useful tokens/s** (on-the-fly per-item tokenization) — roughly **two orders of magnitude** more useful tokens per second on CPU.
- **Training driver implemented** (`core01/pretraining_driver.py`) — config-driven, packed data, doc-level split, AMP/accumulation/checkpoint/resume/logging, safe interrupt.
- **English dataset candidates researched** — FineWeb (ODC-By), DCLM-baseline (CC-BY-4.0), C4 (ODC-By), Wikipedia (CC BY-SA), Project Gutenberg (public domain) documented with caveats; **none downloaded — owner approval required**.
- All existing regression suites still pass; Core-01 remains **UNTRAINED**, 8,842,560 params.

## 2. Root Cause of Padding Waste (verified in code)

`TextDataset.__getitem__` (`core01/dataset.py`) treated **each text line as one example**: tokenize → pad to `max_len=512` → shift. Corpus lines average ~30–110 tokens, so ~95% of every batch was `pad_id`. Additionally `TextDataset` tokenizes **on every `__getitem__`**, making the DataLoader CPU-bound (~124k useful tok/s measured). No attention mask was passed, so pad positions also participated in attention (pad embedding is a zero vector via `padding_idx`; loss ignores them via `ignore_index=pad_id`) — wasteful but not incorrect.

## 3. Files Changed

| File | Change |
|---|---|
| `packages/ai-core/core01/dataset.py` | +`PackedTextDataset` (uint16 token stream, `.npy` cache, blank-doc skip, trailing partial block padded); `split_dataset` now shuffles a **copy** (was mutating caller's list — real bug); +`import numpy` |
| `packages/ai-core/core01/training.py` | `PretrainingEngine.train_epoch` gained optional `on_step` callback (backward compatible, default `None`); no math/optimizer changes |
| `packages/ai-core/core01/pretraining_driver.py` | **NEW** — CLI driver (see §6) |
| `packages/ai-core/core01/__init__.py` | export `PackedTextDataset` |
| `exports/nexusai_core01_kaggle_package/` + `.zip` | synced 4 changed files, added driver → **14 files**, new SHA-256 `a20d9abe…f4f08`, size 297,240 B; manifest updated |
| `exports/NEXUSAI_CORE01_GPU_DIAGNOSTIC` notebook | **unchanged** — still valid (imports unaffected) |

Architecture, tokenizer, vocab, special IDs, checkpoints: **untouched**. Param count re-verified 8,842,560.

## 4. Before/After Measurements (actually executed, CPU)

Corpus: `phase7/tokenizer_corpus/corpus_combined.txt` — 99,097 docs, 3.47M tokens.

| Metric | TextDataset (before) | PackedTextDataset (after) |
|---|---|---|
| Padding | **95.0%** (phase9_2 sample) / ~98% (short-line sample) | **0.008%** (270 pad tokens / 3.47M) |
| Examples per epoch | 99,097 (mostly empty) | 6,774 blocks × 512 |
| Useful tokens/s (DataLoader) | ~124,000 | ~12,470,000 real tok/s |
| Token storage RAM | re-tokenize every step | 6.9 MB uint16 array (+0.02 s cache reload) |
| Build time | n/a (per-step) | 5.0 s one-time (99k docs), cached |
| GPU memory | n/a (CPU env) | **NOT TESTED** — no CUDA locally |

Small-corpus caveat: with tiny inputs the single trailing partial block can be a noticeable *fraction* (still ≤ one block absolute); on real corpora it is negligible.

**Packing semantics:** docs encoded `BOS…EOS`, concatenated, sliced into 513-token blocks → `input=[:-1]`, `target=[1:]`. EOS→BOS marks boundaries; cross-boundary attention within a block is the standard GPT-style trade-off (documented in code). Train/val split is at **document level before packing** → no leakage. `pad_id` targets are ignored by loss (`ignore_index`).

## 5. English Dataset Candidates (license-verified via official sources)

| Dataset | Source | Size | License / terms | Caveats | Verdict |
|---|---|---|---|---|---|
| **FineWeb** (`HuggingFaceFW/fineweb`, `sample-10BT` subset) | huggingface.co | 18.5T tokens total; 10B-token sample | **ODC-By 1.0** + CommonCrawl ToS; attribution required | CC ToS applies; underlying page copyrights remain with authors (ODC-By §2.4) — same caveat as all web corpora | **RECOMMENDED** — best quality/size ratio, modern dedup+filtering |
| **DCLM-baseline-1.0** | huggingface.co/datasets/mlfoundations | 4T tokens / ~780k docs shown | **CC-BY-4.0** | Card says research-oriented; acknowledges copyrighted material possible | ACCEPTABLE w/ attribution; research-use framing |
| **C4** (`allenai/c4`, `en` split) | huggingface.co | 305 GB en | **ODC-By** + CC ToS | April-2019 snapshot — dated; heuristic cleaning only | ACCEPTABLE backup |
| **English Wikipedia** | dumps.wikimedia.org | ~20+ GB XML | **CC BY-SA 3.0/4.0** | Share-alike + attribution; narrow domain | GOOD SUPPLEMENT |
| **Project Gutenberg** | gutenberg.org | ~70k books | **Public domain** | Older literary style; needs cleanup | GOOD SUPPLEMENT |
| OpenWebText2 | github.com/EleutherAI | 65.9 GB / 17.1M docs | Repo MIT; **content = scraped web — terms UNVERIFIED** | Reddit-derived; license of content unclear | **EXCLUDED (UNVERIFIED)** |
| Books3 / The Pile / SlimPajama | various | large | Mixed/unclear per-subset | Copyright questions | **EXCLUDED** |

**Recommendation:** FineWeb `sample-10BT` (first shards) as primary English corpus + Wikipedia/Gutenberg supplements. All require **owner-approved download** (Kaggle-side preferred — local C: has ~4.8 GB free). For an 8.8M-param model even ~100M–1B tokens is far beyond Chinchilla-optimal needs; FineWeb sample is more than sufficient.

**Dataset prep pipeline design (implemented pieces + plan):**
- Implemented now: doc-level seeded split (`split_dataset`, deterministic, non-mutating), exact-duplicate removal is trivial at line level (caller-side), `PackedTextDataset` + `.npy` token cache, provenance via manifest JSON (to be written by download step).
- Planned (needs approval to add code): NFC normalization, length filter (drop <N chars), exact dedup (hash set), optional MinHash near-dedup, language-ID filter (fastText lid.176 needed → new dep, defer), quality heuristics (perplexity filter optional), corpus manifest with source/license/sha256 per file.

## 6. Training Driver — `core01/pretraining_driver.py`

CLI: `--train-file` (.txt/.jsonl/.json) `--val-file|--val-fraction` `--output-dir --device --precision --epochs --max-steps --batch-size --gradient-accumulation-steps --learning-rate --weight-decay --grad-clip --warmup-steps --checkpoint-interval --eval-interval --log-interval --resume --seed --tokenizer`.

- Document-level split **before** packing (no leakage); packed train/val token caches saved as `.npy` (resume-friendly).
- `on_step` callback → per-step logging, mid-epoch eval+checkpoint at intervals, `--max-steps` clean stop, `KeyboardInterrupt` → emergency checkpoint.
- Resume: `--resume <file>` → `engine.load_checkpoint` restores model/optimizer/scheduler/**RNG**/step/epoch (approximate-resume limitation documented previously remains: sampler position not checkpointed).
- 0-batch guard, clear errors for empty corpus/missing files.
- **SFT gate and all Phase 4.x safety features untouched.**

## 7. Proposed Initial Training Config (Kaggle T4, single GPU `cuda:0`)

| Param | Value | Why |
|---|---|---|
| device | `cuda` (one T4) | No DDP/DataParallel implemented — x2 unusable as one job |
| precision | `fp16` | T4 = sm_75, no BF16; `resolve_amp_dtype` auto-falls-back anyway |
| batch_size | 32 | micro-batch; 8.8M model → activations ~1–2 GB, far under 16 GB |
| gradient_accumulation | 1–2 | effective batch 32–64 seqs ≈ 16–32k tokens/step |
| max_len | 512 | packed blocks fully utilized now |
| lr | 3e-4 | config default; appropriate for 8.8M model, short warmup tolerant |
| warmup | 100–500 steps | linear warmup already implemented |
| LR decay | none yet | acceptable for stage-0; add cosine before long runs |
| grad_clip | 1.0 | config default |
| checkpoint_interval | 250–500 steps | ~150–200 MB/ckpt (model+opt+scheduler+RNG) |
| eval_interval | 500 steps or per-epoch | val_loss on held-out packed blocks |
| stopping | fixed step budget + val_loss plateau inspection | no early-stopping code yet — manual review |

Expected throughput: est. ~50k–200k tok/s on T4 (small-model launch-bound); entire current 3.47M-token corpus ≈ minutes — **stage-0 only validates the pipeline; real run needs the approved English corpus.**

## 8. Test Results (actually executed)

| Suite | Result |
|---|---|
| Phase-5 new (`test_phase5_packing.py`) | **24/24 PASS** — packing correctness, shift alignment, EOS counts, pad reduction, doc-level split determinism/no-overlap, cache, `on_step`, driver end-to-end + resume, param count |
| Phase 4.2.2 corrections | 12/12 PASS |
| Phase 4.2 safety | 23/23 PASS |
| Phase 4.3 masking/splits | 14/14 PASS |
| Phase 4.3.1 SFT gate/resume | 19/19 PASS |
| Updated Kaggle ZIP re-validation | diagnostic **13/13 PASS** (CPU mode) |
| Core-01 regression (9-test) | unchanged — no architecture edits |
| **Total** | **102/102 PASS** (incl. diagnostic) |

Notes:
- Old `test_gradaccum_math.py` diagnostic prints "UNDER-SCALED" — it is the **pre-4.2.2 diagnostic** run without dropout=0 seed control; its measurement is noisy (dropout RNG), superseded by the deterministic Phase-4.2.2 suite (12/12). Gradient math itself was not touched this phase.
- **GPU tests: NOT TESTED** (no CUDA locally). Packed-data GPU step-time/VRAM must be measured on Kaggle.
- Driver smoke test used 60 synthetic docs, CPU, fp32 — verified checkpoint + resume path only, not training quality.

## 9. Remaining Blockers

1. **No approved English corpus downloaded** — current 3.47M-token corpus is ~2% of a reasonable target and 0.03% Bengali.
2. Near-duplicate detection not implemented (only exact dedup planned).
3. LR decay schedule absent.
4. Multi-GPU absent (by design for now — single T4).
5. Exact-resume still approximate (sampler state) — documented.
6. `sentencepiece` not in ml-service requirements (Kaggle has it preinstalled).

## 10. Exact Next Actions Requiring Owner Approval

1. **Approve English dataset download** — recommend FineWeb `sample-10BT` subset (+ optional Wikipedia/Gutenberg), destination = Kaggle Dataset or local staging; confirm license acceptance (ODC-By attribution).
2. **Approve corpus-prep code** — cleaner/dedup/manifest script (new file, no architecture change).
3. **Approve stage-0 run** — driver on existing corpus, e.g. `--max-steps 500`, single T4, to measure real tok/s + VRAM + verify checkpoint/resume on GPU.
4. **Approve real pretraining config** after stage-0 metrics.
5. Re-upload updated `nexusai_core01_kaggle_package.zip` (new SHA above) to Kaggle when ready.

## Final Answers

- **Padding optimization complete?** YES — implemented, measured (~95%→0.008%), tested 24/24.
- **English dataset ready?** NO — candidates verified, but nothing downloaded; owner approval required.
- **Training driver ready?** YES (CPU-tested end-to-end incl. resume); GPU run NOT TESTED.
- **Core-01 still UNTRAINED?** YES — 8,842,560 params, random init, status unchanged.
- **Can first pretraining safely begin?** Pipeline-wise yes for a bounded stage-0 run; **meaningful pretraining NO** — corpus insufficient.
- **Approval needed next?** Dataset download (FineWeb sample) + stage-0 run authorization.
