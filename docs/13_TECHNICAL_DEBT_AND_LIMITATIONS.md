# NexusAI Technical Debt and Limitations

## Overview

This document lists known technical debt, limitations, and areas requiring improvement in the NexusAI application.

## Critical Issues

### 1. Database URL Exposure (ACTION REQUIRED)

**Severity**: HIGH
**Status**: ⚠️ REQUIRES USER ACTION

**Issue**: DATABASE_URL credential may have been exposed in previous sessions or logs.

**Impact**: If credential is compromised, unauthorized access to database is possible.

**Action Required**:
- Rotate the Neon database credential via the Neon dashboard
- Update DATABASE_URL in .env
- Check for any leaked credentials in logs or version control

**Related**: [07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md)

---

### 2. Insecure Cookie Secret (ACTION REQUIRED)

**Severity**: HIGH
**Status**: ⚠️ REQUIRES USER ACTION

**Issue**: Default/development cookie secret in use.

**Impact**: Session security depends on this secret. Default secret is insecure.

**Action Required**:
- Generate a secure random string: `openssl rand -base64 32`
- Set COOKIE_SECRET in .env
- Restart backend

**Related**: [07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md)

---

## High Priority Issues

### 3. Rate Limiting Not Production-Tested

**Severity**: HIGH
**Status**: ⚠️ RECOMMENDED FOR PRODUCTION

**Issue**: Rate limiting implementation exists but is not fully tested in production.

**Impact**: Vulnerable to brute force attacks on authentication endpoints.

**Current State**:
- Implementation exists in `apps/api/src/rate-limit.ts`
- Configured in `apps/api/src/app.ts`
- Not tested under production load

**Action Required**:
- Test rate limiting under load
- Verify rate limit headers are set correctly
- Monitor rate limit effectiveness
- Consider implementing distributed rate limiting (Redis)

**Related**: [07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md)

---

### 4. Profile Images Use localStorage (Not Production-Ready)

**Severity**: HIGH
**Status**: ⚠️ NOT PRODUCTION-READY

**Issue**: Profile images stored in localStorage (development only).

**Impact**:
- Device-specific (not cross-device)
- No cloud backup
- Browser quota limits (5-10MB)
- Lost if browser data cleared
- No CDN distribution

**Current Implementation**:
- Service: `apps/web/lib/avatar-service.ts`
- Key: `nexusai_avatar_{userId}`
- Format: Data URLs (base64)

**Action Required**:
- Implement cloud storage (Supabase Storage, AWS S3, or Cloudflare R2)
- Update avatar-service.ts to upload to cloud
- Store public URL in database (file_metadata table)
- Migrate existing localStorage avatars to cloud
- Deprecate localStorage usage

**Related**: [09_STORAGE_AND_MEDIA.md](./09_STORAGE_AND_MEDIA.md)

---

### 5. No Email Verification

**Severity**: MEDIUM
**Status**: ⚠️ SECURITY CONCERN

**Issue**: Accounts created without email verification.

**Impact**:
- Users can register with fake emails
- No email ownership verification
- Potential for spam accounts

**Current State**:
- Registration creates account immediately
- No verification email sent
- No verification flow

**Action Required**:
- Implement email verification flow
- Add email_verified_at field (already exists in schema)
- Send verification email on registration
- Require verification before full access
- Add resend verification endpoint

---

### 6. No Password Reset

**Severity**: MEDIUM
**Status**: ⚠️ USER EXPERIENCE ISSUE

**Issue**: Users cannot reset forgotten passwords.

**Impact**:
- Users locked out if password forgotten
- No self-service password recovery
- Requires manual intervention

**Current State**:
- No password reset flow
- No reset token mechanism
- No email sending for password reset

**Action Required**:
- Implement password reset flow
- Add reset token mechanism
- Send reset email
- Add reset endpoint
- Add UI for password reset

---

## Medium Priority Issues

### 7. No Session Cleanup Automation

**Severity**: MEDIUM
**Status**: ⚠️ MAINTENANCE ISSUE

