# PHASE 2 — NEW AI KNOWLEDGE ARCHITECTURE

## ARCHITECTURAL PRINCIPLE

NexusAI shall have **TWO COMPLEMENTARY SYSTEMS**:

1. **MODEL** — Neural network for language generation, reasoning patterns, conversational behavior
2. **KNOWLEDGE SYSTEM** — Facts, documents, retrieved information, source attribution

The knowledge system must be able to grow **without** retraining the entire model.

---

## LAYER A — RAW DATA STORAGE

### Purpose
Store original collected material separately from processed data. Never overwrite the original source.

### Directory Structure
```
packages/ai-core/knowledge/
├── raw/
│   ├── web/
│   │   ├── crawled_2024-01-15/
│   │   │   ├── page_001.html
│   │   │   └── metadata.json
│   │   └── ...
│   ├── books/
│   │   ├── public_domain/
│   │   │   └── book_001.txt
│   │   └── ...
│   ├── articles/
│   │   ├── wikipedia/
│   │   │   └── article_001.json
│   │   └── ...
│   ├── documentation/
│   │   ├── technical/
│   │   └── user_guides/
│   ├── datasets/
│   │   ├── licensed/
│   │   └── public/
│   ├── conversations/
│   │   ├── anonymized/
│   │   └── approved/
│   └── user_uploaded/
│       └── [user_id]/
│           └── document_001.pdf
```

### Raw Document Schema
```json
{
  "document_id": "raw_20240115_abc123",
  "source": "https://example.com/page",
  "source_type": "web",
  "collected_at": "2024-01-15T10:30:00Z",
  "collected_by": "system|user_upload|api",
  "file_path": "raw/web/crawled_2024-01-15/page_001.html",
  "file_hash": "sha256:abc123...",
  "size_bytes": 45000,
  "language": "en",
  "mime_type": "text/html",
  "license": "CC-BY-SA-4.0",
  "copyright_notice": null,
  "access_restricted": false,
  "metadata": {
    "title": "Example Page",
    "author": "John Doe",
    "publish_date": "2024-01-10"
  }
}
```

### Metadata Tracking
- **Source provenance**: Where did it come from?
- **Collection timestamp**: When was it collected?
- **File integrity**: SHA-256 hash
- **License information**: Copyright and usage rights
- **Access restrictions**: Is it public or private?

---

## LAYER B — DATA CLEANING PIPELINE

### Purpose
Deterministic preprocessing pipeline to transform raw data into clean, standardized format.

### Pipeline Stages

#### Stage 1: Extraction
- Extract text from various formats (HTML, PDF, DOCX, etc.)
- Preserve structure (headings, paragraphs, lists)
- Extract metadata (title, author, date)

#### Stage 2: Normalization
- Normalize encoding (UTF-8)
- Normalize whitespace (collapse multiple spaces)
- Normalize line endings
- Remove control characters

#### Stage 3: Deduplication
- Detect exact duplicates (hash-based)
- Detect near-duplicates (minhash, simhash)
- Keep the highest quality version
- Track duplicates for reference

#### Stage 4: Quality Filtering
- Remove corrupted records
- Remove extremely short documents (< 50 chars)
- Remove spam/advertisement patterns
- Detect low-quality content (excessive repetition, gibberish)

#### Stage 5: Language Detection
- Detect document language
- Classify as: en, bn, mixed, unknown
- Filter unsupported languages if needed

#### Stage 6: Content Validation
- Validate structure (has meaningful content)
- Validate minimum length
- Validate maximum length (truncate if needed)
- Detect and remove boilerplate text

#### Stage 7: Metadata Enrichment
- Assign quality score (0.0 - 1.0)
- Assign trust level (TIER_1 to TIER_4)
- Classify information lifetime (STATIC, SLOW_CHANGING, TIME_SENSITIVE)
- Add processing timestamps

### Cleaned Document Schema
```json
{
  "document_id": "clean_20240115_def456",
  "raw_document_id": "raw_20240115_abc123",
  "text": "The cleaned text content...",
  "language": "en",
  "quality_score": 0.85,
  "trust_level": "TIER_2",
  "information_lifetime": "SLOW_CHANGING",
  "word_count": 450,
  "char_count": 2500,
  "processed_at": "2024-01-15T10:35:00Z",
  "processing_metadata": {
    "extraction_method": "html_parser",
    "deduplication_status": "unique",
    "quality_flags": [],
    "processing_time_ms": 125
  },
  "source": {
    "url": "https://example.com/page",
    "source_type": "web",
    "license": "CC-BY-SA-4.0",
    "author": "John Doe",
    "publish_date": "2024-01-10"
  }
}
```

