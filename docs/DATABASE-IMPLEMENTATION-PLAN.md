# NEXUSAI - DATABASE IMPLEMENTATION PLAN
**Date:** 2026-10-14
**Author:** Devin AI Assistant
**Status:** DETAILED PLAN

---

## 1. SCHEMA VALIDATION RESULTS

### Approved Design (docs/05-*, docs/06-*)

The approved design contains **21 entities** for a comprehensive Health & Wellness Companion MVP:

**Core Identity:**
- accounts
- auth_sessions

**User Profile:**
- user_profiles
- wellness_profiles (health-specific - defer for now)

**Consent:**
- consent_records

**Wellness Planning:**
- goals
- routines
- daily_plans
- task_instances (defer all wellness-specific for now)

**Conversation & Memory:**
- conversations ✅ REQUIRED
- messages ✅ REQUIRED
- memory_records ✅ REQUIRED

**Notifications:**
- reminders (defer for now)
- notification_preferences ✅ REQUIRED (as user_preferences)

**Safety & Audit:**
- safety_events (defer for now)
- audit_events (defer for now)
- ai_usage_metadata (defer for now)

**Governance:**
- export_requests (defer for now)
- deletion_requests (defer for now)
- support_access_records (defer for now)

### Current Application Requirements (from master prompt)

**REQUIRED NOW:**
1. ✅ profiles → Use approved `user_profiles`
2. ✅ conversations → Use approved `conversations`
3. ✅ messages → Use approved `messages`
4. ✅ user_memory → Use approved `memory_records`
5. ✅ user_preferences → Use approved `notification_preferences`

**NOT IN APPROVED DESIGN (must design new):**
6. ❌ library_items → NEW ENTITY REQUIRED
7. ❌ file_metadata → NEW ENTITY REQUIRED

**DEFER TO FUTURE (wellness-specific):**
- wellness_profiles
- goals
- routines
- daily_plans
- task_instances
- reminders
- safety_events
- audit_events
- ai_usage_metadata
- export_requests
- deletion_requests
- support_access_records

---

## 2. ENTITY SELECTION FOR PHASE 1

### Implementation Set 1: Core Identity (Required Foundation)
1. **accounts** - User identity anchor
2. **auth_sessions** - Session persistence

### Implementation Set 2: User Profile (Required)
3. **user_profiles** - Profile storage

### Implementation Set 3: Chat & Memory (Required)
4. **conversations** - Chat conversations
5. **messages** - Chat messages
6. **memory_records** - User memory
7. **notification_preferences** - User preferences

### Implementation Set 4: Library & Files (New Design Required)
8. **library_items** - Saved library content
9. **file_metadata** - File upload metadata

**Total:** 9 entities (7 from approved design, 2 new)

---

## 3. NEW ENTITY DESIGNS

### library_items (NEW)
Purpose: Store user-saved content in the Library feature

```sql
CREATE TABLE IF NOT EXISTS nexus.library_items (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    item_type           text NOT NULL,
    title               varchar(255) NOT NULL,
    description         text,
    content             text,
    storage_reference    varchar(500),
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT library_items_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT library_items_account_id_uk UNIQUE (account_id, id),
    CONSTRAINT library_items_type_ck CHECK (item_type IN ('note', 'bookmark', 'reference', 'custom')),
    CONSTRAINT library_items_title_ck CHECK (char_length(btrim(title)) > 0),
    CONSTRAINT library_items_deleted_state_ck CHECK (deleted_at IS NULL OR item_type IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS library_items_account_type_idx
    ON nexus.library_items (account_id, item_type, created_at DESC);
```

### file_metadata (NEW)
Purpose: Store metadata for uploaded files (profile photos, etc.)

```sql
CREATE TABLE IF NOT EXISTS nexus.file_metadata (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          uuid NOT NULL,
    storage_provider     text NOT NULL DEFAULT 'supabase',
    storage_key          varchar(500) NOT NULL,
    mime_type            varchar(100) NOT NULL,
    size_bytes          bigint NOT NULL,
    file_name           varchar(255),
    created_at          timestamptz NOT NULL DEFAULT clock_timestamp(),
    deleted_at          timestamptz,
    CONSTRAINT file_metadata_account_fk FOREIGN KEY (account_id)
        REFERENCES nexus.accounts (id) ON DELETE RESTRICT,
    CONSTRAINT file_metadata_account_id_uk UNIQUE (account_id, id),
    CONSTRAINT file_metadata_provider_ck CHECK (storage_provider IN ('supabase', 's3', 'local')),
    CONSTRAINT file_metadata_size_ck CHECK (size_bytes >= 0),
    CONSTRAINT file_metadata_deleted_state_ck CHECK (deleted_at IS NULL OR storage_key IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS file_metadata_account_created_idx
    ON nexus.file_metadata (account_id, created_at DESC);
```

---

## 4. MIGRATION STRATEGY

### Phase 1: Core Identity (Workstream 2-3)
- Migration 001: Bootstrap (extensions, schema, functions)
- Migration 002: accounts table
- Migration 003: auth_sessions table

### Phase 2: Profile (Workstream 5)
- Migration 004: user_profiles table

### Phase 3: Chat & Memory (Workstream 6-7)
- Migration 005: conversations table
- Migration 006: messages table
- Migration 007: memory_records table
- Migration 008: notification_preferences table

