# NexusAI Project Overview

## What is NexusAI?

NexusAI is a personal AI health and wellness companion application built as a full-stack monorepo using pnpm workspaces. It provides AI-powered conversational assistance with persistent conversation history, user profiles, and optional wellness features.

### Current Status

**Phase**: Phase 13 Part 2 (Authorized / In Progress)

The application is in active development with a focus on core implementation. Production deployment, public beta, and unresolved legal/privacy decisions remain out of scope.

### Core Capabilities

#### Implemented Features
- **Authentication**: Self-managed email/password authentication with bcrypt password hashing
- **Guest Mode**: In-memory chat functionality without authentication
- **Authenticated Chat**: Persistent conversations stored in PostgreSQL
- **Profile Management**: User profiles with display name, age band, locale, and timezone
- **Conversation History**: View and manage past conversations
- **Session Management**: HTTP-only cookie-based sessions with 7-day expiration
- **AI Integration**: External AI service integration for chat responses
- **Mobile Responsive**: Mobile-friendly UI with bottom navigation

#### Planned Features (Not Yet Implemented)
- Goal Management (development-only slice authorized)
- Memory Records with user consent
- Wellness Profile tracking
- Notification Preferences
- Library Items (notes, bookmarks, references)
- File Upload with cloud storage
- Rate Limiting (implementation exists but not fully tested in production)

## Technology Stack

### Frontend
- **Framework**: Next.js 15.5.24
- **UI Library**: React 19
- **Language**: TypeScript
- **Icons**: lucide-react
- **Styling**: CSS with CSS variables
- **State Management**: React Context API
- **Port**: 3000

### Backend
- **Framework**: Fastify 5.12.5
- **Language**: TypeScript
- **Authentication**: bcrypt for password hashing
- **Session Management**: @fastify/cookie with HTTP-only cookies
- **CORS**: @fastify/cors
- **Port**: 4000

### Database
- **Provider**: Neon PostgreSQL
- **Schema**: nexus (custom schema)
- **Connection**: PostgreSQL connection string via DATABASE_URL
- **Client**: Custom PostgreSQL client (@nexusai/database-core)
- **Migrations**: SQL migration files in packages/database-core/migrations/

### AI Service
- **Type**: External Python FastAPI/ML service
- **URL**: http://127.0.0.1:8000 (configurable via AI_SERVICE_URL)
- **Integration**: Backend proxies requests to AI service
- **Endpoint**: /orchestrate for chat requests

