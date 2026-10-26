# NexusAI Testing and QA

## Overview

This document covers the testing strategy, coverage, and quality assurance processes for the NexusAI application.

## Current Testing Status

### Automated Tests

**Status**: Limited automated testing

**Test Framework**: Vitest

**Test Location**: `tests/` directory

**Current Coverage**:
- Foundation tests exist (test:foundation script)
- Keyboard tests exist (test:keyboard script with Playwright)
- No comprehensive unit tests
- No integration tests
- No E2E tests for main application flow

### Manual Testing

**Status**: Primary testing method

**Areas Tested**:
- Authentication (register, login, logout)
- Profile management
- Chat functionality (guest and authenticated)
- Conversation history
- Mobile responsiveness
- Error handling

## Test Types

### Unit Tests

**Current Status**: Minimal

**Recommended Areas**:
- Repository functions (ProfileRepository, ConversationRepository, MessageRepository)
- Authentication utilities (hashPassword, verifyPassword)
- API client functions
- Avatar service functions
- Validation functions

**Example**:
```typescript
import { describe, it, expect } from 'vitest';
import { hashPassword, verifyPassword } from '@nexusai/auth-core';

describe('Password Utilities', () => {
  it('should hash password', async () => {
    const hash = await hashPassword('password123');
    expect(hash).toBeDefined();
    expect(hash).not.toBe('password123');
  });

  it('should verify password', async () => {
    const hash = await hashPassword('password123');
    const isValid = await verifyPassword('password123', hash);
    expect(isValid).toBe(true);
  });
});
```

### Integration Tests

**Current Status**: None

**Recommended Areas**:
- API endpoints with database
- Authentication flow
- Conversation creation and messaging
- Profile CRUD operations

**Example**:
```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { buildApp } from '@nexusai/api/src/app';

describe('Authentication API', () => {
  let app;

  beforeAll(async () => {
    app = await buildApp();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should register a new user', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/v1/auth/register',
      payload: {
        email: 'test@example.com',
        password: 'password123'
      }
    });

    expect(response.statusCode).toBe(201);
    expect(response.json()).toHaveProperty('account_id');
  });
});
```

### End-to-End Tests

**Current Status**: Playwright keyboard tests exist (test:keyboard)

**Recommended Areas**:
- User registration flow
- Login flow
- Chat flow (guest and authenticated)
- Profile update flow
- Logout flow
- Mobile navigation

**Example**:
```typescript
import { test, expect } from '@playwright/test';

test('user can register and login', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('button:has-text("Sign In")');
  await page.click('button:has-text("Register")');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Welcome')).toBeVisible();
});
```

## Manual Testing Procedures

### Authentication Testing

#### Register New Account

1. Navigate to http://localhost:3000
2. Click "Sign In"
3. Click "Register" tab
4. Enter email: test@example.com
5. Enter password: password123 (8+ characters)
6. Click "Register"
7. Verify: Welcome message displayed
8. Verify: Logged in state

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Expected**: 201 Created with account_id

#### Login with Valid Credentials

1. Logout if logged in
2. Click "Sign In"
3. Enter email: test@example.com
4. Enter password: password123
5. Click "Login"
6. Verify: Welcome message displayed

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt
```

**Expected**: 200 OK with account_id

#### Login with Invalid Credentials

1. Logout if logged in
2. Click "Sign In"
3. Enter email: wrong@example.com
4. Enter password: wrongpassword
5. Click "Login"
6. Verify: Error message displayed

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"wrong@example.com","password":"wrongpassword"}'
```

**Expected**: 401 Unauthorized

#### Logout

1. Ensure logged in
2. Click profile
3. Click "Logout"
4. Verify: Logged out state
5. Verify: Guest state

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/auth/logout \
  -b cookies.txt
```

**Expected**: 200 OK

### Chat Testing

#### Guest Chat

1. Ensure logged out (guest mode)
2. Type message in chat input
3. Press Enter or click Send
4. Verify: User message displayed
5. Verify: AI response displayed
6. Refresh page
7. Verify: Conversation cleared (not persisted)

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!"}'
```

**Expected**: 200 OK with AI response

#### Authenticated Chat

1. Log in
2. Type message in chat input
3. Press Enter or click Send
4. Verify: User message displayed
5. Verify: AI response displayed
6. Refresh page
7. Verify: Conversation persisted

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!"}' \
  -b cookies.txt
```

**Expected**: 200 OK with AI response

### Profile Testing

#### Create Profile

1. Log in
2. Click profile
3. Enter display name
4. Upload avatar (optional)
5. Click "Save"
6. Verify: Profile updated

**cURL**:
```bash
curl -X POST http://localhost:4000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"displayName":"Test User"}' \
  -b cookies.txt
```

**Expected**: 201 Created

#### Update Profile

1. Log in
2. Click profile
3. Update display name
4. Click "Save"
5. Verify: Profile updated

**cURL**:
```bash
curl -X PUT http://localhost:4000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"displayName":"Updated Name"}' \
  -b cookies.txt
```

**Expected**: 200 OK

### Conversation History Testing

#### View Conversations

1. Log in
2. Click "History"
3. Verify: Conversation list displayed
4. Click conversation
5. Verify: Conversation with messages displayed

**cURL**:
```bash
curl -X GET http://localhost:4000/api/v1/conversations \
  -b cookies.txt
```

**Expected**: 200 OK with conversation array

## Database Testing

### Schema Verification

**SQL**:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'nexus' 
ORDER BY table_name;
```

**Expected**: 18 tables

### Data Integrity

