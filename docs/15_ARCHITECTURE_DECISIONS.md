# NexusAI Architecture Decision Records

## Overview

This document contains Architectural Decision Records (ADRs) for significant architectural decisions made in the NexusAI project.

## ADR Format

Each ADR follows this format:
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: What is the issue that we're seeing that is motivating this decision?
- **Decision**: What is the change that we're proposing and/or doing?
- **Consequences**: What becomes easier or more difficult to do because of this change?

---

## ADR-001: Monorepo with pnpm Workspaces

**Status**: Accepted
**Date**: 2024 (Initial project setup)
**Deciders**: Development Team

### Context

The project consists of multiple applications (API, Web, Worker) and shared packages (database-core, auth-core, ai-core, repositories, etc.). We need a way to manage these dependencies efficiently and ensure consistency across the codebase.

### Decision

Use pnpm workspaces to manage the monorepo structure. All applications and packages are defined in the root `package.json` under the `workspaces` field.

**Configuration**:
```json
{
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
```

### Consequences

**Positive**:
- Shared code reuse across apps and packages
- Consistent dependency management
- Atomic commits across packages
- Simplified build process with `pnpm -r build`
- Efficient disk usage (hoisting)
- Faster installs due to strict peer dependency handling

**Negative**:
- Learning curve for developers unfamiliar with pnpm
- More complex root package.json
- Workspace configuration overhead

**Neutral**:
- Requires pnpm 11.19.0 (specific version)
- Node version constraint (>=22 <25)

---

## ADR-002: PostgreSQL via Neon

**Status**: Accepted
**Date**: 2024 (Initial project setup)
**Deciders**: Development Team

### Context

We need a database solution that is:
- Easy to set up and manage
- Compatible with standard PostgreSQL
- Scalable for future growth
- Cost-effective for development

### Decision

Use Neon PostgreSQL as the database provider. Use standard PostgreSQL connection strings for compatibility with self-hosted PostgreSQL.

**Configuration**:
```env
DATABASE_PROVIDER=postgresql
DATABASE_URL=postgresql://[user].[project_id]:[password]@[neon-hostname]/[database]?sslmode=verify-full
```

**Rationale**:
- Serverless PostgreSQL (no server management)
- Compatible with standard PostgreSQL (easy migration to self-hosted)
- Built-in connection pooling
- Automatic backups
- Cost-effective for development

### Consequences

**Positive**:
- No server management required
- Easy setup and configuration
- Automatic scaling
- Built-in backups and point-in-time recovery
- Easy migration path to self-hosted PostgreSQL
- Connection pooling included

**Negative**:
- Dependency on third-party service
- Potential vendor lock-in (mitigated by PostgreSQL compatibility)
- Network latency compared to local database
- Cost at scale

**Neutral**:
- Requires SSL connection
- Connection string format same as standard PostgreSQL

---

## ADR-003: Custom nexus Schema

**Status**: Accepted
**Date**: 2024 (Initial database design)
**Deciders**: Development Team

### Context

We need to organize database tables in a way that:
- Separates application data from public schema
- Allows for future multi-tenancy
- Provides clear organization
- Avoids conflicts with extensions

### Decision

Use a custom `nexus` schema for all application tables instead of using the default `public` schema.

**Implementation**:
```sql
CREATE SCHEMA IF NOT EXISTS nexus;
SET search_path = nexus, public;
```

### Consequences

**Positive**:
- Clear separation of application data
- Easy to identify application tables
- Supports future multi-tenancy (one schema per tenant)
- Avoids conflicts with PostgreSQL extensions
- Better organization

**Negative**:
- Must specify schema in all queries
- Slightly more verbose SQL
- Requires schema management

**Neutral**:
- Requires `SET search_path` or explicit schema qualification
- Migration system must handle schema

---

## ADR-004: Self-Managed Authentication

**Status**: Accepted
**Date**: 2024 (Initial implementation)
**Deciders**: Development Team

### Context

We need an authentication system that:
- Is independent of external identity providers
- Provides full control over user data
- Avoids vendor lock-in
- Is simple to implement

### Decision

Implement self-managed email/password authentication using bcrypt for password hashing and HTTP-only cookies for session management.

**Implementation**:
- Password hashing: bcrypt
- Session storage: Database-backed (nexus.auth_sessions)
- Session management: HTTP-only nexus_session cookie
- Session duration: 7 days

### Consequences