### Package Management
- **Manager**: pnpm 11.19.0
- **Workspaces**: Monorepo with apps/* and packages/*
- **Node Version**: >=22 <25

## Architecture Overview

### Monorepo Structure

The project uses pnpm workspaces to manage multiple packages and applications:

```
C:\Users\Nusaiba\Desktop\Ai Breand\
├── apps/
│   ├── api/          # Fastify backend application
│   ├── web/          # Next.js frontend application
│   └── worker/       # Background worker (minimal implementation)
├── packages/
│   ├── database-core/    # PostgreSQL client and migrations
│   ├── auth-core/        # Authentication utilities
│   ├── ai-core/          # AI service integration abstractions
│   ├── repositories/     # Data access layer (CRUD operations)
│   ├── app-core/         # Domain models and business logic
│   ├── config/           # Configuration management
│   ├── contracts/        # Shared TypeScript types
│   └── ... (other core packages)
├── docs/              # Technical documentation
└── package.json       # Root workspace configuration
```

### Key Design Principles

1. **Separation of Concerns**: Frontend never accesses database directly; all data goes through backend API
2. **Domain Services**: Domain services own business state, ownership, consent, lifecycle, and safety policy
3. **AI Traffic Through Gateway**: All AI requests go through backend API to AI service
4. **Minimal Memory Off by Default**: Memory feature is consent-bound, purpose-bound, revocable, and deletable
5. **Safety Modes**: NORMAL, WELLNESS_REDIRECT, SAFETY_ESCALATION, and BLOCKED

## Network Configuration

### Development Environment
- **Web Origin**: http://localhost:3000
- **API Origin**: http://localhost:4000
- **NEXT_PUBLIC_API_ORIGIN**: http://localhost:4000
- **AI Service URL**: http://127.0.0.1:8000
- **API Binding**: 127.0.0.1:4000
- **Web Binding**: 0.0.0.0:3000 (accessible via LAN IP)

### CORS Configuration
- Allows credentials from web origin
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization
- Development: http://localhost:3000
- Production: Must be updated to actual production origin

## Database Overview

### Provider
Neon PostgreSQL (serverless PostgreSQL)

### Schema
Custom `nexus` schema with 18 tables:
- accounts (user accounts)
- auth_sessions (session management)
- user_profiles (user profile data)
- conversations (chat conversations)
- messages (chat messages)
- memory_records (AI memory with consent)
- consent_records (user consent tracking)
- notification_preferences (notification settings)
- library_items (user library)
- file_metadata (file storage metadata)
- Plus additional tables for jobs, templates, usage logs, rate limits, audit logs

### Key Features
- UUID primary keys
- Timestamps (created_at, updated_at, deleted_at)
- Foreign key constraints
- Check constraints for data validation
- Indexes for query optimization
- Soft delete support (deleted_at)
- Triggers for automatic timestamp updates

## Authentication System

### Type
Self-managed email/password authentication (not dependent on external identity providers)

### Implementation
- **Password Hashing**: bcrypt
- **Session Storage**: Database-backed (nexus.auth_sessions table)
- **Session Cookie**: HTTP-only nexus_session cookie
- **Session Duration**: 7 days
- **Cookie Security**: HttpOnly, SameSite=Lax, secure in production
- **Session Validation**: Token hashing with bcrypt for comparison

### Security Features
- Password minimum 8 characters
- Email normalization (lowercase)
- Account status tracking (active, suspended, deletion_pending, deleted, purged)
- Session revocation support
- Last seen tracking

## AI Integration

### Architecture
NexusAI uses an EXTERNAL AI service. The backend acts as a proxy:

```
Frontend → Backend API → AI Service → Response
```

### Flow
1. User sends message via frontend
2. Frontend calls POST /api/v1/ai/chat on backend
3. Backend forwards request to AI service at http://127.0.0.1:8000/orchestrate
4. AI service processes and returns response
5. Backend returns response to frontend
6. Frontend displays response

### Current Limitations
- AI service must be running externally
- No built-in model in NexusAI
- No retry logic for failed AI requests
- 10-second timeout on AI requests

## Storage Implementation

### Profile Images
- **Current**: localStorage (development only)
- **Service**: apps/web/lib/avatar-service.ts
- **Key**: nexusai_avatar_{userId}
- **Format**: Data URLs (base64 encoded)
- **Limitations**: Device-specific, not cross-device, no cloud storage
- **Recommendation**: Implement cloud storage (Supabase Storage, AWS S3) for production

### File Storage
- **Metadata Table**: nexus.file_metadata
- **Providers Supported**: supabase, s3, local
- **Current Status**: Metadata table exists but no active file upload implementation
- **Future**: Cloud storage integration needed

## Development Boundaries

### What the Web App Does
- Calls versioned API endpoints
- Manages UI state and user interactions
- Handles authentication state via cookies
- Stores profile images in localStorage (dev only)

### What the Web App Does NOT Do
- Access database directly
- Access provider secrets
- Bypass backend API for AI requests
- Store sensitive data in client-side storage (except dev-only avatars)

### What Domain Services Own
- Business state
- Ownership validation
- Consent management
- Lifecycle management
- Safety policy enforcement

## Current Limitations

### Technical Debt
1. Profile images use localStorage (not production-ready)
2. No rate limiting on authentication endpoints (implementation exists but not production-tested)
3. Guest conversations are not persisted (by design)
4. No retry logic for failed AI requests
5. AI service dependency is external and must be running

### Security Considerations
1. DATABASE_URL may have been exposed in previous sessions (rotate credential)
2. Default/development cookie secret in use (generate secure secret for production)
3. CORS configured for localhost only (update for production)
4. Password strength only requires 8 characters (consider complexity requirements)

### Unimplemented Features
1. Goal Management (authorized for development)
2. Memory Records with consent tracking
3. Wellness Profile
4. Notification Preferences
5. Library Items
6. File Upload with cloud storage
7. Comprehensive rate limiting
8. Audit logging

## Future Development

See [14_FUTURE_ROADMAP.md](./14_FUTURE_ROADMAP.md) for detailed phased roadmap including:
- Stage A: Stabilization
- Stage B: Maintainability
- Stage C: AI Capability Development
- Stage D: Scalable Infrastructure
- Stage E: Product Expansion

## References

- [README.md](../README.md) - Project README with phase information
- [NEXUSAI_FULL_REPAIR_REPORT.md](../NEXUSAI_FULL_REPAIR_REPORT.md) - Detailed repair report
- [.env.example](../.env.example) - Environment variable reference
- [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) - Detailed architecture diagrams
- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API documentation
- [06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md) - Database schema documentation
