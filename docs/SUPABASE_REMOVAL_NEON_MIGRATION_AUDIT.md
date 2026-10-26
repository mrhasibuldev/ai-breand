# SUPABASE REMOVAL & NEON MIGRATION AUDIT

**Date:** 2025-01-15
**Phase:** Phase Zero - Repository Audit
**Objective:** Complete forensic audit of Supabase dependencies and migration readiness

---

## EXECUTIVE SUMMARY

This audit documents all Supabase dependencies in the NexusAI project to enable a complete migration to Neon PostgreSQL with self-managed authentication and storage. The audit identifies:

- **Frontend:** Direct Supabase client usage for Auth, Storage, and database access
- **Backend:** Provider-independent PostgreSQL layer already exists (can use Neon)
- **Authentication:** Supabase Auth used in frontend, not backend
- **Storage:** Supabase Storage used in frontend with localStorage fallback
- **Database:** PostgreSQL with `nexus` schema, migrations exist, RLS uses Supabase-specific functions
- **Chat:** Guest mode bypasses Supabase, authenticated mode uses Supabase for persistence
- **AI Service:** Python FastAPI, independent of Supabase

**Key Finding:** The database layer (`packages/database-core`) is already provider-independent and can switch to Neon with only a connection string change. However, the frontend has extensive Supabase dependencies that require replacement.

---

## 1. MONOREPO STRUCTURE

### 1.1 Workspace Layout

```
C:\Users\Nusaiba\Desktop\Ai Breand
├── apps/
│   ├── web/          # Next.js 15 frontend (Supabase dependencies)
│   ├── api/          # Fastify backend (provider-independent DB)
│   └── worker/       # Background worker
├── packages/
│   ├── database-core/ # PostgreSQL client (already provider-independent)
│   ├── repositories/ # Data access layer (uses database-core)
│   ├── auth-core/    # Authentication interfaces (unimplemented)
│   ├── app-core/     # Domain models
│   ├── ai-core/      # AI/ML package (Python + TypeScript bridge)
│   ├── config/       # Runtime configuration
│   └── safety-core/  # Content safety
├── tests/            # Test files
└── docs/             # Documentation
```

### 1.2 Package Manager

- **Package Manager:** pnpm workspace
- **Version:** 11.19.0
- **Node Engine:** >=22 <25
- **Total Packages:** 39 packages across 17 projects

### 1.3 Verified Dependencies

**Root:**
- dotenv@18.0.8

**@nexusai/web:**
- @supabase/supabase-js@2.117.3 ← **REMOVE**
- next@15.5.24
- react@19.2.8
- lucide-react@1.55.0

**@nexusai/api:**
- fastify@5.12.5
- @nexusai/database-core (provider-independent)
- @nexusai/repositories (uses database-core)
- No Supabase dependencies

**@nexusai/database-core:**
- pg@8.23.1 (PostgreSQL driver)
- Already provider-independent

---

## 2. SUPABASE DEPENDENCIES

### 2.1 Package Dependencies

**Files with Supabase package imports:**
- `apps/web/package.json` - Contains `@supabase/supabase-js@2.117.3`

**Action Required:** Remove `@supabase/supabase-js` from `apps/web/package.json`

### 2.2 Supabase Client Usage