**Positive**:
- Full control over user data
- No dependency on external identity providers
- No vendor lock-in
- Simple implementation
- Privacy-focused (data stays in our database)

**Negative**:
- Must implement all auth features ourselves (email verification, password reset, 2FA)
- Responsible for security
- No social login integration (unless implemented)
- More maintenance burden

**Neutral**:
- bcrypt is computationally expensive (acceptable for security)
- HTTP-only cookies provide CSRF protection (SameSite=Lax)

---

## ADR-005: HTTP-Only Cookie Sessions

**Status**: Accepted
**Date**: 2024 (Initial implementation)
**Deciders**: Development Team

### Context

We need a session management approach that:
- Is secure against XSS attacks
- Provides CSRF protection
- Is browser-managed
- Doesn't require client-side token storage

### Decision

Use HTTP-only cookies for session management with the nexus_session cookie.

**Cookie Configuration**:
- Name: nexus_session
- HttpOnly: true (prevents JavaScript access)
- SameSite: Lax (CSRF protection)
- Path: / (entire domain)
- Max-Age: 604800 seconds (7 days)
- Secure: true in production (HTTPS only)

### Consequences

**Positive**:
- Secure against XSS attacks (JavaScript cannot access cookie)
- CSRF protection via SameSite=Lax
- Browser-managed expiration
- No client-side token storage
- Simpler than JWT implementation

**Negative**:
- Cannot access session from client-side JavaScript
- Harder to implement mobile apps (need web view or token-based auth)
- Cookie size limits (4KB)
- CSRF protection not perfect (Lax allows some cross-site requests)

**Neutral**:
- Requires HTTPS for secure flag in production
- 7-day expiration may be too long or too short depending on use case

---

## ADR-006: External AI Service

**Status**: Accepted
**Date**: 2024 (Initial implementation)
**Deciders**: Development Team

### Context

We need AI capabilities for chat functionality. Options:
- Build AI model into application
- Use external AI service
- Use cloud AI API (OpenAI, Anthropic, etc.)

### Decision

Use external AI service (Python FastAPI/ML service) running at http://127.0.0.1:8000. Backend acts as a proxy between frontend and AI service.

**Architecture**:
```
Frontend → Backend API → AI Service → Response
```

### Consequences

**Positive**:
- Separation of concerns (AI separate from application)
- Flexible model swapping (change AI service without changing app)
- Reduced deployment complexity (AI service deployed separately)
- Specialized AI infrastructure
- Can use any AI model/framework

**Negative**:
- External dependency (AI service must be running)
- No built-in fallback if AI service down
- Network latency between backend and AI service
- Additional deployment complexity
- No direct control over AI model updates

**Neutral**:
- Backend proxies requests (adds latency)
- AI service can be developed independently
- AI service can be scaled independently

---

## ADR-007: Repository Pattern for Data Access

**Status**: Accepted
**Date**: 2024 (Initial implementation)
**Deciders**: Development Team

### Context

We need a data access layer that:
- Abstracts database queries
- Provides ownership validation
- Is easy to test with mocks
- Centralizes query logic

### Decision

Use the repository pattern for data access. Create repository classes for each entity (ProfileRepository, ConversationRepository, MessageRepository, etc.).

**Implementation**:
```typescript
export class ProfileRepository {
  constructor(private readonly db: DatabaseClient) {}
  
  async findByAccountId(accountId: string): Promise<UserProfile | null> {
    // Query logic
  }
  
  async create(input: CreateProfileInput): Promise<UserProfile> {
    // Create logic
  }
}
```

### Consequences

**Positive**:
- Abstraction over database queries
- Easy testing with mocks
- Centralized query logic
- Ownership validation built-in
- Clear separation of concerns

**Negative**:
- Additional layer of abstraction
- More boilerplate code
- Potential for N+1 query problems if not careful
- Learning curve for developers

**Neutral**:
- Repositories are simple CRUD operations currently
- Could be enhanced with more complex queries later

---

## ADR-008: UUID Primary Keys

**Status**: Accepted
**Date**: 2024 (Initial database design)
**Deciders**: Development Team

### Context

We need a primary key strategy for database tables. Options:
- Sequential integers (auto-increment)
- UUIDs
- Composite keys

### Decision

Use UUID primary keys for all tables, generated by the database using `gen_random_uuid()`.

**Implementation**:
```sql
CREATE TABLE nexus.accounts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    ...
);
```

### Consequences

