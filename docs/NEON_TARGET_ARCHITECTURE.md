# NEON TARGET ARCHITECTURE

**Date:** 2025-01-15
**Phase:** Phase One - Target Architecture Design
**Based On:** SUPABASE_REMOVAL_NEON_MIGRATION_AUDIT.md

---

## EXECUTIVE SUMMARY

This document defines the target architecture for NexusAI after complete Supabase removal and Neon PostgreSQL migration. The architecture maintains the existing frontend and backend applications while replacing Supabase with self-managed infrastructure.

**Key Changes:**
- Database: Supabase PostgreSQL → Neon PostgreSQL
- Authentication: Supabase Auth → Self-managed password-based auth with HTTP-only cookies
- Storage: Supabase Storage → Local storage abstraction (development) / Object storage (future)
- Chat: Direct Supabase access → Backend API orchestration
- Security: Frontend direct access → Backend-mediated access with proper authorization

---

## 1. TARGET ARCHITECTURE OVERVIEW

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER (Client)                        │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Next.js Web    │  │  Auth Context   │  │  Chat Interface │ │
│  │  (React 19)     │  │  (Session Mgmt) │  │  (UI Layer)     │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                     │                     │           │
│           └─────────────────────┴─────────────────────┘           │
│                              │                                    │
│                              │ HTTP-only Cookie                    │
│                              │ (session token)                      │
└──────────────────────────────┼────────────────────────────────────┘
                               │
                               │ HTTPS (CORS-restricted)
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                      BACKEND API (Fastify)                        │
│                              │                                    │
│  ┌─────────────────┐  ┌─────┴─────┐  ┌─────────────────┐         │
│  │  Auth Routes    │  │  Profile  │  │  Conversation   │         │
│  │  (signup/login) │  │  Routes   │  │  Routes         │         │
│  └────────┬────────┘  └─────┬─────┘  └────────┬────────┘         │
│           │                 │                 │                   │
│  ┌────────┴────────┐  ┌─────┴─────┐  ┌────────┴────────┐         │
│  │  Session Mgmt   │  │  Authz    │  │  Orchestration  │         │
│  │  (HTTP-only)    │  │  Middleware│  │  (to ML Service)│         │
│  └────────┬────────┘  └─────┬─────┘  └────────┬────────┘         │
│           │                 │                 │                   │
│           └─────────────────┴─────────────────┘                   │
│                              │                                    │
│                              │ pg (PostgreSQL driver)             │
│                              │ SSL connection                      │
└──────────────────────────────┼────────────────────────────────────┘
                               │
                               │ PostgreSQL (SSL)
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                     NEON POSTGRESQL                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  nexus schema                                             │   │
│  │                                                           │   │
│  │  - accounts                (auth_issuer, auth_subject)   │   │
│  │  - auth_sessions           (session_token_hash)           │   │
│  │  - user_profiles           (display_name, avatar_path)    │   │
│  │  - conversations           (account_id, title)            │   │
│  │  - messages                (conversation_id, content)     │   │
│  │  - memory_records          (category, value)              │   │
│  │  - consent_records         (decision, policy_version)    │   │
│  │  - file_metadata           (storage_provider, path)       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON ML SERVICE (FastAPI)                   │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  /orchestrate   │  │  /generate      │  │  Knowledge Base  │ │
│  │  (Chat API)     │  │  (Text Gen)     │  │  (RAG System)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  CORS: Restricted to backend API origin only                     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

**Frontend (Next.js):**
- UI rendering and user interaction
- Session cookie storage (HTTP-only, set by backend)
- API communication (never direct database access)
- Client-side validation

**Backend API (Fastify):**
- Authentication (signup, login, logout)
- Session management (HTTP-only cookies)
- Authorization (account ownership checks)
- Business logic orchestration
- Database access (via repositories)
- ML service orchestration

**Neon PostgreSQL:**
- Persistent data storage
- User accounts and sessions
- Conversations and messages
- Profiles and file metadata
- Memory and consent records

**Python ML Service:**
- Text generation
- Knowledge retrieval (RAG)
- Memory integration
- Internal-only (CORS restricted to backend)

---

## 2. AUTHENTICATION ARCHITECTURE

### 2.1 Self-Managed Authentication Design

**Method:** Password-based authentication with HTTP-only cookies

