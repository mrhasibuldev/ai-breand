# Memory and Retrieval Systems

**Last Updated**: 2026-10-26  
**Verification Status**: SOURCE-INSPECTED

---

## Overview

This document describes the conversation context, memory systems, retrieval mechanisms, and database integration in the NexusAI AI Core.

## Conversation Context

### Current Implementation

**Location**: `packages/ai-core/ml-service/main.py`

**Type**: In-memory session storage

**Data Structure** (line 123):
```python
conversation_contexts: Dict[str, List[Dict]] = {}
```

**Storage Format**:
```python
{
    "conversation_id": [
        {
            "role": "user",
            "content": "message",
            "language": "detected_language",
            "timestamp": unix_timestamp
        },
        {
            "role": "assistant",
            "content": "response",
            "language": "detected_language",
            "timestamp": unix_timestamp
        }
    ]
}
```

### Context Storage Behavior

**Storage** (lines 460-471):
```python
if conversation_id:
    if conversation_id not in conversation_contexts:
        conversation_contexts[conversation_id] = []
    conversation_contexts[conversation_id].append({
        "role": "user",
        "content": message,
        "language": language,
        "timestamp": time.time()
    })
    # Keep only last 10 messages to avoid unbounded growth
    if len(conversation_contexts[conversation_id]) > 10:
        conversation_contexts[conversation_id] = conversation_contexts[conversation_id][-10:]
```

**Assistant Response Storage** (lines 712-720):
```python
if conversation_id:
    if conversation_id in conversation_contexts:
        conversation_contexts[conversation_id].append({
            "role": "assistant",
            "content": response_text,
            "language": language,
            "timestamp": time.time()
        })
```

### Context Limitations

**Limit**: Last 10 messages per conversation

**Persistence**: In-memory only (lost on service restart)

**Scope**: ML service only (not shared with other services)

**Availability**: Only while ML service is running

### Context Usage in Generation

**Current Implementation**: Context is NOT passed to neural model

**Code** (line 636):
```python
augmented_message = f"{SYSTEM_PROMPT}\n\nUser: {message}\nAssistant:"
```

**Issue**: Only current message is included, not conversation history

**Impact**: Model cannot maintain context across turns

### Verification Status

**Status**: SOURCE-INSPECTED

**Evidence**: Source code shows in-memory storage with 10-message limit, but context is not passed to model.

---

## Persistent Memory

### Current Implementation

**Status**: NOT IMPLEMENTED in AI Core

**Database Integration**: NONE in neural model or ML service

**Application-Level Memory**: 
- NexusAI application has database tables for conversations and messages
- Database: PostgreSQL (Neon)
- Schema: `nexus` schema
- Tables: `conversations`, `messages`

### AI Core Memory Status

**Neural Model**: No memory integration (stateless inference)

**ML Service**: In-memory context only (transient)

**Retrieval Systems**: Filesystem-based (not database)

**Verdict**: AI Core does NOT depend on NexusAI database for memory

### Memory Architecture Separation

**Current Separation**:
```
┌─────────────────────────────────────┐
│   NexusAI Application               │
│   - Database (PostgreSQL)          │
│   - Persistent conversations         │
│   - Persistent messages             │
│   - User profiles                   │
└─────────────────────────────────────┘
            │
            │ HTTP API
            ▼
┌─────────────────────────────────────┐
│   AI Core (ML Service)             │
│   - In-memory context (transient)   │
│   - No database dependency          │
│   - No persistent memory            │
└─────────────────────────────────────┘
```

### Future Memory Interface

**Recommended Design**: AI Core should define memory interface for pluggable memory providers

**Architecture**:
```
AI Core
  ├─ Memory Interface (abstract)
  │   ├─ store(conversation_id, message)
  │   ├─ retrieve(conversation_id, limit)
  │   └─ clear(conversation_id)
  │
  └─ Memory Providers (implementations)
      ├─ InMemoryProvider (current)
      ├─ DatabaseProvider (future)
      └─ RedisProvider (future)
```

**Status**: NOT IMPLEMENTED

---

## Retrieval Systems

### System 1: Simple Retrieval

**Location**: `packages/ai-core/knowledge/store/simple_retrieval.py`

**Type**: Keyword-based retrieval

**Purpose**: Quick implementation for immediate functionality

#### Implementation

**Class**: `SimpleRetrievalSystem`

**Data Source**: `knowledge/cleaned/` directory

**Data Format**: JSON files

