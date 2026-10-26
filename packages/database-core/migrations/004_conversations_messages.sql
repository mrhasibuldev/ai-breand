-- Migration 004: Conversation and Message Tables
-- Creates conversations and messages tables

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
