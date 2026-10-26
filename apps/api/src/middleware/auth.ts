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

  if (!sessionToken) {
    return reply.status(401).send({ error: 'Unauthorized', code: 'no_session' });
  }

  try {
    await ensureDbConnected();

    // Get all active sessions and check the token against each hash
    const sessionsResult = await db.query(
      `SELECT s.id, s.account_id, s.session_token_hash, a.status
       FROM nexus.auth_sessions s
       JOIN nexus.accounts a ON s.account_id = a.id
       WHERE s.revoked_at IS NULL
       AND s.expires_at > NOW()
       ORDER BY s.created_at DESC
       LIMIT 100`
    );

    let matchedSession = null;
    for (const session of sessionsResult.rows) {
      const sessionRow = session as { id: string; account_id: string; session_token_hash: string; status: string };
      const isValid = await verifySessionToken(sessionToken, sessionRow.session_token_hash);
      if (isValid) {
        matchedSession = sessionRow;
        break;
      }
    }

    if (!matchedSession) {
      return reply.status(401).send({ error: 'Unauthorized', code: 'invalid_session' });
    }

    const session = matchedSession as { account_id: string; status: string; id: string };

    // Check account status
    if (session.status !== 'active') {
      return reply.status(403).send({ error: 'Forbidden', code: 'account_inactive' });
    }

    // Set accountId on request
    request.accountId = session.account_id;

    // Update last_seen_at
    await db.query(
      `UPDATE nexus.auth_sessions
       SET last_seen_at = NOW()
       WHERE id = $1`,
      [session.id]
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

  if (!sessionToken) {
    return; // No session, continue without accountId
  }

  try {
    await ensureDbConnected();

    const sessionsResult = await db.query(
      `SELECT s.id, s.account_id, s.session_token_hash, a.status
       FROM nexus.auth_sessions s
       JOIN nexus.accounts a ON s.account_id = a.id
       WHERE s.revoked_at IS NULL
       AND s.expires_at > NOW()
       ORDER BY s.created_at DESC
       LIMIT 100`
    );

    for (const session of sessionsResult.rows) {
      const sessionRow = session as { id: string; account_id: string; session_token_hash: string; status: string };
      const isValid = await verifySessionToken(sessionToken, sessionRow.session_token_hash);
      if (isValid && sessionRow.status === 'active') {
        request.accountId = sessionRow.account_id;
        break;
      }
    }
  } catch (error) {
    console.error('[Optional Auth Middleware] Error:', error);
    // Continue without accountId on error
  }
}
