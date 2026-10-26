# NexusAI Authentication and Security

## Overview

NexusAI implements self-managed email/password authentication with secure session management using HTTP-only cookies. This document covers the authentication implementation, security measures, and best practices.

## Authentication System

### Type

Self-managed email/password authentication (not dependent on external identity providers like Auth0 or Supabase Auth).

### Implementation Details

**Password Hashing**: bcrypt
**Session Storage**: Database-backed (nexus.auth_sessions table)
**Session Cookie**: HTTP-only nexus_session cookie
**Session Duration**: 7 days
**Cookie Security**: HttpOnly, SameSite=Lax, secure in production

## Password Security

### Password Hashing Algorithm

**Algorithm**: bcrypt
**Cost Factor**: Default (typically 10-12 rounds)
**Implementation**: `apps/api/src/auth-utils.ts`

**Functions**:
```typescript
hashPassword(password: string): Promise<string>
verifyPassword(password: string, hash: string): Promise<boolean>
```

### Password Requirements

- **Minimum Length**: 8 characters
- **Validation**: Backend and frontend both enforce 8-character minimum
- **No Complexity Requirements**: Currently only length (future: consider adding uppercase, number, special character)

### Password Storage

- **Hashed**: Never stored in plaintext
- **Salt**: Automatically handled by bcrypt
- **Column**: `accounts.password_hash` (varchar, nullable)
- **Migration**: Added in migration 016_add_password_hash.sql

## Session Management

### Session Token Generation

**File**: `apps/api/src/auth-utils.ts`

**Functions**:
```typescript
generateSessionToken(): string
hashSessionToken(token: string): Promise<string>
verifySessionToken(token: string, hash: string): Promise<boolean>
```

**Process**:
1. Generate random session token (UUID)
2. Hash token with bcrypt for storage
3. Store hash in database
4. Return plaintext token to client via cookie
5. On subsequent requests, hash token and compare with stored hash

### Session Cookie

**Cookie Name**: nexus_session
**Cookie Attributes**:
- `HttpOnly`: true (prevents JavaScript access)
- `SameSite`: Lax (CSRF protection, allows navigation)
- `Path`: / (entire domain)
- `Max-Age`: 604800 seconds (7 days)
- `Secure`: true in production (HTTPS only)

**Example Set-Cookie Header**:
```
Set-Cookie: nexus_session=<token>; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800
```

### Session Storage

**Table**: nexus.auth_sessions

**Columns**:
- `id`: Session UUID
- `account_id`: Associated account
- `session_token_hash`: Hashed session token
- `created_at`: Session creation time
- `expires_at`: Session expiration time
- `last_seen_at`: Last activity time
- `revoked_at`: Revocation time (if revoked)
- `status`: Session status (active, expired, revoked)

### Session Validation

**Middleware**: `apps/api/src/middleware/auth.ts`

**Process**:
1. Extract nexus_session cookie from request
2. Query all active sessions for the account
3. Compare token hash against each session hash using bcrypt
4. Check account status (must be 'active')
5. Update last_seen_at timestamp
6. Set request.accountId for use in route handlers

**Performance Note**: bcrypt comparison requires rehashing, so we query up to 100 recent sessions and compare against each.

### Session Expiration

- **Duration**: 7 days from creation
- **Validation**: Checked on each request
- **Cleanup**: Manual cleanup required (not automated)
- **Revocation**: Manual revoke (logout)

## Authentication Endpoints

### POST /api/v1/auth/register

**File**: `apps/api/src/routes/auth.ts`

**Process**:
1. Validate email and password (8 characters minimum)
2. Normalize email to lowercase
3. Check if email already exists
4. Hash password with bcrypt
5. Create account in nexus.accounts
6. Create session in nexus.auth_sessions
7. Set nexus_session cookie
8. Return account_id and email

**Security Considerations**:
- Email normalization prevents case-sensitivity issues
- Password hashing prevents plaintext storage
- Session creation prevents double registration
- Rate limiting (implementation exists, not production-tested)

### POST /api/v1/auth/login

**File**: `apps/api/src/routes/auth.ts`

**Process**:
1. Validate email and password
2. Query account by email
3. Check account status (must be 'active')
4. Verify password with bcrypt
5. Create new session
6. Set nexus_session cookie
7. Return account_id and email

**Security Considerations**:
- Generic error message ("Invalid email or password") prevents email enumeration
- Account status check prevents suspended/deleted account login
- New session on each login prevents session fixation
- Rate limiting prevents brute force attacks

