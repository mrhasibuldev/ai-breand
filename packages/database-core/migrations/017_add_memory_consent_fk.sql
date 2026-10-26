-- Migration 017: Add Memory Records Consent Foreign Key
-- Adds the foreign key constraint from memory_records to consent_records
-- This was deferred from migration 005 to avoid circular dependency

ALTER TABLE nexus.memory_records
ADD CONSTRAINT memory_records_consent_fk
FOREIGN KEY (consent_record_id)
REFERENCES nexus.consent_records (id) ON DELETE RESTRICT;
