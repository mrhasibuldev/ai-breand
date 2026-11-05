-- NEXUSAI - FIX STORAGE PROVIDER DEFAULT
-- Migration: 020_fix_storage_provider_default
-- Purpose: Update storage_provider default from 'supabase' to 's3' for Neon Object Storage
-- This aligns the schema with the actual S3-compatible storage implementation

-- Update default value for new rows
ALTER TABLE nexus.file_metadata
ALTER COLUMN storage_provider SET DEFAULT 's3';

-- Update existing rows that still have 'supabase' to 's3'
-- Since we use Neon Object Storage via S3-compatible API, 's3' is the correct identifier
UPDATE nexus.file_metadata
SET storage_provider = 's3'
WHERE storage_provider = 'supabase';

-- Verify the change
SELECT column_name, column_default
FROM information_schema.columns
WHERE table_schema = 'nexus'
AND table_name = 'file_metadata'
AND column_name = 'storage_provider';
