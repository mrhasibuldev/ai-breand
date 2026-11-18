# NexusAI Core-05 — Tokenizer Readiness Report

**Status:** READ-ONLY diagnostics completed. No tokenizer modification.

## Asset
- File: `packages/ai-core/data/experimental/phase9_2/tokenizer/bpe_8k/sp_bpe_8k.model` — actual path `.../phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model` (+ `.vocab`)
- Type: SentencePiece BPE; vocab_size reported 8000 by `get_piece_size()`
- Special IDs: pad=0, unk=1, bos=2, eos=3 — match `NexusAICore01Config` defaults; `tokenizer_interface._validate_compatibility` enforces vocab match and warns on ID drift. VERIFIED.

## Measured diagnostics (read-only, this audit)

| Text | chars | tokens | UNK | tok/char |
|---|---|---|---|---|
| English sentence | 42 | 10 | 0 | 0.24 |
| Bengali script | 32 | 9 | 0 | 0.28 |
| Banglish (Romanized Bengali) | 32 | 13 | 0 | 0.41 |
| Mixed incl. foreign script | 38 | 16 | 1 | 0.42 |

Piece-level evidence: Banglish fragments aggressively (`Programming`→`Pro gr am ming`, `shikhAR`→`sh ik h ar`); Bengali script forms whole-word pieces (`প্রোগ্রামিং`); foreign scripts → UNK.

## Findings

1. **English:** efficient, low fragmentation. READY.
2. **Bengali script:** acceptable fragmentation; no UNK on tested samples. PARTIALLY READY — quality on rare words/inflections unverified at scale.
3. **Banglish:** heavy fragmentation (~1.7× English token cost). This inflates sequence length, wastes context budget, and makes learning Romanized-Bengali patterns harder. PARTIALLY READY — usable but a quality ceiling.
4. **Mixed/code-switched:** works but foreign scripts produce UNK. Acceptable if V5 avoids non-Bengali/English scripts.
5. **max_len interaction:** at max_len=512, a Banglish heavy multi-turn conversation may truncate sooner than English. At proposed 1024, mitigated.

## Verdict: PARTIALLY READY

The 8K tokenizer is **adequate for an initial Core-05 SFT experiment** but is a **known quality limiter for Banglish and long mixed conversations**. It does NOT block training; it caps achievable multilingual fluency.

## Recommendation (future mission, not now)
- Option A (low cost): keep 8K tokenizer; accept Banglish ceiling.
- Option B (better): train a larger SentencePiece BPE (e.g., 16K–32K) on a balanced bn/en/banglish corpus — requires tokenizer retraining mission + all checkpoints' vocab_size updated. NOT authorized now.
- Do NOT assume dataset expansion alone fixes fragmentation — tokenization is a vocab/merge-table property.
