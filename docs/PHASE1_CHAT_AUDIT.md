# PHASE 1 — CHAT HISTORY AUDIT REPORT

## EXISTING CHAT ARCHITECTURE

### 1. Frontend Chat Flow

**Component Structure:**
- `ChatInterface.tsx` - Main chat UI component
- `useConversationManager.ts` - Conversation state management hook
- `conversation-types.ts` - TypeScript type definitions

**Current State Management:**
- **Storage Type**: In-memory only (React useState)
- **Persistence**: NONE - all conversations lost on refresh
- **Conversation Manager**: Manages conversations in a Map structure
- **Message Storage**: Each conversation has an array of messages

**Chat Flow:**
```
User types message
  ↓
handleSubmit() in ChatInterface
  ↓
createConversation() if no active conversation
  ↓
handleSendMessage()
  ↓
addMessage() - saves to local state
  ↓
Fetch to ML service (http://127.0.0.1:8000/orchestrate)
  ↓
Receive AI response
  ↓
addMessage() - saves AI response to local state
  ↓
UI renders messages
```

### 2. Database Structure (Supabase/PostgreSQL)

**Existing Tables:**

#### `nexus.conversations`
```sql
- id (uuid, PK)
- account_id (uuid, FK to accounts)
- status (text: 'active', 'ended', 'deleted')
- title (varchar(160))
- started_at (timestamptz)
- ended_at (timestamptz)
- deleted_at (timestamptz)
```

**Constraints:**
- UNIQUE constraint: (account_id, id)
- Foreign key to accounts.id
- Status check constraint
- Ended_at must be >= started_at
- Deleted state requires deleted_at

**Indexes:**
- (account_id, started_at DESC)

#### `nexus.messages`
```sql
- id (uuid, PK)
- conversation_id (uuid, FK to conversations)
- sequence_no (integer)
- sender_role (text: 'user', 'assistant')
- content (text)
- content_status (text: 'active', 'redacted', 'deleted', 'blocked')
- created_at (timestamptz)
- deleted_at (timestamptz)
```

**Constraints:**
- UNIQUE constraint: (conversation_id, sequence_no)
- Foreign key to conversations.id
- Sequence_no must be > 0
- Role check constraint
- Content not empty
- Content status check constraint

**Indexes:**
- (conversation_id, sequence_no)

### 3. Row Level Security (RLS) Policies

**Conversations RLS:**
- ✅ Users can READ own conversations (account_id = auth.uid())
- ✅ Users can INSERT own conversations (account_id = auth.uid())
- ✅ Users can UPDATE own conversations (account_id = auth.uid())
- ✅ Users can DELETE own conversations (account_id = auth.uid())

**Messages RLS:**
- ✅ Users can READ messages from own conversations (via conversation.account_id = auth.uid())
- ✅ Users can INSERT messages to own conversations (via conversation.account_id = auth.uid())
- ✅ Users can UPDATE own messages (via conversation.account_id = auth.uid())
- ✅ Users can DELETE own messages (via conversation.account_id = auth.uid())

**Security Assessment:**
- ✅ User isolation is enforced at database level
- ✅ User A cannot access User B's conversations
- ✅ User A cannot access User B's messages
- ✅ All queries must be authenticated (TO authenticated)

### 4. Authentication

**Current State:**
- **Authentication Provider**: DevAuthService (in-memory mock)
- **Session Storage**: In-memory (SliceStore)
- **Production Status**: Not connected to Supabase Auth yet
- **Auth State**: Currently uses mock authentication

**Limitation:**
- DATABASE_URL is configured but auth.uid() will not work without Supabase Auth session
- RLS policies require `auth.uid()` which returns null without Supabase Auth

### 5. API Routes

**Database-Backed Routes:**
- `apps/api/src/routes/profile.ts` - Profile CRUD
- `apps/api/src/routes/conversations.ts` - Conversation CRUD (IF DATABASE_URL configured)

