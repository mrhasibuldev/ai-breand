import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import bcrypt from 'bcrypt';

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename));
dotenv.config({ path: path.join(projectRoot, '.env') });

import { readDatabaseConfig, createDatabaseClient } from './packages/database-core/dist/index.js';

const config = readDatabaseConfig();
const db = createDatabaseClient(config);
await db.connect();

const testToken = 'd47e5238-038d-4110-98a0-25cb7137d7df';
const sessionTokenHash = await bcrypt.hash(testToken, 12);
console.log('Generated hash:', sessionTokenHash);

// Try the exact query from the auth route
const sessionResult = await db.query(
  `SELECT s.account_id, s.expires_at, s.revoked_at, a.email_normalized, a.status
   FROM nexus.auth_sessions s
   JOIN nexus.accounts a ON s.account_id = a.id
   WHERE s.session_token_hash = $1
     AND s.revoked_at IS NULL
     AND s.expires_at > NOW()`,
  [sessionTokenHash]
);
console.log('Query result rows:', sessionResult.rows.length);

// Now try with the actual hash from DB
const actualHash = await db.query('SELECT session_token_hash FROM nexus.auth_sessions ORDER BY created_at DESC LIMIT 1');
const actualHashValue = actualHash.rows[0].session_token_hash;
console.log('Actual hash from DB:', actualHashValue);

const sessionResult2 = await db.query(
  `SELECT s.account_id, s.expires_at, s.revoked_at, a.email_normalized, a.status
   FROM nexus.auth_sessions s
   JOIN nexus.accounts a ON s.account_id = a.id
   WHERE s.session_token_hash = $1
     AND s.revoked_at IS NULL
     AND s.expires_at > NOW()`,
  [actualHashValue]
);
console.log('Query with actual hash rows:', sessionResult2.rows.length);
console.log('Result:', sessionResult2.rows[0]);

await db.close();
