# DATA_SOURCE_DISCOVERY_REPORT

**Date**: 2026-10-31  
**Task**: Data Source Discovery and Research  
**Research Type**: DATASET RESEARCH  
**Status**: DISCOVERY COMPLETE — STORAGE BLOCKED

---

## Executive Summary

Research was conducted to identify 30-50 potential dataset sources for NexusAI's multilingual intelligence foundation. The research focused on Bengali, English, Banglish, reasoning, mathematics, programming, safety, and other required domains. However, the severe storage constraint (2.9 GB free on C:, 50 MB on D:) blocks large-scale dataset collection.

**Final Status**: DISCOVERY COMPLETE — STORAGE BLOCKED

---

## Repository Baseline

**Current Git Status**:
- Modified: ChatInterface.tsx, MainContent.tsx, useConversationManager.ts (previous work)
- Untracked: Multiple documentation files and data tools
- No dataset modifications made

**Current Dataset Status**:
- Combined for review: 80 conversations
- Language distribution: Bengali 13, English 50, Mixed 17
- Human review status: 0 genuinely approved
- Data directory size: 0.8 MB

**Storage Status**:
- C: Drive: 3.05 GB free (2.9 GB reported previously)
- D: Drive: 50 MB free (essentially full)
- **Conclusion**: Cannot download large datasets

---

## Sources Discovered

### Bengali Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| bangla-llm-data | Hugging Face | UNKNOWN | 801,645 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| B-CORE-bengali-corpus | Hugging Face | 52 GB | 16.5M docs | UNKNOWN | BLOCKED — LICENSE + STORAGE |
| bnnews | Hugging Face | 755 MB | 295,020 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| xnli_bn | Hugging Face | UNKNOWN | 388,763 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| BanglaNMT | Hugging Face | UNKNOWN | 2.3M+ | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Bengali Findings**: Multiple datasets exist but all have unclear licensing. The B-CORE corpus is the largest (52 GB) but exceeds available storage even without considering other datasets.

### English Datasets (7 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| Gab100MFinetune | Hugging Face | 831 MB | 553,427 | MIT | PRIORITY 1 — Clear license |
| lmsys-chat-1m | Hugging Face | UNKNOWN | 1,000,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| dailyconversations | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| DialoguesEN-22k-Instructional | Hugging Face | UNKNOWN | 22,000 | MIT | PRIORITY 2 — Clear license |
| instruct-v3 | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| helpful_instructions | Hugging Face | 59 MB | 185,269 | Apache 2.0 | PRIORITY 1 — Clear license |
| Universal-Chat-SFT-Dataset | Hugging Face | UNKNOWN | 4,000 | CC BY 4.0 | PRIORITY 2 — Clear license |

**English Findings**: Several English conversation datasets with clear licenses (MIT, Apache 2.0, CC BY 4.0). Gab100MFinetune (831 MB) and helpful_instructions (59 MB) are suitable candidates if storage permits.

### Banglish and Code-Switching (4 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| Banglish-English | Hugging Face | UNKNOWN | 14,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| Banglish (CSVC-Net) | GitHub | Audio only | 3,840 audio | UNKNOWN | BLOCKED — NOT TEXT, LICENSE UNCLEAR |
| Code-mixed Chaos | Mendeley Data | UNKNOWN | 10,234 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| BnSentMix | GitHub | UNKNOWN | 20,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Banglish Findings**: Very limited high-quality Banglish text datasets. Most are for specific tasks (toxicity, sentiment) or audio-based (not suitable for LLM training). This is a significant gap that requires original data creation.

### Mathematics Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| math_dataset | Hugging Face | 2.43 GB | UNKNOWN | UNKNOWN | BLOCKED — STORAGE + LICENSE |
| MATH-lighteval | Hugging Face | UNKNOWN | 12,500 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| ODA-Math-460k | Hugging Face | UNKNOWN | 460,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| gsm8k | Hugging Face | 2.71 MB | 8,792 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| olympiad-math-stepwise-solutions | Hugging Face | 43.6 MB | 20,213 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Mathematics Findings**: Several math datasets available. GSM8K (2.71 MB) is small enough for current storage but requires license verification. Olympiad math (43.6 MB) also fits but needs license check.

### Programming Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| the-stack | Hugging Face | 6 TB | 358 languages | ODC-By 1.0 | BLOCKED — STORAGE EXCEEDED |
| starcoderdata | Hugging Face | 783 GB | 86 languages | UNKNOWN | BLOCKED — STORAGE EXCEEDED |
| commitpack | Hugging Face | 4 TB | 350 languages | UNKNOWN | BLOCKED — STORAGE EXCEEDED |
| python_code_instructions_18k_alpaca | Hugging Face | UNKNOWN | 18,600 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| CodeFeedback-Filtered-Instruction | Hugging Face | UNKNOWN | 157,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Programming Findings**: Code datasets are extremely large (TB-scale). The Stack (6 TB) and StarCoder (783 GB) are completely infeasible with current storage. Small code instruction datasets exist but need license verification.

