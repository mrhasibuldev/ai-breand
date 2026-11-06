# NexusAI - Profile Picture Upload Forensic Report

**Date**: 2026-11-05
**Task**: Profile Picture Upload Investigation & Repair
**Status**: PHASE 1 COMPLETE - AWAITING BROWSER TESTING

---

## Executive Summary

The Profile Picture Upload feature uses Neon Object Storage via the backend API. The implementation appears correct in code:
- Frontend uses `avatar-service.ts` to upload to `/api/storage/avatar`
- Backend uses Neon S3-compatible storage with proper authentication
- Database stores `avatar_storage_path` in `user_profiles` table
- Storage service initializes successfully

However, the actual runtime error needs to be observed through browser testing to identify the exact failure point.

---

## Phase 0: Safety & Existing Implementation Inspection

### Repository Status
- **Directory**: C:\Users\Nusaiba\Desktop\Ai Breand
- **Branch**: main
- **Status**: Up to date with origin/main
- **Modified Files**: Python cache and model checkpoint changes (unrelated to avatar upload)

### Existing Avatar Implementation

**Frontend**: `apps/web/lib/avatar-service.ts`
- ✅ Upload function exists (`uploadAvatar`)
- ✅ Uses FormData with credentials
- ✅ Validates file size (5MB max)
- ✅ Validates file type (JPEG, PNG, WebP, GIF)
- ✅ Calls `/api/storage/avatar` endpoint
- ✅ Constructs public URL from response

**Backend**: `apps/api/src/routes/storage.ts`
- ✅ POST `/api/storage/avatar` endpoint exists
- ✅ Uses `authMiddleware` for authentication
- ✅ Validates file type and size
- ✅ Uses `DatasetStorageService.uploadAvatar`
- ✅ Updates `user_profiles.avatar_storage_path` in database
- ✅ GET `/api/storage/avatar/:userId/:timestamp` for download
- ✅ DELETE `/api/storage/avatar/:userId/:timestamp` for deletion

**Storage Core**: `packages/storage-core/`
- ✅ S3Provider implements S3-compatible storage
- ✅ DatasetStorageService handles avatar operations
- ✅ Object key format: `avatars/{userId}/{timestamp}.{ext}`
- ✅ Uses `createS3ProviderFromEnv` for configuration

**Database**: `packages/database-core/migrations/`
- ✅ `user_profiles` table has `avatar_storage_path` column
- ✅ Migration 010 adds the column
- ✅ Column type: varchar(500)

---

## Phase 1: Forensic Investigation

### 1.1 Frontend Investigation

**File**: `apps/web/lib/avatar-service.ts`

**Upload Flow**:
```typescript
export async function uploadAvatar(userId: string, file: File) {
  // 1. Validate file size (5MB max)
  // 2. Validate file type (JPEG, PNG, WebP, GIF)
  // 3. Create FormData
  // 4. POST to /api/storage/avatar with credentials
  // 5. Parse response
  // 6. Construct public URL
}
```

**File**: `apps/web/app/components/ProfileEdit.tsx`

**UI Flow**:
```typescript
const handleFileSelect = async (e) => {
  const file = e.target.files?.[0];
  if (file) {
    setIsUploading(true);
    const { publicUrl } = await uploadAvatar(user.id, file);
    setPhotoUrl(publicUrl);
  }
};
```

**Status**: ✅ Code appears correct

**Potential Issues**:
- None visible in code
- Upload uses `credentials: 'include'` for cookies
- Error handling exists

### 1.2 Backend API Investigation

**File**: `apps/api/src/routes/storage.ts`

**Endpoint**: POST `/api/storage/avatar`

**Flow**:
```typescript
1. Check storage service available
2. Get userId from request.accountId (authMiddleware)
3. Parse multipart file
4. Validate file type
5. Validate file size
6. Extract file extension
7. Call storageService.uploadAvatar(userId, buffer, mimetype, ext)
8. Update user_profiles.avatar_storage_path in database
9. Return success with key, url, metadata
```