**Password Hashing:**
- Library: `bcrypt` or `argon2` (industry standard)
- Salt: Automatic (handled by library)
- Cost factor: 12 (bcrypt) or default (argon2)

**Session Management:**
- Storage: Neon PostgreSQL (`nexus.auth_sessions`)
- Token: Random UUID
- Cookie: HTTP-only, SameSite=Lax, Secure (HTTPS)
- Expiration: Configurable (default: 7 days)
- Rotation: Refresh on sensitive operations

**Session Storage Schema:**
```sql
CREATE TABLE nexus.auth_sessions (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id          uuid NOT NULL,
  session_token_hash  varchar(255) NOT NULL UNIQUE,
  created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
  expires_at          timestamptz NOT NULL,
  last_seen_at        timestamptz NOT NULL DEFAULT clock_timestamp(),
  revoked_at          timestamptz,
  status              text NOT NULL DEFAULT 'active',
  CONSTRAINT auth_sessions_account_fk FOREIGN KEY (account_id)
    REFERENCES nexus.accounts (id) ON DELETE RESTRICT
);
```

### 2.2 Authentication Flow

**Signup Flow:**
```
1. User submits email/password to /api/v1/auth/register
2. Backend validates input, checks email uniqueness
3. Backend hashes password with bcrypt
4. Backend creates account in nexus.accounts
5. Backend creates session in nexus.auth_sessions
6. Backend sets HTTP-only cookie with session token
7. Backend returns account_id and success status
```

**Login Flow:**
```
1. User submits email/password to /api/v1/auth/login
2. Backend validates input
3. Backend finds account by email
4. Backend verifies password hash
5. Backend creates session in nexus.auth_sessions
6. Backend sets HTTP-only cookie with session token
7. Backend returns account_id and success status
```

**Session Validation Flow:**
```
1. Middleware extracts session cookie
2. Backend finds session by token hash
3. Backend checks session not expired/revoked
4. Backend checks account active
5. Middleware sets request.accountId
6. Protected routes use request.accountId
```

**Logout Flow:**
```
1. User requests /api/v1/auth/logout
2. Backend finds session by token hash
3. Backend marks session as revoked
4. Backend clears HTTP-only cookie
5. Backend returns success
```

### 2.3 Authorization Strategy

**Application-Level Authorization:**
- All queries include `WHERE account_id = $1` clause
- No RLS policies (application handles ownership)
- Middleware validates session before route execution
- Routes check account ownership explicitly

**Example:**
```typescript
// Before (untrusted header)
const accountId = request.headers['x-account-id'];

// After (validated session)
const accountId = request.accountId; // Set by auth middleware
const profile = await profileRepo.findByAccountId(accountId);
```

---

## 3. DATABASE ARCHITECTURE

### 3.1 Neon PostgreSQL Configuration

**Connection String Format:**
```
postgresql://[user].[project_id]:[password]@[neon-hostname]/[database]?sslmode=require
```

**Environment Variables:**
```bash
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql://[neon-connection-string]
DATABASE_POOL_SIZE=20
```

**Connection Pooling:**
- Neon provides connection pooling via PgBouncer
- Application uses `pg` library with built-in pooling
- Pool size configurable via `DATABASE_POOL_SIZE`

**SSL:**
- Required: `sslmode=require`
- Handled automatically by `pg` library

### 3.2 Schema Preservation

**Decision:** Preserve existing `nexus` schema

**Rationale:**
- Schema is already provider-independent
- Migrations are standard SQL
- No Supabase-specific features in schema (except RLS)
- Minimal changes required

**Schema Changes Required:**
1. Remove RLS policies (use application-level auth)
2. Add password_hash column to nexus.accounts
3. Add index on accounts.email_normalized for login performance

**Migration Additions:**
```sql
-- Add password hash column
ALTER TABLE nexus.accounts ADD COLUMN password_hash varchar(255);

-- Add email index for login performance
CREATE INDEX IF NOT EXISTS accounts_email_idx
  ON nexus.accounts (email_normalized)
  WHERE status = 'active';
```

### 3.3 Migration Strategy

**Approach:** Fresh schema on Neon (no data migration)

**Steps:**
1. Create Neon project
2. Get Neon connection string
3. Configure DATABASE_URL
4. Run MigrationRunner to apply migrations 001-015
5. Apply additional migration for password_hash column
6. Verify schema via health check

**Excluded Migrations:**
- `COMPLETE_SCHEMA.sql` - Consolidated, not needed
- `RLS_POLICIES.sql` - Supabase-specific, use app-level auth

