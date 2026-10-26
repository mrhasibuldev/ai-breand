# Profile Schema Validation Fix - Documentation

## Root Cause Analysis

### Error: `Invalid schema: nexus`

**Primary Cause:**
The Supabase client is configured with `db: { schema: 'nexus' }` in `supabase-client.ts`, but the `nexus` schema doesn't exist in the actual Supabase database because the migration hasn't been applied.

**Why This Happens:**
1. Database schema migration (`COMPLETE_SCHEMA.sql`) hasn't been executed in Supabase
2. The client tries to query `nexus.user_profiles` but the schema doesn't exist
3. Supabase returns "Invalid schema: nexus" error

**Common Schema Validation Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid schema: nexus` | Schema doesn't exist | Run COMPLETE_SCHEMA.sql |
| `relation "user_profiles" does not exist` | Table doesn't exist in schema | Run COMPLETE_SCHEMA.sql |
| `column "xxx" does not exist` | Column missing in table | Update migration |
| `PGRST116` | No rows returned | Profile doesn't exist (expected) |
| `permission denied` | RLS policy blocking | Check RLS policies |

---

## Fix Implementation

### 1. Enhanced Error Handling

**Before:**
```typescript
catch (error: any) {
  console.error('[Profile] Failed to load profile:', error?.message || error);
  return null;
}
```

**After:**
```typescript
catch (error: any) {
  console.error('[Profile] Unexpected error:', {
    message: error?.message,
    stack: error?.stack,
  });
  return null;
}
```

### 2. Schema-Specific Error Detection

```typescript
if (error.message?.includes('Invalid schema') || error.message?.includes('schema')) {
  console.error('[Profile] Schema error:', error.message);
  console.error('[Profile] SOLUTION: Run COMPLETE_SCHEMA.sql in Supabase SQL Editor to create the nexus schema');
  return null;
}
```

### 3. Data Validation Function

```typescript
function validateProfileData(data: any): UserProfile | null {
  if (!data) return null;

  // Check required fields
  if (!data.id || typeof data.id !== 'string') {
    console.error('[Profile] Validation failed: Invalid or missing id');
    return null;
  }

  if (!data.account_id || typeof data.account_id !== 'string') {
    console.error('[Profile] Validation failed: Invalid or missing account_id');
    return null;
  }

  // Build validated profile with fallbacks
  const profile: UserProfile = {
    id: data.id,
    account_id: data.account_id,
    display_name: data.display_name || null,
    avatar_storage_path: data.avatar_storage_path || null,
    created_at: data.created_at || new Date().toISOString(),
    updated_at: data.updated_at || new Date().toISOString(),
  };

  console.log('[Profile] Data validated successfully');
  return profile;
}
```

### 4. Detailed Logging

**Successful Load:**
```
[Profile] Loading profile for user: xxx
[Profile] Data validated successfully
[Profile] Profile loaded successfully
```

**Schema Error:**
```
[Profile] Loading profile for user: xxx
[Profile] Schema error: Invalid schema: nexus
[Profile] SOLUTION: Run COMPLETE_SCHEMA.sql in Supabase SQL Editor to create the nexus schema
```

**Profile Not Found:**
```
[Profile] Loading profile for user: xxx
[Profile] Profile not found for user: xxx
```

---

## How to Update or Relax Schema Validation

### Option 1: Apply Database Schema (Recommended)

**Steps:**
1. Open Supabase Dashboard: https://app.supabase.com
2. Select project: qzfynpuvbybqgmbaccu
3. Go to SQL Editor
4. Copy `packages/database-core/migrations/COMPLETE_SCHEMA.sql`
5. Paste and Run
6. Verify schema created

**Verification:**
```sql
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name = 'nexus';
```

### Option 2: Use Public Schema (Temporary Fallback)

**If you need to use public schema temporarily:**

```typescript
// In supabase-client.ts
export const supabase = configValid && supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey, {
      db: {
        schema: 'public', // Changed from 'nexus'
      },
    }) 
  : null;
```

**Note:** This is only for testing. Production should use `nexus` schema.

### Option 3: Relax Schema Validation

**If backend data structure changes:**

```typescript
function validateProfileData(data: any): UserProfile | null {
  if (!data) return null;

  // More lenient validation
  const profile: UserProfile = {
    id: data.id || 'unknown',
    account_id: data.account_id || 'unknown',
    display_name: data.display_name || data.name || null, // Allow alternative field
    avatar_storage_path: data.avatar_storage_path || data.avatar || null, // Allow alternative field
    created_at: data.created_at || data.createdAt || new Date().toISOString(),
    updated_at: data.updated_at || data.updatedAt || new Date().toISOString(),
  };

  return profile;
}
```

### Option 4: Add Zod/Valibot Validation

**Install validation library:**
```bash
pnpm add zod
```

**Add schema validation:**
```typescript
import { z } from 'zod';

const UserProfileSchema = z.object({
  id: z.string().uuid(),
  account_id: z.string().uuid(),
  display_name: z.string().nullable(),
  avatar_storage_path: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

function validateProfileData(data: any): UserProfile | null {
  try {
    return UserProfileSchema.parse(data);
  } catch (error) {
    console.error('[Profile] Zod validation failed:', error);
    return null;
  }
}
```

---

## UI & Responsive Behavior

### Desktop Profile Trigger

**File:** `apps/web/app/components/MainContent.tsx`

```typescript
const handleProfileClick = () => {
  if (!isAuthenticated) {
    onAuthRequired(); // Opens auth modal for guests
  } else {
    setIsProfileEditOpen(true); // Opens profile edit for authenticated users
  }
};
```

### Mobile Profile Trigger

**File:** `apps/web/app/components/MobileNavigation.tsx`

Ensure the profile click handler is properly connected:
```typescript
<ProfileIcon onClick={handleProfileClick} />
```

**Common Mobile Issues:**
1. **Touch events not firing** - Ensure `onClick` handler is on button element
2. **Drawer not closing** - Add `onClose` handler to mobile drawer
3. **Profile not loading** - Check authentication state before loading

---

## Testing Checklist

### After Schema Application:

- [ ] Profile loads successfully on desktop
- [ ] Profile loads successfully on mobile
- [ ] Profile save works on desktop
- [ ] Profile save works on mobile
- [ ] Avatar upload works
- [ ] Avatar displays after refresh
- [ ] Console shows no schema errors
- [ ] Profile persists after logout/login

### Schema Validation:

- [ ] Required fields present (id, account_id)
- [ ] Optional fields handled (display_name, avatar_storage_path)
- [ ] Null values handled correctly
- [ ] Date fields validated
- [ ] Type checking works

---

## Current Status

✅ **Fixed:**
- Enhanced error handling with detailed logs
- Schema-specific error detection
- Data validation with fallbacks
- Clear error messages with solutions

⏳ **Pending:**
- Database schema application (manual step)
- Storage bucket creation (manual step)

---

## Next Steps

1. **Apply Database Schema (1 minute):**
   - Run `COMPLETE_SCHEMA.sql` in Supabase SQL Editor

2. **Test Profile Load:**
   - Open browser console
   - Click profile button
   - Check logs for success message

3. **Test Profile Save:**
   - Edit profile
   - Save changes
   - Refresh page
   - Verify persistence

4. **Test Mobile:**
   - Open on mobile device
   - Test profile trigger
   - Test profile save
   - Verify responsive behavior
