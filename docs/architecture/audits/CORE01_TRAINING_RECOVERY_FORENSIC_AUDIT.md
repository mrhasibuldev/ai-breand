# CORE-01 Training Recovery — Consolidated Forensic Audit

**Date:** 2026-11-13 · Repo `main` @ `64d05e9` · READ-ONLY audit + prior approved fixes.
Labels: VERIFIED / PASS / FAIL / WARNING / NOT TESTED / UNKNOWN

## 1. Repository & release inventory
- Repo: `github.com/mrhasibuldev/ai-breand` main @ `64d05e9a65bd` — VERIFIED
- **ACTIVE release:** `exports/NEXUSAI_CORE01_RUN4_SINGLE_UPLOAD_BUNDLE.zip`
  173,913,188 B · SHA `959ac4f076cf939b2cda0321ec74b6dc9353e00b3d47728409b035ee36ccb456` · manifest v2.1.0 (7 entries, all hashes verified)
- Superseded (preserved): `..._v1_1_SUPERSEDED.zip` (`eb693237…`), inner `..._BUNDLE_v1_SUPERSEDED.zip` (`f91411e1…`)
- Inner train ZIP v2: 300,135 B · `e0f9f465f0c30b6bb79a6a14eeeb4b023bf27d50f77b8b06a17d09cd90597d3a`
- Older English-only bundle `NEXUSAI_CORE01_COLAB_TRAINING_BUNDLE.zip` exists (english_first 61,960/958/958) — **NOT the Run4 corpus**; prompt's dataset description refers to it. Run4 uses multilingual `corpus_train.jsonl`.

## 2. Model architecture — VERIFIED/PASS
- `NexusAICore01`: 6L, d_model 256, 8H, d_ff 1024, vocab 8000, max_len 512, sinusoidal PE
- **8,842,560 params** — counted by live instantiation
- Strict `load_state_dict` vs Run3 ckpt: PASS (100 tensors, 0 missing/unexpected — prior verified smoke)

## 3. Run3 checkpoint — VERIFIED/PASS
- `checkpoint_final.pt` 106,777,501 B · `ad515cade…7830` · epoch=3 step=1341 · train 4.426 val 4.217 · PRETRAINING_COMPLETED
- Full state: model/opt/sched/GradScaler/RNG(python,numpy,torch_cpu,torch_cuda)/tokenizer_path — VERIFIED
- Drive-side copies (last/step900–1300): NOT TESTED here (Drive-only)
- **Never modified** — all loads read-only ✅

## 4. Tokenizer — PASS
- `sp_bpe_8k.model` 387,195 B inside inner ZIP; vocab 8000 == config; pad0/unk1/bos2/eos3; en+bn encode verified live

## 5. Dataset (Run4 corpus) — VERIFIED integrity / WARNING quality
- `corpus_train.jsonl` 385,217,021 B · `5f8572ed…8376` · 216,193 records · 0 malformed
- Sources: english_first 61,960 · tinystories 60,000 · bn_wikipedia 45,000 · bongchat 30,000 · reasoning_v1 10,233 · sangraha 9,000
- Lang: en 130,753 / bn_mixed 84,000 / bn 819 / banglish 459 / mixed 162
- WARNING: encyclopedic-heavy; reasoning_v1 has real QA math (7,878 hits); creator=Hasibul ~absent; affection ~40; Banglish thin → conversational goals need later SFT phase
- english_first subset has its own manifest (train/val/test 61,960/958/958) but Run4 driver uses doc-level 2% split of the full corpus — no leakage by construction

## 6. Training pipeline audit — PASS w/ fixes applied
- `pretraining_driver.py` + `training.py`: resume restores model/opt/sched(scheduler init BEFORE load ✅)/scaler/RNG; atomic saves (tmp+os.replace); step ckpts /100, eval /250, epoch `checkpoint_last`, final/maxsteps/interrupted/error variants
- **BUG FOUND & FIXED (approved):** `range(current_epoch=3, epochs=2)` → empty loop → false `PRETRAINING_COMPLETED`. Fixed: train cell `EPOCHS=5` (3+2) + driver zero-step guard (`checkpoint_zero_steps.pt` + RuntimeError, exit 1)
- CPU-verified: bug scenario exits 1 with zero steps; positive run executed steps 1341→1343 correctly
- Train cell now verifies SRC_CKPT sha256 before training; report has steps_executed/epochs_executed

## 7. Bugs/root causes resolved
| Issue | Status |
|---|---|
| Epoch resume off-by-semantics (EPOCHS=2 vs epoch=3) | FIXED → 5 |
| False completion on zero steps | FIXED → guard |
| START_EPOCH undefined claim | NOT A BUG (was defined) |
| Missing ckpt hash re-verify in train cell | FIXED |
| No checkpoint rotation (~7-8.5GB Drive) | WARNING — manual cleanup may be needed |
| est_steps scheduler horizon ignores completed steps | WARNING — cosmetic decay slope |

## 8. Colab/Drive/GPU status — NOT TESTED
- Upload cell v3.1 + GPU smoke cell v1.0 embedded in notebook (20 cells, compile-verified)
- Awaiting user's Colab run: Cells 2→4→6→6b→8→10→12→14→16
- New ZIP `959ac4f0…` REQUIRED — old `eb693237…` superseded (contained epoch bug)

## 9. Proposed training config (pending Colab verification)
- `EPOCHS=5` total (2 new), `MAX_STEPS=8000` cap, bs=8, accum=4 (eff. 32), fp16, ckpt/100, eval/250, resume run3 → `checkpoints/core01_run4/`
- Est. ~6.6K optimizer steps ≈ 2 epochs over 216K docs; storage ~7-8.5GB

## 10. Scaling roadmap (planning targets, not commitments)
Existing doc `NEXUSAI_FUTURE_MODEL_SCALING_ROADMAP.md`; weight-transfer strategy required between stages — never shape-mismatch load. CPU inference feasible only through ~Stage 1-2 realistically.

## 11. Remaining blockers
1. User must run new ZIP through Colab cells (NOT_TESTED)
2. Drive ≥10GB free
3. FP16/GradScaler on real GPU — pending Cell 6b
4. Explicit `START NEXUSAI CORE-01 TRAINING` required

## Status: PARTIALLY READY → awaiting Colab preflight + authorization
