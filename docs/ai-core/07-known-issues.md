# Known Issues Register

**Last Updated**: 2026-10-26  
**Verification Status**: VERIFIED from source code and runtime inspection

---

## Issue Register

### AI-001: Insufficient Training Data

**Title**: Training dataset contains only 19 samples

**Description**: The training dataset `train_cleaned.json` used for MediumTransformer training contains only 19 text samples, which is severely insufficient for training a language model.

**Evidence**:
- File: `packages/ai-core/data/public_datasets/v1.0_cleaned/train_cleaned.json`
- Count: 19 samples (VERIFIED by file inspection)
- Training script: `train_medium_model.py` line 69
- Impact: Vocabulary limited to 74 tokens instead of configured 2000

**Status**: CONFIRMED

**Severity**: CRITICAL

**User Impact**: Model output is incoherent and unusable

**Dependencies**: None

**Related Issues**: AI-002, AI-003

**Recommended Resolution**: Collect sufficient training data (1000+ samples, ideally 10,000+)

**Verification Criteria**: Dataset contains 1000+ diverse samples with proper formatting

**Authorization**: NOT AUTHORIZED (data collection required first)

---

### AI-002: Critically Small Vocabulary

**Title**: Vocabulary size is only 74 tokens

**Description**: The tokenizer vocabulary contains only 74 tokens (70 unique words + 4 special tokens), which severely limits the model's language capability.

**Evidence**:
- Checkpoint vocabulary: 74 tokens (VERIFIED from checkpoint inspection)
- Saved tokenizer: `tokenizer/multilingual_tokenizer.json` (VERIFIED)
- Unique words in dataset: 70 (VERIFIED)
- Training script config: vocab_size=2000 (line 82)

**Status**: CONFIRMED

**Severity**: CRITICAL

**User Impact**: Model cannot express diverse concepts, output is incoherent

**Dependencies**: AI-001 (root cause)

**Related Issues**: AI-003

**Recommended Resolution**: Increase training data to support 2000+ token vocabulary

**Verification Criteria**: Vocabulary size >= 2000 tokens

**Authorization**: NOT AUTHORIZED (dependent on AI-001)

---

### AI-003: Incoherent Model Output

**Title**: Neural model generates incoherent word fragments

**Description**: The MediumTransformer generates output like "you are an by an in you on in three in to the and of of for the in a" with no semantic meaning.

**Evidence**:
- Runtime test output: "you are an by an in you on in three in to the and of of for the in a" (VERIFIED)
- Test message: "Explain why the sky appears blue in simple English."
- Response source: "NEURAL_MODEL" (VERIFIED from runtime logs)
- Inference latency: 3.1s (VERIFIED)

**Status**: CONFIRMED

**Severity**: CRITICAL

**User Impact**: Model is unusable for any practical purpose

**Dependencies**: AI-001, AI-002 (root causes)

**Related Issues**: None

**Recommended Resolution**: Retrain model with sufficient data and proper vocabulary

**Verification Criteria**: Model generates coherent, relevant responses

**Authorization**: NOT AUTHORIZED (dependent on AI-001 and AI-002)

---

### AI-004: Model Status Endpoint Hardcoded

**Title**: /model/status endpoint reports incorrect information

**Description**: The `/model/status` endpoint returns hardcoded values that do not reflect the actual loaded model.

**Evidence**:
- Endpoint response claims: SmallTransformer, checkpoint_epoch_5.pt (VERIFIED from runtime)
- Actual loaded model: MediumTransformer, final_model.pt (VERIFIED from runtime logs)
- Code: `main.py` lines 352-361 (VERIFIED hardcoded values)
- Parameter count: Correct (4,776,522)
- Vocabulary size: Correct (74)

**Status**: RESOLVED (Phase 7)

**Severity**: MEDIUM

**User Impact**: Previously: Misleading debugging/monitoring information. Now: Endpoint reports actual model name, checkpoint path, and sequence length.

**Dependencies**: None

**Related Issues**: None

**Resolution Applied**: Added model metadata tracking during model loading (loaded_model_name, loaded_checkpoint_path, loaded_max_len). Modified model_status() endpoint to return actual device from model parameters, and actual model name, checkpoint path, and sequence length from tracked metadata. Model version remains hardcoded as not stored in checkpoint.

**Verification Criteria**: Endpoint reports actual model name, checkpoint, and configuration

**Authorization**: AUTHORIZED (Phase 7 model status endpoint fix)

---

### AI-005: Hardcoded NexusAI-Specific Responses

**Title**: ML service contains hardcoded application-specific responses

**Description**: The ML service contains hardcoded Bengali/English deterministic responses that are specific to NexusAI, making the AI Core less portable.

