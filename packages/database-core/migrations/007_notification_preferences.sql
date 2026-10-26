-- Migration 007: Notification Preferences Table
-- Creates notification_preferences table for user preferences

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

-- Trigger for updated_at
DROP TRIGGER IF EXISTS notification_preferences_set_updated_at ON nexus.notification_preferences;
CREATE TRIGGER notification_preferences_set_updated_at
BEFORE UPDATE ON nexus.notification_preferences
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
