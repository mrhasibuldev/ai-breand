# NEXUSAI BRAIN - BASELINE BENCHMARK REPORT
**Date:** 2025-10-14
**Benchmark Version:** v0.1
**Status:** COMPLETE

---

## EXECUTIVE SUMMARY

The baseline benchmark reveals that while the NexusAI Brain infrastructure is functional, the actual intelligent capability is severely limited by a critical vocabulary bottleneck. The loaded Medium Transformer (4.8M parameters) has only 74 vocabulary tokens, making it incapable of meaningful generation.

**Key Metrics:**
- 50% of responses are fallback messages
- 19% of responses are neural-generated garbage
- Only 31% of responses are actually functional (deterministic greetings)
- Neural model latency is 1100-1800ms (acceptable for CPU)

**Root Cause:** The Medium model checkpoint was trained on inadequate data with severely limited vocabulary.

---

## BASELINE METRICS

### System Metrics

| Metric | Value |
|--------|-------|
| Model Parameters | 4,776,522 (4.8M) |
| Vocabulary Size | 74 tokens (CRITICAL LIMITATION) |
| Max Sequence Length | 512 |
| Device | CPU |
| API Endpoint | http://127.0.0.1:8000/orchestrate |

### Performance Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 26 |
| Success Rate | 100% (all return response) |
| Average Latency | 948.8ms |
| Min Latency | 2.8ms (deterministic) |
| Max Latency | 1802.4ms (neural/fallback) |

### Response Source Distribution

| Source | Count | Percentage | Quality |
|--------|-------|------------|---------|
| DETERMINISTIC_HANDLER | 8 | 31% | WORKING |
| FALLBACK | 13 | 50% | CRITICAL ISSUE |
| NEURAL_MODEL | 5 | 19% | GARBAGE |

### Response Quality Distribution

| Quality | Count | Percentage |
|---------|-------|------------|
| DETERMINISTIC | 8 | 31% |
| FALLBACK | 13 | 50% |
| GENERATED | 5 | 19% |

---

## CATEGORY BREAKDOWN

### Greetings (5/5 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| Hello | "Hello! I'm NexusAI..." | Deterministic | Working |
| Hi there | "Hello! I'm NexusAI..." | Deterministic | Working |
| Good morning | "Hello! I'm NexusAI..." | Deterministic | Working |
| What is your name? | "I'm NexusAI..." | Deterministic | Working |
| How are you? | "দুঃখিত..." (fallback) | Fallback | Failed |

**Success Rate:** 80% (4/5 meaningful, 1 fallback due to unmatched pattern)

### General Knowledge (5/5 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| What is the capital of Japan? | Fallback message | Fallback | Failed |
| What is photosynthesis? | Fallback message | Fallback | Failed |
| What is the speed of light? | "what is the of" | Neural | Garbage |
| What is DNA? | Fallback message | Fallback | Failed |
| What is gravity? | Fallback message | Fallback | Failed |

**Success Rate:** 0% (0/5 meaningful)

### Instruction Following (4/4 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| Give me three examples of fruits | Fallback message | Fallback | Failed |
| Explain photosynthesis simply | Fallback message | Fallback | Failed |
| Compare cats and dogs | Fallback message | Fallback | Failed |
| Summarize this: The sky is blue | "the is" | Neural | Garbage |

**Success Rate:** 0% (0/4 meaningful)

### Reasoning (3/3 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| Which is larger: 10 or 100? | "which is or" | Neural | Garbage |
| If I have 2 apples and get 3 more... | "and how do" | Neural | Garbage |
| What is 5 times 5? | Fallback message | Fallback | Failed |

**Success Rate:** 0% (0/3 meaningful)

### Context (2/2 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| My name is Alex | Fallback message | Fallback | Failed |
| What is my name? | Fallback message | Fallback | Failed |

**Success Rate:** 0% (0/2 meaningful)

### Bengali (3/3 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| হ্যালো | "হাই! আমি NexusAI..." | Deterministic | Working |
| তোমার নাম কী? | "আমার নাম NexusAI..." | Deterministic | Working |
| কেমন আছো? | "হ্যালো! আমি NexusAI..." | Deterministic | Working |

**Success Rate:** 100% (deterministic patterns working)

### Banglish (2/2 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| Hello tumi kemon acho? | "Hello! I'm NexusAI..." | Deterministic | Partial |
| Ami ki korte pari? | Fallback message | Fallback | Failed |

