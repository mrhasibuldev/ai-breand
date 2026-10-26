/**
 * Authentication Routes
 *
 * Handles signup, login, and logout using Neon PostgreSQL
 * Uses bcrypt for password hashing and HTTP-only cookies for sessions
 */

import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';
import { hashPassword, verifyPassword, generateSessionToken, hashSessionToken, verifySessionToken } from '../auth-utils.js';

interface SignupBody {
  email: string;
  password: string;
}

interface LoginBody {
  email: string;
  password: string;
}

export async function authRoutes(app: FastifyInstance) {
  const config = readDatabaseConfig();
  const db = createDatabaseClient(config);
  await db.connect();

  /**
   * POST /api/v1/auth/register
   * Create a new account with email and password
   */
  app.post('/api/v1/auth/register', async (request: FastifyRequest, reply: FastifyReply) => {
    const body = request.body as SignupBody;
    const { email, password } = body;

    // Validate input
    if (!email || !password) {
      return reply.status(400).send({ error: 'Email and password are required' });
    }

    if (password.length < 8) {
      return reply.status(400).send({ error: 'Password must be at least 8 characters' });
    }

    try {
      // Check if email already exists
      const existingAccounts = await db.query(
        `SELECT id FROM nexus.accounts WHERE email_normalized = $1 AND deleted_at IS NULL`,
        [email.toLowerCase()]
      );

      if (existingAccounts.rows.length > 0) {
        return reply.status(409).send({ error: 'Email already registered' });
      }

      // Hash password
      const passwordHash = await hashPassword(password);

      // Create account
      const accountResult = await db.query(
        `INSERT INTO nexus.accounts (auth_issuer, auth_subject, email_normalized, password_hash)
         VALUES ($1, $2, $3, $4)
         RETURNING id, email_normalized`,
        ['self-managed', email, email.toLowerCase(), passwordHash]
      );

      const account = accountResult.rows[0] as { id: string; email_normalized: string };

      // Create session
      const sessionToken = generateSessionToken();
      const sessionTokenHash = await hashSessionToken(sessionToken);
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

      await db.query(
        `INSERT INTO nexus.auth_sessions (account_id, session_token_hash, expires_at)
         VALUES ($1, $2, $3)`,
        [account.id, sessionTokenHash, expiresAt]
      );

      // Set HTTP-only cookie
      reply.setCookie('nexus_session', sessionToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
        maxAge: 7 * 24 * 60 * 60, // 7 days in seconds
      });

      return reply.status(201).send({
        account_id: account.id,
        email: account.email_normalized,
        authenticated: true,
      });
    } catch (error) {
      console.error('[Auth] Registration error:', error);
      return reply.status(500).send({ error: 'Registration failed' });
    }
  });

  /**
   * POST /api/v1/auth/login
   * Authenticate with email and password
   */
  app.post('/api/v1/auth/login', async (request: FastifyRequest, reply: FastifyReply) => {
    const body = request.body as LoginBody;
    const { email, password } = body;

    // Validate input
    if (!email || !password) {
      return reply.status(400).send({ error: 'Email and password are required' });
    }

    try {
      // Find account by email
      const accountResult = await db.query(
        `SELECT id, email_normalized, password_hash, status
         FROM nexus.accounts
         WHERE email_normalized = $1 AND deleted_at IS NULL`,
        [email.toLowerCase()]
      );

      if (accountResult.rows.length === 0) {
        return reply.status(401).send({ error: 'Invalid email or password' });
      }

      const account = accountResult.rows[0] as { id: string; email_normalized: string; password_hash: string | null; status: string };

      // Check account status
      if (account.status !== 'active') {
        return reply.status(403).send({ error: 'Account is not active' });
      }

      // Verify password
      if (!account.password_hash) {
        return reply.status(401).send({ error: 'Account uses Supabase Auth, not self-managed auth' });
      }

      const passwordValid = await verifyPassword(password, account.password_hash);
      if (!passwordValid) {
        return reply.status(401).send({ error: 'Invalid email or password' });
      }

      // Create session
      const sessionToken = generateSessionToken();
      const sessionTokenHash = await hashSessionToken(sessionToken);
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

      await db.query(
        `INSERT INTO nexus.auth_sessions (account_id, session_token_hash, expires_at)
         VALUES ($1, $2, $3)`,
        [account.id, sessionTokenHash, expiresAt]
      );

      // Set HTTP-only cookie
      reply.setCookie('nexus_session', sessionToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
        maxAge: 7 * 24 * 60 * 60, // 7 days in seconds
      });

      return reply.send({
        account_id: account.id,
        email: account.email_normalized,
        authenticated: true,
      });
    } catch (error) {
      console.error('[Auth] Login error:', error);
      return reply.status(500).send({ error: 'Login failed' });
    }
  });

  /**
   * POST /api/v1/auth/logout
   * Invalidate the current session
   */
  app.post('/api/v1/auth/logout', async (request: FastifyRequest, reply: FastifyReply) => {
    const sessionToken = request.cookies.nexus_session;

    if (!sessionToken) {
      return reply.send({ logged_out: true });
    }

    try {
      // Find the session by comparing token against all hashes
      const sessionsResult = await db.query(
        `SELECT s.id, s.session_token_hash
         FROM nexus.auth_sessions s
         WHERE s.revoked_at IS NULL
         AND s.expires_at > NOW()
         ORDER BY s.created_at DESC
         LIMIT 100`
      );

      let sessionId = null;
      for (const session of sessionsResult.rows) {
        const sessionRow = session as { id: string; session_token_hash: string };
        const isValid = await verifySessionToken(sessionToken, sessionRow.session_token_hash);
        if (isValid) {
          sessionId = sessionRow.id;
          break;
        }
      }

      if (sessionId) {
        // Mark session as revoked
        await db.query(
          `UPDATE nexus.auth_sessions
           SET revoked_at = NOW()
           WHERE id = $1`,
          [sessionId]
        );
      }

      // Clear cookie
      reply.clearCookie('nexus_session', {
        path: '/',
      });

      return reply.send({ logged_out: true });
    } catch (error) {
      console.error('[Auth] Logout error:', error);
      // Still clear cookie even if database error
      reply.clearCookie('nexus_session', { path: '/' });
      return reply.send({ logged_out: true });
    }
  });

  /**
   * GET /api/v1/auth/session
   * Validate current session
   */
  app.get('/api/v1/auth/session', async (request: FastifyRequest, reply: FastifyReply) => {
    const sessionToken = request.cookies.nexus_session;

    console.log('[Auth] Session validation - token present:', !!sessionToken);

    if (!sessionToken) {
      return reply.status(401).send({ authenticated: false });
    }

    try {
      // Get all active sessions for this account and check the token against each hash
      // This is less efficient but necessary because bcrypt requires rehashing to compare
      const sessionsResult = await db.query(
        `SELECT s.id, s.account_id, s.session_token_hash, s.expires_at, s.revoked_at, a.email_normalized, a.status
         FROM nexus.auth_sessions s
         JOIN nexus.accounts a ON s.account_id = a.id
         WHERE s.revoked_at IS NULL
         AND s.expires_at > NOW()
         ORDER BY s.created_at DESC
         LIMIT 100`
      );

      let matchedSession = null;
      for (const session of sessionsResult.rows) {
        const sessionRow = session as {
          id: string;
          account_id: string;
          session_token_hash: string;
          expires_at: Date;
          revoked_at: Date | null;
          email_normalized: string;
          status: string;
        };
        const isValid = await verifySessionToken(sessionToken, sessionRow.session_token_hash);
        if (isValid) {
          matchedSession = sessionRow;
          break;
        }
      }

      console.log('[Auth] Session validation - matched session:', !!matchedSession);

      if (!matchedSession) {
        return reply.status(401).send({ authenticated: false });
      }

      const session = matchedSession as {
        account_id: string;
        email_normalized: string;
        status: string;
        id: string;
      };

      // Check account status
      if (session.status !== 'active') {
        return reply.status(403).send({ authenticated: false, reason: 'Account not active' });
      }

      // Update last_seen_at
      await db.query(
        `UPDATE nexus.auth_sessions
         SET last_seen_at = NOW()
         WHERE id = $1`,
        [session.id]
      );

      return reply.send({
        authenticated: true,
        account_id: session.account_id,
        email: session.email_normalized,
      });
    } catch (error) {
      console.error('[Auth] Session validation error:', error);
      return reply.status(500).send({ error: 'Session validation failed' });
    }
  });
}