**Frontend Supabase Client:**
- `apps/web/lib/supabase-client.ts` - Main Supabase client initialization
  - Creates Supabase client using `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - Exports `supabase` and `supabaseStorage` instances
  - Contains helper functions: `getCurrentUserSafe()`, `signOut()`, `isSupabaseConfigured()`

**Files importing Supabase client:**
1. `apps/web/lib/conversation-service.ts` - Direct database queries via Supabase
2. `apps/web/lib/message-service.ts` - Direct database queries via Supabase
3. `apps/web/lib/profile-service.ts` - Direct database queries via Supabase
4. `apps/web/lib/avatar-service.ts` - Supabase Storage usage
5. `apps/web/app/components/AuthContext.tsx` - Supabase Auth state management
6. `apps/web/app/components/useConversationManager.ts` - Conversation persistence via Supabase
7. `apps/web/app/components/test-auth-debug.tsx` - Debug component
8. `apps/web/app/api/check-supabase/route.ts` - Supabase health check API route
9. `apps/web/lib/direct-supabase-check.ts` - Supabase diagnostics
10. `apps/web/lib/supabase-diagnostics.ts` - Supabase diagnostics

**Action Required:** Replace all Supabase client usage with backend API calls

### 2.3 Supabase Environment Variables

**Current `.env.example`:**
```bash
# Database Configuration
DATABASE_PROVIDER=supabase
DATABASE_URL=
DATABASE_POOL_SIZE=20

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

**Frontend Environment Variables (public):**
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key

**Backend Environment Variables (private):**
- `DATABASE_URL` - PostgreSQL connection string (already generic)
- `DATABASE_PROVIDER` - Currently 'supabase', can be 'postgresql'
- `SUPABASE_SERVICE_ROLE_KEY` - Not used in current code

**Action Required:**
- Remove `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- Keep `DATABASE_URL` (will point to Neon)
- Change `DATABASE_PROVIDER` to 'postgresql'

### 2.4 Supabase Usage Patterns

**Pattern 1: Direct Database Access (VIOLATION)**
```typescript
// apps/web/lib/conversation-service.ts
const { data } = await supabase
  .schema('nexus')
  .from('conversations')
  .select('*')
  .eq('account_id', accountId);
```

**Impact:** Frontend bypasses backend API, violates architecture

**Pattern 2: Supabase Auth**
```typescript
// apps/web/app/components/AuthContext.tsx
const { data: { session } } = await client.auth.getSession();
```

**Impact:** Authentication depends on Supabase Auth service

**Pattern 3: Supabase Storage**
```typescript
// apps/web/lib/avatar-service.ts
const { data } = await supabaseStorage.storage
  .from('avatars')
  .upload(filePath, file);