### 3.4 Database Health Check

**Implementation:**
```typescript
// packages/database-core/src/index.ts
async healthCheck(): Promise<{ status: 'ok' | 'error'; latency?: number }> {
  const start = Date.now();
  try {
    await this.query('SELECT 1');
    return { status: 'ok', latency: Date.now() - start };
  } catch (error) {
    return { status: 'error' };
  }
}
```

**API Endpoint:**
```typescript
// apps/api/src/app.ts
app.get('/health/database', async () => {
  const dbHealth = await db.healthCheck();
  return dbHealth;
});
```

---

## 4. STORAGE ARCHITECTURE

### 4.1 Storage Abstraction Design

**Interface:**
```typescript
interface StorageProvider {
  upload(file: File, path: string): Promise<{ url: string; path: string }>;
  delete(path: string): Promise<void>;
  getPublicUrl(path: string): string;
}
```

**Development Implementation (Local):**
- Store files in `public/uploads/` directory
- Serve via Next.js static file serving
- Not production-ready for multi-instance

**Future Production Implementation:**
- AWS S3 adapter
- Cloudflare R2 adapter
- Google Cloud Storage adapter

### 4.2 File Metadata Storage

**Database Table:**
```sql
CREATE TABLE nexus.file_metadata (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id          uuid NOT NULL,
  storage_provider    varchar(50) NOT NULL DEFAULT 'local',
  storage_path        varchar(500) NOT NULL,
  file_name           varchar(255) NOT NULL,
  file_size           bigint NOT NULL,
  mime_type           varchar(100) NOT NULL,
  created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
  deleted_at          timestamptz,
  CONSTRAINT file_metadata_account_fk FOREIGN KEY (account_id)
    REFERENCES nexus.accounts (id) ON DELETE RESTRICT
);
```

**API Endpoints:**
- `POST /api/v1/files/upload` - Upload file
- `DELETE /api/v1/files/:id` - Delete file
- `GET /api/v1/files/:id` - Get file metadata

### 4.3 Avatar Flow

**Upload Flow:**
```
1. User selects avatar file
2. Frontend validates file type/size
3. Frontend POSTs to /api/v1/files/upload
4. Backend saves file to local storage
5. Backend creates file_metadata record
6. Backend updates user_profiles.avatar_storage_path
7. Backend returns public URL
8. Frontend displays avatar
```

**Authorization:**
- Only account owner can upload/update avatar
- Backend validates account ownership
- Files isolated by account_id

---

## 5. CHAT SYSTEM ARCHITECTURE

### 5.1 Guest Chat Flow

**Current Issue:** Direct ML service call, bypasses backend

**Target Flow:**
```
1. Guest submits message to /api/v1/chat/guest
2. Backend validates request (no auth required)
3. Backend forwards to Python ML service
4. ML service returns response
5. Backend returns response to frontend
6. Frontend displays message (in-memory only)
```

**Backend Endpoint:**
```typescript
// apps/api/src/routes/chat.ts
app.post('/api/v1/chat/guest', async (request, reply) => {
  const { message } = request.body;
  const response = await mlServiceClient.generate({
    message,
    conversation_id: 'guest',
    conversation_history: [],
  });
  return reply.send({ response });
});
```

### 5.2 Authenticated Chat Flow

**Current Issue:** Direct Supabase access, bypasses backend

**Target Flow:**
```
1. Authenticated user submits message to /api/v1/chat/message
2. Backend validates session (auth middleware)
3. Backend creates or finds conversation (via repository)
4. Backend saves user message (via repository)
5. Backend forwards to Python ML service with context
6. ML service returns response
7. Backend saves AI response (via repository)
8. Backend returns conversation and messages to frontend
9. Frontend displays messages
```

**Backend Endpoint:**
```typescript
// apps/api/src/routes/chat.ts
app.post('/api/v1/chat/message', async (request, reply) => {
  const accountId = request.accountId; // From auth middleware
  const { message, conversationId } = request.body;

  // Create conversation if needed
  let convId = conversationId;
  if (!convId) {
    const conv = await conversationRepo.create({
      accountId,
      title: message.substring(0, 30),
    });
    convId = conv.id;
  }

  // Save user message
  await messageRepo.create({
    conversationId: convId,
    senderRole: 'user',
    content: message,
  });

  // Get conversation history
  const messages = await messageRepo.listByConversationId(convId);

  // Call ML service
  const response = await mlServiceClient.generate({
    message,
    conversation_id: convId,
    conversation_history: messages,
  });

  // Save AI response
  await messageRepo.create({
    conversationId: convId,
    senderRole: 'assistant',
    content: response,
  });

  // Return updated conversation
  const updatedMessages = await messageRepo.listByConversationId(convId);
  return reply.send({ conversationId: convId, messages: updatedMessages });
});
```

