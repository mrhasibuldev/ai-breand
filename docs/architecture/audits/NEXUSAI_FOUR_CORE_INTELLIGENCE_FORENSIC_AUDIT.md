# NexusAI Four-Core Intelligence Forensic Audit

Read-only audit. Baseline: `cb289fb` local (remote `d278893`, unpushed).
No training, no runtime changes, no commits.

## A. Git safety — VERIFIED
HEAD `cb289fb`; 147 uncommitted entries (pre-existing user work +
mission artifacts) preserved. v1 dataset untouched (645 records intact).

## B–D. Model inventory & architecture — VERIFIED
All four cores share ONE Transformer implementation
(`core01/transformer.py` pre-norm decoder-only) with independent
configs/weights — NOT four different architectures. Params: c01/c03
8.84M, c02 20.35M, c04 33.42M. Tokenizer shared: sp_bpe_8k (vocab 8000,
sha 2fcc6a87…). Checkpoints + SHA-256 verified previously; registry
loads strict+lazy; neural-only path verified live (cb289fb).

## E. Bengali conversational root-cause matrix (VERIFIED evidence)

| Suspected issue | Evidence | Confidence | Correction |
|---|---|---|---|
| Banglish/mixed tokenizer fragmentation | sp_bpe encodes "Tumi kemon acho?" → 29 tokens/50 chars (0.58 tok/char), pieces like ▁T,um,i,▁k,em,on — near char-level | VERIFIED | retrain/extend tokenizer with Banglish vocab OR accept en-bn only near-term |
| Bengali script tokenization OK | "বাংলাদেশের রাজধানী কী?" → 6 tokens, whole-word pieces; 2819/8000 vocab pieces contain Bengali | VERIFIED (not the bottleneck) | — |
| Insufficient paired bn conversational SFT | largest bn SFT assets: ~590+151 cleaned texts UNPAIRED; v1+v2 bn SFT records ~300 total | VERIFIED | v2/v3 conversational expansion (in progress) |
| Multi-turn absence | v1 had 6 multi-turn; v2 has 35 — still far below need | VERIFIED | scenario-driven expansion |
| Uncertainty/refusal scarcity | v1: 17+4; v2: 27+4 — small but present | VERIFIED | keep expanding |
| Code-mixed garbage tokens | " teachersএর" splits into 'te','acher','s','এ','র' — mixed-script compounds fragment badly | VERIFIED | data-level: avoid awkward code-mix in training text |
| Small model capacity | 8.8M params vs task complexity | PARTIAL | more data first; architecture change only if evidence demands |

## F. Tokenizer/language analysis — VERIFIED
- en: 0.29 tok/char — efficient.
- bn script: 0.27-0.37 tok/char — good.
- banglish romanized: 0.51-0.58 tok/char — severe fragmentation.
- mixed bn+en compounds: worst fragmentation.
Conclusion: written Bengali is NOT tokenizer-limited; the weak bn chat
comes from DATA scarcity (paired conversational bn SFT ~hundreds of
records) + multi-turn absence. Banglish is BOTH tokenizer-limited AND
data-limited — treat as research problem, not quick fix.

## G. Dataset v1 integrity — VERIFIED
645 approved / 27 rejected (dup_question); 581/32/32 splits; manifests+
checksums intact; builder reproduces deterministically (SEED=42).

## H–R. v2 construction — see construction report
1054 approved / 51 rejected; v1 carryover + scenarios + reasoning/
decision/self_correction/clarification + procedural math/logic.
Multi-turn 35 (still below 300-500 goal — PARTIAL). Language dist
en53/bn32/banglish15/mixed<1 — off the bn40/en30/banglish20/mixed10
target — PARTIAL, documented.

## S–V. Core readiness
- Core-01: v2 usable for pilot conv-SFT; needs more bn/banglish/multi-turn — PARTIAL.
- Core-02: reasoning/decision records added (13+7) — still thin vs its template-bias problem — PARTIAL.
- Core-03: math 582 verified procedural — USABLE (best-covered core).
- Core-04: knowledge 33 + uncertainty 27 + refusal 4 — direction right, volume small — PARTIAL.

## W–AC. Benchmark/training/Colab — documented in roadmap doc.
