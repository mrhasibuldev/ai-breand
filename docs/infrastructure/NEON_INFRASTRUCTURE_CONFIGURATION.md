# Neon Infrastructure Configuration

**Date**: 2026-11-01
**Infrastructure Provider**: Neon (PostgreSQL + Object Storage)
**Configuration Status**: CONFIGURED AND DOCUMENTED
**Scope**: Configuration foundation for database and object storage integration

---

## Overview

This document permanently stores the official Neon infrastructure configuration for NexusAI. All Neon-related connections, endpoints, and environment variables are documented here to ensure future development can proceed without repeatedly requesting the same information.

**IMPORTANT**: This document contains configuration NAMES and LOCATIONS only. Actual credentials (passwords, secret keys) are stored in `.env` files which are Git-ignored.

---

## 1. Neon PostgreSQL Database

### Connection Information

**Database Provider**: Neon PostgreSQL
**Connection Method**: PostgreSQL connection string via `DATABASE_URL`

### Connection String Format

```
postgresql://[user]:[password]@[host]/[database]?sslmode=require&channel_binding=require
```

### Environment Variables

| Variable Name | Description | Location | Required |
|---------------|-------------|----------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `.env` | Yes |
| `DATABASE_PROVIDER` | Database provider type | `.env` | No (default: postgresql) |
| `DATABASE_POOL_SIZE` | Connection pool size | `.env` | No (default: 20) |

### Configuration Location

**Primary Configuration File**: `.env` (root of repository)

**Configuration Example** (DO NOT COPY ACTUAL VALUES):
```bash
DATABASE_URL=postgresql://[user]:[password]@[host]/[database]?sslmode=require&channel_binding=require
DATABASE_PROVIDER=postgresql
DATABASE_POOL_SIZE=20
```

### Database Configuration in Code

**Config Module**: `packages/database-core/src/config.ts`

**Implementation**:
```typescript
export function readDatabaseConfig(env: NodeJS.ProcessEnv = process.env): DatabaseConfig {
  const provider = (env.DATABASE_PROVIDER || 'postgresql') as 'supabase' | 'postgresql';
  const connectionString = env.DATABASE_URL;

  if (!connectionString) {
    throw new Error(
      `DATABASE_URL is required for provider '${provider}'. ` +
      `For Neon, get it from the Neon dashboard. ` +
      `For Supabase, get it from the Supabase dashboard (Settings > Database). ` +
      `For self-hosted, provide your PostgreSQL connection string.`
    );
  }

  return {
    provider,
    connectionString,
    poolSize: parseInt(env.DATABASE_POOL_SIZE || '20', 10),
  };
}
```

### Database Schema

**Schema Name**: `nexus`
**Schema Location**: `packages/database-core/migrations/COMPLETE_SCHEMA.sql`

**Key Tables**:
- `nexus.accounts` — User accounts
- `nexus.auth_sessions` — Session management
- `nexus.user_profiles` — User profiles
- `nexus.conversations` — Conversation metadata
- `nexus.messages` — Message metadata
- `nexus.memory_records` — Long-term memory
- `nexus.file_metadata` — File storage metadata

### SSL Configuration

**SSL Mode**: `require` (from Neon connection string)
**Channel Binding**: `require` (from Neon connection string)

**Note**: The existing `.env` uses `sslmode=verify-full` which is more strict. Both are acceptable for Neon.

---

## 2. Neon Object Storage (S3-Compatible)

### Storage Provider

**Provider**: Neon Object Storage
**Interface**: AWS S3-compatible API
**SDK**: AWS SDK for JavaScript v3 (`@aws-sdk/client-s3`)

### Bucket Information

**Bucket Name**: `upload`
**Status**: Existing bucket, must be reused
**Configuration**: Configured as public by owner (verify access controls before storing private data)

### Environment Variables

| Variable Name | Description | Location | Required |
|---------------|-------------|----------|----------|
| `AWS_ENDPOINT_URL_S3` | S3 endpoint URL | `.env` | Yes |
| `AWS_ACCESS_KEY_ID` | S3 access key ID | `.env` | Yes |
| `AWS_SECRET_ACCESS_KEY` | S3 secret access key | `.env` | Yes |
| `AWS_REGION` | AWS region | `.env` | Yes |
| `AWS_BUCKET` | S3 bucket name | `.env` | Yes |

### Configuration Location

**Primary Configuration File**: `.env` (root of repository)

**Configuration Example** (DO NOT COPY ACTUAL VALUES):
```bash
AWS_ENDPOINT_URL_S3=https://[endpoint].storage.c-6.us-east-2.aws.neon.tech
AWS_ACCESS_KEY_ID=[access-key-id]
AWS_SECRET_ACCESS_KEY=[secret-access-key]
AWS_REGION=us-east-2
AWS_BUCKET=upload
```