**Evidence**:
- Code: `main.py` lines 540-611 (VERIFIED)
- Hardcoded responses for: GREETING, FAREWELL, IDENTITY_QUESTION, etc.
- NexusAI branding in responses
- Application-specific prompts

**Status**: CONFIRMED

**Severity**: MEDIUM

**User Impact**: AI Core cannot be easily reused by other applications

**Dependencies**: None

**Related Issues**: AI-006

**Recommended Resolution**: Move deterministic responses to application layer, parameterize system prompt

**Verification Criteria**: ML service has no hardcoded NexusAI-specific logic

**Authorization**: NOT AUTHORIZED (architectural refactoring required)

---

### AI-006: Hardcoded System Prompt

**Title**: System prompt is hardcoded with NexusAI branding

**Description**: The system prompt contains hardcoded NexusAI-specific information ("created by Mr. Hasibul", "NexusAI", Islam-specific knowledge).

**Evidence**:
- Code: `main.py` lines 8-26 (VERIFIED)
- Content: Creator information, NexusAI branding, Islam-specific knowledge

**Status**: CONFIRMED

**Severity**: MEDIUM

**User Impact**: AI Core cannot be used by other applications without modification

**Dependencies**: None

**Related Issues**: AI-005

**Recommended Resolution**: Make system prompt configurable via environment variable or config file

**Verification Criteria**: System prompt is externalized and configurable

**Authorization**: NOT AUTHORIZED (architectural refactoring required)

---

### AI-007: Hardcoded Filesystem Paths

**Title**: ML service has hardcoded monorepo filesystem paths

**Description**: The ML service uses hardcoded relative paths that assume the monorepo structure, reducing portability.

**Evidence**:
- Code: `main.py` lines 213-234 (VERIFIED)
- Paths: `os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")`
- Paths: `os.path.join(ai_core_dir, "data/train_v2.json")`
- Assumption: Monorepo structure with `packages/ai-core/`

**Status**: CONFIRMED

**Severity**: MEDIUM

**User Impact**: AI Core cannot be easily distributed as standalone package

**Dependencies**: None

**Related Issues**: AI-005, AI-006

**Recommended Resolution**: Use configuration file or environment variables for all paths

**Verification Criteria**: All paths are configurable

**Authorization**: NOT AUTHORIZED (architectural refactoring required)

---

### AI-008: Context Not Passed to Model

**Title**: Conversation context is stored but not included in model prompt

**Description**: The ML service stores conversation context in memory but does not include it in the prompt sent to the neural model.

**Evidence**:
- Context storage: `main.py` lines 460-471, 712-720 (VERIFIED)
- Prompt construction: line 636 (VERIFIED)
- Current prompt: Only includes current message
- Missing: Conversation history

**Status**: CONFIRMED

**Severity**: MEDIUM

**User Impact**: Model cannot maintain context across conversation turns

**Dependencies**: None

**Related Issues**: None

**Recommended Resolution**: Include conversation history in augmented prompt

**Verification Criteria**: Model prompt includes relevant conversation context

**Authorization**: NOT AUTHORIZED (implementation required)

---

### AI-009: Simple Retrieval Returns No Context

**Title**: Simple retrieval system returns context length 0 for general questions

**Description**: The simple retrieval system loads 20 documents and 24 chunks but returns no context for general knowledge questions.

**Evidence**:
- Runtime logs: "Loaded 20 documents and 24 chunks" (VERIFIED)
- Runtime logs: "Context length: 0" for sky question (VERIFIED)
- Test query: "Explain why the sky appears blue"
- Code: `knowledge/store/simple_retrieval.py`

**Status**: CONFIRMED

**Severity**: MEDIUM

**User Impact**: Retrieval augmentation is ineffective

**Dependencies**: None

**Related Issues**: None

**Recommended Resolution**: Investigate retrieval scoring and keyword matching

**Verification Criteria**: Retrieval returns relevant context for general questions

**Authorization**: NOT AUTHORIZED (investigation required)

---

### AI-010: RAG System Failed to Load

**Title**: RAG system cannot load processed data directory

**Description**: The RAG system fails to load because the `data/processed` directory does not exist.

**Evidence**:
- Runtime logs: "Processed data directory not found for RAG system" (VERIFIED)
- Code: `main.py` lines 299-329
- Expected directory: `data/processed/`

**Status**: CONFIRMED

**Severity**: LOW

**User Impact**: RAG augmentation unavailable

**Dependencies**: None

**Related Issues**: None

**Recommended Resolution**: Create processed data directory or implement data pipeline

**Verification Criteria**: RAG system loads successfully

**Authorization**: NOT AUTHORIZED (data pipeline required)

---

### AI-011: In-Memory Context Lost on Restart

**Title**: Conversation context is lost when ML service restarts

