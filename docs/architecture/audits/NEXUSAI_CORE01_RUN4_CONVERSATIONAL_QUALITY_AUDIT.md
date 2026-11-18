# NexusAI Core-01 — Run4 Conversational Quality & SFT Readiness Forensic Audit

**Date:** 2026-11-17 · PHASE A+B · READ-ONLY · no files modified

## Executive summary
Run4 CPU inference is **fully verified** (hash/strict-load/generation PASS).
Conversational quality is poor for identifiable reasons: (1) model is
pretrained-only — never saw chat format; (2) immediate-EOS on OOD prompts;
(3) sft_v1 exists but is **90% arithmetic templates**, 16 Bengali, no splits,
no response-only loss masking in pipeline. SFT is feasible on free Colab GPU
(model is tiny). 3 real gaps found: prompt-masking, dataset balance/splits,
chat-format encoding.

## A. Generation root-cause findings (evidence-backed)

| symptom | root cause | type |
|---|---|---|
| 5/11 EMPTY (immediate EOS) | After BOS, model assigns high P(EOS) — pretraining doc-boundary prior; prompts are OOD vs training docs | MODEL+FORMAT, not bug |
| Story/lyrics outputs | Pretraining continuation — model continues "text" not "answers" | MODEL (needs SFT) |
| Bengali template noise | bn_mixed corpus gave script exposure but no QA structure | DATA |
| Repetition loop (en_ai) | greedy + small model + no rep-penalty in eval path (engine default do_sample=True→we used False; rep_penalty default 1.2 exists but unused at 1.0?) | CONFIG minor |
| Banglish EMPTY ×2 | Romanized bn underrepresented (459 records) | DATA |

**No inference code defect found** — fixed generate() is correct; EOS-stop
verified via generated_ids (fwd_calls match token counts).

## B. SFT dataset audit — `data/phase3/sft_v1/sft_train.jsonl`
- 536 pairs · 0 empty · 0 dup questions · format `{lang,category,messages}`
- **CRITICAL imbalance:** math templates = 484/536 (90%); facts 25;
  identity 12; greeting 7; thanks 4; safety 4
- lang: en 345 / banglish 175 / **bn only 16**
- avg response 17 chars (very short); max q 54 chars
- **NO train/val/test split** — single file
- No multi-turn; template-heavy → overfitting risk
- Verdict: **seed dataset — smoke-test only, NOT production SFT**

## C. Training pipeline compatibility
- `PackedTextDataset` packs token stream, `input_ids=block[:-1]`,
  `targets=block[1:]` — standard CLM shift ✓
- Loss: `F.cross_entropy(..., ignore_index=pad_id)` — **prompt tokens DO
  contribute to loss** (no response-only masking) — acceptable for smoke
  SFT, suboptimal; proper SFT masks user turn
- AdamW+LambdaLR+grad-accum+AMP all present; resume loads full state ✓
- **Gap:** no chat-format dataset class; sft JSONL `{messages}` needs
  conversion to token stream `[BOS] user:..[EOS] assistant:..[EOS]`

## D. GPU/compute estimate (evidence-based)
- model 35MB fp32 + AdamW states ~70MB + grads 35MB ≈ **150MB weights**
- activations: batch 8-16 × seq 256-512 → few hundred MB
- **T4 16GB: trivially fits**; 536 pairs × ~3 epochs = minutes
- Even Kaggle P100 fine. No blocker.

## Issues register
| ID | sev | area | issue |
|---|---|---|---|
| I1 | HIGH | pipeline | no response-only loss masking for SFT |
| I2 | HIGH | dataset | 90% math skew, bn=16, no splits |
| I3 | MED | dataset | no chat-template tokenization path |
| I4 | MED | eval | heuristic-only quality; need fixed versioned suite |
| I5 | LOW | inference | repetition_penalty not exercised in eval |
| I6 | INFO | model | pretraining-only — expected, SFT is the fix |

## Prioritized roadmap
1. **P1:** chat-format SFT dataset builder v2 (balanced langs, splits, response masking spec)
2. **P2:** SFT training cell (resume Run4, low LR ~1e-5-5e-5, 2-3 epochs, new ckpt `run5_sft.pt`)
3. **P3:** versioned eval suite + before/after `/eval/run` comparison
4. **P4:** acceptance gates (empty-rate↓, bn-script↑, relevance manual)

## Files that WOULD change (pending approval)
- NEW `data/build_sft_v2.py` + `sft_v2/` dataset (original sft_v1 immutable)
- NEW Colab SFT training cell (no repo source changes needed if driver supports custom dataset — VERIFY: driver takes --train-file JSONL of {text}; chat pairs need flattening to text OR new dataset class → likely small `sft_dataset.py` addition)
- NEW eval suite file
- NO changes: transformer, tokenizer, Run4 ckpt, inference engine

## Estimated GPU need
T4/Kaggle GPU, ~10-30 min for 536-pair smoke SFT. Free Colab sufficient.

## Decision gates status
Dataset discovered+checksummed: PASS · parsing: PASS · splits: **FAIL** ·
lang dist: PASS(measured) · loss masking: **FAIL(needs impl)** ·
resume compat: PASS(code-verified) · GPU config: PASS(estimated).

## STOP — awaiting explicit approval
Phase C: approve dataset v2 builder + SFT cell design? Phase F (training)
requires separate approval after prep verification.
