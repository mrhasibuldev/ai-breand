/**
 * Memory Repository
 * 
 * Handles memory persistence with ownership validation
 */

import type { DatabaseClient } from '@nexusai/database-core';

export interface MemoryRecord {
  readonly id: string;
  readonly accountId: string;
  readonly consentRecordId?: string;
  readonly sourceMessageId?: string;
  readonly category: string;
  readonly purpose: string;
  readonly value: string;
  readonly status: 'candidate' | 'approved' | 'rejected' | 'revoked' | 'deleted';
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly deletedAt?: string;
}

export interface CreateMemoryInput {
  readonly accountId: string;
  readonly consentRecordId?: string;
  readonly sourceMessageId?: string;
  readonly category: string;
  readonly purpose: string;
  readonly value: string;
}

export class MemoryRepository {
  constructor(private readonly db: DatabaseClient) {}

  /**
   * Find memory by ID with ownership check
   */
  async find(accountId: string, id: string): Promise<MemoryRecord | null> {
    const result = await this.db.query<MemoryRecord>(
      `SELECT id, account_id, consent_record_id, source_message_id, 
              category, purpose, value, status, created_at, updated_at, deleted_at
       FROM nexus.memory_records
       WHERE id = $1 AND account_id = $2 AND deleted_at IS NULL`,
      [id, accountId]
    );

    return result.rows[0] || null;
  }

  /**
   * List approved memories for an account and purpose
   */
  async listApproved(accountId: string, purpose?: string): Promise<readonly MemoryRecord[]> {
    let query = `
      SELECT id, account_id, consent_record_id, source_message_id, 
             category, purpose, value, status, created_at, updated_at, deleted_at
      FROM nexus.memory_records
      WHERE account_id = $1 AND status = 'approved' AND deleted_at IS NULL
    `;
    const params: unknown[] = [accountId];

    if (purpose) {
      query += ` AND purpose = $2`;
      params.push(purpose);
    }

    query += ` ORDER BY created_at DESC`;

    const result = await this.db.query<MemoryRecord>(query, params);
    return result.rows;
  }

  /**
   * Save a memory record
   */
  async save(record: MemoryRecord): Promise<void> {
    await this.db.query(
      `INSERT INTO nexus.memory_records 
       (id, account_id, consent_record_id, source_message_id, category, purpose, value, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       ON CONFLICT (id) DO UPDATE SET
         purpose = EXCLUDED.purpose,
         value = EXCLUDED.value,
         status = EXCLUDED.status,
         updated_at = NOW()`,
      [
        record.id,
        record.accountId,
        record.consentRecordId || null,
        record.sourceMessageId || null,
        record.category,
        record.purpose,
        record.value,
        record.status,
      ]
    );
  }

  /**
   * Change memory status
   */
  async changeStatus(accountId: string, id: string, status: MemoryRecord['status']): Promise<boolean> {
    const result = await this.db.query(
      `UPDATE nexus.memory_records
       SET status = $1, updated_at = NOW()
       WHERE id = $2 AND account_id = $3 AND deleted_at IS NULL`,
      [status, id, accountId]
    );

    return result.rowCount > 0;
  }

  /**
   * Clear all memories for an account
   */
  async clear(accountId: string): Promise<void> {
    await this.db.query(
      `UPDATE nexus.memory_records
       SET deleted_at = NOW()
       WHERE account_id = $1 AND deleted_at IS NULL`,
      [accountId]
    );
  }
}
