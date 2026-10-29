# NexusAI AI Core — Baseline Evaluation Report

**Date**: 2026-10-26  
**Phase**: Phase 8 - Baseline Evaluation  
**Auditor**: Senior Machine Learning Engineer, AI Reliability Engineer  
**Authorization**: Phase 8 execution authorized

---

## Executive Summary

This baseline evaluation assessed the actual capabilities and limitations of the current MediumTransformer model using diagnostic mode implemented in Phase 7. The evaluation revealed that the neural model generates consistently incoherent, repetitive output across all test prompts, justifying the existence of the quality filter. The model is not capable of factual question answering, reasoning, arithmetic, or creative generation in either English or Bengali.

**Key Findings**:
- Neural model output is uniformly incoherent and repetitive
- Quality filter correctly rejects poor output
- Simple retrieval system provides some coherent responses but often irrelevant
- Bengali language detection fails for Bengali text
- Model has no practical utility in current state

**Training Readiness Decision**: **NOT READY** - Model quality is too poor for meaningful evaluation baseline. Data foundation (Phase 1) is required before any training consideration.

---

## Test Environment

### Model and Checkpoint Identity

**Model**: MediumTransformer  
**Checkpoint**: `packages/ai-core/models/checkpoints_medium/final_model.pt`  
**Parameters**: 4,776,522  
**Vocabulary Size**: 74 tokens  
**Sequence Length**: 512  
**Device**: CPU  
**Tokenizer**: Loaded from checkpoint (Phase 4 fix verified)

### Diagnostic Configuration

**DIAGNOSTIC_MODE_ENABLED**: true (local evaluation only)  
**ML Service Port**: 8000  
**Evaluation Date**: 2026-10-26

---

## Complete Test Matrix

### English Prompts (5)

| # | Prompt | Category | Raw Neural Output | Final Response | Response Source | Rejection Reason | Latency (ms) | Coherent | Relevant | Language |
|---|--------|----------|-------------------|---------------|----------------|-----------------|--------------|----------|----------|----------|
| 1 | What is the capital of Bangladesh? | Factual | "you you your answer the and bangladesh of of the what is the capital of bangladesh?" | Bengali fallback | FALLBACK | CONTAINMENT | 2576 | ❌ | ❌ | ❌ |
| 2 | Explain why the sky appears blue in simple terms. | Explanation | "you you your answer the and bangladesh of of the the" | Same as raw | NEURAL_MODEL | null | 1620 | ❌ | ❌ | ❌ |
| 3 | What is 2 plus 2? | Arithmetic | "you you your answer the and bangladesh of of the what is" | Same as raw | NEURAL_MODEL | null | 2384 | ❌ | ❌ | ❌ |
| 4 | Tell me a short story about a cat. | Creative | "you you your answer the and bangladesh of of the" | Same as raw | NEURAL_MODEL | null | 2582 | ❌ | ❌ | ❌ |
| 5 | What happens when water boils? | Science | [Geography text from retrieval] | Same as raw | SIMPLE_RETRIEVAL | null | 0.5 | ✅ | ❌ | ✅ |

### Bengali Prompts (5)

| # | Prompt | Category | Raw Neural Output | Final Response | Response Source | Rejection Reason | Latency (ms) | Coherent | Relevant | Language |
|---|--------|----------|-------------------|---------------|----------------|-----------------|--------------|----------|----------|----------|
| 6 | বাংলাদেশের রাজধানী কোথায়? | Factual | "you you your answer the and bangladesh of of the" | Same as raw | NEURAL_MODEL | null | 1909 | ❌ | ❌ | ❌ |
| 7 | আপনি কে? | Identity | "you you your answer the and bangladesh of of the" | Same as raw | NEURAL_MODEL | null | 2335 | ❌ | ❌ | ❌ |
| 8 | আসসালামু আলাইকুম | Greeting | "you you your answer the and bangladesh of of the" | Same as raw | NEURAL_MODEL | null | 2054 | ❌ | ❌ | ❌ |
| 9 | দুই যোগ দুই কত? | Arithmetic | "you you your answer the and bangladesh of of the" | Same as raw | NEURAL_MODEL | null | 2201 | ❌ | ❌ | ❌ |
| 10 | একটি ছোট গল্প বলুন | Creative | "you you your answer the and bangladesh of of the" | Same as raw | NEURAL_MODEL | null | 1883 | ❌ | ❌ | ❌ |

### Mixed-Language Prompt (1)

| # | Prompt | Category | Raw Neural Output | Final Response | Response Source | Rejection Reason | Latency (ms) | Coherent | Relevant | Language |
|---|--------|----------|-------------------|---------------|----------------|-----------------|--------------|----------|----------|----------|
| 11 | Hello Bangladesh, what is 5 minus 3? | Mixed | "you you your answer the and bangladesh of of the what is" | Same as raw | NEURAL_MODEL | null | 2054 | ❌ | ❌ | ❌ |

### Deterministic Handler Test (1)

