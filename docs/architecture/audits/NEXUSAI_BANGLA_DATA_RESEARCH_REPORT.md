# NEXUSAI BANGLA DATA RESEARCH REPORT

**Phase:** Bengali training data research & collection planning
**Status:** RESEARCH ONLY — no downloads, no training, no dataset modification
**Date:** 2026-11-09
**Rule:** NexusAI remains independent — no external AI models, APIs, or pretrained weights used for data generation or judging.

---

## 1. VERIFIED SOURCE INVENTORY

| # | Source | URL | Size | License | Commercial? | Verdict |
|---|--------|-----|------|---------|-------------|---------|
| 1 | Bangla Wikipedia (sagorsarker/bangla-wikipedia) | huggingface.co/datasets/sagorsarker/bangla-wikipedia | ~995MB, 171,674 articles | **MIT** (per dataset card) | ✅ | **APPROVED — primary corpus** |
| 2 | Bengali Wikipedia (rejauldu/bengali-wikipedia) | huggingface.co/datasets/rejauldu/bengali-wikipedia | ~1.5GB, 178K articles | **CC BY-SA 3.0** | ⚠️ share-alike | APPROVED w/ attribution + SA compliance |
| 3 | Sangraha Bengali (ai4bharat/sangraha) | huggingface.co/datasets/ai4bharat/sangraha | multi-domain verified corpus | **CC BY 4.0** | ✅ | **APPROVED** |
| 4 | TituLM Bangla Corpus (hishab/titulm-bangla-corpus) | HF | web-crawl corpus | **CC BY 4.0** | ✅ | APPROVED |
| 5 | BanglaRQA | huggingface.co/datasets/sartajekram/BanglaRQA | 14,889 QA pairs (3K contexts) | **CC BY-NC-SA 4.0** | ❌ NON-COMMERCIAL | ⚠️ CONDITIONAL — usable only if NexusAI stays non-commercial |
| 6 | PROSHNO BINNASH | PMC12720108 / doi:10.1016/j.dib.2025.112261 | 4,069 QA entries, 10 categories | **CC BY-NC 4.0** | ❌ NON-COMMERCIAL | ⚠️ CONDITIONAL (same) |
| 7 | BanglaCoRe-5000 | huggingface.co/datasets/Maruf204949/BanglaCoRe-5000 | 5,000 MCQ reasoning items, 16 categories | **CC BY 4.0** | ✅ | **APPROVED — reasoning** |
| 8 | Bengali Chat / bengalichat | huggingface.co/datasets/rishiraj/bengalichat | 9.5K instruction pairs | **CC BY-NC 4.0** | ❌ NON-COMMERCIAL | ⚠️ CONDITIONAL |
| 9 | BongChat-v1-253k | huggingface.co/datasets/lumatic-ai/BongChat-v1-253k | 253K instructions | **MIT** | ✅ | **APPROVED — instruction/SFT** |
| 10 | bangla-instruction-dataset | huggingface.co/datasets/kamruzzaman-asif/bangla-instruction-dataset | multi-source aggregate | **MIXED — per-source check required** | varies | INVESTIGATE per subset |
| 11 | REVEAL-Bangla | huggingface.co/datasets/khondoker/reveal-bangla | multi-step reasoning eval | **CC BY-ND 4.0** | ❌ NO DERIVATIVES | ❌ **REJECTED for training** (eval-only possible) |
| 12 | X-CLAIM (Bengali split) | github.com/mbzuai-nlp/x-claim | ~102 test + small train/dev | research dataset, license unstated on card | unclear | INVESTIGATE — claim-span task only, low value for LM |
| 13 | BanglaBERT corpus (csebuetnlp) | github.com/csebuetnlp/BanglaBERT | large pretraining corpus | check repo license | — | INVESTIGATE |
| 14 | Tanzil Quran text (Uthmani) | tanzil.net | full Quran, verified text | free w/ attribution (verify current terms) | likely ✅ | APPROVED candidate for islamic_knowledge w/ references |
| 15 | Hadith collections (Sunnah.com / Dorar) | — | — | site terms apply | — | ⚠️ needs permission review; prefer structured HF mirrors if license-clear |

**Key license risk:** Several high-value QA/reasoning sets are **CC BY-NC** (non-commercial). Decision needed: is NexusAI permanently non-commercial? If yes → usable. If commercial future → exclude or replace.

---

## 2. DATA CATEGORY DESIGN (proposed)

| Category | Sources | Est. initial size |
|---|---|---|
| `bangla_general` | Bangla Wikipedia (MIT dump), Sangraha BN, TituLM | ~1–2 GB text |
| `bangla_love_emotion` | existing love_emotion_* (local), BongChat emotional subset, filtered wiki | small, curated |
| `bangla_islamic_knowledge` | Tanzil Quran + verified hadith extracts w/ references | curated only |
| `bangla_reasoning` | BanglaCoRe-5000 (CC BY), PROSHNO BINNASH (NC), BanglaRQA (NC) | ~10–20K items |
| `bangla_decision_making` | **self-authored schema** (Situation→Info→Constraints→Alternatives→Reasoning→Decision→Explanation) | needs creation (~2–5K) |
| `bangla_daily_life` | wiki how-to subset, BongChat daily-life, curated | medium |

**Decision-making format:** structured JSONL — no external AI generation allowed; items authored/derived from licensed sources only.

---

## 3. JSONL SCHEMA (proposed)

```json
{
  "record_id": "bn_gen_000001",
  "text": "...",
  "answer": "... or null",
  "category": "bangla_general",
  "source_name": "bangla-wikipedia",
  "source_url": "https://...",
  "license": "MIT",
  "attribution": "...",
  "verification_status": "unverified|verified|disputed",
  "quality_status": "raw|cleaned|approved",
  "split": "train|validation|test"
}
```

Raw sources immutable in `data/raw_bangla/`; cleaned output in `data/bangla_cleaned/`.

---

## 4. QUALITY CONTROLS

- SHA-256 dedup (proven method from english_first)
- Bengali Unicode range validation (U+0980–U+09FF) + Banglish (Latin+BN mix) tagging
- Language classifier per record (langdetect or script-ratio heuristic)
- Encoding repair (utf-8 strict), spam/boilerplate filters
- License field mandatory per record; NC sources quarantined in separate split if commercial ambiguity
- Deterministic seed-42 train/val/test split, zero-overlap verified

---

## 5. RECOMMENDED FIRST BATCH (pending approval)

1. Bangla Wikipedia MIT dump (~995MB) — biggest single quality source
2. Sangraha Bengali subset (CC BY 4.0)
3. BanglaCoRe-5000 (CC BY 4.0) — reasoning
4. BongChat MIT subset — instruction tuning
5. Existing local: phase9_1 Bengali cleaned + love_emotion_bn* — incorporate w/ provenance

**Defer:** NC-licensed sets until commercial-use decision; Islamic content until source terms verified.

## 6. ESTIMATED STORAGE

First batch ≈ **2–3 GB raw** → ~1.5 GB cleaned JSONL. Fits Drive + local.

## 7. UNRESOLVED RISKS

- NC-license commercial ambiguity (needs product decision)
- Wikipedia SA share-alike obligations on redistribution
- Islamic content: scholarly accuracy + attribution requirements unresolved
- Banglish: **no known quality public dataset** — likely must be self-created or mined from existing local staging

---

**NEXT:** Await approval for Batch 1 collection plan, and decision on non-commercial license acceptance.
