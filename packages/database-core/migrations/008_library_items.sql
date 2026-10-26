-- Migration 008: Library Items Table
-- Creates library_items table for user-saved content (NEW ENTITY)

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

-- Trigger for updated_at
DROP TRIGGER IF EXISTS library_items_set_updated_at ON nexus.library_items;
CREATE TRIGGER library_items_set_updated_at
BEFORE UPDATE ON nexus.library_items
FOR EACH ROW EXECUTE FUNCTION nexus.set_updated_at();
