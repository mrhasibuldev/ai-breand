-- NEXUSAI - COMPLETE DATABASE SCHEMA
-- Run this entire script in Supabase SQL Editor
-- This creates all required tables for NexusAI application

-- ============================================
-- PART 1: BOOTSTRAP
-- ============================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS nexus;
SET search_path = nexus, public;

CREATE OR REPLACE FUNCTION nexus.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = clock_timestamp();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION nexus.prevent_history_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Append-only history cannot be updated or deleted: %.%', TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$;

-- ============================================
-- PART 2: CORE IDENTITY TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.accounts (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_issuer         varchar(100) NOT NULL,
    auth_subject        varchar(255) NOT NULL,
    email_normalized    varchar(320) NOT NULL,
    status              text NOT NULL DEFAULT 'active',
    email_verified_at   timestamptz,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    purge_after         timestamptz,
    CONSTRAINT accounts_auth_identity_uk UNIQUE (auth_issuer, auth_subject),
    CONSTRAINT accounts_status_ck CHECK (status IN ('active', 'suspended', 'deletion_pending', 'deleted', 'purged')),
    CONSTRAINT accounts_verified_after_created_ck CHECK (email_verified_at IS NULL OR email_verified_at >= created_at),
    CONSTRAINT accounts_deleted_state_ck CHECK (status NOT IN ('deletion_pending', 'deleted', 'purged') OR deleted_at IS NOT NULL),
    CONSTRAINT accounts_purge_after_deleted_ck CHECK (purge_after IS NULL OR deleted_at IS NOT NULL)
);

CREATE UNIQUE INDEX IF NOT EXISTS accounts_email_nonpurged_uk
    ON nexus.accounts (email_normalized)
    WHERE status <> 'purged';

CREATE INDEX IF NOT EXISTS accounts_status_created_idx
    ON nexus.accounts (status, created_at);

