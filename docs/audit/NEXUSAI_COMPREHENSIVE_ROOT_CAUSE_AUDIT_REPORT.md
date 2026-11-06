# NEXUSAI COMPREHENSIVE ROOT CAUSE AUDIT REPORT

**Date**: 2026-11-06
**Type**: Root Cause Analysis
**Scope**: Mobile Profile Editing, Authentication, Timeout, AI Service, Conversation System

---

## A. EXECUTIVE SUMMARY

**Issues Investigated**:
1. Settings → Account → Profile Editing
2. Authentication Failed
3. Request Timeout
4. AI Service Unavailable
5. Messenger/Conversation System
6. Profile Design & Settings UI Regression

**Root Causes Identified**:
1. **Profile Edit Stacking Context Issue**: ProfileEdit rendered inside Settings dialog creates stacking context problem
2. **Authentication Working**: Auth flow is correct; HTTP 200 responses indicate success
3. **Timeout Configuration**: 15-second timeout may be too aggressive for some operations
4. **AI Service Status**: Service availability needs verification
5. **Conversation Loading**: Backend integration appears correct

**Priority Fixes**:
1. **HIGH**: Fix Settings Profile Edit stacking context
2. **MEDIUM**: Verify AI service availability
3. **LOW**: Adjust timeout configuration if needed

---

## B. INITIAL GIT STATUS

### B.1 Modified Files
- `apps/api/src/routes/storage.ts`
- `apps/web/app/components/MainContent.tsx`
- `apps/web/app/components/Sidebar.tsx`
- `apps/web/app/globals.css`
- `apps/web/app/layout.tsx`
- `apps/web/app/page.tsx`
- `packages/ai-core/ml-service/__pycache__/main.cpython-314.pyc`
- `packages/ai-core/models/checkpoints_medium/final_model.pt`
- `packages/ai-core/training/__pycache__/checkpoint.cpython-314.pyc`
- `packages/ai-core/training/__pycache__/pipeline.cpython-314.pyc`

### B.2 New Components
- `apps/web/app/components/LogoutConfirmDialog.tsx`
- `apps/web/app/components/MobileProfileScreen.tsx`
- `apps/web/app/components/MobileSettingsDetailScreen.tsx`
- `apps/web/app/components/ProfileMenu.tsx`
- `apps/web/app/components/Settings.tsx`
- `apps/web/app/components/ThemeProvider.tsx`

### B.3 Recent Changes Preserved
- Profile Edit z-index fix (3000 → 3500)
- Dark mode implementation
- Mobile Profile Screen
- Mobile Settings Detail Screen
- Theme Provider

**All previous changes will be preserved.**

---

## C. ISSUE 1: SETTINGS → ACCOUNT → PROFILE EDITING

### C.1 Problem Description
The user reports:
- Main mobile Profile → Profile Editing now works correctly
- Settings → Account → Profile → Edit Profile does not work reliably
- Sometimes the option appears after a significant delay
- Clicking Edit Profile does not reliably open the editor

### C.2 Root Cause Analysis

**Current Implementation**:

In `Settings.tsx` (lines 159-173):
```tsx
{/* Profile Edit Dialog */}
{isProfileEditOpen && (
  <ProfileEdit
    initialName={editingProfileName}
    initialEmail={editingProfileEmail}
    initialPhotoUrl={editingProfilePhoto}
    onSave={(name, email, photoUrl) => {
      setEditingProfileName(name);
      setEditingProfileEmail(email);
      setEditingProfilePhoto(photoUrl);
      onProfileSave(name, email, photoUrl);
      setIsProfileEditOpen(false);
    }}
    onClose={() => setIsProfileEditOpen(false)}
  />
)}
```

**Stacking Context Problem**:

1. Settings Overlay: z-index: 3200
2. Settings Dialog: position: fixed
3. ProfileEdit Overlay: z-index: 3500 (INSIDE Settings dialog)

