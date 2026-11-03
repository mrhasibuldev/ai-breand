# VERIFIED_DATASET_SOURCE_REGISTRY

**Date**: 2026-10-31  
**Task**: Verified Dataset Source Registry  
**Registry Type**: DATASET CATALOG  
**Status**: PARTIAL — LICENSE VERIFICATION PENDING

---

## Summary

This registry catalogs discovered dataset sources with their licensing, commercial use permissions, and NexusAI suitability assessment.

**Total Sources**: 58  
**Fully Verified**: 4  
**Partially Verified**: 3  
**Blocked by License**: 43  
**Blocked by Storage**: 8  
**Blocked by Format**: 1

---

## Registry Format

| Field | Description |
|-------|-------------|
| Dataset Name | Official name |
| Official URL | Verified source URL |
| Publisher | Owner or organization |
| Languages | Actual supported languages |
| Domain | Subject coverage |
| Data Format | JSON, JSONL, CSV, Parquet, etc. |
| Approximate Size | Verified size or UNKNOWN |
| Number of Records | Verified count or UNKNOWN |
| License | Exact license |
| Commercial Use | Allowed / Restricted / Unknown |
| Modification | Allowed / Restricted / Unknown |
| Redistribution | Allowed / Restricted / Unknown |
| Attribution | Requirements |
| Personal Data | Known privacy concerns |
| Download | Available / Restricted / Unknown |
| NexusAI Suitability | High / Medium / Low |
| Decision | APPROVED FOR FUTURE REVIEW / BLOCKED / NEEDS VERIFICATION |

---

## Verified Sources (Clear License + Feasible Size)

### 1. Gab100MFinetune

| Field | Value |
|-------|-------|
| Dataset Name | Gab100MFinetune |
| Official URL | https://huggingface.co/datasets/gszauer/Gab100MFinetune |
| Publisher | gszauer |
| Languages | English |
| Domain | General conversation, education, programming, life skills |
| Data Format | Plain text with chat markers |
| Approximate Size | 831 MB |
| Number of Records | 553,427 |
| License | MIT License |
| Commercial Use | Allowed |
| Modification | Allowed |
| Redistribution | Allowed |
| Attribution | MIT license requirements |
| Personal Data | None known |
| Download | Available |
| NexusAI Suitability | High |
| Decision | APPROVED FOR FUTURE REVIEW |

### 2. helpful_instructions

| Field | Value |
|-------|-------|
| Dataset Name | Helpful Instructions |
| Official URL | https://huggingface.co/datasets/HuggingFaceH4/helpful_instructions |
| Publisher | HuggingFace |
| Languages | English |
| Domain | Instruction following |
| Data Format | JSON |
| Approximate Size | 59 MB |
| Number of Records | 185,269 |
| License | Apache 2.0 |
| Commercial Use | Allowed |
| Modification | Allowed |
| Redistribution | Allowed |
| Attribution | Apache 2.0 requirements |
| Personal Data | None known |
| Download | Available |
| NexusAI Suitability | High |
| Decision | APPROVED FOR FUTURE REVIEW |

### 3. DialoguesEN-22k-Instructional

| Field | Value |
|-------|-------|
| Dataset Name | DialoguesEN-22k-Instructional |
| Official URL | https://huggingface.co/datasets/VDC-team/DialoguesEN-22k-Instructional |
| Publisher | VDC-team |
| Languages | English |
| Domain | Instructional dialogues |
| Data Format | JSONL |
| Approximate Size | UNKNOWN |
| Number of Records | 22,000 |
| License | MIT License |
| Commercial Use | Allowed |
| Modification | Allowed |
| Redistribution | Allowed |
| Attribution | MIT license requirements |
| Personal Data | None known |
| Download | Available |
| NexusAI Suitability | High |
| Decision | APPROVED FOR FUTURE REVIEW |

### 4. Universal-Chat-SFT-Dataset

| Field | Value |
|-------|-------|
| Dataset Name | Universal-Chat-SFT-Dataset |
| Official URL | https://huggingface.co/datasets/Srijan-Chakraborty/Universal-Chat-SFT-Dataset |
| Publisher | Srijan-Chakraborty |
| Languages | English |
| Domain | Multi-turn conversations |
| Data Format | JSON |
| Approximate Size | UNKNOWN |
| Number of Records | 4,000 |
| License | CC BY 4.0 |
| Commercial Use | Allowed |
| Modification | Allowed |
| Redistribution | Allowed |
| Attribution | Required (CC BY 4.0) |
| Personal Data | None known |
| Download | Available |
| NexusAI Suitability | Medium |
| Decision | APPROVED FOR FUTURE REVIEW |

---

## Partially Verified (Clear License, Size Unknown)

### 5. qulture-general-knowledge-dataset

| Field | Value |
|-------|-------|
| Dataset Name | Qulture Multilingual General Knowledge Question Dataset |
| Official URL | https://huggingface.co/datasets/Qulture/qulture-general-knowledge-dataset |
| Publisher | Qulture |
| Languages | French, English, German, Spanish |
| Domain | General knowledge |
| Data Format | CSV, JSON |
| Approximate Size | UNKNOWN |
| Number of Records | 64 |
| License | CC BY 4.0 |
| Commercial Use | Allowed |
| Modification | Allowed |
| Redistribution | Allowed |
| Attribution | Required (CC BY 4.0) |
| Personal Data | None known |
| Download | Available |
| NexusAI Suitability | Low (too small) |
| Decision | NEEDS VERIFICATION |