**Current Status:**
- API checks for DATABASE_URL before loading database routes
- If DATABASE_URL not set, database routes are skipped
- API currently runs without database routes (DATABASE_URL not loaded by pnpm dev)

### 6. Frontend API Client

**Location:** `apps/web/lib/api-client.ts`

**Current Behavior:**
- Direct fetch to ML service for AI responses
- No API calls to backend for conversation/message persistence
- All conversation state is local

### 7. Current Issues

**Issue 1: No Persistence**
- Conversations exist only in React state
- All history lost on page refresh
- No database integration

**Issue 2: Database Not Connected**
- DATABASE_URL in .env but not loaded by API
- API runs without database routes
- Cannot persist conversations even if frontend wanted to

**Issue 3: Authentication Not Connected**
- RLS policies require Supabase Auth
- auth.uid() will be null without proper auth session
- Cannot enforce user isolation

**Issue 4: No Backend API Usage**
- Frontend calls ML service directly
- No conversation/message API calls
- Cannot leverage existing database tables

---

## PHASE 1 AUDIT CONCLUSION

### What Exists:
- ✅ Database tables (conversations, messages)
- ✅ Proper schema with constraints
- ✅ RLS policies for user isolation
- ✅ Frontend chat UI (ChatInterface)
- ✅ Conversation state management (useConversationManager)
- ✅ Message types

### What's Missing:
- ❌ Database connection in API (DATABASE_URL not loaded)
- ❌ Supabase Auth integration
- ❌ Backend API route usage
- ❌ Conversation persistence to database
- ❌ Message persistence to database
- ❌ History loading from database
- ❌ Refresh persistence

### Database Schema Assessment:
- ✅ Sufficient for requirements
- ✅ No additional tables needed
- ✅ No schema changes needed
- ❌ Just need to connect and use existing tables

### RLS Assessment:
- ✅ Policies are correct
- ✅ User isolation enforced
- ❌ Requires Supabase Auth to work (auth.uid())

---

## RECOMMENDED IMPLEMENTATION APPROACH

### Option A: Full Supabase Integration (Requires DATABASE_URL + Auth)
1. Fix DATABASE_URL loading in API
2. Add Supabase Auth client to frontend
3. Create API routes for conversations/messages
4. Connect frontend to API
5. Persist conversations/messages

### Option B: Mock Persistence for Development (Faster)
1. Use localStorage for persistence
2. Keep existing in-memory state
3. Sync to localStorage on changes
4. Restore from localStorage on load
5. Later migrate to Supabase

### Option C: Hybrid (Recommended for Current State)
1. Fix DATABASE_URL loading first
2. Keep in-memory state for now
3. Add persistence layer when DATABASE_URL works
4. Maintain ability to switch to localStorage fallback

---

## CRITICAL BLOCKER

**DATABASE_URL Loading Issue:**
- .env file exists with DATABASE_URL
- API doesn't load environment variables from .env
- Database routes are skipped
- Cannot implement persistence without database connection

**Authentication Issue:**
- RLS requires Supabase Auth
- Current auth is mock (DevAuthService)
- auth.uid() will be null without Supabase Auth session
- Cannot use database tables effectively without auth

---

## NEXT STEPS (Recommended Order)

1. **Fix DATABASE_URL loading** in API (pnpm dev environment)
2. **Test database connection** and migration
3. **Implement API routes** for conversations/messages
4. **Add Supabase Auth** to frontend (or use mock for development)
5. **Connect frontend to API** for persistence
6. **Test refresh persistence**
7. **Test user isolation**

---

## DATABASE SCHEMA ADEQUACY

**Existing Schema:**
- ✅ conversations table - PERFECT
- ✅ messages table - PERFECT
- ✅ RLS policies - PERFECT
- ✅ Indexes - PERFECT
- ✅ Constraints - PERFECT

**Conclusion:**
NO database schema changes needed. The existing structure is exactly what we need. Just need to connect and use it.
