/**
 * Profile Repository
 * 
 * Handles profile persistence with ownership validation
 */

import type { DatabaseClient } from '@nexusai/database-core';

export interface UserProfile {
  readonly id: string;
  readonly accountId: string;
  readonly displayName?: string;
  readonly ageBand?: string;
  readonly locale?: string;
  readonly timezone?: string;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly deletedAt?: string;
}

export interface CreateProfileInput {
  readonly accountId: string;
  readonly displayName?: string;
  readonly ageBand?: string;
  readonly locale?: string;
  readonly timezone?: string;
}

export interface UpdateProfileInput {
  readonly displayName?: string;
  readonly ageBand?: string;
  readonly locale?: string;
  readonly timezone?: string;
}

export class ProfileRepository {
  constructor(private readonly db: DatabaseClient) {}

  /**
   * Find profile by account ID
   */
  async findByAccountId(accountId: string): Promise<UserProfile | null> {
    const result = await this.db.query<UserProfile>(
      `SELECT id, account_id, display_name, age_band, locale, timezone, 
              created_at, updated_at, deleted_at
       FROM nexus.user_profiles 
       WHERE account_id = $1 AND deleted_at IS NULL`,
      [accountId]
    );

    return result.rows[0] || null;
  }

  /**
   * Create a new profile
   */
  async create(input: CreateProfileInput): Promise<UserProfile> {
    const result = await this.db.query<UserProfile>(
      `INSERT INTO nexus.user_profiles (account_id, display_name, age_band, locale, timezone)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING id, account_id, display_name, age_band, locale, timezone, 
                 created_at, updated_at, deleted_at`,
      [
        input.accountId,
        input.displayName || null,
        input.ageBand || null,
        input.locale || null,
        input.timezone || null,
      ]
    );

    return result.rows[0];
  }

  /**
   * Update profile (requires ownership)
   */
  async update(accountId: string, input: UpdateProfileInput): Promise<UserProfile | null> {
    // Build dynamic update query
    const updates: string[] = [];
    const values: unknown[] = [];
    let paramIndex = 1;

    if (input.displayName !== undefined) {
      updates.push(`display_name = $${paramIndex++}`);
      values.push(input.displayName);
    }
    if (input.ageBand !== undefined) {
      updates.push(`age_band = $${paramIndex++}`);
      values.push(input.ageBand);
    }
    if (input.locale !== undefined) {
      updates.push(`locale = $${paramIndex++}`);
      values.push(input.locale);
    }
    if (input.timezone !== undefined) {
      updates.push(`timezone = $${paramIndex++}`);
      values.push(input.timezone);
    }

    if (updates.length === 0) {
      return this.findByAccountId(accountId);
    }

    values.push(accountId);

    const result = await this.db.query<UserProfile>(
      `UPDATE nexus.user_profiles
       SET ${updates.join(', ')}
       WHERE account_id = $${paramIndex} AND deleted_at IS NULL
       RETURNING id, account_id, display_name, age_band, locale, timezone, 
                 created_at, updated_at, deleted_at`,
      values
    );

    return result.rows[0] || null;
  }

  /**
   * Soft delete profile
   */
  async delete(accountId: string): Promise<boolean> {
    const result = await this.db.query(
      `UPDATE nexus.user_profiles
       SET deleted_at = NOW()
       WHERE account_id = $1 AND deleted_at IS NULL`,
      [accountId]
    );

    return result.rowCount > 0;
  }
}