**SQL**:
```sql
-- Check accounts
SELECT COUNT(*) FROM nexus.accounts WHERE deleted_at IS NULL;

-- Check sessions
SELECT COUNT(*) FROM nexus.auth_sessions WHERE revoked_at IS NULL AND expires_at > NOW();

-- Check conversations
SELECT COUNT(*) FROM nexus.conversations WHERE deleted_at IS NULL;

-- Check messages
SELECT COUNT(*) FROM nexus.messages WHERE deleted_at IS NULL;
```

### Foreign Key Constraints

**SQL**:
```sql
-- Try to delete account with sessions (should fail)
DELETE FROM nexus.accounts WHERE id = '<account_id>';
```

**Expected**: Error due to foreign key constraint

## API Testing

### Health Endpoints

**cURL**:
```bash
curl http://localhost:4000/health/live
curl http://localhost:4000/health/ready
```

**Expected**: 200 OK with status "ok" or "ready"

### AI Service Health

**cURL**:
```bash
curl http://localhost:4000/api/v1/ai/health
```

**Expected**: 200 OK with status "healthy" or 503 if AI service down

## Mobile Testing

### Responsive Design

**Test Points**:
- Mobile view (< 768px)
- Tablet view (768px - 1024px)
- Desktop view (> 1024px)

**Tools**:
- Browser DevTools device emulation
- Actual mobile device

**Test Cases**:
- Navigation bar adapts to screen size
- Chat interface works on mobile
- Input field accessible on mobile
- Buttons touch-friendly
- No horizontal overflow

**Limitation**: Cross-device localStorage testing requires actual mobile device.

## Performance Testing

### Load Testing

**Current Status**: Not performed

**Recommended Tools**:
- Apache JMeter
- k6
- Artillery

**Test Scenarios**:
- Concurrent user registration
- Concurrent login attempts
- Concurrent chat requests
- Database query performance

### Response Time Targets

- Authentication: < 500ms
- Profile operations: < 300ms
- Conversation list: < 500ms
- Chat message: < 2000ms (includes AI service)

## Security Testing

### Authentication Security

**Test Cases**:
- [ ] SQL injection attempts
- [ ] XSS attempts
- [ ] CSRF attempts
- [ ] Brute force password attempts
- [ ] Session hijacking attempts
- [ ] Cookie security (HttpOnly, SameSite)

### Input Validation

**Test Cases**:
- [ ] Invalid email formats
- [ ] Short passwords (< 8 chars)
- [ ] Empty fields
- [ ] Special characters in inputs
- [ ] Large file uploads

### Rate Limiting

**Test Cases**:
- [ ] Multiple rapid login attempts
- [ ] Multiple rapid registration attempts
- [ ] API endpoint rate limiting

**Status**: Rate limiting implementation exists but not production-tested.

## Accessibility Testing

### WCAG Compliance

**Test Cases**:
- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] ARIA labels
- [ ] Color contrast
- [ ] Focus management

**Tools**:
- axe DevTools
- WAVE
- Lighthouse accessibility audit

**Current Status**: Not performed

## Browser Compatibility

### Supported Browsers

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Test Cases**:
- [ ] Authentication works in all browsers
- [ ] Chat works in all browsers
- [ ] Profile editing works in all browsers
- [ ] localStorage works in all browsers

**Current Status**: Not tested across all browsers

## Continuous Integration

### GitHub Actions

**File**: `.github/workflows/ci.yml`

**Current Status**: CI workflow exists

**Triggers**:
- Push to main
- Pull requests

**Steps**:
- [ ] Install dependencies
- [ ] Type check
- [ ] Lint
- [ ] Build
- [ ] Run tests

## Test Environment Setup

### Local Environment

1. Start backend: `pnpm dev` (in apps/api)
2. Start frontend: `pnpm dev` (in apps/web)
3. Start AI service: External service
4. Ensure database is accessible

### Test Database

Use separate test database or clean data between tests:

```sql
-- Clean test data
DELETE FROM nexus.auth_sessions;
DELETE FROM nexus.messages;
DELETE FROM nexus.conversations;
DELETE FROM nexus.user_profiles;
DELETE FROM nexus.accounts WHERE email LIKE 'test%@example.com';
```

## Test Reporting

### Current State

- Console output for manual tests
- No automated test reports
- No coverage reports

### Recommended Improvements

- HTML test reports
- Coverage reports (Istanbul/nyc)
- Test history tracking
- Failure notifications

## Testing Checklist

### Before Release

- [ ] All manual tests pass
- [ ] Authentication flow works
- [ ] Chat works (guest and authenticated)
- [ ] Profile management works
- [ ] Conversation history works
- [ ] Mobile responsive
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Build succeeds
- [ ] Database schema verified

### Before Production Deployment

- [ ] All automated tests pass
- [ ] Security tests pass
- [ ] Performance tests pass
- [ ] Load tests pass
- [ ] Accessibility tests pass
- [ ] Browser compatibility verified
- [ ] Rate limiting tested
- [ ] Error handling verified
- [ ] Monitoring configured
- [ ] Backup procedures tested

## Recommendations

### Immediate Improvements

1. Add unit tests for repositories
2. Add integration tests for API endpoints
3. Add E2E tests for critical user flows
4. Set up test coverage reporting
5. Add CI test reporting

### Long-term Improvements

1. Implement comprehensive test suite
2. Add performance testing
3. Add security testing
4. Add accessibility testing
5. Add cross-browser testing
6. Implement visual regression testing

## References

- [10_DEVELOPER_SETUP.md](./10_DEVELOPER_SETUP.md) - Setup guide
- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API documentation
- [13_TECHNICAL_DEBT_AND_LIMITATIONS.md](./13_TECHNICAL_DEBT_AND_LIMITATIONS.md) - Known issues