### Directory Structure
```
packages/ai-core/knowledge/
├── cleaned/
│   ├── web/
│   │   └── cleaned_20240115.jsonl
│   ├── books/
│   │   └── cleaned_20240115.jsonl
│   └── ...
└── cleaning_logs/
    └── 20240115_cleaning.log
```

---

## LAYER C — KNOWLEDGE INGESTION PIPELINE

### Purpose
Reusable pipeline to ingest knowledge from multiple sources.

### Pipeline Flow
```
SOURCE
  ↓
FETCH
  ↓
PARSE
  ↓
CLEAN (Layer B)
  ↓
DEDUPLICATE
  ↓
QUALITY CHECK
  ↓
CHUNK
  ↓
INDEX
  ↓
STORE
```

### Supported Sources

#### 1. Public Documentation
- API documentation
- Technical manuals
- User guides
- Requirements: Permissive license (MIT, Apache, CC-BY)

#### 2. Educational Datasets
- Wikipedia dumps
- Open educational resources
- Public domain textbooks
- Requirements: Public domain or CC license

#### 3. Public-Domain Books
- Project Gutenberg
- Open Library
- Requirements: Verified public domain

#### 4. Structured Datasets
- CSV/JSON datasets
- Knowledge graphs
- Requirements: Clear license, attribution

#### 5. Licensed Datasets
- Commercial datasets with license
- Requirements: Valid license, usage compliance

#### 6. User-Provided Documents
- Uploaded by users
- Requirements: User consent, privacy checked

#### 7. Approved Web Sources
- Whitelisted domains
- RSS feeds
- Requirements: robots.txt respected, ToS compliant

#### 8. Internal Knowledge Files
- Company documentation
- Internal wikis
- Requirements: Access control, classification

### Chunking Strategy

#### Semantic Chunking
- Split by paragraphs
- Preserve section boundaries
- Chunk size: 200-500 tokens
- Overlap: 50 tokens

#### Metadata per Chunk
```json
{
  "chunk_id": "chunk_20240115_ghi789",
  "document_id": "clean_20240115_def456",
  "chunk_index": 3,
  "text": "The chunk text content...",
  "token_count": 350,
  "section_title": "Introduction",
  "section_hierarchy": ["Chapter 1", "Introduction"],
  "position_in_document": 0.25,
  "preceding_chunk_id": "chunk_20240115_ghi788",
  "following_chunk_id": "chunk_20240115_ghi790"
}
```

### Ingestion API
```python
class KnowledgeIngestionPipeline:
    async def ingest_from_url(self, url: str, source_config: dict) -> IngestionResult
    async def ingest_from_file(self, file_path: str, metadata: dict) -> IngestionResult
    async def ingest_from_directory(self, dir_path: str, config: dict) -> IngestionResult
    async def ingest_from_dataset(self, dataset_path: str, config: dict) -> IngestionResult
```

---

## LAYER D — KNOWLEDGE STORE

### Purpose
Proper knowledge store separate from model weights. AI should NOT need to retrain to add new information.

### Components

#### 1. Document Store
- Store full documents
- Index by document_id
- Support retrieval by metadata
- Store in database (PostgreSQL/Supabase)

**Schema:**
```sql
CREATE TABLE documents (
  document_id TEXT PRIMARY KEY,
  raw_document_id TEXT,
  text TEXT NOT NULL,
  language TEXT,
  quality_score FLOAT,
  trust_level TEXT,
  information_lifetime TEXT,
  word_count INT,
  char_count INT,
  processed_at TIMESTAMP,
  source_url TEXT,
  source_type TEXT,
  license TEXT,
  author TEXT,
  publish_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. Chunk Store
- Store document chunks
- Link to parent document
- Support chunk retrieval

**Schema:**
```sql
CREATE TABLE chunks (
  chunk_id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,
  chunk_index INT,
  text TEXT NOT NULL,
  token_count INT,
  section_title TEXT,
  section_hierarchy JSONB,
  position_in_document FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (document_id) REFERENCES documents(document_id)
);
```

#### 3. Metadata Store
- Store document metadata
- Support filtering and search
- Track provenance

**Schema:**
```sql
CREATE TABLE document_metadata (
  document_id TEXT PRIMARY KEY,
  metadata JSONB NOT NULL,
  FOREIGN KEY (document_id) REFERENCES documents(document_id)
);
```

#### 4. Embedding Index
- Store vector embeddings
- Support similarity search
- Use pgvector or external vector DB

**Schema (with pgvector):**
```sql
CREATE TABLE chunk_embeddings (
  chunk_id TEXT PRIMARY KEY,
  embedding vector(768),
  embedding_model TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id)
);

