# NexusAI Runtime Architecture

## Active Runtime Path

```
User Message (Web UI)
    ↓
apps/web/lib/backend-conversation.ts
    ↓
POST /api/v1/ai/chat
    ↓
apps/api/src/routes/ai.ts
    ↓
fetch http://127.0.0.1:8000/orchestrate
    ↓
packages/ai-core/ml-service/main.py (FastAPI)
    ↓
load_model_if_needed()
    ↓
Load checkpoint: models/checkpoints_medium/final_model.pt
    ↓
Load tokenizer from checkpoint (74 tokens)
    ↓
Initialize MediumTransformer (4,776,522 parameters)
    ↓
Language Detection (Unicode-based: Bengali/English/Mixed/Unknown)
    ↓
Intent Classification (Pattern-based: greeting, farewell, identity, capability, etc.)
    ↓
Routing Decision:
  - If deterministic intent → DETERMINISTIC_HANDLER
  - Otherwise → NEURAL_MODEL
    ↓
Neural Model Path:
  - Try RAG augmentation (if loaded)
  - Try simple retrieval (knowledge/cleaned/)
  - Otherwise: TextGenerator.generate()
    ↓
Quality Filter:
  - Reject if empty
  - Reject if too short (<3 chars)
  - Reject if equals input
  - Reject if contains input
    ↓
Fallback (if rejected): Bengali fallback message
    ↓
Response with diagnostics
    ↓
JSON response to apps/api
    ↓
JSON response to apps/web
```

## ML Service Endpoints

### /health
Health check endpoint.

**Response**:
```json
{
  "status": "ok",
  "service": "nexusai-brain",
  "model_loaded": true
}
```

### /model/status
Model status endpoint.

**Response**:
```json
{
  "model_loaded": true,
  "model_name": "MediumTransformer",
  "model_version": "1.0.0",
  "parameter_count": 4776522,
  "checkpoint": "models/checkpoints_medium/final_model.pt",
  "device": "cpu",
  "vocabulary_size": 74,
  "sequence_length": 512
}
```

### /orchestrate
Main inference endpoint with language detection and intent classification.

**Request**:
```json
{
  "message": "Hello",
  "conversation_id": "optional-conversation-id",
  "conversation_history": [],
  "request_id": "optional-request-id",
  "diagnostic_mode": false
}
```

**Response**:
```json
{
  "response": "Hello! I'm NexusAI...",
  "latency_ms": 45,
  "intent": "GREETING",
  "response_source": "DETERMINISTIC_HANDLER",
  "language": "english",
  "diagnostics": [...]
}
```

**Response Sources**:
- `DETERMINISTIC_HANDLER` - Handled by pattern-based logic
- `NEURAL_MODEL` - Handled by neural generation
- `RAG_AUGMENTED` - Handled by RAG system
- `SIMPLE_RETRIEVAL` - Handled by simple retrieval
- `FALLBACK` - Bengali fallback message

## Deterministic Handlers

The ML service handles certain intents deterministically without using the neural model:

### Greetings
- English: "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?"
- Bengali: Random selection from Bengali greetings
- Mixed: "হ্যালো! I'm NexusAI..."

### Farewells
- English: "Goodbye! Feel free to come back anytime you need assistance."
- Bengali: "বিদায়! যখনই আপনার সাহায্য প্রয়োজন হবে, ফিরে আসুন।"

### Identity Questions
- English: "I'm NexusAI, a custom AI assistant designed to help you with various tasks."
- Bengali: "আমার নাম NexusAI। আমি একটি কাস্টম AI সহকারী..."

### Capability Questions
- English: "I can help you with conversations, answer questions, and assist with various tasks. However, my current model is still learning..."
- Bengali: "আমি কথোপকথনের মাধ্যমে সাহায্য করতে পারি..."

### Thanks
- English: "You're welcome! Is there anything else I can help you with?"
- Bengali: "স্বাগতম! আমি আপনাকে আর কীভাবে সাহায্য করতে পারি?"

### Help Requests
- English: "I'm here to help! You can ask me questions, have a conversation, or tell me what you need assistance with."
- Bengali: "আমি সাহায্য করতে প্রস্তুত! আপনি প্রশ্ন জিজ্ঞাসা করতে পারেন..."

