# NEXUSAI BRAIN - FORENSIC CAPABILITY AUDIT
**Date:** 2025-10-14
**Phase:** A - Forensic Capability Audit

---

## EXECUTIVE SUMMARY

The NexusAI Brain currently has dual model architectures but the active model in production is the **Small Transformer** (228K parameters). The system has a sophisticated orchestration layer that uses deterministic responses for common intents and falls back to neural model generation for unknown queries. However, the neural model's training data is extremely limited (~316 samples), and the RAG system exists but is not loaded with data.

**Key Finding:** The bottleneck is primarily **insufficient and poor-quality training data**, not model architecture.

---

## 1. CURRENT ARCHITECTURE STATE

### 1.1 Tokenizer
- **Type:** Simple word-level tokenizer
- **Vocabulary Size:** 1000-2000 tokens
- **Special Tokens:** PAD, UNK, BOS, EOS
- **Tokenization Method:** Whitespace split + lowercase
- **Status:** FUNCTIONAL but limited (no subword tokenization)

**Evidence:** `packages/ai-core/tokenizer/tokenizer.py`

### 1.2 Model Architecture

#### Small Transformer (ACTIVE in production)
- **Parameters:** 228,968 (~229K)
- **d_model:** 64
- **n_layers:** 2
- **n_heads:** 2
- **d_ff:** 256
- **max_len:** 128
- **Checkpoints:** 5 epochs available

**Evidence:** `packages/ai-core/neural/transformer.py` and `packages/ai-core/ml-service/main.py` (line 186-193)

#### Medium Transformer (AVAILABLE but NOT LOADED)
- **Parameters:** 5,764,560 (~5.8M) - **25x larger**
- **d_model:** 256
- **n_layers:** 6
- **n_heads:** 8
- **d_ff:** 1024
- **max_len:** 512
- **Checkpoints:** 5 epochs + final model available

**Evidence:** `packages/ai-core/neural/medium_transformer.py`

### 1.3 Training Data

#### Dataset Analysis
| Dataset | Lines | Quality | Status |
|---------|-------|---------|--------|
| `data/synthetic/train.json` | 241 | Mixed (statements + Q&A) | Small |
| `data/train_final.json` | 316 | Similar to synthetic | Primary |
| `data/public_datasets/v1.0/train.json` | 20 | Unknown | Unused |
| `data/public_datasets/v1.0_cleaned/train_cleaned.json` | 20 | Very small | Unused |
| `data/public_datasets/v1.0_cleaned/conversational_pairs.json` | 70 | **Circular/bad data** | **TOXIC** |

**CRITICAL ISSUE:** The conversational_pairs.json contains circular data where questions are answers to previous questions, creating a confusion loop.

**Total usable training samples:** ~316

**Evidence:** File inspection and `wc -l` counts

### 1.4 Inference System
- **Location:** `packages/ai-core/inference/generator.py`
- **Sampling:** temperature, top-k, top-p, repetition_penalty
- **Status:** FUNCTIONAL with good sampling parameters

### 1.5 RAG System
- **Location:** `packages/ai-core/data/rag_system.py`
- **Embedding:** Simple character-based (demonstration only)
- **Vector Store:** In-memory
- **Status:** **NOT LOADED** - No processed data directory exists
- **Data Path Expected:** `data/processed/` - DOES NOT EXIST

**Evidence:** `packages/ai-core/ml-service/main.py` (line 228-241)

### 1.6 Orchestration Layer
- **Location:** `packages/ai-core/ml-service/main.py` (orchestrate endpoint)
- **Language Detection:** Unicode-based (Bengali/English/Mixed)
- **Intent Classification:** Pattern-based (Greeting, Farewell, Identity, Capability, etc.)
- **Routing:**
  - Deterministic handler for known intents
  - Neural model for GENERAL_QUESTION and unknown intents
  - RAG augmentation (attempted but fails due to no data)
- **Fallback:** "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"

**Status:** SOPHISTICATED but neural model has poor data

---

## 2. ROOT CAUSE ANALYSIS

### 2.1 Bottleneck Ranking

| Priority | Issue | Evidence | Impact |
|----------|-------|----------|--------|
| **CRITICAL** | Insufficient training data | Only 316 samples | Model cannot learn patterns |
| **CRITICAL** | Poor data quality | Circular conversational pairs | Confuses model during training |
| **HIGH** | RAG not activated | No processed data, system returns empty | No knowledge retrieval |
| **HIGH** | Small model in production | 229K parameters vs 5.8M available | Limited capacity |
| **MEDIUM** | Tokenizer limitations | Word-level, no subword | Poor OOV handling |
| **LOW** | Generation parameters | Already good (temp=0.8, top-k=50, top-p=0.9) | Not the issue |

### 2.2 Why Current System Fails