### Phase 4: Library & Files (Workstream 6)
- Migration 009: library_items table
- Migration 010: file_metadata table

### RLS Policies (Workstream 8)
- Applied after all tables created
- One policy per table
- Test with dedicated authorization tests

---

## 5. PROVIDER ABSTRACTION DESIGN

### Architecture
```
packages/database-core/
├── src/
│   ├── index.ts (existing interfaces)
│   ├── postgres-client.ts (existing implementation)
│   ├── supabase-client.ts (NEW - Supabase-specific)
│   └── migration-runner.ts (NEW - migration execution)
```

### Interfaces (preserve existing)
- DatabaseClient (from index.ts)
- Repository (from index.ts)
- MigrationRunner (from index.ts)

### New Implementation
- **SupabaseClient**: Wraps @supabase/supabase-js for TypeScript client
- **MigrationRunner**: Executes SQL migrations in order

### Provider Switching
Environment variable `DATABASE_PROVIDER` controls which client:
- `postgresql` → PostgresClient (self-hosted)
- `supabase` → SupabaseClient (managed)

---

## 6. IMPLEMENTATION WORKSTREAMS

### Workstream 1: Schema Validation ✅ COMPLETED
- Reviewed approved 21-entity design
- Identified 9 entities for current requirements
- Designed 2 new entities (library_items, file_metadata)

### Workstream 2: Database Configuration (NEXT)
- Add environment variables to .env.example
- Create database configuration module
- Implement connection handling with provider abstraction

### Workstream 3: SQL Migrations
- Create migrations/ directory
- Implement MigrationRunner
- Create migration files 001-010
- Add migration execution script

### Workstream 4: Provider Abstraction
- Implement SupabaseClient
- Update config to support provider selection
- Test connection handling

### Workstream 5: Profile Persistence
- Implement ProfileRepository
- Update API to use database
- Update frontend to fetch/save from API
- Test profile CRUD

### Workstream 6: Conversation/Message Persistence
- Implement ConversationRepository
- Implement MessageRepository
- Update ChatInterface to use API
- Update useConversationManager to use API
- Test chat save/load

### Workstream 7: Memory Repository
- Implement MemoryRepository (database-backed)
- Connect to memory service
- Test memory CRUD

### Workstream 8: RLS and Security
- Create RLS policies for all user-owned tables
- Implement ownership validation
- Add cross-user authorization tests

### Workstream 9: Automated Tests
- Database migration tests
- Repository CRUD tests
- Authorization tests
- API integration tests

### Workstream 10: Documentation
- Supabase setup guide
- Environment variable documentation
- Migration commands
- Self-hosting migration path

---

## 7. CRITICAL DEPENDENCIES

### Blockers
1. **Supabase Project Credentials** - Required for actual connection testing
   - If unavailable: Implement code + migrations, document missing config, do not fake connection

2. **PostgreSQL for Local Testing** - Required for migration tests
   - Can use Docker if available
   - Otherwise: Use Supabase for testing

### Non-Blockers
- Can implement all code without credentials
- Can create migrations without running them
- Can write tests without executing them
- Document what requires manual setup

---

## 8. SUCCESS CRITERIA

### Workstream 2 (Database Configuration)
✅ Environment variables defined
✅ Configuration module works
✅ Connection handling abstracted
✅ Provider selection works

### Workstream 3 (SQL Migrations)
✅ Migration files created
✅ MigrationRunner implemented
✅ Migrations are idempotent
✅ Migration order is versioned

### Workstream 4 (Provider Abstraction)
✅ SupabaseClient implemented
✅ Provider switching works
✅ Both providers share interface

### Workstream 5 (Profile Persistence)
✅ ProfileRepository implemented
✅ API endpoint uses database
✅ Frontend saves/loads from API
✅ Profile persists across refresh

### Workstream 6 (Conversation/Message Persistence)
✅ ConversationRepository implemented
✅ MessageRepository implemented
✅ Chat saves to database
✅ History loads from database
✅ Pagination works

### Workstream 7 (Memory Repository)
✅ MemoryRepository implemented
✅ Memory service uses database
✅ Memory persists across sessions

### Workstream 8 (RLS and Security)
✅ RLS policies created
✅ Ownership validation works
✅ Cross-user access blocked
✅ Authorization tests pass

### Workstream 9 (Automated Tests)
✅ Migration tests pass
✅ Repository tests pass
✅ Authorization tests pass
✅ API integration tests pass

### Workstream 10 (Documentation)
✅ Setup guide complete
✅ Environment variables documented
✅ Migration commands documented
✅ Self-hosting path documented

---

## 9. MANUAL SETUP STEPS (REQUIRED IF CREDENTIALS UNAVAILABLE)

### If Supabase Credentials Available:
1. Create Supabase project
2. Enable PostgreSQL, Storage, Auth
3. Copy project URL and anon key to .env
4. Run migrations
5. Test connection

### If Supabase Credentials Unavailable:
1. Implement all code (Workstreams 2-10)
2. Create migration files
3. Write tests
4. Document that connection testing is blocked by missing credentials
5. Provide manual setup steps for when credentials available

---

## 10. NEXT STEPS

Proceed to **Workstream 2: Database Configuration** to implement environment variables and connection handling.

---

**Plan Status:** COMPLETE
**Ready for Workstream 2: Database Configuration**