### 5.3 Message Persistence Fix

**Issue:** Messages disappear on failed requests

**Solution:**
1. Add message to UI state optimistically
2. Send request to backend
3. If success: mark as persisted
4. If failure: show error, keep message in UI for retry
5. Implement retry mechanism

**Implementation:**
```typescript
// Frontend ChatInterface.tsx
const handleSubmit = async (message: string) => {
  // Optimistic update
  const tempMessage: ConversationMessage = {
    id: crypto.randomUUID(),
    role: 'user',
    content: message,
    timestamp: new Date(),
    pending: true,
  };

  setMessages(prev => [...prev, tempMessage]);

  try {
    const result = await api.sendMessage(message);
    // Replace temp message with persisted message
    setMessages(prev => prev.map(m =>
      m.id === tempMessage.id ? result.userMessage : m
    ));
  } catch (error) {
    // Keep message for retry, show error
    setMessages(prev => prev.map(m =>
      m.id === tempMessage.id ? { ...m, isError: true } : m
    ));
  }
};
```

---

## 6. API ROUTE STRUCTURE

### 6.1 Auth Routes

```
POST   /api/v1/auth/register   - Signup
POST   /api/v1/auth/login      - Login
POST   /api/v1/auth/logout     - Logout
GET    /api/v1/auth/session    - Validate session
POST   /api/v1/auth/refresh    - Refresh session
```

### 6.2 Profile Routes

```
GET    /api/v1/profile              - Get current profile
POST   /api/v1/profile              - Create profile
PUT    /api/v1/profile              - Update profile
DELETE /api/v1/profile              - Delete profile
```

### 6.3 Conversation Routes

```
GET    /api/v1/conversations           - List conversations
GET    /api/v1/conversations/:id       - Get conversation with messages
POST   /api/v1/conversations           - Create conversation
DELETE /api/v1/conversations/:id       - Delete conversation
```

### 6.4 Chat Routes

```
POST   /api/v1/chat/guest          - Guest chat (no auth)
POST   /api/v1/chat/message        - Authenticated chat
POST   /api/v1/chat/regenerate     - Regenerate AI response
```

### 6.5 File Routes

```
POST   /api/v1/files/upload        - Upload file
DELETE /api/v1/files/:id           - Delete file
GET    /api/v1/files/:id           - Get file metadata
```

---

## 7. SECURITY ARCHITECTURE

### 7.1 Security Boundaries

**Frontend:**
- No database credentials
- No direct database access
- Session storage via HTTP-only cookies only
- Input validation

**Backend:**
- Never trusts client-provided account IDs
- Validates session on every protected request
- Checks account ownership for all data access
- Parameterized SQL queries
- CORS restricted to frontend origin

**Database:**
- No direct frontend access
- SSL required
- Application-level authorization (no RLS)
- Passwords hashed with bcrypt

**ML Service:**
- CORS restricted to backend API origin only
- Not exposed to public internet
- Internal communication only

### 7.2 Security Headers

**Backend Headers:**
```typescript
app.addHook('onRequest', async (request, reply) => {
  reply.header('x-content-type-options', 'nosniff');
  reply.header('x-frame-options', 'DENY');
  reply.header('referrer-policy', 'no-referrer');
  reply.header('cache-control', 'private, no-store');
  reply.header('access-control-allow-origin', config.webOrigin);
  reply.header('access-control-allow-credentials', 'true');
});
```

### 7.3 Rate Limiting

**Auth Endpoints:**
- IP-based rate limit: 20 attempts per minute
- Email-based rate limit: 5 attempts per minute

**Chat Endpoints:**
- Account-based rate limit: 100 messages per hour

---

## 8. IMPLEMENTATION ORDER

### Phase 2: Neon Database Access (Week 1)

**Tasks:**
1. Update `.env.example` with Neon format
2. Add password_hash column migration
3. Create database health check
4. Configure DATABASE_URL for Neon
5. Run migrations on Neon
6. Verify database connectivity

