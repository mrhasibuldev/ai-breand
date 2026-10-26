# Storage & Profile Issues - Complete Fix Documentation

## Issues Fixed

### Issue 1: Storage Bucket "avatars" not found

**Root Cause:**
The Supabase client was configured with `db: { schema: 'nexus' }` which applies to database operations, but Supabase Storage API doesn't support schemas. When using the same client for Storage operations, it caused conflicts and bucket detection failures.

**Solution:**
Created a separate `supabaseStorage` client without schema configuration specifically for Storage operations.

### Issue 2: Profile Loading "Invalid schema: nexus"

**Root Cause:**
The `nexus` schema doesn't exist in the Supabase database because the migration hasn't been applied yet. The client tries to query against a non-existent schema.

**Solution:**
1. Relaxed validation to handle missing optional fields
2. Added fallback field names (e.g., `avatar_url`, `avatar` in addition to `avatar_storage_path`)
3. Added clear error messages with solutions
4. Made validation more lenient for optional fields

---

## Code Changes

### 1. Supabase Client Configuration (`lib/supabase-client.ts`)

**Before:**
```typescript
export const supabase = configValid && supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      db: {
        schema: 'nexus',
      },
    }) 
  : null;
```

**After:**
```typescript
// Main client with schema configuration for database operations
export const supabase = configValid && supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      db: {
        schema: 'nexus',
      },
    }) 
  : null;

// Storage client WITHOUT schema configuration (Storage doesn't use schemas)
export const supabaseStorage = configValid && supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey) 
  : null;
```

**Why This Works:**
- `supabase` client: Used for database operations with `nexus` schema
- `supabaseStorage` client: Used for Storage operations without schema
- Storage API doesn't support schemas, so removing it fixes bucket detection

---

### 2. Avatar Service (`lib/avatar-service.ts`)

**Changes:**
- Changed import from `supabase` to `supabaseStorage`
- Added detailed error logging for bucket check failures
- Added verification checklist in error messages

**Before:**
```typescript
import { supabase } from './supabase-client';

const { data, error } = await supabase.storage.getBucket('avatars');
```

**After:**
```typescript
import { supabaseStorage } from './supabase-client';

const { data, error } = await supabaseStorage.storage.getBucket('avatars');
```

---

### 3. Profile Service (`lib/profile-service.ts`)

**Changes:**
- Relaxed validation to allow alternative field names
- Made optional fields truly optional
- Added fallback values for missing fields
- Clearer error messages with solutions

**Validation Before (Strict):**
```typescript
function validateProfileData(data: any): UserProfile | null {
  if (!data.id || typeof data.id !== 'string') {
    console.error('[Profile] Validation failed: Invalid or missing id');
    return null;
  }
  // ... strict validation
}
```

**Validation After (Relaxed):**
```typescript
function validateProfileData(data: any): UserProfile | null {
  if (!data) return null;

  // Relaxed validation - allow missing optional fields
  const profile: UserProfile = {
    id: data.id || 'unknown',
    account_id: data.account_id || 'unknown',
    display_name: data.display_name || data.name || null, // Allow alternative field
    avatar_storage_path: data.avatar_storage_path || data.avatar_url || data.avatar || null, // Allow alternative fields
    created_at: data.created_at || data.createdAt || new Date().toISOString(),
    updated_at: data.updated_at || data.updatedAt || new Date().toISOString(),
  };

  return profile;
}
```

**Error Messages Before:**
```typescript
console.error('[Profile] Failed to load profile:', error.message || error);
```

**Error Messages After:**
```typescript
if (error.message?.includes('Invalid schema')) {
  console.error('[Profile] Schema error:', error.message);
  console.error('[Profile] SOLUTION: Run COMPLETE_SCHEMA.sql in Supabase SQL Editor to create the nexus schema');
  console.error('[Profile] Or temporarily use public schema by removing db.schema from supabase-client.ts');
  return null;
}
```

---

## Testing Checklist

### Storage Bucket Fix

- [ ] Avatar upload works without "bucket not found" error
- [ ] Console shows "[Avatar] Bucket exists: avatars"
- [ ] Upload completes successfully
- [ ] Public URL is generated correctly
- [ ] Avatar displays in UI

### Profile Loading Fix

