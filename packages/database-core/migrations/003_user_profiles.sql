-- Migration 003: User Profile Table
-- Creates user_profiles table

CREATE TABLE IF NOT EXISTS nexus.user_profiles (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    display_name        varchar(120),
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

-- Trigger for updated_at
DROP TRIGGER IF EXISTS user_profiles_set_updated_at ON nexus.user_profiles;
CREATE TRIGGER user_profiles_set_updated_at
BEFORE UPDATE ON nexus.user_profiles
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
