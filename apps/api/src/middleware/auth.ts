/**
 * Authentication Middleware
 *
 * Validates HTTP-only session cookies and sets request.accountId
 */

import type { FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { verifySessionToken } from '../auth-utils.js';

// Extend FastifyRequest to include accountId
declare module 'fastify' {
  interface FastifyRequest {
    accountId?: string;
  }
}

const config = readDatabaseConfig();
const db = createDatabaseClient(config);
let dbConnected = false;

async function ensureDbConnected() {
  if (!dbConnected) {
    await db.connect();
    dbConnected = true;
  }
}

/**
 * Authentication middleware
 * Validates session cookie and sets request.accountId
 */
export async function authMiddleware(request: FastifyRequest, reply: FastifyReply) {
  const sessionToken = request.cookies.nexus_session;
  const sessionId = request.cookies.nexus_session_id;

  if (!sessionToken) {
    return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
  }

  try {
    await ensureDbConnected();

    // Efficient lookup: use session_id if available, otherwise fallback to old method
    let session = null;

    if (sessionId) {
      // Direct lookup by session_id (efficient)
      const sessionResult = await db.query(
        `SELECT s.id, s.account_id, s.session_token_hash, a.status
         FROM nexus.auth_sessions s
         JOIN nexus.accounts a ON s.account_id = a.id
         WHERE s.id = $1
         AND s.revoked_at IS NULL
         AND s.expires_at > NOW()`,
        [sessionId]
      );

      if (sessionResult.rows.length > 0) {
        const sessionRow = sessionResult.rows[0] as { id: string; account_id: string; session_token_hash: string; status: string };
        const isValid = await verifySessionToken(sessionToken, sessionRow.session_token_hash);
        if (isValid) {
          session = sessionRow;
        }
      }
    }

    // Fallback: retrieve all active sessions (for backward compatibility)
    if (!session) {
      const sessionsResult = await db.query(
        `SELECT s.id, s.account_id, s.session_token_hash, a.status
         FROM nexus.auth_sessions s
         JOIN nexus.accounts a ON s.account_id = a.id
         WHERE s.revoked_at IS NULL
         AND s.expires_at > NOW()
         ORDER BY s.created_at DESC
         LIMIT 100`
      );

      for (const sessionRow of sessionsResult.rows) {
        const row = sessionRow as { id: string; account_id: string; session_token_hash: string; status: string };
        const isValid = await verifySessionToken(sessionToken, row.session_token_hash);
        if (isValid) {
          session = row;
          break;
        }
      }
    }

    if (!session) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'invalid_session' });
    }

    const sessionData = session as { account_id: string; status: string; id: string };

    // Check account status
    if (sessionData.status !== 'active') {
      return reply.status(403).send({ error: 'Forbidden', code: 'account_inactive' });
    }

    // Set accountId on request
    request.accountId = sessionData.account_id;

    // Update last_seen_at
    await db.query(
      `UPDATE nexus.auth_sessions
       SET last_seen_at = NOW()
       WHERE id = $1`,
      [sessionData.id]
    );
  } catch (error) {
    console.error('[Auth Middleware] Error:', error);
    return reply.status(500).send({ error: 'Authentication failed' });
  }
}

/**
 * Optional authentication middleware
 * Sets request.accountId if session exists, but doesn't fail if not
 */
export async function optionalAuthMiddleware(request: FastifyRequest, reply: FastifyReply) {
  const sessionToken = request.cookies.nexus_session;
  const sessionId = request.cookies.nexus_session_id;

  if (!sessionToken) {
    return; // No session, continue without accountId
  }

  try {
    await ensureDbConnected();

    // Efficient lookup: use session_id if available
    let session = null;

    if (sessionId) {
      const sessionResult = await db.query(
        `SELECT s.id, s.account_id, s.session_token_hash, a.status
         FROM nexus.auth_sessions s
         JOIN nexus.accounts a ON s.account_id = a.id
         WHERE s.id = $1
         AND s.revoked_at IS NULL
         AND s.expires_at > NOW()`,
        [sessionId]
      );

      if (sessionResult.rows.length > 0) {
        const sessionRow = sessionResult.rows[0] as { id: string; account_id: string; session_token_hash: string; status: string };
        const isValid = await verifySessionToken(sessionToken, sessionRow.session_token_hash);
        if (isValid && sessionRow.status === 'active') {
          request.accountId = sessionRow.account_id;
          return;
        }
      }
    }

    // Fallback for backward compatibility
    const sessionsResult = await db.query(
      `SELECT s.id, s.account_id, s.session_token_hash, a.status
       FROM nexus.auth_sessions s
       JOIN nexus.accounts a ON s.account_id = a.id
       WHERE s.revoked_at IS NULL
       AND s.expires_at > NOW()
       ORDER BY s.created_at DESC
       LIMIT 100`
    );

    for (const sessionRow of sessionsResult.rows) {
      const row = sessionRow as { id: string; account_id: string; session_token_hash: string; status: string };
      const isValid = await verifySessionToken(sessionToken, row.session_token_hash);
      if (isValid && row.status === 'active') {
        request.accountId = row.account_id;
        break;
      }
    }
  } catch (error) {
    console.error('[Optional Auth Middleware] Error:', error);
    // Continue without accountId on error
  }
}
