# Chat Pipeline — Frontend to Backend to Model Request Flow

**Last Updated**: 2026-10-26  
**Verification Status**: PARTIALLY VERIFIED (backend-to-model verified, frontend-to-backend source-inspected only)

---

## Overview

This document traces the complete request flow from user message submission through the frontend, backend API, ML service, and neural model, back to the frontend display.

## Complete Request Flow

```
User Message
    ↓
Frontend: ChatInterface.tsx (React/Next.js)
    ↓
HTTP POST http://localhost:4000/api/v1/ai/chat
    ↓
Backend: apps/api/src/routes/ai.ts (Fastify/TypeScript)
    ↓
HTTP POST http://127.0.0.1:8000/orchestrate
    ↓
ML Service: packages/ai-core/ml-service/main.py (FastAPI/Python)
    ↓
Orchestrator (language detection, intent classification)
    ↓
Response Routing (deterministic → retrieval → neural model)
    ↓
Neural Model: MediumTransformer (PyTorch)
    ↓
Inference: TextGenerator.generate()
    ↓
ML Service Response
    ↓
Backend Response
    ↓
Frontend Display
```

## Stage 1: Frontend Submission

### Component

**File**: `apps/web/app/components/ChatInterface.tsx`

**Technology**: React 19, TypeScript, Next.js 15.5.24

**Port**: 3000

### Function: handleSubmit()

**Location**: Lines 115-157 (estimated, need verification)

**Behavior**:
1. User types message in chat input
2. User submits form (Enter key or Send button)
3. `handleSubmit()` is called
4. Routes to guest or authenticated flow

### Guest Mode Flow

**Function**: `handleGuestMessage()`

**Behavior**:
1. Creates in-memory guest conversation
2. Sends request to backend API
3. Displays response in guest conversation

**Request Payload**:
```typescript
{
  message: userMessage,
  conversationId: 'guest',
  context: []
}
```

**Request Details**:
```typescript
const response = await fetch('http://localhost:4000/api/v1/ai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
  body: JSON.stringify({
    message: userMessage,
    conversationId: 'guest',
    context: [],
  }),
});
```

**Response Handling**:
```typescript
const data = await response.json();
content: data.response
```

### Authenticated Mode Flow

**Function**: `handleSendMessage()`

**Behavior**:
1. Creates conversation via conversation manager
2. Sends request to backend API with accountId
3. Updates conversation with response
4. Persists to database

**Request Payload**:
```typescript
{
  message: userMessage,
  conversationId: conversationId,
  context: []
}
```

**Cookies**: Auth cookie included via `credentials: 'include'`

### Verification Status

**Status**: SOURCE-INSPECTED ONLY

**Evidence**: Source code inspected shows correct implementation. Frontend was not runtime tested due to existing process on port 3000.

---

## Stage 2: Backend API Receipt

### Component

**File**: `apps/api/src/routes/ai.ts`

**Technology**: Fastify 5, TypeScript

**Port**: 4000

### Endpoint

**Route**: `POST /api/v1/ai/chat`

**Middleware**: `optionalAuthMiddleware` (allows both guest and authenticated users)

### Request Handling

**Location**: Lines 29-83

**Behavior**:
1. Extract `accountId` from request (if authenticated)
2. Extract `message`, `conversationId`, `context` from body
3. Validate message is not empty
4. Call Python ML service
5. Return response to frontend

### ML Service Call

**Code**:
```typescript
const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';

const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

const response = await fetch(`${aiServiceUrl}/orchestrate`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  signal: controller.signal,
  body: JSON.stringify({
    message,
    conversation_id: conversationId,
    context: context || [],
    user_id: accountId,
  }),
});
```

**Request Payload to ML Service**:
```json
{
  "message": "user message",
  "conversation_id": "guest or actual id",
  "context": [],
  "user_id": "accountId or null"
}
```

### Response Handling

**Code**:
```typescript
const aiResponse = await response.json();

return reply.send({
  response: aiResponse.response || aiResponse.message || aiResponse.text || 'No response from AI',
  conversationId: aiResponse.conversation_id || conversationId,
  messageId: aiResponse.message_id,
});
```

**Response to Frontend**:
```json
{
  "response": "generated text",
  "conversationId": "guest or actual id",
  "messageId": "optional message id"
}
```

### Error Handling

**Timeout** (10 seconds):
```typescript
if (error instanceof Error && error.name === 'AbortError') {
  return reply.status(504).send({ error: 'AI service timeout' });
}
```

**Service Unavailable**:
```typescript
return reply.status(502).send({ error: 'AI service unavailable' });
```

### Verification Status

**Status**: RUNTIME VERIFIED

