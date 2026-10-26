-- Migration 016: Add Password Hash Column
-- Adds password_hash column to accounts table for self-managed authentication
-- Uses bcrypt for secure password hashing

ALTER TABLE nexus.accounts
ADD COLUMN password_hash varchar(255);

-- Add index on email_normalized for login performance
CREATE INDEX IF NOT EXISTS accounts_email_normalized_idx
  ON nexus.accounts (email_normalized)
  WHERE status = 'active';

-- Add comment to document the password hashing approach
COMMENT ON COLUMN nexus.accounts.password_hash IS 'Bcrypt hash of user password. Only used for self-managed authentication (Supabase Auth users do not have this).';
