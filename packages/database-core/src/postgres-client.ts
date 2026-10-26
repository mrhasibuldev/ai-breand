import pg from 'pg';
import type {
  DatabaseClient,
  DatabaseSession,
  QueryResult,
  QueryValues,
  TransactionManager,
} from './index.js';
import type { DatabaseConfig } from './config.js';

const { Pool } = pg;

export class PostgresClient implements DatabaseClient, TransactionManager {
  private pool: pg.Pool | null = null;
  private readonly config: DatabaseConfig;

  constructor(config: DatabaseConfig) {
    this.config = config;
  }

  async connect(): Promise<void> {
    if (this.pool) return;
    this.pool = new Pool({
      connectionString: this.config.connectionString,
      max: this.config.poolSize,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 10000, // Increased from 2000ms to 10000ms for Neon
    });
  }

  async query<Row>(statement: string, values?: QueryValues): Promise<QueryResult<Row>> {
    if (!this.pool) throw new Error('Database not connected');
    const result = await this.pool.query(statement, values as unknown[]);
    return {
      rows: result.rows as Row[],
      rowCount: result.rowCount ?? 0,
    };
  }

  async transaction<Result>(work: (session: DatabaseSession) => Promise<Result>): Promise<Result> {
    if (!this.pool) throw new Error('Database not connected');
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const session: DatabaseSession = {
        query: async <Row>(statement: string, values?: QueryValues) => {
          const result = await client.query(statement, values as unknown[]);
          return {
            rows: result.rows as Row[],
            rowCount: result.rowCount ?? 0,
          };
        },
      } as DatabaseSession;
      const result = await work(session);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async healthCheck(): Promise<{ readonly ready: boolean; readonly error?: string }> {
    if (!this.pool) return { ready: false, error: 'Pool not initialized' };
    try {
      await this.pool.query('SELECT 1');
      return { ready: true };
    } catch (error) {
      return { ready: false, error: error instanceof Error ? error.message : String(error) };
    }
  }

  async close(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
    }
  }
}
