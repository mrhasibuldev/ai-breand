# RUN4 Recovery — Phase A Read-Only Forensic Audit

**Date:** 2026-11-13 · READ-ONLY · No files modified · No training.

## A1. Repository
- Remote: `github.com/mrhasibuldev/ai-breand.git` · branch `main` · HEAD `64d05e9` (docs commit, 2026-11-10)
- 61 uncommitted/untracked paths (prior work) — untouched
- Relevant tree verified locally: `packages/ai-core/core01/{transformer,training,dataset,tokenizer_interface,pretraining_driver,inference,evaluation}.py`, `models/nexusai_core_01/config/model_config.py`, tokenizer `sp_bpe_8k.model/.vocab`, `exports/` ZIPs, `docs/notebooks/*`, `eval_reports/*`

## A2. Architecture (verified from source + live instantiation)
- `NexusAICore01`: 6 layers, d_model 256, 8 heads, d_ff 1024, vocab 8000, max_len 512, sinusoidal PE, pre-norm style blocks, output Linear(256→8000)
- **Param count: 8,842,560** (counted locally — matches ckpt `estimated_parameters`)
- State-dict strict load vs Run3 ckpt: **PASS** (verified in prior bounded smoke + strict=True loads)

## A3. Run3 checkpoint (repo copy; Drive copy verified by hash in preflight)
- `checkpoint_final.pt`: 106,777,501 B · `ad515cade…7830` · epoch=3, step=1341, train_loss 4.426, val_loss 4.217, PRETRAINING_COMPLETED
- Contains: model/optimizer/scheduler/GradScaler/RNG(python,numpy,torch_cpu,torch_cuda)/tokenizer_path
- Other Drive ckpts (last/step900-1300) exist per user report — **not independently re-hashed this session** (Drive-only, NOT_TESTED here)

## A4. Strict compatibility — PASS (strict=True, no missing/unexpected keys)

## A5. Tokenizer — PASS (prior session: sp_bpe_8k.model 387,195 B; en+bn encode verified; vocab 8000 == config; pad0/unk1/bos2/eos3)

## A6. Dataset — PASS integrity
- `corpus_train.jsonl` 385,217,021 B · `5f8572ed…8376` · 216,193 records · 0 malformed · schema {text,category,lang,source}
- Distribution (actual scan): en 130,753 / bn_mixed 84,000 / bn 819 / banglish 459 / mixed 162
- Quality caveat: encyclopedic-heavy; reasoning_v1 10,233 QA math; creator/love/Banglish thin → SFT needed later for those behaviors

## A7. Driver audit — scheduler order CORRECT
- `setup_scheduler(est_steps)` (line 276) runs BEFORE `load_checkpoint` (line 316) → scheduler state restores properly ✅
- `load_checkpoint` restores model+opt+sched+scaler+RNG, sets `current_epoch`/`current_step` ✅
- Atomic save: tmp + `os.replace` ✅; epoch ckpt `checkpoint_last.pt`, step ckpts `checkpoint_step{N}.pt` every 100, eval every 250
- **No checkpoint rotation** → ~7-8.5GB Drive usage projected

## PHASE B — BUG INVESTIGATION RESULTS

### BUG 1 — EPOCH RESUME: **CONFIRMED CRITICAL**
- Driver: `for epoch in range(engine.current_epoch, args.epochs)` (driver ~line 324)
- Run3 ckpt: `epoch=3` → `engine.current_epoch=3`
- Train cell: `EPOCHS = 2` → `range(3, 2)` = **EMPTY → ZERO training steps**
- Then unconditional `save_checkpoint("checkpoint_final.pt", finalize=True)` → **FALSE `PRETRAINING_COMPLETED`** with 0 steps
- Epoch semantics verified: per-epoch save uses `epoch=epoch+1` (1-based completed count); `range(current_epoch, epochs)` treats `epochs` as **total target epoch count**
- **Correct fix: `EPOCHS = 5`** (3 completed + 2 new). `MAX_STEPS=8000` remains the global cap (resumes at step 1341 → ~6,659 optimizer steps ≈ 2 epochs). est_steps scheduler horizon uses args.epochs — with 5 it approximates correctly.

### BUG 2 — START_EPOCH: **NOT A BUG in current file**
- `START_STEP = ck["step"]; START_EPOCH = ck.get("epoch", 0)` — both defined; report uses real values ✅

### BUG 3 — FALSE COMPLETION: **CONFIRMED (same root as BUG 1)**
- Driver has no guard against empty epoch loop → marks completed. Fix must add executed-step accounting: report `steps_executed = final_step - start_step`; refuse `finalize=True` if 0 steps ran.

## Additional findings
- Train cell `VAL = TRAIN` unused var (driver splits internally — harmless)
- Train cell asserts `ck.step==1341` but does NOT re-hash SRC_CKPT — relies on preflight hash check; recommend adding sha verify (minor)
- `est_steps` scheduler horizon doesn't subtract completed steps — decay slope slightly long; cosmetic, document only

## Status
`AUDIT: COMPLETE` · `BUGS: 1 CRITICAL CONFIRMED + 1 FALSE-COMPLETION (same fix)` · `IMPLEMENTATION: AWAITING APPROVAL (Phase F)`
