# SQL FILES INSPECTION REPORT
**Date:** 2026-10-15
**Status:** INSPECTION COMPLETE

---

## A. COMPLETE_SCHEMA.sql Analysis

### File Location
`packages/database-core/migrations/COMPLETE_SCHEMA.sql`

### Safety Assessment
✅ **SAFE TO RUN**

### Safety Features
- Uses `CREATE TABLE IF NOT EXISTS` - won't destroy existing tables
- Uses `CREATE OR REPLACE FUNCTION` - safe for functions
- Uses `DROP TRIGGER IF EXISTS` - safe for triggers
- No `DROP TABLE` statements
- No `DELETE` or `TRUNCATE` statements
- No destructive operations
- Idempotent - can be rerun safely

### Syntax Validation
✅ **NO SYNTAX ERRORS FOUND**

### Tables Created (11 total)
1. nexus.accounts
2. nexus.auth_sessions
3. nexus.user_profiles
4. nexus.conversations
5. nexus.messages
6. nexus.consent_records
7. nexus.memory_records
8. nexus.notification_preferences
9. nexus.library_items
10. nexus.file_metadata
11. nexus.schema_migrations

### Issues Found
❌ **NONE** - Schema file is clean and safe

### Dependencies
- Requires PostgreSQL (provided by Supabase)
- Requires pgcrypto extension (uses CREATE EXTENSION IF NOT EXISTS)
- No external dependencies

---

## B. RLS_POLICIES.sql Analysis

### File Location
`packages/database-core/migrations/RLS_POLICIES.sql`

### Safety Assessment
⚠️ **PARTIALLY SAFE**

### Issues Found

**Issue 1: Missing "TO authenticated" Clause**
- Original file does NOT include `TO authenticated` clauses
- Without this, policies apply to all roles including public
- This is a security issue - policies should be restricted to authenticated users

**Evidence:**
```sql
-- ORIGINAL (packages/database-core/migrations/RLS_POLICIES.sql):
CREATE POLICY "Users can read own profile"
ON nexus.user_profiles FOR SELECT
USING (account_id = auth.uid());
-- Missing: TO authenticated
```

**Issue 2: Not Idempotent**
- Uses `CREATE POLICY` without `IF NOT EXISTS`
- Rerunning will fail with "policy already exists" error
- Should use `DROP POLICY IF EXISTS` first or `CREATE OR REPLACE` pattern

**Evidence:**
```sql
-- CURRENT:
CREATE POLICY "Users can read own profile"
-- Will fail if policy already exists

-- SHOULD BE:
DROP POLICY IF EXISTS "Users can read own profile" ON nexus.user_profiles;
CREATE POLICY "Users can read own profile"
```

**Issue 3: Inconsistent Versions**
- The copy in `docs/RLS_POLICIES.sql` has `TO authenticated` clauses
- The original in `packages/database-core/migrations/RLS_POLICIES.sql` does NOT
- This creates confusion about which version to use

### Syntax Validation
✅ **NO SYNTAX ERRORS**

### Tables with RLS (7 total)
1. nexus.user_profiles
2. nexus.conversations
3. nexus.messages
4. nexus.memory_records
5. nexus.library_items
6. nexus.file_metadata
7. nexus.notification_preferences

### Policies Created (14 total)
- user_profiles: 3 policies (SELECT, INSERT, UPDATE)
- conversations: 4 policies (SELECT, INSERT, UPDATE, DELETE)
- messages: 4 policies (SELECT, INSERT, UPDATE, DELETE)
- memory_records: 4 policies (SELECT, INSERT, UPDATE, DELETE)
- library_items: 4 policies (SELECT, INSERT, UPDATE, DELETE)
- file_metadata: 3 policies (SELECT, INSERT, DELETE)
- notification_preferences: 3 policies (SELECT, INSERT, UPDATE)

---

## C. Overlap Analysis

### COMPLETE_SCHEMA.sql Content
- ✅ Does NOT include any RLS policies
- ✅ Does NOT enable RLS on tables
- ✅ Pure schema, functions, triggers, indexes

### RLS_POLICIES.sql Content
- ✅ Does NOT include any table definitions
- ✅ Does NOT create tables
- ✅ Pure RLS enablement and policies

### Overlap
❌ **NO OVERLAP** - Files are complementary

### Execution Order
1. **FIRST:** COMPLETE_SCHEMA.sql (creates tables)
2. **SECOND:** RLS_POLICIES.sql (enables RLS and creates policies)

---

## D. Required Fixes

### Fix 1: Add "TO authenticated" to All Policies
**Priority:** HIGH (Security)
**Impact:** Without this, policies apply to public role
**Fix:** Add `TO authenticated` to all CREATE POLICY statements

### Fix 2: Make RLS Policies Idempotent
**Priority:** MEDIUM (Usability)
**Impact:** Cannot rerun script without errors
**Fix:** Add `DROP POLICY IF EXISTS` before each CREATE POLICY

### Fix 3: Resolve Version Inconsistency
**Priority:** HIGH (Confusion)
**Impact:** Unclear which version to use
**Fix:** Update original file to match corrected version, remove duplicate

---

## E. Corrected RLS_POLICIES.sql

A corrected version is provided at:
`docs/RLS_POLICIES_CORRECTED.sql`

This version includes:
- ✅ `TO authenticated` on all policies
- ✅ `DROP POLICY IF EXISTS` for idempotency
- ✅ Verification queries at the end

---

## F. Execution Instructions

### Step 1: Apply Schema
```bash
File: packages/database-core/migrations/COMPLETE_SCHEMA.sql
Location: Supabase SQL Editor
Safe to rerun: YES
Estimated time: 30 seconds
```

### Step 2: Apply RLS Policies
```bash
File: docs/RLS_POLICIES_CORRECTED.sql (USE THIS VERSION)
Location: Supabase SQL Editor
Safe to rerun: YES (after fix)
Estimated time: 30 seconds
```

### Verification
```sql
-- Check tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'nexus';

-- Check RLS enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'nexus';

-- Check policies
SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'nexus';
```

---

## G. Summary

### COMPLETE_SCHEMA.sql
- ✅ Safe to run
- ✅ No syntax errors
- ✅ Idempotent
- ✅ No destructive operations
- ✅ Ready to execute

### RLS_POLICYS.sql (Original)
- ⚠️ Missing security clauses
- ⚠️ Not idempotent
- ⚠️ Has inconsistent version
- ❌ Needs correction before use

### Recommendation
1. Use COMPLETE_SCHEMA.sql as-is
2. Use RLS_POLICIES_CORRECTED.sql instead of original
3. Execute in order: Schema first, then RLS
4. Run verification queries after each step

---

**Inspection Status:** COMPLETE
**Ready for Manual Execution:** YES (with corrected RLS file)
