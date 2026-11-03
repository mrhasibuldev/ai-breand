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

console.log('[API] Config loaded:', { apiHost: config.apiHost, apiPort: config.apiPort });

let app: any;

const shutdown = async (signal: string) => {
  console.log(`[API] Received ${signal}, shutting down...`);
  if (app) {
    await app.close();
  }
  process.exit(0);
};

process.once('SIGINT', () => void shutdown('SIGINT'));
process.once('SIGTERM', () => void shutdown('SIGTERM'));

(async () => {
  try {
    console.log('[API] Building application...');
    app = await buildApp();
    console.log('[API] Application built, starting server...');
    const address = await app.listen({ port: config.apiPort, host: config.apiHost });
    console.log(`[API] Server listening on ${address}`);
    console.log('[API] Press Ctrl+C to stop');
  } catch (error) {
    console.error('[API] Failed to start server:', error);
    if (error instanceof Error) {
      console.error('[API] Error details:', error.stack);
    }
    process.exit(1);
  }
})();

