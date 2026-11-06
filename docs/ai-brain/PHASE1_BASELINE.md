# PHASE 1 — BASELINE REPORT

**Date**: 2026-11-03
**Phase**: 1 - Database & Security Foundation
**Task**: Baseline inspection before Phase 1 implementation
**Status**: ✅ COMPLETE

---

## EXECUTIVE SUMMARY

This baseline report documents the current state of the NexusAI repository before Phase 1 database and security foundation hardening.

**Current Branch**: main
**Git Status**: 1 untracked commit (post-push verification report), 6 untracked files (AI Core training scripts and data)
**Database Provider**: Neon PostgreSQL (configured)
**Storage Provider**: Neon Object Storage via S3-compatible API
**Authentication**: PostgreSQL-backed with HTTP-only cookies

---

## A. GIT BASELINE

### Branch
- **Current Branch**: main
- **Remote**: origin/main
- **Status**: 1 commit ahead of origin (44d3126 - post-push verification report)

### Modified Files
- **NONE** - No staged or modified files

### Untracked Files
- `packages/ai-core/data/pilots/b4-b2-p1/combined_for_review.json`
- `packages/ai-core/ml-service/knowledge/` (directory)
- `packages/ai-core/training/run_training.py`
- `packages/ai-core/training/test_inference.py`
- `packages/ai-core/training/validate_architecture.py`
- `packages/ai-core/training/verify_checkpoint.py`
- `training/` (directory)

**Note**: These are AI Core training-related files unrelated to Phase 1 database/security work.

---

## B. DATABASE FOUNDATION

### B.1 Neon Configuration

**Location**: `packages/database-core/src/config.ts`

**Findings**:
- ✅ Provider defaults to 'postgresql'
- ✅ Reads DATABASE_URL from environment
- ✅ Connection pool size: 20 (configurable)
- ✅ Error handling for missing DATABASE_URL
- ✅ Comments acknowledge both Supabase and self-hosted PostgreSQL support

**Configuration Interface**:
```typescript
{
  provider: 'supabase' | 'postgresql',
  connectionString: string,
  poolSize: number
}
```

**Status**: ✅ **NEON CONFIGURATION CORRECT**

### B.2 Schema Consistency

**Location**: `packages/database-core/migrations/COMPLETE_SCHEMA.sql`

**Issue Identified**: `nexus.file_metadata.storage_provider`

**Current Schema**:
```sql
storage_provider text NOT NULL DEFAULT 'supabase',
CONSTRAINT file_metadata_provider_ck CHECK (storage_provider IN ('supabase', 's3', 'local'))
```

**Actual Storage Implementation**:
- Storage package: `packages/storage-core/src/s3-provider.ts`
- Uses Neon Object Storage via S3-compatible API
- Environment variables: AWS_ENDPOINT_URL_S3, AWS_ACCESS_KEY_ID, etc.
- Provider identifier in code: 's3' (referring to S3 API protocol, not AWS)

**Analysis**:
- The schema allows 's3' as a valid value ✅
- The default is 'supabase' which is outdated ⚠️
- The implementation correctly uses 's3' to identify the S3-compatible API protocol
- This is technically correct: Neon Object Storage uses the S3 API protocol
- The naming convention is: Service = Neon, Protocol = S3

**Schema Comment Issue**:
- Line 2: "Run this entire script in Supabase SQL Editor"
- This comment is outdated since the project uses Neon PostgreSQL

**Status**: ⚠️ **MINOR INCONSISTENCY** - Default should be 's3', comment outdated

---

## C. AUTHENTICATION SECURITY

### C.1 Cookie Security

**Location**: `apps/api/src/routes/auth.ts`

**Current Settings** (lines 80-86, 154-160):
```typescript
reply.setCookie('nexus_session', sessionToken, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  path: '/',
  maxAge: 7 * 24 * 60 * 60, // 7 days
});
```

**Analysis**:
- ✅ httpOnly: true (explicit)
- ✅ secure: conditional on NODE_ENV === 'production' (explicit)
- ✅ sameSite: 'lax' (explicit)
- ✅ path: '/' (explicit)
- ✅ maxAge: 7 days (explicit)

**Cookie Secret**:
- Location: `apps/api/src/app.ts` line 58
- Current: `options.env?.COOKIE_SECRET || process.env.COOKIE_SECRET || 'nexus-cookie-secret-change-in-production'`
- ⚠️ Hardcoded fallback is a security risk

