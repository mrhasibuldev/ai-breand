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
const result = await db.query('SELECT id, account_id, created_at, expires_at FROM nexus.auth_sessions ORDER BY created_at DESC LIMIT 5');
console.log('Recent sessions:', result.rows);
await db.close();
