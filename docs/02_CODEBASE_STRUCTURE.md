# NexusAI Codebase Structure

## Repository Root

```
C:\Users\Nusaiba\Desktop\Ai Breand\
```

### Root Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Root package.json with pnpm workspace configuration |
| `pnpm-workspace.yaml` | Workspace configuration (apps/*, packages/*) |
| `tsconfig.json` | Root TypeScript configuration |
| `tsconfig.base.json` | Base TypeScript configuration for all packages |
| `.env.example` | Environment variable template (names only) |
| `.gitignore` | Git ignore patterns |
| `.prettierrc.json` | Prettier formatting configuration |
| `eslint.config.mjs` | ESLint configuration |
| `.editorconfig` | Editor configuration |
| `.vscode/settings.json` | VSCode settings |
| `.vscode/extensions.json` | VSCode recommended extensions |
| `.github/workflows/ci.yml` | GitHub Actions CI workflow |

### Root Scripts (package.json)

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start all apps in parallel (web, api, worker) |
| `pnpm build` | Build all packages and apps |
| `pnpm typecheck` | Type check all packages and apps |
| `pnpm lint` | Run ESLint on entire codebase |
| `pnpm format` | Format code with Prettier |
| `pnpm test` | Run Vitest tests |
| `pnpm check` | Run format:check, lint, typecheck, test, build |

## Apps Directory

### apps/api/ - Fastify Backend

Backend API server running on port 4000.

```
apps/api/
├── package.json                    # API dependencies
├── tsconfig.json                   # TypeScript config
├── tsx.json                        # tsx configuration
├── dev-wrapper.mjs                 # Development wrapper script
├── src/
│   ├── server.ts                   # Server entry point
│   ├── app.ts                      # Fastify app builder
│   ├── foundation.ts               # Foundation utilities
│   ├── auth-utils.ts               # Password/session hashing utilities
│   ├── idempotency.ts              # Idempotency handling
│   ├── rate-limit.ts               # Rate limiting implementation
│   ├── middleware/
│   │   └── auth.ts                 # Authentication middleware
│   └── routes/
│       ├── auth.ts                 # Authentication endpoints
│       ├── profile.ts              # Profile endpoints
│       ├── conversations.ts        # Conversation endpoints
│       └── ai.ts                   # AI proxy endpoints
```

#### Key Files

**src/server.ts**
- Entry point for the API server
- Loads environment variables from .env
- Builds Fastify app
- Listens on configured port (default 4000)
- Handles graceful shutdown (SIGINT, SIGTERM)

**src/app.ts**
- Main Fastify application builder
- Registers CORS and cookie plugins
- Sets up authentication middleware
- Registers route handlers
- Implements error handling
- Supports both database-backed and DevAuthService modes
- When DATABASE_URL is set: uses database-backed routes
- When DATABASE_URL is not set: uses in-memory DevAuthService

**src/routes/auth.ts**
- POST /api/v1/auth/register - User registration
- POST /api/v1/auth/login - User login
- POST /api/v1/auth/logout - User logout
- GET /api/v1/auth/session - Session validation
- Uses bcrypt for password hashing
- HTTP-only cookie session management

**src/routes/profile.ts**
- GET /api/v1/profile - Get user profile
- POST /api/v1/profile - Create profile
- PUT /api/v1/profile - Update profile
- Uses ProfileRepository from @nexusai/repositories

**src/routes/conversations.ts**
- GET /api/v1/conversations - List conversations
- POST /api/v1/conversations - Create conversation
- GET /api/v1/conversations/:id - Get conversation with messages
- POST /api/v1/conversations/:id/messages - Add message
- DELETE /api/v1/conversations/:id - Delete conversation
- Uses ConversationRepository and MessageRepository

**src/routes/ai.ts**
- POST /api/v1/ai/chat - Proxy to AI service
- GET /api/v1/ai/health - AI service health check
- Forwards requests to http://127.0.0.1:8000
- 10-second timeout on AI requests

**src/middleware/auth.ts**
- authMiddleware - Requires valid session
- optionalAuthMiddleware - Optional session
- Validates HTTP-only nexus_session cookie
- Sets request.accountId
- Updates last_seen_at timestamp

### apps/web/ - Next.js Frontend

Frontend web application running on port 3000.

```
apps/web/
├── package.json                    # Web dependencies
├── tsconfig.json                   # TypeScript config
├── next-env.d.ts                   # Next.js type definitions
├── dev.mjs                         # Development script
├── forensic_audit.mjs              # Audit script
├── public/
│   ├── favicon.ico                 # Favicon
│   └── images/
│       └── logo.png                 # Logo
├── app/
│   ├── layout.tsx                   # Root layout
│   ├── page.tsx                    # Home page
│   ├── globals.css                  # Global styles
│   ├── types.d.ts                  # TypeScript type definitions
│   └── components/
│       ├── AuthContext.tsx         # Authentication context
│       ├── AuthModal.tsx            # Auth modal component
│       ├── ChatInterface.tsx        # Chat interface
│       ├── ChatList.tsx             # Conversation list
│       ├── HistoryPage.tsx          # History page
│       ├── MainContent.tsx         # Main content area
│       ├── ProfileEdit.tsx          # Profile edit modal
│       ├── Sidebar.tsx              # Sidebar navigation
│       ├── conversation-types.ts    # Conversation type definitions
│       └── useConversationManager.ts # Conversation management hook
└── lib/
    ├── api-client.ts                # API client
    ├── avatar-service.ts           # Avatar upload service (localStorage)
    ├── backend-auth.ts              # Auth API calls
    ├── backend-conversation.ts      # Conversation API calls
    └── backend-profile.ts           # Profile API calls
```

#### Key Files

**app/page.tsx**
- Main application entry point
- Combines Sidebar and MainContent
- Manages navigation state
- Handles profile state
- Shows loading overlay during session restoration
- Guest mode support

**app/layout.tsx**
- Root layout component
- Sets up HTML structure
- Includes global styles

**app/globals.css**
- Global CSS styles
- CSS variables for theming
- Responsive design
- Mobile-specific styles

**app/components/AuthContext.tsx**
- Authentication context provider
- Manages user authentication state
- Session refresh on visibility change
- Login/logout functions
- Guest mode support

**app/components/AuthModal.tsx**
- Login/registration modal
- Email/password form
- Validation (8 character minimum password)
- Error handling

**app/components/ChatInterface.tsx**
- Chat UI component
- Message display
- Input field
- Typing indicator
- Guest mode (in-memory)
- Authenticated mode (persistent)
- AI service integration
- Error handling (Bangla error messages)

**app/components/Sidebar.tsx**
- Sidebar navigation
- Profile display
- Navigation items (Home, History, Settings)
- Mobile bottom navigation
- Logout button

**app/components/MainContent.tsx**
- Main content area
- Routes based on activeNav
- Home page with chat
- History page
- Profile edit modal

**app/components/useConversationManager.ts**
- Custom hook for conversation management
- Loads conversations from backend
- Creates new conversations
- Adds messages
- Manages active conversation state

**lib/api-client.ts**
- HTTP client for API calls
- GET, POST, PUT, DELETE methods
- Error handling
- Account ID header support

**lib/avatar-service.ts**
- Avatar upload service
- localStorage implementation (dev only)
- File validation (5MB max, JPEG/PNG/WebP/GIF)
- Key: nexusai_avatar_{userId}
- Data URL format (base64)

**lib/backend-auth.ts**
- Authentication API calls
- register(), login(), logout(), getSession()

**lib/backend-conversation.ts**
- Conversation API calls
- listConversations(), createConversation(), addMessage()

**lib/backend-profile.ts**
- Profile API calls
- getProfile(), createProfile(), updateProfile()

### apps/worker/ - Background Worker

Background worker service (minimal implementation).

```
apps/worker/
├── package.json                    # Worker dependencies
├── tsconfig.json                   # TypeScript config
└── src/
    └── index.ts                    # Worker entry point
```

## Packages Directory

### packages/database-core/ - Database Client

PostgreSQL client and migration system.

```
packages/database-core/
├── package.json
├── vitest.config.ts
├── src/
│   ├── index.ts                    # Main exports
│   ├── config.ts                   # Database configuration
│   ├── postgres-client.ts          # PostgreSQL client
│   ├── migration-loader.ts         # Migration file loader
│   └── migration-runner.ts         # Migration execution
├── migrations/
│   ├── 001_bootstrap.sql           # Schema creation
│   ├── 002_core_identity.sql       # Accounts and sessions
│   ├── 003_user_profiles.sql       # User profiles
│   ├── 004_conversations_messages.sql # Conversations and messages
│   ├── 005_consent_records.sql     # Consent tracking
│   ├── 006_memory_records.sql      # Memory records
│   ├── 007_notification_preferences.sql # Notification prefs
│   ├── 008_library_items.sql       # Library items
│   ├── 009_file_metadata.sql       # File metadata
│   ├── 010_add_avatar_storage_path.sql # Avatar path
│   ├── 011_create_g_media_table.sql # Media table
│   ├── 012_g_media_rls_policies.sql # RLS policies
│   ├── 013_knowledge_tables.sql    # Knowledge tables
│   ├── 014_fix_conversations_account_id.sql # Fix
│   ├── 015_grant_nexus_api_access.sql # Grants
│   ├── 016_add_password_hash.sql   # Password hash
│   ├── 017_add_memory_consent_fk.sql # Foreign key
│   ├── COMPLETE_SCHEMA.sql         # Full schema
│   └── RLS_POLICIES.sql            # Row-level security
```

#### Key Files

**src/config.ts**
- Reads DATABASE_URL from environment
- Supports 'supabase' and 'postgresql' providers
- Pool size configuration
- Connection string validation

**src/postgres-client.ts**
- PostgreSQL client implementation
- Query execution
- Connection management
- Error handling

**src/migration-runner.ts**
- Migration execution system
- Tracks applied migrations
- Idempotent migration application

### packages/repositories/ - Data Access Layer

Repository pattern for database operations.

```
packages/repositories/
├── package.json
└── src/
    ├── index.ts                    # Main exports
    ├── profile-repository.ts       # Profile CRUD
    ├── conversation-repository.ts  # Conversation CRUD
    ├── message-repository.ts       # Message CRUD
    └── memory-repository.ts        # Memory CRUD
```

#### Key Files

**profile-repository.ts**
- findByAccountId()
- create()
- update()
- delete()
- Soft delete support

**conversation-repository.ts**
- findById()
- listByAccountId()
- create()
- updateTitle()
- end()
- delete()

**message-repository.ts**
- findById()
- listByConversationId()
- create()
- delete()
- Auto-incrementing sequence numbers

### packages/auth-core/ - Authentication Utilities

Authentication-related utilities.

```
packages/auth-core/
├── package.json
└── src/
    └── index.ts                    # Auth utilities
```

### packages/ai-core/ - AI Integration

AI service integration abstractions.

```
packages/ai-core/
├── package.json
└── src/
    ├── index.ts                    # Main exports
    ├── bridge/                     # AI service bridge
    │   ├── client.ts
    │   ├── config.ts
    │   ├── errors.ts
    │   └── types.ts
    ├── orchestrator/               # AI orchestration
    │   ├── brain-orchestrator.ts
    │   ├── intent-classifier.ts
    │   ├── response-validator.ts
    │   └── intent-types.ts
    ├── memory/                     # Memory management
    ├── safety/                     # Safety checks
    └── tools/                      # AI tools
```

### packages/app-core/ - Domain Models

Domain models and business logic.

```
packages/app-core/
├── package.json
└── src/
    └── index.ts                    # Domain models
```

### packages/config/ - Configuration

Configuration management.

```
packages/config/
├── package.json
└── src/
    └── index.ts                    # Config utilities
```

### packages/contracts/ - Shared Types

Shared TypeScript types and interfaces.

```
packages/contracts/
├── package.json
└── src/
    └── index.ts                    # Shared types
```

### Other Packages

- **packages/domain/** - Domain logic
- **packages/memory-core/** - Memory management
- **packages/observability/** - Observability (logging, metrics)
- **packages/policy/** - Policy enforcement
- **packages/safety-core/** - Safety checks
- **packages/worker-core/** - Worker utilities

## Documentation Directory

```
docs/
├── README.md                       # This index
├── 01_PROJECT_OVERVIEW.md         # Project overview
├── 02_CODEBASE_STRUCTURE.md        # This file
├── 03_SYSTEM_ARCHITECTURE.md      # Architecture diagrams
├── 04_FRONTEND_GUIDE.md            # Frontend guide
├── 05_BACKEND_API_REFERENCE.md     # API documentation
├── 06_DATABASE_GUIDE.md            # Database schema
├── 07_AUTHENTICATION_SECURITY.md   # Auth and security
├── 08_AI_BRAIN_ARCHITECTURE.md     # AI integration
├── 09_STORAGE_AND_MEDIA.md         # Storage implementation
├── 10_DEVELOPER_SETUP.md           # Developer setup
├── 11_DATA_FLOWS_AND_WORKFLOWS.md  # Data flows
├── 12_TESTING_AND_QA.md            # Testing guide
├── 13_TECHNICAL_DEBT_AND_LIMITATIONS.md # Debt and limits
├── 14_FUTURE_ROADMAP.md            # Roadmap
├── 15_ARCHITECTURE_DECISIONS.md    # ADRs
├── 00-project-overview.md          # Legacy docs
├── 01-product-discovery.md         # Legacy docs
├── 02-prd-nexus-ai-health-companion-mvp.md # Legacy docs
├── 03-system-architecture-outline.md # Legacy docs
├── 04-architecture-review.md       # Legacy docs
├── 05-data-dictionary.md           # Legacy docs
├── 05-database-decisions.md       # Legacy docs
├── 05-database-design.md           # Legacy docs
├── 05-erd.md                       # Legacy docs
├── 06-database-implementation.md   # Legacy docs
├── 06-database-validation.md       # Legacy docs
├── 06-ddl.md                       # Legacy docs
├── 06-migration-strategy.md        # Legacy docs
├── 07-api-authentication.md        # Legacy docs
├── 07-api-contract.md              # Legacy docs
├── 07-api-design.md                # Legacy docs
├── 07-api-error-handling.md        # Legacy docs
├── 07-api-security.md              # Legacy docs
├── 07-api-validation.md            # Legacy docs
├── 08-ai-data-flow.md              # Legacy docs
├── 08-ai-decisions.md              # Legacy docs
├── 08-ai-intelligence-architecture.md # Legacy docs
├── 08-memory-architecture.md       # Legacy docs
├── 08-model-provider-abstraction.md # Legacy docs
├── 08-planning-and-agent-architecture.md # Legacy docs
├── 08-safety-architecture.md       # Legacy docs
├── 09-accessibility.md             # Legacy docs
├── 09-design-system.md             # Legacy docs
├── 09-information-architecture.md # Legacy docs
├── 09-screen-specifications.md    # Legacy docs
├── 09-ui-api-traceability.md       # Legacy docs
├── 09-ui-decisions.md              # Legacy docs
├── 09-ui-ux-architecture.md        # Legacy docs
├── 09-user-flows.md                # Legacy docs
└── 10-admin-support-security.md    # Legacy docs
```

## Root Level Scripts and Utilities

```
scripts/
├── check-secrets.mjs                # Secret scanning
└── check-architecture.mjs           # Architecture validation
```

## Database Directory

```
database/
└── README.md                        # Database documentation
```

## Test Directory

```
tests/
└── (test files)
```

## File Naming Conventions

- **TypeScript**: `.ts` for regular files, `.tsx` for React components
- **SQL**: `.sql` for database migrations
- **Configuration**: `.json`, `.mjs`, `.yaml`
- **Documentation**: `.md`
- **Components**: PascalCase (e.g., AuthModal.tsx)
- **Utilities**: camelCase (e.g., api-client.ts)
- **Hooks**: use* prefix (e.g., useConversationManager.ts)

## Import Patterns

### Relative Imports
```typescript
import { something } from './local-file';
import { something } from '../parent-folder/file';
```

### Package Imports
```typescript
import { DatabaseClient } from '@nexusai/database-core';
import { ProfileRepository } from '@nexusai/repositories';
```

### Next.js Imports
```typescript
import { useState, useEffect } from 'react';
import { useAuth } from './components/AuthContext';
```

## Environment Variables

Environment variables are defined in `.env` (not committed) and documented in `.env.example`:

- `NODE_ENV` - Environment (development/production)
- `WEB_PORT` - Web server port (default 3000)
- `API_PORT` - API server port (default 4000)
- `API_ORIGIN` - API origin URL
- `WEB_ORIGIN` - Web origin URL
- `NEXT_PUBLIC_API_ORIGIN` - Public API origin (for frontend)
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_POOL_SIZE` - Database pool size (default 20)
- `COOKIE_SECRET` - Cookie signing secret
- `AI_SERVICE_URL` - AI service URL (default http://127.0.0.1:8000)

## Summary

The NexusAI codebase is organized as a monorepo with:
- 3 applications (api, web, worker)
- ~15 shared packages
- Clear separation between frontend, backend, and shared logic
- Database-backed repositories for data access
- Migration system for schema management
- Comprehensive documentation

For more details, see:
- [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) - Architecture diagrams
- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API endpoints
- [06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md) - Database schema