**The Issue**:
Since ProfileEdit is rendered INSIDE the Settings dialog as a child component, it's affected by the parent's stacking context. The z-index: 3500 is relative to the Settings dialog's stacking context, not the global stacking context. This means:

- On mobile, Settings dialog is full-screen (100vw × 100vh)
- ProfileEdit is rendered inside this full-screen container
- Even with z-index: 3500, it's still clipped by the Settings dialog's overflow/border
- The editor may not be visible or may be partially hidden

**Comparison with Working Implementation**:

In `page.tsx`, ProfileEdit is rendered at the root level:
```tsx
{isProfileEditOpen && (
  <ProfileEdit
    initialName={profileName}
    initialEmail={profileEmail}
    initialPhotoUrl={profilePhoto}
    onSave={handleProfileSave}
    onClose={() => setIsProfileEditOpen(false)}
  />
)}
```

This places ProfileEdit in the global stacking context at z-index: 3500, which is above:
- Mobile Profile Screen: z-index: 3400
- Settings Overlay: z-index: 3200

### C.3 Affected Files
- `apps/web/app/components/Settings.tsx` (lines 159-173, 181-187)
- `apps/web/app/page.tsx` (needs callback prop)
- `apps/web/app/globals.css` (z-index values are correct)

### C.4 Proposed Fix

**Approach**: Move ProfileEdit rendering to page level

1. Add `onProfileEditRequest` callback to Settings props
2. Remove ProfileEdit rendering from inside Settings
3. Render ProfileEdit at page level when `isProfileEditOpen` is true
4. Close Settings dialog when ProfileEdit opens (optional, for cleaner UX)

**Why This Works**:
- ProfileEdit will be in global stacking context at z-index: 3500
- Not affected by Settings dialog's stacking context
- Consistent with the working mobile profile implementation

**Regression Risk**: LOW
- Same pattern as mobile profile
- No logic changes to ProfileEdit component
- Settings dialog behavior unchanged

---

## D. ISSUE 2: AUTHENTICATION FAILED

### D.1 Problem Description
Observed console errors:
- Authentication failed
- ConversationManager failed to load conversations
- File: `backend-conversation.ts`
- Locations: approximately lines 46 and 71

Browser shows:
- `/api/v1/auth/session` returning HTTP 200
- `/api/v1/profile` returning HTTP 200
- ChatInterface reports `authenticated: false`

### D.2 Root Cause Analysis

**Authentication Flow Investigation**:

1. **Session Check** (`backend-auth.ts` lines 111-122):
```typescript
export async function getSession(): Promise<SessionResponse> {
  const response = await fetchWithTimeout(`${API_BASE}/api/v1/auth/session`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    return { authenticated: false };
  }

  return response.json();
}
```

2. **AuthContext** (`AuthContext.tsx` lines 46-55):
```typescript
const session = await getSession();
if (session.authenticated && session.account_id && session.email) {
  setUser({
    id: session.account_id,
    email: session.email,
  });
} else {
  setUser(null);
}
```

3. **User Reports**: HTTP 200 from `/api/v1/auth/session` and `/api/v1/profile`

**Analysis**:
The authentication flow is correctly implemented. If the endpoints return HTTP 200 and the user is authenticated, `AuthContext` should set `user` state correctly.

**Possible Issues**:
1. **Response Format**: The backend may return `{ authenticated: false }` even with HTTP 200
2. **Session Expiration**: Session may have expired between initial load and conversation loading
3. **Cookie Domain/Path**: Cookies may not be sent correctly to all API endpoints
4. **Backend Configuration**: Backend auth middleware may be misconfigured

**Not a Frontend Bug**:
The frontend authentication logic is correct. The issue is likely in:
- Backend session validation
- Cookie configuration
- API response format

### D.3 Affected Files
- `apps/web/lib/backend-auth.ts` (logic correct)
- `apps/web/app/components/AuthContext.tsx` (logic correct)
- Backend API routes (need verification)