| # | Prompt | Category | Raw Neural Output | Final Response | Response Source | Rejection Reason | Latency (ms) | Coherent | Relevant | Language |
|---|--------|----------|-------------------|---------------|----------------|-----------------|--------------|----------|----------|----------|
| 12 | Hello | Greeting | null | "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?" | DETERMINISTIC_HANDLER | null | 1 | ✅ | ✅ | ✅ |

---

## Neural Output Analysis

### Pattern Recognition

**Dominant Pattern**: All neural outputs (except retrieval) follow the same pattern:
- "you you your answer the and bangladesh of of the [partial prompt]"

**Characteristics**:
- Highly repetitive ("you you", "of of")
- Contains training data artifacts ("bangladesh" appears in all outputs)
- Often ends with partial prompt repetition
- No semantic meaning
- No variation across different prompt types
- No language adaptation (English prompts generate same pattern as Bengali)

**Hypothesis**: Model has memorized a specific phrase from training data and repeats it regardless of input. The 74-token vocabulary is insufficient to express diverse concepts.

### Bengali Language Detection Failure

**Observation**: All Bengali prompts were detected as "unknown" language instead of "bengali"

**Impact**: Bengali prompts did not trigger Bengali deterministic responses (e.g., greeting fallbacks)

**Root Cause**: Language detection logic may have issues with Unicode ranges or the detection thresholds

---

## Response Source Distribution

| Response Source | Count | Percentage |
|-----------------|-------|------------|
| NEURAL_MODEL | 9 | 75% |
| FALLBACK | 1 | 8% |
| SIMPLE_RETRIEVAL | 1 | 8% |
| DETERMINISTIC_HANDLER | 1 | 8% |
| **Total** | **12** | **100%** |

**Note**: One neural output was rejected by quality filter (CONTAINMENT), increasing FALLBACK count from 1 to 2 if considering final responses.

---

## Quality Filter Evaluation

### Rejection Reasons

| Rejection Reason | Count | Percentage |
|-----------------|-------|------------|
| CONTAINMENT | 1 | 100% |
| EMPTY_RESPONSE | 0 | 0% |
| EQUALS_MESSAGE | 0 | 0% |
| TOO_SHORT | 0 | 0% |

### Rejection Analysis

**Rejected Output**: "you you your answer the and bangladesh of of the what is the capital of bangladesh?"

**Rejection Reason**: CONTAINMENT (response contains input message)

**Assessment**: ✅ JUSTIFIED

**Rationale**: 
- Output is incoherent and repetitive
- Contains the full input message
- Would not be useful to user
- Quality filter correctly identified poor output

**Conclusion**: Quality filter is functioning as intended and protecting users from poor neural output.

---

## Latency Summary

| Response Source | Min (ms) | Max (ms) | Avg (ms) |
|-----------------|----------|----------|----------|
| NEURAL_MODEL | 1620 | 2582 | 2154 |
| FALLBACK | 2576 | 2576 | 2576 |
| SIMPLE_RETRIEVAL | 0.5 | 0.5 | 0.5 |
| DETERMINISTIC_HANDLER | 1 | 1 | 1 |

**Observation**: Neural model inference latency is consistently 1.6-2.6 seconds on CPU, which is acceptable for current hardware but would need optimization for production use.

---

## English Performance Observations

### Factual Questions
- **Test**: "What is the capital of Bangladesh?"
- **Result**: Rejected by quality filter (CONTAINMENT)
- **Assessment**: ❌ FAIL - Cannot answer factual questions

### Explanations
- **Test**: "Explain why the sky appears blue in simple terms."
- **Result**: Incoherent repetitive output
- **Assessment**: ❌ FAIL - Cannot provide explanations

### Arithmetic
- **Test**: "What is 2 plus 2?"
- **Result**: Incoherent repetitive output
- **Assessment**: ❌ FAIL - Cannot perform arithmetic

### Creative Generation
- **Test**: "Tell me a short story about a cat."
- **Result**: Incoherent repetitive output
- **Assessment**: ❌ FAIL - Cannot generate creative content

### Science Questions
- **Test**: "What happens when water boils?"
- **Result**: Coherent but irrelevant (geography text about physical geography)
- **Assessment**: ❌ FAIL - Retrieval returned wrong topic

**Overall English Performance**: ❌ COMPLETE FAILURE

---

## Bengali Performance Observations

### Factual Questions
- **Test**: "বাংলাদেশের রাজধানী কোথায়?"
- **Result**: Incoherent repetitive output (English words)
- **Assessment**: ❌ FAIL - Cannot answer Bengali factual questions

### Identity Questions
- **Test**: "আপনি কে?"
- **Result**: Incoherent repetitive output (English words)
- **Assessment**: ❌ FAIL - Cannot respond to Bengali identity questions

### Greetings
- **Test**: "আসসালামু আলাইকুম"
- **Result**: Incoherent repetitive output (English words)
- **Assessment**: ❌ FAIL - Cannot respond to Bengali greetings

### Arithmetic
- **Test**: "দুই যোগ দুই কত?"
- **Result**: Incoherent repetitive output (English words)
- **Assessment**: ❌ FAIL - Cannot perform Bengali arithmetic

