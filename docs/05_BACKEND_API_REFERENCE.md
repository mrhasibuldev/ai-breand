# NexusAI Backend API Reference

## Overview

The NexusAI backend API is built with Fastify 5 and provides RESTful endpoints for authentication, profile management, conversations, and AI chat. All endpoints use JSON for request/response bodies.

## Base URL

**Development**: http://localhost:4000
**Production**: (TODO - configure production URL)

## API Version

Current version: v1
All endpoints are prefixed with `/api/v1`

## Authentication

### Authentication Method

- **Type**: HTTP-only cookie (nexus_session)
- **Cookie Name**: nexus_session
- **Duration**: 7 days
- **Security**: HttpOnly, SameSite=Lax, secure in production

### Authenticated Endpoints

Most endpoints require authentication via the nexus_session cookie. The backend validates the session cookie and sets `request.accountId` for use in business logic.

### Guest Mode

Some endpoints support optional authentication (guest mode). Guests can use the AI chat endpoint without being logged in, but their conversations are not persisted.

## Response Format

### Success Response

```json
{
  "status": "ok",
  "data": { ... }
}
```

### Error Response

```json
{
  "error": "Error message",
  "code": "error_code"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 502 | Bad Gateway (AI service unavailable) |
| 503 | Service Unavailable |
| 504 | Gateway Timeout (AI service timeout) |

## Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register

Register a new user account.

**File**: `apps/api/src/routes/auth.ts`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Validation**:
- email: Required, valid email format
- password: Required, minimum 8 characters

**Response (201 Created)**:
```json
{
  "account_id": "uuid",
  "email": "user@example.com",
  "authenticated": true
}
```

**Error Responses**:
- 400: Invalid input
- 409: Email already registered
- 500: Registration failed

**Headers**:
- Set-Cookie: nexus_session=<token>; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800

**Implementation Details**:
- Normalizes email to lowercase
- Hashes password with bcrypt
- Creates account in nexus.accounts table
- Creates session in nexus.auth_sessions table
- Sets HTTP-only cookie

---

#### POST /api/v1/auth/login

Authenticate with email and password.

**File**: `apps/api/src/routes/auth.ts`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Validation**:
- email: Required
- password: Required

**Response (200 OK)**:
```json
{
  "account_id": "uuid",
  "email": "user@example.com",
  "authenticated": true
}
```

**Error Responses**:
- 400: Invalid input
- 401: Invalid email or password
- 403: Account not active
- 500: Login failed

**Headers**:
- Set-Cookie: nexus_session=<token>; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800

**Implementation Details**:
- Verifies password with bcrypt
- Checks account status (must be 'active')
- Creates new session
- Updates last_seen_at

---

#### POST /api/v1/auth/logout

Invalidate the current session.

**File**: `apps/api/src/routes/auth.ts`

**Authentication**: Required

**Request Body**: None

**Response (200 OK)**:
```json
{
  "logged_out": true
}
```

**Error Responses**:
- 401: Unauthorized (no session)
- 500: Logout failed

**Headers**:
- Clear-Cookie: nexus_session; Path=/

**Implementation Details**:
- Marks session as revoked in database
- Clears cookie
- Works even if database error occurs (still clears cookie)

---

#### GET /api/v1/auth/session

Validate current session and get user info.

**File**: `apps/api/src/routes/auth.ts`

**Authentication**: Required (via cookie)

**Request Body**: None

**Response (200 OK)**:
```json
{
  "authenticated": true,
  "account_id": "uuid",
  "email": "user@example.com"
}
```

**Error Responses**:
- 401: Unauthorized (invalid or expired session)
- 403: Account not active
- 500: Session validation failed

**Implementation Details**:
- Validates session token against all active session hashes
- Checks account status
- Updates last_seen_at
- Returns user info if valid

---

### Profile Endpoints

#### GET /api/v1/profile

Get current user's profile.

**File**: `apps/api/src/routes/profile.ts`

**Authentication**: Required

**Request Body**: None

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "display_name": "John Doe",
  "age_band": "25-34",
  "locale": "en-US",
  "timezone": "America/New_York",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "deleted_at": null
}
```

**Error Responses**:
- 401: Unauthorized
- 404: Profile not found

**Implementation Details**:
- Uses ProfileRepository.findByAccountId()
- Returns 404 if profile doesn't exist

---

#### POST /api/v1/profile

Create a new profile.

**File**: `apps/api/src/routes/profile.ts`

**Authentication**: Required

**Request Body**:
```json
{
  "displayName": "John Doe",
  "ageBand": "25-34",
  "locale": "en-US",
  "timezone": "America/New_York"
}
```

**Validation**:
- All fields are optional
- displayName: String
- ageBand: String
- locale: String
- timezone: String

