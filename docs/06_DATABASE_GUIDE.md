# NexusAI Database Guide

## Overview

NexusAI uses PostgreSQL via Neon (serverless PostgreSQL) as its database. The database uses a custom `nexus` schema with 18 tables for accounts, sessions, profiles, conversations, messages, memory, consent, and more.

## Database Provider

**Provider**: Neon PostgreSQL
**Connection String**: DATABASE_URL environment variable
**Schema**: nexus
**Pool Size**: 20 (configurable via DATABASE_POOL_SIZE)

### Connection String Format

```
postgresql://[user].[project_id]:[password]@[neon-hostname]/[database]?sslmode=verify-full
```

Get your connection string from the Neon dashboard: https://neon.tech

## Schema Overview

### Schema: nexus

All tables are in the `nexus` schema to isolate application data from public schema.

### Tables

1. **accounts** - User accounts
2. **auth_sessions** - Session management
3. **user_profiles** - User profile data
4. **conversations** - Chat conversations
5. **messages** - Chat messages
6. **memory_records** - AI memory with consent
7. **consent_records** - User consent tracking
8. **notification_preferences** - Notification settings
9. **library_items** - User library (notes, bookmarks)
10. **file_metadata** - File storage metadata
11. **usage_logs** - Usage tracking
12. **rate_limits** - Rate limiting data
13. **audit_logs** - Audit trail
14. **jobs** - Background jobs
15. **job_results** - Job execution results
16. **job_dependencies** - Job dependencies
17. **templates** - Template definitions
18. **user_preferences** - User preferences

## Table Definitions

### accounts

User accounts with authentication credentials.

**File**: `packages/database-core/migrations/002_core_identity.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Account ID |
| auth_issuer | varchar(100) | NOT NULL | Authentication issuer (e.g., 'self-managed') |
| auth_subject | varchar(255) | NOT NULL | Authentication subject (e.g., email) |
| email_normalized | varchar(320) | NOT NULL, UNIQUE | Lowercase email address |
| status | text | NOT NULL, DEFAULT 'active', CHECK | Account status |
| email_verified_at | timestamptz | NULL | Email verification timestamp |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| updated_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Last update timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |
| purge_after | timestamptz | NULL | Purge timestamp |

**Constraints**:
- `accounts_auth_identity_uk`: UNIQUE (auth_issuer, auth_subject)
- `accounts_status_ck`: CHECK (status IN ('active', 'suspended', 'deletion_pending', 'deleted', 'purged'))
- `accounts_verified_after_created_ck`: CHECK (email_verified_at IS NULL OR email_verified_at >= created_at)
- `accounts_deleted_state_ck`: CHECK (status NOT IN ('deletion_pending', 'deleted', 'purged') OR deleted_at IS NOT NULL)
- `accounts_purge_after_deleted_ck`: CHECK (purge_after IS NULL OR deleted_at IS NOT NULL)

**Indexes**:
- `accounts_email_nonpurged_uk`: UNIQUE (email_normalized) WHERE status <> 'purged'
- `accounts_status_created_idx`: (status, created_at)

**Triggers**:
- `accounts_set_updated_at`: Updates updated_at on row update

---

### auth_sessions

Session management for authentication.

**File**: `packages/database-core/migrations/002_core_identity.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Session ID |
| account_id | uuid | NOT NULL, FK → accounts.id | Account ID |
| session_token_hash | varchar(255) | NOT NULL, UNIQUE | Hashed session token |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| expires_at | timestamptz | NOT NULL | Expiration timestamp |
| last_seen_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Last activity timestamp |
| revoked_at | timestamptz | NULL | Revocation timestamp |
| status | text | NOT NULL, DEFAULT 'active', CHECK | Session status |

**Constraints**:
- `auth_sessions_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `auth_sessions_token_uk`: UNIQUE (session_token_hash)
- `auth_sessions_status_ck`: CHECK (status IN ('active', 'expired', 'revoked'))
- `auth_sessions_expiry_ck`: CHECK (expires_at > created_at)
- `auth_sessions_last_seen_ck`: CHECK (last_seen_at >= created_at)
- `auth_sessions_revoked_ck`: CHECK (revoked_at IS NULL OR revoked_at >= created_at)
- `auth_sessions_revoked_state_ck`: CHECK (status <> 'revoked' OR revoked_at IS NOT NULL)

**Indexes**:
- `auth_sessions_account_status_idx`: (account_id, status, expires_at)

---

### user_profiles

User profile information.

**File**: `packages/database-core/migrations/003_user_profiles.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Profile ID |
| account_id | uuid | NOT NULL, FK → accounts.id, UNIQUE | Account ID |
| display_name | varchar(120) | NULL | Display name |
| avatar_storage_path | varchar(500) | NULL | Avatar storage path |
| age_band | varchar(40) | NULL | Age band (e.g., '25-34') |
| locale | varchar(20) | NULL | Locale (e.g., 'en-US') |
| timezone | varchar(64) | NULL | Timezone (e.g., 'America/New_York') |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| updated_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Last update timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |

