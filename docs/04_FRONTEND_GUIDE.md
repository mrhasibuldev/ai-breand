# NexusAI Frontend Guide

## Overview

The NexusAI frontend is built with Next.js 15.5.24, React 19, and TypeScript. It provides a responsive web interface for AI chat, profile management, and conversation history.

## Technology Stack

- **Framework**: Next.js 15.5.24
- **UI Library**: React 19
- **Language**: TypeScript
- **Icons**: lucide-react
- **Styling**: CSS with CSS variables
- **State Management**: React Context API
- **Port**: 3000

## Project Structure

```
apps/web/
├── app/
│   ├── layout.tsx                   # Root layout
│   ├── page.tsx                    # Home page (main app)
│   ├── globals.css                  # Global styles
│   ├── types.d.ts                  # TypeScript definitions
│   └── components/
│       ├── AuthContext.tsx         # Authentication context
│       ├── AuthModal.tsx            # Auth modal
│       ├── ChatInterface.tsx        # Chat UI
│       ├── ChatList.tsx             # Conversation list
│       ├── HistoryPage.tsx          # History page
│       ├── MainContent.tsx         # Main content area
│       ├── ProfileEdit.tsx          # Profile edit
│       ├── Sidebar.tsx              # Sidebar navigation
│       ├── conversation-types.ts    # Type definitions
│       └── useConversationManager.ts # Conversation hook
└── lib/
    ├── api-client.ts                # API client
    ├── avatar-service.ts           # Avatar service
    ├── backend-auth.ts              # Auth API calls
    ├── backend-conversation.ts      # Conversation API
    └── backend-profile.ts           # Profile API
```

## Core Components

### AuthContext.tsx

Authentication context provider that manages user authentication state.

**Location**: `apps/web/app/components/AuthContext.tsx`

**Key Features**:
- Manages user authentication state
- Handles session validation
- Refreshes session on visibility change (not polling)
- Provides login/logout functions
- Supports guest mode

**State**:
- `user`: Current user object or null
- `isAuthenticated`: Boolean authentication status
- `initialized`: Boolean initialization status

**Functions**:
- `login(email, password)`: Authenticate user
- `logout()`: Clear session
- `refreshUser()`: Refresh session from backend

**Usage**:
```tsx
import { useAuth } from './components/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  // ...
}
```

### AuthModal.tsx

Modal component for user registration and login.

**Location**: `apps/web/app/components/AuthModal.tsx`

**Key Features**:
- Tab-based UI (Login/Register)
- Email/password form
- Validation (8 character minimum password)
- Error handling
- Loading states

**Props**:
- `isOpen`: Boolean - Modal open state
- `onClose`: Function - Close handler

**Validation**:
- Email: Required
- Password: Minimum 8 characters (matches backend)

### ChatInterface.tsx

Main chat interface component.

**Location**: `apps/web/app/components/ChatInterface.tsx`

**Key Features**:
- Message display with user/assistant roles
- Input field with send button
- Typing indicator
- Guest mode (in-memory only)
- Authenticated mode (persistent)
- AI service integration
- Error handling with Bangla messages
- Auto-scroll to latest message
- Request cancellation

**State**:
- `inputValue`: Current input text
- `isTyping`: AI typing state
- `activeRequestId`: Current request ID
- `guestConversations`: In-memory guest conversations

**Functions**:
- `handleSubmit()`: Send message
- `handleGuestMessage()`: Handle guest mode message
- `handleSendMessage()`: Handle authenticated message
- `handleCancelRequest()`: Cancel active request

**Error Messages (Bangla)**:
- AI service unavailable: "দুঃখিত, AI সার্ভিসটি বর্তমানে উপলব্ধ নেই। অনুগ্রহ করে পরে আবার চেষ্টা করুন।"
- AI service timeout: "দুঃখিত, AI সার্ভিসটি সময়সীমা অতিক্রম করেছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।"
- Backend server error: "দুঃখিত, সার্ভারে একটি ত্রুটি হয়েছে। অনুগ্রহ করে পরে আবার চেষ্টা করুন।"
- Authentication required: "দুঃখিত, আপনার সেশন মেয়াদ শেষ হয়েছে। অনুগ্রহ করে আবার লগ ইন করুন।"

