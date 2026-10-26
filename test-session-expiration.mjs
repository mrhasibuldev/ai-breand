import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename));
dotenv.config({ path: path.join(projectRoot, '.env') });

import { readDatabaseConfig, createDatabaseClient } from './packages/database-core/dist/index.js';

const config = readDatabaseConfig();
const db = createDatabaseClient(config);
await db.connect();

// Update the most recent session to be revoked
console.log('Setting recent session to revoked...');
const result = await db.query(
  `UPDATE nexus.auth_sessions
   SET revoked_at = NOW()
   WHERE id = (SELECT id FROM nexus.auth_sessions ORDER BY created_at DESC LIMIT 1)
   RETURNING id, account_id, revoked_at`
);

if (result.rows.length > 0) {
  console.log('Session updated to revoked:');
  console.log('  ID:', result.rows[0].id);
  console.log('  Account ID:', result.rows[0].account_id);
  console.log('  Revoked at:', result.rows[0].revoked_at);
} else {
  console.log('No sessions found');
}

await db.close();