### D.4 Proposed Fix

**Frontend**: No changes needed - logic is correct

**Backend Investigation Required**:
1. Verify `/api/v1/auth/session` response format
2. Verify cookie domain/path configuration
3. Verify session expiration logic
4. Verify auth middleware

**Priority**: HIGH (backend issue)
**Frontend Priority**: LOW (no frontend fix needed)

---

## E. ISSUE 3: REQUEST TIMEOUT

### E.1 Problem Description
Observed errors:
- Request timeout
- `backend-conversation.ts`
- Locations: approximately lines 32 and 54

### E.2 Root Cause Analysis

**Timeout Configuration**:

In `backend-conversation.ts` (line 8):
```typescript
const REQUEST_TIMEOUT = 15000; // 15 seconds
```

In `backend-auth.ts` (line 9):
```typescript
const REQUEST_TIMEOUT = 15000; // 15 seconds
```

**Timeout Implementation** (lines 40-58):
```typescript
async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = REQUEST_TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timeout');
    }
    throw error;
  }
}
```

**Analysis**:
The timeout implementation is correct. 15 seconds is a reasonable timeout for most API operations.

**Possible Timeout Causes**:
1. **Backend Unavailable**: API server at `http://127.0.0.1:4000` may be down
2. **Database Latency**: Database queries may be slow
3. **Network Issues**: Local network issues
4. **Long-Running Operations**: Some operations may legitimately take >15s

**Not a Frontend Bug**:
The timeout implementation is correct. The timeout indicates a backend or infrastructure issue.

### E.3 Affected Files
- `apps/web/lib/backend-conversation.ts` (timeout config correct)
- `apps/web/lib/backend-auth.ts` (timeout config correct)

### E.4 Proposed Fix

**Frontend**: No changes needed - timeout implementation is correct

**Backend Investigation Required**:
1. Verify API server is running and responsive
2. Check database query performance
3. Add backend logging for slow operations
4. Consider increasing timeout only if operations legitimately need >15s

**Priority**: MEDIUM (depends on backend investigation)
**Frontend Priority**: LOW (no frontend fix needed)

---

## F. ISSUE 4: AI SERVICE UNAVAILABLE

### F.1 Problem Description
Observed error:
`Guest request failed: Error: AI service unavailable`
Location: `ChatInterface.tsx`, approximately line 261

Additional console information:
- Guest message submission is attempted
- `authenticated: false`
- `activeConversationId: null`

### F.2 Root Cause Analysis

**AI Request Flow** (ChatInterface.tsx lines 235-245):
```typescript
const response = await fetch('http://localhost:4000/api/v1/ai/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  signal: abortControllerRef.current.signal,
  body: JSON.stringify({
    message: userMessage,
    conversationId: 'guest',
    context: conversationHistory,
  }),
});
```

**Error Handling** (lines 250-261):
```typescript
if (!response.ok) {
  const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));

  // Distinguish between different error types
  if (response.status === 502) {
    throw new Error('AI service unavailable');
  } else if (response.status === 504) {
    throw new Error('AI service timeout');
  } else if (response.status === 500) {
    throw new Error('Backend server error');
  } else if (response.status === 401) {
    throw new Error('Authentication required');
  } else {
    throw new Error(errorData.error || 'AI service error');
  }
}
```

**Analysis**:
The error "AI service unavailable" means the backend returned HTTP 502 (Bad Gateway). This indicates:
1. The backend API server is running
2. The backend tried to reach the AI/ML service
3. The AI/ML service is not responding

**Not a Frontend Bug**:
The frontend correctly sends the request and handles the 502 error. The issue is in the backend-to-ML service connection.

### F.3 Affected Files
- `apps/web/app/components/ChatInterface.tsx` (error handling correct)
- Backend AI route (need verification)
- Python ML service (need verification)

### F.4 Proposed Fix

**Frontend**: No changes needed - error handling is correct