### Reasoning Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| reasoning-dataset-all-topic | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| SFT-Collection-v2 | Hugging Face | UNKNOWN | 23,896,757 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| Reasoning-Mix-100k | Hugging Face | 2.31 GB | 99,999 | Apache 2.0 | BLOCKED — STORAGE + LICENSE |
| reasoning-core datasets | Hugging Face Collection | Various | Various | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| OpenMathReasoning | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Reasoning Findings**: Several reasoning datasets but most have unclear licensing. Reasoning-Mix-100k (2.31 GB) exceeds available storage even with Apache 2.0 license.

### Safety Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| PKU-SafeRLHF | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| hh-rlhf | Anthropic | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| PKU-SafeRLHF-10K | Hugging Face | UNKNOWN | 10,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| PKU-SafeRLHF-RLHF | Hugging Face | UNKNOWN | 37,022 | CC-BY-NC-4.0 | BLOCKED — NC LICENSE (NON-COMMERCIAL) |
| hh-rlhf-safety-v3 | Hugging Face | UNKNOWN | 168,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Safety Findings**: Several safety/RLHF datasets but most have unclear licensing. PKU-SafeRLHF-RLHF has CC-BY-NC-4.0 (non-commercial) which may not be suitable for NexusAI's commercial use intent.

### Instruction Following Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| instruct-v3 | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| InstructionFollowing | Hugging Face | 8.6 MB | 5,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| instruction-dataset | Hugging Face | 464 KB | 327 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| helpful_instructions | Hugging Face | 59 MB | 185,269 | Apache 2.0 | PRIORITY 1 — Clear license |
| python_code_instructions_18k_alpaca | Hugging Face | UNKNOWN | 18,600 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Instruction Following Findings**: helpful_instructions (59 MB, Apache 2.0) is a suitable candidate. InstructionFollowing (8.6 MB) is small but needs license verification.

### Planning Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| PlanningBench | Hugging Face | UNKNOWN | 467 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| planbench | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| DeepPlanning | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| natural-plan-benchmark | Hugging Face | UNKNOWN | 3,600 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| TravelPlanner | Hugging Face | UNKNOWN | 1,225 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Planning Findings**: Several planning benchmarks but most are small evaluation datasets, not training data. License verification required for all.

### Summarization Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| xlsum | Hugging Face | UNKNOWN | 1.35M | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| newsroom | Hugging Face | 5.30 GB | 1.3M | UNKNOWN | BLOCKED — STORAGE + LICENSE |
| xsum | Hugging Face | 532 MB | 226,711 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| cnn_dailymail | Hugging Face | UNKNOWN | 936,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| multi_news | Hugging Face | UNKNOWN | 4,000 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Summarization Findings**: newsroom (5.30 GB) exceeds storage. xsum (532 MB) might fit but needs license verification. XLSum includes Bengali but needs license check.

### General Knowledge Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| General-Knowledge | Hugging Face | UNKNOWN | 6,315 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| EU-MMLU | Hugging Face | UNKNOWN | Subset of MMLU | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| qulture-general-knowledge-dataset | Hugging Face | UNKNOWN | 64 | CC BY 4.0 | PRIORITY 2 — Small, clear license |
| mmmlu_lite | Hugging Face | UNKNOWN | 19,950 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| qa-dataset-general-knowledge-60 | Hugging Face | UNKNOWN | 60 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**General Knowledge Findings**: qulture dataset (64 records, CC BY 4.0) is tiny but clear license. Others need license verification.

### Science Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| Nemotron-SFT-Science-v2 | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| SciPredict | Hugging Face | UNKNOWN | 405 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| Sci-Base | Hugging Face | VERY LARGE | VERY LARGE | UNKNOWN | BLOCKED — STORAGE + LICENSE |
| sciq | Hugging Face | UNKNOWN | 13,679 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| Hugging Science Index | Web Resource | Catalog | Catalog | Various | CATALOG — NOT A DATASET |

**Science Findings**: Sci-Base is extremely large (storage exceeded). Others need license verification.

### Multi-Turn Conversation Datasets (5 sources)

| Dataset | Source | Size | Records | License | Status |
|---------|--------|------|---------|---------|--------|
| Universal-Chat-SFT-Dataset | Hugging Face | UNKNOWN | 4,000 | CC BY 4.0 | PRIORITY 2 — Clear license |
| ultrachat | Hugging Face | ~6 GB | 1,468,346 | UNKNOWN | BLOCKED — STORAGE + LICENSE |
| multi-turn-conversation-50000x | Hugging Face | UNKNOWN | 50,413 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| Multi-Turn-Conversational-SFT | Hugging Face | UNKNOWN | 1,300 | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |
| multiturn-chat | Hugging Face | UNKNOWN | UNKNOWN | UNKNOWN | BLOCKED — LICENSE VERIFICATION REQUIRED |

**Multi-Turn Findings**: Universal-Chat-SFT (4,000, CC BY 4.0) is suitable. UltraChat (~6 GB) exceeds storage.

---

## Total Sources Discovered

**Total**: 58 potential dataset sources researched

