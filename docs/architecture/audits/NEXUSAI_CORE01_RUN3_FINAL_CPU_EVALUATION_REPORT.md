# NEXUSAI CORE-01 RUN3 — FINAL CPU EVALUATION REPORT

**Date:** 2026-11-09 · READ-ONLY eval · All outputs verbatim from native `core01` InferenceEngine path (strict state_dict load, greedy, CPU)

## PHASE A — Checkpoint integrity: **PASS**

| Check | Expected | Actual | Status |
|---|---|---|---|
| Path | `models/checkpoints_core01_run3/checkpoint_final.pt` | same | PASS |
| Size | 106,777,501 B | 106,777,501 B | PASS |
| SHA-256 | `ad515c…7830` | `ad515cadea433d1782e9f1d5f8806d850ee519b86b42b4b9db11c3b3f4bb7830` | **PASS exact match** |
| Loadable | yes | `torch.load` OK | PASS |
| Keys | model/opt/scheduler/rng/config | all present | PASS |
| Meta | step 1341, epoch 3, PRETRAINING_COMPLETED, tl 4.4259, vl 4.2169 | identical | PASS |

## PHASE B — Tokenizer: **PASS**
sp_bpe_8k vocab 8000; EN/BN/Banglish encode+decode OK; 0% UNK on tested samples [prior verified].

## PHASE C — Native loading: **PASS**
`NexusAICore01(cfg).load_state_dict(strict=True)` — 0 missing/unexpected keys, 8,842,560 params confirmed.

## PHASE D — Generation results (verbatim; full log `eval_reports/core01_run3/cpu_eval.json`)

Pattern across ALL 22 prompts: fluent English surface text but **off-topic/generic** — model reproduces corpus-style fragments ("The first person is…", "a good way to get a car"), ignores question semantics.

| Category | Result | Evidence |
|---|---|---|
| English QA | FAIL | answers are generic text, not answers |
| Bengali | FAIL | outputs English only — no BN generation |
| Banglish | FAIL | outputs English only |
| Math | FAIL | e.g. 17×23 → irrelevant story; 100−37 → wrong template |
| Reasoning | FAIL | generic paragraphs, no reasoning |
| Decision | FAIL | no decision logic |
| Abstention | FAIL | invents confident nonsense for fake entities |

Sample verbatim:
- `What is 17 times 23?` → "The total number of goals in the first year…"
- `তুমি কে?` → "The following are the most popular sports…"
- `What is the capital of Zzyzxq?` → hallucinated US-city description

## PHASE E — CPU benchmark [VERIFIED]
- Checkpoint load: 0.1s (weights_only load) · strict model load: instant
- RAM: 322MB after ckpt, **382MB peak** during eval
- Generation: **42.6 tok/s avg**, 22 prompts in 23.6s
- Hardware: Windows CPU (torch cpu), stable, no errors

## PHASE F — Independence: **PASS**
Path uses only torch + sentencepiece + numpy. No external AI API anywhere in core01 inference.

## Root cause
Model trained 3 epochs on 7.4M-token English corpus → learned surface English style, **no semantic QA capability**. Bengali/Banglish absent from training. This is expected for the data scale — not a code defect.

## FINAL VERDICT: **PARTIALLY VERIFIED — INFERENCE WORKS, CAPABILITIES LIMITED**

Mechanically: real checkpoint loads, generates on CPU offline at usable speed, fully independent.
Capability-wise: current model is a weak English LM — **not yet conversationally useful**.

## Path forward (evidence-based)
1. Bengali corpus cleaning (148M tokens ready) → continued pretraining
2. English corpus expansion (alpaca EXCLUDED — GPT-generated; use own/license-clean data)
3. More epochs on larger data; then re-eval
4. Instruction/reasoning stages only after language foundation improves