**Issue**: Expired sessions not automatically cleaned up.

**Impact**:
- Database bloat over time
- Slower session validation queries
- Manual cleanup required

**Current State**:
- Sessions have expires_at field
- No automated cleanup job
- Manual cleanup required via SQL

**Action Required**:
- Implement scheduled job to clean expired sessions
- Clean sessions older than 30 days
- Clean revoked sessions
- Consider using worker package for scheduled jobs

**SQL for Manual Cleanup**:
```sql
DELETE FROM nexus.auth_sessions
WHERE expires_at < NOW()
OR (revoked_at IS NOT NULL AND revoked_at < NOW() - INTERVAL '30 days');
```

---

### 8. Guest Conversations Not Persisted

**Severity**: LOW (by design)
**Status**: ⚠️ DESIGN DECISION

**Issue**: Guest conversations are not persisted to database.

**Impact**:
- Conversation lost on page refresh
- No conversation history for guests
- Inconsistent experience between guest and authenticated

**Current State**:
- Guest mode uses in-memory storage (Map)
- No database persistence
- By design for privacy/anonymity

**Action Required**:
- Document this behavior clearly
- Consider offering "save this conversation" for guests
- Prompt guests to sign up to save conversations

---

### 9. No Retry Logic for AI Requests

**Severity**: MEDIUM
**Status**: ⚠️ RELIABILITY ISSUE

**Issue**: No automatic retry logic for failed AI requests.

**Impact**:
- Users must manually retry failed requests
- Poor user experience on transient failures
- No exponential backoff

**Current State**:
- Single attempt per request
- 10-second timeout
- Error displayed to user
- No retry mechanism

**Action Required**:
- Implement retry logic with exponential backoff
- Retry on 502, 504, and network errors
- Max retry limit (e.g., 3 attempts)
- User notification on retry attempts

---

### 10. AI Service Dependency

**Severity**: MEDIUM
**Status**: ⚠️ EXTERNAL DEPENDENCY

**Issue**: AI service is external and must be running separately.

**Impact**:
- Application unusable if AI service down
- No fallback mechanism
- No built-in AI model

**Current State**:
- AI service at http://127.0.0.1:8000
- Backend proxies requests to AI service
- No fallback if AI service unavailable

**Action Required**:
- Implement health checks with circuit breaker
- Add fallback to simpler model or canned responses
- Consider embedding minimal AI model for emergency
- Improve error messages when AI service down

---

## Low Priority Issues

### 11. Simple Password Requirements

**Severity**: LOW
**Status**: ⚠️ SECURITY IMPROVEMENT

**Issue**: Password only requires 8 characters, no complexity requirements.

**Impact**:
- Weak passwords allowed
- Increased risk of password guessing
- No complexity enforcement

**Current State**:
- Minimum 8 characters
- No uppercase, number, or special character requirements
- No password strength meter

**Action Required**:
- Add complexity requirements (uppercase, number, special character)
- Implement password strength meter
- Check against common passwords
- Implement password policies

---

### 12. No Audit Logging

**Severity**: LOW
**Status**: ⚠️ COMPLIANCE CONCERN

**Issue**: No audit logging for authentication and sensitive operations.

**Impact**:
- No audit trail for security events
- Difficult to investigate issues
- Compliance concerns (GDPR, HIPAA, etc.)

**Current State**:
- audit_logs table exists but not used
- No logging of auth events
- No logging of data changes

**Action Required**:
- Implement audit logging for auth events
- Log data changes (profile, conversations)
- Use audit_logs table
- Add audit log viewer for admins

---

### 13. No Two-Factor Authentication (2FA)

**Severity**: LOW
**Status**: ⚠️ SECURITY IMPROVEMENT

**Issue**: No two-factor authentication support.

**Impact**:
- Increased risk of account compromise
- No additional security layer

**Current State**:
- Password-only authentication
- No 2FA implementation
- No TOTP or SMS support

**Action Required**:
- Implement TOTP-based 2FA
- Add 2FA setup flow
- Add backup codes
- Make 2FA optional but recommended

