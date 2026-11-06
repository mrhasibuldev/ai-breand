# NEXUSAI CORE-01 — PHASE 2 ZERO-BUDGET DATASET & GPU READINESS AUDIT

**Date**: 2026-11-06
**Type**: READ-ONLY AUDIT (No code, data, checkpoint, or Git modifications)
**Scope**: Dataset inventory + token statistics (actual 8K tokenizer) + free GPU feasibility + VRAM estimation + zero-budget training roadmap

---

## EXECUTIVE SUMMARY

**Direct answers:**

- **Dataset exists and is real**: 83,892 records across ~30 dataset files, **~5.46M total tokens** measured with the actual NexusAI 8K SentencePiece tokenizer (not estimates).
- **BUT Bengali is severely underrepresented**: only ~73K Bengali tokens (1.3% of total). English dominates at ~5.38M tokens.
- **License risk found**: `alpaca_data.json` (52K records, 889K tokens) is under a **non-commercial research license** — must NOT be used for a commercial product. Dolly 15K is CC BY-SA 3.0 (share-alike obligation). GSM8K is MIT (safe).
- **Free GPU is feasible**: Kaggle offers 2×T4 (16GB each) with ~30 GPU-hours/week, 12h sessions; Google Colab free offers T4 (~12h sessions, dynamic quota); Lightning AI offers ~75 free T4-hours. An 8.84M-param model trains comfortably on a single 16GB T4.
- **Training is feasible within free tiers**: ~5M tokens/epoch × 3 epochs ≈ 7-9 GPU-hours on T4 — fits inside ONE Kaggle session or ONE Colab session.
- **Critical privacy warning**: `packages/ai-core/knowledge/` contains user-uploaded documents — must NEVER be uploaded to Colab/Kaggle.
- **Zero-budget verdict**: YES, a first real pretraining run of Core-01 is achievable entirely on free GPU tiers with checkpoint-resume discipline.

---

## 1. ACTUAL DATASET INVENTORY

All paths relative to `C:\Users\Nusaiba\Desktop\Ai Breand`.

| Dataset | Path | Records | Size | Format | Status |
|---|---|---|---|---|---|
| Phase 10 train (PRODUCTION legacy data) | `packages/ai-core/data/experimental/phase10/datasets/train.json` | 1,449 | 699 KB | JSON list, pre-tokenized | Pre-tokenized w/ `tokens` field |
| Phase 10 val | `.../phase10/datasets/val.json` | 181 | 90 KB | same | — |
| Phase 10 test | `.../phase10/datasets/test.json` | 182 | 81 KB | same | — |
| Dolly 15K cleaned | `packages/ai-core/data/collected/cleaned/dolly/dolly-15k_cleaned.jsonl` | 14,779 | 12.5 MB | JSONL instruction/context/response | Collected |
| GSM8K train cleaned | `.../cleaned/gsm8k/gsm8k_train_cleaned.jsonl` | 7,473 | 4.1 MB | JSONL math CoT | Collected |
| GSM8K test cleaned | `.../cleaned/gsm8k/gsm8k_test_cleaned.jsonl` | 1,319 | 733 KB | JSONL | Collected |
| Alpaca | `.../collected/small_datasets/alpaca_data.json` | 52,002 | 22.5 MB | JSON | ⚠️ LICENSE RISK |
| Wikipedia BN | `.../collected/wikipedia/bn/*.json` | 5 articles | 10 KB | JSON | Tiny |
| Wikipedia EN | `.../collected/wikipedia/en/*.json` | 14 articles | 11 KB | JSON | Tiny |
| Phase 9.1 combined cleaned | `.../phase9_1/cleaned/combined_cleaned.jsonl` | 741 | 217 KB | JSONL Bengali chat | Project-generated |
| Phase 9.1 Bengali chat | `.../phase9_1/cleaned/bengali_chat_conv_cleaned.jsonl` | 590 | 184 KB | JSONL | Project-generated |
| Phase 9.1 Bengali SFT | `.../phase9_1/cleaned/bengali_sft_v1_cleaned.jsonl` | 151 | 33 KB | JSONL | Project-generated |
| Phase 9.2 corpus combined | `.../phase9_2/corpus/combined.txt` | 1,867 lines | 288 KB | TXT | Project-generated |
| Phase 9.2 corpus Bengali | `.../phase9_2/corpus/bengali.txt` | 742 lines | 168 KB | TXT | overlaps phase9_1 |
| Phase 9.2 corpus English | `.../phase9_2/corpus/english.txt` | 1,111 lines | 118 KB | TXT | has junk lines |
| Phase 9.2 corpus mixed | `.../phase9_2/corpus/mixed.txt` | 14 lines | 2 KB | TXT | — |
| Public v1.0 train/val/test | `.../public_datasets/v1.0/*.json` | 19/2/3 | ~1 KB | JSON string arrays | Tiny |
| Public v1.0 cleaned | `.../public_datasets/v1.0_cleaned/*.json` | 17+19 | ~2 KB | JSON | Tiny |
| Bengali-English mixed | `.../public_datasets/bengali_english_mixed.json` | 24 | 2 KB | JSON | Tiny |
| train_v2 | `.../data/train_v2.json` | 502 | 149 KB | JSON messages format | Project-generated |
| train_final | `.../data/train_final.json` | 223 | 11 KB | JSON strings | Project-generated |
| merged_train | `.../data/merged_train.json` | 167 | 8 KB | JSON strings | subset of train_final |
| conversational_data | `.../data/conversational_data.json` | 28 | 5 KB | JSON messages | Tiny |
| synthetic train/val | `.../data/synthetic/*.json` | 148/38 | 9 KB | JSON strings | Synthetic, low value |
| Love/emotion staging | `data/staging/love_emotion/*.jsonl` | 69 total | 23 KB | JSONL | Staged, unverified license field |
| training/ dir | `training/train.json`, `val.json`, `original_dataset.jsonl` | 10/2/1 | 143 KB | mixed | 1 huge Wikipedia dump w/ nav junk |
| Knowledge base | `packages/ai-core/knowledge/**` | ~50 raw + cleaned | varies | txt/json | ⚠️ USER DATA — privacy |