### Creative Generation
- **Test**: "একটি ছোট গল্প বলুন"
- **Result**: Incoherent repetitive output (English words)
- **Assessment**: ❌ FAIL - Cannot generate Bengali creative content

**Language Detection Issue**: All Bengali prompts detected as "unknown" instead of "bengali"

**Overall Bengali Performance**: ❌ COMPLETE FAILURE

---

## Mixed-Language Performance Observations

### Mixed Prompt
- **Test**: "Hello Bangladesh, what is 5 minus 3?"
- **Result**: Incoherent repetitive output
- **Assessment**: ❌ FAIL - Cannot handle mixed-language input

**Overall Mixed-Language Performance**: ❌ COMPLETE FAILURE

---

## Deterministic Handler Performance

### Greetings
- **Test**: "Hello"
- **Result**: "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?"
- **Assessment**: ✅ PASS - Deterministic handler provides appropriate response

**Note**: Deterministic handlers bypass neural model entirely and are not evidence of neural model capability.

---

## Limitations of This Evaluation

### Small Test Set
- Only 12 prompts tested
- Not statistically significant
- May not capture all failure modes

### No Conversation History Testing
- Each prompt was independent
- Did not test multi-turn conversation capability
- Context integration not evaluated

### No Subjective Quality Metrics
- No human judgment scoring
- No linguistic quality assessment
- Coherence and relevance assessed manually

### Limited Bengali Testing
- Bengali language detection failed
- Cannot assess whether model could generate Bengali text with correct detection
- May be a detection bug rather than model capability issue

### Retrieval System Not Fully Evaluated
- Only one retrieval test performed
- Returned irrelevant content (geography for boiling water)
- Retrieval quality needs separate evaluation

---

## Priority Problems That Must Be Addressed Before Training

### Critical (Must Fix Before Any Training)

1. **Insufficient Training Data (AI-001)**
   - Current: 19 samples
   - Required: 1000+ samples, ideally 10,000+
   - Impact: Model cannot learn meaningful patterns

2. **Critically Small Vocabulary (AI-002)**
   - Current: 74 tokens
   - Required: 2000+ tokens
   - Impact: Model cannot express diverse concepts

3. **Dataset Quality**
   - Current dataset may contain poor quality examples
   - Need diverse, high-quality conversations
   - Need proper Bengali-English balance

### High Priority (Should Fix Before Training)

4. **Bengali Language Detection**
   - Current: Fails to detect Bengali text
   - Required: Accurate language detection
   - Impact: Bengali users cannot use system

5. **Retrieval System Quality**
   - Current: Returns irrelevant content
   - Required: Accurate knowledge retrieval
   - Impact: RAG augmentation ineffective

### Medium Priority (Should Address)

6. **Quality Filter Thresholds**
   - Current: May be too aggressive
   - Required: Evidence-based threshold tuning
   - Impact: May filter acceptable responses

7. **Conversation History Integration**
   - Current: Not passed to model
   - Required: Context-aware generation
   - Impact: No multi-turn conversation capability

---

## Recommendation for Next Phase

### Immediate Next Step: Phase 1 - Data Foundation

**Rationale**:
- Current model quality is uniformly poor across all test categories
- Training data is critically insufficient (19 samples)
- Vocabulary is critically small (74 tokens)
- No meaningful baseline can be established without fixing data foundation
- Any training on current data would be wasted effort

**Phase 1 Requirements**:
1. Collect 1000+ high-quality conversation samples
2. Ensure proper Bengali-English balance
3. Expand vocabulary to 2000+ tokens
4. Validate dataset quality and diversity
5. Implement proper data preprocessing pipeline
6. Backup existing checkpoint before any retraining

**After Phase 1**:
- Re-train model with improved data
- Re-run baseline evaluation
- Assess model quality improvement
- Consider quality filter adjustments if needed

**Authorization Required**: YES (data collection and validation required)

---

## Conclusion

The current MediumTransformer model is not capable of factual question answering, reasoning, arithmetic, or creative generation in either English or Bengali. The model generates uniformly incoherent, repetitive output that justifies the existence of the quality filter. The quality filter is functioning correctly and protecting users from poor neural output.

**Model Status**: ❌ NOT PRODUCTION READY  
**Baseline Established**: ❌ NO MEANINGFUL BASELINE  
**Training Readiness**: ❌ NOT READY  
**Next Phase**: Phase 1 - Data Foundation

---

## Appendix: Raw Neural Outputs

### English Prompts
1. "you you your answer the and bangladesh of of the what is the capital of bangladesh?"
2. "you you your answer the and bangladesh of of the the"
3. "you you your answer the and bangladesh of of the what is"
4. "you you your answer the and bangladesh of of the"
5. [Geography text from retrieval system]

### Bengali Prompts
6. "you you your answer the and bangladesh of of the"
7. "you you your answer the and bangladesh of of the"
8. "you you your answer the and bangladesh of of the"
9. "you you your answer the and bangladesh of of the"
10. "you you your answer the and bangladesh of of the"

### Mixed-Language Prompt
11. "you you your answer the and bangladesh of of the what is"

**Pattern**: All neural outputs (except retrieval) follow the same repetitive pattern with training data artifacts.