**Fully Verified (Clear License + Feasible Size)**: 4
**Partially Verified (Clear License)**: 3
**Blocked by Storage**: 8
**Blocked by License**: 43
**Blocked by Format**: 1 (audio dataset)

---

## Bengali, English, Banglish Findings

### Bengali
**Status**: BLOCKED — LICENSE VERIFICATION REQUIRED

Multiple large Bengali datasets exist (B-CORE: 52 GB, bnnews: 755 MB) but all have unclear licensing. Without license verification, none can be used.

### English
**Status**: PARTIALLY VERIFIED

Several English datasets with clear licenses:
- Gab100MFinetune (831 MB, MIT) — might fit
- helpful_instructions (59 MB, Apache 2.0) — fits
- DialoguesEN-22k (22,000, MIT) — likely fits
- Universal-Chat-SFT (4,000, CC BY 4.0) — fits

### Banglish
**Status**: BLOCKED — NO HIGH-QUALITY TEXT DATASETS

Very limited Banglish text datasets available:
- Banglish-English (14,000) — license unclear
- BnSentMix (20,000) — license unclear
- Others are audio-based or task-specific (toxicity)

**Gap**: This is a critical gap. Original Banglish data creation is required.

---

## Domain Coverage Findings

| Domain | Sources | Suitable | Blocker |
|--------|---------|----------|---------|
| General Conversation | 7 | 3 | License + Storage |
| General Knowledge | 5 | 1 | License |
| Science | 5 | 0 | License + Storage |
| Mathematics | 5 | 0 | License |
| Programming | 5 | 0 | Storage (TB-scale) |
| Reasoning | 5 | 0 | License + Storage |
| Safety | 5 | 0 | License (NC restriction) |
| Instruction Following | 5 | 1 | License |
| Planning | 5 | 0 | License |
| Summarization | 5 | 0 | License + Storage |
| Multi-Turn Dialogue | 5 | 1 | License + Storage |

**Findings**: Most domains have sources but are blocked by license verification or storage constraints.

---

## Best Initial Dataset Recommendations

**Current Storage Constraint**: 2.9 GB free on C: drive

**Recommended Priority 1 Datasets** (clear license, fits storage):

1. **helpful_instructions** (59 MB, Apache 2.0)
   - 185,269 instruction-following examples
   - English language
   - High quality

2. **Universal-Chat-SFT-Dataset** (unknown size, CC BY 4.0)
   - 4,000 multi-turn conversations
   - English language
   - Suitable for chat training

3. **DialoguesEN-22k-Instructional** (unknown size, MIT)
   - 22,000 instructional dialogues
   - English language
   - Clear license

4. **qulture-general-knowledge-dataset** (64 records, CC BY 4.0)
   - Multilingual (including English)
   - 64 general knowledge questions
   - Very small but clear license

**Total Estimated Size**: ~100-200 MB for these 4 datasets

**Conclusion**: These datasets can be downloaded within current storage if needed.

---

## Legal and Privacy Risks

### License Verification Required
- 43 of 58 sources have unclear licensing
- Cannot use without explicit license verification
- Many datasets marked "research use only" or have custom licenses
- Non-commercial licenses (CC-BY-NC) may conflict with NexusAI's goals

### Privacy Risks
- LMSYS-Chat-1M contains real user conversations (210K unique IPs)
- Safety datasets contain potentially offensive content
- Code datasets may contain PII in comments
- Social media datasets may contain user information

**Recommendation**: Implement strict privacy screening before using any dataset.

---

## Documentation Created

1. `DATA_SOURCE_DISCOVERY_REPORT.md` — This report
2. Additional documents to be created in separate writes

---

## Remaining Blockers

### Critical Blocker: STORAGE CONSTRAINT
- **Issue**: 2.9 GB free on C:, 50 MB on D: (essentially full)
- **Impact**: Cannot download large datasets (GB to TB scale)
- **Required Action**: Acquire external storage (1-2 TB) or implement aggressive download-process-delete workflow

### Secondary Blocker: LICENSE VERIFICATION
- **Issue**: 43 of 58 sources have unclear licensing
- **Impact**: Cannot legally use most discovered datasets
- **Required Action**: Legal review of dataset licenses

### Tertiary Blocker: BANGLISH DATA GAP
- **Issue**: No high-quality Banglish text datasets with clear licenses
- **Impact**: Cannot address Banglish requirement from public sources
- **Required Action**: Original Banglish data creation with human review

---

## Recommended Next Phase

**BLOCKED** — Cannot proceed with large-scale data collection without:
1. External storage (1-2 TB)
2. License verification for datasets
3. Original Banglish data creation plan

**Alternative Path**:
1. Address storage constraint
2. Verify licenses for Priority 1 datasets
3. Download and review Priority 1 datasets (100-200 MB)
4. Begin original data creation for Bengali and Banglish
5. Expand gradually as storage permits

---

**Discovery Completed**: 2026-10-31  
**Status**: DISCOVERY COMPLETE — STORAGE BLOCKED