---

### 14. No Account Lockout

**Severity**: LOW
**Status**: ⚠️ SECURITY IMPROVEMENT

**Issue**: No automatic account lockout after failed login attempts.

**Impact**:
- Vulnerable to brute force attacks (despite rate limiting)
- No account protection

**Current State**:
- Rate limiting exists but not production-tested
- No account lockout mechanism
- No notification of suspicious activity

**Action Required**:
- Implement account lockout after N failed attempts
- Add lockout duration
- Send email notification on lockout
- Add unlock mechanism

---

### 15. Limited Error Messages

**Severity**: LOW
**Status**: ⚠️ USER EXPERIENCE

**Issue**: Generic error messages in some areas.

**Impact**:
- Difficult for users to understand issues
- Harder to debug problems

**Current State**:
- Some specific error messages (AI service errors in Bangla)
- Some generic error messages
- No error codes for client handling

**Action Required**:
- Standardize error messages
- Add error codes for client handling
- Provide actionable error messages
- Add error context in development mode

---

## Code Quality Issues

### 16. Unused Code

**Severity**: LOW
**Status**: ✅ FIXED

**Issue**: Unused imports and variables causing TypeScript/ESLint errors.

**Current State**: Fixed in NEXUSAI_FULL_REPAIR_REPORT.md

**Files Fixed**:
- apps/web/app/page.tsx
- apps/web/app/components/ChatInterface.tsx
- apps/web/app/components/AuthModal.tsx
- apps/web/app/components/HistoryPage.tsx
- apps/web/app/components/useConversationManager.ts

---

### 17. Console.log Statements

**Severity**: LOW
**Status**: ⚠️ DEBUGGING CODE

**Issue**: Console.log statements throughout codebase for debugging.

**Impact**:
- Performance impact (minimal)
- Information leakage in production
- Cluttered console

**Current State**:
- Console.log statements present
- Intentional for debugging
- Not removed in production builds

**Action Required**:
- Replace with proper logging library (Winston, Pino)
- Add log levels (debug, info, warn, error)
- Remove or disable debug logs in production

---

## Performance Issues

### 18. Session Validation Inefficiency

**Severity**: LOW
**Status**: ⚠️ PERFORMANCE CONCERN

**Issue**: Session validation queries up to 100 recent sessions and compares hash against each.

**Impact**:
- O(n) complexity where n = number of recent sessions
- Slower as session count grows
- bcrypt comparison is expensive

**Current State**:
- Queries up to 100 sessions
- Compares token hash against each using bcrypt
- No caching of validation results

**Action Required**:
- Implement Redis caching for session validation
- Add session ID to cookie (lookup by ID instead of hash comparison)
- Consider JWT with session ID reference

---

### 19. No Caching Layer

**Severity**: LOW
**Status**: ⚠️ PERFORMANCE IMPROVEMENT

**Issue**: No caching layer for frequently accessed data.

**Impact**:
- All requests hit database
- Slower response times
- Increased database load

**Current State**:
- No Redis or other caching
- No CDN for static assets
- No query result caching

**Action Required**:
- Implement Redis for session caching
- Implement Redis for query result caching
- Add CDN for static assets
- Consider HTTP caching headers

---

## Architecture Issues

### 20. AI Core Package Not Used

**Severity**: LOW
**Status**: ⚠️ INCONSISTENCY

**Issue**: ai-core package exists but is not actively used.

**Impact**:
- Unused code
- Confusion about architecture
- Maintenance burden

**Current State**:
- packages/ai-core/ exists with abstractions
- Backend directly proxies to AI service
- No use of ai-core abstractions

**Action Required**:
- Either use ai-core abstractions or remove package
- If using: Implement bridge, orchestrator, safety modules
- If removing: Delete packages/ai-core/

---

### 21. Single Fastify Instance

**Severity**: LOW
**Status**: ⚠️ SCALABILITY CONCERN

**Issue**: Single Fastify instance (no horizontal scaling).

**Impact**:
- Cannot scale horizontally
- Single point of failure
- Limited capacity

