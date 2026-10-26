-- Migration 013: Knowledge Tables
-- Creates tables for persistent knowledge storage
-- Separate from user data (accounts, memory, etc.)

-- ============================================
-- KNOWLEDGE SOURCES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.knowledge_sources (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type         text NOT NULL,
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

CREATE INDEX IF NOT EXISTS knowledge_sources_type_idx ON nexus.knowledge_sources(source_type);
CREATE INDEX IF NOT EXISTS knowledge_sources_status_idx ON nexus.knowledge_sources(status);

-- ============================================
-- DOCUMENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.documents (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           uuid REFERENCES nexus.knowledge_sources(id) ON DELETE SET NULL,
    content_hash        text NOT NULL,
    title               text,
    content             text NOT NULL,
    language            text NOT NULL,
    trust_level         text NOT NULL,
    quality_score       numeric NOT NULL,
    information_lifetime text NOT NULL,
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

CREATE UNIQUE INDEX IF NOT EXISTS documents_hash_active_uk ON nexus.documents(content_hash) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS documents_source_idx ON nexus.documents(source_id);
CREATE INDEX IF NOT EXISTS documents_language_idx ON nexus.documents(language);
CREATE INDEX IF NOT EXISTS documents_trust_level_idx ON nexus.documents(trust_level);
CREATE INDEX IF NOT EXISTS documents_status_idx ON nexus.documents(status);
CREATE INDEX IF NOT EXISTS documents_created_at_idx ON nexus.documents(created_at DESC);

-- Trigger for documents updated_at
DROP TRIGGER IF EXISTS documents_set_updated_at ON nexus.documents;
CREATE TRIGGER documents_set_updated_at
BEFORE UPDATE ON nexus.documents
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- DOCUMENT CHUNKS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.document_chunks (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         uuid NOT NULL REFERENCES nexus.documents(id) ON DELETE CASCADE,
    chunk_index         integer NOT NULL,
    content             text NOT NULL,
    content_hash        text NOT NULL,
    token_count         integer,
    char_count          integer,
    section_title       text,
    section_hierarchy   text[],
    position_in_document numeric NOT NULL,
    metadata            jsonb,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT document_chunks_document_fk FOREIGN KEY (document_id)
        REFERENCES nexus.documents(id) ON DELETE CASCADE,
    CONSTRAINT document_chunks_chunk_index_ck CHECK (chunk_index >= 0),
    CONSTRAINT document_chunks_position_ck CHECK (position_in_document >= 0 AND position_in_document <= 1)
);

CREATE UNIQUE INDEX IF NOT EXISTS document_chunks_doc_hash_uk ON nexus.document_chunks(document_id, content_hash);
CREATE INDEX IF NOT EXISTS document_chunks_document_idx ON nexus.document_chunks(document_id);
CREATE INDEX IF NOT EXISTS document_chunks_chunk_index_idx ON nexus.document_chunks(document_id, chunk_index);

-- Trigger for document_chunks updated_at
DROP TRIGGER IF EXISTS document_chunks_set_updated_at ON nexus.document_chunks;
CREATE TRIGGER document_chunks_set_updated_at
BEFORE UPDATE ON nexus.document_chunks
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- DOCUMENT METADATA TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.document_metadata (
    document_id         uuid PRIMARY KEY REFERENCES nexus.documents(id) ON DELETE CASCADE,
    metadata            jsonb NOT NULL,
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp()
);

-- ============================================
-- INGESTION RUNS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.ingestion_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_type            text NOT NULL,
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

CREATE INDEX IF NOT EXISTS ingestion_runs_status_idx ON nexus.ingestion_runs(status);
CREATE INDEX IF NOT EXISTS ingestion_runs_started_at_idx ON nexus.ingestion_runs(started_at DESC);

-- ============================================
-- KNOWLEDGE GAPS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.knowledge_gaps (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    query               text NOT NULL,
    failure_type        text NOT NULL,
    retrieval_results   jsonb,
    confidence          numeric,
    detected_at         timestamptz NOT NULL DEFAULT clock_timestamp(),
    resolved_at         timestamptz,
    resolution_notes    text,
    CONSTRAINT knowledge_gaps_type_ck CHECK (failure_type IN ('KNOWLEDGE_MISSING', 'RETRIEVAL_FAILURE', 'CONTEXT_FAILURE', 'REASONING_FAILURE', 'GENERATION_FAILURE'))
);

CREATE INDEX IF NOT EXISTS knowledge_gaps_detected_at_idx ON nexus.knowledge_gaps(detected_at DESC);
CREATE INDEX IF NOT EXISTS knowledge_gaps_failure_type_idx ON nexus.knowledge_gaps(failure_type);
CREATE INDEX IF NOT EXISTS knowledge_gaps_resolved_at_idx ON nexus.knowledge_gaps(resolved_at) WHERE resolved_at IS NOT NULL;

-- ============================================
-- VERIFY TABLES CREATED
-- ============================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'nexus'
AND table_name IN ('knowledge_sources', 'documents', 'document_chunks', 'document_metadata', 'ingestion_runs', 'knowledge_gaps')
ORDER BY table_name;