**Evidence**: Backend successfully started on port 4000 and received test requests during runtime verification.

---

## Stage 3: Backend to ML Service Request

### Component

**File**: `packages/ai-core/ml-service/main.py`

**Technology**: FastAPI, Python 3.14.6, PyTorch 2.14.1+cpu

**Port**: 8000 (binds to 127.0.0.1)

### Endpoint

**Route**: `POST /orchestrate`

**Function**: `orchestrate()` (lines 417-781)

### Request Parsing

**Code** (lines 423-432):
```python
body_bytes = await request.body()
body_text = body_bytes.decode('utf-8')
body_data = json.loads(body_text)

message = body_data.get('message', '')
conversation_id = body_data.get('conversation_id')
conversation_history = body_data.get('conversation_history', [])
request_id = body_data.get('request_id')
```

**Note**: Manual UTF-8 decoding to handle Bengali text correctly

### Model Loading

**Code** (lines 433-434):
```python
if not model_loaded:
    load_model_if_needed()
```

**Behavior**: Loads MediumTransformer from `final_model.pt` on first request

### RAG Loading

**Code** (lines 436-437):
```python
if not rag_loaded:
    load_rag_if_needed()
```

**Behavior**: Attempts to load RAG system if available

### Verification Status

**Status**: RUNTIME VERIFIED

**Evidence**: ML service successfully started on port 8000 and received requests during runtime verification.

---

## Stage 4: Language Detection

### Function

**Location**: `detect_language()` (lines 126-154)

### Implementation

**Method**: Unicode range detection

**Bengali Range**: U+0980 to U+09FF

**Latin/English Range**: A-Z, a-z

### Detection Logic

```python
if bengali_count > 0:
    if latin_count > 0:
        return 'mixed'
    return 'bengali'
elif latin_count > 0:
    return 'english'
else:
    return 'unknown'
```

### Verification Status

**Status**: SOURCE-INSPECTED

**Evidence**: Source code inspected shows Unicode-based detection.

---

## Stage 5: Intent Classification

### Function

**Location**: Lines 473-531 in `orchestrate()`

### Bengali Patterns

**Greetings**: হ্যালো, হাই, হেলো, আসসালামু, নমস্কার, শুভ, সকাল, দুপুর, সন্ধ্যা, কেমন আছ, কেমন আছো, কেমন আছেন

**Farewells**: বিদায়, আবার, দেখা, কেয়ার, যাচ্ছি, যাই

**Identity**: নাম, কী, কি, তোমার, তোমার নাম

**Capability**: করতে, পার, সক্ষম, সাহায্য, কী করতে পারো, কী করতে পারে

**Thanks**: ধন্যবাদ, থ্যাংক, শুকরিয়া

**Help**: সাহায্য, হেল্প, সাহায্য চাই, হেল্প চাই

**Casual**: কেমন, কী খবর, কেমন চলছে, কী অবস্থা

### English Patterns

**Greetings**: hello, hi, hey, good morning, good afternoon, good evening

**Farewells**: bye, goodbye, farewell, see you, take care

**Identity**: name + your

**Capability**: what can you do, what are your capabilities, how can you help

**Thanks**: thank, thanks, appreciate

**Help**: help me, help, assist

**Questions**: what, how, why, when, where, who (at start of message)

### Knowledge Topics

**Keywords**: science, mathematics, math, physics, chemistry, biology, computer science, history, philosophy, economics, geography, what is, tell me about, explain, define, describe

**Intent**: GENERAL_QUESTION

### Verification Status

**Status**: SOURCE-INSPECTED

**Evidence**: Source code inspected shows keyword/pattern-based intent classification.

---

## Stage 6: Response Routing

### Function

**Location**: Lines 536-611 in `orchestrate()`

### Routing Logic

