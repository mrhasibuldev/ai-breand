/**
 * Message Repository
 * 
 * Handles message persistence with ownership validation
 */

import type { DatabaseClient } from '@nexusai/database-core';

export interface Message {
  readonly id: string;
  readonly conversationId: string;
  readonly sequenceNo: number;
  readonly senderRole: 'user' | 'assistant';
  readonly content: string;
  readonly contentStatus: 'active' | 'redacted' | 'deleted' | 'blocked';
  readonly createdAt: string;
  readonly deletedAt?: string;
}

export interface CreateMessageInput {
  readonly conversationId: string;
  readonly senderRole: 'user' | 'assistant';
  readonly content: string;
}

export class MessageRepository {
  constructor(private readonly db: DatabaseClient) {}

  /**
   * Find message by ID
   */
  async findById(id: string): Promise<Message | null> {
    const result = await this.db.query<Message>(
      `SELECT id, conversation_id, sequence_no, sender_role, content, 
              content_status, created_at, deleted_at
       FROM nexus.messages
       WHERE id = $1 AND deleted_at IS NULL`,
      [id]
    );

    return result.rows[0] || null;
  }

  /**
   * List all messages for a conversation in order
   */
  async listByConversationId(conversationId: string): Promise<readonly Message[]> {
    const result = await this.db.query<Message>(
      `SELECT id, conversation_id, sequence_no, sender_role, content, 
              content_status, created_at, deleted_at
       FROM nexus.messages
       WHERE conversation_id = $1 AND deleted_at IS NULL
       ORDER BY sequence_no ASC`,
      [conversationId]
    );

    return result.rows;
  }

  /**
   * Create a new message with auto-incrementing sequence
   */
  async create(input: CreateMessageInput): Promise<Message> {
    // Get next sequence number
    const seqResult = await this.db.query<{ next_seq: number }>(
      `SELECT COALESCE(MAX(sequence_no), 0) + 1 as next_seq
       FROM nexus.messages
       WHERE conversation_id = $1`,
      [input.conversationId]
    );

    const nextSeq = seqResult.rows[0]?.next_seq || 1;

    // Insert message
    const result = await this.db.query<Message>(
      `INSERT INTO nexus.messages (conversation_id, sequence_no, sender_role, content)
       VALUES ($1, $2, $3, $4)
       RETURNING id, conversation_id, sequence_no, sender_role, content, 
                 content_status, created_at, deleted_at`,
      [input.conversationId, nextSeq, input.senderRole, input.content]
    );

    return result.rows[0];
  }

  /**
   * Soft delete a message
   */
  async delete(id: string): Promise<boolean> {
    const result = await this.db.query(
      `UPDATE nexus.messages
       SET deleted_at = NOW()
       WHERE id = $1 AND deleted_at IS NULL`,
      [id]
    );

    return result.rowCount > 0;
  }
}
