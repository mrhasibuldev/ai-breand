/**
 * Consent Record Repository
 */

import type { DatabaseClient } from '@nexusai/database-core';

export interface ConsentRecord {
  readonly id: string;
  readonly accountId: string;
  readonly consentType: string;
  readonly policyVersion: string;
  readonly decision: 'granted' | 'denied' | 'revoked' | 'superseded';
  readonly capturedAt: string;
  readonly revokedAt?: string;
  readonly captureSource: string;
}

export class ConsentRecordRepository {
  /**
   * Repository for consent_records table operations
   */
  
  constructor(private readonly db: DatabaseClient) {}
  
  /**
   * Find the most recent consent record for an account and consent type
   */
  async findLatestByAccountAndType(
    accountId: string,
    consentType: string
  ): Promise<ConsentRecord | null> {
    const result = await this.db.query<ConsentRecord>(
      `
      SELECT id, account_id, consent_type, policy_version, decision, 
             captured_at, revoked_at, capture_source
      FROM nexus.consent_records
      WHERE account_id = $1 AND consent_type = $2
      ORDER BY captured_at DESC
      LIMIT 1
      `,
      [accountId, consentType]
    );
    
    return result.rows[0] || null;
  }
  
  /**
   * Check if consent is currently granted (not denied or revoked)
   */
  async isGranted(
    accountId: string,
    consentType: string
  ): Promise<boolean> {
    const record = await this.findLatestByAccountAndType(accountId, consentType);
    
    if (!record) {
      return false; // No consent record = not granted
    }
    
    if (record.decision !== 'granted') {
      return false; // Not granted
    }
    
    if (record.revokedAt !== null) {
      return false; // Revoked
    }
    
    return true; // Granted and not revoked
  }
}