**Constraints**:
- `user_profiles_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `user_profiles_account_uk`: UNIQUE (account_id)
- `user_profiles_display_name_ck`: CHECK (display_name IS NULL OR char_length(btrim(display_name)) > 0)

**Triggers**:
- `user_profiles_set_updated_at`: Updates updated_at on row update

---

### conversations

Chat conversations.

**File**: `packages/database-core/migrations/004_conversations_messages.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Conversation ID |
| account_id | uuid | NOT NULL, FK → accounts.id | Account ID |
| status | text | NOT NULL, DEFAULT 'active', CHECK | Conversation status |
| title | varchar(160) | NULL | Conversation title |
| started_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Start timestamp |
| ended_at | timestamptz | NULL | End timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |

**Constraints**:
- `conversations_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `conversations_account_id_uk`: UNIQUE (account_id, id)
- `conversations_status_ck`: CHECK (status IN ('active', 'ended', 'deleted'))
- `conversations_end_order_ck`: CHECK (ended_at IS NULL OR ended_at >= started_at)
- `conversations_deleted_state_ck`: CHECK (status <> 'deleted' OR deleted_at IS NOT NULL)

**Indexes**:
- `conversations_account_started_idx`: (account_id, started_at DESC)

---

### messages

Chat messages within conversations.

**File**: `packages/database-core/migrations/004_conversations_messages.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Message ID |
| conversation_id | uuid | NOT NULL, FK → conversations.id | Conversation ID |
| sequence_no | integer | NOT NULL, CHECK | Message sequence number |
| sender_role | text | NOT NULL, CHECK | Sender role |
| content | text | NOT NULL, CHECK | Message content |
| content_status | text | NOT NULL, DEFAULT 'active', CHECK | Content status |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |

**Constraints**:
- `messages_conversation_fk`: FOREIGN KEY (conversation_id) REFERENCES nexus.conversations(id) ON DELETE RESTRICT
- `messages_conversation_sequence_uk`: UNIQUE (conversation_id, sequence_no)
- `messages_sequence_ck`: CHECK (sequence_no > 0)
- `messages_role_ck`: CHECK (sender_role IN ('user', 'assistant'))
- `messages_content_ck`: CHECK (char_length(btrim(content)) > 0)
- `messages_content_status_ck`: CHECK (content_status IN ('active', 'redacted', 'deleted', 'blocked'))
- `messages_deleted_state_ck`: CHECK (content_status IN ('deleted', 'redacted') OR deleted_at IS NULL OR content_status = 'blocked')

**Indexes**:
- `messages_conversation_sequence_idx`: (conversation_id, sequence_no)

---

### memory_records

AI memory records with consent tracking.

**File**: `packages/database-core/migrations/006_memory_records.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Memory ID |
| account_id | uuid | NOT NULL, FK → accounts.id | Account ID |
| consent_record_id | uuid | NULL, FK → consent_records.id | Consent record ID |
| source_message_id | uuid | NULL, FK → messages.id | Source message ID |
| category | text | NOT NULL, CHECK | Memory category |
| purpose | text | NOT NULL, CHECK | Memory purpose |
| value | text | NOT NULL, CHECK | Memory value |
| status | text | NOT NULL, DEFAULT 'candidate', CHECK | Memory status |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| updated_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Last update timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |

**Constraints**:
- `memory_records_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `memory_records_consent_fk`: FOREIGN KEY (consent_record_id) REFERENCES nexus.consent_records(id) ON DELETE RESTRICT
- `memory_records_source_message_fk`: FOREIGN KEY (source_message_id) REFERENCES nexus.messages(id) ON DELETE RESTRICT
- `memory_records_category_ck`: CHECK (category IN ('name', 'age_band', 'wellness_goal', 'preference', 'daily_habit', 'plan_preference', 'custom'))
- `memory_records_purpose_ck`: CHECK (char_length(btrim(purpose)) > 0)
- `memory_records_value_ck`: CHECK (char_length(btrim(value)) > 0)
- `memory_records_status_ck`: CHECK (status IN ('candidate', 'approved', 'rejected', 'revoked', 'deleted'))
- `memory_records_deleted_state_ck`: CHECK (status <> 'deleted' OR deleted_at IS NOT NULL)