```

**Impact:** File storage depends on Supabase Storage

**Pattern 4: RLS Policies**
```sql
-- packages/database-core/migrations/RLS_POLICIES.sql
CREATE POLICY ... USING (auth.uid() = account_id);
```

**Impact:** RLS uses Supabase-specific `auth.uid()` function

---

## 3. DATABASE LAYER AUDIT

### 3.1 Database Core Package

**Location:** `packages/database-core/`

**Key Files:**
- `src/config.ts` - Configuration reader (provider-independent)
- `src/index.ts` - Client factory (always returns PostgresClient)
- `src/postgres-client.ts` - PostgreSQL client implementation
- `src/migration-loader.ts` - Migration file loader
- `src/migration-runner.ts` - Migration execution
- `migrations/*.sql` - SQL migration files

**Current Configuration:**
```typescript
export interface DatabaseConfig {
  readonly provider: 'supabase' | 'postgresql';
  readonly connectionString: string;
  readonly poolSize: number;
}
```

**Architecture Decision (Verified):**
> "For database connectivity, we use PostgreSQL connection strings for both Supabase and self-hosted. This makes migration from Supabase to self-hosted PostgreSQL straightforward (just change connection string)."

**Impact:** Database layer is ALREADY provider-independent. Can switch to Neon with only:
1. Change `DATABASE_PROVIDER` to 'postgresql'
2. Change `DATABASE_URL` to Neon connection string
3. No code changes required in database-core

### 3.2 Migrations

**Migration Files:**
1. `001_bootstrap.sql` - Create schema, extensions, functions
2. `002_core_identity.sql` - accounts, auth_sessions tables
3. `003_user_profiles.sql` - user_profiles table
4. `004_conversations_messages.sql` - conversations, messages tables
5. `005_memory_records.sql` - memory_records table
6. `006_consent_records.sql` - consent_records table
7. `007_notification_preferences.sql` - notification_preferences table
8. `008_library_items.sql` - library_items table
9. `010_add_avatar_storage_path.sql` - Add avatar_storage_path column
10. `011_create_g_media_table.sql` - g_media table
11. `012_g_media_rls_policies.sql` - RLS for g_media
12. `013_knowledge_tables.sql` - Knowledge documents/chunks
13. `014_fix_conversations_account_id.sql` - Fix account_id column
14. `015_grant_nexus_api_access.sql` - Grant permissions
15. `COMPLETE_SCHEMA.sql` - Consolidated schema (Supabase-oriented)
16. `RLS_POLICIES.sql` - Supabase-specific RLS policies

**Total:** 16 SQL files, 1,350 lines

**Schema:** `nexus` (custom schema, not Supabase-specific)

**RLS Policy Issue:**
```sql
-- Uses Supabase-specific function
CREATE POLICY ... USING (auth.uid() = account_id);
```

**Impact:** RLS policies will not work with Neon (no `auth.uid()` function). Need application-level authorization.

### 3.3 Repositories

**Location:** `packages/repositories/`

**Repository Classes:**
- `ProfileRepository` - Profile CRUD
- `ConversationRepository` - Conversation CRUD
- `MessageRepository` - Message CRUD
- `MemoryRepository` - Memory CRUD

**Current Usage:**
- Backend API routes use these repositories (`apps/api/src/routes/*.ts`)
- Frontend does NOT use these repositories (bypasses API)

**Impact:** Repositories are already compatible with Neon. Frontend must be changed to use API routes instead of direct Supabase access.

### 3.4 Backend API Database Integration

**Current Implementation:**
```typescript
// apps/api/src/app.ts
if (process.env.DATABASE_URL) {
  Promise.all([
    import('./routes/profile.js'),
    import('./routes/conversations.js'),
  ]);
}
```

**Issue:** Database routes only load if `DATABASE_URL` is set

**Authentication Issue:**
```typescript
// apps/api/src/routes/profile.ts
const accountId = request.headers['x-account-id'] as string;
```

**Security Issue:** Uses untrusted header `x-account-id` for identity. No real authentication in backend API.

**Impact:** Backend needs authentication implementation before database routes can be used securely.

---

## 4. AUTHENTICATION AUDIT

### 4.1 Current Authentication Implementation

**Frontend Authentication:**
- **Provider:** Supabase Auth
- **Location:** `apps/web/app/components/AuthContext.tsx`
- **Method:** Supabase JavaScript SDK
- **Session Storage:** Supabase handles session management
- **Session Restoration:** `client.auth.getSession()` on mount

**Backend Authentication:**
- **Provider:** DevAuthService (development-only, in-memory)
- **Location:** `apps/api/src/app.ts`
- **Method:** HTTP-only cookies with session tokens
- **Issue:** Production disabled (throws error in production mode)

**Auth-Core Package:**
- **Location:** `packages/auth-core/`
- **Status:** Interfaces only, no implementation
- **Adapters:** `UnconfiguredIdentityAdapter` (throws error)

### 4.2 Authentication Flow

**Current Flow (Supabase):**
```
User → Frontend (Supabase Auth) → Supabase Auth Service
                          ↓
                    Supabase Session
                          ↓
           Frontend uses session for database access
```

**Target Flow (Self-Managed):**
```
User → Frontend → Backend API (Custom Auth) → Neon
                          ↓
                    HTTP-only Cookie
                          ↓
           Backend validates session, returns data
```

### 4.3 Auth Dependencies

**Supabase Auth Usage:**
- `apps/web/app/components/AuthContext.tsx` - Session management
- `apps/web/lib/supabase-client.ts` - Auth client initialization
- `apps/web/app/components/useConversationManager.ts` - Auth check before operations

**Action Required:** Implement self-managed authentication in backend, replace Supabase Auth in frontend.

---

## 5. STORAGE AUDIT

### 5.1 Current Storage Implementation

**Provider:** Supabase Storage

**Location:** `apps/web/lib/avatar-service.ts`

**Implementation:**
- Upload to Supabase Storage bucket 'avatars'
- Public URL generation via Supabase Storage API
- localStorage fallback for missing infrastructure

**Fallback:**
- If Supabase Storage unavailable, stores images as Data URLs in localStorage
- Not production-ready for multi-instance deployment

### 5.2 Storage Dependencies

**Supabase Storage Usage:**
- `apps/web/lib/avatar-service.ts` - Upload, delete, public URL
- `apps/web/lib/profile-service.ts` - Avatar URL generation

**Metadata Storage:**
- `nexus.user_profiles.avatar_storage_path` - Path in storage
- `nexus.file_metadata` - File metadata table

**Action Required:** Implement storage abstraction with local development implementation, migrate from Supabase Storage.

---

## 6. CHAT SYSTEM AUDIT

### 6.1 Guest Chat Flow

**Current Implementation:**
- **Location:** `apps/web/app/components/ChatInterface.tsx`
- **Method:** In-memory state only, no persistence
- **API Call:** Directly to Python ML service at `http://127.0.0.1:8000/orchestrate`
- **Issue:** Bypasses backend API, calls Python service directly

**Request Flow:**
```
Frontend (Guest) → Python ML Service (localhost:8000) → Response
```

**Status:** Works (no Supabase dependency in guest mode)

### 6.2 Authenticated Chat Flow

**Current Implementation:**
- **Location:** `apps/web/app/components/useConversationManager.ts`
- **Method:** Supabase persistence for conversations and messages
- **API Call:** Direct to Python ML service (bypasses backend)
- **Issue:** Uses Supabase directly, bypasses backend API

**Request Flow:**
```
Frontend → Supabase (conversations/messages) → Python ML Service → Supabase (save response)
```

**Issues Identified:**
1. Frontend bypasses backend API
2. Direct Supabase database access
3. No message persistence for guest mode
4. RLS depends on Supabase Auth

**Action Required:** Route all chat requests through backend API, implement backend-to-ML service communication.

### 6.3 Message Disappearing Issue

**Symptom:** Messages disappear after failed requests

**Root Cause Analysis:**
- Frontend clears input before request completes
- If request fails, message is lost
- No retry mechanism
- No optimistic update persistence

**Action Required:** Implement optimistic updates with rollback on failure.

---

## 7. AI SERVICE AUDIT

### 7.1 Python ML Service

**Location:** `packages/ai-core/ml-service/main.py`

**Framework:** FastAPI

**Endpoints:**
- `/orchestrate` - Main orchestration endpoint
- `/generate` - Text generation
- Data upload endpoints

**CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← SECURITY ISSUE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security Issue:** CORS allows all origins

**Status:** Independent of Supabase, can remain unchanged

### 7.2 AI Model

**Location:** `packages/ai-core/neural/transformer.py`

**Type:** Custom decoder-only Transformer

**Training:** Custom training pipeline exists

**Status:** Works, but model quality not verified (out of scope for database migration)

---

## 8. MEMORY & RAG AUDIT

### 8.1 Memory System

**Location:** `packages/repositories/src/memory-repository.ts`

**Database Table:** `nexus.memory_records`

**Status:** Repository exists, but not integrated into inference

**Issue:** Memory retrieval exists but not connected to AI orchestration

### 8.2 RAG System

**Location:** `packages/ai-core/knowledge/`

**Status:** RAG modules exist but not connected to inference

**Issue:** Knowledge base exists but not used in chat flow

**Action Required:** Integrate memory and RAG into backend orchestration (separate from database migration).

---

## 9. ENVIRONMENT CONFIGURATION AUDIT

### 9.1 Current Environment Variables

**Required Variables:**
```bash
NODE_ENV=development
WEB_PORT=3000
API_PORT=4000
API_ORIGIN=http://localhost:4000
WEB_ORIGIN=http://localhost:3000
DATABASE_PROVIDER=supabase
DATABASE_URL=
DATABASE_POOL_SIZE=20
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

**Runtime Config Check:**
```typescript
// packages/config/src/index.ts
if (nodeEnv === 'production' && !env.DATABASE_URL) errors.push('DATABASE_URL');
```

**Issue:** Production requires DATABASE_URL but ready flag is false (no production storage)

### 9.2 Environment Variable Loading

**Backend:**
- Uses `dotenv/config` in `apps/api/src/server.ts`
- Loads from `.env` file

**Frontend:**
- Next.js loads from `.env.local` and `.env`
- Public variables must start with `NEXT_PUBLIC_`

**Issue:** `.env` files are gitignored (cannot read for audit)

---

## 10. BUILD & TEST STATUS

### 10.1 Build Status

**Last Known Build Results:**
- ✅ database-core: BUILDS successfully
- ✅ repositories: BUILDS successfully
- ✅ auth-core: BUILDS successfully
- ✅ config: BUILDS successfully
- ❌ ai-core: FAILS with TypeScript errors
  - Missing file extensions in ES module imports
  - Property access errors in inference/model adapter code
  - Strict-mode errors for using `arguments` as class property

**Impact:** Pre-existing AI-core errors unrelated to database migration

### 10.2 Test Status

**Database Core Tests:**
- `packages/database-core/src/config.test.ts` - PASSED (6/6 tests)

**Other Tests:**
- Various test files exist in `tests/` directory
- Status unknown (not run during audit)

---

## 11. SECURITY ISSUES IDENTIFIED

### 11.1 Current Security Issues

1. **Frontend Direct Database Access**
   - Frontend accesses Supabase directly
   - Bypasses backend API
   - Violates security boundary

2. **Untrusted Header for Identity**
   - Backend uses `x-account-id` header for identity
   - Header can be spoofed by client
   - No real authentication in backend

3. **CORS Allows All Origins**
   - Python ML service allows all origins
   - Should restrict to backend API origin

4. **RLS Depends on Supabase Auth**
   - RLS policies use `auth.uid()` function
   - Will not work with Neon
   - Need application-level authorization

5. **Production Disabled**
   - API throws error in production mode
   - No production persistence available

### 11.2 Security Requirements for Migration

1. Remove frontend database access
2. Implement backend authentication
3. Add authorization checks on all protected routes
4. Restrict CORS on ML service
5. Implement proper session management

---

## 12. MIGRATION READINESS ASSESSMENT

### 12.1 Ready for Migration

- ✅ Database layer is provider-independent
- ✅ Migrations are standard SQL
- ✅ Repositories use database abstraction
- ✅ Backend API has database route structure
- ✅ Neon connection string format is standard PostgreSQL

### 12.2 Not Ready for Migration

- ❌ Frontend has extensive Supabase dependencies
- ❌ Authentication is Supabase Auth (not self-managed)
- ❌ Storage is Supabase Storage (not abstracted)
- ❌ Frontend bypasses backend API
- ❌ Backend has no real authentication
- ❌ RLS policies use Supabase-specific functions
- ❌ Chat system uses direct Supabase access

### 12.3 Blockers

1. **Neon Connection String:** Not provided by user
2. **Authentication Implementation:** Does not exist in backend
3. **Storage Abstraction:** Does not exist
4. **Frontend API Integration:** Frontend uses Supabase directly
5. **RLS Replacement:** Need application-level authorization

---

## 13. RECOMMENDED MIGRATION ORDER

### Phase 1: Database Layer (Neon Connection)
- Change `DATABASE_PROVIDER` to 'postgresql'
- Configure `DATABASE_URL` for Neon
- Run migrations on Neon
- Verify database connectivity

### Phase 2: Backend Authentication
- Implement password hashing (bcrypt/argon2)
- Implement session management (HTTP-only cookies)
- Add signup/login/logout endpoints
- Add session validation middleware
- Replace DevAuthService with real auth

### Phase 3: Frontend API Integration
- Replace Supabase client calls with backend API calls
- Remove `@supabase/supabase-js` dependency
- Update AuthContext to use backend auth
- Remove public Supabase environment variables

### Phase 4: Storage Abstraction
- Create storage interface
- Implement local storage for development
- Migrate avatar uploads to backend API
- Remove Supabase Storage dependency

### Phase 5: Chat System
- Route chat requests through backend API
- Backend orchestrates ML service calls
- Implement backend-to-ML service communication
- Fix message disappearing issue

### Phase 6: Memory & RAG Integration
- Connect memory repository to backend
- Integrate RAG into orchestration
- (Separate from database migration)

### Phase 7: Cleanup
- Remove all Supabase packages
- Remove Supabase environment variables
- Remove unused Supabase code
- Update documentation

---

## 14. FILES REQUIRING CHANGES

### 14.1 Configuration Files

1. `.env.example` - Remove Supabase variables, add Neon format
2. `apps/web/package.json` - Remove `@supabase/supabase-js`

### 14.2 Frontend Files (High Priority)

1. `apps/web/lib/supabase-client.ts` - DELETE or replace with API client
2. `apps/web/lib/conversation-service.ts` - Replace with API calls
3. `apps/web/lib/message-service.ts` - Replace with API calls
4. `apps/web/lib/profile-service.ts` - Replace with API calls
5. `apps/web/lib/avatar-service.ts` - Replace with storage abstraction
6. `apps/web/app/components/AuthContext.tsx` - Replace with backend auth
7. `apps/web/app/components/useConversationManager.ts` - Use API
8. `apps/web/app/components/ChatInterface.tsx` - Use backend API

### 14.3 Backend Files (High Priority)

1. `apps/api/src/app.ts` - Implement real authentication
2. `apps/api/src/routes/profile.ts` - Add authentication checks
3. `apps/api/src/routes/conversations.ts` - Add authentication checks
4. `apps/api/src/routes/auth.ts` - CREATE (signup/login/logout)
5. `apps/api/src/middleware/auth.ts` - CREATE (session validation)

### 14.4 Database Files (Medium Priority)

1. `packages/database-core/migrations/RLS_POLICIES.sql` - Replace with app-level auth
2. `packages/database-core/src/config.ts` - Change default provider to 'postgresql'

### 14.5 Test/Diagnostic Files (Low Priority)

1. `apps/web/test_*.js` - DELETE or update for backend API
2. `apps/web/authenticated_audit.mjs` - DELETE
3. `apps/web/forensic_audit.mjs` - DELETE
4. `apps/web/app/api/check-supabase/route.ts` - DELETE
5. `apps/web/lib/direct-supabase-check.ts` - DELETE
6. `apps/web/lib/supabase-diagnostics.ts` - DELETE

---

## 15. ASSUMPTIONS & LIMITATIONS

### 15.1 Assumptions

1. User has Neon project or can create one
2. No existing Supabase data needs migration (stated in requirements)
3. Local development environment can use local file storage
4. Backend API can orchestrate ML service calls
5. Password-based authentication is acceptable (not OAuth/SAML)

### 15.2 Limitations

1. Cannot read `.env` files (gitignored for security)
2. Cannot verify actual Supabase data (no access)
3. Cannot verify Neon connection (no credentials)
4. AI model quality not assessed (out of scope)
5. RAG system not assessed (out of scope)

---

## 16. NEXT STEPS

### Immediate Actions Required

1. **User Action:** Provide Neon connection string
2. **User Approval:** Confirm self-managed authentication approach
3. **User Approval:** Confirm local storage approach for development
4. **Architecture Design:** Create detailed target architecture document

### Phase Zero Complete

This audit provides a complete picture of Supabase dependencies and migration readiness. The next phase (Phase One) will design the target architecture and implementation order.

---

**Audit Status:** COMPLETE
**Next Phase:** Phase One - Target Architecture Design
