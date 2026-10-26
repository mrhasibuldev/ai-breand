-- NEXUSAI - ADD AVATAR STORAGE PATH TO USER PROFILES
-- Migration: 010_add_avatar_storage_path
-- Purpose: Add avatar_storage_path column to user_profiles table for persistent avatar support

-- Add avatar_storage_path column
ALTER TABLE nexus.user_profiles 
ADD COLUMN IF NOT EXISTS avatar_storage_path varchar(500);

-- Add comment to document the column
COMMENT ON COLUMN nexus.user_profiles.avatar_storage_path IS 'Storage path for profile avatar in Supabase Storage (e.g., {user_id}/avatar.webp)';

-- Verify column added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_schema = 'nexus' 
AND table_name = 'user_profiles' 
AND column_name = 'avatar_storage_path';