**Description**: Conversation context is stored in Python dictionary and is lost when the ML service restarts.

**Evidence**:
- Code: `main.py` line 123 (VERIFIED)
- Storage type: In-memory dict
- Persistence: None

**Status**: CONFIRMED

**Severity**: LOW

**User Impact**: Conversation history not persistent across service restarts

**Dependencies**: None

**Related Issues**: AI-008

**Recommended Resolution**: Implement persistent context storage (database or Redis)

**Verification Criteria**: Context persists across service restarts

**Authorization**: NOT AUTHORIZED (infrastructure required)

---

### AI-012: Deterministic Responses Bypass Model

**Title**: Deterministic handlers bypass neural model for common intents

**Description**: Common intents (greetings, farewells, etc.) are handled by hardcoded responses and never reach the neural model.

**Evidence**:
- Code: `main.py` lines 540-611 (VERIFIED)
- Handled intents: GREETING, FAREWELL, IDENTITY_QUESTION, etc.
- Bypass: Completely bypasses neural model

**Status**: CONFIRMED

**Severity**: LOW (intentional design)

**User Impact**: Model is not used for common interactions

**Dependencies**: None

**Related Issues**: None

**Recommended Resolution**: None (this is intentional for current model quality)

**Verification Criteria**: N/A (intentional behavior)

**Authorization**: N/A (intentional design)

---

### AI-013: Training/Inference Tokenizer Mismatch

**Title**: Inference rebuilds tokenizer from different dataset than training

**Description**: ML service rebuilds tokenizer from train_v2.json at runtime, but training used train_cleaned.json. Even though both produce 74-token vocabularies, the actual tokens are different.

**Evidence**:
- Training: train_cleaned.json (19 samples, Bengali/English mix) → 74 tokens (VERIFIED)
- Inference: train_v2.json (502 samples, mostly English) → 74 tokens capped (VERIFIED from Phase 3)
- Code: `main.py` lines 228-234 (VERIFIED - original code)
- Inference tokenizer top words: is, a, what, the, of, or, and, to, in, that (VERIFIED from Phase 3)
- Bengali words excluded from inference tokenizer (VERIFIED from Phase 3)

**Status**: RESOLVED (Phase 4)

**Severity**: MEDIUM

**User Impact**: Previously: Inference may encounter unknown words not in training vocabulary, Bengali support inconsistent. Now: Fixed by loading tokenizer from checkpoint.

**Dependencies**: AI-001, AI-002

**Related Issues**: None

**Resolution Applied**: Modified `ml-service/main.py` lines 228-239 to load tokenizer vocabulary from checkpoint if available, ensuring exact token-to-ID mapping compatibility.

**Verification Criteria**: Training and inference use identical tokenizer vocabulary

**Authorization**: AUTHORIZED (Phase 4 pipeline repair)

---

### AI-014: train_with_v2.py Conversation Flattening

**Title**: Alternative training script flattens conversation structure

**Description**: `train_with_v2.py` converts conversations to "role: content" format, losing role information for next-token prediction.

**Evidence**:
- Code: `train_with_v2.py` lines 29-40 (VERIFIED)
- Conversion: "user: Hello assistant: Hello! I'm NexusAI..." (VERIFIED)
- Impact: Model may not learn role-specific response patterns

**Status**: CONFIRMED (Phase 3)

**Severity**: LOW

**User Impact**: Reduced learning of conversation structure

**Dependencies**: None

**Related Issues**: None

**Recommended Resolution**: Consider conversation-aware training format (e.g., separate role tokens or turn-based training)

**Verification Criteria**: Training preserves conversation structure

**Authorization**: NOT AUTHORIZED (requires training script modification)

---

### AI-015: Evaluation Suite Model Mismatch

**Title**: Evaluation suite imports SmallTransformer but active model is MediumTransformer

**Description**: The evaluation suite `evaluator.py` imports SmallTransformer and type-hints it, but the actual loaded model is MediumTransformer.

**Evidence**:
- Code: `evaluation/evaluator.py` line 12 (VERIFIED - original code)
- Code: `evaluation/evaluator.py` line 21 (VERIFIED - original code)
- Active model: MediumTransformer (VERIFIED from Phase 1-3 audits)

**Status**: RESOLVED (Phase 4)

**Severity**: LOW

**User Impact**: Previously: Evaluation suite could not test MediumTransformer. Now: Model-agnostic interface allows testing any model.

**Dependencies**: None

**Related Issues**: None

**Resolution Applied**: Modified `evaluation/evaluator.py` to use model-agnostic type hint (`torch.nn.Module`) instead of specific model class, allowing evaluation of any model.

**Verification Criteria**: Evaluation suite can test MediumTransformer

