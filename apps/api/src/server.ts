import { buildApp } from './app.js';
import { readRuntimeConfig } from '@nexusai/config';

const config = readRuntimeConfig(process.env);
const app = buildApp();

await app.listen({ port: config.apiPort, host: config.apiHost });

const shutdown = async (signal: string) => {
  app.log.info({ signal }, 'Shutting down API');
  await app.close();
  process.exit(0);
};

process.once('SIGINT', () => void shutdown('SIGINT'));
process.once('SIGTERM', () => void shutdown('SIGTERM'));
