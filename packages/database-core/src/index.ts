import { PostgresClient } from './postgres-client.js';
import { readDatabaseConfig, isDatabaseConfigured, type DatabaseConfig } from './config.js';

export type QueryValues = readonly unknown[];

export type QueryResult<Row> = {
  readonly rows: readonly Row[];
  readonly rowCount: number;
};

export interface DatabaseSession {
  query<Row>(statement: string, values?: QueryValues): Promise<QueryResult<Row>>;
}

export interface TransactionManager extends DatabaseSession {
  transaction<Result>(work: (session: DatabaseSession) => Promise<Result>): Promise<Result>;
}

export interface DatabaseClient extends TransactionManager {
  connect(): Promise<void>;
  healthCheck(): Promise<{ readonly ready: boolean; readonly error?: string }>;
  close(): Promise<void>;
}

export interface Repository<Entity, Id> {
  findOwnedById(accountId: string, id: Id): Promise<Entity | null>;
}

export interface IMigrationRunner {
  status(): Promise<readonly { readonly id: string; readonly applied: boolean }[]>;
  applyPending(): Promise<void>;
}

export class UnconfiguredDatabaseClient implements DatabaseClient {
  async connect(): Promise<void> {
    throw new Error('Database adapter is not configured');
  }

  async query<Row>(): Promise<QueryResult<Row>> {
    throw new Error('Database adapter is not configured');
  }

  async transaction<Result>(): Promise<Result> {
    throw new Error('Database adapter is not configured');
  }

  async healthCheck(): Promise<{ readonly ready: boolean; readonly error?: string }> {
    return { ready: false, error: 'Database adapter is not configured' };
  }

  async close(): Promise<void> {}
}

/**
 * Create a database client based on configuration
 * 
 * This factory abstracts the provider, allowing easy switching between
 * Supabase and self-hosted PostgreSQL without changing application code.
 */
export function createDatabaseClient(config: DatabaseConfig): DatabaseClient {
  // Both Supabase and self-hosted PostgreSQL use the same PostgreSQL client
  // The only difference is the connection string source
  return new PostgresClient(config);
}

// Re-export for convenience
export { PostgresClient } from './postgres-client.js';
export { readDatabaseConfig, isDatabaseConfigured } from './config.js';
export { MigrationRunner } from './migration-runner.js';
export { loadMigrations } from './migration-loader.js';
