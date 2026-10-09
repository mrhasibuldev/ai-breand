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
  healthCheck(): Promise<{ readonly ready: boolean }>;
  close(): Promise<void>;
}

export interface Repository<Entity, Id> {
  findOwnedById(accountId: string, id: Id): Promise<Entity | null>;
}

export interface MigrationRunner {
  status(): Promise<readonly { readonly id: string; readonly applied: boolean }[]>;
  applyPending(): Promise<void>;
}

export class UnconfiguredDatabaseClient implements DatabaseClient {
  async query<Row>(): Promise<QueryResult<Row>> {
    throw new Error('Database adapter is not configured');
  }

  async transaction<Result>(): Promise<Result> {
    throw new Error('Database adapter is not configured');
  }

  async healthCheck(): Promise<{ readonly ready: boolean }> {
    return { ready: false };
  }

  async close(): Promise<void> {}
}

export { PostgresClient } from './postgres-client.js';
