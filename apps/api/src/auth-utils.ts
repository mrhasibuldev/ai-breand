/**
 * Authentication Utilities
 *
 * Password hashing and verification using bcrypt
 */

import bcrypt from 'bcrypt';
import crypto from 'crypto';

const SALT_ROUNDS = 12;

/**
 * Hash a password using bcrypt
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

/**
 * Verify a password against a hash
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

/**
 * Generate a random session token
 */
export function generateSessionToken(): string {
  return crypto.randomUUID();
}

/**
 * Hash a session token for storage
 */
export async function hashSessionToken(token: string): Promise<string> {
  return bcrypt.hash(token, SALT_ROUNDS);
}

/**
 * Verify a session token against a hash
 */
export async function verifySessionToken(token: string, hash: string): Promise<boolean> {
  return bcrypt.compare(token, hash);
}