**Positive**:
- No exposed sequential IDs (security)
- Easy to generate client-side if needed
- No database contention for key generation
- Works well with distributed systems
- No key exhaustion

**Negative**:
- Larger than integers (16 bytes vs 4/8 bytes)
- Slower for joins (indexed but still larger)
- Not human-readable
- More storage space

**Neutral**:
- PostgreSQL handles UUIDs efficiently
- UUIDs are standard in modern applications

---

## ADR-009: Soft Delete Pattern

**Status**: Accepted
**Date**: 2024 (Initial database design)
**Deciders**: Development Team

### Context

We need a deletion strategy that:
- Allows data recovery
- Maintains data integrity
- Supports audit trails
- Complies with data retention policies

### Decision

Use soft delete pattern with `deleted_at` timestamp. Records are marked as deleted instead of being physically removed.

**Implementation**:
```sql
CREATE TABLE nexus.accounts (
    ...
    deleted_at timestamptz,
    ...
);
```

**Queries**:
```sql
-- Active records only
SELECT * FROM nexus.accounts WHERE deleted_at IS NULL;

-- Include deleted records
SELECT * FROM nexus.accounts;
```

### Consequences

**Positive**:
- Data recovery possible
- Audit trail maintained
- No data loss
- Supports data retention policies
- Can analyze deleted data

**Negative**:
- Database grows over time
- Must filter `deleted_at IS NULL` in queries
- Requires cleanup job for old deleted records
- More complex queries

**Neutral**:
- Unique constraints can exclude deleted records
- Requires manual cleanup or scheduled job

---

## ADR-010: localStorage for Profile Images (Development Only)

**Status**: Accepted (Temporary)
**Date**: 2024 (Initial implementation)
**Deciders**: Development Team

### Context

We need a way to store profile images for development. Options:
- Cloud storage (Supabase Storage, AWS S3)
- Local file system
- Browser localStorage

### Decision

Use browser localStorage for profile images in development only. Store as Data URLs (base64 encoded).

**Implementation**:
```typescript
const key = `nexusai_avatar_${userId}`;
localStorage.setItem(key, dataUrl);
```

### Consequences

**Positive**:
- Quick implementation for MVP
- No external service dependency
- No server-side file handling
- Simple to implement

**Negative**:
- Device-specific (not cross-device)
- No cloud backup
- Browser quota limits (5-10MB)
- Lost if browser data cleared
- NOT production-ready
- Base64 overhead (~33% larger)

**Neutral**:
- Works for development and testing
- Must be replaced with cloud storage for production

**Future**: Replace with cloud storage (Supabase Storage, AWS S3, or Cloudflare R2) before production deployment.

---

## ADR-011: TypeScript Strict Mode

**Status**: Accepted
**Date**: 2024 (Initial project setup)
**Deciders**: Development Team

### Context

We need a type system that:
- Catches errors at compile time
- Improves code quality
- Provides better IDE support
- Enables safer refactoring

### Decision

Use TypeScript with strict mode enabled across the entire codebase.