CREATE INDEX ON chunk_embeddings USING ivfflat (embedding vector_cosine_ops);
```

#### 5. Retrieval Layer
- Query processing
- Similarity search
- Metadata filtering
- Result ranking

### Directory Structure
```
packages/ai-core/knowledge/
├── store/
│   ├── document_store.py
│   ├── chunk_store.py
│   ├── metadata_store.py
│   ├── embedding_store.py
│   └── retrieval_engine.py
└── indices/
    └── chunk_embeddings/
```

---

## LAYER E — RETRIEVAL SYSTEM

### Purpose
Retrieve relevant knowledge for user queries.

### Retrieval Interface
```python
class RetrievalEngine:
    async def retrieve_knowledge(
        self,
        query: str,
        options: RetrievalOptions
    ) -> List[RetrievalResult]

class RetrievalOptions:
    top_k: int = 5
    min_score: float = 0.5
    trust_levels: List[str] = ["TIER_1", "TIER_2", "TIER_3"]
    languages: List[str] = ["en", "bn"]
    information_lifetime: List[str] = ["STATIC", "SLOW_CHANGING"]
    metadata_filters: Dict[str, Any] = {}
    use_hybrid_search: bool = True

class RetrievalResult:
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any]
    source: Dict[str, Any]
```

### Retrieval Strategies

#### 1. Semantic Search
- Use embedding similarity
- Cosine similarity
- Top-k retrieval

#### 2. Keyword Search
- Full-text search (PostgreSQL FTS)
- BM25 ranking
- Phrase matching

#### 3. Hybrid Search
- Combine semantic + keyword
- Reciprocal rank fusion (RRF)
- Boost factors

#### 4. Metadata Filtering
- Filter by trust level
- Filter by language
- Filter by information lifetime
- Custom metadata filters

### Retrieval Flow
```
USER QUERY
  ↓
QUERY ANALYSIS
  ↓
GENERATE QUERY EMBEDDING
  ↓
SEMANTIC SEARCH (vector similarity)
  ↓
KEYWORD SEARCH (full-text)
  ↓
HYBRID RANKING (RRF)
  ↓
METADATA FILTERING
  ↓
DUPLICATE SUPPRESSION
  ↓
TOP-K SELECTION
  ↓
RETURN RESULTS
```

### Confidence Scoring
- **High confidence**: score > 0.8, TIER_1 or TIER_2
- **Medium confidence**: score 0.5-0.8, TIER_3
- **Low confidence**: score < 0.5 or TIER_4

### Insufficiency Detection
- If no results found
- If all scores below threshold
- If filtered out by metadata
- → Return KNOWLEDGE_MISSING signal

---

## LAYER F — KNOWLEDGE VALIDATION

### Purpose
Validate knowledge before it enters the trusted knowledge base.

### Validation Pipeline
```
SOURCE
  ↓
CLEAN
  ↓
QUALITY SCORE
  ↓
CONSISTENCY CHECK
  ↓
DUPLICATE CHECK
  ↓
TRUST LEVEL
  ↓
STORE
```

### Source Trust Levels

#### TIER_1: Highly Authoritative
- Peer-reviewed academic papers
- Official documentation
- Government publications
- Standards organizations
- Example: IEEE papers, W3C specs

#### TIER_2: Reliable Secondary Sources
- Reputable news outlets
- Established encyclopedias
- Technical blogs from experts
- Verified educational resources
- Example: Wikipedia, arXiv, MDN

#### TIER_3: General Public Sources
- User-generated content
- Blogs (unverified)
- Forums (Q&A sites)
- Social media (with caution)
- Example: Stack Overflow, Medium

#### TIER_4: Unverified Material
- User uploads (unverified)
- Crowdsourced data
- Automatically collected
- Example: Reddit, scraped content

### Quality Scoring

#### Factors
- **Content quality**: Grammar, structure, completeness (0-0.3)
- **Source authority**: Domain reputation, author credentials (0-0.3)
- **Freshness**: Recency, update frequency (0-0.2)
- **Citations**: References to other sources (0-0.2)

#### Score Calculation
```python
quality_score = (
    content_quality * 0.3 +
    source_authority * 0.3 +
    freshness * 0.2 +
    citations * 0.2
)
```

### Consistency Checking
- Detect contradictions with existing knowledge
- Flag for manual review
- Version tracking for updates

### Duplicate Detection
- Exact duplicates (hash match)
- Near duplicates (minhash similarity > 0.9)
- Keep highest quality version
- Link duplicates for reference

---

## LAYER G — CONVERSATIONAL MEMORY

### Purpose
Memory separate from general knowledge. Multi-layer memory system.

### Memory Layers

#### 1. Short-Term Memory
- Current conversation context
- Last N messages (configurable, default 10)
- Temporary, session-based
- No persistence

**Schema:**
```typescript
interface ShortTermMemory {
  conversation_id: string;
  messages: ConversationMessage[];
  max_history: number;
}

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}
```

#### 2. Episodic Memory
- Important events from previous conversations
- User preferences explicitly stated
- Significant interactions
- Persistent, with retention policy

**Schema:**
```typescript
interface EpisodicMemory {
  episode_id: string;
  user_id: string;
  conversation_id: string;
  event_type: 'preference' | 'fact' | 'correction' | 'milestone';
  content: string;
  importance: 'low' | 'medium' | 'high';
  timestamp: Date;
  expires_at?: Date;
  consented: boolean;
}