1. **Model is trained on only 316 samples** - This is insufficient for learning general conversation patterns
2. **Circular data** in conversational_pairs.json teaches the model that question A's answer is question B
3. **RAG system is not loaded** - No knowledge base to augment responses
4. **Small model capacity** - 229K parameters is extremely small for language modeling
5. **Medium model exists but is not used** - The better model is trained but not loaded in production

---

## 3. CAPABILITY MATRIX (PRELIMINARY)

| Capability | Current Status | Evidence | Improvement Needed |
|------------|----------------|----------|--------------------|
| Greeting | **WORKING** | Deterministic handler | None |
| Identity Question | **WORKING** | Deterministic handler | None |
| Capability Question | **WORKING** | Deterministic handler | None |
| General Knowledge | **FAILING** | Insufficient training data | CRITICAL |
| Factual Questions | **FAILING** | No RAG, insufficient data | CRITICAL |
| Context/Memory | **PARTIAL** | In-memory context (10 messages) | Could be improved |
| Follow-up Questions | **FAILING** | Model cannot maintain context | HIGH |
| Reasoning | **FAILING** | Insufficient data | HIGH |
| Unknown Handling | **HONEST** | Fallback message | GOOD |
| Multilingual | **DETECTING** | Language detection works | Model needs training |

---

## 4. DATA STRATEGY RECOMMENDATIONS

### 4.1 Immediate Actions

1. **Remove toxic circular data** from conversational_pairs.json
2. **Generate real conversational dataset** with proper Q&A pairs
3. **Add general knowledge entries** (geography, science, history)
4. **Add instruction-following examples**
5. **Add contextual conversation examples**

### 4.2 Dataset Categories Needed

#### A. Conversational Data (Target: 200+ samples)
- Greetings (variations)
- Polite conversation
- Questions and answers
- Follow-up conversations
- Clarifications

#### B. General Knowledge (Target: 150+ samples)
- Geography (countries, capitals, landmarks)
- Science (photosynthesis, gravity, etc.)
- Mathematics (basic arithmetic)
- History (major events)
- Technology (computers, internet)

#### C. Instruction Following (Target: 100+ samples)
- "Explain X simply"
- "Give me N examples"
- "Summarize this"
- "Compare X and Y"

#### D. Contextual Conversation (Target: 50+ samples)
- Name retention
- Location retention
- Multi-turn context

**Total Target:** 500+ high-quality samples

---

## 5. MODEL STRATEGY

### 5.1 Recommended Path

**Option A (Recommended):**
1. Switch to Medium Transformer (5.8M parameters)
2. Retrain with new high-quality dataset
3. Activate RAG with processed data
4. Test and evaluate

**Option B (Conservative):**
1. Keep Small Transformer
2. Improve dataset dramatically
3. Train for more epochs
4. Later upgrade to Medium model

**Recommendation:** Option A - The Medium model is already trained and has 25x capacity. We should use it.

---

## 6. IMPLEMENTATION PLAN

### Phase A (CURRENT): Forensic Audit ✅
- [x] Inspect tokenizer
- [x] Inspect model architecture
- [x] Inspect training data
- [x] Inspect inference system
- [x] Inspect RAG system
- [x] Inspect orchestration layer
- [x] Identify bottlenecks
- [x] Create capability matrix

### Phase B: Data Generation & Cleaning
- [ ] Remove circular data
- [ ] Generate conversational dataset
- [ ] Generate general knowledge dataset
- [ ] Generate instruction-following dataset
- [ ] Generate contextual conversation dataset
- [ ] Validate data quality
- [ ] Save as train_v2.json

### Phase C: Model Configuration
- [ ] Switch ML service to load Medium model
- [ ] Update model loading path
- [ ] Test model loading
- [ ] Verify inference works

### Phase D: Training
- [ ] Prepare dataset for Medium model
- [ ] Build tokenizer for new dataset
- [ ] Train Medium model on new data
- [ ] Save checkpoints
- [ ] Validate training metrics

### Phase E: RAG Activation
- [ ] Process data for RAG
- [ ] Create processed/ directory
- [ ] Generate embeddings
- [ ] Load RAG system in ML service
- [ ] Test retrieval

### Phase F: Testing & Evaluation
- [ ] Run 22-question test set
- [ ] Measure meaningful response rate
- [ ] Measure repetition rate
- [ ] Measure retrieval success
- [ ] Document before/after

---

## 7. HARDWARE CONSTRAINTS

- **Device:** CPU-only (no GPU available)
- **Memory:** Limited
- **Training Time:** Slow for large models
- **Inference:** Must be < 2 seconds for UX

**Implication:** Cannot train massive models, but Medium model (5.8M) is feasible on CPU.

---

## 8. NEXT STEPS

**Immediate:** Start Phase B - Data Generation & Cleaning

**Priority:** Generate 500+ high-quality training samples covering the categories identified above.

---

## SIGNATURE

**Audited by:** Devin AI Assistant
**Date:** 2025-10-14
**Status:** COMPLETE - Ready for Phase B
