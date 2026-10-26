# SUPABASE STORAGE BUCKET SETUP GUIDE

## Problem: "bucket not found" Error

This error occurs when the `avatars` bucket doesn't exist in Supabase Storage.

## Solution: Create the Bucket

### Step 1: Check Existing Buckets
1. Go to Supabase Dashboard: https://app.supabase.com
2. Select project: qzfynpuvbybqgmbaccu
3. Click **Storage** in the left sidebar
4. Check if "avatars" bucket exists in the list

### Step 2: Create avatars Bucket (if not exists)
1. Click **Create a new bucket**
2. Fill in:
   - **Name:** `avatars` (exact lowercase)
   - **Public bucket:** No (uncheck)
   - **File size limit:** 5MB
   - **Allowed MIME types:** `image/jpeg, image/png, image/webp, image/gif`
3. Click **Create bucket**

### Step 3: Create g-media Bucket (if not exists)
1. Click **Create a new bucket**
2. Fill in:
   - **Name:** `g-media` (exact lowercase with hyphen)
   - **Public bucket:** No (uncheck)
   - **File size limit:** 100MB
   - **Allowed MIME types:** `image/*, video/*, audio/*, application/pdf`
3. Click **Create bucket**

### Step 4: Apply Storage Policies
1. Go to **SQL Editor**
2. Copy contents of `docs/STORAGE-SETUP.sql`
3. Paste and Run
4. Verify 8 policies created

## Verification

After setup, verify buckets exist:
```sql
SELECT id, name, public, file_size_limit
FROM storage.buckets
WHERE name IN ('avatars', 'g-media');
```

## Debugging

If you still get "bucket not found" error:

1. **Check browser console:**
   - Open DevTools (F12)
   - Look for `[Avatar]` logs
   - Check error details

2. **Check bucket name:**
   - Ensure bucket name is exactly `avatars` (lowercase)
   - Check code in `apps/web/lib/avatar-service.ts` line 25
   - Must match exactly

3. **Check bucket permissions:**
   - Ensure bucket is not public
   - Ensure policies are applied
   - Check user is authenticated

## Expected Console Logs

On successful upload:
```
[Avatar] Starting upload for user: <user-id>
[Avatar] File: image.jpg Size: 12345 Type: image/jpeg
[Avatar] Bucket exists: avatars
[Avatar] Uploading to path: <user-id>/avatar.jpg
[Avatar] Upload successful: <user-id>/avatar.jpg
[Avatar] Public URL: https://...
```

On bucket not found:
```
[Avatar] Bucket check failed: Bucket not found
[Avatar] Starting upload for user: <user-id>
[Avatar] Bucket does not exist
Error: Storage bucket "avatars" not found. Please create it in Supabase Dashboard > Storage
```