**Response (201 Created)**:
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "display_name": "John Doe",
  "age_band": "25-34",
  "locale": "en-US",
  "timezone": "America/New_York",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "deleted_at": null
}
```

**Error Responses**:
- 401: Unauthorized
- 500: Creation failed

**Implementation Details**:
- Uses ProfileRepository.create()
- Account ID from session

---

#### PUT /api/v1/profile

Update existing profile.

**File**: `apps/api/src/routes/profile.ts`

**Authentication**: Required

**Request Body**:
```json
{
  "displayName": "Jane Doe",
  "ageBand": "35-44",
  "locale": "en-GB",
  "timezone": "Europe/London"
}
```

**Validation**:
- All fields are optional
- Only provided fields are updated

**Response (200 OK)**:
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "display_name": "Jane Doe",
  "age_band": "35-44",
  "locale": "en-GB",
  "timezone": "Europe/London",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z",
  "deleted_at": null
}
```

**Error Responses**:
- 401: Unauthorized
- 404: Profile not found
- 500: Update failed

**Implementation Details**:
- Uses ProfileRepository.update()
- Dynamic update query (only provided fields)
- Returns 404 if profile doesn't exist

---

### Conversation Endpoints

#### GET /api/v1/conversations

List user's conversations.

**File**: `apps/api/src/routes/conversations.ts`

**Authentication**: Required

**Request Body**: None

**Response (200 OK)**:
```json
[
  {
    "id": "uuid",
    "account_id": "uuid",
    "status": "active",
    "title": "Conversation Title",
    "started_at": "2024-01-01T00:00:00Z",
    "ended_at": null,
    "deleted_at": null
  }
]
```

**Error Responses**:
- 401: Unauthorized
- 500: Failed to list conversations

**Implementation Details**:
- Uses ConversationRepository.listByAccountId()
- Ordered by started_at DESC
- Only returns non-deleted conversations

---

#### POST /api/v1/conversations

Create a new conversation.

**File**: `apps/api/src/routes/conversations.ts`

**Authentication**: Required

**Request Body**:
```json
{
  "title": "New Conversation"
}
```

**Validation**:
- title: Optional string

**Response (201 Created)**:
```json
{
  "id": "uuid",
  "account_id": "uuid",
  "status": "active",
  "title": "New Conversation",
  "started_at": "2024-01-01T00:00:00Z",
  "ended_at": null,
  "deleted_at": null
}
```

**Error Responses**:
- 401: Unauthorized
- 500: Creation failed

**Implementation Details**:
- Uses ConversationRepository.create()
- Status defaults to 'active'
- Account ID from session

---

#### GET /api/v1/conversations/:id

Get specific conversation with messages.

**File**: `apps/api/src/routes/conversations.ts`

**Authentication**: Required

**URL Parameters**:
- id: Conversation UUID

**Request Body**: None

**Response (200 OK)**:
```json
{
  "conversation": {
    "id": "uuid",
    "account_id": "uuid",
    "status": "active",
    "title": "Conversation Title",
    "started_at": "2024-01-01T00:00:00Z",
    "ended_at": null,
    "deleted_at": null
  },
  "messages": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "sequence_no": 1,
      "sender_role": "user",
      "content": "Hello",
      "content_status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "deleted_at": null
    }
  ]
}
```

**Error Responses**:
- 401: Unauthorized
- 404: Conversation not found
- 500: Failed to load conversation

**Implementation Details**:
- Verifies conversation ownership
- Uses ConversationRepository.findById()
- Uses MessageRepository.listByConversationId()
- Messages ordered by sequence_no ASC

---

#### POST /api/v1/conversations/:id/messages

Add message to conversation.

**File**: `apps/api/src/routes/conversations.ts`

**Authentication**: Required

**URL Parameters**:
- id: Conversation UUID

**Request Body**:
```json
{
  "senderRole": "user",
  "content": "Hello, AI!"
}
```

**Validation**:
- senderRole: Required, must be 'user' or 'assistant'
- content: Required, non-empty string