**Backend Investigation Required**:
1. Verify Python ML service is running
2. Verify backend AI route configuration
3. Check ML service logs
4. Verify backend-to-ML service connection

**Priority**: HIGH (service unavailable)
**Frontend Priority**: LOW (no frontend fix needed)

---

## G. ISSUE 5: MESSENGER / CONVERSATION SYSTEM

### G.1 Problem Description
The user reports that Messenger conversations are not working correctly.

Console shows:
- `[ChatInterface] Found pending message from homepage: hello`
- `[ConversationManager] Loaded conversations from backend: 57`

### G.2 Root Cause Analysis

**Conversation Loading** (useConversationManager.ts lines 25-67):
```typescript
const loadConversationsFromBackend = useCallback(async () => {
  if (!isAuthenticated) {
    console.log('[ConversationManager] Not authenticated, skipping load');
    return;
  }

  setLoading(true);
  try {
    const backendConversations = await backendConversationService.listConversations();

    // Convert backend conversations to local format
    const convMap = new Map<string, Conversation>();
    for (const conv of backendConversations) {
      convMap.set(conv.id, {
        id: conv.id,
        title: conv.title,
        messages: [], // Messages loaded separately
        createdAt: new Date(conv.started_at),
        updatedAt: conv.ended_at ? new Date(conv.ended_at) : new Date(conv.started_at),
      });
    }

    setConversations(convMap);
    console.log('[ConversationManager] Loaded conversations from backend:', convMap.size);
    // ...
  } catch (error) {
    console.error('[ConversationManager] Failed to load conversations:', error);
    throw error;
  } finally {
    setLoading(false);
  }
}, [isAuthenticated]);
```

**Analysis**:
The console shows "Loaded conversations from backend: 57", which means:
1. The backend API is responding
2. Conversations are being loaded successfully
3. The conversation loading logic is working

**Pending Message Handling**:
The pending message from homepage is a separate feature for transferring messages from the landing page to the chat interface. This appears to be working based on the console log.

**Not a Frontend Bug**:
The conversation loading logic is correct. If there are specific issues with conversation display or message persistence, those would need more specific investigation.

### G.3 Affected Files
- `apps/web/app/components/useConversationManager.ts` (logic correct)
- `apps/web/lib/backend-conversation.ts` (logic correct)

### G.4 Proposed Fix

**Frontend**: No changes needed - logic appears correct

**Further Investigation Required**:
1. Identify specific conversation-related issues (display, persistence, etc.)
2. Verify backend conversation API behavior
3. Test conversation creation, selection, and deletion

**Priority**: LOW (logic appears correct, needs specific issue identification)
**Frontend Priority**: LOW (no frontend fix needed based on current evidence)

---

## H. ISSUE 6: PROFILE DESIGN & SETTINGS UI REGRESSION

### H.1 Problem Description
The user reports that the Profile appearance has changed unexpectedly.

### H.2 Root Cause Analysis

**Recent CSS Changes**:
The recent z-index fix and mobile CSS implementations may have affected the visual appearance.

**Investigation Required**:
1. Compare current Profile appearance with expected appearance
2. Check if CSS changes introduced unintended side effects
3. Verify Settings navigation text visibility (from previous audit)

### H.3 Affected Files
- `apps/web/app/globals.css`

### H.4 Proposed Fix

**Needs Visual Verification**:
1. Inspect current Profile menu appearance
2. Inspect current Settings appearance
3. Compare with expected design
4. Adjust CSS if needed

**Priority**: MEDIUM (visual regression)
**Frontend Priority**: LOW (depends on visual inspection)

---

## I. ROOT CAUSE MATRIX

