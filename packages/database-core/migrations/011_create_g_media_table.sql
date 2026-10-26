-- NEXUSAI - G-MEDIA TABLE CREATION
-- Migration: 011_create_g_media_table
-- Purpose: Create table for persistent G-Media storage with Supabase Storage integration

CREATE TABLE IF NOT EXISTS nexus.g_media (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    media_type          text NOT NULL,
    title               varchar(255),
    description         text,
    storage_path        varchar(500) NOT NULL,
    file_name           varchar(255),
    mime_type           varchar(100) NOT NULL,
    file_size_bytes     bigint NOT NULL,
    width               integer,
    height              integer,
    duration_seconds    numeric,
    thumbnail_path      varchar(500),
    metadata            jsonb,
    status              text NOT NULL DEFAULT 'active',
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT g_media_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT g_media_account_id_uk UNIQUE (account_id, id),
    CONSTRAINT g_media_type_ck CHECK (media_type IN ('image', 'video', 'audio', 'document', 'other')),
    CONSTRAINT g_media_status_ck CHECK (status IN ('active', 'deleted', 'processing', 'failed')),
    CONSTRAINT g_media_size_ck CHECK (file_size_bytes >= 0),
    CONSTRAINT g_media_deleted_state_ck CHECK (status <> 'deleted' OR deleted_at IS NOT NULL)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS g_media_account_created_idx
    ON nexus.g_media (account_id, created_at DESC);

CREATE INDEX IF NOT EXISTS g_media_type_idx
    ON nexus.g_media (media_type);

CREATE INDEX IF NOT EXISTS g_media_status_idx
    ON nexus.g_media (status);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS g_media_set_updated_at ON nexus.g_media;
CREATE TRIGGER g_media_set_updated_at
BEFORE UPDATE ON nexus.g_media
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
