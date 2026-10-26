/**
 * Database Migration Script
 * 
 * This script runs database migrations against the configured database.
 * Usage: node run-migrations.js
 */

import { readDatabaseConfig, createDatabaseClient, MigrationRunner, loadMigrations } from './dist/index.js';

async function main() {
  console.log('[Migration Script] Starting database migration...');

  try {
    // Read configuration
    const config = readDatabaseConfig();
    console.log('[Migration Script] Database provider:', config.provider);
    console.log('[Migration Script] Database configured:', !!config.connectionString);

    // Create client
    const client = createDatabaseClient(config);
    await client.connect();
    console.log('[Migration Script] Connected to database');

    // Health check
    const health = await client.healthCheck();
    console.log('[Migration Script] Database health:', health);

    if (!health.ready) {
      throw new Error('Database is not ready');
    }

    // Load migrations
    const migrations = loadMigrations();
    console.log(`[Migration Script] Loaded ${migrations.length} migrations`);

    // Run migrations
    const runner = new MigrationRunner(migrations, client);
    await runner.applyPending();

    // Close connection
    await client.close();
    console.log('[Migration Script] Migration completed successfully');
  } catch (error) {
    console.error('[Migration Script] Migration failed:', error);
    process.exit(1);
  }
}

main();