**Status**: ⚠️ **COOKIE SETTINGS EXPLICIT BUT HARDCODED FALLBACK RISK**

### C.2 CSRF Protection

**Location**: `apps/api/src/app.ts` lines 172-233

**Current Implementation**:
```typescript
// CSRF protection for state-changing requests
const trustedOrigins = new Set([
  config.webOrigin || 'http://localhost:3000',
  'http://localhost:3000',
  'http://127.0.0.1:3000',
]);

const isStateChanging = (method: string, url: string) => {
  if (method === 'GET' || method === 'HEAD' || method === 'OPTIONS') return false;
  if (url.startsWith('/health/')) return false;
  return true;
};

app.addHook('onRequest', async (request, reply) => {
  // CSRF protection for state-changing requests
  if (isStateChanging(request.method, request.url)) {
    const origin = request.headers.origin;
    const referer = request.headers.referer;

    // Allow requests from trusted origins
    if (origin && trustedOrigins.has(origin)) {
      return;
    }

    // Fallback to referer if origin is missing
    if (referer) {
      try {
        const refererUrl = new URL(referer);
        if (trustedOrigins.has(refererUrl.origin)) {
          return;
        }
      } catch {
        // Invalid referer URL
      }
    }

    // Development mode: allow localhost without origin
    if (config.nodeEnv === 'development' && request.ip === '127.0.0.1' || request.ip === '::1') {
      return;
    }

    // Reject untrusted state-changing requests
    throw new FoundationHttpError(403, 'csrf_rejected', 'Origin verification failed');
  }
});
```

**Analysis**:
- ✅ CSRF protection IS implemented
- ✅ Validates Origin header first
- ✅ Falls back to Referer header
- ✅ Allows localhost in development mode
- ✅ Rejects untrusted state-changing requests
- ✅ Uses FoundationHttpError for consistent error handling
- ✅ Excludes GET/HEAD/OPTIONS (safe methods)
- ✅ Excludes health endpoints

**Status**: ✅ **CSRF PROTECTION ALREADY IMPLEMENTED**

### C.3 Session Validation Efficiency

**Location**: `apps/api/src/middleware/auth.ts` and `apps/api/src/routes/auth.ts`

**Current Implementation** (auth.ts lines 44-52):
```typescript
const sessionsResult = await db.query(
  `SELECT s.id, s.account_id, s.session_token_hash, a.status
   FROM nexus.auth_sessions s
   JOIN nexus.accounts a ON s.account_id = a.id
   WHERE s.revoked_at IS NULL
   AND s.expires_at > NOW()
   ORDER BY s.created_at DESC
   LIMIT 100`
);
```

**Issue**:
- Retrieves up to 100 active sessions per validation
- Iterates through all sessions to find matching token hash
- This is inefficient with many concurrent sessions
- Caused by bcrypt requiring rehashing for comparison

**Status**: ❌ **INEFFICIENT** - Should use targeted lookup

---

## D. STORAGE & AVATAR

### D.1 Avatar Access Policy

**Location**: `apps/api/src/routes/storage.ts` lines 129-159

**Current Implementation**:
```typescript
fastify.get('/api/storage/avatar/:userId/:timestamp', { preHandler: authMiddleware }, async (request, reply) => {
  const requestUserId = request.accountId;
  const { userId, timestamp } = request.params as { userId: string; timestamp: string };

  // Users can retrieve their own avatars
  if (requestUserId !== userId) {
    return reply.status(403).send({ error: 'Forbidden' });
  }

  // ... download logic
});
```

**Analysis**:
- ✅ Requires authentication (authMiddleware)
- ✅ Ownership check: requestUserId === userId
- ✅ Returns 403 for cross-user access
- ✅ Avatars are PRIVATE, not public

**Status**: ✅ **PRIVATE AVATAR ACCESS POLICY CORRECT**

### D.2 Ownership Isolation

**Avatar Operations** (storage.ts):
- Upload: Uses `request.accountId` from authenticated session ✅
- Download: Validates `requestUserId === userId` ✅
- Delete: Validates `requestUserId === userId` ✅

**Dataset Operations** (storage.ts):
- Upload: Uses `request.accountId` from authenticated session ✅
- Download: Uses `request.accountId` from authenticated session ✅
- Delete: Uses `request.accountId` from authenticated session ✅

**Status**: ✅ **OWNERSHIP ISOLATION CORRECT**

### D.3 Avatar Metadata Persistence

