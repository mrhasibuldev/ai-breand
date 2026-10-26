import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load .env from project root
const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename), '..', '..', '..');
dotenv.config({ path: path.join(projectRoot, '.env') });

import { buildApp } from './app.js';
import { readRuntimeConfig } from '@nexusai/config';

const config = readRuntimeConfig(process.env);

const app = await buildApp();

await app.listen({ port: config.apiPort, host: config.apiHost });

const shutdown = async (signal: string) => {
  await app.close();
  process.exit(0);
};

process.once('SIGINT', () => void shutdown('SIGINT'));
process.once('SIGTERM', () => void shutdown('SIGTERM'));
