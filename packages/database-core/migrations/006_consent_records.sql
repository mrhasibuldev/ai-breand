-- Migration 006: Consent Records Table
-- Creates consent_records table for tracking user consent decisions

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