```
┌─────────────────────────────────────┐
│ Language Detection                  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Intent Classification               │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Route to Appropriate Handler       │
│                                     │
│ ┌───────────────────────────────┐  │
│ │ Deterministic Handler         │  │
│ │ (Greeting, Farewell, etc.)   │  │
│ └──────────┬────────────────────┘  │
│            │                       │
│            ├─ Bypasses Neural Model │
│            │                       │
│            ▼                       │
│ ┌───────────────────────────────┐  │
│ │ Neural Model                 │  │
│ │ (General Question, Unknown)  │  │
│ └──────────┬────────────────────┘  │
│            │                       │
│            ├─ Uses Model          │
│            │                       │
│            ▼                       │
│ ┌───────────────────────────────┐  │
│ │ Retrieval (Simple/RAG)        │  │
│ │ (Optional augmentation)       │  │
│ └──────────┬────────────────────┘  │
│            │                       │
│            ▼                       │
│ ┌───────────────────────────────┐  │
│ │ Fallback (if validation fails)│  │
│ └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Deterministic Handler

**Location**: Lines 540-611

**Handled Intents**:
- GREETING
- FAREWELL
- IDENTITY_QUESTION
- CAPABILITY_QUESTION
- THANKS
- HELP_REQUEST
- CASUAL_CHECKIN

**Behavior**: Returns hardcoded Bengali/English responses

**Example** (Bengali Greeting):
```python
greetings = [
    "হ্যালো! আমি NexusAI, আপনার ব্যক্তিগত AI সহকারী। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
    "আসসালামু আলাইকুম! আমি NexusAI। আপনার জন্য কী করতে পারি?",
    # ...
]
response_text = random.choice(greetings)
```

**Response Source**: `DETERMINISTIC_HANDLER`

### Neural Model Handler

**Location**: Lines 614-690

**Triggered Intents**:
- GENERAL_QUESTION
- UNKNOWN

**Behavior**:
1. Try simple retrieval first
2. Try RAG augmentation if available
3. Use neural model generation
4. Validate output
5. Apply fallback if validation fails

**Response Source**: `NEURAL_MODEL`, `SIMPLE_RETRIEVAL`, `RAG_AUGMENTED`, or `FALLBACK`

### Verification Status

**Status**: RUNTIME VERIFIED

**Evidence**: Runtime test confirmed "Hello" triggered deterministic handler and "Explain why..." triggered neural model.

---

## Stage 7: Neural Model Invocation

### Function

**Location**: Lines 672-680 in `orchestrate()`

### Code

```python
response_text = generator.generate(
    prompt=augmented_message,
    max_new_tokens=50,
    temperature=0.8,
    top_k=50,
    top_p=0.9,
    do_sample=True,
    repetition_penalty=1.2
)
```

### Augmented Prompt

**Code** (line 636):
```python
augmented_message = f"{SYSTEM_PROMPT}\n\nUser: {message}\nAssistant:"
```

**System Prompt** (lines 8-26):
```
You are an AI assistant created by Mr. Hasibul, an engineer based in Bangladesh. 
You respond accurately based on your knowledge base in three styles/languages:
- English
- Banglish (Bengali written in English alphabet)
- Bengali (বাংলা)

Always answer according to the user's input language and tone.

Creator Information:
- Created by: Mr. Hasibul
- Profession: Engineer
- Location: Bangladesh

Key Knowledge:
- First pillar of Islam: Shahada (faith)
- Five pillars of Islam: Shahada, Salah, Zakat, Sawm, Hajj
- Salah: Islamic prayer performed five times daily
- Zakat: Obligatory charity for helping the poor
```

### TextGenerator.generate()

**File**: `packages/ai-core/inference/generator.py`

**Behavior**:
1. Encode prompt to token IDs
2. Autoregressively generate tokens
3. Apply temperature, top-k, top-p sampling
4. Apply repetition penalty
5. Decode token IDs to text

### Model Used

**Model**: MediumTransformer

**Checkpoint**: `models/checkpoints_medium/final_model.pt`

**Parameters**: 4,776,522

**Vocabulary**: 74 tokens

### Runtime Output

**Test Message**: "Explain why the sky appears blue in simple English."

**Model Output**: "you are an by an in you on in three in to the and of of for the in a"

**Quality**: INCOHERENT

### Verification Status

**Status**: RUNTIME VERIFIED

**Evidence**: Runtime logs show "Neural Model Inference: success" with 3.1s latency.

---

## Stage 8: Response Validation

### Function

**Location**: Lines 694-710 in `orchestrate()`

### Validation Rules

```python
is_fallback = False

if not response_text:
    response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
    is_fallback = True
elif response_text == message.lower():
    response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
    is_fallback = True
elif len(response_text) < 3:
    response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
    is_fallback = True
elif response_text.lower() in message.lower() or message.lower() in response_text.lower():
    response_text = "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"
    is_fallback = True