### Sidebar.tsx

Sidebar navigation component.

**Location**: `apps/web/app/components/Sidebar.tsx`

**Key Features**:
- Profile display with avatar
- Navigation items (Home, History, Settings)
- Mobile bottom navigation
- Logout button
- Responsive design

**Props**:
- `activeNav`: Current active navigation
- `onNavChange`: Navigation change handler
- `profileName`: User's display name
- `profileEmail`: User's email
- `profilePhoto`: User's avatar URL
- `isAuthenticated`: Authentication status
- `onProfileClick`: Profile click handler
- `onLogout`: Logout handler

### MainContent.tsx

Main content area that routes based on active navigation.

**Location**: `apps/web/app/components/MainContent.tsx`

**Key Features**:
- Routes to Home, History, or Settings
- Contains ChatInterface for Home
- Contains HistoryPage for History
- Contains ProfileEdit for Settings
- Handles auth-required prompts

**Props**:
- `activeNav`: Current active navigation
- `onNavChange`: Navigation change handler
- `profileName`: User's display name
- `profileEmail`: User's email
- `profilePhoto`: User's avatar URL
- `onProfileSave`: Profile save handler
- `isAuthenticated`: Authentication status
- `onAuthRequired`: Auth required handler

### HistoryPage.tsx

Conversation history page.

**Location**: `apps/web/app/components/HistoryPage.tsx`

**Key Features**:
- Lists user's conversations
- Pagination (10 items at a time)
- Relative time formatting
- Empty state
- Error state with retry
- Loading state
- Requires authentication

**State**:
- `conversations`: Array of conversations
- `loading`: Loading state
- `error`: Error state

### ProfileEdit.tsx

Profile edit modal.

**Location**: `apps/web/app/components/ProfileEdit.tsx`

**Key Features**:
- Edit display name
- Upload avatar
- Save to backend
- localStorage for avatar (dev only)

**Props**:
- `isOpen`: Modal open state
- `onClose`: Close handler
- `profileName`: Current profile name
- `profileEmail`: Current email
- `profilePhoto`: Current avatar
- `onSave`: Save handler

### useConversationManager.ts

Custom hook for conversation management.

**Location**: `apps/web/app/components/useConversationManager.ts`

**Key Features**:
- Loads conversations from backend
- Creates new conversations
- Adds messages to conversations
- Manages active conversation state
- Requires authentication

**State**:
- `conversations`: Map of conversations
- `activeConversationId`: Active conversation ID
- `loading`: Loading state

**Functions**:
- `loadConversations()`: Load from backend
- `createConversation()`: Create new conversation
- `addMessage()`: Add message to conversation
- `getActiveConversation()`: Get active conversation

## API Client

### api-client.ts

HTTP client for backend API calls.

**Location**: `apps/web/lib/api-client.ts`

**Key Features**:
- GET, POST, PUT, DELETE methods
- Error handling
- Account ID header support
- Base URL configuration

**Usage**:
```typescript
import { apiClient } from '../lib/api-client';

const data = await apiClient.get<T>('/api/v1/profile');
const result = await apiClient.post<T>('/api/v1/auth/login', body);
```

### backend-auth.ts

Authentication API calls.

**Location**: `apps/web/lib/backend-auth.ts`

**Functions**:
- `register(email, password)`: Register new account
- `login(email, password)`: Login with credentials
- `logout()`: Logout current session
- `getSession()`: Get current session

### backend-conversation.ts

Conversation API calls.

**Location**: `apps/web/lib/backend-conversation.ts`

**Functions**:
- `listConversations()`: List user's conversations
- `createConversation(title)`: Create new conversation
- `addMessage(conversationId, message)`: Add message to conversation

### backend-profile.ts

Profile API calls.

**Location**: `apps/web/lib/backend-profile.ts`