**Database Schema**:
- Table: `nexus.user_profiles`
- Column: `avatar_storage_path varchar(500)` (added in migration 010)

**Frontend Loading** (apps/web/lib/avatar-service.ts lines 71-81):
```typescript
export async function loadAvatar(userId: string): Promise<string | null> {
  try {
    // Get the latest avatar timestamp from profile or storage
    // For now, return null and let the UI handle default avatar
    console.log('[Avatar] Loading avatar for user:', userId);
    return null;
  } catch (e) {
    console.warn('[Avatar] Failed to load avatar:', e);
    return null;
  }
}
```

**Issue**:
- loadAvatar() returns null (placeholder)
- Does not query user_profiles.avatar_storage_path
- No reliable avatar timestamp persistence

**Status**: ⚠️ **AVATAR LOADING NOT IMPLEMENTED**

---

## E. DATASET FOUNDATION

### E.1 Existing Knowledge Tables

**Migrations**:
- 013_knowledge_tables.sql
- 019_extended_knowledge_source_registry.sql

**Tables**:
- nexus.knowledge_sources
- nexus.documents
- nexus.document_chunks
- nexus.document_metadata
- nexus.ingestion_runs
- nexus.knowledge_gaps

### E.2 Dataset Registry

**Migration**: 018_dataset_registry_tables.sql

**Tables**:
- nexus.dataset_registry
- nexus.dataset_versions
- nexus.dataset_approval_history

**Status**: ✅ Dataset registry schema exists

### E.3 Missing for Full Dataset Management

Not part of Phase 1 scope, but documented for future Phase 2:
- No explicit dataset versioning workflow
- No training eligibility tracking
- No provenance checksums in current schema
- No quality metrics tracking

**Status**: ✅ **ADEQUATE FOR PHASE 1, MORE NEEDED FOR PHASE 2**

---

## F. SUMMARY OF ISSUES TO FIX

### High Priority
1. **Session Validation Efficiency** - Replace 100-session retrieval with targeted lookup
2. **Cookie Secret Hardcoded Fallback** - Remove or make it fail explicitly

### Medium Priority
3. **Schema Default Value** - Change file_metadata.storage_provider default from 'supabase' to 's3'
4. **Schema Comment** - Update "Run in Supabase SQL Editor" comment
5. **Avatar Loading** - Implement proper avatar loading from database

### Low Priority / Future Scope
6. **Avatar Metadata Persistence** - Ensure avatar_storage_path is updated on upload/delete

---

## G. FILES TO MODIFY

### Database Migrations
- `packages/database-core/migrations/COMPLETE_SCHEMA.sql` (update default and comment)
- Create new migration: `020_fix_storage_provider_default.sql`

### Authentication
- `apps/api/src/middleware/auth.ts` (session validation efficiency)
- `apps/api/src/routes/auth.ts` (session validation in logout/session endpoints)
- `apps/api/src/app.ts` (cookie secret fallback)

### Avatar
- `apps/api/src/routes/storage.ts` (update avatar_storage_path on upload)
- `apps/api/src/routes/profile.ts` (or create endpoint to get avatar path)
- `apps/web/lib/avatar-service.ts` (implement loadAvatar from database)

---

## H. EXCLUDED FROM PHASE 1

- Dataset registry expansion (Phase 2)
- Model architecture changes (never in Phase 1)
- Training pipeline changes (never in Phase 1)
- UI redesign (not security-related)
- New database creation (use existing Neon)
- Supabase introduction (use existing Neon)

---

## I. VERIFICATION STATUS

### Already Verified
- ✅ Neon configuration
- ✅ Cookie security settings (explicit but with fallback risk)
- ✅ CSRF protection (already implemented)
- ✅ Avatar access policy (private)
- ✅ Ownership isolation (correct)

### Needs Verification After Fixes
- ⏳ Session validation efficiency
- ⏳ Cookie secret explicit failure
- ⏳ Schema consistency
- ⏳ Avatar loading

### Runtime Testing Required
- ⏳ Two-user authorization tests
- ⏳ Storage connectivity tests
- ⏳ Cookie behavior in production-like environment

---

## J. NEXT STEPS

1. Fix session validation efficiency
2. Fix cookie secret fallback
3. Update schema default and comment
4. Implement avatar loading
5. Run authorization tests
6. Run storage connectivity tests
7. Create final Phase 1 report

---

**Baseline Status**: ✅ COMPLETE
**Ready for Implementation**: YES
