# NexusAI - Avatar Persistence Forensic Report

**Date**: 2026-11-05
**Task**: Avatar Persistence Investigation
**Status**: ✅ ROOT CAUSE IDENTIFIED

---

## Executive Summary

The profile picture upload appears to succeed and the image may display immediately, but after page refresh the image disappears. The root cause is that the `ProfileRepository` does not include `avatar_storage_path` in its database queries or the `UserProfile` interface, even though the avatar upload endpoint correctly saves the storage path to the database.

**Root Cause**: ProfileRepository missing `avatar_storage_path` column in SELECT queries and interface
**Severity**: HIGH - Users cannot see their uploaded profile pictures after refresh
**Status**: ✅ IDENTIFIED - Ready for repair

---

## User-Reported Problem

**Symptoms**:
- Profile picture upload appears to succeed
- Uploaded picture may appear immediately
- After refreshing the page, the picture disappears
- Browser console shows warnings (CSS, aborted logo request) - these are unrelated

**Console Observations** (Unrelated):
- `GET http://localhost:3000/images/logo.png` - NS_BINDING_ABORTED
- CSS warnings about `-moz-osx-font-smoothing`
- CSS parsing warnings
- These are NOT the root cause

---

## Phase 1: Complete Avatar Lifecycle Trace

### Upload Flow

**Step 1: File Selection**
- File: `apps/web/app/components/ProfileEdit.tsx`
- Function: `handleFileSelect` (line 48)
- Action: User selects file → Calls `uploadAvatar(user.id, file)`

**Step 2: Upload Request**
- File: `apps/web/lib/avatar-service.ts`
- Function: `uploadAvatar` (line 18)
- Action: POST to `/api/storage/avatar` with FormData
- Authentication: `credentials: 'include'` ✅

**Step 3: Backend Storage Upload**
- File: `apps/api/src/routes/storage.ts`
- Endpoint: POST `/api/storage/avatar` (line 65)
- Action: Uploads to Neon Object Storage bucket `upload`
- Object Key: `avatars/{userId}/{timestamp}.{ext}` ✅

**Step 4: Database Update**
- File: `apps/api/src/routes/storage.ts`
- Query: Line 111-116
```sql
UPDATE nexus.user_profiles
SET avatar_storage_path = $1
WHERE account_id = $2
```
- Status: ✅ Correctly updates `avatar_storage_path` in database

**Step 5: Frontend State Update**
- File: `apps/web/app/components/ProfileEdit.tsx`
- Action: Line 60-61 - Sets local `photoUrl` state
- Problem: Uses temporary URL, not persisted to profile ✅

**Step 6: Save Changes**
- File: `apps/web/app/page.tsx`
- Function: `handleProfileSave` (line 79)
- Action: Calls `updateProfile({ displayName: name })`
- Problem: photoUrl is NOT sent to backend ✅
- Note: This is actually correct - avatar is already saved by upload endpoint

### Refresh Flow (WHERE IT FAILS)

**Step 1: Page Refresh**
- File: `apps/web/app/page.tsx`
- Action: `useEffect` triggers (line 39)
- Calls `getProfile()` → `loadAvatar(user.id)`

**Step 2: Profile Fetch**
- File: `apps/web/lib/backend-profile.ts`
- Function: `getProfile` (line 62)
- Action: GET `/api/v1/profile`
- Backend: `apps/api/src/routes/profile.ts` (line 21)

**Step 3: Backend Profile Query**
- File: `apps/api/src/routes/profile.ts`
- Action: Calls `profileRepo.findByAccountId(accountId)` (line 28)

**Step 4: Repository Query (THE BUG)**
- File: `packages/repositories/src/profile-repository.ts`
- Function: `findByAccountId` (line 42)
- Query: Line 44-45
```sql
SELECT id, account_id, display_name, age_band, locale, timezone,
       created_at, updated_at, deleted_at
FROM nexus.user_profiles
WHERE account_id = $1 AND deleted_at IS NULL
```
- **PROBLEM**: `avatar_storage_path` is NOT selected ❌

**Step 5: Response to Frontend**
- File: `packages/repositories/src/profile-repository.ts`
- Interface: `UserProfile` (line 9-19)
- **PROBLEM**: `avatar_storage_path` is NOT in interface ❌
- Response does NOT include `avatar_storage_path` ❌

**Step 6: Frontend Load Avatar**
- File: `apps/web/lib/avatar-service.ts`
- Function: `loadAvatar` (line 71)
- Action: Line 85 - Tries to parse `profile.avatar_storage_path`
- Result: `avatarStoragePath` is undefined → Returns null ❌