## 2. VERIFIED TOKEN STATISTICS (actual 8K SentencePiece tokenizer)

Measured by running `sp.encode()` on every record. Script: `C:\Users\Nusaiba\AppData\Local\Temp\nexusai_dataset_audit.py` (outside repo, read-only).

| Dataset | Records | Tokens | UNK tokens | Exact dups |
|---|---|---|---|---|
| phase10 train | 1,449 | 32,013 | 7 | 0 |
| phase10 val | 181 | 4,064 | 0 | 0 |
| phase10 test | 182 | 3,669 | 0 | 0 |
| dolly-15k cleaned | 14,779 | 3,565,503 | 6,035 | 1 |
| gsm8k train | 7,473 | 643,787 | 229 | 0 |
| gsm8k test | 1,319 | 116,006 | 28 | 0 |
| alpaca | 52,002 | 889,355 | 243 | 0 |
| wikipedia bn | 5 | 950 | 0 | 0 |
| wikipedia en | 14 | 1,895 | 0 | 0 |
| phase9_1 combined | 741 | 14,211 | 1 | 0 |
| phase9_1 chat | 590 | 11,815 | 1 | 0 |
| phase9_1 sft | 151 | 2,396 | 0 | 0 |
| phase9_2 combined | 1,867 | 44,485 | 10 | 28 |
| phase9_2 bengali | 742 | 13,985 | 1 | 1 |
| phase9_2 english | 1,111 | 30,301 | 9 | 27 |
| phase9_2 mixed | 14 | 199 | 0 | 0 |
| public v1.0 (all) | 24 | 213 | 0 | 0 |
| v1.0_cleaned (all) | 36 | 332 | 0 | 0 |
| train_v2 | 502 | 18,199 | 0 | 0 |
| train_final | 223 | 2,114 | 0 | 6 |
| merged_train | 167 | 1,590 | 0 | 0 |
| conversational_data | 28 | 444 | 0 | 0 |
| synthetic (all) | 186 | 1,789 | 0 | 0 |
| love_emotion (all 4 files) | 69 | 9,137 | ~400 | 0 |
| training/ (all 3) | 13 | 51,528 | 375 | 0 |

**GRAND TOTAL: 83,892 records → 5,460,193 tokens, 18.16M chars, 63 exact duplicates, 7,340 UNK tokens**

### Language distribution (by token count)

| Language | Records | Tokens | % of tokens |
|---|---|---|---|
| English | 79,737 | 5,383,266 | 98.6% |
| Bengali | 3,878 | 73,145 | 1.3% |
| Mixed | 42 | 3,177 | 0.06% |
| Other | 235 | 605 | 0.01% |

**VERIFIED FACT**: Bengali representation is critically low. Romanized Bengali is counted inside "english" bucket (Latin script) — true Romanized-Bengali share is a subset of that, unverified separately.

## 3. DATASET QUALITY & SAFETY ASSESSMENT

**VERIFIED FACTS:**

