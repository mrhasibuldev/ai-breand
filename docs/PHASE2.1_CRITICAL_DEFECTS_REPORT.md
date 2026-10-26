# PHASE 2.1 — CRITICAL DEFECTS AUDIT REPORT

## EXECUTIVE SUMMARY

Critical defects found in the Phase 2 implementation that prevent it from working in production:

1. **CRITICAL:** conversations.account_id FK constraint mismatch
2. **CRITICAL:** Nexus schema not exposed to Supabase Data API
3. **CRITICAL:** No API permissions granted for nexus schema
4. **HIGH:** History page component completely missing
5. **MEDIUM:** No conversation restoration logic after refresh

---

## CRITICAL DEFECT #1: DATABASE OWNERSHIP MODEL MISMATCH

### Problem:
The `nexus.conversations` table has:
```sql
account_id uuid NOT NULL,
CONSTRAINT conversations_account_fk FOREIGN KEY (account_id)
    REFERENCES nexus.accounts (id) ON DELETE RESTRICT
```

But RLS policies check:
```sql
WITH CHECK (account_id = auth.uid())
```

**This is fundamentally broken because:**
- `auth.uid()` returns the Supabase Auth user UUID (from `auth.users` table)
- `nexus.accounts.id` is a separate UUID with its own schema (auth_issuer, auth_subject, email_normalized)
- There is NO guarantee that `nexus.accounts.id` equals `auth.uid()`
- No trigger automatically sets `account_id`
- The `createConversation()` function doesn't set `account_id` at all

### Evidence:
- Migration 002 defines `nexus.accounts` with its own UUID
- Migration 004 defines `conversations.account_id` with FK to `nexus.accounts`
- RLS policies check `account_id = auth.uid()`
- No migration creates a mapping between `auth.users` and `nexus.accounts`
- No trigger populates `account_id` from `auth.uid()`

### Impact:
- INSERT will fail with foreign key constraint violation
- RLS policies will fail to match because account_id != auth.uid()
- User cannot create conversations
- Database persistence completely broken

### Fix Applied:
**Migration 014:** `014_fix_conversations_account_id.sql`
- Drops FK constraint to nexus.accounts
- Removes unique constraint that includes account_id
- Adds unique constraint on id only
- Adds comment explaining account_id should equal auth.uid()

**Code Fix:** Updated `conversation-service.ts`
- `createConversation()` now sets `account_id = user.id` (Supabase Auth user ID)
- Added error handling for FK constraint violations

### Status:
- ✅ Migration created (014_fix_conversations_account_id.sql)
- ✅ Code updated (conversation-service.ts)
- ⚠️ Migration NOT YET APPLIED to production database
- ⚠️ Requires manual execution in Supabase SQL Editor

---

## CRITICAL DEFECT #2: NEXUS SCHEMA NOT EXPOSED TO DATA API

### Problem:
When attempting to query nexus schema via Supabase JS client:
```
[INFO] Query failed: Invalid schema: nexus
```

### Evidence:
- Test script `test_authenticated_access.js` confirms "Invalid schema: nexus"
- Nexus schema exists in database but not exposed to Supabase Data API
- Supabase Data API by default only exposes `public` schema

### Impact:
- Cannot query nexus.conversations via Supabase JS client
- Cannot query nexus.messages via Supabase JS client
- Cannot perform any database operations
- Complete failure of persistence layer

### Fix Applied:
**Migration 015:** `015_grant_nexus_api_access.sql`
- Grants USAGE on nexus schema to anon and authenticated roles
- Grants SELECT on all tables to anon
- Grants INSERT, UPDATE, DELETE on user tables to authenticated
- Grants USAGE on sequences

### Status:
- ✅ Migration created (015_grant_nexus_api_access.sql)
- ⚠️ Migration NOT YET APPLIED to production database
- ⚠️ Requires manual execution in Supabase SQL Editor

---

## CRITICAL DEFECT #3: NO API PERMISSIONS

### Problem:
Even if schema is exposed, no permissions granted for nexus tables.

### Evidence:
- Default Supabase setup doesn't grant permissions to custom schemas
- No existing migration grants permissions for nexus schema
- Test confirms schema not accessible

### Impact:
- Same as Defect #2 - complete failure

### Fix:
Included in Migration 015 (see above)

### Status:
- ✅ Migration created
- ⚠️ Not yet applied

---

## HIGH DEFECT #4: HISTORY PAGE COMPLETELY MISSING