**Indexes**:
- `memory_records_account_status_idx`: (account_id, status, created_at DESC)
- `memory_records_category_idx`: (category)

**Triggers**:
- `memory_records_set_updated_at`: Updates updated_at on row update

---

### consent_records

User consent tracking for privacy compliance.

**File**: `packages/database-core/migrations/005_consent_records.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Consent ID |
| account_id | uuid | NOT NULL, FK → accounts.id | Account ID |
| consent_type | text | NOT NULL, CHECK | Type of consent |
| policy_version | varchar(80) | NOT NULL | Policy version |
| decision | text | NOT NULL, CHECK | Consent decision |
| captured_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Capture timestamp |
| revoked_at | timestamptz | NULL | Revocation timestamp |
| capture_source | varchar(40) | NOT NULL, CHECK | Capture source |

**Constraints**:
- `consent_records_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `consent_records_type_ck`: CHECK (char_length(btrim(consent_type)) BETWEEN 1 AND 80)
- `consent_records_decision_ck`: CHECK (decision IN ('granted', 'denied', 'revoked', 'superseded'))
- `consent_records_revoke_ck`: CHECK (decision <> 'revoked' OR revoked_at IS NOT NULL)
- `consent_records_source_ck`: CHECK (char_length(btrim(capture_source)) BETWEEN 1 AND 40)

**Indexes**:
- `consent_records_account_type_time_idx`: (account_id, consent_type, captured_at DESC)

**Triggers**:
- `consent_records_append_only`: Prevents updates and deletes (append-only table)

---

### notification_preferences

User notification preferences.

**File**: `packages/database-core/migrations/007_notification_preferences.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Preference ID |
| account_id | uuid | NOT NULL, FK → accounts.id, UNIQUE | Account ID |
| email_enabled | boolean | NOT NULL, DEFAULT false | Email notifications enabled |
| push_enabled | boolean | NOT NULL, DEFAULT false | Push notifications enabled |
| timezone | varchar(64) | NULL | Timezone |
| updated_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Last update timestamp |

**Constraints**:
- `notification_preferences_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `notification_preferences_account_uk`: UNIQUE (account_id)

**Triggers**:
- `notification_preferences_set_updated_at`: Updates updated_at on row update

---

### library_items

User library (notes, bookmarks, references).

**File**: `packages/database-core/migrations/008_library_items.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | Item ID |
| account_id | uuid | NOT NULL, FK → accounts.id | Account ID |
| item_type | text | NOT NULL, CHECK | Item type |
| title | varchar(255) | NOT NULL, CHECK | Item title |
| description | text | NULL | Item description |
| content | text | NULL | Item content |
| storage_reference | varchar(500) | NULL | Storage reference |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| updated_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Last update timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |

**Constraints**:
- `library_items_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `library_items_account_id_uk`: UNIQUE (account_id, id)
- `library_items_type_ck`: CHECK (item_type IN ('note', 'bookmark', 'reference', 'custom'))
- `library_items_title_ck`: CHECK (char_length(btrim(title)) > 0)

**Indexes**:
- `library_items_account_type_idx`: (account_id, item_type, created_at DESC)

**Triggers**:
- `library_items_set_updated_at`: Updates updated_at on row update

---

### file_metadata

File storage metadata.

**File**: `packages/database-core/migrations/009_file_metadata.sql`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PRIMARY KEY, DEFAULT gen_random_uuid() | File ID |
| account_id | uuid | NOT NULL, FK → accounts.id | Account ID |
| storage_provider | text | NOT NULL, DEFAULT 'supabase', CHECK | Storage provider |
| storage_key | varchar(500) | NOT NULL | Storage key |
| mime_type | varchar(100) | NOT NULL | MIME type |
| size_bytes | bigint | NOT NULL, CHECK | File size in bytes |
| file_name | varchar(255) | NULL | Original file name |
| created_at | timestamptz | NOT NULL, DEFAULT clock_timestamp() | Creation timestamp |
| deleted_at | timestamptz | NULL | Soft delete timestamp |

