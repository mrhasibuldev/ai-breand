# NEXUSAI AI BRAIN — COMPLETE BEGINNER'S GUIDE

> **Read this first if you are new to NexusAI.** Simple words, real file paths, honest status.

## 1. What is NexusAI?
NexusAI is our own **independent AI Brain** project. The goal: a language model that understands English, Bengali, and Banglish — trained on OUR data, with OUR code, running on OUR computers. It is **not** a wrapper around ChatGPT, Gemini, or Claude. No external AI answers our users.

## 2. How does a model "learn"? (simple version)
Think of it like teaching a child with a giant textbook:

- **Dataset** = the textbook (collection of texts the model reads).
- **Tokenizer** = the system that cuts sentences into small pieces called **tokens** (like `▁বাংলাদেশের`, `the`, `17`). Our tokenizer is SentencePiece BPE with 8,000 pieces — it already knows Bengali, English, and mixed text.
- **Training** = the child reads the book millions of times and learns which token usually comes next.
- **Loss** = a score for "how wrong" the guesses are. Lower = better. Train loss = score while studying; validation loss = score on practice questions never shown during study.
- **Overfitting** = memorizing the book instead of learning (bad — model repeats instead of understanding).
- **Checkpoint** = a saved progress point (weights + optimizer + step counter). Like a game save — you can stop and resume exactly.
- **GPU** = fast graphics card used ONLY for training (rented temporarily on Colab/Kaggle — free).
- **CPU inference** = after training, the saved model runs on a normal laptop — no GPU, no internet AI needed.

## 3. What we have actually built (verified)

| Thing | Status | Where |
|---|---|---|
| Transformer model (Core-01) | DONE — 8,842,560 params | `packages/ai-core/core01/transformer.py` |
| Tokenizer | DONE — multilingual | `packages/ai-core/data/experimental/phase9_2/tokenizers/bpe_8k/` |
| Training code | DONE — tested 3 runs | `packages/ai-core/core01/pretraining_driver.py` |
| Datasets | DONE — EN+BN corpus built | `packages/ai-core/data/` |
| Run3 checkpoint | DONE — verified | `models/checkpoints_core01_run3/checkpoint_final.pt` |
| CPU inference | DONE — 42 tok/s | `core01/inference.py` |
| Run4 training | PREPARED — needs Colab | `docs/notebooks/COLAB_RUN4_TRAIN_CELL.py` |

## 4. Training history (real numbers)
Run1: 447 steps, val loss 4.85 → Run2: 894 steps, 4.47 → **Run3: 1,341 steps, 4.22** — improving but still weak (undertrained: only 7.4M English tokens).

## 5. Honest current capability
- ✅ Generates English text offline on CPU
- ❌ Answers are often off-topic/generic
- ❌ Bengali/Banglish: not yet trained (Run4 will fix)
- ❌ Math/reasoning/decisions: not demonstrated
- See `docs/architecture/audits/NEXUSAI_CORE01_RUN3_FINAL_CPU_EVALUATION_REPORT.md`

## 6. The data pipeline (real paths)
`raw_*` (immutable) → `cleaned_bangla/` → `phase2/reasoning/` → `phase2/run4_corpus/corpus_train.jsonl` (216K docs, ~60M tokens, 60% Bengali) → Colab training → checkpoint → local CPU.

## 7. What's next
1. Upload corpus to Drive → run `COLAB_RUN4_TRAIN_CELL.py`
2. Download run4 checkpoint → evaluate vs run3
3. Iterate: more data, instruction tuning, reasoning stages

## 8. Key documents
- Status: `docs/architecture/audits/NEXUSAI_CURRENT_AI_BRAIN_STATUS.md`
- History: `docs/architecture/audits/NEXUSAI_MODEL_TRAINING_HISTORY.md`
- Data: `docs/architecture/data/NEXUSAI_DATASET_AND_DATA_PIPELINE_GUIDE.md`
- Licenses: `docs/architecture/data/NEXUSAI_DATASET_LICENSE_AND_PROVENANCE_REGISTRY.md`
- Problems: `docs/architecture/audits/NEXUSAI_REMAINING_PROBLEMS_AND_FIX_PLAN.md`
- Roadmap: `docs/architecture/future/NEXUSAI_AI_BRAIN_DEVELOPMENT_ROADMAP.md`
- Voice: `docs/architecture/future/NEXUSAI_REALTIME_VOICE_CONVERSATION_ROADMAP.md`
- GPU/CPU guide: `docs/architecture/training/NEXUSAI_GPU_TRAINING_LOCAL_CPU_INFERENCE_GUIDE.md`