interface EpisodicMemoryStore {
  async store(episode: EpisodicMemory): Promise<void>;
  async retrieve(user_id: string, limit: number): Promise<EpisodicMemory[]>;
  async retrieve_by_type(user_id: string, event_type: string): Promise<EpisodicMemory[]>;
  async delete(episode_id: string): Promise<void>;
  async expire_old(): Promise<void>;
}
```

#### 3. User Memory
- Stable user preferences/facts
- Explicitly shared by user
- System is allowed to retain
- Persistent, revocable

**Schema:**
```typescript
interface UserMemory {
  memory_id: string;
  user_id: string;
  fact_type: 'name' | 'location' | 'preference' | 'custom';
  fact_key: string;
  fact_value: string;
  confidence: float;
  source: 'explicit' | 'inferred' | 'derived';
  consented: boolean;
  created_at: Date;
  updated_at: Date;
  expires_at?: Date;
}

interface UserMemoryStore {
  async store(memory: UserMemory): Promise<void>;
  async retrieve(user_id: string, fact_type?: string): Promise<UserMemory[]>;
  async update(memory_id: string, updates: Partial<UserMemory>): Promise<void>;
  async delete(memory_id: string): Promise<void>;
  async revoke_consent(user_id: string): Promise<void>;
}
```

#### 4. Semantic Knowledge
- General world knowledge
- Retrieved from knowledge store
- Not user-specific
- Shared across all users

**Schema:**
```typescript
interface SemanticKnowledge {
  knowledge_id: string;
  fact: string;
  category: string;
  trust_level: 'TIER_1' | 'TIER_2' | 'TIER_3' | 'TIER_4';
  information_lifetime: 'STATIC' | 'SLOW_CHANGING' | 'TIME_SENSITIVE';
  source: string;
  created_at: Date;
  updated_at: Date;
}
```

### Memory Architecture
```
┌─────────────────────────────────────────┐
│         MEMORY COORDINATOR              │
└─────────────────────────────────────────┘
            │
    ┌───────┴───────┬──────────┬──────────┐
    ↓               ↓          ↓          ↓
┌─────────┐  ┌──────────┐ ┌─────────┐ ┌─────────┐
│ SHORT-  │  │ EPISODIC │ │  USER   │ │ SEMANTIC│
│  TERM   │  │  MEMORY  │ │ MEMORY  │ │KNOWLEDGE│
└─────────┘  └──────────┘ └─────────┘ └─────────┘
    │              │           │          │
 In-memory    PostgreSQL  PostgreSQL  Knowledge
 (session)      (persistent) (persistent)   Store
```

### Memory API
```python
class MemoryCoordinator:
    async def store_short_term(self, conversation_id: str, message: ConversationMessage)
    async def retrieve_short_term(self, conversation_id: str) -> List[ConversationMessage]
    async def store_episodic(self, episode: EpisodicMemory)
    async def retrieve_episodic(self, user_id: str, event_type?: str) -> List[EpisodicMemory]
    async def store_user_memory(self, memory: UserMemory)
    async def retrieve_user_memory(self, user_id: str, fact_type?: str) -> List[UserMemory]
    async def retrieve_semantic(self, query: str) -> List[SemanticKnowledge]
    async def resolve_reference(self, reference: str, context: ConversationContext) -> Any
```

---

## LAYER H — CONVERSATION ENGINE

### Purpose
Human-like conversation handling with reference resolution and context awareness.

### Response Pipeline
```
USER MESSAGE
  ↓
INTENT CLASSIFICATION
  ↓
REFERENCE RESOLUTION
  ↓
CONTEXT LOADING
    ├─ Short-term memory
    ├─ Episodic memory
    ├─ User memory
    └─ Semantic knowledge
  ↓