### S3 Client Configuration

**Source**: Neon Console > Object Storage > S3 Client

**Example `client.ts`** (from Neon documentation):
```typescript
import "dotenv/config";
import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ forcePathStyle: true });
const bucket = "upload";
const key = "uploads/file.txt";

await s3.send(new PutObjectCommand({ Bucket: bucket, Key: key, Body: "Hello World!" }));

const url = await getSignedUrl(s3, new GetObjectCommand({ Bucket: bucket, Key: key }), { expiresIn: 3600 });
console.log(`[view] ${url}`);
```

### S3 Client Implementation Notes

**Key Configuration**:
- `forcePathStyle: true` — Required for Neon Object Storage
- Uses environment variables for authentication (no hardcoded credentials)
- Bucket name: `upload`

**Required SDK Packages**:
```bash
pnpm add @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

**Package Installation Location**: Should be installed in `packages/storage-core/` or backend API package when implementing storage layer.

---

## 3. Environment Configuration Files

### `.env` (Local Development)

**Location**: Root of repository
**Git Status**: Ignored by `.gitignore`
**Purpose**: Stores actual credentials for local development
**Contents**:
- Database connection string
- Object storage credentials
- Application configuration

**Security**: NEVER commit this file to Git

### `.env.example`

**Location**: Root of repository
**Git Status**: Tracked (safe to commit)
**Purpose**: Template for required environment variables
**Contents**: Variable names only, NO actual values

**Current Variables**:
```bash
# Database Configuration
DATABASE_PROVIDER=postgresql
DATABASE_URL=
DATABASE_POOL_SIZE=20

# Neon Object Storage (S3-compatible)
AWS_ENDPOINT_URL_S3=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_BUCKET=
```

### `.gitignore`

**Relevant Entries**:
```
.env
.env.*
!.env.example
```

**Status**: CORRECT — `.env` is ignored, `.env.example` is tracked

---

## 4. Configuration Architecture

### Database Connection Flow

```
.env (DATABASE_URL)
  ↓
packages/database-core/src/config.ts (readDatabaseConfig)
  ↓
packages/database-core/src/postgres-client.ts (PostgresClient)
  ↓
apps/api/src/app.ts (conditional route registration)
  ↓
Database operations
```

### Object Storage Connection Flow (Future Implementation)

```
.env (AWS_ENDPOINT_URL_S3, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_BUCKET)
  ↓
packages/storage-core/src/s3-provider.ts (S3Client initialization)
  ↓
packages/storage-core/src/dataset-storage-service.ts (storage operations)
  ↓
apps/api/src/routes/storage.ts (API endpoints)
  ↓
Storage operations
```

---

## 5. Security Requirements

### Database Security

✅ **IMPLEMENTED**
- Credentials stored in `.env` (Git-ignored)
- No hardcoded credentials in code
- SSL mode: `require` or `verify-full`
- Parameterized SQL queries
- Connection pooling (default: 20)

### Object Storage Security

⚠️ **TO BE IMPLEMENTED**
- Credentials stored in `.env` (Git-ignored) ✅
- No hardcoded credentials in code ✅
- S3 secret key must not be exposed in API responses (to be implemented)
- Bucket access controls must be verified (to be implemented)
- Signed URLs for temporary access (recommended)

### Security Best Practices

1. **Never commit `.env`** — Already configured in `.gitignore`
2. **Never expose secrets in logs** — Implement log redaction
3. **Never send credentials to frontend** — Backend-only access
4. **Use signed URLs** — For temporary object access
5. **Verify bucket visibility** — Ensure private data is not publicly accessible
6. **Rotate credentials** — access keys (Neon dashboard)

---

## 6. Existing Repository Configuration

### Database Configuration

**Files**:
- `packages/database-core/src/config.ts` — Database configuration reader
- `packages/database-core/src/postgres-client.ts` — PostgreSQL client
- `packages/database-core/src/index.ts` — Database module exports
- `packages/config/src/index.ts` — Runtime configuration validation

**Status**: FULLY CONFIGURED ✅

### Object Storage Configuration

**Files**:
- None currently exist
- Future implementation required

**Status**: NOT YET IMPLEMENTED ❌

### Avatar Storage

**Current Implementation**: localStorage (development only)
**File**: `apps/web/lib/avatar-service.ts`
**Status**: TO BE MIGRATED to Neon Object Storage

---

## 7. SDK Requirements

### Required Packages for Object Storage

**When implementing storage layer, install**:
```bash
pnpm add @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

