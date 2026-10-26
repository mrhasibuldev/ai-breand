/**
 * Conversation Repository
 * 
 * Handles conversation persistence with ownership validation
 */

import type { DatabaseClient } from '@nexusai/database-core';

export interface Conversation {
  readonly id: string;
  readonly accountId: string;
  readonly status: 'active' | 'ended' | 'deleted';
  readonly title?: string;
  readonly startedAt: string;
  readonly endedAt?: string;
  readonly deletedAt?: string;
}

export interface CreateConversationInput {
  readonly accountId: string;
  readonly title?: string;
}

export class ConversationRepository {
  constructor(private readonly db: DatabaseClient) {}

  /**
   * Find conversation by ID with ownership check
   */
  async findById(accountId: string, id: string): Promise<Conversation | null> {
    const result = await this.db.query<Conversation>(
      `SELECT id, account_id, status, title, started_at, ended_at, deleted_at
       FROM nexus.conversations
       WHERE id = $1 AND account_id = $2 AND deleted_at IS NULL`,
      [id, accountId]
    );

    return result.rows[0] || null;
  }

  /**
   * List all conversations for an account
   */
  async listByAccountId(accountId: string): Promise<readonly Conversation[]> {
    const result = await this.db.query<Conversation>(
      `SELECT id, account_id, status, title, started_at, ended_at, deleted_at
       FROM nexus.conversations
       WHERE account_id = $1 AND deleted_at IS NULL
       ORDER BY started_at DESC`,
      [accountId]
    );

    return result.rows;
  }

  /**
   * Create a new conversation
   */
  async create(input: CreateConversationInput): Promise<Conversation> {
    const result = await this.db.query<Conversation>(
      `INSERT INTO nexus.conversations (account_id, title, status)
       VALUES ($1, $2, 'active')
       RETURNING id, account_id, status, title, started_at, ended_at, deleted_at`,
      [input.accountId, input.title || null]
    );

    return result.rows[0];
  }

  /**
   * Update conversation title
   */
  async updateTitle(accountId: string, id: string, title: string): Promise<Conversation | null> {
    const result = await this.db.query<Conversation>(
      `UPDATE nexus.conversations
       SET title = $1
       WHERE id = $2 AND account_id = $3 AND deleted_at IS NULL
       RETURNING id, account_id, status, title, started_at, ended_at, deleted_at`,
      [title, id, accountId]
    );

    return result.rows[0] || null;
  }

  /**
   * End a conversation
   */
  async end(accountId: string, id: string): Promise<boolean> {
    const result = await this.db.query(
      `UPDATE nexus.conversations
       SET status = 'ended', ended_at = NOW()
       WHERE id = $1 AND account_id = $2 AND status = 'active'`,
      [id, accountId]
    );

    return result.rowCount > 0;
  }

  /**
   * Soft delete a conversation
   */
  async delete(accountId: string, id: string): Promise<boolean> {
    const result = await this.db.query(
      `UPDATE nexus.conversations
       SET deleted_at = NOW()
       WHERE id = $1 AND account_id = $2 AND deleted_at IS NULL`,
      [id, accountId]
    );

    return result.rowCount > 0;
  }
}
