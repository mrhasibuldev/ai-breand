-- Migration 005: Memory Records Table
-- Creates memory_records table for user memory
-- Note: consent_record_id foreign key will be added in migration 006 to avoid circular dependency

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

-- Trigger for updated_at
DROP TRIGGER IF EXISTS memory_records_set_updated_at ON nexus.memory_records;
CREATE TRIGGER memory_records_set_updated_at
BEFORE UPDATE ON nexus.memory_records
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