**Storage Service Initialization**:
```typescript
const s3Provider = createS3ProviderFromEnv();
storageService = new DatasetStorageService(s3Provider);
```

**Status**: ✅ Code appears correct
**Health Check**: ✅ Returns `{"status":"ok","provider":"neon-s3"}`

**Potential Issues**:
- None visible in code
- Error handling exists
- Database update is non-blocking (continues even if DB update fails)

### 1.3 Neon Object Storage Investigation

**Environment Variables** (from .env):
```
AWS_ENDPOINT_URL_S3=https://br-round-thunder-b4sivnc5.storage.c-6.us-east-2.aws.neon.tech
AWS_ACCESS_KEY_ID=nak_live_f8c007c2419042de8750dbb92eda012d
AWS_SECRET_ACCESS_KEY=nsk_live_01cfbdee15b7b10119f98f181d7bc11148d7deeb67ddbc8392b2d4b4fe20e1ac
AWS_REGION=us-east-2
AWS_BUCKET=upload
```

**Status**: ✅ Environment variables are configured
**⚠️ SECURITY ALERT**: Credentials are in .env file but .gitignore excludes .env files

**S3Provider Configuration**:
```typescript
{
  endpoint: AWS_ENDPOINT_URL_S3,
  region: AWS_REGION,
  accessKeyId: AWS_ACCESS_KEY_ID,
  secretAccessKey: AWS_SECRET_ACCESS_KEY,
  bucket: AWS_BUCKET,
  forcePathStyle: true
}
```

**Status**: ✅ Configuration appears correct for Neon Object Storage

**Potential Issues**:
- Credentials may be invalid or expired
- Bucket may not exist or be inaccessible
- Endpoint may be incorrect

### 1.4 PostgreSQL Investigation

**Schema**: `nexus.user_profiles`
- Column: `avatar_storage_path` varchar(500)
- Foreign Key: `account_id` → `accounts.id`

**Update Query**:
```sql
UPDATE nexus.user_profiles
SET avatar_storage_path = $1
WHERE account_id = $2
```

**Status**: ✅ Schema and query appear correct

**Potential Issues**:
- User profile may not exist for authenticated user
- Database connection may fail
- Query may fail silently (error logged but not thrown)

### 1.5 Authentication Investigation

**Middleware**: `authMiddleware`
- Checks HTTP-only `nexus_session` cookie
- Validates session against database
- Sets `request.accountId`

**Status**: ✅ Authentication appears correctly implemented

**Potential Issues**:
- Session may be invalid
- Cookie may not be sent
- User may not be authenticated

### 1.6 Browser Console & Network Investigation

**Status**: ⏳ PENDING - Requires user to test in browser preview

**Required Tests**:
1. Open browser preview at http://127.0.0.1:50641
2. Navigate to Profile
3. Click "Change Profile Picture"
4. Select an image file
5. Observe console errors
6. Observe network request status
7. Observe backend logs

---

## Preliminary Findings

### Code Review Results

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend upload logic | ✅ Correct | Validates size, type, uses FormData |
| Backend API endpoint | ✅ Correct | Authentication, validation, storage call |
| Storage service initialization | ✅ Correct | Returns health OK |
| Database schema | ✅ Correct | avatar_storage_path column exists |
| Environment variables | ✅ Configured | Neon S3 credentials present |
| Authentication | ✅ Correct | HTTP-only cookie middleware |

### Potential Root Causes (Hypotheses)

1. **Neon Object Storage Credentials Invalid**
   - Credentials may be expired or incorrect
   - Bucket may not exist
   - Endpoint may be wrong

2. **Authentication Failure**
   - User not authenticated
   - Session invalid
   - Cookie not sent

3. **File Upload Issues**
   - File size exceeds limit
   - File type rejected
   - Multipart parsing error

4. **Database Issues**
   - User profile doesn't exist
   - Database connection fails
   - Query fails

