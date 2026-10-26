-- Grant access to nexus schema for Supabase Data API
-- This allows the API to access the nexus schema
-- Note: This migration is a no-op for Neon because:
-- 1. The "anon" and "authenticated" roles are Supabase-specific
-- 2. Neon does not provide these Supabase Auth roles
-- Access control will be handled at the application layer instead

-- No grants applied for Neon - application-level authorization will be used
-- This migration is kept for compatibility with the migration numbering system
-- but does not apply any Supabase-specific role grants for Neon
