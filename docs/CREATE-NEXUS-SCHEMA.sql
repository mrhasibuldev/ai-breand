-- NEXUSAI - MINIMAL SCHEMA CREATION
-- Run this in Supabase SQL Editor
-- This creates ONLY what's needed for profile/avatar to work

-- ============================================
-- STEP 1: Create nexus schema
-- ============================================
CREATE SCHEMA IF NOT EXISTS nexus;

-- ============================================
-- STEP 2: Create user_profiles table
-- ============================================
CREATE TABLE IF NOT EXISTS nexus.user_profiles (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    display_name        varchar(120),
    avatar_storage_path varchar(500),
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT user_profiles_account_uk UNIQUE (account_id)
);

-- ============================================
-- STEP 3: Add RLS policies
-- ============================================
ALTER TABLE nexus.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read own profile
DROP POLICY IF EXISTS "Users can read own profile" ON nexus.user_profiles;
CREATE POLICY "Users can read own profile"
ON nexus.user_profiles FOR SELECT
TO authenticated
USING (account_id = auth.uid());

-- Policy: Users can insert own profile
DROP POLICY IF EXISTS "Users can insert own profile" ON nexus.user_profiles;
CREATE POLICY "Users can insert own profile"
ON nexus.user_profiles FOR INSERT
TO authenticated
WITH CHECK (account_id = auth.uid());

-- Policy: Users can update own profile
DROP POLICY IF EXISTS "Users can update own profile" ON nexus.user_profiles;
CREATE POLICY "Users can update own profile"
ON nexus.user_profiles FOR UPDATE
TO authenticated
USING (account_id = auth.uid())
WITH CHECK (account_id = auth.uid());

-- ============================================
-- STEP 4: Verification
-- ============================================
-- Check if schema exists
SELECT 'nexus schema exists' as status, schema_name 
FROM information_schema.schemata 
WHERE schema_name = 'nexus';

-- Check if table exists
SELECT 'user_profiles table exists' as status, table_name 
FROM information_schema.tables 
WHERE table_schema = 'nexus' AND table_name = 'user_profiles';

-- Check if columns exist
SELECT 'user_profiles columns' as status, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'nexus' AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Check if RLS is enabled
SELECT 'RLS enabled' as status, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'nexus' AND tablename = 'user_profiles';

-- Check if policies exist
SELECT 'RLS policies' as status, policyname, cmd 
FROM pg_policies 
WHERE schemaname = 'nexus' AND tablename = 'user_profiles';
