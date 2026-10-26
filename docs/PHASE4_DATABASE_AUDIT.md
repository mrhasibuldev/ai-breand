# PHASE 4 — DATABASE AUDIT REPORT

## STEP 1 — EXISTING SUPABASE ARCHITECTURE AUDIT

### 1.1 Database Configuration
- **Provider**: Supabase (PostgreSQL)
- **Schema**: `nexus` (custom schema, not public)
- **Configuration**: Environment variable `DATABASE_URL`
- **Status**: Currently optional (API can run without it)
- **Access Pattern**: Through `database-core` package with PostgreSQL client

### 1.2 Existing Migrations (12 migrations applied)
1. `001_bootstrap.sql` - Schema, extensions, functions
2. `002_core_identity.sql` - Accounts, auth_sessions
3. `003_user_profiles.sql` - User profiles
4. `004_conversations_messages.sql` - Conversations, messages
5. `005_memory_records.sql` - Memory records
6. `006_consent_records.sql` - Consent records
7. `007_notification_preferences.sql` - Notification preferences
8. `008_library_items.sql` - Library items
9. `010_add_avatar_storage_path.sql` - Avatar storage path
10. `011_create_g_media_table.sql` - G media table
11. `012_g_media_rls_policies.sql` - RLS policies
12. `COMPLETE_SCHEMA.sql` - Complete schema

### 1.3 Existing Tables (in `nexus` schema)
- `accounts` - User accounts
- `auth_sessions` - Authentication sessions
- `user_profiles` - User profile data
- `conversations` - Conversation tracking
- `messages` - Chat messages
- `consent_records` - User consent tracking
- `memory_records` - User memory (name, preferences, etc.)
- `notification_preferences` - Notification settings
- `library_items` - User library (notes, bookmarks)
- `file_metadata` - File storage metadata
- `schema_migrations` - Migration tracking
- `g_media` - Media storage

### 1.4 Existing Extensions
- `pgcrypto` - Cryptographic functions (ENABLED)

### 1.5 pgvector Status
- **NOT YET CHECKED** - Need to verify if pgvector extension is available in Supabase
- **Action Required**: Check pgvector availability before creating embeddings table

### 1.6 Existing Security (RLS)
- Row Level Security (RLS) policies exist
- Separate user data from global data
- Memory records linked to accounts
- Consent tracking for data collection

### 1.7 Database Access Pattern
- TypeScript/Node.js through `database-core` package
- Migration runner in `database-core/migrations/`
- PostgreSQL client for direct queries
- No direct SQL in application code

### 1.8 Knowledge-Related Tables (NONE)
- **NO knowledge tables exist yet**
- Knowledge is currently stored as files only
- Need to create: documents, chunks, embeddings, knowledge_sources

---

## STEP 2 — KNOWLEDGE DATABASE DESIGN

### 2.1 Tables to Create

#### Table: `knowledge_sources`
Tracks where knowledge comes from (websites, books, datasets, etc.)

```sql
CREATE TABLE nexus.knowledge_sources (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type         text NOT NULL, -- 'web', 'book', 'article', 'documentation', 'dataset', 'user_uploaded'
    source_url          text,
    source_name         text,
    license             text,
    copyright_notice    text,
    metadata            jsonb,
    status              text NOT NULL DEFAULT 'active',
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT knowledge_sources_type_ck CHECK (source_type IN ('web', 'book', 'article', 'documentation', 'dataset', 'user_uploaded')),
    CONSTRAINT knowledge_sources_status_ck CHECK (status IN ('active', 'inactive', 'blocked'))
);

CREATE INDEX knowledge_sources_type_idx ON nexus.knowledge_sources(source_type);
CREATE INDEX knowledge_sources_status_idx ON nexus.knowledge_sources(status);
```

#### Table: `documents`
Stores full documents with deduplication by content hash