**Loading** (lines 34-54):
```python
def load(self):
    # Load cleaned documents
    for file_path in self.cleaned_data_dir.glob("clean_*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            doc = json.load(f)
            self.documents.append(doc)
    
    # Load chunks
    chunks_file = self.cleaned_data_dir / "chunks.jsonl"
    if chunks_file.exists():
        with open(chunks_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunk = json.loads(line)
                    self.chunks.append(chunk)
```

**Data Loaded** (from runtime logs):
- Documents: 20
- Chunks: 24

#### Retrieval Method

**Function**: `retrieve()` (lines 56-103)

**Method**: Keyword overlap scoring

**Algorithm**:
1. Convert query to lowercase
2. Extract keywords (remove stop words)
3. Calculate keyword overlap with chunks
4. Score based on overlap percentage
5. Bonus for exact phrase match
6. Return top-k results

**Stop Words**: Common words (is, a, an, the, and, or, but, in, on, at, to, for, of, with, by, from, what, how, why, when, where, who, tell, me, about, explain, define, describe)

**Scoring**:
```python
overlap = len(query_keywords & chunk_words)
score = overlap / len(query_keywords) if query_keywords else 0
if query_lower in chunk_text:
    score += 0.5  # Bonus for exact match
```

#### Runtime Behavior

**Test Query**: "Explain why the sky appears blue"

**Context Length**: 0 (VERIFIED from runtime logs)

**Issue**: Retrieval returned no context for sky question

**Status**: RUNTIME VERIFIED

---

### System 2: RAG (Retrieval-Augmented Generation)

**Location**: `packages/ai-core/data/rag_system.py`

**Type**: Vector-based retrieval with character embeddings

**Purpose**: Advanced retrieval with embeddings

#### Implementation

**Components**:
1. **SimpleEmbedding** — Character-based embedding model
2. **VectorStore** — In-memory vector store
3. **RAGSystem** — Retrieval and prompt augmentation

**Embedding Method** (lines 55-77):
```python
def encode(self, text: str) -> np.ndarray:
    embedding = np.zeros(self.dimension)
    
    for i, char in enumerate(text[:self.dimension]):
        idx = ord(char) % self.dimension
        embedding[idx] += 1.0
    
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding
```

**Method**: Simple character-based encoding (character modulo dimension)

**Dimension**: 768 (configurable)

**Note**: This is a placeholder/demonstration embedding, not a production-quality embedding model

#### Vector Store

**Storage**: In-memory numpy arrays

**Search Method**: Cosine similarity

**Code** (lines 132-165):
```python
def search(self, query_embedding: np.ndarray, top_k: int = 5):
    if len(self.documents) == 0:
        return []
    
    # Compute cosine similarity
    similarities = np.dot(self.embeddings, query_embedding)
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # Filter by threshold
    results = []
    for idx in top_indices:
        score = similarities[idx]
        if score >= threshold:
            results.append((self.documents[idx], float(score)))
    
    return results
```

#### Data Loading

**Expected Location**: `data/processed/`

**Expected Format**: JSON or JSONL with processed documents

**Runtime Status**: RAG system failed to load (VERIFIED from runtime logs)

**Error**: "Processed data directory not found for RAG system"

**Impact**: RAG augmentation unavailable

---

### Retrieval Integration in ML Service

**Location**: `ml-service/main.py` lines 617-690

**Integration Flow**:

1. **Simple Retrieval First** (lines 617-631):
```python
if SIMPLE_RETRIEVAL_AVAILABLE and simple_retrieval is not None:
    try:
        if not simple_retrieval.loaded:
            simple_retrieval.load()
        context = simple_retrieval.get_context(message, top_k=2)
        if context:
            retrieved_context = context
    except Exception as e:
        print(f"[ML Service] Simple retrieval failed: {e}")
```

2. **RAG Augmentation** (lines 638-662):
```python
if rag_loaded and rag_system is not None:
    try:
        augmented_prompt = rag_system.augment_prompt(augmented_message, top_k=3)
        response_text = generator.generate(prompt=augmented_prompt, ...)
        response_source = "RAG_AUGMENTED"
    except Exception as e:
        # Fallback to original prompt
        response_text = generator.generate(prompt=augmented_message, ...)
```

3. **Simple Retrieval Direct** (lines 663-680):
```python
elif retrieved_context:
    results = simple_retrieval.retrieve(message, top_k=1)
    if results:
        response_text = results[0]["text"]
        response_source = "SIMPLE_RETRIEVAL"
    else:
        # Fallback to neural model
        response_text = generator.generate(prompt=augmented_message, ...)
```

