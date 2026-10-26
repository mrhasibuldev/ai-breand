# Authentication & Chat Functionality Fixes

## Summary of Issues Fixed

This document describes the fixes applied to resolve chat functionality issues for authenticated users.

### Issues Addressed

1. **Authentication vs Guest Mode Discrepancy**: Chat messaging and conversation creation worked in Guest Mode but failed when a user was logged in
2. **Chat History Persistence & Retrieval**: History page displayed "No conversations yet" with errors like `Failed to load conversations`
3. **Error Handling and State Reset**: Secondary errors such as `ConversationManager failed to create conversation` and `Error finding account`

### Root Cause

The primary issue was in the Row Level Security (RLS) policies in Supabase. The policies were incorrectly checking `account_id = auth.uid()`, but:
- `account_id` is a UUID from the `nexus.accounts` table
- `auth.uid()` is the Supabase Auth user ID
- These are different values - the application maps them via the `auth_subject` field in the accounts table

### Fixes Applied

#### 1. RLS Policy Corrections (Critical - Must Apply to Supabase)

**File**: `packages/database-core/migrations/RLS_POLICIES.sql`

All RLS policies have been updated to correctly check account ownership by joining with the accounts table:

**Before (Incorrect)**:
```sql
USING (account_id = auth.uid())
```

**After (Correct)**:
```sql
USING (
  account_id IN (
    SELECT id FROM nexus.accounts 
    WHERE auth_subject = auth.uid()
  )
)
```

**For messages table (with conversation join)**:
```sql
USING (
  conversation_id IN (
    SELECT c.id FROM nexus.conversations c
    JOIN nexus.accounts a ON c.account_id = a.id
    WHERE a.auth_subject = auth.uid() AND c.deleted_at IS NULL
  )
)
```

**Tables Updated**:
- `nexus.accounts` (new RLS policies added)
- `nexus.user_profiles`
- `nexus.conversations`
- `nexus.messages`
- `nexus.memory_records`
- `nexus.library_items`
- `nexus.file_metadata`
- `nexus.notification_preferences`

#### 2. Error Handling Improvements

**File**: `apps/web/app/components/ChatInterface.tsx`

- Added try-catch block around `createConversation()` call
- Added try-catch around `addMessage()` call with proper error recovery
- Input value is restored on error so user can retry
- Better error logging and state management

**File**: `apps/web/app/components/useConversationManager.ts`

- `createConversation()` now throws errors instead of returning null
- `addMessage()` now throws errors instead of silently failing
- `loadConversationsFromSupabase()` now throws errors to allow UI error handling
- Better error propagation for debugging

**File**: `apps/web/app/components/HistoryPage.tsx`

- Added error state display
- Added retry button for failed conversation loads
- Better error messaging for users

### Required Actions

#### Step 1: Apply RLS Policy Changes to Supabase

**CRITICAL**: You must apply the updated RLS policies to your Supabase database for the fixes to work.

1. Open Supabase Dashboard
2. Navigate to SQL Editor
3. Open the file: `packages/database-core/migrations/RLS_POLICIES.sql`
4. Run the entire SQL script in the SQL Editor
5. Verify that all policies were created successfully

#### Step 2: Verify Account Creation

The application automatically creates accounts when users first authenticate, but you may need to verify:

1. Check the `nexus.accounts` table to ensure it has entries
2. Verify that `auth_subject` field matches the Supabase user IDs
3. Check that existing users have corresponding account records

#### Step 3: Test the Application

1. Start the development server: `pnpm dev`
2. Sign in with an authenticated user
3. Try creating a new conversation
4. Verify that the conversation persists and appears in the History page
5. Test sending messages and verify they persist
6. Check browser console for any remaining errors

### How the Fix Works

1. **User Authentication**: When a user signs in, the application gets their Supabase user ID via `auth.uid()`

2. **Account Resolution**: The `getOrCreateAccountId()` function in `conversation-service.ts`:
   - First checks if an account exists with `auth_subject = auth.uid()`
   - If not found, checks by email and links the account
   - If still not found, creates a new account with `auth_subject = auth.uid()`

3. **Conversation Creation**: When creating a conversation:
   - The resolved `account_id` (from nexus.accounts) is used
   - RLS policies verify the conversation's `account_id` belongs to the authenticated user by checking if the account's `auth_subject` matches `auth.uid()`

4. **Message Persistence**: Messages are linked to conversations, and RLS policies verify the conversation belongs to the user before allowing message operations

### Troubleshooting

If issues persist after applying the fixes:

1. **Check RLS Policies**:
   ```sql
   SELECT 
     schemaname,
     tablename,
     policyname,
     cmd,
     qual
   FROM pg_policies 
   WHERE schemaname = 'nexus'
   ORDER BY tablename, policyname;
   ```

2. **Check Account Records**:
   ```sql
   SELECT id, auth_subject, email_normalized, status 
   FROM nexus.accounts;
   ```

3. **Check Conversation Records**:
   ```sql
   SELECT id, account_id, title, status 
   FROM nexus.conversations;
   ```

4. **Check Browser Console**: Look for detailed error messages in the browser's developer console

5. **Verify Supabase Session**: Ensure the user is properly authenticated and the session is active

### Files Modified

1. `packages/database-core/migrations/RLS_POLICIES.sql` - RLS policy corrections
2. `apps/web/app/components/ChatInterface.tsx` - Error handling improvements
3. `apps/web/app/components/useConversationManager.ts` - Error propagation
4. `apps/web/app/components/HistoryPage.tsx` - Error state display

### Notes

- Guest mode (unauthenticated) continues to work as before with in-memory state
- All authenticated operations now properly respect user ownership via RLS
- Error handling provides better feedback to users and developers
- The fixes maintain backward compatibility with existing data structures