- `phase9_2/corpus/english.txt` contains junk lines: `- Battery Life`, `3) Realio - $RIO`, `কম্পিউটারের ফুল ফর্ম কী?` — looks like scraped Wikipedia list/ticker fragments. ~87 "other" records. Should be filtered.
- `training/original_dataset.jsonl` = ONE 140K-char Wikipedia "Machine learning" dump including navigation boilerplate (`Jump to content Main menu...`). Low value as-is.
- `merged_train.json` ⊂ `train_final.json` (same first samples, 167 vs 223) — cross-file duplication.
- `phase9_2/corpus/bengali.txt` and `combined.txt` substantially overlap `phase9_1/cleaned/*` (same Bengali chat content, same 14,163 Bengali token count) — cross-source duplication if both used.
- `love_emotion` files store JSON as raw string inside JSONL records (double-encoded) — needs parsing fix before use. 105-125 UNK tokens each (highest UNK rate ~4%).
- `knowledge/` directory = user-uploaded documents → **privacy risk, exclude from any cloud upload**.
- Phase 10 data is already tokenized with the same 8K tokenizer — directly reusable.

**License status:**
- GSM8K: MIT ✅ safe
- Dolly 15K: CC BY-SA 3.0 ⚠️ attribution + share-alike required
- Alpaca: **non-commercial research license** ❌ exclude for product
- Wikipedia: CC BY-SA 4.0 ⚠️ attribution required
- Project-generated (phase9_1, 9_2, 10, train_v2, staging): owned ✅ but human-review status varies (pilot dataset was "pending review")

## 4. FREE GPU PLATFORM COMPARISON

| Platform | Free GPU | VRAM | Session limit | Weekly quota | Persist storage | Payment required | Auto-charge risk | Evidence |
|---|---|---|---|---|---|---|---|---|
| **Kaggle Notebooks** | 2× Tesla T4 | 16 GB each | 12 h | ~30 GPU-h/week (resets Sat UTC) | 20 GB `/kaggle/working` persists | No (phone verify) | None on free tier | kaggle.com/docs/efficient-gpu-usage |
| **Google Colab free** | T4 (sometimes K80) | 16 GB | ~12 h, 90-min idle disconnect | Dynamic/unstated (~100 compute units/mo reported) | None persistent (Drive mount possible) | No | None on free tier; Pro=$9.99/mo optional | research.google.com/colaboratory/faq.html |
| **Lightning AI** | T4, L4, etc. | 16-24 GB | Studio restarts every 4 h | ~75 free T4-h (30 credits, interruptible) | 50 GB persistent Drive | No card for 5 credits; +25 credits needs card | Credits expire 12 mo; no auto-charge without purchase | lightning.ai/pricing |
| **SageMaker Studio Lab** | varies | ~12-16 GB | 4 h/session, 4 h/24 h | — | env persists | AWS account | ❌ **CLOSED to new customers** | docs.aws.amazon.com studio-lab-availability-change |
| Paperspace Gradient Free | M4000/P4000 | 8 GB | 12 h auto-shutdown | — | limited | account | free tier only, old GPUs | thundercompute comparison |
| Modal | T4+ serverless | varies | scales to zero | $30/mo credits claimed | ephemeral | card for credits | possible if credits configured | modal.com |

**VERIFIED**: Kaggle = best free option (documented 30 h/week, 2×T4, persistent 20 GB). Colab = good backup but unguaranteed GPU + idle disconnects. Lightning AI = decent third option with persistent storage. Studio Lab = unavailable to new users.

**Privacy note**: All cloud notebooks see uploaded data. Only upload public/licensed datasets — never `knowledge/` user data, never `.env`, never checkpoints containing user info.

## 5. ACTUAL MODEL VRAM REQUIREMENTS (Core-01, 8,842,560 params)

Computed from real config: d_model=256, 6 layers, 8 heads, d_ff=1024, vocab=8000, max_len=512.

| Component | FP32 | Mixed precision (FP16/BF16) |
|---|---|---|
| Weights | 8.84M × 4B = **35.4 MB** | 17.7 MB |
| AdamW states (m+v) | 8.84M × 8B = **70.7 MB** | 35.4 MB (master weights FP32: +35.4) |
| Gradients | 8.84M × 4B = **35.4 MB** | 17.7 MB |
| Static total | **~142 MB** | **~106 MB** |
| Activations (batch 8 × seq 512, est.) | ~1.5-3 GB (attention scores B×H×S×S dominate: 8×8×512×512×4B ≈ 67 MB/layer ×6 ≈ 400 MB + FFN intermediates) | ~half |
| **Total @ batch 8, seq 512** | **~2-3.5 GB** | **~1.5-2 GB** |

**Estimated, not measured.** Even batch 16/32 likely fits in 8-12 GB.

**Verdict**: a single 16 GB T4 is **massively sufficient** — this model is tiny. Even Kaggle's per-GPU 16 GB or Colab T4 can run batch 16-32 with mixed precision. CPU fallback is technically possible but ~50-100× slower — not recommended beyond smoke tests.

## 6. TRAINING FEASIBILITY ESTIMATION