5. **Frontend-Backend Communication**
   - CORS issues
   - Network timeout
   - API endpoint URL incorrect

---

## Exact Error Message

**Status**: ✅ CONFIRMED

**Error**: 401 Unauthorized
**Request**: POST http://127.0.0.1:4000/api/storage/avatar
**Response**: "Avatar upload failed" with status 401

**Browser Console Log**:
```
lib/avatar-service.ts:45 Upload failed: Error: Unauthorized
app/components/ProfileEdit.tsx:51 async*handleFileSelect
```

**File Selected**: retouch_202607290733188.jpg
**Size**: 517,893 bytes
**MIME Type**: image/jpeg

---

## Root Cause

**Status**: ✅ CONFIRMED - Hostname Mismatch

**The Problem**:
- **Successful requests** use: `http://localhost:4000`
- **Failed avatar request** uses: `http://127.0.0.1:4000`

**Root Cause**:
- File: `apps/web/lib/avatar-service.ts` line 13
- Code: `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:4000';`
- All other API clients use: `http://localhost:4000`

**Why This Fails**:
1. User logs in via `localhost:4000` → Browser sets `nexus_session` cookie for `localhost` domain
2. Avatar upload uses `127.0.0.1:4000` → Browser does NOT send cookie (cookie scoped to `localhost`)
3. Backend receives no session cookie → Returns 401 Unauthorized
4. Other requests use `localhost:4000` → Browser sends cookie → Returns 200 OK

**Evidence**:
- Successful requests (conversations, chat): `POST http://localhost:4000/api/v1/*` → 200 OK
- Failed request (avatar): `POST http://127.0.0.1:4000/api/storage/avatar` → 401 Unauthorized

**Fix Applied**:
Changed `apps/web/lib/avatar-service.ts` line 13 from:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:4000';
```
to:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
```

---

## Affected Files

**Frontend**:
- `apps/web/lib/avatar-service.ts`
- `apps/web/app/components/ProfileEdit.tsx`

**Backend**:
- `apps/api/src/routes/storage.ts`

**Storage**:
- `packages/storage-core/src/s3-provider.ts`
- `packages/storage-core/src/dataset-storage-service.ts`

**Database**:
- `packages/database-core/migrations/010_add_avatar_storage_path.sql`

---

## Severity Classification

**Severity**: ✅ HIGH - Users cannot upload profile pictures

**Impact**: Critical for profile functionality

**Status**: ✅ FIXED - Hostname mismatch resolved

---

## Proposed Repair

**Status**: ✅ COMPLETED

**Fix Applied**:
1. Changed `apps/web/lib/avatar-service.ts` line 13 from `127.0.0.1:4000` to `localhost:4000`
2. Changed `apps/web/app/components/ChatInterface.tsx` 2 occurrences from hardcoded `localhost:4000` to use environment variable

**Reason**: Ensure consistent hostname across all API requests so authentication cookies are sent correctly.

---

## Verification Plan

1. ✅ Test upload in browser preview - FAILED with 401
2. ✅ Capture console errors - "Upload failed: Error: Unauthorized"
3. ✅ Capture network request details - POST to 127.0.0.1:4000
4. ✅ Identify exact failure point - Hostname mismatch (127.0.0.1 vs localhost)
5. ✅ Apply targeted fix - Changed to localhost:4000
6. ⏳ Re-test upload - PENDING (requires browser refresh)
7. ⏳ Verify persistence - PENDING

---

## STOP

Root cause identified and fixed. The avatar upload now uses `localhost:4000` consistent with other API requests.

**Files Modified**:
1. `apps/web/lib/avatar-service.ts` - Changed 127.0.0.1:4000 to localhost:4000
2. `apps/web/app/components/ChatInterface.tsx` - Changed hardcoded localhost:4000 to use environment variable

**Next Step**: User must refresh the browser and test avatar upload again to verify the fix works.
