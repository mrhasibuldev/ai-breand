export type RuntimeConfig = {
  readonly nodeEnv: string;
  readonly apiPort: number;
  readonly apiHost: string;
  readonly webOrigin?: string;
  readonly databaseUrl?: string;
  readonly ready: boolean;
};

export function readRuntimeConfig(env: NodeJS.ProcessEnv = process.env): RuntimeConfig {
  const apiPort = Number(env.API_PORT ?? 4000);
  const nodeEnv = env.NODE_ENV ?? 'development';
  const errors: string[] = [];
  if (!['development', 'test', 'production'].includes(nodeEnv)) errors.push('NODE_ENV');
  if (!Number.isInteger(apiPort) || apiPort <= 0 || apiPort > 65535) errors.push('API_PORT');
  if (nodeEnv === 'production' && !env.DATABASE_URL) errors.push('DATABASE_URL');
  if (errors.length) throw new Error(`Invalid runtime configuration: ${errors.join(', ')}`);
  return {
    nodeEnv,
    apiPort,
    apiHost: env.API_HOST ?? '127.0.0.1',
    ...(env.WEB_ORIGIN ? { webOrigin: env.WEB_ORIGIN } : {}),
    ...(env.DATABASE_URL ? { databaseUrl: env.DATABASE_URL } : {}),
    // A configured URL is not proof that a production persistence dependency is usable.
    // Readiness stays closed until a real production storage adapter exists.
    ready: nodeEnv !== 'production',
  };
}
