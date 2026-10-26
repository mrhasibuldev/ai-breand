-- Migration: Fix conversations.account_id to use auth.uid() directly
-- This removes the FK constraint to nexus.accounts since auth.uid() refers to auth.users
-- not nexus.accounts. This aligns the schema with Supabase Auth's expected behavior.

-- Step 1: Drop the foreign key constraint
ALTER TABLE nexus.conversations DROP CONSTRAINT IF EXISTS conversations_account_fk;

-- Step 2: Remove the unique constraint that includes account_id (will recreate without it)
ALTER TABLE nexus.conversations DROP CONSTRAINT IF EXISTS conversations_account_id_uk;

-- Step 3: Add a new unique constraint on id only (for foreign key references from messages)
ALTER TABLE nexus.conversations ADD CONSTRAINT conversations_id_uk UNIQUE (id);

-- Step 4: Add a comment explaining that account_id should equal auth.uid()
COMMENT ON COLUMN nexus.conversations.account_id IS 'Supabase Auth user ID (auth.uid()), not nexus.accounts.id';

-- Verification
SELECT 
  column_name, 
  data_type, 
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'nexus' 
  AND table_name = 'conversations'
ORDER BY ordinal_position;
