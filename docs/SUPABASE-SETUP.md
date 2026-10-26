# SUPABASE DATABASE SETUP GUIDE

## Prerequisites
- Supabase project: qzfynpuvbybqgqmbaccu
- Access to Supabase Dashboard: https://app.supabase.com
- No data loss will occur (uses CREATE TABLE IF NOT EXISTS)

---

## Step 1: Apply Database Schema

### File Location
`packages/database-core/migrations/COMPLETE_SCHEMA.sql`

### Execution Instructions
1. Open Supabase Dashboard: https://app.supabase.com
2. Select project: **qzfynpuvbybqgqmbaccu**
3. Click **SQL Editor** in the left sidebar
4. Click **New query**
5. Copy the entire contents of `COMPLETE_SCHEMA.sql`
6. Paste into the SQL Editor
7. Click **Run** (or press Ctrl+Enter)

### What This Creates
- **Schema:** `nexus` schema
- **Extensions:** pgcrypto
- **Functions:** set_updated_at(), prevent_history_mutation()
- **Tables (11 total):**
  - nexus.accounts
  - nexus.auth_sessions
  - nexus.user_profiles
  - nexus.conversations
  - nexus.messages
  - nexus.consent_records
  - nexus.memory_records
  - nexus.notification_preferences
  - nexus.library_items
  - nexus.file_metadata
  - nexus.schema_migrations
- **Indexes:** Performance indexes on key columns
- **Triggers:** Automatic updated_at timestamp management

### Verification
After running, you should see a table list at the bottom showing all 11 tables.

---

## Step 2: Apply RLS Policies

### File Location
`packages/database-core/migrations/RLS_POLICIES.sql`

### Execution Instructions
1. Still in SQL Editor
2. Click **New query** (or clear current query)
3. Copy the entire contents of `RLS_POLICIES.sql`
4. Paste into the SQL Editor
5. Click **Run** (or press Ctrl+Enter)

### What This Creates
- **RLS Policies (14 total):**
  - user_profiles: Read/Insert/Update own profile
  - conversations: Read/Insert/Update/Delete own conversations
  - messages: Read/Insert/Update/Delete own conversation messages
  - memory_records: Read/Insert/Update/Delete own memory
  - library_items: Read/Insert/Update/Delete own items
  - file_metadata: Read/Insert/Delete own files
  - notification_preferences: Read/Insert/Update own preferences

### Security
- Policies ensure users can only access their own data
- Cross-user access is automatically blocked by database
- Service role bypasses RLS (used by backend API)

### Verification
```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'nexus';

-- Check policies exist
SELECT schemaname, tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'nexus';
```

---

## Step 3: Configure Supabase Storage (Optional for Profile Pictures)

### Create Bucket
1. Go to **Storage** in Supabase Dashboard
2. Click **Create a new bucket**
3. Name: `avatars`
4. Public bucket: **No** (private with signed URLs)
5. Click **Create bucket**

### Bucket Policies
1. Click on the `avatars` bucket
2. Go to **Policies**
3. Add policy for authenticated users:
   - **SELECT:** Allow read access to owner
   - **INSERT:** Allow upload to owner
   - **UPDATE:** Allow update by owner
   - **DELETE:** Allow delete by owner

### Policy SQL Example
```sql
-- Allow authenticated users to upload avatars
CREATE POLICY "Users can upload avatars"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow users to read their own avatars
CREATE POLICY "Users can read own avatars"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'avatars'
  AND auth.uid()::text = (storage.foldername(name))[1]
);
```

---

## Execution Order
1. ✅ COMPLETE_SCHEMA.sql (must run first)
2. ✅ RLS_POLICIES.sql (must run after schema)
3. ⚠️ Storage setup (optional, for profile pictures)

---

## Troubleshooting

### Error: "schema nexus does not exist"
**Solution:** The COMPLETE_SCHEMA.sql creates the schema. Ensure you ran it first.

### Error: "relation already exists"
**Solution:** SQL uses CREATE TABLE IF NOT EXISTS, so this should not occur. If it does, the table already exists (safe to ignore).

### Error: "permission denied"
**Solution:** Ensure you are logged in as the project owner with admin privileges.

### RLS Policies Not Working
**Solution:** 
1. Verify schema is applied first
2. Check that RLS is enabled on tables: `SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'nexus';`
3. Verify policies exist: `SELECT * FROM pg_policies WHERE schemaname = 'nexus';`

---

## Verification Script

Run this after both SQL files to verify setup:

```sql
-- Verify all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'nexus' 
ORDER BY table_name;

-- Verify RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'nexus' 
ORDER BY tablename;

-- Verify policies exist
SELECT tablename, policyname, permissive, roles, cmd 
FROM pg_policies 
WHERE schemaname = 'nexus' 
ORDER BY tablename, policyname;
```

Expected results:
- 11 tables listed
- All tables show `rowsecurity = true`
- 14 policies listed

---

## Important Notes

### No Data Loss
- Uses CREATE TABLE IF NOT EXISTS
- Safe to run multiple times
- Will not drop existing tables
- Will not delete existing data

### Supabase Project
- Project: qzfynpuvbybqgqmbaccu
- URL: https://qzfynpuvbybqgqmbaccu.supabase.co
- Schema: nexus

### Security
- RLS policies enforce user ownership
- Backend uses service role key for privileged operations
- Frontend uses anon key with RLS protection
- Never expose service role key in frontend

---

## Next Steps After Database Setup

1. **Restart dev server** (if needed)
2. **Test signup/login** with real Supabase Auth
3. **Implement profile persistence** in backend API
4. **Connect frontend to profile API**
5. **Implement avatar upload** with Supabase Storage
6. **Test end-to-end profile save/load**

---

**Setup Guide Complete**
