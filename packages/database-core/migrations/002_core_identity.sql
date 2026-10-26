-- Migration 002: Core Identity Tables
-- Creates accounts and auth_sessions tables

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

-- Triggers for updated_at
DROP TRIGGER IF EXISTS accounts_set_updated_at ON nexus.accounts;
CREATE TRIGGER accounts_set_updated_at
BEFORE UPDATE ON nexus.accounts
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