**Authorization**: AUTHORIZED (Phase 4 evaluator preparation)

---

### AI-016: Response Quality Filter Hides Neural Output

**Title**: Quality filter replaces neural model output with Bengali fallback response

**Description**: The ML service includes a response quality filter that rejects neural model output and replaces it with a hardcoded Bengali fallback message, even when neural inference succeeds successfully. The original neural output is not retained for diagnostics.

**Evidence**:
|- Code: `main.py` lines 702-718 (VERIFIED BY SOURCE INSPECTION)
|- Rejection conditions: empty, equals message, < 3 chars, contains message or contained by message (VERIFIED)
|- Fallback text: Always Bengali regardless of detected language (VERIFIED)
|- Phase 5 runtime: Neural inference succeeded (2548ms) but response_source was FALLBACK (VERIFIED BY RUNTIME)
|- Neural output: Not retained anywhere for diagnostics (VERIFIED)

**Status**: RESOLVED (Phase 7)

**Severity**: HIGH

**User Impact**: Previously: Cannot assess actual neural model capability; quality filter prevents seeing model output. Now: Diagnostic mode available to inspect raw neural output when enabled.

**Dependencies**: AI-001, AI-002, AI-003 (root causes - poor model quality)

**Related Issues**: AI-004 (model status endpoint), AI-015 (evaluation suite)

**Resolution Applied**: Added diagnostic mode with environment variable gate (DIAGNOSTIC_MODE_ENABLED) and request parameter (diagnostic_mode). Raw neural output is now saved before validation and returned only when both environment variable and request parameter are enabled. Specific rejection reasons added (EMPTY_RESPONSE, EQUALS_MESSAGE, TOO_SHORT, CONTAINMENT).

**Verification Criteria**: Diagnostic mode available to inspect raw neural output; fallback text language matches detected language

**Authorization**: AUTHORIZED (Phase 7 diagnostic mode implementation)

---

## Issue Summary

| Issue ID | Title | Severity | Status | Authorized |
|-----------|-------|----------|--------|------------|
| AI-001 | Insufficient Training Data | CRITICAL | CONFIRMED | NO |
| AI-002 | Critically Small Vocabulary | CRITICAL | CONFIRMED | NO |
| AI-003 | Incoherent Model Output | CRITICAL | CONFIRMED | NO |
| AI-004 | Model Status Endpoint Hardcoded | MEDIUM | RESOLVED | YES |
| AI-005 | Hardcoded NexusAI-Specific Responses | MEDIUM | CONFIRMED | NO |
| AI-006 | Hardcoded System Prompt | MEDIUM | CONFIRMED | NO |
| AI-007 | Hardcoded Filesystem Paths | MEDIUM | CONFIRMED | NO |
| AI-008 | Context Not Passed to Model | MEDIUM | CONFIRMED | NO |
| AI-009 | Simple Retrieval Returns No Context | MEDIUM | CONFIRMED | NO |
| AI-010 | RAG System Failed to Load | LOW | CONFIRMED | NO |
| AI-011 | In-Memory Context Lost on Restart | LOW | CONFIRMED | NO |
| AI-012 | Deterministic Responses Bypass Model | LOW | CONFIRMED | N/A |
| AI-013 | Training/Inference Tokenizer Mismatch | MEDIUM | RESOLVED | YES |
| AI-014 | train_with_v2.py Conversation Flattening | LOW | CONFIRMED | NO |
| AI-015 | Evaluation Suite Model Mismatch | LOW | RESOLVED | YES |
| AI-016 | Response Quality Filter Hides Neural Output | HIGH | RESOLVED | YES |

## Prioritization

### Immediate Priority (Critical)
1. **AI-001**: Collect sufficient training data
2. **AI-002**: Increase vocabulary size (dependent on AI-001)
3. **AI-003**: Retrain model (dependent on AI-001 and AI-002)

### High Priority (Architectural)
4. **AI-005**: Remove hardcoded NexusAI responses
5. **AI-006**: Parameterize system prompt
6. **AI-007**: Externalize filesystem paths

### Medium Priority (Functional)
7. **AI-008**: Pass context to model
8. **AI-009**: Fix retrieval system
9. **AI-010**: Implement RAG data pipeline

### Low Priority (Infrastructure)
10. **AI-011**: Implement persistent context
11. **AI-004**: Fix model status endpoint
12. **AI-012**: Review deterministic response strategy (after model quality improves)

## References

- **Training Data**: `packages/ai-core/data/public_datasets/v1.0_cleaned/train_cleaned.json`
- **ML Service**: `packages/ai-core/ml-service/main.py`
- **Simple Retrieval**: `packages/ai-core/knowledge/store/simple_retrieval.py`
- **RAG System**: `packages/ai-core/data/rag_system.py`
