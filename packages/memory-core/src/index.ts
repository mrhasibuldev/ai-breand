export type MemoryStatus = 'candidate' | 'approved' | 'rejected' | 'revoked' | 'deleted';

export type MemoryRecord = {
  readonly id: string;
  readonly accountId: string;
  readonly purpose: string;
  readonly value: unknown;
  readonly status: MemoryStatus;
};

export interface MemoryConsentBoundary {
  isMemoryEnabled(accountId: string, purpose: string): Promise<boolean>;
}

export interface MemoryRepository {
  save(record: MemoryRecord): Promise<void>;
  find(accountId: string, id: string): Promise<MemoryRecord | null>;
  listApproved(accountId: string, purpose: string): Promise<readonly MemoryRecord[]>;
  changeStatus(accountId: string, id: string, status: MemoryStatus): Promise<void>;
  clear(accountId: string): Promise<void>;
}

export interface MemoryService {
  propose(candidate: MemoryRecord): Promise<void>;
  approve(accountId: string, id: string): Promise<void>;
  reject(accountId: string, id: string): Promise<void>;
  retrieve(accountId: string, purpose: string): Promise<readonly MemoryRecord[]>;
  edit(accountId: string, id: string, value: unknown): Promise<void>;
  delete(accountId: string, id: string): Promise<void>;
  clear(accountId: string): Promise<void>;
  revoke(accountId: string, id: string): Promise<void>;
  disable(accountId: string): Promise<void>;
}

export class ConsentRequiredMemoryService implements MemoryService {
  constructor(
    private readonly consent: MemoryConsentBoundary,
    private readonly repository: MemoryRepository,
  ) {}

  async propose(candidate: MemoryRecord): Promise<void> {
    if (candidate.status !== 'candidate') throw new Error('Memory must begin as a candidate');
    if (!(await this.consent.isMemoryEnabled(candidate.accountId, candidate.purpose))) {
      throw new Error('Memory consent is not active');
    }
    await this.repository.save(candidate);
  }

  async approve(accountId: string, id: string): Promise<void> {
    const record = await this.requireOwned(accountId, id);
    if (!(await this.consent.isMemoryEnabled(accountId, record.purpose))) {
      throw new Error('Memory consent is not active');
    }
    await this.repository.changeStatus(accountId, id, 'approved');
  }

  async reject(accountId: string, id: string): Promise<void> {
    await this.requireOwned(accountId, id);
    await this.repository.changeStatus(accountId, id, 'rejected');
  }

  async retrieve(accountId: string, purpose: string): Promise<readonly MemoryRecord[]> {
    if (!(await this.consent.isMemoryEnabled(accountId, purpose))) return [];
    return this.repository.listApproved(accountId, purpose);
  }

  async edit(accountId: string, id: string, value: unknown): Promise<void> {
    const current = await this.requireOwned(accountId, id);
    if (current.status !== 'approved') throw new Error('Only approved memory can be edited');
    await this.repository.save({ ...current, value });
  }

  async delete(accountId: string, id: string): Promise<void> {
    await this.requireOwned(accountId, id);
    await this.repository.changeStatus(accountId, id, 'deleted');
  }

  async clear(accountId: string): Promise<void> {
    await this.repository.clear(accountId);
  }

  async revoke(accountId: string, id: string): Promise<void> {
    await this.requireOwned(accountId, id);
    await this.repository.changeStatus(accountId, id, 'revoked');
  }

  async disable(accountId: string): Promise<void> {
    await this.repository.clear(accountId);
  }

  private async requireOwned(accountId: string, id: string): Promise<MemoryRecord> {
    const record = await this.repository.find(accountId, id);
    if (!record) throw new Error('Memory not found');
    return record;
  }
}