**Current State**:
- Single Fastify instance
- No load balancer
- No horizontal scaling

**Action Required**:
- Implement horizontal scaling with load balancer
- Add health checks for load balancer
- Consider containerization (Docker)
- Consider orchestration (Kubernetes)

---

## Documentation Issues

### 22. Incomplete Documentation

**Severity**: LOW
**Status**: ✅ ADDRESSED

**Issue**: Limited technical documentation.

**Current State**: Being addressed with this documentation suite

**Action Required**:
- Keep documentation up to date
- Add API documentation for all endpoints
- Add architecture decision records (ADRs)
- Add troubleshooting guides

---

## Testing Issues

### 23. Limited Automated Testing

**Severity**: MEDIUM
**Status**: ⚠️ QUALITY CONCERN

**Issue**: Minimal automated testing coverage.

**Impact**:
- Reliance on manual testing
- Higher risk of regressions
- Slower development cycle

**Current State**:
- Foundation tests exist
- Keyboard tests exist (Playwright)
- No comprehensive unit tests
- No integration tests
- No E2E tests for main flows

**Action Required**:
- Add unit tests for repositories
- Add integration tests for API endpoints
- Add E2E tests for critical user flows
- Set up test coverage reporting
- Integrate tests into CI pipeline

**Related**: [12_TESTING_AND_QA.md](./12_TESTING_AND_QA.md)

---

## Security Issues

### 24. No Content Filtering for AI

**Severity**: MEDIUM
**Status**: ⚠️ SAFETY CONCERN

**Issue**: No content filtering before sending to AI service.

**Impact**:
- Potential for inappropriate content
- No PII redaction
- No input sanitization

**Current State**:
- Messages sent directly to AI service
- No content filtering
- No PII redaction

**Action Required**:
- Implement content filtering before AI service
- Add PII redaction
- Add input sanitization
- Implement safety checks

---

### 25. No Rate Limiting on AI Endpoint

**Severity**: MEDIUM
**Status**: ⚠️ ABUSE CONCERN

**Issue**: No rate limiting on AI chat endpoint.

**Impact**:
- Vulnerable to abuse
- Potential for high AI service costs
- No protection against spam

**Current State**:
- AI endpoint supports guest mode
- No rate limiting
- No usage tracking

**Action Required**:
- Implement rate limiting on AI endpoint
- Track usage per user/IP
- Implement quota system
- Monitor AI service costs

---

## Dependencies

### 26. Outdated Dependencies

**Severity**: LOW
**Status**: ⚠️ MAINTENANCE

**Issue**: Dependencies may become outdated over time.

**Impact**:
- Security vulnerabilities
- Missing features
- Compatibility issues

**Current State**:
- Dependencies not regularly updated
- No automated dependency updates

**Action Required**:
- Implement Dependabot or Renovate
- Regular dependency audits
- Update dependencies regularly
- Test after dependency updates

---

## Summary

### Critical (Action Required)
1. Database URL exposure - Rotate credential
2. Insecure cookie secret - Generate secure secret

### High Priority
3. Rate limiting not production-tested
4. Profile images use localStorage (not production-ready)

### Medium Priority
5. No email verification
6. No password reset
7. No session cleanup automation
8. No retry logic for AI requests
9. AI service dependency
10. No audit logging
11. Limited automated testing
12. No content filtering for AI
13. No rate limiting on AI endpoint

### Low Priority
14. Simple password requirements
15. No two-factor authentication
16. No account lockout
17. Limited error messages
18. Console.log statements
19. Session validation inefficiency
20. No caching layer
21. AI core package not used
22. Single Fastify instance
23. Outdated dependencies

## References

- [07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md) - Security details
- [09_STORAGE_AND_MEDIA.md](./09_STORAGE_AND_MEDIA.md) - Storage issues
- [12_TESTING_AND_QA.md](./12_TESTING_AND_QA.md) - Testing issues
- [14_FUTURE_ROADMAP.md](./14_FUTURE_ROADMAP.md) - Planned improvements