### Problem:
- Sidebar has "History" navigation item
- No corresponding History page component exists
- No routing for History page
- Users cannot view conversation history

### Evidence:
- Sidebar.tsx line 70: `{ id: 'history', label: 'History', icon: Clock }`
- No `app/history/page.tsx` exists
- No history component in app/components
- MainContent likely shows default home page for history nav

### Impact:
- Users cannot access conversation history
- Cannot reopen old conversations
- UX incomplete
- Core feature claimed in report but not implemented

### Fix:
- Need to implement History page component
- Need to add routing
- Need to load conversations from Supabase
- Need to display conversation list
- Need to allow selecting conversations

### Status:
- ❌ NOT IMPLEMENTED
- ⚠️ PENDING (Step 6 of current task)

---

## MEDIUM DEFECT #5: NO CONVERSATION RESTORATION LOGIC

### Problem:
- No logic to restore active conversation after refresh
- `useConversationManager` loads all conversations but doesn't set active one
- User always starts with no active conversation after refresh

### Evidence:
- `useConversationManager.ts` loads conversations but `activeConversationId` remains null
- No URL-based conversation selection
- No localStorage-based conversation selection
- No "last active conversation" tracking

### Impact:
- After refresh, user sees empty chat
- Must manually select conversation from History (if History existed)
- Poor UX

### Fix:
- Track last active conversation ID
- Restore it after authentication
- Or use URL-based conversation selection
- Or load most recent conversation as active

### Status:
- ❌ NOT IMPLEMENTED
- ⚠️ PENDING (Step 7 of current task)

---

## FILES CHANGED (Phase 2.1 So Far)

### Created:
1. `packages/database-core/migrations/014_fix_conversations_account_id.sql`
2. `packages/database-core/migrations/015_grant_nexus_api_access.sql`
3. `apps/web/test_authenticated_access.js`

### Modified:
1. `apps/web/lib/conversation-service.ts` - Added account_id setting

---

## MIGRATIONS REQUIRED FOR PRODUCTION

To fix the database issues, the following migrations must be manually executed in Supabase SQL Editor:

### Migration 014: Fix conversations.account_id
```sql
-- Removes FK to nexus.accounts since account_id should equal auth.uid()
ALTER TABLE nexus.conversations DROP CONSTRAINT IF EXISTS conversations_account_fk;
ALTER TABLE nexus.conversations DROP CONSTRAINT IF EXISTS conversations_account_id_uk;
ALTER TABLE nexus.conversations ADD CONSTRAINT conversations_id_uk UNIQUE (id);
COMMENT ON COLUMN nexus.conversations.account_id IS 'Supabase Auth user ID (auth.uid()), not nexus.accounts.id';
```

### Migration 015: Grant API Access
```sql
-- Exposes nexus schema to Supabase Data API
GRANT USAGE ON SCHEMA nexus TO anon;
GRANT USAGE ON SCHEMA nexus TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA nexus TO anon;
GRANT SELECT ON ALL TABLES IN SCHEMA nexus TO authenticated;
GRANT INSERT, UPDATE, DELETE ON nexus.conversations TO authenticated;
GRANT INSERT, UPDATE, DELETE ON nexus.messages TO authenticated;
GRANT INSERT, UPDATE, DELETE ON nexus.user_profiles TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA nexus TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA nexus TO authenticated;
```

---

## NEXT STEPS

### Immediate (Required for Production):
1. Execute Migration 014 in Supabase SQL Editor
2. Execute Migration 015 in Supabase SQL Editor
3. Verify migrations applied successfully
4. Test authenticated access with real user account

### Implementation (Current Task):
5. Implement History page component (Step 6)
6. Implement conversation restoration logic (Step 7)
7. Verify authentication/session behavior (Step 3)
8. Run full test matrix (Step 10)

### After Phase 2.1:
9. Document migration requirements in project README
10. Consider automating migration execution in deployment pipeline

---

## CONCLUSION

The Phase 2 implementation has **critical database schema defects** that prevent it from working at all. The previous report incorrectly claimed implementation was complete, but:

- ❌ Database FK constraint broken
- ❌ Schema not exposed to API
- ❌ No API permissions
- ❌ History page missing
- ❌ No conversation restoration

These are **blockers** that must be resolved before any runtime testing can succeed.

**Status:** Phase 2 cannot work until migrations 014 and 015 are applied.
