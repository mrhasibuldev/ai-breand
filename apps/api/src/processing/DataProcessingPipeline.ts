/**
 * Data Processing Pipeline
 * Processes collected raw data through normalization, validation, deduplication, and quality scoring
 */

import { createHash, randomUUID } from 'crypto';

export interface RawCollectionItem {
  sourceId: string;
  originalUrl: string;
  finalUrl?: string;
  title?: string;
  content?: string;
  contentType?: string;
  language?: string;
  publicationDate?: string;
  author?: string;
  collectionTimestamp: Date;
  license?: string;
  licenseMetadata?: Record<string, any>;
  httpStatus?: number;
  checksum?: string;
  sizeBytes?: number;
  error?: string;
}

export interface ProcessedDocument {
  id: string;
  sourceId: string;
  originalUrl: string;
  finalUrl?: string;
  title?: string;
  content: string;
  normalizedContent: string;
  contentType: string;
  language: string;
  author?: string;
  publicationDate?: string;
  collectionTimestamp: Date;
  processingTimestamp: Date;
  license?: string;
  contentHash: string;
  sizeBytes: number;
  wordCount: number;
  charCount: number;
  qualityScore: number;
  qualityStatus: 'accepted' | 'rejected' | 'duplicate' | 'failed';
  qualityReasons: string[];
  httpStatus?: number;
  metadata: Record<string, any>;
}

export interface ProcessingResult {
  totalProcessed: number;
  accepted: number;
  rejected: number;
  duplicate: number;
  failed: number;
  documents: ProcessedDocument[];
  errors: string[];
}

export interface ProcessingConfig {
  minContentLength: number;
  maxContentLength: number;
  minQualityScore: number;
  enableDeduplication: boolean;
  normalizeWhitespace: boolean;
  normalizeUnicode: boolean;
  stripHTML: boolean;
}

const DEFAULT_CONFIG: ProcessingConfig = {
  minContentLength: 50,
  maxContentLength: 10000000, // 10MB
  minQualityScore: 0.5,
  enableDeduplication: true,
  normalizeWhitespace: true,
  normalizeUnicode: true,
  stripHTML: true
};

export class DataProcessingPipeline {
  private config: ProcessingConfig;
  private seenHashes = new Set<string>();
  private seenUrls = new Set<string>();