**Success Rate:** 50% (1/2 meaningful)

### Unknown (2/2 tests)
| Question | Response | Source | Quality |
|----------|----------|--------|---------|
| What is the meaning of X7Z-99? | "what is the of" | Neural | Garbage |
| Who invented the quantum frobnicator? | Fallback message | Fallback | Failed |

**Success Rate:** 0% (0/2 meaningful)

---

## CRITICAL ISSUES IDENTIFIED

### 1. Vocabulary Bottleneck (CRITICAL)
- **Current:** 74 tokens
- **Required:** 3000+ tokens for meaningful conversation
- **Impact:** 50% fallback rate, 19% garbage generation
- **Priority:** CRITICAL

### 2. Model Not Trained on New Dataset (CRITICAL)
- **Available:** 2948 high-quality conversations in train_v2.json
- **Current:** Trained on old inadequate data
- **Impact:** No knowledge or conversation patterns learned
- **Priority:** CRITICAL

### 3. RAG System Not Activated (HIGH)
- **Status:** Code exists but not loaded
- **Impact:** No knowledge retrieval capability
- **Priority:** HIGH

### 4. No Comprehensive Evaluation (HIGH)
- **Status:** Baseline now exists
- **Impact:** Cannot measure improvements systematically
- **Priority:** HIGH

---

## DETERMINISTIC HANDLER CAPABILITY

The deterministic handler works well for:
- Greetings (English and Bengali)
- Identity questions
- Capability questions
- Farewells
- Thanks

This is legitimate orchestration, not fake intelligence.

**Limitation:** Cannot handle general knowledge, reasoning, or contextual questions.

---

## NEURAL MODEL CAPABILITY

**Current State:** Attempting to generate but producing garbage due to 74-token vocabulary.

**Examples of garbage output:**
- "what is the of"
- "which is or"
- "and how do"
- "the is"

**Root Cause:** Vocabulary too small to encode meaningful words.

---

## LATENCY ANALYSIS

| Operation | Latency | Assessment |
|-----------|---------|------------|
| Deterministic handler | 2-6ms | Excellent |
| Neural model inference | 1100-1800ms | Acceptable for CPU |
| Fallback detection | 1100-1800ms | Same as neural |

**Conclusion:** Latency is acceptable for CPU-only inference. The issue is quality, not speed.

---

## HARDWARE UTILIZATION

**Inferred from architecture:**
- Device: CPU
- Model: 4.8M parameters
- Memory: No data collected yet
- Training: Would be slow on CPU (to be measured)

---

## BASELINE SUMMARY

### What Works:
✅ Deterministic orchestration layer
✅ Language detection (Bengali/English/Mixed)
✅ Intent classification
✅ Greeting patterns (English & Bengali)
✅ API infrastructure
✅ Chat integration
✅ Latency (acceptable for CPU)

### What Fails:
❌ General knowledge (50% fallback)
❌ Instruction following (100% fallback or garbage)
❌ Reasoning (100% garbage or fallback)
❌ Context (100% fallback)
❌ Neural model generation (garbage due to vocabulary)

### Root Cause:
The Medium model checkpoint has only 74 vocabulary tokens, making it incapable of meaningful text generation.

---

## IMPROVEMENT TARGETS

After retraining on train_v2.json with proper vocabulary:

### Minimum Targets:
- Fallback rate: < 10% (from 50%)
- Meaningful neural generation: > 70% (from 0%)
- General knowledge: > 60% meaningful (from 0%)
- Instruction following: > 60% meaningful (from 0%)
- Context: > 50% meaningful (from 0%)

### Stretch Targets:
- Fallback rate: < 5%
- Meaningful neural generation: > 85%
- General knowledge: > 80%
- Instruction following: > 80%
- Context: > 70%

---

## NEXT STEPS

**Phase 2-4:**
1. Build/improve data pipeline for train_v2.json
2. Retrain Medium model with proper vocabulary (3000+ tokens)
3. Benchmark after training to measure improvements

**Phase 5-15:**
4. RAG activation
5. Evaluation suite expansion
6. Continuous improvements

---

## BASELINE DATA

**Full results saved to:** `packages/ai-core/evaluation_results/baseline_benchmark_results.json`

**Benchmark script:** `packages/ai-core/evaluation/baseline_benchmark.py`

---

**Benchmark Completed:** 2025-10-14
**Status:** COMPLETE
**Ready for Phase 2: Data Pipeline**