CREATE TABLE IF NOT EXISTS nexus.auth_sessions (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    session_token_hash  varchar(255) NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    expires_at          timestamptz NOT NULL,
    last_seen_at        timestamptz NOT NULL DEFAULT clock_timestamp(),
    revoked_at          timestamptz,
    status              text NOT NULL DEFAULT 'active',
    CONSTRAINT auth_sessions_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT auth_sessions_token_uk UNIQUE (session_token_hash),
    CONSTRAINT auth_sessions_status_ck CHECK (status IN ('active', 'expired', 'revoked')),
    CONSTRAINT auth_sessions_expiry_ck CHECK (expires_at > created_at),
    CONSTRAINT auth_sessions_last_seen_ck CHECK (last_seen_at >= created_at),
    CONSTRAINT auth_sessions_revoked_ck CHECK (revoked_at IS NULL OR revoked_at >= created_at),
    CONSTRAINT auth_sessions_revoked_state_ck CHECK (status <> 'revoked' OR revoked_at IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS auth_sessions_account_status_idx
    ON nexus.auth_sessions (account_id, status, expires_at);

-- Trigger for accounts updated_at
DROP TRIGGER IF EXISTS accounts_set_updated_at ON nexus.accounts;
CREATE TRIGGER accounts_set_updated_at
BEFORE UPDATE ON nexus.accounts
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- PART 3: USER PROFILE TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.user_profiles (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    display_name        varchar(120),
    avatar_storage_path varchar(500),
    age_band            varchar(40),
    locale              varchar(20),
    timezone            varchar(64),
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT user_profiles_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT user_profiles_account_uk UNIQUE (account_id),
    CONSTRAINT user_profiles_display_name_ck CHECK (display_name IS NULL OR char_length(btrim(display_name)) > 0)
);

-- Trigger for user_profiles updated_at
DROP TRIGGER IF EXISTS user_profiles_set_updated_at ON nexus.user_profiles;
CREATE TRIGGER user_profiles_set_updated_at
BEFORE UPDATE ON nexus.user_profiles
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- PART 4: CONVERSATION AND MESSAGE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.conversations (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    status              text NOT NULL DEFAULT 'active',
    title               varchar(160),
    started_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    ended_at            timestamptz,
    deleted_at          timestamptz,
    CONSTRAINT conversations_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT conversations_account_id_uk UNIQUE (account_id, id),
    CONSTRAINT conversations_status_ck CHECK (status IN ('active', 'ended', 'deleted')),
    CONSTRAINT conversations_end_order_ck CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT conversations_deleted_state_ck CHECK (status <> 'deleted' OR deleted_at IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS conversations_account_started_idx
    ON nexus.conversations (account_id, started_at DESC);

CREATE TABLE IF NOT EXISTS nexus.messages (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     uuid NOT NULL,
    sequence_no         integer NOT NULL,
    sender_role         text NOT NULL,
    content             text NOT NULL,
    content_status      text NOT NULL DEFAULT 'active',
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT messages_conversation_fk FOREIGN KEY (conversation_id)
        REFERENCES nexus.conversations (id) ON DELETE RESTRICT,
    CONSTRAINT messages_conversation_sequence_uk UNIQUE (conversation_id, sequence_no),
    CONSTRAINT messages_sequence_ck CHECK (sequence_no > 0),
    CONSTRAINT messages_role_ck CHECK (sender_role IN ('user', 'assistant')),
    CONSTRAINT messages_content_ck CHECK (char_length(btrim(content)) > 0),
    CONSTRAINT messages_content_status_ck CHECK (content_status IN ('active', 'redacted', 'deleted', 'blocked')),
    CONSTRAINT messages_deleted_state_ck CHECK (content_status IN ('deleted', 'redacted') OR deleted_at IS NULL OR content_status = 'blocked')
);

CREATE INDEX IF NOT EXISTS messages_conversation_sequence_idx
    ON nexus.messages (conversation_id, sequence_no);

-- ============================================
-- PART 5: CONSENT RECORDS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.consent_records (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    consent_type        text NOT NULL,
    policy_version      varchar(80) NOT NULL,
    decision            text NOT NULL,
    captured_at         timestamptz NOT NULL DEFAULT clock_timestamp(),
    revoked_at          timestamptz,
    capture_source      varchar(40) NOT NULL,
    CONSTRAINT consent_records_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT consent_records_type_ck CHECK (char_length(btrim(consent_type)) BETWEEN 1 AND 80),
    CONSTRAINT consent_records_decision_ck CHECK (decision IN ('granted', 'denied', 'revoked', 'superseded')),
    CONSTRAINT consent_records_revoke_ck CHECK (decision <> 'revoked' OR revoked_at IS NOT NULL),
    CONSTRAINT consent_records_source_ck CHECK (char_length(btrim(capture_source)) BETWEEN 1 AND 40)
);

CREATE INDEX IF NOT EXISTS consent_records_account_type_time_idx
    ON nexus.consent_records (account_id, consent_type, captured_at DESC);

-- Trigger for append-only (prevent updates/deletes)
DROP TRIGGER IF EXISTS consent_records_append_only ON nexus.consent_records;
CREATE TRIGGER consent_records_append_only
BEFORE UPDATE OR DELETE ON nexus.consent_records
FOR EACH ROW EXECUTE FUNCTION nexus.prevent_history_mutation();

-- ============================================
-- PART 6: MEMORY RECORDS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.memory_records (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id              uuid NOT NULL,
    consent_record_id       uuid,
    source_message_id       uuid,
    category                text NOT NULL,
    purpose                 text NOT NULL,
    value                   text NOT NULL,
    status                  text NOT NULL DEFAULT 'candidate',
    created_at              timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at              timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at              timestamptz,
    CONSTRAINT memory_records_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT memory_records_consent_fk FOREIGN KEY (consent_record_id)
        REFERENCES nexus.consent_records (id) ON DELETE RESTRICT,
    CONSTRAINT memory_records_source_message_fk FOREIGN KEY (source_message_id)
        REFERENCES nexus.messages (id) ON DELETE RESTRICT,
    CONSTRAINT memory_records_category_ck CHECK (category IN ('name', 'age_band', 'wellness_goal', 'preference', 'daily_habit', 'plan_preference', 'custom')),
    CONSTRAINT memory_records_purpose_ck CHECK (char_length(btrim(purpose)) > 0),
    CONSTRAINT memory_records_value_ck CHECK (char_length(btrim(value)) > 0),
    CONSTRAINT memory_records_status_ck CHECK (status IN ('candidate', 'approved', 'rejected', 'revoked', 'deleted')),
    CONSTRAINT memory_records_deleted_state_ck CHECK (status <> 'deleted' OR deleted_at IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS memory_records_account_status_idx
    ON nexus.memory_records (account_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS memory_records_category_idx
    ON nexus.memory_records (category);

-- Trigger for memory_records updated_at
DROP TRIGGER IF EXISTS memory_records_set_updated_at ON nexus.memory_records;
CREATE TRIGGER memory_records_set_updated_at
BEFORE UPDATE ON nexus.memory_records
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- PART 7: NOTIFICATION PREFERENCES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.notification_preferences (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    email_enabled       boolean NOT NULL DEFAULT false,
    push_enabled        boolean NOT NULL DEFAULT false,
    timezone            varchar(64),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT notification_preferences_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT notification_preferences_account_uk UNIQUE (account_id)
);

-- Trigger for notification_preferences updated_at
DROP TRIGGER IF EXISTS notification_preferences_set_updated_at ON nexus.notification_preferences;
CREATE TRIGGER notification_preferences_set_updated_at
BEFORE UPDATE ON nexus.notification_preferences
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- PART 8: LIBRARY ITEMS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.library_items (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    item_type           text NOT NULL,
    title               varchar(255) NOT NULL,
    description         text,
    content             text,
    storage_reference   varchar(500),
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT library_items_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT library_items_account_id_uk UNIQUE (account_id, id),
    CONSTRAINT library_items_type_ck CHECK (item_type IN ('note', 'bookmark', 'reference', 'custom')),
    CONSTRAINT library_items_title_ck CHECK (char_length(btrim(title)) > 0)
);

CREATE INDEX IF NOT EXISTS library_items_account_type_idx
    ON nexus.library_items (account_id, item_type, created_at DESC);

-- Trigger for library_items updated_at
DROP TRIGGER IF EXISTS library_items_set_updated_at ON nexus.library_items;
CREATE TRIGGER library_items_set_updated_at
BEFORE UPDATE ON nexus.library_items
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- PART 9: FILE METADATA TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.file_metadata (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    storage_provider     text NOT NULL DEFAULT 'supabase',
    storage_key          varchar(500) NOT NULL,
    mime_type            varchar(100) NOT NULL,
    size_bytes          bigint NOT NULL,
    file_name           varchar(255),
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT file_metadata_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT file_metadata_account_id_uk UNIQUE (account_id, id),
    CONSTRAINT file_metadata_provider_ck CHECK (storage_provider IN ('supabase', 's3', 'local')),
    CONSTRAINT file_metadata_size_ck CHECK (size_bytes >= 0)
);

CREATE INDEX IF NOT EXISTS file_metadata_account_created_idx
    ON nexus.file_metadata (account_id, created_at DESC);

-- ============================================
-- PART 10: MIGRATIONS TRACKING TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.schema_migrations (
    id TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Record all migrations as applied
INSERT INTO nexus.schema_migrations (id) VALUES 
('001_bootstrap'),
('002_core_identity'),
('003_user_profiles'),
('004_conversations_messages'),
('005_consent_records'),
('006_memory_records'),
('007_notification_preferences'),
('008_library_items'),
('009_file_metadata'),
('011_create_g_media_table'),
('012_g_media_rls_policies')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- COMPLETE
-- ============================================

-- Verify tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'nexus' 
ORDER BY table_name;
