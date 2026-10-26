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

// Get the most recent session
const result = await db.query('SELECT session_token_hash FROM nexus.auth_sessions ORDER BY created_at DESC LIMIT 1');
console.log('Session token hash from DB:', result.rows[0]?.session_token_hash);

// Check if a plain token matches
const testToken = 'd47e5238-038d-4110-98a0-25cb7137d7df';
const matches = await bcrypt.compare(testToken, result.rows[0]?.session_token_hash);
console.log('Test token:', testToken);
console.log('Match:', matches);

await db.close();
