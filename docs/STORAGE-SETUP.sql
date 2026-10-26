-- NEXUSAI - SUPABASE STORAGE SETUP FOR AVATARS AND G-MEDIA
-- IMPORTANT: This file documents the required Storage setup
-- Storage buckets must be created MANUALLY in Supabase Dashboard
-- Storage policies SQL should be run AFTER buckets are created

-- ============================================
-- MANUAL SETUP STEPS (REQUIRED)
-- ============================================
-- Step 1: Create Storage Buckets in Supabase Dashboard
-- Go to Storage section and create these buckets:

-- BUCKET 1: avatars
-- Purpose: Store user profile pictures
-- Public: No (private, authenticated access only)
-- File size limit: 5MB (recommended for avatars)
-- Allowed MIME types: image/jpeg, image/png, image/webp, image/gif

-- BUCKET 2: g-media
-- Purpose: Store G-Media files (images, videos, audio, documents)
-- Public: No (private, authenticated access only)
-- File size limit: 100MB (adjust based on needs)
-- Allowed MIME types: image/*, video/*, audio/*, application/pdf

-- Step 2: Run Storage Policies SQL (AFTER buckets are created)
-- Use the SQL section below after manually creating the buckets
-- The policies will restrict access to authenticated users only

-- ============================================
-- STORAGE POLICIES SQL
-- Run this AFTER creating the buckets manually
-- ============================================

-- AVATARS BUCKET POLICIES

-- Policy: Users can upload avatars to their own folder
DROP POLICY IF EXISTS "Users can upload own avatars" ON storage.objects;
CREATE POLICY "Users can upload own avatars"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'avatars'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy: Users can read their own avatars
DROP POLICY IF EXISTS "Users can read own avatars" ON storage.objects;
CREATE POLICY "Users can read own avatars"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'avatars'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy: Users can replace their own avatars
DROP POLICY IF EXISTS "Users can replace own avatars" ON storage.objects;
CREATE POLICY "Users can replace own avatars"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'avatars'
  AND auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
  bucket_id = 'avatars'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy: Users can delete their own avatars
DROP POLICY IF EXISTS "Users can delete own avatars" ON storage.objects;
CREATE POLICY "Users can delete own avatars"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'avatars'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- G-MEDIA BUCKET POLICIES

-- Policy: Users can upload media to their own folder
DROP POLICY IF EXISTS "Users can upload own g-media" ON storage.objects;
CREATE POLICY "Users can upload own g-media"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'g-media'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy: Users can read their own media
DROP POLICY IF EXISTS "Users can read own g-media" ON storage.objects;
CREATE POLICY "Users can read own g-media"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'g-media'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy: Users can replace their own media
DROP POLICY IF EXISTS "Users can replace own g-media" ON storage.objects;
CREATE POLICY "Users can replace own g-media"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'g-media'
  AND auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
  bucket_id = 'g-media'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy: Users can delete their own media
DROP POLICY IF EXISTS "Users can delete own g-media" ON storage.objects;
CREATE POLICY "Users can delete own g-media"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'g-media'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- ============================================
-- COMPLETE
-- After running these policies, verify in Storage section of Dashboard
-- ============================================