**Functions**:
- `getProfile()`: Get user profile
- `createProfile(data)`: Create new profile
- `updateProfile(data)`: Update user profile

## Avatar Service

### avatar-service.ts

Avatar upload service using localStorage (development only).

**Location**: `apps/web/lib/avatar-service.ts`

**Key Features**:
- localStorage implementation
- File validation (5MB max)
- Supported formats: JPEG, PNG, WebP, GIF
- Data URL format (base64)
- Key: nexusai_avatar_{userId}

**Functions**:
- `uploadAvatar(userId, file)`: Upload avatar
- `loadAvatarFromLocalStorage(userId)`: Load avatar
- `deleteAvatar(storagePath, userId)`: Delete avatar

**Limitations**:
- Device-specific (not cross-device)
- No cloud storage
- Browser localStorage quota limits
- NOT production-ready

**Recommendation**: Implement cloud storage (Supabase Storage, AWS S3) for production.

## Styling

### globals.css

Global CSS styles with CSS variables.

**Location**: `apps/web/app/globals.css`

**CSS Variables**:
```css
:root {
  --bg-primary: #f5f5f5;
  --bg-secondary: #ffffff;
  --surface: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent-primary: #6366f1;
  --accent-hover: #4f46e5;
  --border-color: #e5e5e5;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
}
```

**Key Features**:
- Responsive design with media queries
- Mobile-specific styles
- Loading overlay styles
- Chat interface styles
- Sidebar styles
- Modal styles

## Type Definitions

### conversation-types.ts

Type definitions for conversations.

**Location**: `apps/web/app/components/conversation-types.ts`

**Types**:
```typescript
export interface Conversation {
  id: string;
  accountId: string;
  status: 'active' | 'ended' | 'deleted';
  title?: string;
  startedAt: Date;
  endedAt?: Date;
  messages: ConversationMessage[];
  updatedAt: Date;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isError?: boolean;
  responseSource?: string;
}
```

### types.d.ts

Global TypeScript definitions.

**Location**: `apps/web/app/types.d.ts`

## State Management

### React Context API

The application uses React Context API for state management:

1. **AuthContext**: Authentication state
2. **Local Component State**: Component-specific state
3. **Custom Hooks**: Reusable stateful logic (useConversationManager)

### Data Flow

```
User Action → Component State → API Call → Backend → Database
                                        ↓
                                    Response → Component State → UI Update
```

## Routing

Next.js App Router is used for routing:

- `/` - Home page (main app with chat)
- No additional routes currently (single-page app with client-side navigation)

## Responsive Design

### Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Mobile Features

- Bottom navigation bar
- Touch-friendly buttons
- Safe area handling
- Horizontal overflow prevention

## Performance Considerations

### Optimizations

- Code splitting with Next.js
- Lazy loading of components
- Debounced input handling
- Abort controller for request cancellation
- Visibility-based session refresh (not polling)

### Known Issues

- No image optimization
- No lazy loading for conversation history
- localStorage quota limits for avatars

## Error Handling

### Error States

- Network errors: Display error message in chat
- Authentication errors: Redirect to login
- AI service errors: Display Bangla error messages
- Validation errors: Display inline errors

### Error Messages

All error messages are user-friendly and localized to Bangla for AI service errors.

## Accessibility

### Current State

- Semantic HTML
- ARIA labels on buttons
- Keyboard navigation support
- Focus management in modals

### Future Improvements

- Full ARIA compliance
- Screen reader testing
- Keyboard shortcuts
- High contrast mode

## Testing

### Current State

- No automated tests for frontend
- Manual testing required

### Future Improvements

- Jest/React Testing Library
- Component tests
- E2E tests with Playwright
- Accessibility tests

## Development

### Running the Frontend

```bash
cd apps/web
pnpm dev
```

Access at http://localhost:3000

### Building for Production

```bash
cd apps/web
pnpm build
```

### Type Checking

```bash
cd apps/web
pnpm typecheck
```

## References

- [02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md) - File structure
- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API documentation
- [10_DEVELOPER_SETUP.md](./10_DEVELOPER_SETUP.md) - Setup guide