| Issue | Root Cause | Affected Files | Priority | Frontend Fix Needed |
|-------|-----------|----------------|----------|-------------------|
| Settings Profile Edit | Stacking context - ProfileEdit inside Settings dialog | Settings.tsx, page.tsx | HIGH | YES |
| Authentication Failed | Backend session validation or cookie configuration | Backend API routes | HIGH | NO |
| Request Timeout | Backend/infrastructure latency or unavailability | Backend infrastructure | MEDIUM | NO |
| AI Service Unavailable | Python ML service not responding (HTTP 502) | Backend ML integration | HIGH | NO |
| Messenger System | Logic appears correct; needs specific issue identification | None identified | LOW | NO |
| Profile UI Regression | CSS changes may have affected appearance | globals.css | MEDIUM | MAYBE |

---

## J. PROTECTED SYSTEMS CONFIRMATION

### J.1 Neon PostgreSQL Database
**Status**: ✅ PROTECTED
- No schema changes proposed
- No migration changes proposed

### J.2 Authentication Architecture
**Status**: ✅ PROTECTED
- No authentication logic changes proposed
- No security bypass proposed

### J.3 AI Brain Architecture
**Status**: ✅ PROTECTED
- No model changes proposed
- No training changes proposed

### J.4 Storage Architecture
**Status**: ✅ PROTECTED
- No S3/Neon changes proposed

### J.5 Desktop Layout
**Status**: ✅ PROTECTED
- No desktop UI changes proposed
- Mobile-specific fix only

---

## K. PROPOSED IMPLEMENTATION

### K.1 Fix: Settings Profile Edit Stacking Context

**File**: `apps/web/app/components/Settings.tsx`

**Changes**:
1. Remove ProfileEdit rendering from inside Settings
2. Add `onProfileEditRequest` callback prop
3. Call callback when Edit Profile is clicked

**File**: `apps/web/app/page.tsx`

**Changes**:
1. Add `onProfileEditRequest` to Settings props
2. Handle callback by setting `isProfileEditOpen(true)`
3. Optionally close Settings when ProfileEdit opens

**Expected Result**:
- ProfileEdit renders at page level (global stacking context)
- z-index: 3500 works correctly
- Both mobile entry points work consistently

### K.2 Backend Issues (No Frontend Changes)

**Authentication**: Backend investigation required
**Timeout**: Backend investigation required
**AI Service**: Backend investigation required

---

## L. TESTING PLAN

### L.1 Profile Editing Tests
- [ ] Mobile Profile → Profile Editing
- [ ] Settings → Account → Profile → Profile Editing
- [ ] Edit profile information
- [ ] Save changes
- [ ] Cancel changes
- [ ] Verify persistence
- [ ] Verify avatar functionality

### L.2 Authentication Tests
- [ ] Verify backend session endpoint response format
- [ ] Verify cookie configuration
- [ ] Test authenticated conversation flow
- [ ] Test guest conversation flow

### L.3 AI Service Tests
- [ ] Verify Python ML service is running
- [ ] Test backend AI route
- [ ] Test guest message submission
- [ ] Test authenticated message submission

### L.4 UI Tests
- [ ] Inspect Profile appearance
- [ ] Inspect Settings appearance
- [ ] Verify text and icon visibility
- [ ] Test light and dark themes

---

## M. CONCLUSION

### M.1 Summary

**Frontend Fix Required**: ONE ISSUE
- Settings Profile Edit stacking context (HIGH priority)

**Backend Investigation Required**: THREE ISSUES
- Authentication session validation (HIGH priority)
- AI service availability (HIGH priority)
- Request timeout causes (MEDIUM priority)

**Logic Appears Correct**: TWO ISSUES
- Messenger/Conversation system (LOW priority - needs specific issue identification)
- Profile UI regression (MEDIUM priority - needs visual inspection)

### M.2 Next Steps

1. **Implement Frontend Fix**: Move ProfileEdit to page level
2. **Backend Investigation**: Verify auth, AI service, and timeout issues
3. **Visual Inspection**: Check Profile and Settings appearance
4. **Comprehensive Testing**: Test all fixes and regressions

---

**END OF ROOT CAUSE AUDIT REPORT**
