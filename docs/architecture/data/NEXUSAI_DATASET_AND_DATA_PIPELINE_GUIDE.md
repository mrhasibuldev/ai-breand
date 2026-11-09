# NEXUSAI DATASET & DATA PIPELINE GUIDE

## Beginner glossary
- **Dataset** = the textbook the model studies.
- **Raw data** = untouched collected text.
- **Cleaning** = removing duplicates, junk, broken text.
- **Train/val/test** = study book / practice exam / final unseen exam. Test must NEVER be seen in training.
- **Tokenizer** = cuts text into small pieces (tokens) the model can read.
- **Token** = a word-piece like `▁বাংলাদেশের`.
- **SentencePiece BPE** = learns common word-pieces automatically from text.
- **Vocab size** = how many pieces the tokenizer knows (ours: 8,000).
- **Checkpoint** = saved progress (weights + optimizer + step) you can resume from.

## Actual pipeline (real paths)
1. **Collect** → `packages/ai-core/data/raw_bangla/`, `raw_english/` (immutable)
2. **Clean** → `data/cleaned_bangla/` via `clean_bangla_batch1_v2.py` (dedup, HTML strip, BN-script filter, license metadata, reject logs)
3. **Reasoning** → `data/phase2/reasoning/` via `generate_reasoning_dataset.py` (deterministic, code-verified answers)
4. **Assemble** → `data/phase2/run4_corpus/corpus_train.jsonl` via `build_run4_corpus.py` (seed 42 sampling)
5. **Train** → Colab `pretraining_driver.py` (packed 512-token sequences, causal LM, fp16)
6. **Eval** → `scripts/eval_core01_run3.py` + Colab eval cells

## Current corpus composition (verified)

| Source | Docs | ~Tokens | Lang |
|---|---|---|---|
| Bangla Wikipedia | 45,000 | 26.1M | bn |
| Sangraha BN | 9,000 | 6.5M | bn |
| BongChat | 30,000 | 3.5M | bn/mixed |
| english_first | 61,960 | 7.2M | en |
| TinyStories | 60,000 | 16.5M | en |
| reasoning_v1 ×3 | 10,233 | ~0.6M | en/bn/banglish/mixed |
| **Total** | **216,193** | **~60.4M** | BN≈60% |
