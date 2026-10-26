/**
 * Database Configuration
 * 
 * Reads environment variables and provides database configuration.
 * 
 * Architecture Decision:
 * - For database connectivity, we use PostgreSQL connection strings for both Supabase and self-hosted
 * - This makes migration from Supabase to self-hosted PostgreSQL straightforward (just change connection string)
 * - Supabase-specific features (Auth, Storage) are handled at the application layer, not the database layer
 * - This aligns with the requirement to preserve a practical path to future self-hosted infrastructure
 */

export interface DatabaseConfig {
  readonly provider: 'supabase' | 'postgresql';
  readonly connectionString: string;
  readonly poolSize: number;
}

export function readDatabaseConfig(env: NodeJS.ProcessEnv = process.env): DatabaseConfig {
  const provider = (env.DATABASE_PROVIDER || 'postgresql') as 'supabase' | 'postgresql';

  // Use the DATABASE_URL (PostgreSQL connection string)
  // This works for both Supabase and self-hosted PostgreSQL (including Neon)
  const connectionString = env.DATABASE_URL;

  if (!connectionString) {
    throw new Error(
      `DATABASE_URL is required for provider '${provider}'. ` +
      `For Neon, get it from the Neon dashboard. ` +
      `For Supabase, get it from the Supabase dashboard (Settings > Database). ` +
      `For self-hosted, provide your PostgreSQL connection string.`
    );
  }

  return {
    provider,
    connectionString,
    poolSize: parseInt(env.DATABASE_POOL_SIZE || '20', 10),
  };
}

export function isDatabaseConfigured(config: DatabaseConfig): boolean {
  return !!config.connectionString;
}