4. **Neural Model Only** (lines 681-690):
```python
else:
    response_text = generator.generate(prompt=augmented_message, ...)
```

### Runtime Retrieval Behavior

**Test Query**: "Explain why the sky appears blue"

**Simple Retrieval**: Loaded 20 docs/24 chunks, but context length = 0

**RAG**: Failed to load (no processed data directory)

**Result**: Neural model used without retrieval augmentation

**Status**: RUNTIME VERIFIED

---

## Database Integration

### AI Core Database Dependencies

**Neural Model**: NONE

**ML Service**: NONE

**Retrieval Systems**: NONE (filesystem-based)

**Verdict**: AI Core is fully independent from NexusAI database

### NexusAI Application Database

**Location**: PostgreSQL (Neon)

**Schema**: `nexus`

**Tables**:
- `conversations` — Conversation records
- `messages` — Message records
- `user_profiles` — User profile data
- `memory_records` — Memory records (if implemented)
- `consent_records` — Consent records

**Purpose**: Persistent storage for application-level data

**AI Core Access**: NONE (AI Core does not access this database)

---

## Memory vs Model Knowledge

### Neural Model Knowledge

**Source**: Training data (19 samples from train_cleaned.json)

**Storage**: Model weights (parameters)

**Type**: Implicit knowledge encoded in neural network

**Update Method**: Training/fine-tuning (not currently used)

**Status**: Insufficient training data limits model knowledge

### Conversation Context

**Source**: Current conversation messages

**Storage**: In-memory (ML service) or database (application)

**Type**: Explicit context (message history)

**Update Method**: Append new messages

**Status**: Exists but not passed to model

### Retrieval Knowledge

**Source**: External knowledge base (knowledge/cleaned/)

**Storage**: Filesystem (JSON files)

**Type**: Explicit knowledge (document text)

**Update Method**: Add new documents to knowledge base

**Status**: Simple retrieval works but returns no context for general questions

### Long-term User Memory

**Source**: Application database (not AI Core)

**Storage**: PostgreSQL database

**Type**: Persistent user-specific information

**Update Method**: Database writes via application

**Status**: Not integrated with AI Core

---

## Context Handling Issues

### Issue 1: Context Not Passed to Model

**Problem**: Conversation context is stored but not included in model prompt

**Location**: `main.py` line 636

**Current Code**:
```python
augmented_message = f"{SYSTEM_PROMPT}\n\nUser: {message}\nAssistant:"
```

**Expected Code**:
```python
# Include conversation history
context_text = "\n".join([
    f"{msg['role']}: {msg['content']}" 
    for msg in conversation_contexts.get(conversation_id, [])
])
augmented_message = f"{SYSTEM_PROMPT}\n\n{context_text}\nUser: {message}\nAssistant:"
```

**Impact**: Model cannot maintain context across turns

**Status**: VERIFIED ISSUE

### Issue 2: In-Memory Context Lost on Restart

**Problem**: Conversation context is stored in Python dict, lost when ML service restarts

**Impact**: Conversation history not persistent

**Status**: VERIFIED LIMITATION

### Issue 3: No Database Memory Integration

**Problem**: AI Core does not access application database for memory

**Impact**: Cannot access persistent user memory

**Status**: VERIFIED LIMITATION (by design for independence)

---

## Recommendations

### Memory System

1. **Pass context to model**: Include conversation history in prompt
2. **Define memory interface**: Create abstract memory provider interface
3. **Implement database provider**: Optional database-backed memory
4. **Persistent context**: Use database or Redis for persistent context
5. **Context window**: Implement proper context window management

### Retrieval Systems

1. **Fix simple retrieval**: Investigate why context length is 0
2. **Improve embeddings**: Replace character embeddings with proper sentence embeddings
3. **Add more knowledge**: Expand knowledge base with relevant documents
4. **Vector database**: Consider proper vector database (e.g., Chroma, Pinecone)
5. **Retrieval quality**: Improve retrieval scoring and ranking

### Database Integration

1. **Keep independence**: AI Core should remain database-independent
2. **Optional integration**: Database memory should be optional provider
3. **Clear separation**: Application owns database, AI Core defines interface

---

## References

- **Conversation Context**: `packages/ai-core/ml-service/main.py` lines 123, 460-471, 712-720
- **Simple Retrieval**: `packages/ai-core/knowledge/store/simple_retrieval.py`
- **RAG System**: `packages/ai-core/data/rag_system.py`
- **Database Schema**: `packages/database-core/migrations/`