**Constraints**:
- `file_metadata_account_fk`: FOREIGN KEY (account_id) REFERENCES nexus.accounts(id) ON DELETE RESTRICT
- `file_metadata_account_id_uk`: UNIQUE (account_id, id)
- `file_metadata_provider_ck`: CHECK (storage_provider IN ('supabase', 's3', 'local'))
- `file_metadata_size_ck`: CHECK (size_bytes >= 0)

**Indexes**:
- `file_metadata_account_created_idx`: (account_id, created_at DESC)

---

### Additional Tables

The following tables exist but are not currently actively used in the application:

1. **usage_logs** - Usage tracking
2. **rate_limits** - Rate limiting data
3. **audit_logs** - Audit trail
4. **jobs** - Background jobs
5. **job_results** - Job execution results
6. **job_dependencies** - Job dependencies
7. **templates** - Template definitions
8. **user_preferences** - User preferences

These tables are part of the schema but are reserved for future use.

## Entity Relationship Diagram

```mermaid
erDiagram
    accounts ||--o{ auth_sessions : "has"
    accounts ||--o| user_profiles : "has"
    accounts ||--o{ conversations : "has"
    accounts ||--o{ consent_records : "has"
    accounts ||--o| notification_preferences : "has"
    accounts ||--o{ memory_records : "has"
    accounts ||--o{ library_items : "has"
    accounts ||--o{ file_metadata : "has"
    
    conversations ||--o{ messages : "contains"
    messages ||--o{ memory_records : "references"
    
    consent_records ||--o{ memory_records : "authorizes"
    
    accounts {
        uuid id PK
        varchar auth_issuer
        varchar auth_subject
        varchar email_normalized UK
        text status
        timestamptz email_verified_at
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
        timestamptz purge_after
    }
    
    auth_sessions {
        uuid id PK
        uuid account_id FK
        varchar session_token_hash UK
        timestamptz created_at
        timestamptz expires_at
        timestamptz last_seen_at
        timestamptz revoked_at
        text status
    }
    
    user_profiles {
        uuid id PK
        uuid account_id FK UK
        varchar display_name
        varchar avatar_storage_path
        varchar age_band
        varchar locale
        varchar timezone
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }
    
    conversations {
        uuid id PK
        uuid account_id FK
        text status
        varchar title
        timestamptz started_at
        timestamptz ended_at
        timestamptz deleted_at
    }
    
    messages {
        uuid id PK
        uuid conversation_id FK
        integer sequence_no
        text sender_role
        text content
        text content_status
        timestamptz created_at
        timestamptz deleted_at
    }
    
    consent_records {
        uuid id PK
        uuid account_id FK
        text consent_type
        varchar policy_version
        text decision
        timestamptz captured_at
        timestamptz revoked_at
        varchar capture_source
    }
    
    memory_records {
        uuid id PK
        uuid account_id FK
        uuid consent_record_id FK
        uuid source_message_id FK
        text category
        text purpose
        text value
        text status
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }
```

## Key Relationships

### Primary Key Strategy
- All tables use UUID primary keys (gen_random_uuid())
- UUIDs are generated by the database
- No sequential IDs exposed to clients

### Foreign Key Constraints
- All foreign keys use ON DELETE RESTRICT
- Prevents accidental data deletion
- Requires explicit cleanup before deletion

### Soft Delete Pattern
- Most tables have deleted_at column
- Soft delete instead of hard delete
- Allows data recovery
- Unique constraints exclude soft-deleted rows

### Timestamp Patterns
- created_at: Set on row creation (DEFAULT clock_timestamp())
- updated_at: Updated by trigger on row update
- deleted_at: Set on soft delete
- All timestamps use timestamptz (timezone-aware)

### Check Constraints
- Enum-like values stored as text with CHECK constraints
- Data validation at database level
- Prevents invalid data insertion

## Triggers

### set_updated_at()
Updates updated_at timestamp on row update.

**Applied to**:
- accounts
- user_profiles
- memory_records
- notification_preferences
- library_items

**Function**:
```sql
CREATE OR REPLACE FUNCTION nexus.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = clock_timestamp();
    RETURN NEW;
END;
$$;
```

### prevent_history_mutation()
Prevents updates and deletes on append-only tables.

**Applied to**:
- consent_records