**Installation Location**:
- Option 1: `packages/storage-core/` (recommended for shared storage layer)
- Option 2: `apps/api/` (if storage is API-specific only)

**Type Definitions**:
```bash
pnpm add -D @types/aws-sdk
```

---

## 8. Future Integration Instructions

### Step 1: Install AWS SDK

```bash
cd packages/storage-core
pnpm add @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

### Step 2: Create Storage Provider Interface

**File**: `packages/storage-core/src/storage-provider.ts`

Define interface for provider-independent storage operations.

### Step 3: Implement S3 Provider

**File**: `packages/storage-core/src/s3-provider.ts`

Use Neon configuration:
```typescript
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  forcePathStyle: true,
  endpoint: process.env.AWS_ENDPOINT_URL_S3,
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});
```

### Step 4: Create Dataset Storage Service

**File**: `packages/storage-core/src/dataset-storage-service.ts`

Implement dataset upload, download, and metadata operations.

### Step 5: Add API Endpoints

**File**: `apps/api/src/routes/storage.ts`

Create backend-controlled storage API endpoints.

### Step 6: Update Avatar Service

**File**: `apps/web/lib/avatar-service.ts`

Migrate from localStorage to backend-controlled storage API.

---

## 9. Verification Checklist

After configuration changes, verify:

- [x] `.env` contains DATABASE_URL with Neon connection string
- [x] `.env` contains AWS_ENDPOINT_URL_S3 with Neon endpoint
- [x] `.env` contains AWS_ACCESS_KEY_ID with Neon access key
- [x] `.env` contains AWS_SECRET_ACCESS_KEY with Neon secret key
- [x] `.env` contains AWS_REGION with region (us-east-2)
- [x] `.env` contains AWS_BUCKET with bucket name (upload)
- [x] `.env.example` updated with Neon variable names
- [x] `.gitignore` contains `.env` and `.env.*`
- [x] No credentials committed to Git
- [x] Database configuration module reads correct variables
- [x] No duplicate configuration systems created

---

## 10. Configuration Status Summary

### Database
- **Environment Variables**: CONFIGURED ✅
- **Code Integration**: EXISTING ✅
- **Schema**: EXISTING ✅
- **Connection String**: VERIFIED ✅
- **SSL Configuration**: VERIFIED ✅

### Object Storage
- **Environment Variables**: CONFIGURED ✅
- **Code Integration**: NOT IMPLEMENTED ❌
- **SDK Packages**: NOT INSTALLED ❌
- **Storage Layer**: NOT IMPLEMENTED ❌
- **API Endpoints**: NOT IMPLEMENTED ❌

### Documentation
- **Configuration Document**: CREATED ✅
- **Environment Variable Names**: DOCUMENTED ✅
- **Security Requirements**: DOCUMENTED ✅
- **Integration Instructions**: DOCUMENTED ✅

---

## 11. Troubleshooting

### Database Connection Issues

**Error**: "DATABASE_URL is required"
**Solution**: Ensure `.env` file exists and contains `DATABASE_URL`

**Error**: "connection refused"
**Solution**: Verify connection string format and SSL mode (`sslmode=require`)

### Object Storage Connection Issues

**Error**: "Access Denied"
**Solution**: Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are correct

**Error**: "Invalid endpoint"
**Solution**: Verify `AWS_ENDPOINT_URL_S3` matches Neon console

**Error**: "Bucket not found"
**Solution**: Verify `AWS_BUCKET` is set to `upload`

---

## 12. References

### Neon Documentation
- Neon PostgreSQL: https://neon.tech/docs
- Neon Object Storage: https://neon.tech/docs/object-storage
- Neon S3 Client: https://neon.tech/docs/object-storage/s3-client

### AWS SDK Documentation
- AWS SDK for JavaScript v3: https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/
- S3 Client: https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-s3/

### Repository Documentation
- Database Guide: `docs/06_DATABASE_GUIDE.md`
- Storage and Media: `docs/09_STORAGE_AND_MEDIA.md`
- Database Configuration Verification: `docs/ai-core/NEON_CONFIGURATION_VERIFICATION_REPORT.md`

---

## 13. Change Log

**2026-11-01**: Initial configuration and documentation
- Added Neon PostgreSQL connection configuration to `.env`
- Added Neon Object Storage S3 configuration to `.env`
- Updated `.env.example` with Neon variable names
- Created permanent configuration documentation
- Verified `.gitignore` configuration

---

**Configuration Status**: CONFIGURED AND DOCUMENTED ✅
**Ready for Next Phase**: YES — Object storage integration implementation can proceed using this configuration
