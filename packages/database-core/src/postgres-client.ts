import pg from 'pg';
import type {
  DatabaseClient,
  DatabaseSession,
  QueryResult,
  QueryValues,
  TransactionManager,
} from './index.js';

const { Pool } = pg;

export class PostgresClient implements DatabaseClient, TransactionManager {
  private pool: pg.Pool | null = null;
  private readonly connectionString: string;

  constructor(connectionString: string) {
    this.connectionString = connectionString;
  }

  async connect(): Promise<void> {
    if (this.pool) return;
    this.pool = new Pool({
      connectionString: this.connectionString,
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
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

  async healthCheck(): Promise<{ readonly ready: boolean }> {
    if (!this.pool) return { ready: false };
    try {
      await this.pool.query('SELECT 1');
      return { ready: true };
    } catch {
      return { ready: false };
    }
  }

  async close(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
    }
  }
}
