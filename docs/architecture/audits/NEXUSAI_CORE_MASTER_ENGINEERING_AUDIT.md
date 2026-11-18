# NEXUSAI CORE — MASTER ENGINEERING AUDIT

**Date:** 2026-11-10 · READ-ONLY investigation + planning · No implementation
**Evidence base:** all prior session audits (model inventory, forensic failure audit, provenance audit, English-origin audit, Phase-2 reports) — all verified against live files/DB/runtime this session.

## 1. Executive summary
NexusAI has a **real, working independent AI pipeline** — own Transformer, own tokenizer, own checkpoints, own CPU inference, zero external AI dependency — but the **model is undertrained and the app historically served the wrong (weakest) checkpoint**. As of today: Core-01 run3 is connected via a validated registry+router, routing/language/fallback bugs are fixed, and Run4 (60M-token multilingual corpus) is fully prepared awaiting one Colab run. The gap between "pipeline works" and "model is smart" is now purely a **training-data/compute problem**, not an engineering problem.

## 2. Verified model inventory
| Model | Arch | Params | Checkpoint | SHA-256 | Status |
|---|---|---|---|---|---|
| nexus-core-01 | core01 6L/256d/8H/1024, ctx512 | 8,842,560 | `checkpoints_core01_run3/checkpoint_final.pt` | `ad515cad…7830` ✅ | **ACTIVE** |
| nexus-medium | medium 2L/128d/2H/512, ctx128 | 2,468,928 | `checkpoints_medium/final_model.pt` (+best_model.pt dup) | `4f592af9…` | fallback |
| small×5 | SmallTransformer | 185,173 | `checkpoints/checkpoint_epoch_*` | various | excluded (SimpleTokenizer ~1K) |
| medium-epoch×5 | MediumTransformer | 4,907,594 | `checkpoints_medium/checkpoint_epoch_*` | various | excluded (char-74 vocab) |

Tokenizers: sp_bpe_8k (active, vocab 8000, multilingual-verified) + incompatible legacy ones.

## 3. Training history (verified)
- Run1/2/3: english_first 7.43M tokens, steps 447/894/1341, val_loss 4.85→4.22, resume chain verified, AUDIT_PASS
- Run3 eval: checkpoint perfect, CPU inference works (382MB, 42.6 tok/s), **quality weak** — off-topic, BN→EN, math wrong, hallucination
- Run4: **prepared not executed** — corpus 216,193 docs/~60.4M tok (60% BN), bundle+cell ready

## 4. Runtime findings (verified today)
- Active path: web→api→ml-service /orchestrate→model_router.NexusBrain→registry→core01
- Provenance proven: 25 forward calls/25 tokens; deterministic handlers labeled; retrieval disabled; no external AI
- DB audit (332 msgs): all prior answers were canned/fallback/gibberish — no hidden smart path
- Bugs fixed today: wrong ckpt, malformed current.json, Bengali intent misroute, English-only lang detect, Bengali-only fallback, /model/status 500, history-key mismatch **still open** in intelligence-engine.ts

## 5. Dataset inventory (key items)
- cleaned_bangla: 291,580 docs / ~133.9M tok (wiki+sangraha+bongchat) — validated
- run4 corpus: 216,193 docs / ~60.4M tok — built, hashed
- reasoning_v1: 3,411 train + 300 held-out — deterministic, code-verified
- english_first: 63,876 docs / 7.43M tok
- TinyStories: 60K MIT stories
- alpaca: EXCLUDED (GPT-generated); NC datasets excluded; BanglaCoRe gated

## 6. Intelligence capability — honest assessment
- Pipeline: ✅ works end-to-end
- Neural generation: ✅ real (proven)
- Answer quality: ❌ weak (undertrained)
- Reasoning/decision: ❌ not demonstrated
- Bengali generation: ❌ not yet (Run4 pending)
- Banglish: ⚠️ detection works, generation unproven

## 7. Architecture gaps
- history-key bug (context dropped) — small fix
- No streaming generation
- No self-correction/verification pass
- No specialist models (by design — foundation first)
- Memory retrieval untested

## 8. Resource constraints
CPU-only, 8GB RAM, ~5GB disk free. Core-01 fits (~400MB). Larger models need quantization or GPU-serving later.

## 9. Risk assessment
- Run4 may improve BN but EN could regress slightly (mitigated: 40% EN/mixed)
- Template reasoning data limits reasoning gains
- Colab availability uncertain → resume-safe design handles

## 10. Recommended architecture
Keep: registry+router+core01. Add later: streaming, self-check pass, instruction-tuning stage, specialist registry entries. See companion docs.

## 11. Roadmap (reordered by evidence)
1. **NOW:** Run4 Colab training (only blocker to measurable improvement)
2. Fix history-key bug + expand eval suite
3. Run5: scale to ~150M tokens + SFT stage
4. Self-correction inference pass + reasoning benchmarks
5. Specialists only if foundation eval demands
6. Public API last (after capability proven)

## 12. Exact next steps
1. User: upload corpus → Colab run cell → download run4 ckpt
2. Me: eval run4 vs run3 (same suite), promote if better
3. Fix intelligence-engine.ts history key (1-line, needs approval)
4. Update docs + report

## 13. Files that would need modification (future, pending approval)
- `apps/api/src/intelligence-engine.ts` — history key fix
- `ml-service/*` — streaming/self-check (later)
- `MODEL_DEFS` — add run4 entry on arrival
- Docs/README updates

## 14. Backup/rollback
`backups/20261110_multimodel/` has pre-change main.py+current.json. Registry/router are additive; brain path try/except-guarded → deleting 2 files + restoring backup fully rolls back.

## VERDICT: **INVENTORY COMPLETE — IMPLEMENTATION NOT APPROVED**
(Roadmap/planning stage per instructions; Run4 awaits user's Colab action.)