### POST /api/v1/auth/logout

**File**: `apps/api/src/routes/auth.ts`

**Process**:
1. Extract nexus_session cookie
2. Find session by comparing token against hashes
3. Mark session as revoked in database
4. Clear nexus_session cookie
5. Return success

**Security Considerations**:
- Session revocation prevents reuse
- Cookie clearing on client
- Still clears cookie even if database error (fail-safe)

### GET /api/v1/auth/session

**File**: `apps/api/src/routes/auth.ts`

**Process**:
1. Extract nexus_session cookie
2. Find session by comparing token against hashes
3. Check account status
4. Update last_seen_at
5. Return account_id and email if valid

**Security Considerations**:
- Validates session on each request
- Updates last_seen_at for activity tracking
- Returns 401 if invalid or expired

## Authentication Middleware

### authMiddleware

**File**: `apps/api/src/middleware/auth.ts`

**Usage**: Required for authenticated endpoints

**Process**:
1. Validates nexus_session cookie
2. Sets request.accountId
3. Returns 401 if invalid
4. Returns 403 if account not active

**Example**:
```typescript
app.get('/api/v1/profile', { preHandler: authMiddleware }, handler);
```

### optionalAuthMiddleware

**File**: `apps/api/src/middleware/auth.ts`

**Usage**: Optional authentication (guest mode support)

**Process**:
1. Validates nexus_session cookie if present
2. Sets request.accountId if valid
3. Continues without accountId if invalid or missing

**Example**:
```typescript
app.post('/api/v1/ai/chat', { preHandler: optionalAuthMiddleware }, handler);
```

## Account Status

### Status Values

- **active**: Account is active and can login
- **suspended**: Account is suspended (cannot login)
- **deletion_pending**: Account pending deletion
- **deleted**: Account is soft-deleted
- **purged**: Account is permanently deleted

### Status Checks

- Login checks: account must be 'active'
- Session validation checks: account must be 'active'
- Middleware checks: account must be 'active'

## Rate Limiting

### Implementation

**File**: `apps/api/src/rate-limit.ts`

**Class**: `InMemoryAuthRateLimit`

**Configuration** (from app.ts):
- Register/Login: 20 attempts per IP per 60 seconds
- Register/Login: 5 attempts per email per 60 seconds
- Logout: 20 attempts per IP per 60 seconds
- Logout: 20 attempts per session per 60 seconds

### Rate Limit Headers

On rate limit exceeded:
- Header: `retry-after: <seconds>`
- Status: 429 Too Many Requests

### Current Status

Implementation exists but not fully tested in production. Rate limiting is recommended before production deployment.

## Security Headers

### Response Headers

All API responses include security headers:

```http
x-request-id: <uuid>
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: no-referrer
access-control-allow-origin: <origin>
access-control-allow-credentials: true
cache-control: private, no-store (for auth endpoints)
```

### Header Descriptions

- **x-request-id**: Unique request ID for tracing
- **x-content-type-options: nosniff**: Prevents MIME sniffing
- **x-frame-options: DENY**: Prevents clickjacking
- **referrer-policy: no-referrer**: Prevents referrer leakage
- **cache-control: private, no-store**: Prevents caching of auth data

## CORS Configuration

### Development

**Origin**: http://localhost:3000
**Credentials**: true
**Methods**: GET, POST, PUT, DELETE, OPTIONS
**Headers**: Content-Type, Authorization

### Production (TODO)

Must update to actual production origin:
- Origin: https://your-domain.com
- Same configuration structure
- HTTPS required for secure cookies

## Security Best Practices

### Implemented

✅ Password hashing with bcrypt
✅ HTTP-only session cookies
✅ SameSite=Lax for CSRF protection
✅ Secure flag in production
✅ Generic error messages (no information leakage)
✅ Account status tracking
✅ Session revocation support
✅ Last seen tracking
✅ Soft delete support
✅ Security headers
✅ CORS configuration

### Recommended for Production

⚠️ Rate limiting (implementation exists, not production-tested)
⚠️ Password complexity requirements (uppercase, number, special character)
⚠️ Account lockout after failed attempts
⚠️ Email verification
⚠️ Password reset flow
⚠️ Two-factor authentication (2FA)
⚠️ Session cleanup automation
⚠️ Audit logging for auth events
⚠️ IP-based blocking for suspicious activity

