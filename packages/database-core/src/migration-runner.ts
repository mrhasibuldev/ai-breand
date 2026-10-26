/**
 * Migration Runner
 * 
 * Executes SQL migrations in version order.
 * Migrations are idempotent and versioned.
 */

import type { DatabaseClient, QueryResult, IMigrationRunner } from './index.js';

export interface Migration {
  readonly id: string;
  readonly name: string;
  readonly up: string;
  readonly down?: string;
}

export interface MigrationRecord {
  readonly id: string;
  readonly applied_at: string;
}

export class MigrationRunner implements IMigrationRunner {
  private readonly migrations: readonly Migration[];
  private readonly client: DatabaseClient;

  constructor(migrations: readonly Migration[], client: DatabaseClient) {
    this.migrations = migrations;
    this.client = client;
  }

  /**
   * Get migration status - which migrations have been applied
   */
  async status(): Promise<readonly { readonly id: string; readonly applied: boolean }[]> {
    // Ensure migrations table exists
    await this.ensureMigrationsTable();

    // Get applied migrations
    const result = await this.client.query<MigrationRecord>(
      'SELECT id FROM nexus.schema_migrations ORDER BY id'
    );

    const appliedIds = new Set(result.rows.map(r => r.id));

    return this.migrations.map(m => ({
      id: m.id,
      applied: appliedIds.has(m.id),
    }));
  }

  /**
   * Apply all pending migrations
   */
  async applyPending(): Promise<void> {
    const currentStatus = await this.status();
    const pending = this.migrations.filter(m => {
      const status = currentStatus.find(s => s.id === m.id);
      return !status?.applied;
    });

    if (pending.length === 0) {
      console.log('[MigrationRunner] No pending migrations');
      return;
    }

    console.log(`[MigrationRunner] Applying ${pending.length} pending migrations`);

    for (const migration of pending) {
      await this.applyMigration(migration);
    }

    console.log('[MigrationRunner] All migrations applied successfully');
  }

  /**
   * Apply a single migration within a transaction
   */
  private async applyMigration(migration: Migration): Promise<void> {
    console.log(`[MigrationRunner] Applying migration: ${migration.id} - ${migration.name}`);

    await this.client.transaction(async (session) => {
      // Execute migration SQL
      await session.query(migration.up);

      // Record migration
      await session.query(
        'INSERT INTO nexus.schema_migrations (id, applied_at) VALUES ($1, NOW())',
        [migration.id]
      );
    });

    console.log(`[MigrationRunner] Migration applied: ${migration.id}`);
  }

  /**
   * Ensure the migrations tracking table exists
   */
  private async ensureMigrationsTable(): Promise<void> {
    try {
      await this.client.query(`
        CREATE SCHEMA IF NOT EXISTS nexus;
        
        CREATE TABLE IF NOT EXISTS nexus.schema_migrations (
          id TEXT PRIMARY KEY,
          applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
      `);
    } catch (error) {
      console.error('[MigrationRunner] Failed to ensure migrations table:', error);
      throw error;
    }
  }
}