## Language Detection

**Method**: Unicode range detection

**Implementation** (ml-service/main.py):
```python
def detect_language(text: str) -> str:
    bengali_count = 0
    latin_count = 0
    
    for char in text:
        code = ord(char)
        if 0x0980 <= code <= 0x09FF:  # Bengali Unicode range
            bengali_count += 1
        elif (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):  # Latin
            latin_count += 1
    
    if bengali_count > 0 and latin_count > 0:
        return 'mixed'
    elif bengali_count > 0:
        return 'bengali'
    elif latin_count > 0:
        return 'english'
    else:
        return 'unknown'
```

**Priority**: Bengali presence takes precedence over Latin for mixed classification.

## Quality Filter

The ML service validates neural output before returning it:

**Rejection Conditions**:
1. Empty response
2. Response equals input (case-insensitive)
3. Response length < 3 characters
4. Response contains input or input contains response

**Fallback Message** (Bengali):
```
দুঃখিত, এই বিষযটি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।
```

**Translation**: "Sorry, I do not have sufficient data or information to answer this topic."

## Diagnostic Mode

**Status**: Disabled by default for safety

**Activation**: Requires both:
1. Environment variable: `DIAGNOSTIC_MODE_ENABLED=true`
2. Request parameter: `diagnostic_mode=true`

**Diagnostic Fields** (when enabled):
- `raw_neural_output` - Raw neural output before validation
- `rejection_reason` - Reason for rejection (EMPTY_RESPONSE, EQUALS_MESSAGE, TOO_SHORT, CONTAINMENT)

**Safety**: If environment variable is not set, diagnostic fields are never exposed regardless of request parameter.

## Simple Retrieval System

**Status**: Integrated and working

**Location**: `knowledge/store/simple_retrieval.py`

**Data**: 19 cleaned documents in `knowledge/cleaned/`

**Implementation**: Keyword-based retrieval with stop-word filtering

**Usage**: Called by ML service for general questions before neural generation

## RAG System

**Status**: Loaded but not functional (missing processed data)

**Location**: `data/rag_system.py`

**Issue**: Processed data directory (`data/processed/`) does not contain required files

## Conversation Context

**Implementation**: In-memory dictionary (session-based)

**Storage**: `conversation_contexts: Dict[str, List[Dict]]`

**Retention**: Last 10 messages per conversation

**Scope**: Session-only (not persistent)

## Model Loading Configuration

**Current Configuration**: Hardcoded in `ml-service/main.py` (line 226)

```python
checkpoint_path = os.path.join(ai_core_dir, "models/checkpoints_medium/final_model.pt")
```

**Fallback Path** (if MediumTransformer fails):
```python
checkpoint_path_small = os.path.join(ai_core_dir, "models/checkpoints/checkpoint_epoch_5.pt")
```

**Future Improvement**: Use production configuration file (models/production/current.json) to remove hardcoding.

## Known Limitations

1. **74-Token Vocabulary** - Critically small for bilingual use
2. **Word-Level Tokenizer** - Poor Bengali morphological handling
3. **No Subword Tokenization** - Limits vocabulary efficiency
4. **Session-Only Context** - No persistent conversation memory
5. **Simple Retrieval** - Keyword-based, not semantic
6. **RAG Not Functional** - Missing processed data
7. **Hardcoded Checkpoint Path** - No production configuration file
8. **No Model Versioning** - Checkpoints lack full metadata

## Rollback Instructions

If changes break the ML service:

1. **Revert main.py changes**:
   ```bash
   git checkout packages/ai-core/ml-service/main.py
   ```

2. **Verify checkpoint integrity**:
   ```python
   import torch
   checkpoint = torch.load('models/checkpoints_medium/final_model.pt', map_location='cpu')
   assert 'model_state_dict' in checkpoint
   assert 'tokenizer_vocab' in checkpoint
   ```

3. **Test ML service startup**:
   ```bash
   cd packages/ai-core
   python ml-service/main.py
   ```

4. **Test inference**:
   ```bash
   curl -X POST http://127.0.0.1:8000/orchestrate \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```

---

**Last Updated**: Phase 1C - Architecture Stabilization
