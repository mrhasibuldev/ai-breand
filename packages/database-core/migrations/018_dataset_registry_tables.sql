-- Migration 018: Dataset Registry Tables
-- Creates dedicated tables for dataset management, approval workflow, and training eligibility

-- ============================================
-- DATASET REGISTRY TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.dataset_registry (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    dataset_name        varchar(255) NOT NULL,
    description         text,
    category            varchar(100),
    storage_key         varchar(500) NOT NULL,
    file_size_bytes     bigint NOT NULL,
    sha256_checksum     varchar(64) NOT NULL,
    mime_type           varchar(100) NOT NULL,
    version             varchar(50) NOT NULL DEFAULT 'v1.0',
    source              varchar(100),
    provenance          text,
    license             varchar(100),
    privacy_status      text NOT NULL DEFAULT 'private',
    validation_status   text NOT NULL DEFAULT 'pending',
    approval_status     text NOT NULL DEFAULT 'pending_review',
    training_eligible   boolean NOT NULL DEFAULT false,
    ingestion_run_id    uuid REFERENCES nexus.ingestion_runs(id) ON DELETE SET NULL,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT dataset_registry_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts(id) ON DELETE RESTRICT,
    CONSTRAINT dataset_registry_account_id_uk UNIQUE (account_id, dataset_name, version),
    CONSTRAINT dataset_registry_storage_key_uk UNIQUE (storage_key),
    CONSTRAINT dataset_registry_checksum_uk UNIQUE (sha256_checksum),
    CONSTRAINT dataset_registry_name_ck CHECK (char_length(btrim(dataset_name)) > 0),
    CONSTRAINT dataset_registry_size_ck CHECK (file_size_bytes >= 0),
    CONSTRAINT dataset_registry_checksum_ck CHECK (char_length(sha256_checksum) = 64),
    CONSTRAINT dataset_registry_privacy_ck CHECK (privacy_status IN ('public', 'private', 'restricted')),
    CONSTRAINT dataset_registry_validation_ck CHECK (validation_status IN ('pending', 'validating', 'valid', 'invalid', 'failed')),
    CONSTRAINT dataset_registry_approval_ck CHECK (approval_status IN ('pending_review', 'approved', 'rejected', 'archived'))
);

CREATE INDEX IF NOT EXISTS dataset_registry_account_idx ON nexus.dataset_registry(account_id, created_at DESC);
CREATE INDEX IF NOT EXISTS dataset_registry_status_idx ON nexus.dataset_registry(approval_status, training_eligible);
CREATE INDEX IF NOT EXISTS dataset_registry_category_idx ON nexus.dataset_registry(category);
CREATE INDEX IF NOT EXISTS dataset_registry_checksum_idx ON nexus.dataset_registry(sha256_checksum);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS dataset_registry_set_updated_at ON nexus.dataset_registry;
CREATE TRIGGER dataset_registry_set_updated_at
BEFORE UPDATE ON nexus.dataset_registry
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();

-- ============================================
-- DATASET VERSION HISTORY TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.dataset_versions (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id          uuid NOT NULL REFERENCES nexus.dataset_registry(id) ON DELETE CASCADE,
    version             varchar(50) NOT NULL,
    storage_key         varchar(500) NOT NULL,
    file_size_bytes     bigint NOT NULL,
    sha256_checksum     varchar(64) NOT NULL,
    is_active           boolean NOT NULL DEFAULT false,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT dataset_versions_dataset_id_version_uk UNIQUE (dataset_id, version),
    CONSTRAINT dataset_versions_storage_key_uk UNIQUE (storage_key),
    CONSTRAINT dataset_versions_size_ck CHECK (file_size_bytes >= 0),
    CONSTRAINT dataset_versions_checksum_ck CHECK (char_length(sha256_checksum) = 64)
);

CREATE INDEX IF NOT EXISTS dataset_versions_dataset_idx ON nexus.dataset_versions(dataset_id, created_at DESC);
CREATE INDEX IF NOT EXISTS dataset_versions_active_idx ON nexus.dataset_versions(dataset_id, is_active) WHERE is_active = true;

-- ============================================
-- DATASET APPROVAL HISTORY TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.dataset_approval_history (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id          uuid NOT NULL REFERENCES nexus.dataset_registry(id) ON DELETE CASCADE,
    reviewer_id         uuid REFERENCES nexus.accounts(id) ON DELETE SET NULL,
    previous_status     text,
    new_status          text NOT NULL,
    reason              text,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT dataset_approval_history_status_ck CHECK (new_status IN ('pending_review', 'approved', 'rejected', 'archived'))
);

CREATE INDEX IF NOT EXISTS dataset_approval_history_dataset_idx ON nexus.dataset_approval_history(dataset_id, created_at DESC);

-- ============================================
-- TRAINING RUNS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS nexus.training_runs (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id          uuid NOT NULL REFERENCES nexus.dataset_registry(id) ON DELETE RESTRICT,
    dataset_version     varchar(50) NOT NULL,
    model_config        jsonb NOT NULL,
    training_config     jsonb NOT NULL,
    metrics             jsonb,
    checkpoint_path     varchar(500),
    status              text NOT NULL DEFAULT 'pending',
    started_at          timestamptz,
    completed_at        timestamptz,
    error_message       text,
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT training_runs_status_ck CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS training_runs_dataset_idx ON nexus.training_runs(dataset_id, created_at DESC);
CREATE INDEX IF NOT EXISTS training_runs_status_idx ON nexus.training_runs(status, created_at DESC);

-- ============================================
-- VERIFY TABLES CREATED
-- ============================================

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'nexus' 
AND table_name IN ('dataset_registry', 'dataset_versions', 'dataset_approval_history', 'training_runs')
ORDER BY table_name;