```sql
CREATE TABLE nexus.documents (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           uuid REFERENCES nexus.knowledge_sources(id) ON DELETE SET NULL,
    content_hash        text NOT NULL, -- SHA-256 of content for deduplication
    title               text,
    content             text NOT NULL,
    language            text NOT NULL, -- 'en', 'bn', 'mixed', 'unknown'
    trust_level         text NOT NULL, -- 'TIER_1', 'TIER_2', 'TIER_3', 'TIER_4'
    quality_score       numeric NOT NULL, -- 0.0 to 1.0
    information_lifetime text NOT NULL, -- 'STATIC', 'SLOW_CHANGING', 'TIME_SENSITIVE'
    word_count          integer,
    char_count          integer,
    author              text,
    publish_date        date,
    status              text NOT NULL DEFAULT 'active',
    version             integer NOT NULL DEFAULT 1,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT documents_content_hash_uk UNIQUE (content_hash),
    CONSTRAINT documents_language_ck CHECK (language IN ('en', 'bn', 'mixed', 'unknown')),
    CONSTRAINT documents_trust_level_ck CHECK (trust_level IN ('TIER_1', 'TIER_2', 'TIER_3', 'TIER_4')),
    CONSTRAINT documents_lifetime_ck CHECK (information_lifetime IN ('STATIC', 'SLOW_CHANGING', 'TIME_SENSITIVE')),
    CONSTRAINT documents_quality_ck CHECK (quality_score >= 0 AND quality_score <= 1),
    CONSTRAINT documents_status_ck CHECK (status IN ('active', 'deleted', 'blocked')),
    CONSTRAINT documents_version_ck CHECK (version >= 1)
);

CREATE UNIQUE INDEX documents_hash_active_uk ON nexus.documents(content_hash) WHERE status = 'active';
CREATE INDEX documents_source_idx ON nexus.documents(source_id);
CREATE INDEX documents_language_idx ON nexus.documents(language);
CREATE INDEX documents_trust_level_idx ON nexus.documents(trust_level);
CREATE INDEX documents_status_idx ON nexus.documents(status);
CREATE INDEX documents_created_at_idx ON nexus.documents(created_at DESC);
```

#### Table: `document_chunks`
Stores document chunks for retrieval

```sql
CREATE TABLE nexus.document_chunks (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         uuid NOT NULL REFERENCES nexus.documents(id) ON DELETE CASCADE,
    chunk_index         integer NOT NULL,
    content             text NOT NULL,
    content_hash        text NOT NULL, -- SHA-256 of chunk content
    token_count         integer,
    char_count          integer,
    section_title       text,
    section_hierarchy   text[], -- Array of section titles
    position_in_document numeric NOT NULL, -- 0.0 to 1.0
    metadata            jsonb,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT document_chunks_document_fk FOREIGN KEY (document_id)
        REFERENCES nexus.documents(id) ON DELETE CASCADE,
    CONSTRAINT document_chunks_chunk_index_ck CHECK (chunk_index >= 0),
    CONSTRAINT document_chunks_position_ck CHECK (position_in_document >= 0 AND position_in_document <= 1)
);

CREATE UNIQUE INDEX document_chunks_doc_hash_uk ON nexus.document_chunks(document_id, content_hash);
CREATE INDEX document_chunks_document_idx ON nexus.document_chunks(document_id);
CREATE INDEX document_chunks_chunk_index_idx ON nexus.document_chunks(document_id, chunk_index);
```

#### Table: `document_metadata`
Extended metadata for documents (kept separate for flexibility)

```sql
CREATE TABLE nexus.document_metadata (
    document_id         uuid PRIMARY KEY REFERENCES nexus.documents(id) ON DELETE CASCADE,
    metadata            jsonb NOT NULL,
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp()
);
```

#### Table: `embeddings` (CONDITIONAL - depends on pgvector)
Stores vector embeddings for semantic search

```sql
-- ONLY CREATE IF pgvector IS AVAILABLE
-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE nexus.embeddings (
    chunk_id            uuid PRIMARY KEY REFERENCES nexus.document_chunks(id) ON DELETE CASCADE,
    embedding           vector(768), -- 768-dimensional embedding
    embedding_model     text NOT NULL DEFAULT 'sentence-transformers/all-MiniLM-L6-v2',
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX embeddings_vector_idx ON nexus.embeddings USING ivfflat (embedding vector_cosine_ops);
```

#### Table: `ingestion_runs`
Tracks knowledge ingestion runs

```sql
CREATE TABLE nexus.ingestion_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_type            text NOT NULL, -- 'file', 'url', 'batch', 'migration'
    source              text,
    documents_inserted  integer NOT NULL DEFAULT 0,
    documents_skipped   integer NOT NULL DEFAULT 0,
    documents_updated   integer NOT NULL DEFAULT 0,
    documents_failed    integer NOT NULL DEFAULT 0,
    chunks_created      integer NOT NULL DEFAULT 0,
    started_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at        timestamptz,
    status              text NOT NULL DEFAULT 'running',
    error_message       text,
    metadata            jsonb,
    CONSTRAINT ingestion_runs_type_ck CHECK (run_type IN ('file', 'url', 'batch', 'migration')),
    CONSTRAINT ingestion_runs_status_ck CHECK (status IN ('running', 'completed', 'failed'))
);

CREATE INDEX ingestion_runs_status_idx ON nexus.ingestion_runs(status);
CREATE INDEX ingestion_runs_started_at_idx ON nexus.ingestion_runs(started_at DESC);
```

#### Table: `knowledge_gaps`
Tracks queries that couldn't be answered

