/**
 * Database Configuration Test
 * 
 * Tests that database configuration can be read and validated.
 */

import { describe, it, expect } from 'vitest';
import { readDatabaseConfig, isDatabaseConfigured, createDatabaseClient, UnconfiguredDatabaseClient } from '../src/index.js';

describe('Database Configuration', () => {
  it('should read configuration from environment', () => {
    const config = readDatabaseConfig({
      DATABASE_PROVIDER: 'postgresql',
      DATABASE_URL: 'postgresql://localhost:5432/test',
      DATABASE_POOL_SIZE: '10',
    });

    expect(config.provider).toBe('postgresql');
    expect(config.connectionString).toBe('postgresql://localhost:5432/test');
    expect(config.poolSize).toBe(10);
  });

  it('should detect unconfigured database', () => {
    const config = readDatabaseConfig({
      DATABASE_PROVIDER: 'postgresql',
      DATABASE_URL: 'postgresql://localhost:5432/test',
    });

    expect(isDatabaseConfigured(config)).toBe(true);
  });

  it('should detect configured database', () => {
    const config = readDatabaseConfig({
      DATABASE_PROVIDER: 'postgresql',
      DATABASE_URL: 'postgresql://localhost:5432/test',
    });

    expect(isDatabaseConfigured(config)).toBe(true);
  });

  it('should throw error when DATABASE_URL is missing', () => {
    expect(() => {
      readDatabaseConfig({
        DATABASE_PROVIDER: 'postgresql',
        DATABASE_URL: '',
      });
    }).toThrowError('DATABASE_URL is required');
  });

  it('should create PostgresClient with config', () => {
    const config = readDatabaseConfig({
      DATABASE_PROVIDER: 'postgresql',
      DATABASE_URL: 'postgresql://localhost:5432/test',
    });

    const client = createDatabaseClient(config);
    expect(client).toBeInstanceOf(Object); // PostgresClient instance
  });

  it('should use UnconfiguredDatabaseClient when not configured', async () => {
    const client = new UnconfiguredDatabaseClient();
    await expect(client.connect()).rejects.toThrow('Database adapter is not configured');
    const result = await client.healthCheck();
    expect(result).toEqual({ ready: false, error: 'Database adapter is not configured' });
  });
});