KNOWLEDGE RETRIEVAL
  ↓
CONFIDENCE ASSESSMENT
  ↓
RESPONSE GENERATION
  ↓
SAFETY CHECK
  ↓
STYLE ADJUSTMENT
  ↓
RESPONSE DELIVERY
  ↓
MEMORY UPDATE
  ↓
FEEDBACK COLLECTION
```

### Reference Resolution

#### Types of References
1. **Anaphoric**: "What did I ask earlier?"
2. **Elliptical**: "What about the second option?"
3. **Deictic**: "Explain that more simply"
4. **Temporal**: "Remember what I told you yesterday"

#### Resolution Strategy
- Maintain conversation state
- Track entity mentions
- Resolve using context history
- Fall back to asking for clarification

### Confidence Assessment

#### Confidence Levels
- **HIGH**: Knowledge retrieved, high similarity, trusted source
- **MEDIUM**: Knowledge retrieved, medium similarity, medium trust
- **LOW**: No knowledge retrieved, low trust, or ambiguous
- **UNKNOWN**: Complete lack of information

#### Response Strategy
- **HIGH**: Provide direct answer with citation
- **MEDIUM**: Provide answer with uncertainty disclaimer
- **LOW**: Admit lack of knowledge, suggest alternatives
- **UNKNOWN**: "I don't have information about that"

### Response Style
- **Concise**: For simple questions
- **Detailed**: For complex topics
- **Conversational**: For casual interaction
- **Formal**: For technical queries
- **Educational**: For learning scenarios

---

## LAYER I — TRAINING DATA PIPELINE

### Purpose
Generate training datasets from collected data. Collected data should NOT automatically become training data.

### Pipeline Flow
```
RAW DATA
  ↓
CLEAN (Layer B)
  ↓
FILTER
  ↓
DEDUPLICATE
  ↓
QUALITY SCORE
  ↓
FORMAT
  ↓
TRAIN/VALIDATION SPLIT
  ↓
DATASET VERSION
  ↓
TRAINING
```

### Dataset Versions

#### Versioning Scheme
- `dataset_v001`: Initial version
- `dataset_v002`: Added new sources
- `dataset_v003`: Improved cleaning
- Each version is immutable

#### Version Metadata
```json
{
  "dataset_version": "dataset_v003",
  "created_at": "2024-01-15T10:00:00Z",
  "sources": [
    {"source": "wikipedia", "count": 10000},
    {"source": "books", "count": 500},
    {"source": "documentation", "count": 2000}
  ],
  "total_examples": 12500,
  "training_examples": 10000,
  "validation_examples": 2500,
  "cleaning_pipeline_version": "v2.1",
  "quality_threshold": 0.7,
  "trust_levels": ["TIER_1", "TIER_2"],
  "languages": ["en", "bn"],
  "hash": "sha256:xyz789..."
}
```

### Training Metadata Tracking

Every training run must record:
- Dataset version
- Number of examples
- Training configuration
- Validation configuration
- Model version
- Training loss
- Validation loss
- Evaluation results
- Timestamp

**Schema:**
```sql
CREATE TABLE training_runs (
  run_id TEXT PRIMARY KEY,
  dataset_version TEXT NOT NULL,
  model_version TEXT NOT NULL,
  training_config JSONB,
  validation_config JSONB,
  training_loss_start FLOAT,
  training_loss_end FLOAT,
  validation_loss FLOAT,
  evaluation_results JSONB,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  status TEXT
);
```

---

## LAYER J — TRAINING STRATEGY

### Purpose
Reproducible training with candidate evaluation and promotion.

### Training Process
```
SELECT DATASET VERSION
  ↓
CONFIGURE TRAINING
  ↓
TRAIN CANDIDATE MODEL
  ↓
EVALUATE CANDIDATE
  ↓
COMPARE WITH CURRENT
  ↓
PROMOTE IF BETTER
  ↓
ELSE DISCARD
```

### Reproducibility
- Fixed random seeds
- Deterministic data loading
- Versioned dependencies
- Recorded hyperparameters
- Checkpoint at each epoch

### Checkpointing
- Save model state every N epochs
- Save optimizer state
- Save training configuration
- Save validation metrics
- Allow resume from checkpoint

### Validation
- Separate validation set
- Compute validation loss each epoch
- Early stopping if no improvement
- Save best model separately

### Candidate Evaluation
- Evaluate on benchmark suite
- Compare with current model
- Metric: accuracy, retrieval, memory, conversation
- Threshold: Must improve by > 5%

### Promotion/Rejection
- **Promote**: If better than current by threshold
- **Reject**: If worse or equal
- **Rollback**: If promoted model fails in production

### Model Versioning
- `model_v001`: Initial model
- `model_v002`: Trained on dataset_v002
- `model_v003`: Fine-tuned on specific task
- Each version is immutable

---

## LAYER K — CONTINUOUS LEARNING LOOP

### Purpose
Controlled learning loop. NOT uncontrolled recursive self-training.

### Loop Flow
```
COLLECT
  ↓