**Step 7: Image Display**
- File: `apps/web/app/page.tsx`
- Action: Line 49-52 - `setProfilePhoto(avatarUrl)` receives null
- Result: No image displayed ❌

---

## Phase 2: Frontend Investigation

**Upload Service**: `apps/web/lib/avatar-service.ts`
- ✅ Upload function correct
- ✅ Uses correct hostname (localhost:4000)
- ✅ Constructs public URL correctly
- ✅ Load avatar function attempts to parse `avatar_storage_path`

**Profile Component**: `apps/web/app/components/ProfileEdit.tsx`
- ✅ File selection works
- ✅ Upload works
- ✅ Preview shows immediately
- ✅ Error handling present

**Main Page**: `apps/web/app/page.tsx`
- ✅ Calls `loadAvatar` on auth change
- ✅ Handles avatar URL from backend
- ❌ Cannot get avatar URL because backend doesn't return it

**Profile Service**: `apps/web/lib/backend-profile.ts`
- ✅ Calls correct endpoint
- ✅ Uses credentials
- ❌ UserProfile interface does not include `avatar_storage_path`

---

## Phase 3: Backend Investigation

**Upload Endpoint**: `apps/api/src/routes/storage.ts`
- ✅ POST `/api/storage/avatar` works
- ✅ Uploads to Neon Storage
- ✅ Updates `user_profiles.avatar_storage_path` correctly
- ✅ Returns storage key and metadata

**Profile Endpoint**: `apps/api/src/routes/profile.ts`
- ✅ GET `/api/v1/profile` calls repository
- ✅ Authentication works
- ❌ Repository does not return `avatar_storage_path`

**Profile Repository**: `packages/repositories/src/profile-repository.ts`
- ❌ SELECT query missing `avatar_storage_path` (line 44-45)
- ❌ UserProfile interface missing `avatar_storage_path` (line 9-19)
- ❌ CREATE query missing `avatar_storage_path` (line 59-62)
- ❌ UPDATE query missing `avatar_storage_path` (line 107-112)

---

## Phase 4: Neon Storage & PostgreSQL Verification

**Storage**: Neon Object Storage
- ✅ Bucket: `upload`
- ✅ Upload works
- ✅ Image is persisted in storage

**PostgreSQL**: Neon PostgreSQL
- ✅ Table: `nexus.user_profiles`
- ✅ Column: `avatar_storage_path` varchar(500) exists
- ✅ Upload endpoint updates column correctly
- ❌ Profile repository does not read the column

---

## Confirmed Root Cause

**Root Cause**: The `ProfileRepository` does not include `avatar_storage_path` in:
1. SELECT queries (line 44-45)
2. UserProfile interface (line 9-19)
3. CREATE query RETURNING clause (line 61-62)
4. UPDATE query RETURNING clause (line 111-112)

**Impact**: Even though the avatar upload correctly saves the storage path to the database, the profile API never returns it to the frontend. After page refresh, the frontend cannot retrieve the saved avatar reference, so the image disappears.

**Evidence**:
- Storage endpoint successfully updates `avatar_storage_path` (storage.ts line 111-116)
- Profile repository does not SELECT `avatar_storage_path` (profile-repository.ts line 44-45)
- Profile interface does not include `avatar_storage_path` (profile-repository.ts line 9-19)
- Frontend `loadAvatar` depends on `profile.avatar_storage_path` (avatar-service.ts line 85)

---

## Proposed Repair

**Files to Modify**:
1. `packages/repositories/src/profile-repository.ts`
   - Add `avatar_storage_path` to UserProfile interface
   - Add `avatar_storage_path` to SELECT query in `findByAccountId`
   - Add `avatar_storage_path` to RETURNING clause in `create`
   - Add `avatar_storage_path` to RETURNING clause in `update`

2. `apps/web/lib/backend-profile.ts`
   - Add `avatar_storage_path` to UserProfile interface
   - Add `avatar_storage_path` to CreateProfileInput and UpdateProfileInput (optional, not needed)

**Why This Fix**:
- Minimal change - only adds missing column to existing queries
- Preserves existing architecture
- Does not change storage or authentication
- Does not create duplicate systems
- Fixes the exact root cause

---

## Verification Plan

After fix:
1. Upload profile picture
2. Verify image appears immediately
3. Refresh page
4. Verify image persists
5. Log out and log in
6. Verify image persists
7. Test mobile and desktop
8. Verify database contains `avatar_storage_path`
9. Verify profile API returns `avatar_storage_path`

---

## STOP

Root cause identified. Ready for repair.