**Response (201 Created)**:
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "sequence_no": 2,
  "sender_role": "user",
  "content": "Hello, AI!",
  "content_status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "deleted_at": null
}
```

**Error Responses**:
- 401: Unauthorized
- 404: Conversation not found
- 500: Failed to add message

**Implementation Details**:
- Verifies conversation ownership
- Uses MessageRepository.create()
- Auto-increments sequence_no
- Content status defaults to 'active'

---

#### DELETE /api/v1/conversations/:id

Delete conversation (soft delete).

**File**: `apps/api/src/routes/conversations.ts`

**Authentication**: Required

**URL Parameters**:
- id: Conversation UUID

**Request Body**: None

**Response (204 No Content)**

**Error Responses**:
- 401: Unauthorized
- 404: Conversation not found
- 500: Failed to delete

**Implementation Details**:
- Verifies conversation ownership
- Uses ConversationRepository.delete()
- Soft delete (sets deleted_at)
- Returns 204 on success

---

### AI Endpoints

#### POST /api/v1/ai/chat

Send message to AI service and get response.

**File**: `apps/api/src/routes/ai.ts`

**Authentication**: Optional (guest mode supported)

**Request Body**:
```json
{
  "message": "Hello, AI!",
  "conversationId": "uuid",
  "context": [
    {
      "role": "user",
      "content": "Previous message",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Validation**:
- message: Required, non-empty string
- conversationId: Optional UUID
- context: Optional array of previous messages

**Response (200 OK)**:
```json
{
  "response": "AI response text",
  "conversationId": "uuid",
  "messageId": "uuid"
}
```

**Error Responses**:
- 400: Message required
- 502: AI service unavailable
- 504: AI service timeout
- 500: Backend error

**Implementation Details**:
- Forwards request to AI service at AI_SERVICE_URL
- Endpoint: /orchestrate
- Timeout: 10 seconds
- Passes user_id if authenticated
- Supports guest mode (user_id will be null)

**AI Service Request**:
```json
{
  "message": "Hello, AI!",
  "conversation_id": "uuid",
  "context": [...],
  "user_id": "uuid"
}
```

---

#### GET /api/v1/ai/health

Check AI service health.

**File**: `apps/api/src/routes/ai.ts`

**Authentication**: Not required

**Request Body**: None

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "http://127.0.0.1:8000"
}
```

**Error Responses**:
- 503: AI service unreachable

**Implementation Details**:
- Calls AI service /health endpoint
- Returns service status and URL

---

## Health Endpoints

#### GET /health/live

Liveness probe.

**Response (200 OK)**:
```json
{
  "status": "ok",
  "service": "api"
}
```

---

#### GET /health/ready

Readiness probe.

**Response (200 OK)**:
```json
{
  "status": "ready",
  "service": "api"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "not_ready"
}
```

---

## Request Headers

### Standard Headers

- `Content-Type: application/json`
- `Cookie: nexus_session=<token>` (for authenticated requests)

### Response Headers

- `x-request-id: <uuid>` - Unique request ID
- `x-content-type-options: nosniff`
- `x-frame-options: DENY`
- `referrer-policy: no-referrer`
- `access-control-allow-origin: <origin>`
- `access-control-allow-credentials: true`
- `cache-control: private, no-store` (for auth endpoints)

## Rate Limiting

**Status**: Implementation exists in `apps/api/src/rate-limit.ts` but not fully tested in production.

**Implementation**:
- IP-based rate limiting
- Email-based rate limiting
- Configurable windows
- Configurable maximum attempts

**Current Configuration** (from app.ts):
- Register/Login: 20 attempts per IP per 60 seconds
- Register/Login: 5 attempts per email per 60 seconds
- Logout: 20 attempts per IP per 60 seconds
- Logout: 20 attempts per session per 60 seconds

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "code": "error_code",
  "request_id": "uuid",
  "details": [
    {
      "field": "field_name",
      "issue": "validation message"
    }
  ]
}
```

### Common Error Codes

- `invalid_request` - Malformed request
- `unauthenticated` - Not logged in
- `invalid_auth_proof` - Invalid credentials
- `forbidden` - Access denied
- `not_found` - Resource not found
- `conflict` - Resource conflict
- `rate_limited` - Too many requests
- `internal_error` - Server error

## CORS Configuration

**Development**:
- Origin: http://localhost:3000
- Credentials: true
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization

**Production** (TODO):
- Must update to actual production origin
- Same configuration structure

## Security Headers

All responses include security headers:
- `x-content-type-options: nosniff`
- `x-frame-options: DENY`
- `referrer-policy: no-referrer`

## Idempotency

**Status**: Implementation exists in `apps/api/src/idempotency.ts` for DevAuthService mode.

**Usage**:
- Header: `Idempotency-Key: <unique-key>`
- Prevents duplicate operations
- Returns cached result for repeated requests

## Testing

### Example cURL Commands

**Register**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Login**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Get Profile**:
```bash
curl -X GET http://localhost:4000/api/v1/profile \
  -b cookies.txt
```

**AI Chat**:
```bash
curl -X POST http://localhost:4000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!"}' \
  -b cookies.txt
```

## References

- [02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md) - File structure
- [06_DATABASE_GUIDE.md](./06_DATABASE_GUIDE.md) - Database schema
- [07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md) - Security details
