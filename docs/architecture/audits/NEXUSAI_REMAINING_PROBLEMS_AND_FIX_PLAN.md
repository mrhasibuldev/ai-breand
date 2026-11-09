# NEXUSAI — REMAINING PROBLEMS & FIX PLAN

## Issue register (severity / evidence / fix)

### Critical
1. **Model quality weak** — run3 eval: off-topic fluent text, BN→EN, math wrong, hallucination. Root cause: 7.4M-token English-only training. Fix: Run4 multilingual corpus (prepared). Blocks: useful conversation.
2. **Run4 not executed** — needs Colab GPU. Fix: user uploads corpus + runs cell.

### High
3. **Reasoning data thin** — 3,411 template examples; diversity limited. Fix: expand human-authored reasoning sets (Phase C).
4. **Banglish coverage** — only ~168 examples + bongchat mixed. Fix: dedicated Banglish corpus creation.
5. **English corpus small** — 7.4M+16.5M tokens; Chinchilla-optimal for 8.8M ≈ 175M. Fix: scale English data (FineWeb etc., license-checked).

### Medium
6. **english_first train/val near-dup** (gsm8k reworded) — pre-existing; document, acceptable pilot.
7. **Sangraha partial** (9K of ~77GB) — resume stream when disk allows.
8. **BanglaCoRe gated** — needs HF login or substitute (hishab/bangla-mmlu license check).
9. **ml-service `/model/status` 500** — `get_vocab_size` missing on wrapper (cosmetic bug).
10. **Production designation JSON malformed** — silent fallback to medium ckpt.

### Low
11. Near-template residual in reasoning test (6/300) — documented.
12. MinHash near-dup not implemented in cleaner — conservative only.

## Not blockers for Run4
Tokenizer (verified), architecture (sound), pipeline (proven), checkpoint safety (verified).