---

## Blocked by License (License Verification Required)

### Bengali Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| bangla-llm-data | UNKNOWN | License verification required |
| B-CORE-bengali-corpus | UNKNOWN | License verification required |
| bnnews | UNKNOWN | License verification required |
| xnli_bn | UNKNOWN | License verification required |
| BanglaNMT | UNKNOWN | License verification required |

### English Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| lmsys-chat-1m | UNKNOWN | License verification required + privacy concerns |
| dailyconversations | UNKNOWN | License verification required |
| instruct-v3 | UNKNOWN | License verification required |
| ultrachat | UNKNOWN | License verification required |
| multi-turn-conversation-50000x | UNKNOWN | License verification required |
| Multi-Turn-Conversational-SFT | UNKNOWN | License verification required |
| multiturn-chat | UNKNOWN | License verification required |

### Mathematics Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| math_dataset | UNKNOWN | License verification required |
| MATH-lighteval | UNKNOWN | License verification required |
| ODA-Math-460k | UNKNOWN | License verification required |
| gsm8k | UNKNOWN | License verification required |
| olympiad-math-stepwise-solutions | UNKNOWN | License verification required |

### Programming Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| starcoderdata | UNKNOWN | License verification required |
| python_code_instructions_18k_alpaca | UNKNOWN | License verification required |
| CodeFeedback-Filtered-Instruction | UNKNOWN | License verification required |

### Reasoning Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| reasoning-dataset-all-topic | UNKNOWN | License verification required |
| SFT-Collection-v2 | UNKNOWN | License verification required |
| reasoning-core datasets | UNKNOWN | License verification required |
| OpenMathReasoning | UNKNOWN | License verification required |

### Safety Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| PKU-SafeRLHF | UNKNOWN | License verification required |
| hh-rlhf | UNKNOWN | License verification required |
| PKU-SafeRLHF-10K | UNKNOWN | License verification required |
| hh-rlhf-safety-v3 | UNKNOWN | License verification required |

### Other Domains

| Dataset | License | Blocker |
|---------|---------|---------|
| InstructionFollowing | UNKNOWN | License verification required |
| instruction-dataset | UNKNOWN | License verification required |
| python_code_instructions_18k_alpaca | UNKNOWN | License verification required |
| PlanningBench | UNKNOWN | License verification required |
| planbench | UNKNOWN | License verification required |
| DeepPlanning | UNKNOWN | License verification required |
| natural-plan-benchmark | UNKNOWN | License verification required |
| TravelPlanner | UNKNOWN | License verification required |
| xlsum | UNKNOWN | License verification required |
| newsroom | UNKNOWN | License verification required |
| xsum | UNKNOWN | License verification required |
| cnn_dailymail | UNKNOWN | License verification required |
| multi_news | UNKNOWN | License verification required |
| General-Knowledge | UNKNOWN | License verification required |
| EU-MMLU | UNKNOWN | License verification required |
| mmmlu_lite | UNKNOWN | License verification required |
| qa-dataset-general-knowledge-60 | UNKNOWN | License verification required |
| Nemotron-SFT-Science-v2 | UNKNOWN | License verification required |
| SciPredict | UNKNOWN | License verification required |
| Sci-Base | UNKNOWN | License verification required |
| sciq | UNKNOWN | License verification required |

### Banglish Datasets

| Dataset | License | Blocker |
|---------|---------|---------|
| Banglish-English | UNKNOWN | License verification required |
| Banglish (CSVC-Net) | UNKNOWN | License verification required + audio format |
| Code-mixed Chaos | UNKNOWN | License verification required |
| BnSentMix | UNKNOWN | License verification required |

---

## Blocked by Storage (Size Exceeds Available Capacity)

| Dataset | Size | Available | Required | Blocker |
|---------|------|-----------|----------|---------|
| B-CORE-bengali-corpus | 52 GB | 2.9 GB | External storage | STORAGE |
| the-stack | 6 TB | 2.9 GB | External storage | STORAGE |
| starcoderdata | 783 GB | 2.9 GB | External storage | STORAGE |
| commitpack | 4 TB | 2.9 GB | External storage | STORAGE |
| newsroom | 5.30 GB | 2.9 GB | External storage | STORAGE |
| ultrachat | ~6 GB | 2.9 GB | External storage | STORAGE |
| Reasoning-Mix-100k | 2.31 GB | 2.9 GB | External storage | STORAGE |
| Sci-Base | VERY LARGE | 2.9 GB | External storage | STORAGE |

---

## Blocked by Format

| Dataset | Format | Blocker |
|---------|--------|---------|
| Banglish (CSVC-Net) | Audio files | Not suitable for LLM text training |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total Sources | 58 |
| Fully Verified | 4 (6.9%) |
| Partially Verified | 1 (1.7%) |
| Blocked by License | 43 (74.1%) |
| Blocked by Storage | 8 (13.8%) |
| Blocked by Format | 1 (1.7%) |
| Blocked by NC License | 1 (not counted above) |

---

## Critical Finding

**74.1% of discovered sources are blocked by license verification requirements.**

This indicates that license verification is the primary blocker, not storage.

---

**Registry Created**: 2026-10-31  
**Status**: PARTIAL — LICENSE VERIFICATION PENDING