**Files Changed:**
- `.env.example`
- `packages/database-core/migrations/016_add_password_hash.sql` (new)
- `packages/database-core/src/index.ts` (health check)

**Acceptance Criteria:**
- Database connects to Neon successfully
- All migrations applied
- Health check returns { status: 'ok' }

### Phase 3: Backend Authentication (Week 2)

**Tasks:**
1. Install bcrypt package
2. Implement password hashing utilities
3. Create auth routes (signup, login, logout)
4. Implement session management
5. Create auth middleware
6. Update profile/conversation routes with auth checks
7. Replace DevAuthService with real auth

**Files Changed:**
- `apps/api/package.json` (add bcrypt)
- `apps/api/src/routes/auth.ts` (new)
- `apps/api/src/middleware/auth.ts` (new)
- `apps/api/src/app.ts` (auth integration)
- `apps/api/src/routes/profile.ts` (auth checks)
- `apps/api/src/routes/conversations.ts` (auth checks)

**Acceptance Criteria:**
- Signup creates account with hashed password
- Login verifies password and sets cookie
- Logout revokes session and clears cookie
- Protected routes require valid session
- Invalid sessions return 401

### Phase 4: Frontend API Integration (Week 3)

**Tasks:**
1. Create API client for backend communication
2. Replace Supabase Auth with backend auth
3. Replace Supabase conversation service with API calls
4. Replace Supabase message service with API calls
5. Replace Supabase profile service with API calls
6. Remove Supabase client dependency
7. Remove public Supabase environment variables

**Files Changed:**
- `apps/web/lib/api-client.ts` (new)
- `apps/web/app/components/AuthContext.tsx` (backend auth)
- `apps/web/lib/conversation-service.ts` (API calls)
- `apps/web/lib/message-service.ts` (API calls)
- `apps/web/lib/profile-service.ts` (API calls)
- `apps/web/lib/supabase-client.ts` (delete)
- `apps/web/package.json` (remove @supabase/supabase-js)

**Acceptance Criteria:**
- Signup/login works via backend API
- Conversations load via backend API
- Messages save via backend API
- Profile updates via backend API
- No Supabase client references remain

### Phase 5: Storage Abstraction (Week 4)

**Tasks:**
1. Create storage interface
2. Implement local storage provider
3. Create file upload/delete API routes
4. Update avatar service to use storage abstraction
5. Remove Supabase Storage dependency

**Files Changed:**
- `packages/storage-core/src/index.ts` (new package)
- `apps/api/src/routes/files.ts` (new)
- `apps/web/lib/avatar-service.ts` (storage abstraction)
- `apps/web/lib/profile-service.ts` (remove Supabase Storage)

**Acceptance Criteria:**
- Avatar uploads work with local storage
- Avatar deletion works
- Storage abstraction interface defined
- No Supabase Storage references remain

### Phase 6: Chat System Fix (Week 5)

**Tasks:**
1. Create guest chat API route
2. Create authenticated chat API route
3. Implement backend-to-ML service client
4. Update ChatInterface to use backend API
5. Fix message disappearing issue (optimistic updates)
6. Restrict ML service CORS to backend origin

**Files Changed:**
- `apps/api/src/routes/chat.ts` (new)
- `apps/api/src/ml-client.ts` (new)
- `apps/web/app/components/ChatInterface.tsx` (backend API)
- `packages/ai-core/ml-service/main.py` (CORS restriction)

**Acceptance Criteria:**
- Guest chat works without login
- Authenticated chat works after login
- Messages persist correctly
- No messages disappear on failure
- ML service restricted to backend origin

### Phase 7: Memory & AI Integration (Week 6)

**Tasks:**
1. Connect memory repository to backend
2. Implement memory retrieval in orchestration
3. Integrate RAG into ML service (if applicable)
4. Add memory to chat context

**Files Changed:**
- `apps/api/src/routes/chat.ts` (memory integration)
- `packages/ai-core/ml-service/main.py` (RAG integration)

**Acceptance Criteria:**
- Memory saves to database
- Memory retrieves for relevant conversations
- RAG provides context to model (if implemented)

### Phase 8: Cleanup (Week 7)

**Tasks:**
1. Remove all Supabase packages
2. Remove Supabase environment variables
3. Remove unused Supabase code
4. Remove test/diagnostic files
5. Update documentation
6. Remove RLS policies from migrations