```sql
CREATE TABLE nexus.knowledge_gaps (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    query               text NOT NULL,
    failure_type        text NOT NULL, -- 'KNOWLEDGE_MISSING', 'RETRIEVAL_FAILURE', etc.
    retrieval_results   jsonb,
    confidence          numeric,
    detected_at         timestamptz NOT NULL DEFAULT clock_timestamp(),
    resolved_at         timestamptz,
    resolution_notes    text,
    CONSTRAINT knowledge_gaps_type_ck CHECK (failure_type IN ('KNOWLEDGE_MISSING', 'RETRIEVAL_FAILURE', 'CONTEXT_FAILURE', 'REASONING_FAILURE', 'GENERATION_FAILURE'))
);

CREATE INDEX knowledge_gaps_detected_at_idx ON nexus.knowledge_gaps(detected_at DESC);
CREATE INDEX knowledge_gaps_failure_type_idx ON nexus.knowledge_gaps(failure_type);
CREATE INDEX knowledge_gaps_resolved_at_idx ON nexus.knowledge_gaps(resolved_at) WHERE resolved_at IS NOT NULL;
```

### 2.2 Triggers

```sql
-- Trigger for documents updated_at
DROP TRIGGER IF EXISTS documents_set_updated_at ON nexus.documents;
CREATE TRIGGER documents_set_updated_at
BEFORE UPDATE ON nexus.documents
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- Trigger for document_chunks updated_at
DROP TRIGGER IF EXISTS document_chunks_set_updated_at ON nexus.document_chunks;
CREATE TRIGGER document_chunks_set_updated_at
BEFORE UPDATE ON nexus.document_chunks
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- Trigger for embeddings updated_at (if created)
DROP TRIGGER IF EXISTS embeddings_set_updated_at ON nexus.embeddings;
CREATE TRIGGER embeddings_set_updated_at
BEFORE UPDATE ON nexus.embeddings
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
```

---

## STEP 3 — DEDUPLICATION STRATEGY

### 3.1 Document Deduplication
- Use `content_hash` (SHA-256) as unique constraint
- If document with same hash exists: skip insertion
- Report as "skipped duplicate"

### 3.2 Chunk Deduplication
- Use `(document_id, content_hash)` as unique constraint
- If chunk with same hash exists for same document: skip
- Report as "skipped duplicate"

### 3.3 Ingestion Report
```typescript
{
  documents_inserted: number,
  documents_skipped: number,
  documents_updated: number,
  documents_failed: number,
  chunks_created: number,
  chunks_skipped: number
}
```

---

## STEP 4 — MIGRATION STRATEGY

### 4.1 Migration File
Create `013_knowledge_tables.sql` in `database-core/migrations/`

### 4.2 Import Process
1. Read cleaned documents from `knowledge/cleaned/*.json`
2. Read chunks from `knowledge/cleaned/chunks.jsonl`
3. Insert into Supabase via database-core client
4. Track ingestion run in `ingestion_runs` table
5. Report exact counts

---

## STEP 5 — VECTOR SUPPORT

### 5.1 pgvector Check
- Need to verify if pgvector extension is available in Supabase
- If available: create embeddings table with pgvector
- If not available: create placeholder table without vectors, prepare for future migration

### 5.2 Embedding Interface
Create modular interface:
```typescript
interface EmbeddingService {
  generateEmbedding(text: string): Promise<number[]>;
  generateEmbeddings(texts: string[]): Promise<number[][]>;
  generateQueryEmbedding(query: string): Promise<number[]>;
}
```

---

## STEP 6 — REPOSITORY LAYER

Create TypeScript repository in `packages/database-core/src/`:
- `knowledge-repository.ts` - Document and chunk operations
- `embedding-repository.ts` - Embedding operations (if pgvector available)
- `ingestion-repository.ts` - Ingestion run tracking

---

## STEP 7 — RETRIEVAL PREPARATION

### 7.1 Keyword Search
- Use PostgreSQL full-text search on `documents.content` and `document_chunks.content`
- Create GIN indexes for FTS

### 7.2 Metadata Filtering
- Filter by `trust_level`, `language`, `information_lifetime`
- Add composite indexes

### 7.3 Ranking
- Trust level priority: TIER_1 > TIER_2 > TIER_3 > TIER_4
- Freshness score for TIME_SENSITIVE data

---

## STEP 8 — SECURITY

### 8.1 RLS Policies
- Knowledge tables should be publicly readable (global knowledge)
- User-specific memory tables remain private
- No mixing of public knowledge with private user data

### 8.2 Separation
- `documents`, `document_chunks` - Public knowledge (READ for all)
- `memory_records` - Private user data (authenticated users only)

---

## NEXT STEPS

Now I will:
1. Create migration file `013_knowledge_tables.sql`
2. Check pgvector availability
3. Create repository layer
4. Implement migration of existing 10 documents
5. Test database operations