### Current Limitations

1. **No Email Verification**: Accounts are created without email verification
2. **No Password Reset**: Users cannot reset forgotten passwords
3. **No 2FA**: No two-factor authentication
4. **No Account Lockout**: No automatic lockout after failed attempts
5. **No Session Cleanup**: Expired sessions not automatically cleaned
6. **No Audit Logging**: Auth events not logged
7. **Simple Password Requirements**: Only 8 characters minimum

## Known Security Issues

### 1. Database URL Exposure (ACTION REQUIRED)

**Issue**: DATABASE_URL credential may have been exposed in previous sessions or logs.

**Action Required**: Rotate the Neon database credential via the Neon dashboard.

**Impact**: High if credential is compromised.

**Status**: ⚠️ REQUIRES USER ACTION

### 2. Insecure Cookie Secret (ACTION REQUIRED)

**Issue**: Default/development cookie secret in use.

**Action Required**: Generate a secure random string for COOKIE_SECRET in production.

**Impact**: Session security depends on this secret.

**Status**: ⚠️ REQUIRES USER ACTION

### 3. Rate Limiting Missing (RECOMMENDED)

**Issue**: No rate limiting on authentication endpoints in production.

**Action Required**: Implement and test rate limiting before production deployment.

**Impact**: Vulnerable to brute force attacks.

**Status**: ⚠️ RECOMMENDED FOR PRODUCTION

## Cookie Secret

### Generation

Generate a secure random string:

```bash
openssl rand -base64 32
```

### Configuration

Set in .env file:

```env
COOKIE_SECRET=<your-secure-random-string>
```

### Default Fallback

If not set, uses: 'nexus-cookie-secret-change-in-production'

**Warning**: This is insecure and must be changed for production.

## Password Policy

### Current Policy

- Minimum 8 characters
- No complexity requirements

### Recommended Policy (Future)

- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character
- No common passwords
- No personal information

## Session Cleanup

### Current State

Expired sessions are not automatically cleaned up. Manual cleanup is required.

### Recommended Automation

Create a scheduled job to clean up expired sessions:

```sql
DELETE FROM nexus.auth_sessions
WHERE expires_at < NOW()
OR (revoked_at IS NOT NULL AND revoked_at < NOW() - INTERVAL '30 days');
```

## Audit Logging

### Current State

No audit logging for authentication events.

### Recommended Events to Log

- Account creation
- Login attempts (success and failure)
- Logout
- Password changes
- Email changes
- Account status changes
- Session creation and revocation

## Testing Authentication

### cURL Examples

**Register**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Login**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Get Session**:
```bash
curl -X GET http://localhost:4000/api/v1/auth/session \
  -b cookies.txt
```

**Logout**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/logout \
  -b cookies.txt
```

## Frontend Authentication

### AuthContext

**File**: `apps/web/app/components/AuthContext.tsx`

**Features**:
- Manages user authentication state
- Handles session validation
- Refreshes session on visibility change (not polling)
- Provides login/logout functions
- Supports guest mode

**Session Refresh**:
- Refreshes when page becomes visible (user returns to tab)
- No polling (reduces network traffic)
- Abort controller prevents race conditions

### AuthModal

**File**: `apps/web/app/components/AuthModal.tsx`

**Features**:
- Tab-based UI (Login/Register)
- Email/password form
- Validation (8 character minimum password)
- Error handling

### Backend Auth API

**File**: `apps/web/lib/backend-auth.ts`

**Functions**:
- `register(email, password)`: Register new account
- `login(email, password)`: Login with credentials
- `logout()`: Logout current session
- `getSession()`: Get current session

## Security Checklist

### Before Production Deployment

- [ ] Rotate DATABASE_URL
- [ ] Generate secure COOKIE_SECRET
- [ ] Enable rate limiting
- [ ] Update CORS origin to production domain
- [ ] Enable HTTPS
- [ ] Set secure flag on cookies
- [ ] Implement email verification
- [ ] Implement password reset
- [ ] Add account lockout
- [ ] Implement audit logging
- [ ] Set up session cleanup automation
- [ ] Review and update password policy
- [ ] Enable monitoring for auth events
- [ ] Set up alerts for suspicious activity

## References

- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API documentation
- [06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md) - Database schema
- [13_TECHNICAL_DEBT_AND_LIMITATIONS.md](./13_TECHNICAL_DEBT_AND_LIMITATIONS.md) - Known issues