CLEAN
  ↓
VALIDATE
  ↓
STORE
  ↓
INDEX
  ↓
EVALUATE
  ↓
GENERATE TRAINING DATA
  ↓
TRAIN CANDIDATE MODEL
  ↓
EVALUATE
  ↓
PROMOTE ONLY IF BETTER
```

### Control Mechanisms

#### Data Quality Control
- Minimum quality threshold (0.7)
- Maximum synthetic data ratio (20%)
- Human review for ambiguous data
- Reject low-confidence data

#### Training Frequency Control
- Minimum time between training runs (7 days)
- Minimum new data threshold (1000 examples)
- Manual approval for training
- Monitoring for degradation

#### Evaluation Control
- Must pass automated benchmark
- Must have human review
- Must have A/B testing if deployed
- Rollback mechanism

### Anti-Recursion Safeguards
- Track synthetic data generation
- Limit synthetic data ratio
- Detect circular dependencies
- Prevent model training on its own outputs indefinitely

---

## LAYER L — USER FEEDBACK LOOP

### Purpose
Collect feedback signals to identify improvement areas.

### Feedback Types

#### 1. Retrieval Success
- Did retrieval find relevant information?
- Binary: yes/no

#### 2. User Feedback
- Explicit rating (1-5 stars)
- Thumbs up/down
- "Helpful" / "Not helpful"

#### 3. Answer Quality
- Correctness (user correction)
- Completeness
- Clarity

#### 4. Correction
- User provides correct answer
- System learns from correction

#### 5. Failure Type
- Knowledge missing
- Retrieval failure
- Context failure
- Reasoning failure
- Generation failure
- Safety block
- Unknown

### Feedback Schema
```sql
CREATE TABLE feedback (
  feedback_id TEXT PRIMARY KEY,
  conversation_id TEXT,
  message_id TEXT,
  user_id TEXT,
  feedback_type TEXT,
  rating INT,
  text_feedback TEXT,
  failure_type TEXT,
  confidence_score FLOAT,
  retrieval_success BOOLEAN,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

### Feedback Analysis
- Aggregate feedback by failure type
- Identify knowledge gaps
- Prioritize data acquisition
- Improve retrieval system
- Adjust model training

---

## LAYER M — EVALUATION SYSTEM

### Purpose
Automated evaluation suite with benchmark dataset.

### Benchmark Categories

#### 1. General Knowledge
- Factual questions
- Concept explanations
- Definitions

#### 2. Reasoning
- Mathematical problems
- Logical deductions
- Multi-step reasoning

#### 3. Language
- Translation
- Summarization
- Grammar correction

#### 4. Conversation
- Reference resolution
- Context retention
- Coherence

#### 5. Factual Retrieval
- Knowledge base queries
- Source attribution
- Accuracy

#### 6. Memory
- User fact recall
- Preference retention
- Episode memory

#### 7. Instruction Following
- Task completion
- Format compliance
- Constraint satisfaction

### Benchmark Dataset
```json
{
  "benchmark_id": "benchmark_v001",
  "created_at": "2024-01-15T10:00:00Z",
  "questions": [
    {
      "question_id": "q001",
      "category": "general_knowledge",
      "question": "What is the capital of France?",
      "expected_answer": "Paris",
      "answer_type": "exact",
      "difficulty": "easy"
    },
    {
      "question_id": "q002",
      "category": "reasoning",
      "question": "If A > B and B > C, what can you say about A and C?",
      "expected_answer": "A > C",
      "answer_type": "exact",
      "difficulty": "medium"
    }
  ]
}
```

### Evaluation Report
```json
{
  "evaluation_id": "eval_20240115_abc123",
  "model_version": "model_v003",
  "dataset_version": "dataset_v003",
  "benchmark_id": "benchmark_v001",
  "timestamp": "2024-01-15T12:00:00Z",
  "results": {
    "total_questions": 100,
    "passed": 85,
    "failed": 15,
    "accuracy": 0.85,
    "by_category": {
      "general_knowledge": {"passed": 20, "total": 25, "accuracy": 0.8},
      "reasoning": {"passed": 15, "total": 20, "accuracy": 0.75},
      "language": {"passed": 18, "total": 20, "accuracy": 0.9},
      "conversation": {"passed": 17, "total": 20, "accuracy": 0.85},
      "factual_retrieval": {"passed": 10, "total": 10, "accuracy": 1.0},
      "memory": {"passed": 5, "total": 5, "accuracy": 1.0}
    },
    "retrieval_accuracy": 0.92,
    "memory_accuracy": 1.0,
    "conversation_score": 0.85
  }
}
```

### Regression Testing
- Compare with previous model version
- Detect performance degradation
- Fail if regression > 5%
- Require investigation before promotion

---

## LAYER N — KNOWLEDGE GAP DETECTION

### Purpose
Detect when AI cannot answer and prioritize knowledge acquisition.

### Gap Detection
```json
{
  "gap_id": "gap_20240115_xyz789",
  "query": "What is the Bangladesh tax system?",
  "failure_type": "KNOWLEDGE_MISSING",
  "timestamp": "2024-01-15T14:30:00Z",
  "retrieval_results": [],
  "confidence": 0.0,
  "user_id": "user_123",
  "conversation_id": "conv_456"
}
```

### Gap Analysis
- Aggregate gaps by topic
- Identify high-frequency gaps
- Prioritize by user impact
- Suggest data sources

### Gap Resolution
- Search approved sources
- Ingest relevant documents
- Validate quality
- Add to knowledge store
- Mark gap as resolved

---

## LAYER O — KNOWLEDGE FRESHNESS

### Purpose
Classify information by lifetime and handle time-sensitive data appropriately.

### Information Lifetime Classes

#### STATIC
- Mathematical definitions
- Scientific constants
- Historical facts (past events)
- Lifetime: Permanent

#### SLOW_CHANGING
- Government policies (rarely change)
- Scientific theories (evolve slowly)
- Geographic information (rarely changes)
- Lifetime: Years

#### TIME_SENSITIVE
- Current events
- Stock prices
- Weather
- News
- Lifetime: Hours to days

### Handling Strategy
- **STATIC**: Bake into model weights (fine-tuning)
- **SLOW_CHANGING**: Store in knowledge store, refresh periodically
- **TIME_SENSITIVE**: Retrieve from current sources, do not store

### Freshness Tracking
```json
{
  "document_id": "doc_20240115_abc123",
  "information_lifetime": "TIME_SENSITIVE",
  "publish_date": "2024-01-15T10:00:00Z",
  "last_verified": "2024-01-15T10:00:00Z",
  "expires_at": "2024-01-16T10:00:00Z",
  "refresh_source": "https://example.com/feed"
}
```

### Auto-Refresh
- Monitor sources for updates
- Re-ingest when changes detected
- Update knowledge store
- Invalidate old versions

---

## LAYER P — DATA SAFETY

### Purpose
Protect sensitive data and respect privacy.

### Data to NOT Collect/Store
- Passwords
- Authentication tokens
- Private credentials
- Unnecessary personal information
- Private conversations without authorization
- Sensitive personal information without legitimate reason

### Data Retention Rules
- **Short-term memory**: Session only (expires on logout)
- **Episodic memory**: Configurable (default 1 year)
- **User memory**: Until consent revoked
- **Semantic knowledge**: Permanent (public knowledge)

### Deletion Mechanisms
- Delete by document_id
- Delete by user_id (user data)
- Delete by date range
- Bulk delete for GDPR requests

### Consent Tracking
```json
{
  "consent_id": "consent_20240115_abc123",
  "user_id": "user_123",
  "consent_type": "memory_retention",
  "consented": true,
  "timestamp": "2024-01-15T10:00:00Z",
  "revoked_at": null
}
```

### Privacy Controls
- Anonymize user data before training
- Hash user IDs for identification
- Separate user data from training data
- Allow users to view/delete their data

---

## LAYER Q — INTERNAL API DESIGN

### Purpose
Clean, modular interfaces for all components.

### Core APIs

#### Knowledge Ingestion
```python
class KnowledgeIngestionAPI:
    async def ingest_document(self, document: RawDocument) -> CleanedDocument
    async def ingest_batch(self, documents: List[RawDocument]) -> List[CleanedDocument]
    async def get_ingestion_status(self, job_id: str) -> IngestionStatus
```

#### Knowledge Store
```python
class KnowledgeStoreAPI:
    async def store_document(self, document: CleanedDocument) -> str
    async def retrieve_document(self, document_id: str) -> CleanedDocument
    async def store_chunk(self, chunk: Chunk) -> str
    async def retrieve_chunk(self, chunk_id: str) -> Chunk
    async def delete_document(self, document_id: str) -> None
```

#### Retrieval
```python
class RetrievalAPI:
    async def retrieve_knowledge(self, query: str, options: RetrievalOptions) -> List[RetrievalResult]
    async def hybrid_search(self, query: str, options: RetrievalOptions) -> List[RetrievalResult]
    async def semantic_search(self, query: str, options: RetrievalOptions) -> List[RetrievalResult]
    async def keyword_search(self, query: str, options: RetrievalOptions) -> List[RetrievalResult]
```

#### Memory
```python
class MemoryAPI:
    async def store_memory(self, memory: Union[EpisodicMemory, UserMemory]) -> str
    async def retrieve_memory(self, user_id: str, memory_type: str) -> List[Memory]
    async def update_memory(self, memory_id: str, updates: dict) -> None
    async def delete_memory(self, memory_id: str) -> None
    async def revoke_consent(self, user_id: str) -> None
```

#### Training
```python
class TrainingAPI:
    async def create_training_dataset(self, config: DatasetConfig) -> str
    async def train_model(self, config: TrainingConfig) -> str
    async def evaluate_model(self, model_version: str) -> EvaluationResult
    async def promote_model(self, candidate_version: str) -> PromotionResult
    async def rollback_model(self, to_version: str) -> RollbackResult
```

#### Evaluation
```python
class EvaluationAPI:
    async def run_benchmark(self, model_version: str) -> EvaluationReport
    async def compare_models(self, version_a: str, version_b: str) -> ComparisonResult
    async def get_evaluation_history(self, model_version: str) -> List[EvaluationReport]
```

#### Feedback
```python
class FeedbackAPI:
    async def record_feedback(self, feedback: Feedback) -> str
    async def analyze_feedback(self, time_range: DateRange) -> FeedbackAnalysis
    async def get_gaps(self, priority: str) -> List[KnowledgeGap]
```

### Module Independence
- Each module has its own API
- No direct dependencies between modules
- Communication through well-defined interfaces
- Easy to swap implementations

---

## LAYER R — OBSERVABILITY

### Purpose
Structured logging and health checks for all components.

### Structured Logging

#### Log Format
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "level": "INFO",
  "operation": "ingest_document",
  "duration_ms": 125,
  "success": true,
  "record_count": 1,
  "model_version": "model_v003",
  "dataset_version": "dataset_v003",
  "error_category": null,
  "metadata": {
    "document_id": "doc_20240115_abc123",
    "source": "https://example.com"
  }
}
```

#### Important Operations to Log
- Document ingestion
- Knowledge retrieval
- Model inference
- Training runs
- Evaluation runs
- Memory operations
- Feedback recording
- Error occurrences

### Health Checks

#### Components to Monitor
- API health
- Model health
- Database health
- Knowledge store health
- Retrieval system health
- Training pipeline health
- Memory system health

#### Health Check Endpoints
```python
GET /health
GET /health/api
GET /health/model
GET /health/database
GET /health/knowledge_store
GET /health/retrieval
GET /health/training
GET /health/memory
```

#### Health Check Response
```json
{
  "status": "healthy",
  "components": {
    "api": {"status": "healthy", "latency_ms": 5},
    "model": {"status": "healthy", "version": "model_v003"},
    "database": {"status": "healthy", "connection_pool": "5/20"},
    "knowledge_store": {"status": "healthy", "document_count": 12500},
    "retrieval": {"status": "healthy", "avg_latency_ms": 50},
    "training": {"status": "idle", "last_run": "2024-01-14"},
    "memory": {"status": "healthy", "active_users": 42}
  }
}
```

### Metrics
- Document ingestion rate
- Retrieval latency
- Retrieval success rate
- Model inference latency
- Training loss over time
- Evaluation accuracy over time
- User feedback scores
- Knowledge gap frequency

---

## SUMMARY

This architecture provides:

1. **Separation of Concerns**: Model vs. Knowledge
2. **Modularity**: Independent, swappable components
3. **Scalability**: Can grow without retraining
4. **Safety**: Data protection, consent tracking
5. **Observability**: Logging, health checks, metrics
6. **Quality Control**: Validation, evaluation, feedback
7. **Reproducibility**: Versioning, metadata tracking
8. **Continuous Improvement**: Learning loop, gap detection

The AI will be able to:
- Answer factual questions using retrieved knowledge
- Remember user preferences across sessions
- Learn from feedback
- Improve over time
- Maintain safety and privacy
- Scale knowledge without model retraining

---

## NEXT PHASE

**Phase 3:** Build Knowledge Ingestion Pipeline
- Implement raw data storage
- Implement data cleaning pipeline
- Implement chunking strategy
- Implement quality scoring
- Test with small dataset (10 documents)
