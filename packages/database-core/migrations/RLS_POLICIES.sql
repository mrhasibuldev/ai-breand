-- NEXUSAI - ROW LEVEL SECURITY (RLS) POLICIES
-- Run this in Supabase SQL Editor after the main schema is created
-- FIXED VERSION: Includes TO authenticated and idempotent DROP statements

-- ============================================
-- ENABLE RLS ON ALL USER-OWNED TABLES
-- ============================================

ALTER TABLE nexus.accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.memory_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.library_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.file_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus.notification_preferences ENABLE ROW LEVEL SECURITY;

-- ============================================
-- ACCOUNTS RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own account" ON nexus.accounts;
CREATE POLICY "Users can read own account"
ON nexus.accounts FOR SELECT
TO authenticated
USING (auth_subject = auth.uid());

DROP POLICY IF EXISTS "Users can insert own account" ON nexus.accounts;
CREATE POLICY "Users can insert own account"
ON nexus.accounts FOR INSERT
TO authenticated
WITH CHECK (auth_subject = auth.uid());

DROP POLICY IF EXISTS "Users can update own account" ON nexus.accounts;
CREATE POLICY "Users can update own account"
ON nexus.accounts FOR UPDATE
TO authenticated
USING (auth_subject = auth.uid())
WITH CHECK (auth_subject = auth.uid());

-- ============================================
-- USER PROFILES RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own profile" ON nexus.user_profiles;
CREATE POLICY "Users can read own profile"
ON nexus.user_profiles FOR SELECT
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can insert own profile" ON nexus.user_profiles;
CREATE POLICY "Users can insert own profile"
ON nexus.user_profiles FOR INSERT
TO authenticated
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can update own profile" ON nexus.user_profiles;
CREATE POLICY "Users can update own profile"
ON nexus.user_profiles FOR UPDATE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
)
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

-- ============================================
-- CONVERSATIONS RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own conversations" ON nexus.conversations;
CREATE POLICY "Users can read own conversations"
ON nexus.conversations FOR SELECT
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can insert own conversations" ON nexus.conversations;
CREATE POLICY "Users can insert own conversations"
ON nexus.conversations FOR INSERT
TO authenticated
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can update own conversations" ON nexus.conversations;
CREATE POLICY "Users can update own conversations"
ON nexus.conversations FOR UPDATE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
)
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can delete own conversations" ON nexus.conversations;
CREATE POLICY "Users can delete own conversations"
ON nexus.conversations FOR DELETE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

-- ============================================
-- MESSAGES RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own conversation messages" ON nexus.messages;
CREATE POLICY "Users can read own conversation messages"
ON nexus.messages FOR SELECT
TO authenticated
USING (
  conversation_id IN (
    SELECT c.id FROM nexus.conversations c
    JOIN nexus.accounts a ON c.account_id = a.id
    WHERE a.auth_subject = auth.uid() AND c.deleted_at IS NULL
  )
);

DROP POLICY IF EXISTS "Users can insert to own conversations" ON nexus.messages;
CREATE POLICY "Users can insert to own conversations"
ON nexus.messages FOR INSERT
TO authenticated
WITH CHECK (
  conversation_id IN (
    SELECT c.id FROM nexus.conversations c
    JOIN nexus.accounts a ON c.account_id = a.id
    WHERE a.auth_subject = auth.uid() AND c.deleted_at IS NULL
  )
);

DROP POLICY IF EXISTS "Users can update own messages" ON nexus.messages;
CREATE POLICY "Users can update own messages"
ON nexus.messages FOR UPDATE
TO authenticated
USING (
  conversation_id IN (
    SELECT c.id FROM nexus.conversations c
    JOIN nexus.accounts a ON c.account_id = a.id
    WHERE a.auth_subject = auth.uid() AND c.deleted_at IS NULL
  )
);

DROP POLICY IF EXISTS "Users can delete own messages" ON nexus.messages;
CREATE POLICY "Users can delete own messages"
ON nexus.messages FOR DELETE
TO authenticated
USING (
  conversation_id IN (
    SELECT c.id FROM nexus.conversations c
    JOIN nexus.accounts a ON c.account_id = a.id
    WHERE a.auth_subject = auth.uid() AND c.deleted_at IS NULL
  )
);

-- ============================================
-- MEMORY RECORDS RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own memory" ON nexus.memory_records;
CREATE POLICY "Users can read own memory"
ON nexus.memory_records FOR SELECT
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can insert own memory" ON nexus.memory_records;
CREATE POLICY "Users can insert own memory"
ON nexus.memory_records FOR INSERT
TO authenticated
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can update own memory" ON nexus.memory_records;
CREATE POLICY "Users can update own memory"
ON nexus.memory_records FOR UPDATE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
)
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can delete own memory" ON nexus.memory_records;
CREATE POLICY "Users can delete own memory"
ON nexus.memory_records FOR DELETE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

-- ============================================
-- LIBRARY ITEMS RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own library items" ON nexus.library_items;
CREATE POLICY "Users can read own library items"
ON nexus.library_items FOR SELECT
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can insert own library items" ON nexus.library_items;
CREATE POLICY "Users can insert own library items"
ON nexus.library_items FOR INSERT
TO authenticated
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can update own library items" ON nexus.library_items;
CREATE POLICY "Users can update own library items"
ON nexus.library_items FOR UPDATE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
)
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can delete own library items" ON nexus.library_items;
CREATE POLICY "Users can delete own library items"
ON nexus.library_items FOR DELETE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

-- ============================================
-- FILE METADATA RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own files" ON nexus.file_metadata;
CREATE POLICY "Users can read own files"
ON nexus.file_metadata FOR SELECT
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can insert own files" ON nexus.file_metadata;
CREATE POLICY "Users can insert own files"
ON nexus.file_metadata FOR INSERT
TO authenticated
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can delete own files" ON nexus.file_metadata;
CREATE POLICY "Users can delete own files"
ON nexus.file_metadata FOR DELETE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

-- ============================================
-- NOTIFICATION PREFERENCES RLS
-- ============================================

DROP POLICY IF EXISTS "Users can read own preferences" ON nexus.notification_preferences;
CREATE POLICY "Users can read own preferences"
ON nexus.notification_preferences FOR SELECT
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can insert own preferences" ON nexus.notification_preferences;
CREATE POLICY "Users can insert own preferences"
ON nexus.notification_preferences FOR INSERT
TO authenticated
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

DROP POLICY IF EXISTS "Users can update own preferences" ON nexus.notification_preferences;
CREATE POLICY "Users can update own preferences"
ON nexus.notification_preferences FOR UPDATE
TO authenticated
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
)
WITH CHECK (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
);

-- ============================================
-- COMPLETE
-- ============================================

-- Verify RLS policies created
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies 
WHERE schemaname = 'nexus'
ORDER BY tablename, policyname;