**Files Changed:**
- `apps/web/package.json` (remove all Supabase)
- `.env.example` (remove Supabase vars)
- `packages/database-core/migrations/RLS_POLICIES.sql` (delete)
- All test files referencing Supabase (delete/update)
- `README.md` (update setup instructions)

**Acceptance Criteria:**
- No Supabase packages in lockfile
- No Supabase environment variables
- No Supabase imports in code
- No test failures due to missing Supabase

### Phase 9: Verification (Week 8)

**Tasks:**
1. Run typecheck
2. Run build
3. Run unit tests
4. Run integration tests
5. Test guest chat end-to-end
6. Test signup → login → chat → logout
7. Test session restoration
8. Test profile update and avatar upload
9. Test conversation persistence
10. Repository-wide Supabase scan

**Acceptance Criteria:**
- Typecheck passes
- Build succeeds
- Tests pass
- All user flows work
- No Supabase references found

---

## 9. ROLLBACK PLAN

### 9.1 Code Rollback

**Git Strategy:**
- Create branch before each phase
- Commit after each phase
- Tag major milestones

**Rollback Commands:**
```bash
# Rollback entire migration
git checkout main

# Rollback specific phase
git checkout phase-2-start
```

### 9.2 Database Rollback

**Strategy:**
- Neon schema is fresh (no production data)
- Delete Neon project if needed
- Recreate with Supabase connection string

**Steps:**
1. Update DATABASE_URL to Supabase
2. Change DATABASE_PROVIDER to 'supabase'
3. Run Supabase migrations
4. Restore frontend Supabase integration

---

## 10. REMAINING LIMITATIONS

### 10.1 Post-Migration Limitations

1. **Local Storage:** Not production-ready for multi-instance deployment
2. **No OAuth:** Only password-based authentication
3. **No MFA:** No multi-factor authentication
4. **No Email Verification:** Emails not verified on signup
5. **No Password Reset:** Cannot reset forgotten passwords
6. **No Account Deletion:** Account deletion not implemented
7. **ML Service Quality:** Model training/quality not addressed
8. **RAG Integration:** May not be fully connected

### 10.2 Future Enhancements

1. **OAuth Providers:** Google, GitHub, etc.
2. **MFA:** TOTP-based multi-factor authentication
3. **Email Verification:** Send verification emails
4. **Password Reset:** Email-based password reset
5. **Account Deletion:** GDPR-compliant deletion
6. **Object Storage:** S3/R2 adapter for production
7. **Model Training:** Improve model quality
8. **Advanced RAG:** Better knowledge retrieval

---

## 11. BLOCKERS & RISKS

### 11.1 Current Blockers

1. **Neon Connection String:** User must provide
2. **User Approval:** Confirm self-managed auth approach
3. **User Approval:** Confirm local storage approach

### 11.2 Risks

**High Risk:**
- Session security: HTTP-only cookies must be implemented correctly
- Password hashing: Must use industry-standard library
- SQL injection: Must use parameterized queries
- CORS misconfiguration: ML service must be restricted

**Medium Risk:**
- Message persistence: Optimistic updates must handle failures
- Storage migration: File migration path not defined
- Session expiration: Must handle expired sessions gracefully

**Low Risk:**
- Local storage: Not production-ready, but acceptable for development
- RLS removal: Application-level auth must be comprehensive

---

## 12. SUCCESS CRITERIA

### 12.1 Migration Complete When:

- ✅ Neon is the verified primary application database
- ✅ Supabase is no longer required anywhere in the active application
- ✅ Guest Chat works without login
- ✅ Authenticated Chat works after login
- ✅ Messages do not disappear silently
- ✅ Authentication, session handling, and user-data isolation are verified
- ✅ Profile and avatar flows work using the replacement implementation
- ✅ The AI service is reached through the intended backend path
- ✅ Type checks, tests, and builds have been run and their actual outcomes documented
- ✅ No Supabase references remain in code

### 12.2 Production Readiness Gap

This migration does NOT achieve production readiness. Additional work required:
- Email verification
- Password reset
- OAuth providers
- MFA
- Object storage (S3/R2)
- Rate limiting (production-grade)
- Monitoring and observability
- Load testing
- Security audit

---

**Architecture Status:** DESIGNED
**Next Phase:** Phase Two - Implement Neon Database Access
