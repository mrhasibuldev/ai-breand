-- Migration 019: Extended Knowledge Source Registry
-- Adds fields for multi-source knowledge acquisition

-- Create collection_jobs table first
CREATE TABLE IF NOT EXISTS nexus.collection_jobs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id           uuid REFERENCES nexus.knowledge_sources(id) ON DELETE CASCADE,
    job_type            text NOT NULL,
    status              text NOT NULL DEFAULT 'pending',
    started_at          timestamptz,
    completed_at        timestamptz,
    documents_collected integer NOT NULL DEFAULT 0,
    documents_failed    integer NOT NULL DEFAULT 0,
    documents_skipped   integer NOT NULL DEFAULT 0,
    bytes_downloaded    bigint NOT NULL DEFAULT 0,
    error_message       text,
    metadata            jsonb,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT collection_jobs_type_ck CHECK (job_type IN ('full', 'incremental', 'manual')),
    CONSTRAINT collection_jobs_status_ck CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS collection_jobs_source_idx ON nexus.collection_jobs(source_id, created_at DESC);
CREATE INDEX IF NOT EXISTS collection_jobs_status_idx ON nexus.collection_jobs(status, created_at DESC);

-- Add new columns to nexus.knowledge_sources
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'source_category' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN source_category text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'description' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN description text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'collection_method' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN collection_method text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'api_config_ref' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN api_config_ref text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'robots_txt_policy' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN robots_txt_policy text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'tos_status' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN tos_status text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'language' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN language text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'trust_level' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN trust_level text;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'last_successful_collection' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN last_successful_collection timestamptz;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'next_scheduled_collection' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN next_scheduled_collection timestamptz;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'knowledge_sources' AND column_name = 'collection_frequency' AND table_schema = 'nexus') THEN
        ALTER TABLE nexus.knowledge_sources ADD COLUMN collection_frequency text;
    END IF;
END $$;

-- Add constraints
ALTER TABLE nexus.knowledge_sources
DROP CONSTRAINT IF EXISTS knowledge_sources_collection_method_ck;

ALTER TABLE nexus.knowledge_sources
ADD CONSTRAINT knowledge_sources_collection_method_ck
  CHECK (collection_method IN ('api', 'crawl', 'rss', 'download', 'manual_upload'));

ALTER TABLE nexus.knowledge_sources
DROP CONSTRAINT IF EXISTS knowledge_sources_tos_status_ck;

ALTER TABLE nexus.knowledge_sources
ADD CONSTRAINT knowledge_sources_tos_status_ck
  CHECK (tos_status IN ('unknown', 'compliant', 'restricted', 'blocked'));

ALTER TABLE nexus.knowledge_sources
DROP CONSTRAINT IF EXISTS knowledge_sources_trust_level_ck;

ALTER TABLE nexus.knowledge_sources
ADD CONSTRAINT knowledge_sources_trust_level_ck
  CHECK (trust_level IN ('TIER_1', 'TIER_2', 'TIER_3', 'TIER_4'));

ALTER TABLE nexus.knowledge_sources
DROP CONSTRAINT IF EXISTS knowledge_sources_frequency_ck;

ALTER TABLE nexus.knowledge_sources
ADD CONSTRAINT knowledge_sources_frequency_ck
  CHECK (collection_frequency IN ('once', 'daily', 'weekly', 'monthly', 'on_demand'));

-- Add indexes
CREATE INDEX IF NOT EXISTS knowledge_sources_category_idx ON nexus.knowledge_sources(source_category);
CREATE INDEX IF NOT EXISTS knowledge_sources_collection_method_idx ON nexus.knowledge_sources(collection_method);
CREATE INDEX IF NOT EXISTS knowledge_sources_trust_level_idx ON nexus.knowledge_sources(trust_level);
CREATE INDEX IF NOT EXISTS knowledge_sources_next_collection_idx ON nexus.knowledge_sources(next_scheduled_collection) WHERE next_scheduled_collection IS NOT NULL;

-- Trigger for updated_at
DROP TRIGGER IF EXISTS knowledge_sources_set_updated_at ON nexus.knowledge_sources;
CREATE TRIGGER knowledge_sources_set_updated_at
BEFORE UPDATE ON nexus.knowledge_sources
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

DROP TRIGGER IF EXISTS collection_jobs_set_updated_at ON nexus.collection_jobs;
CREATE TRIGGER collection_jobs_set_updated_at
BEFORE UPDATE ON nexus.collection_jobs
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'nexus'
AND table_name = 'knowledge_sources'
AND column_name IN ('source_category', 'collection_method', 'trust_level', 'last_successful_collection', 'next_scheduled_collection')
ORDER BY column_name;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'nexus'
AND table_name = 'collection_jobs';
