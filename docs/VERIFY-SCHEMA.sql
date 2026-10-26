-- NEXUSAI - SCHEMA VERIFICATION SCRIPT
-- Run this in Supabase SQL Editor to check what actually exists

-- ============================================
-- CHECK 1: Does nexus schema exist?
-- ============================================
SELECT 
  schema_name,
  schema_owner
FROM information_schema.schemata 
WHERE schema_name = 'nexus';

-- Expected: 1 row with schema_name = 'nexus'
-- If no rows returned: nexus schema does not exist

-- ============================================
-- CHECK 2: What tables exist in nexus schema?
-- ============================================
SELECT 
  table_name,
  table_type
FROM information_schema.tables 
WHERE table_schema = 'nexus'
ORDER BY table_name;

-- Expected: 11 tables (accounts, auth_sessions, user_profiles, etc.)
-- If no rows returned: nexus schema is empty or doesn't exist

-- ============================================
-- CHECK 3: Does user_profiles table exist?
-- ============================================
SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns 
WHERE table_schema = 'nexus' 
AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Expected: Columns including id, account_id, display_name, avatar_storage_path, etc.
-- If no rows returned: user_profiles table doesn't exist

-- ============================================
-- CHECK 4: Does avatar_storage_path column exist?
-- ============================================
SELECT 
  column_name,
  data_type,
  character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'nexus' 
AND table_name = 'user_profiles' 
AND column_name = 'avatar_storage_path';

-- Expected: 1 row with column_name = 'avatar_storage_path'
-- If no rows returned: avatar_storage_path column doesn't exist

-- ============================================
-- CHECK 5: Do Storage buckets exist?
-- ============================================
SELECT 
  name,
  public,
  file_size_limit,
  allowed_mime_types
FROM storage.buckets 
WHERE name IN ('avatars', 'g-media')
ORDER BY name;

-- Expected: 2 rows (avatars and g-media)
-- If no rows returned: buckets don't exist

-- ============================================
-- CHECK 6: Do Storage policies exist?
-- ============================================
-- Note: storage.policies relation may not be accessible in all Supabase environments
-- Check policies in Supabase Dashboard > Storage > [bucket] > Policies

-- Expected: 16 policies (8 for avatars, 8 for g-media)
-- If not visible in Dashboard: Run STORAGE-SETUP.sql in SQL Editor

-- ============================================
-- CHECK 7: What migrations were recorded?
-- ============================================
-- Note: This will fail if nexus schema doesn't exist
-- Try running it only if nexus schema exists

-- SELECT 
--   id,
--   applied_at
-- FROM nexus.schema_migrations
-- ORDER BY applied_at;

-- Expected: Rows with migration IDs (001_bootstrap, 002_core_identity, etc.)
-- If error: schema_migrations table doesn't exist or nexus schema doesn't exist

-- ============================================
-- DIAGNOSIS
-- ============================================
-- After running this script, look at the results:
--
-- If CHECK 1 returns no rows:
--   -> nexus schema was never created
--   -> Solution: Run COMPLETE_SCHEMA.sql again
--
-- If CHECK 1 returns rows but CHECK 2 returns no rows:
--   -> nexus schema exists but is empty
--   -> Solution: Run COMPLETE_SCHEMA.sql again
--
-- If CHECK 2 returns rows but user_profiles is missing:
--   -> Partial schema was created
--   -> Solution: Run COMPLETE_SCHEMA.sql again
--
-- If CHECK 3 returns rows but CHECK 4 returns no rows:
--   -> table exists but avatar_storage_path column missing
--   -> Solution: Run this: ALTER TABLE nexus.user_profiles ADD COLUMN IF NOT EXISTS avatar_storage_path varchar(500);
--
-- If CHECK 5 returns no rows:
--   -> Storage buckets were never created
--   -> Solution: Create buckets in Supabase Dashboard > Storage
--
-- If CHECK 6 returns no rows:
--   -> Storage policies were never applied
--   -> Solution: Run STORAGE-SETUP.sql in SQL Editor