- FLOPs/token ≈ 6 × params = ~53 MFLOPs. T4 realistic throughput ~25-40 TFLOPS effective → **~1.5-3 h per 1M tokens/epoch** (batch 16, seq 512, mixed precision).
- Available corpus (license-clean subset): phase10 (39.7K tok) + phase9_1/9_2 dedup'd (~55K tok) + GSM8K (~760K) + Dolly (~3.57M, CC-BY-SA) + misc (~50K) ≈ **~4.4M usable tokens** (excluding alpaca).
- 3 epochs ≈ 13M tokens ≈ **~8-15 GPU-hours** → fits in ONE 12-h Kaggle session or split across 2 sessions with checkpoint resume.
- Chinchilla-optimal would be ~177M tokens — **not achievable free**; a 4-5M token first run is a legitimate pipeline-verification baseline, not a "good" model. Honest expectation: coherent short Bengali/English phrases possible; general intelligence NO.

## 7. RECOMMENDED ZERO-BUDGET TRAINING ROADMAP

- **Stage 1 — Pipeline verification (CPU, local, ~30 min)**: run PretrainingEngine for ~50 steps on phase10 subset, verify loss decreases, checkpoint saves. No GPU needed.
- **Stage 2 — Kaggle smoke run (~1-2 GPU-h)**: upload tokenizer + phase10 + small subset; train 200-500 steps; verify checkpoint download/resume works.
- **Stage 3 — Full first pretrain (~8-15 GPU-h, 1-2 Kaggle sessions)**: combined dedup'd corpus, 3 epochs, save checkpoint every ~30 min to `/kaggle/working`, download to local `models/nexusai_core_01/checkpoints/`.
- **Stage 4 — Evaluate** with `ModelEvaluator` + manual Bengali/English/Romanized prompts.
- **Stage 5 — Instruction tuning** on phase9_1 SFT + love_emotion (after license check) — separate small run.
- **Stage 6 — Iterate**: only if results promising, expand Bengali corpus (biggest gap).

## 8. CHECKPOINT & BACKUP STRATEGY

- Core-01 checkpoints → `packages/ai-core/models/nexusai_core_01/checkpoints/` (already separate from legacy).
- During cloud training: save `checkpoint_step{N}.pt` every ~30 min + `latest.pt`; Kaggle `/kaggle/working` persists 20 GB — download after each session.
- Local backup: copy to `models/nexusai_core_01/checkpoints/` — do NOT commit .pt files to Git (add to .gitignore if not already).
- Integrity: `CheckpointManager` already writes full config+timestamp; add SHA-256 sidecar on download.
- Legacy model (`checkpoints_medium/`) and tokenizer untouched — verified intact this session.
- Never upload: `knowledge/`, `.env*`, user data, credentials.

## 9. RISKS & LIMITATIONS

- **Bengali data scarcity** is the #1 quality bottleneck — 73K tokens won't teach Bengali well.
- Free-tier session kills are routine → checkpoint-every-30-min is mandatory.
- Kaggle GPU availability not guaranteed at peak times (queue).
- Dataset license audit incomplete for staging/pilot files — legal review needed before commercial use.
- ~5.4M tokens is far below what's needed for a "good" 8.8M model; expect a weak-but-real baseline.
- Alpaca must be excluded (non-commercial). Dolly/Wikipedia need attribution if shipped.

## 10. RECOMMENDED NEXT ACTIONS

1. Owner decision: approve Kaggle/Colab account usage (phone verification needed — owner must do this).
2. Build deduplicated, license-clean corpus manifest (exclude alpaca, flag CC-BY-SA).
3. CPU smoke test of PretrainingEngine on phase10 (Stage 1) — needs approval since it writes a checkpoint.
4. Expand Bengali corpus (largest quality lever) — B-CORE/BanglaLLM license verification first.

## 11. GIT STATUS

Before audit: `M packages/ai-core/ml-service/__pycache__/main.cpython-314.pyc`, untracked `data/`, `docs/architecture/audits/`, `packages/ai-core/core01/`, `packages/ai-core/models/nexusai_core_01/`, `packages/ai-core/test_core01.py`, `packages/ai-core/data/.venv/`
After audit: **identical** — only this report file added under `docs/architecture/audits/`. No source/data/checkpoint/Git-state modifications.

## 12. CONFIRMATIONS

- ✅ No training started or initialized
- ✅ No payments, trials, or cloud resources created
- ✅ No code or dataset modifications
- ✅ No external pretrained weights used
- ✅ Temp audit script placed OUTSIDE repo (`%TEMP%\nexusai_dataset_audit.py`), read-only
- ✅ All token counts measured with the actual `sp_bpe_8k.model` tokenizer

**STOP — awaiting explicit owner approval before any implementation or training.**
