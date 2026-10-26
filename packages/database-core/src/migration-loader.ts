/**
 * Migration Loader
 * 
 * Loads migration SQL files from the migrations directory
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const migrationsDir = join(__dirname, '..', 'migrations');

export interface Migration {
  readonly id: string;
  readonly name: string;
  readonly up: string;
}

export function loadMigrations(): readonly Migration[] {
  const files = readdirSync(migrationsDir)
    .filter(f => f.endsWith('.sql'))
    .filter(f => {
      // Exclude non-incremental migration files
      // COMPLETE_SCHEMA.sql and RLS_POLICIES.sql are for reference only
      // Only load numbered incremental migrations (001-999)
      return !f.startsWith('COMPLETE') && !f.startsWith('RLS');
    })
    .sort(); // Sort by filename for consistent order

  return files.map(file => {
    const id = file.replace('.sql', '');
    const sql = readFileSync(join(migrationsDir, file), 'utf-8');
    return {
      id,
      name: id,
      up: sql,
    };
  });
}