**Function**:
```sql
CREATE OR REPLACE FUNCTION nexus.prevent_history_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Append-only history cannot be updated or deleted: %.%', TG_TABLE_SCHEMA, TG_TABLE_NAME;
END;
$$;
```

## Migrations

### Migration System

**Location**: `packages/database-core/migrations/`

**Files**:
- 001_bootstrap.sql - Schema creation
- 002_core_identity.sql - Accounts and sessions
- 003_user_profiles.sql - User profiles
- 004_conversations_messages.sql - Conversations and messages
- 005_consent_records.sql - Consent tracking
- 006_memory_records.sql - Memory records
- 007_notification_preferences.sql - Notification prefs
- 008_library_items.sql - Library items
- 009_file_metadata.sql - File metadata
- 010_add_avatar_storage_path.sql - Avatar path
- 011_create_g_media_table.sql - Media table
- 012_g_media_rls_policies.sql - RLS policies
- 013_knowledge_tables.sql - Knowledge tables
- 014_fix_conversations_account_id.sql - Fix
- 015_grant_nexus_api_access.sql - Grants
- 016_add_password_hash.sql - Password hash
- 017_add_memory_consent_fk.sql - Foreign key
- COMPLETE_SCHEMA.sql - Full schema (all migrations combined)

### Migration Tracking

**Table**: nexus.schema_migrations

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PRIMARY KEY | Migration ID |
| applied_at | TIMESTAMPTZ NOT NULL | Application timestamp |

**Applied Migrations**:
- 001_bootstrap
- 002_core_identity
- 003_user_profiles
- 004_conversations_messages
- 005_consent_records
- 006_memory_records
- 007_notification_preferences
- 008_library_items
- 009_file_metadata
- 011_create_g_media_table
- 012_g_media_rls_policies

## Database Client

### Configuration

**File**: `packages/database-core/src/config.ts`

**Function**: `readDatabaseConfig(env)`

**Returns**:
```typescript
{
  provider: 'postgresql' | 'supabase',
  connectionString: string,
  poolSize: number
}
```

### Client

**File**: `packages/database-core/src/postgres-client.ts`

**Usage**:
```typescript
import { createDatabaseClient } from '@nexusai/database-core';

const db = createDatabaseClient(config);
await db.connect();

const result = await db.query('SELECT * FROM nexus.accounts');
```

## Repository Pattern

The application uses the repository pattern for data access:

- **ProfileRepository** (`packages/repositories/src/profile-repository.ts`)
- **ConversationRepository** (`packages/repositories/src/conversation-repository.ts`)
- **MessageRepository** (`packages/repositories/src/message-repository.ts`)
- **MemoryRepository** (`packages/repositories/src/memory-repository.ts`)

Repositories handle:
- CRUD operations
- Ownership validation
- Soft delete logic
- Query building

## Performance Considerations

### Indexes

Key indexes are defined for:
- Email lookups (accounts)
- Session lookups (auth_sessions)
- Conversation listings (conversations)
- Message sequences (messages)
- Memory filtering (memory_records)
- Consent tracking (consent_records)

### Query Optimization

- Use indexed columns in WHERE clauses
- Avoid SELECT * (select specific columns)
- Use prepared statements (parameterized queries)
- Connection pooling (pool size: 20)

## Backup and Recovery

### Neon Backup

Neon provides automated backups:
- Point-in-time recovery
- Branching for development
- Automatic WAL archiving

### Manual Backups

For self-hosted PostgreSQL:
```bash
pg_dump -h <host> -U <user> -d <database> -n nexus > backup.sql
```

## Security

### Connection Security

- SSL required (sslmode=verify-full)
- Connection string in environment variable (not in code)
- No plaintext passwords in code

### Data Security

- Passwords hashed with bcrypt
- Session tokens hashed with bcrypt
- Sensitive data not logged
- Soft delete for data retention

### Access Control

- Database access via environment variable
- No direct database access from frontend
- All access through backend API
- Row-level security (RLS) policies exist but not actively used

## References

- [02_CODEBASE_STRUCTURE.md](./02_CODEBASE_STRUCTURE.md) - File structure
- [05_BACKEND_API_REFERENCE.md](./05_BACKEND_API_REFERENCE.md) - API documentation
- [07_AUTHENTICATION_SECURITY.md](./07_AUTHENTICATION_SECURITY.md) - Security details
- COMPLETE_SCHEMA.sql - Full schema SQL