```

### Fallback Response

**Response Source**: `FALLBACK`

**Fallback Message**: "দুঃখিত, এই বিষয়টি উত্তর দেওয়ার জন্য আমার কাছে পর্যাপ্ত পরিমাণ ডেটা বা তথ্য নেই।"

**Translation**: "Sorry, I don't have enough data or information to answer this topic."

### Verification Status

**Status**: SOURCE-INSPECTED

**Evidence**: Source code inspected shows validation rules.

---

## Stage 9: ML Service Response

### Response Format

**Code** (lines 760-767):
```python
return OrchestratorResponse(
    response=response_text,
    latency_ms=latency_ms,
    intent=intent,
    response_source=response_source,
    language=language,
    diagnostics=diagnostics
)
```

### Response Fields

- `response`: Generated text
- `latency_ms`: Processing time in milliseconds
- `intent`: Detected intent (GREETING, GENERAL_QUESTION, etc.)
- `response_source`: Source of response (DETERMINISTIC_HANDLER, NEURAL_MODEL, etc.)
- `language`: Detected language (bengali, english, mixed, unknown)
- `diagnostics`: Processing step status

### Example Response

**Deterministic Handler**:
```json
{
  "response": "Hello! I'm NexusAI, your personal AI assistant. How can I help you today?",
  "latency_ms": 1,
  "intent": "GREETING",
  "response_source": "DETERMINISTIC_HANDLER",
  "language": "english",
  "diagnostics": [...]
}
```

**Neural Model**:
```json
{
  "response": "you are an by an in you on in three in to the and of of for the in a",
  "latency_ms": 3163.97,
  "intent": "GENERAL_QUESTION",
  "response_source": "NEURAL_MODEL",
  "language": "english",
  "diagnostics": [...]
}
```

### Verification Status

**Status**: RUNTIME VERIFIED

**Evidence**: Runtime test confirmed response format and fields.

---

## Stage 10: Backend Response

### Function

**Location**: `apps/api/src/routes/ai.ts` lines 68-74

### Code

```typescript
const aiResponse = await response.json();

return reply.send({
  response: aiResponse.response || aiResponse.message || aiResponse.text || 'No response from AI',
  conversationId: aiResponse.conversation_id || conversationId,
  messageId: aiResponse.message_id,
});
```

### Response Extraction

**Field Extracted**: `aiResponse.response`

**Fallback Fields**: `aiResponse.message`, `aiResponse.text`, or `'No response from AI'`

### Response to Frontend

```json
{
  "response": "generated text",
  "conversationId": "guest or actual id",
  "messageId": "optional message id"
}
```

### Verification Status

**Status**: RUNTIME VERIFIED

**Evidence**: Backend successfully returned ML service response during runtime test.

---

## Stage 11: Frontend Display

### Component

**File**: `apps/web/app/components/ChatInterface.tsx`

### Response Handling

**Code** (estimated):
```typescript
const data = await response.json();
content: data.response
```

### Display

**Behavior**:
1. Parse response from backend
2. Create assistant message object
3. Append to conversation messages array
4. Render in chat interface
5. Auto-scroll to bottom

### Guest Mode

**Storage**: In-memory state (not persisted)

**Conversation**: Map of conversation IDs to message arrays

### Authenticated Mode

**Storage**: Database via conversation manager

**Conversation**: Persisted to PostgreSQL

### Verification Status

**Status**: NOT TESTED

**Reason**: Frontend was not runtime tested due to existing process on port 3000.

---

## Complete Flow Summary

| Stage | Component | Status | Evidence |
|-------|-----------|--------|----------|
| 1. Frontend submission | ChatInterface.tsx | SOURCE-INSPECTED | Source code shows correct implementation |
| 2. Backend API receipt | ai.ts POST /api/v1/ai/chat | RUNTIME VERIFIED | Backend started and received requests |
| 3. Backend-to-ML request | Backend proxies to ML service | RUNTIME VERIFIED | Backend called ML service successfully |
| 4. ML service receipt | main.py POST /orchestrate | RUNTIME VERIFIED | ML service received requests |
| 5. Language detection | detect_language() | SOURCE-INSPECTED | Source code shows Unicode detection |
| 6. Intent classification | Pattern matching | SOURCE-INSPECTED | Source code shows keyword patterns |
| 7. Response routing | Deterministic vs neural | RUNTIME VERIFIED | Runtime test confirmed routing |
| 8. Neural model invocation | TextGenerator.generate() | RUNTIME VERIFIED | Runtime logs show inference success |
| 9. Response validation | Validation rules | SOURCE-INSPECTED | Source code shows validation logic |
| 10. ML service response | OrchestratorResponse | RUNTIME VERIFIED | Runtime test confirmed response format |
| 11. Backend response | Extracts response field | RUNTIME VERIFIED | Backend returned correct response |
| 12. Frontend display | ChatInterface renders | NOT TESTED | Frontend not tested due to port 3000 |

---

## References

- **Frontend**: `apps/web/app/components/ChatInterface.tsx`
- **Backend**: `apps/api/src/routes/ai.ts`
- **ML Service**: `packages/ai-core/ml-service/main.py`
- **Inference**: `packages/ai-core/inference/generator.py`
- **Neural Model**: `packages/ai-core/neural/medium_transformer.py`