**Configuration**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    ...
  }
}
```

### Consequences

**Positive**:
- Catches errors at compile time
- Better IDE support (autocomplete, refactoring)
- Self-documenting code
- Safer refactoring
- Improved code quality

**Negative**:
- Learning curve for developers unfamiliar with TypeScript
- More verbose code (type annotations)
- Longer development time initially
- Some third-party libraries have poor type definitions

**Neutral**:
- Requires type definitions for all dependencies
- Build step required (TypeScript compilation)

---

## ADR-012: Next.js App Router

**Status**: Accepted
**Date**: 2024 (Initial frontend setup)
**Deciders**: Development Team

### Context

We need a frontend framework that:
- Supports React
- Provides server-side rendering
- Has good performance
- Has strong community support

### Decision

Use Next.js 15 with App Router (app directory) for the frontend.

### Consequences

**Positive**:
- Server-side rendering out of the box
- Excellent performance
- Strong community and ecosystem
- Built-in optimization
- API routes for backend-for-frontend
- File-based routing

**Negative**:
- Learning curve for App Router (newer than Pages Router)
- Some limitations compared to custom React setup
- Build complexity
- Verbose for simple apps

**Neutral**:
- Requires Node.js server
- Can deploy to Vercel or other platforms

---

## ADR-013: Fastify for Backend

**Status**: Accepted
**Date**: 2024 (Initial backend setup)
**Deciders**: Development Team

### Context

We need a backend framework that:
- Is fast and efficient
- Has good TypeScript support
- Provides plugin system
- Has good community support

### Decision

Use Fastify 5 for the backend API.

### Consequences

**Positive**:
- Very fast performance
- Excellent TypeScript support
- Plugin system (@fastify/cookie, @fastify/cors)
- Schema validation built-in
- Good developer experience
- Low overhead

**Negative**:
- Smaller ecosystem compared to Express
- Less documentation and examples
- Learning curve for developers familiar with Express
- Some plugins may be less mature

**Neutral**:
- Requires TypeScript compilation
- Can be deployed to any Node.js hosting

---

## ADR-014: CSS Variables for Theming

**Status**: Accepted
**Date**: 2024 (Initial frontend styling)
**Deciders**: Development Team

### Context

We need a styling approach that:
- Supports theming
- Is easy to maintain
- Works with React
- Doesn't require heavy build tools

### Decision

Use CSS with CSS variables for theming. No CSS-in-JS library (like styled-components or emotion).

**Implementation**:
```css
:root {
  --bg-primary: #f5f5f5;
  --text-primary: #1a1a1a;
  --accent-primary: #6366f1;
}
```

### Consequences

**Positive**:
- Simple and lightweight
- No additional dependencies
- Works with any CSS framework
- Easy to implement theming
- Good performance
- Works with CSS modules if needed

**Negative**:
- No scoped styles by default
- No type safety for styles
- Limited dynamic styling capabilities
- Must be careful with naming conflicts

**Neutral**:
- Works well with component-based architecture
- Can add CSS-in-JS later if needed

---

## ADR-015: Visibility-Based Session Refresh

**Status**: Accepted
**Date**: 2024 (AuthContext optimization)
**Deciders**: Development Team

### Context

The original AuthContext used `setInterval` to poll the session every 30 seconds. This caused:
- Unnecessary network traffic
- Potential timing attack vector
- Wasted resources when tab is inactive

### Decision

Replace polling with visibility-based session refresh. Refresh session only when page becomes visible (user returns to tab).

**Implementation**:
```typescript
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    refreshUser();
  }
};

document.addEventListener('visibilitychange', handleVisibilityChange);
```

### Consequences

**Positive**:
- No unnecessary background network requests
- Better performance
- Reduced server load
- No timing attack vector
- Better user experience (session fresh when user returns)

**Negative**:
- Session may be stale if user keeps tab open but inactive for long time
- Less frequent session validation
- May miss session revocation if tab is open

**Neutral**:
- Abort controller prevents race conditions
- Still validates session on API calls

---

## ADR-016: Guest Mode Support

**Status**: Accepted
**Date**: 2024 (Initial chat implementation)
**Deciders**: Development Team

### Context

We want to allow users to try the chat functionality without requiring registration. This:
- Reduces friction for new users
- Allows product testing
- Provides immediate value

### Decision

Implement guest mode for chat. Guests can chat without authentication, but conversations are not persisted (in-memory only).

**Implementation**:
- AI endpoint supports optional authentication
- Guest conversations stored in browser memory (Map)
- No database persistence for guest conversations
- Prompt guests to sign up to save conversations

### Consequences

**Positive**:
- Reduced friction for new users
- Allows product testing without commitment
- Immediate value delivery
- Simpler onboarding

**Negative**:
- Inconsistent experience (guest vs authenticated)
- No conversation history for guests
- Lost on page refresh
- Harder to convert guests to registered users

**Neutral**:
- AI service gets null user_id for guests
- Guest conversations use fixed ID ('guest')

---

## Future ADRs

The following architectural decisions may need to be made in the future:

### ADR-017: Cloud Storage for Files (Pending)
- Decision on cloud storage provider (Supabase Storage, AWS S3, Cloudflare R2)
- Migration strategy from localStorage

### ADR-018: Caching Strategy (Pending)
- Decision on caching layer (Redis, Memcached)
- Cache invalidation strategy
- Cache key design

### ADR-019: Multi-Tenancy (Pending)
- Decision on multi-tenancy approach (schema per tenant, row-level filtering)
- Tenant isolation strategy
- Tenant onboarding flow

### ADR-020: Real-Time Features (Pending)
- Decision on real-time technology (WebSockets, Server-Sent Events, WebSub)
- Use cases for real-time features
- Scalability considerations

## References

- [01_PROJECT_OVERVIEW.md](./01_PROJECT_OVERVIEW.md) - Project overview
- [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) - Architecture diagrams
- [02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md) - Codebase structure
