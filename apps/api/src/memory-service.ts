/**
 * NexusAI Memory Service Integration
 *
 * Integrates memory retrieval with the IntelligenceEngine
 * Enforces consent boundaries
 */

import { MemoryRepository, type MemoryRecord, type CreateMemoryInput, ConsentRecordRepository } from '@nexusai/repositories';
import { readDatabaseConfig, createDatabaseClient } from '@nexusai/database-core';

export interface MemoryContext {
  accountId: string;
  memories: Array<{
    category: string;
    purpose: string;
    value: string;
  }>;
}

/**
 * Memory Service for Phase 3
 * 
 * Handles memory retrieval with consent enforcement
 */
export class NexusAIMemoryService {
  private memoryRepo: MemoryRepository;
  private consentRepo: ConsentRecordRepository;
  private db: ReturnType<typeof createDatabaseClient>;
  private dbConnectPromise: Promise<void> | null = null;

  constructor() {
    const dbConfig = readDatabaseConfig();
    const db = createDatabaseClient(dbConfig);
    this.db = db;
    this.memoryRepo = new MemoryRepository(db);
    this.consentRepo = new ConsentRecordRepository(db);
  }

  /**
   * Retrieve approved memories for a user
   * Guest mode returns empty memories
   * Consent is checked before retrieval
   */
  private async ensureDbConnected(): Promise<void> {
    if (!this.dbConnectPromise) {
      this.dbConnectPromise = this.db.connect().catch((err) => {
        this.dbConnectPromise = null;
        throw err;
      });
    }
    await this.dbConnectPromise;
  }

  async retrieveMemories(accountId: string, purpose?: string): Promise<MemoryContext> {
    await this.ensureDbConnected();
    if (accountId === 'guest') {
      return {
        accountId: 'guest',
        memories: [],
      };
    }

    try {
      // Check consent for memory usage
      const consentGranted = await this.consentRepo.isGranted(accountId, 'memory');
      if (!consentGranted) {
        console.log('[MemoryService] Memory consent not granted, returning empty memories');
        return {
          accountId,
          memories: [],
        };
      }

      const memories = await this.memoryRepo.listApproved(accountId, purpose);
      
      return {
        accountId,
        memories: memories.map(mem => ({
          category: mem.category,
          purpose: mem.purpose,
          value: mem.value,
        })),
      };
    } catch (error) {
      console.error('[MemoryService] Failed to retrieve memories:', error);
      // Fallback to empty memories on error
      return {
        accountId,
        memories: [],
      };
    }
  }

  /**
   * Create a memory candidate
   * For Phase 3, this is a stub - full consent flow implemented later
   */
  async proposeMemory(input: CreateMemoryInput): Promise<string> {
    try {
      await this.ensureDbConnected();
      const id = crypto.randomUUID();
      
      // Build record with only defined optional fields
      const record: MemoryRecord = {
        id,
        accountId: input.accountId,
        category: input.category,
        purpose: input.purpose,
        value: input.value,
        status: 'candidate',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      await this.memoryRepo.save(record);
      return id;
    } catch (error) {
      console.error('[MemoryService] Failed to propose memory:', error);
      throw error;
    }
  }
}

/**
 * Singleton instance
 */
export const memoryService = new NexusAIMemoryService();