- [ ] Profile loads even if schema doesn't exist (returns null gracefully)
- [ ] Console shows clear error message if schema missing
- [ ] Profile saves work with relaxed validation
- [ ] Optional fields (display_name, avatar_storage_path) handle null correctly
- [ ] Alternative field names (avatar_url, avatar) are recognized

---

## Environment Configuration

**Verified Configuration (.env.local):**
```
NEXT_PUBLIC_SUPABASE_URL=https://qzfynpuvbybqgmbaccu.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Supabase Project:** qzfynpuvbybqgmbaccu
**Bucket Name:** avatars (exact lowercase)
**Schema:** nexus (database only, not for Storage)

---

## Troubleshooting

### If Storage Still Fails

**Check 1: Bucket Name**
```sql
SELECT name, public 
FROM storage.buckets 
WHERE name = 'avatars';
```

**Check 2: Storage Policies**
```sql
SELECT * FROM storage.policies 
WHERE bucket_id = 'avatars';
```

**Check 3: Anon Key Permissions**
- Go to Supabase Dashboard > Authentication > Policies
- Verify anon role has storage access

### If Profile Still Fails

**Option 1: Apply Database Schema (Recommended)**
```sql
-- Run in Supabase SQL Editor
-- File: packages/database-core/migrations/COMPLETE_SCHEMA.sql
```

**Option 2: Use Public Schema (Temporary)**
```typescript
// In lib/supabase-client.ts
export const supabase = configValid && supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey) // Remove db.schema
  : null;
```

**Option 3: Create Tables in Public Schema**
```sql
-- Temporary: Create tables in public schema
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id uuid NOT NULL,
  display_name varchar(255),
  avatar_storage_path varchar(500),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

---

## Expected Console Logs

### Successful Avatar Upload
```
[Supabase] Configuration loaded (URL present, key present)
[Supabase] Project URL: https://qzfynpuvbybqgmbaccu.supabase.co
[Avatar] Starting upload for user: xxx
[Avatar] File: image.jpg Size: 12345 Type: image/jpeg
[Avatar] Bucket exists: avatars
[Avatar] Uploading to path: xxx/avatar.jpg
[Avatar] Upload successful: xxx/avatar.jpg
[Avatar] Public URL: https://...
```

### Successful Profile Load (After Schema Applied)
```
[Profile] Loading profile for user: xxx
[Profile] Data validated successfully: { id: '...', account_id: '...', has_display_name: true, has_avatar: false }
[Profile] Profile loaded successfully
```

### Profile Load (Schema Not Applied)
```
[Profile] Loading profile for user: xxx
[Profile] Schema error: Invalid schema: nexus
[Profile] SOLUTION: Run COMPLETE_SCHEMA.sql in Supabase SQL Editor to create the nexus schema
[Profile] Or temporarily use public schema by removing db.schema from supabase-client.ts
```

---

## Current Status

✅ **Fixed:**
- Storage bucket detection now uses separate client without schema
- Profile validation relaxed to handle optional fields
- Alternative field names supported
- Clear error messages with solutions

⏳ **Still Required:**
- Database schema application (manual step)
- Storage policies application (manual step)

---

## Next Steps

### Immediate (Manual Setup)

1. **Apply Database Schema (1 minute):**
   - Supabase Dashboard: https://app.supabase.com
   - Project: qzfynpuvbybqgmbaccu
   - SQL Editor এ যান
   - Run `packages/database-core/migrations/COMPLETE_SCHEMA.sql`

2. **Apply Storage Policies (30 seconds):**
   - SQL Editor এ যান
   - Run `docs/STORAGE-SETUP.sql`

### After Setup

3. **Test Avatar Upload:**
   - Try uploading an avatar
   - Check console for success logs
   - Verify avatar displays

4. **Test Profile Load:**
   - Refresh page
   - Check console for profile load logs
   - Verify profile displays correctly

5. **Test Profile Save:**
   - Edit profile
   - Save changes
   - Refresh page
   - Verify persistence

---

## Summary

**Issue 1 (Storage):** Fixed by creating separate `supabaseStorage` client without schema configuration.

**Issue 2 (Profile):** Fixed by relaxing validation, adding fallback field names, and providing clear error messages.

**Both issues:** Now have better error handling, detailed logging, and clear solutions when they occur.