  constructor(config: Partial<ProcessingConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Process a collection of raw items
   */
  async processCollection(items: RawCollectionItem[]): Promise<ProcessingResult> {
    const result: ProcessingResult = {
      totalProcessed: items.length,
      accepted: 0,
      rejected: 0,
      duplicate: 0,
      failed: 0,
      documents: [],
      errors: []
    };

    for (const item of items) {
      try {
        const processed = await this.processItem(item);

        if (processed.qualityStatus === 'accepted') {
          result.accepted++;
          result.documents.push(processed);
        } else if (processed.qualityStatus === 'rejected') {
          result.rejected++;
        } else if (processed.qualityStatus === 'duplicate') {
          result.duplicate++;
        } else {
          result.failed++;
        }
      } catch (error) {
        result.failed++;
        result.errors.push(`Failed to process item from ${item.originalUrl}: ${error}`);
      }
    }

    return result;
  }

  /**
   * Process a single raw item
   */
  async processItem(item: RawCollectionItem): Promise<ProcessedDocument> {
    // Step 1: Validation
    const validation = this.validateItem(item);
    if (!validation.valid) {
      return this.createRejectedDocument(item, validation.reasons);
    }

    // Step 2: Normalization
    const normalized = this.normalizeContent(item.content || '');

    // Step 3: Deduplication
    if (this.config.enableDeduplication) {
      const contentHash = this.computeHash(normalized);
      if (this.seenHashes.has(contentHash)) {
        return this.createDuplicateDocument(item, contentHash);
      }
      this.seenHashes.add(contentHash);

      if (this.seenUrls.has(item.originalUrl)) {
        return this.createDuplicateDocument(item, contentHash);
      }
      this.seenUrls.add(item.originalUrl);
    }

    // Step 4: Quality Scoring
    const qualityScore = this.computeQualityScore(item, normalized);

    // Step 5: Filtering
    if (qualityScore < this.config.minQualityScore) {
      return this.createRejectedDocument(item, [`Quality score ${qualityScore} below threshold ${this.config.minQualityScore}`]);
    }

    // Step 6: Create processed document
    const contentHash = this.computeHash(normalized);
    const wordCount = this.countWords(normalized);
    const charCount = normalized.length;

    return {
      id: this.generateId(),
      sourceId: item.sourceId,
      originalUrl: item.originalUrl,
      ...(item.finalUrl ? { finalUrl: item.finalUrl } : {}),
      ...(item.title ? { title: item.title } : {}),
      content: item.content || '',
      normalizedContent: normalized,
      contentType: item.contentType || 'text/plain',
      language: item.language || 'unknown',
      ...(item.author ? { author: item.author } : {}),
      ...(item.publicationDate ? { publicationDate: item.publicationDate } : {}),
      collectionTimestamp: item.collectionTimestamp,
      processingTimestamp: new Date(),
      ...(item.license ? { license: item.license } : {}),
      contentHash,
      sizeBytes: item.sizeBytes || 0,
      wordCount,
      charCount,
      qualityScore,
      qualityStatus: 'accepted',
      qualityReasons: ['valid_content', 'sufficient_length', 'quality_above_threshold'],
      ...(item.httpStatus ? { httpStatus: item.httpStatus } : {}),
      metadata: {
        licenseMetadata: item.licenseMetadata,
        originalChecksum: item.checksum
      }
    };
  }

  /**
   * Validate raw item
   */
  private validateItem(item: RawCollectionItem): { valid: boolean; reasons: string[] } {
    const reasons: string[] = [];

    if (!item.content || item.content.length === 0) {
      reasons.push('empty_content');
    }

    if (item.content && item.content.length < this.config.minContentLength) {
      reasons.push(`content_too_short: ${item.content.length} < ${this.config.minContentLength}`);
    }

    if (item.content && item.content.length > this.config.maxContentLength) {
      reasons.push(`content_too_long: ${item.content.length} > ${this.config.maxContentLength}`);
    }

    if (!item.originalUrl || !this.isValidUrl(item.originalUrl)) {
      reasons.push('invalid_source_url');
    }

    if (item.httpStatus && item.httpStatus >= 400) {
      reasons.push(`http_error: ${item.httpStatus}`);
    }

    return {
      valid: reasons.length === 0,
      reasons
    };
  }

  /**
   * Normalize content
   */
  private normalizeContent(content: string): string {
    let normalized = content;

    // Strip HTML if enabled
    if (this.config.stripHTML) {
      normalized = this.stripHTML(normalized);
    }

    // Normalize whitespace
    if (this.config.normalizeWhitespace) {
      normalized = normalized
        .replace(/\s+/g, ' ')
        .replace(/\n\s*\n/g, '\n')
        .trim();
    }

    // Normalize Unicode (NFC form)
    if (this.config.normalizeUnicode) {
      normalized = normalized.normalize('NFC');
    }

    // Remove control characters except newlines and tabs
    normalized = normalized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

    return normalized;
  }

  /**
   * Strip HTML tags
   */
  private stripHTML(html: string): string {
    return html
      .replace(/<script[^>]*>.*?<\/script>/gis, '')
      .replace(/<style[^>]*>.*?<\/style>/gis, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'");
  }

  /**
   * Compute quality score
   */
  private computeQualityScore(item: RawCollectionItem, normalized: string): number {
    let score = 0.0;
    const reasons: string[] = [];

    // Content length factor (0-0.3)
    const length = normalized.length;
    if (length >= 100) score += 0.1;
    if (length >= 500) score += 0.1;
    if (length >= 1000) score += 0.1;

    // Content type factor (0-0.2)
    if (item.contentType === 'text/html' || item.contentType === 'text/plain') {
      score += 0.2;
    } else if (item.contentType) {
      score += 0.1;
    }

    // Title presence (0-0.1)
    if (item.title && item.title.length > 0) {
      score += 0.1;
    }

    // Language detection (0-0.1)
    if (item.language && item.language !== 'unknown') {
      score += 0.1;
    }

    // HTTP status (0-0.2)
    if (!item.httpStatus || item.httpStatus < 300) {
      score += 0.2;
    } else if (item.httpStatus < 400) {
      score += 0.1;
    }

    // License information (0-0.1)
    if (item.license) {
      score += 0.1;
    }

    return Math.min(score, 1.0);
  }

  /**
   * Compute hash
   */
  private computeHash(content: string): string {
    return createHash('sha256').update(content).digest('hex');
  }

  /**
   * Count words
   */
  private countWords(content: string): number {
    return content.split(/\s+/).filter(w => w.length > 0).length;
  }

  /**
   * Validate URL
   */
  private isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Generate ID
   */
  private generateId(): string {
    return randomUUID();
  }

  /**
   * Create rejected document
   */
  private createRejectedDocument(item: RawCollectionItem, reasons: string[]): ProcessedDocument {
    const content = item.content || '';
    return {
      id: this.generateId(),
      sourceId: item.sourceId,
      originalUrl: item.originalUrl,
      ...(item.finalUrl ? { finalUrl: item.finalUrl } : {}),
      ...(item.title ? { title: item.title } : {}),
      content,
      normalizedContent: content,
      contentType: item.contentType || 'text/plain',
      language: item.language || 'unknown',
      ...(item.author ? { author: item.author } : {}),
      ...(item.publicationDate ? { publicationDate: item.publicationDate } : {}),
      collectionTimestamp: item.collectionTimestamp,
      processingTimestamp: new Date(),
      ...(item.license ? { license: item.license } : {}),
      contentHash: '',
      sizeBytes: item.sizeBytes || 0,
      wordCount: 0,
      charCount: 0,
      qualityScore: 0,
      qualityStatus: 'rejected',
      qualityReasons: reasons,
      ...(item.httpStatus ? { httpStatus: item.httpStatus } : {}),
      metadata: {}
    };
  }

  /**
   * Create duplicate document
   */
  private createDuplicateDocument(item: RawCollectionItem, hash: string): ProcessedDocument {
    const content = item.content || '';
    return {
      id: this.generateId(),
      sourceId: item.sourceId,
      originalUrl: item.originalUrl,
      ...(item.finalUrl ? { finalUrl: item.finalUrl } : {}),
      ...(item.title ? { title: item.title } : {}),
      content,
      normalizedContent: content,
      contentType: item.contentType || 'text/plain',
      language: item.language || 'unknown',
      ...(item.author ? { author: item.author } : {}),
      ...(item.publicationDate ? { publicationDate: item.publicationDate } : {}),
      collectionTimestamp: item.collectionTimestamp,
      processingTimestamp: new Date(),
      ...(item.license ? { license: item.license } : {}),
      contentHash: hash,
      sizeBytes: item.sizeBytes || 0,
      wordCount: 0,
      charCount: 0,
      qualityScore: 0,
      qualityStatus: 'duplicate',
      qualityReasons: ['duplicate_content'],
      ...(item.httpStatus ? { httpStatus: item.httpStatus } : {}),
      metadata: {}
    };
  }

  /**
   * Reset deduplication cache
   */
  resetCache(): void {
    this.seenHashes.clear();
    this.seenUrls.clear();
  }
}
